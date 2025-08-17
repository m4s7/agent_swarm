"""
Recovery handler for Claude Code auto-resume functionality
"""

import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.error_types import (
    ErrorContext, 
    RecoveryStrategy, 
    ErrorSeverity,
    ERROR_PATTERNS
)
from utils.error_detector import LimitDetector
from state.session_manager import SessionState, SessionManager, get_session_manager
from state.checkpoint_manager import (
    CheckpointManager, 
    get_checkpoint_manager,
    CheckpointType,
    CheckpointTrigger
)


class RecoveryStatus(Enum):
    """Status of recovery attempt"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    ESCALATED = "escalated"


@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt"""
    attempt_id: str
    error_context: ErrorContext
    strategy: RecoveryStrategy
    status: RecoveryStatus
    started_at: float
    completed_at: Optional[float] = None
    checkpoint_used: Optional[str] = None
    new_session_id: Optional[str] = None
    recovery_metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.recovery_metadata is None:
            self.recovery_metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['error_context'] = self.error_context.to_dict()
        result['strategy'] = self.strategy.value
        result['status'] = self.status.value
        return result
    
    def duration(self) -> float:
        """Calculate recovery duration"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return time.time() - self.started_at


class RecoveryHandler:
    """Handles error recovery and auto-resume functionality"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Component references
        self.error_detector = LimitDetector()
        self.session_manager = get_session_manager()
        self.checkpoint_manager = get_checkpoint_manager()
        
        # Recovery state
        self.recovery_attempts: List[RecoveryAttempt] = []
        self.max_recovery_attempts = self.config.get('max_recovery_attempts', 3)
        self.recovery_timeout = self.config.get('recovery_timeout', 300)  # 5 minutes
        
        # Recovery callbacks
        self.recovery_callbacks: Dict[RecoveryStrategy, Callable] = {}
        self._register_default_callbacks()
        
        # Metrics
        self.recovery_stats = {
            'total_attempts': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'strategies_used': {}
        }
    
    def handle_error(self, 
                    error_message: str,
                    http_code: Optional[int] = None,
                    context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[SessionState]]:
        """
        Main entry point for error handling and recovery
        
        Returns:
            Tuple of (recovery_success, recovered_session)
        """
        
        # Detect and classify error
        error_context = self.error_detector.detect_error(
            error_message, http_code, context=context
        )
        
        if not error_context:
            self.logger.warning(f"Unrecognized error, cannot recover: {error_message}")
            return False, None
        
        self.logger.info(f"Error detected: {error_context.error_type}, attempting recovery")
        
        # Get recovery strategy
        strategy = self.error_detector.get_recovery_strategy(error_context)
        
        # Create recovery attempt record
        attempt = RecoveryAttempt(
            attempt_id=f"recovery_{int(time.time())}_{hash(time.time()) % 10000}",
            error_context=error_context,
            strategy=strategy,
            status=RecoveryStatus.IN_PROGRESS,
            started_at=time.time()
        )
        
        self.recovery_attempts.append(attempt)
        self.recovery_stats['total_attempts'] += 1
        
        # Execute recovery
        try:
            recovered_session = self._execute_recovery(attempt)
            
            if recovered_session:
                attempt.status = RecoveryStatus.SUCCESS
                attempt.completed_at = time.time()
                attempt.new_session_id = recovered_session.session_id
                
                self.recovery_stats['successful_recoveries'] += 1
                self.logger.info(f"Recovery successful using {strategy.value}")
                
                return True, recovered_session
            else:
                attempt.status = RecoveryStatus.FAILED
                attempt.completed_at = time.time()
                
                self.recovery_stats['failed_recoveries'] += 1
                self.logger.error(f"Recovery failed using {strategy.value}")
                
                return False, None
                
        except Exception as e:
            attempt.status = RecoveryStatus.FAILED
            attempt.completed_at = time.time()
            attempt.error_message = str(e)
            
            self.recovery_stats['failed_recoveries'] += 1
            self.logger.error(f"Recovery exception: {e}")
            
            return False, None
    
    def _execute_recovery(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Execute recovery based on strategy"""
        
        strategy = attempt.strategy
        
        # Track strategy usage
        self.recovery_stats['strategies_used'][strategy.value] = \
            self.recovery_stats['strategies_used'].get(strategy.value, 0) + 1
        
        # Get recovery callback
        callback = self.recovery_callbacks.get(strategy)
        
        if not callback:
            self.logger.error(f"No recovery callback for strategy: {strategy.value}")
            return None
        
        # Execute recovery
        return callback(attempt)
    
    def _register_default_callbacks(self):
        """Register default recovery callbacks for each strategy"""
        
        self.recovery_callbacks[RecoveryStrategy.WAIT_AND_RETRY] = self._recover_wait_and_retry
        self.recovery_callbacks[RecoveryStrategy.TRUNCATE_CONTEXT] = self._recover_truncate_context
        self.recovery_callbacks[RecoveryStrategy.CHECKPOINT_AND_RETRY] = self._recover_checkpoint
        self.recovery_callbacks[RecoveryStrategy.ESCALATE_TO_HUMAN] = self._recover_escalate
        self.recovery_callbacks[RecoveryStrategy.AGENT_HANDOFF] = self._recover_agent_handoff
        self.recovery_callbacks[RecoveryStrategy.GRACEFUL_DEGRADATION] = self._recover_graceful_degradation
    
    def _recover_wait_and_retry(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Recovery strategy: Wait and retry with exponential backoff"""
        
        error_context = attempt.error_context
        
        # Check if we should retry
        if not self.error_detector.should_retry(error_context):
            self.logger.info("Max retries exceeded, cannot recover")
            return None
        
        # Calculate backoff delay
        delay = self.error_detector.calculate_backoff_delay(error_context)
        
        self.logger.info(f"Waiting {delay:.1f} seconds before retry...")
        time.sleep(delay)
        
        # Increment retry count
        error_context.retry_count += 1
        
        # Return current session for retry
        return self.session_manager.current_session
    
    def _recover_truncate_context(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Recovery strategy: Truncate context to fit within limits"""
        
        if not self.session_manager.current_session:
            return None
        
        session = self.session_manager.current_session
        
        # Configuration for truncation
        keep_recent_messages = 10
        preserve_current_task = True
        
        self.logger.info(f"Truncating context from {len(session.conversation_history)} messages")
        
        # Create checkpoint before truncation
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            CheckpointType.RECOVERY,
            description="Pre-truncation checkpoint"
        )
        attempt.checkpoint_used = checkpoint_id
        
        # Truncate conversation history
        if len(session.conversation_history) > keep_recent_messages:
            # Keep system messages and recent messages
            system_messages = [
                msg for msg in session.conversation_history 
                if msg.role == 'system'
            ]
            
            recent_messages = session.conversation_history[-keep_recent_messages:]
            
            # Create summary of truncated content
            truncated_count = len(session.conversation_history) - keep_recent_messages
            from state.session_manager import Message
            summary_message = Message(
                role='system',
                content=f"[Context truncated: {truncated_count} messages removed due to token limit]",
                timestamp=time.time(),
                message_id=f"truncation_{int(time.time())}"
            )
            
            # Rebuild conversation history
            session.conversation_history = system_messages + [summary_message] + recent_messages
            
            self.logger.info(f"Context truncated to {len(session.conversation_history)} messages")
        
        # Clear unnecessary agent contexts to save space
        if len(session.agent_contexts) > 3:
            # Keep only the most recently active agents
            recent_agents = sorted(
                session.agent_contexts.items(),
                key=lambda x: x[1].last_active or 0,
                reverse=True
            )[:3]
            
            session.agent_contexts = dict(recent_agents)
            self.logger.info(f"Agent contexts reduced to {len(session.agent_contexts)}")
        
        # Save the truncated session
        self.session_manager.save_session()
        
        return session
    
    def _recover_checkpoint(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Recovery strategy: Restore from checkpoint"""
        
        if not self.session_manager.current_session:
            return None
        
        session_id = self.session_manager.current_session.session_id
        
        # Find suitable checkpoint
        checkpoint = self.checkpoint_manager.find_recovery_checkpoint(
            session_id, attempt.error_context
        )
        
        if not checkpoint:
            self.logger.error("No suitable checkpoint found for recovery")
            return None
        
        self.logger.info(f"Restoring from checkpoint: {checkpoint.checkpoint_id}")
        
        # Restore from checkpoint
        recovered_session = self.checkpoint_manager.restore_from_checkpoint(
            checkpoint.checkpoint_id
        )
        
        if recovered_session:
            attempt.checkpoint_used = checkpoint.checkpoint_id
            
            # Update session manager
            self.session_manager.current_session = recovered_session
            
            # Add recovery message
            from state.session_manager import Message
            recovery_message = Message(
                role='system',
                content=f"[Session restored from checkpoint after {attempt.error_context.error_type}]",
                timestamp=time.time(),
                message_id=f"recovery_{int(time.time())}"
            )
            recovered_session.conversation_history.append(recovery_message)
            
            return recovered_session
        
        return None
    
    def _recover_escalate(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Recovery strategy: Escalate to human intervention"""
        
        self.logger.warning("Error requires human intervention")
        
        if self.session_manager.current_session:
            session = self.session_manager.current_session
            
            # Add escalation message
            from state.session_manager import Message
            escalation_message = Message(
                role='system',
                content=f"""
⚠️ Error requires human intervention:
- Error Type: {attempt.error_context.error_type}
- Error Message: {attempt.error_context.error_message}
- Recommended Action: Please check your configuration or contact support
""",
                timestamp=time.time(),
                message_id=f"escalation_{int(time.time())}"
            )
            session.conversation_history.append(escalation_message)
            
            # Suspend session
            self.session_manager.suspend_session(
                f"Escalated due to {attempt.error_context.error_type}"
            )
            
            attempt.status = RecoveryStatus.ESCALATED
        
        return None
    
    def _recover_agent_handoff(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Recovery strategy: Hand off to different agent"""
        
        if not self.session_manager.current_session:
            return None
        
        session = self.session_manager.current_session
        error_context = attempt.error_context
        
        # Get the failing agent
        failing_agent = error_context.agent_id
        
        if not failing_agent:
            self.logger.warning("No agent identified for handoff")
            return None
        
        self.logger.info(f"Attempting handoff from agent: {failing_agent}")
        
        # Find alternative agent
        alternative_agent = self._find_alternative_agent(failing_agent, session)
        
        if not alternative_agent:
            self.logger.error("No alternative agent found for handoff")
            return None
        
        # Create checkpoint before handoff
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            CheckpointType.AGENT_HANDOFF,
            description=f"Handoff from {failing_agent} to {alternative_agent}"
        )
        attempt.checkpoint_used = checkpoint_id
        
        # Update session with handoff information
        from state.session_manager import Message
        handoff_message = Message(
            role='system',
            content=f"[Agent handoff: {failing_agent} → {alternative_agent} due to error]",
            timestamp=time.time(),
            message_id=f"handoff_{int(time.time())}"
        )
        session.conversation_history.append(handoff_message)
        
        # Transfer context to new agent
        if failing_agent in session.agent_contexts:
            old_context = session.agent_contexts[failing_agent]
            
            # Create new agent context
            from state.session_manager import AgentContext
            new_context = AgentContext(
                agent_id=alternative_agent,
                agent_type=self._get_agent_type(alternative_agent),
                current_task=old_context.current_task,
                progress=old_context.progress,
                memory_state=old_context.memory_state
            )
            
            session.update_agent_context(alternative_agent, new_context)
        
        attempt.recovery_metadata['new_agent'] = alternative_agent
        
        return session
    
    def _recover_graceful_degradation(self, attempt: RecoveryAttempt) -> Optional[SessionState]:
        """Recovery strategy: Continue with reduced functionality"""
        
        if not self.session_manager.current_session:
            return None
        
        session = self.session_manager.current_session
        
        self.logger.info("Applying graceful degradation strategy")
        
        # Disable problematic features
        degradation_config = {
            'disable_mcp_servers': True,
            'disable_parallel_execution': True,
            'reduce_agent_count': True,
            'simplify_workflow': True
        }
        
        # Add degradation notice
        from state.session_manager import Message
        degradation_message = Message(
            role='system',
            content=f"""
[Operating in degraded mode due to {attempt.error_context.error_type}]
- Some features may be temporarily unavailable
- Performance may be reduced
- Will attempt to restore full functionality when possible
""",
            timestamp=time.time(),
            message_id=f"degradation_{int(time.time())}"
        )
        session.conversation_history.append(degradation_message)
        
        # Store degradation config in session
        session.user_preferences['degradation_mode'] = degradation_config
        
        attempt.recovery_metadata['degradation_config'] = degradation_config
        
        return session
    
    def _find_alternative_agent(self, failing_agent: str, session: SessionState) -> Optional[str]:
        """Find an alternative agent for handoff"""
        
        # Map of agent alternatives
        agent_alternatives = {
            'python-pro': ['python-dev', 'debugger', 'code-reviewer'],
            'frontend-developer': ['react-dev', 'typescript-pro', 'ui-engineer'],
            'data-analyst': ['data-scientist', 'research-analyst', 'data-researcher'],
            'architect-reviewer': ['code-reviewer', 'test-automator', 'qa-expert'],
            'deployment-engineer': ['devops-engineer', 'fintech-engineer', 'tooling-engineer']
        }
        
        # Get alternatives for the failing agent
        alternatives = agent_alternatives.get(failing_agent, [])
        
        # Find first alternative not currently active
        active_agents = set(session.agent_contexts.keys())
        
        for alt_agent in alternatives:
            if alt_agent not in active_agents:
                return alt_agent
        
        # If no specific alternative, use a general-purpose agent
        if 'debugger' not in active_agents:
            return 'debugger'
        
        return None
    
    def _get_agent_type(self, agent_id: str) -> str:
        """Get agent type from agent ID"""
        # For now, return the agent_id as type
        # This could be enhanced with a proper agent registry
        return agent_id
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get statistics about recovery attempts"""
        
        stats = self.recovery_stats.copy()
        
        # Add recent attempts
        recent_attempts = self.recovery_attempts[-10:] if self.recovery_attempts else []
        stats['recent_attempts'] = [
            {
                'attempt_id': attempt.attempt_id,
                'error_type': attempt.error_context.error_type,
                'strategy': attempt.strategy.value,
                'status': attempt.status.value,
                'duration': attempt.duration()
            }
            for attempt in recent_attempts
        ]
        
        # Calculate success rate
        total = stats['total_attempts']
        if total > 0:
            stats['success_rate'] = stats['successful_recoveries'] / total
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def register_custom_recovery(self, 
                                strategy: RecoveryStrategy,
                                callback: Callable[[RecoveryAttempt], Optional[SessionState]]):
        """Register a custom recovery callback"""
        self.recovery_callbacks[strategy] = callback
        self.logger.info(f"Registered custom recovery for {strategy.value}")
    
    async def handle_error_async(self,
                                error_message: str,
                                http_code: Optional[int] = None,
                                context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[SessionState]]:
        """Async version of error handling"""
        
        # Run recovery in background
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.handle_error,
            error_message,
            http_code,
            context
        )


class AutoResumeCoordinator:
    """Coordinates all auto-resume components"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.recovery_handler = RecoveryHandler()
        self.session_manager = get_session_manager()
        self.checkpoint_manager = get_checkpoint_manager()
        
        # Configuration
        self.auto_checkpoint_enabled = True
        self.auto_recovery_enabled = True
        
        # State
        self.is_active = False
        self.monitoring_task = None
    
    def start(self, session_id: Optional[str] = None):
        """Start auto-resume coordinator"""
        
        # Create or load session
        if session_id:
            session = self.session_manager.load_session(session_id)
            if not session:
                session = self.session_manager.create_session(session_id)
        else:
            session = self.session_manager.create_session()
        
        self.is_active = True
        self.logger.info(f"Auto-resume coordinator started for session: {session.session_id}")
        
        # Start monitoring if async
        if asyncio.get_event_loop().is_running():
            self.monitoring_task = asyncio.create_task(self._monitor_session())
        
        return session
    
    def stop(self):
        """Stop auto-resume coordinator"""
        
        self.is_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        # Save final session state
        if self.session_manager.current_session:
            self.session_manager.save_session()
        
        self.logger.info("Auto-resume coordinator stopped")
    
    def handle_operation(self, operation_context: Dict[str, Any]):
        """Handle an operation with auto-checkpoint"""
        
        if not self.auto_checkpoint_enabled:
            return
        
        # Check if checkpoint needed
        checkpoint_id = self.checkpoint_manager.checkpoint_before_operation(operation_context)
        
        if checkpoint_id:
            self.logger.debug(f"Created pre-operation checkpoint: {checkpoint_id}")
    
    def handle_error(self, error_message: str, **kwargs) -> Tuple[bool, Optional[SessionState]]:
        """Handle an error with auto-recovery"""
        
        if not self.auto_recovery_enabled:
            return False, None
        
        return self.recovery_handler.handle_error(error_message, **kwargs)
    
    async def _monitor_session(self):
        """Monitor session and create periodic checkpoints"""
        
        while self.is_active:
            try:
                # Check for auto-checkpoint
                self.checkpoint_manager.auto_checkpoint_if_needed()
                
                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status"""
        
        status = {
            'is_active': self.is_active,
            'auto_checkpoint_enabled': self.auto_checkpoint_enabled,
            'auto_recovery_enabled': self.auto_recovery_enabled,
            'current_session': None,
            'recovery_stats': self.recovery_handler.get_recovery_statistics(),
            'checkpoint_stats': self.checkpoint_manager.get_checkpoint_statistics()
        }
        
        if self.session_manager.current_session:
            session = self.session_manager.current_session
            status['current_session'] = {
                'session_id': session.session_id,
                'status': session.status.value,
                'message_count': len(session.conversation_history),
                'agent_count': len(session.agent_contexts)
            }
        
        return status


# Global coordinator instance
_coordinator = None

def get_auto_resume_coordinator() -> AutoResumeCoordinator:
    """Get the global auto-resume coordinator"""
    global _coordinator
    if _coordinator is None:
        _coordinator = AutoResumeCoordinator()
    return _coordinator
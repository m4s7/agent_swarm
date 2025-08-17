"""
Checkpoint management for Claude Code auto-resume functionality
"""

import time
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.session_manager import SessionState, SessionManager, get_session_manager
from utils.error_types import ErrorContext, RecoveryStrategy


class CheckpointType(Enum):
    """Types of checkpoints"""
    AUTO = "auto"                    # Automatic periodic checkpoint
    ERROR = "error"                  # Before risky operation
    MANUAL = "manual"                # User-triggered
    WORKFLOW = "workflow"            # At workflow stage boundaries
    AGENT_HANDOFF = "agent_handoff"  # Before agent transitions
    RECOVERY = "recovery"            # During recovery process


class CheckpointTrigger(Enum):
    """Triggers for automatic checkpoints"""
    TIME_INTERVAL = "time_interval"      # Every N seconds
    MESSAGE_COUNT = "message_count"      # Every N messages
    AGENT_CHANGE = "agent_change"        # When active agent changes
    WORKFLOW_STAGE = "workflow_stage"    # At workflow boundaries
    ERROR_THRESHOLD = "error_threshold"  # After N errors
    TOOL_USAGE = "tool_usage"           # Before risky tool usage


@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint"""
    checkpoint_id: str
    checkpoint_type: CheckpointType
    trigger: Optional[CheckpointTrigger]
    session_id: str
    created_at: float
    description: str
    context_size: int              # Size of context at checkpoint
    message_count: int             # Number of messages at checkpoint
    active_agents: List[str]       # Active agents at checkpoint
    workflow_stage: Optional[str]  # Current workflow stage
    risk_level: str                # low, medium, high
    recovery_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.recovery_metadata is None:
            self.recovery_metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['checkpoint_type'] = self.checkpoint_type.value
        if self.trigger:
            result['trigger'] = self.trigger.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckpointMetadata':
        data['checkpoint_type'] = CheckpointType(data['checkpoint_type'])
        if 'trigger' in data and data['trigger']:
            data['trigger'] = CheckpointTrigger(data['trigger'])
        return cls(**data)


@dataclass
class CheckpointConfig:
    """Configuration for checkpoint behavior"""
    auto_checkpoint_interval: int = 300  # 5 minutes
    auto_checkpoint_message_threshold: int = 20
    max_checkpoints_per_session: int = 50
    checkpoint_retention_days: int = 7
    enable_compression: bool = True
    enable_encryption: bool = False
    
    # Risk-based checkpointing
    checkpoint_before_high_risk_operations: bool = True
    high_risk_tools: List[str] = None
    high_risk_keywords: List[str] = None
    
    def __post_init__(self):
        if self.high_risk_tools is None:
            self.high_risk_tools = [
                'Bash', 'Write', 'Edit', 'MultiEdit', 
                'git', 'npm', 'pip', 'docker'
            ]
        if self.high_risk_keywords is None:
            self.high_risk_keywords = [
                'delete', 'remove', 'rm', 'drop', 'truncate',
                'install', 'upgrade', 'deploy', 'production'
            ]


class CheckpointManager:
    """Manages checkpoint creation, storage, and recovery"""
    
    def __init__(self, 
                 config: Optional[CheckpointConfig] = None,
                 storage_dir: str = ".claude/state/checkpoints"):
        self.config = config or CheckpointConfig()
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Session manager reference
        self.session_manager = get_session_manager()
        
        # Checkpoint tracking
        self.last_auto_checkpoint = 0
        self.checkpoint_message_count = 0
        self.checkpoints_created = 0
        
        # Risk assessment
        self.pending_high_risk_operation = False
        self.risk_context = {}
    
    def should_create_checkpoint(self, 
                               trigger: CheckpointTrigger,
                               context: Optional[Dict[str, Any]] = None) -> bool:
        """Determine if a checkpoint should be created"""
        
        current_time = time.time()
        
        if trigger == CheckpointTrigger.TIME_INTERVAL:
            return (current_time - self.last_auto_checkpoint) >= self.config.auto_checkpoint_interval
        
        elif trigger == CheckpointTrigger.MESSAGE_COUNT:
            return self.checkpoint_message_count >= self.config.auto_checkpoint_message_threshold
        
        elif trigger == CheckpointTrigger.AGENT_CHANGE:
            return True  # Always checkpoint on agent changes
        
        elif trigger == CheckpointTrigger.WORKFLOW_STAGE:
            return True  # Always checkpoint at workflow boundaries
        
        elif trigger == CheckpointTrigger.ERROR_THRESHOLD:
            if context and 'error_count' in context:
                return context['error_count'] >= 3
            return False
        
        elif trigger == CheckpointTrigger.TOOL_USAGE:
            if context and 'tool_name' in context:
                tool_name = context['tool_name']
                operation = context.get('operation', '').lower()
                
                # Check if tool is high risk
                if tool_name in self.config.high_risk_tools:
                    return True
                
                # Check if operation contains high risk keywords
                for keyword in self.config.high_risk_keywords:
                    if keyword in operation:
                        return True
            
            return False
        
        return False
    
    def create_checkpoint(self,
                         checkpoint_type: CheckpointType,
                         trigger: Optional[CheckpointTrigger] = None,
                         description: str = "",
                         context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a checkpoint of current session state"""
        
        if not self.session_manager.current_session:
            self.logger.warning("No active session to checkpoint")
            return None
        
        try:
            session = self.session_manager.current_session
            current_time = time.time()
            
            # Generate checkpoint ID
            checkpoint_id = f"cp_{session.session_id}_{int(current_time)}_{hash(current_time) % 10000}"
            
            # Assess risk level
            risk_level = self._assess_risk_level(context)
            
            # Create metadata
            metadata = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                checkpoint_type=checkpoint_type,
                trigger=trigger,
                session_id=session.session_id,
                created_at=current_time,
                description=description or f"Checkpoint created by {checkpoint_type.value}",
                context_size=len(json.dumps(session.to_dict())),
                message_count=len(session.conversation_history),
                active_agents=list(session.agent_contexts.keys()),
                workflow_stage=session.workflow_state.current_stage if session.workflow_state else None,
                risk_level=risk_level,
                recovery_metadata=context or {}
            )
            
            # Save checkpoint data
            checkpoint_file = self.storage_dir / f"{checkpoint_id}.json"
            
            checkpoint_data = {
                'metadata': metadata.to_dict(),
                'session_state': session.to_dict(),
                'format_version': '1.0',
                'created_at': current_time
            }
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Update tracking
            self.last_auto_checkpoint = current_time
            self.checkpoint_message_count = 0
            self.checkpoints_created += 1
            
            self.logger.info(f"Checkpoint created: {checkpoint_id} ({checkpoint_type.value})")
            
            # Clean up old checkpoints if needed
            self._cleanup_old_checkpoints(session.session_id)
            
            return checkpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
            return None
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[SessionState]:
        """Restore session state from a checkpoint"""
        
        try:
            checkpoint_file = self.storage_dir / f"{checkpoint_id}.json"
            
            if not checkpoint_file.exists():
                self.logger.error(f"Checkpoint file not found: {checkpoint_id}")
                return None
            
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # Verify format
            if checkpoint_data.get('format_version') != '1.0':
                self.logger.error(f"Unsupported checkpoint format: {checkpoint_data.get('format_version')}")
                return None
            
            # Restore session state
            session_data = checkpoint_data['session_state']
            session = SessionState.from_dict(session_data)
            
            # Load metadata
            metadata = CheckpointMetadata.from_dict(checkpoint_data['metadata'])
            
            self.logger.info(f"Restored session from checkpoint: {checkpoint_id}")
            self.logger.info(f"Checkpoint created: {time.ctime(metadata.created_at)}")
            self.logger.info(f"Messages restored: {metadata.message_count}")
            self.logger.info(f"Active agents: {', '.join(metadata.active_agents)}")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to restore from checkpoint {checkpoint_id}: {e}")
            return None
    
    def list_checkpoints(self, session_id: Optional[str] = None) -> List[CheckpointMetadata]:
        """List available checkpoints"""
        
        checkpoints = []
        
        for checkpoint_file in self.storage_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                metadata = CheckpointMetadata.from_dict(checkpoint_data['metadata'])
                
                if session_id is None or metadata.session_id == session_id:
                    checkpoints.append(metadata)
                    
            except Exception as e:
                self.logger.warning(f"Failed to read checkpoint {checkpoint_file}: {e}")
        
        # Sort by creation time (newest first)
        checkpoints.sort(key=lambda x: x.created_at, reverse=True)
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        
        try:
            checkpoint_file = self.storage_dir / f"{checkpoint_id}.json"
            
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                self.logger.info(f"Checkpoint deleted: {checkpoint_id}")
                return True
            else:
                self.logger.warning(f"Checkpoint file not found: {checkpoint_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
            return False
    
    def find_recovery_checkpoint(self, 
                                session_id: str,
                                error_context: ErrorContext) -> Optional[CheckpointMetadata]:
        """Find the best checkpoint for recovery from an error"""
        
        checkpoints = self.list_checkpoints(session_id)
        
        if not checkpoints:
            return None
        
        # Recovery strategy based on error type
        recovery_strategy = self._get_recovery_strategy(error_context)
        
        if recovery_strategy == RecoveryStrategy.TRUNCATE_CONTEXT:
            # Find checkpoint with smaller context for token limit errors
            suitable_checkpoints = [
                cp for cp in checkpoints 
                if cp.context_size < error_context.metadata.get('max_context_size', 100000)
            ]
            return suitable_checkpoints[0] if suitable_checkpoints else None
        
        elif recovery_strategy == RecoveryStrategy.CHECKPOINT_AND_RETRY:
            # Find most recent checkpoint before error
            error_time = error_context.timestamp
            suitable_checkpoints = [
                cp for cp in checkpoints 
                if cp.created_at < error_time
            ]
            return suitable_checkpoints[0] if suitable_checkpoints else None
        
        elif recovery_strategy == RecoveryStrategy.AGENT_HANDOFF:
            # Find checkpoint where different agents were active
            current_agents = error_context.metadata.get('active_agents', [])
            suitable_checkpoints = [
                cp for cp in checkpoints 
                if not set(cp.active_agents).intersection(set(current_agents))
            ]
            return suitable_checkpoints[0] if suitable_checkpoints else checkpoints[0]
        
        # Default: return most recent checkpoint
        return checkpoints[0] if checkpoints else None
    
    def auto_checkpoint_if_needed(self, context: Optional[Dict[str, Any]] = None):
        """Check if auto-checkpoint is needed and create if so"""
        
        # Check time-based trigger
        if self.should_create_checkpoint(CheckpointTrigger.TIME_INTERVAL):
            self.create_checkpoint(
                CheckpointType.AUTO,
                CheckpointTrigger.TIME_INTERVAL,
                "Automatic time-based checkpoint"
            )
        
        # Check message count trigger
        elif self.should_create_checkpoint(CheckpointTrigger.MESSAGE_COUNT):
            self.create_checkpoint(
                CheckpointType.AUTO,
                CheckpointTrigger.MESSAGE_COUNT,
                "Automatic message count checkpoint"
            )
    
    def checkpoint_before_operation(self, operation_context: Dict[str, Any]) -> Optional[str]:
        """Create checkpoint before potentially risky operation"""
        
        if self.should_create_checkpoint(CheckpointTrigger.TOOL_USAGE, operation_context):
            return self.create_checkpoint(
                CheckpointType.ERROR,
                CheckpointTrigger.TOOL_USAGE,
                f"Pre-operation checkpoint: {operation_context.get('tool_name', 'unknown')}",
                operation_context
            )
        
        return None
    
    def _assess_risk_level(self, context: Optional[Dict[str, Any]]) -> str:
        """Assess risk level of current operation"""
        
        if not context:
            return "low"
        
        risk_score = 0
        
        # Check for high-risk tools
        tool_name = context.get('tool_name', '')
        if tool_name in self.config.high_risk_tools:
            risk_score += 2
        
        # Check for high-risk keywords
        operation = context.get('operation', '').lower()
        for keyword in self.config.high_risk_keywords:
            if keyword in operation:
                risk_score += 1
        
        # Check file operations
        if 'file_path' in context:
            file_path = context['file_path']
            if any(path in file_path for path in ['/etc/', '/usr/', '/var/', '~/']):
                risk_score += 1
        
        # Check for production environments
        if any(term in operation for term in ['production', 'prod', 'live']):
            risk_score += 2
        
        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _get_recovery_strategy(self, error_context: ErrorContext) -> RecoveryStrategy:
        """Get recovery strategy for error context"""
        
        from ..utils.error_detector import LimitDetector
        detector = LimitDetector()
        return detector.get_recovery_strategy(error_context)
    
    def _cleanup_old_checkpoints(self, session_id: str):
        """Remove old checkpoints to stay within limits"""
        
        checkpoints = self.list_checkpoints(session_id)
        
        if len(checkpoints) <= self.config.max_checkpoints_per_session:
            return
        
        # Sort by creation time (oldest first for deletion)
        checkpoints.sort(key=lambda x: x.created_at)
        
        # Delete oldest checkpoints beyond limit
        to_delete = checkpoints[:-self.config.max_checkpoints_per_session]
        
        for checkpoint in to_delete:
            self.delete_checkpoint(checkpoint.checkpoint_id)
    
    def cleanup_expired_checkpoints(self) -> int:
        """Clean up expired checkpoints based on retention policy"""
        
        cutoff_time = time.time() - (self.config.checkpoint_retention_days * 24 * 60 * 60)
        deleted_count = 0
        
        for checkpoint_file in self.storage_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                created_at = checkpoint_data.get('created_at', 0)
                if created_at < cutoff_time:
                    checkpoint_file.unlink()
                    deleted_count += 1
                    
            except Exception as e:
                self.logger.warning(f"Failed to process checkpoint file {checkpoint_file}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} expired checkpoints")
        return deleted_count
    
    def get_checkpoint_statistics(self) -> Dict[str, Any]:
        """Get statistics about checkpoints"""
        
        checkpoints = self.list_checkpoints()
        
        if not checkpoints:
            return {
                'total_checkpoints': 0,
                'storage_mb': 0
            }
        
        stats = {
            'total_checkpoints': len(checkpoints),
            'checkpoints_by_type': {},
            'checkpoints_by_session': {},
            'oldest_checkpoint': min(cp.created_at for cp in checkpoints),
            'newest_checkpoint': max(cp.created_at for cp in checkpoints),
            'average_context_size': sum(cp.context_size for cp in checkpoints) / len(checkpoints)
        }
        
        # Count by type
        for checkpoint in checkpoints:
            cp_type = checkpoint.checkpoint_type.value
            stats['checkpoints_by_type'][cp_type] = stats['checkpoints_by_type'].get(cp_type, 0) + 1
            
            session_id = checkpoint.session_id
            stats['checkpoints_by_session'][session_id] = stats['checkpoints_by_session'].get(session_id, 0) + 1
        
        # Calculate storage size
        total_size = 0
        for checkpoint_file in self.storage_dir.glob("*.json"):
            total_size += checkpoint_file.stat().st_size
        
        stats['storage_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats


# Global checkpoint manager instance
_checkpoint_manager = None

def get_checkpoint_manager() -> CheckpointManager:
    """Get the global checkpoint manager instance"""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
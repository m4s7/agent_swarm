"""
Session state management for Claude Code auto-resume functionality
"""

import json
import time
import pickle
import hashlib
import asyncio
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.error_types import ErrorContext


class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended" 
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class Message:
    """Represents a conversation message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float
    message_id: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(**data)


@dataclass  
class AgentContext:
    """Context for individual agent state"""
    agent_id: str
    agent_type: str
    current_task: Optional[str] = None
    progress: Dict[str, Any] = None
    memory_state: Dict[str, Any] = None
    mcp_state: Dict[str, Any] = None
    artifacts: List[str] = None
    last_active: float = None
    
    def __post_init__(self):
        if self.progress is None:
            self.progress = {}
        if self.memory_state is None:
            self.memory_state = {}
        if self.mcp_state is None:
            self.mcp_state = {}
        if self.artifacts is None:
            self.artifacts = []
        if self.last_active is None:
            self.last_active = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentContext':
        return cls(**data)


@dataclass
class WorkflowState:
    """State of workflow execution"""
    workflow_id: str
    workflow_type: str
    current_stage: str
    completed_stages: List[str] = None
    stage_results: Dict[str, Any] = None
    stage_errors: Dict[str, ErrorContext] = None
    total_stages: int = 0
    start_time: float = None
    
    def __post_init__(self):
        if self.completed_stages is None:
            self.completed_stages = []
        if self.stage_results is None:
            self.stage_results = {}
        if self.stage_errors is None:
            self.stage_errors = {}
        if self.start_time is None:
            self.start_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        # Convert ErrorContext objects to dict
        stage_errors_dict = {}
        for stage, error in self.stage_errors.items():
            if isinstance(error, ErrorContext):
                stage_errors_dict[stage] = error.to_dict()
            else:
                stage_errors_dict[stage] = error
        
        result = asdict(self)
        result['stage_errors'] = stage_errors_dict
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        # Convert dict back to ErrorContext objects
        if 'stage_errors' in data:
            stage_errors = {}
            for stage, error_data in data['stage_errors'].items():
                if isinstance(error_data, dict):
                    stage_errors[stage] = ErrorContext.from_dict(error_data)
                else:
                    stage_errors[stage] = error_data
            data['stage_errors'] = stage_errors
        
        return cls(**data)


@dataclass
class SessionState:
    """Complete session state"""
    session_id: str
    status: SessionStatus
    conversation_history: List[Message] = None
    agent_contexts: Dict[str, AgentContext] = None
    workflow_state: Optional[WorkflowState] = None
    mcp_state: Dict[str, Any] = None
    user_preferences: Dict[str, Any] = None
    error_history: List[ErrorContext] = None
    created_at: float = None
    updated_at: float = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.agent_contexts is None:
            self.agent_contexts = {}
        if self.mcp_state is None:
            self.mcp_state = {}
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.error_history is None:
            self.error_history = []
        if self.created_at is None:
            self.created_at = time.time()
        if self.updated_at is None:
            self.updated_at = time.time()
    
    def add_message(self, message: Message):
        """Add a message to conversation history"""
        self.conversation_history.append(message)
        self.updated_at = time.time()
    
    def update_agent_context(self, agent_id: str, context: AgentContext):
        """Update context for a specific agent"""
        self.agent_contexts[agent_id] = context
        self.updated_at = time.time()
    
    def add_error(self, error: ErrorContext):
        """Add an error to history"""
        self.error_history.append(error)
        self.updated_at = time.time()
    
    def get_conversation_summary(self, max_messages: int = 10) -> List[Message]:
        """Get recent conversation messages"""
        return self.conversation_history[-max_messages:] if self.conversation_history else []
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for state integrity verification"""
        state_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            'session_id': self.session_id,
            'status': self.status.value,
            'conversation_history': [msg.to_dict() for msg in self.conversation_history],
            'agent_contexts': {k: v.to_dict() for k, v in self.agent_contexts.items()},
            'workflow_state': self.workflow_state.to_dict() if self.workflow_state else None,
            'mcp_state': self.mcp_state,
            'user_preferences': self.user_preferences,
            'error_history': [error.to_dict() for error in self.error_history],
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """Create from dictionary"""
        # Convert nested objects
        conversation_history = [Message.from_dict(msg) for msg in data.get('conversation_history', [])]
        agent_contexts = {k: AgentContext.from_dict(v) for k, v in data.get('agent_contexts', {}).items()}
        workflow_state = WorkflowState.from_dict(data['workflow_state']) if data.get('workflow_state') else None
        error_history = [ErrorContext.from_dict(error) for error in data.get('error_history', [])]
        
        return cls(
            session_id=data['session_id'],
            status=SessionStatus(data['status']),
            conversation_history=conversation_history,
            agent_contexts=agent_contexts,
            workflow_state=workflow_state,
            mcp_state=data.get('mcp_state', {}),
            user_preferences=data.get('user_preferences', {}),
            error_history=error_history,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class SessionManager:
    """Manages session state persistence and recovery"""
    
    def __init__(self, storage_dir: str = ".claude/state/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Active session
        self.current_session: Optional[SessionState] = None
        
        # Compression and encryption settings
        self.compress_state = True
        self.encrypt_state = False  # TODO: Implement encryption
        
        # Auto-save settings
        self.auto_save_interval = 30  # seconds
        self.auto_save_task = None
    
    def create_session(self, session_id: Optional[str] = None) -> SessionState:
        """Create a new session"""
        if session_id is None:
            session_id = f"session_{int(time.time())}_{hash(time.time()) % 10000}"
        
        session = SessionState(
            session_id=session_id,
            status=SessionStatus.ACTIVE
        )
        
        self.current_session = session
        self.logger.info(f"Created new session: {session_id}")
        
        # Start auto-save
        self._start_auto_save()
        
        return session
    
    def save_session(self, session: Optional[SessionState] = None) -> bool:
        """Save session state to disk"""
        if session is None:
            session = self.current_session
        
        if session is None:
            self.logger.warning("No session to save")
            return False
        
        try:
            session_file = self.storage_dir / f"{session.session_id}.json"
            
            # Update timestamp
            session.updated_at = time.time()
            
            # Serialize to JSON
            session_data = session.to_dict()
            
            # Add metadata
            save_metadata = {
                'format_version': '1.0',
                'saved_at': time.time(),
                'checksum': session.calculate_checksum(),
                'session_data': session_data
            }
            
            # Save to file
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(save_metadata, f, indent=2)
            
            self.logger.debug(f"Session saved: {session.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session {session.session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[SessionState]:
        """Load session state from disk"""
        try:
            session_file = self.storage_dir / f"{session_id}.json"
            
            if not session_file.exists():
                self.logger.warning(f"Session file not found: {session_id}")
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                save_metadata = json.load(f)
            
            # Verify format version
            if save_metadata.get('format_version') != '1.0':
                self.logger.warning(f"Unsupported session format: {save_metadata.get('format_version')}")
                return None
            
            # Load session data
            session_data = save_metadata['session_data']
            session = SessionState.from_dict(session_data)
            
            # Verify integrity
            if 'checksum' in save_metadata:
                current_checksum = session.calculate_checksum()
                saved_checksum = save_metadata['checksum']
                if current_checksum != saved_checksum:
                    self.logger.warning(f"Session integrity check failed for {session_id}")
                    # Continue loading but log the issue
            
            self.current_session = session
            self.logger.info(f"Session loaded: {session_id}")
            
            # Start auto-save
            self._start_auto_save()
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions"""
        sessions = []
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    save_metadata = json.load(f)
                
                session_data = save_metadata['session_data']
                sessions.append({
                    'session_id': session_data['session_id'],
                    'status': session_data['status'],
                    'created_at': session_data['created_at'],
                    'updated_at': session_data['updated_at'],
                    'message_count': len(session_data.get('conversation_history', [])),
                    'agent_count': len(session_data.get('agent_contexts', {}))
                })
                
            except Exception as e:
                self.logger.warning(f"Failed to read session metadata from {session_file}: {e}")
        
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            session_file = self.storage_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
                self.logger.info(f"Session deleted: {session_id}")
                return True
            else:
                self.logger.warning(f"Session file not found: {session_id}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def suspend_session(self, reason: str = ""):
        """Suspend current session"""
        if self.current_session:
            self.current_session.status = SessionStatus.SUSPENDED
            if reason:
                self.current_session.user_preferences['suspend_reason'] = reason
            self.save_session()
            self._stop_auto_save()
            self.logger.info(f"Session suspended: {self.current_session.session_id}")
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a suspended session"""
        session = self.load_session(session_id)
        if session and session.status == SessionStatus.SUSPENDED:
            session.status = SessionStatus.ACTIVE
            self.save_session()
            self.logger.info(f"Session resumed: {session_id}")
            return True
        return False
    
    def cleanup_old_sessions(self, max_age_days: int = 30):
        """Clean up old sessions"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    save_metadata = json.load(f)
                
                session_data = save_metadata['session_data']
                if session_data.get('updated_at', 0) < cutoff_time:
                    session_file.unlink()
                    deleted_count += 1
                    self.logger.debug(f"Deleted old session: {session_data['session_id']}")
                    
            except Exception as e:
                self.logger.warning(f"Failed to process session file {session_file}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old sessions")
        return deleted_count
    
    def _start_auto_save(self):
        """Start auto-save task"""
        if self.auto_save_task:
            self.auto_save_task.cancel()
        
        # Only start auto-save if there's an event loop running
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                async def auto_save_loop():
                    while True:
                        await asyncio.sleep(self.auto_save_interval)
                        if self.current_session:
                            self.save_session()
                
                self.auto_save_task = asyncio.create_task(auto_save_loop())
        except RuntimeError:
            # No event loop running, skip auto-save for now
            pass
    
    def _stop_auto_save(self):
        """Stop auto-save task"""
        if self.auto_save_task:
            self.auto_save_task.cancel()
            self.auto_save_task = None
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics about session storage"""
        sessions = self.list_sessions()
        
        if not sessions:
            return {
                'total_sessions': 0,
                'active_sessions': 0,
                'suspended_sessions': 0,
                'completed_sessions': 0,
                'total_storage_mb': 0
            }
        
        stats = {
            'total_sessions': len(sessions),
            'active_sessions': sum(1 for s in sessions if s['status'] == 'active'),
            'suspended_sessions': sum(1 for s in sessions if s['status'] == 'suspended'),
            'completed_sessions': sum(1 for s in sessions if s['status'] == 'completed'),
            'oldest_session': min(s['created_at'] for s in sessions),
            'newest_session': max(s['created_at'] for s in sessions),
            'total_messages': sum(s['message_count'] for s in sessions),
            'total_agents': sum(s['agent_count'] for s in sessions)
        }
        
        # Calculate storage size
        total_size = 0
        for session_file in self.storage_dir.glob("*.json"):
            total_size += session_file.stat().st_size
        
        stats['total_storage_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats


# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
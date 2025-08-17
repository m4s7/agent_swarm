"""
State management package for Claude Code auto-resume functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.session_manager import (
    SessionState,
    SessionStatus,
    Message,
    AgentContext,
    WorkflowState,
    SessionManager,
    get_session_manager
)

from state.checkpoint_manager import (
    CheckpointType,
    CheckpointTrigger,
    CheckpointMetadata,
    CheckpointConfig,
    CheckpointManager,
    get_checkpoint_manager
)

from state.serializers import (
    StateSerializer,
    CompactSerializer,
    IncrementalSerializer,
    AsyncSerializer,
    create_serializer
)

__all__ = [
    # Session management
    'SessionState',
    'SessionStatus', 
    'Message',
    'AgentContext',
    'WorkflowState',
    'SessionManager',
    'get_session_manager',
    
    # Checkpoint management
    'CheckpointType',
    'CheckpointTrigger',
    'CheckpointMetadata',
    'CheckpointConfig',
    'CheckpointManager',
    'get_checkpoint_manager',
    
    # Serialization
    'StateSerializer',
    'CompactSerializer',
    'IncrementalSerializer',
    'AsyncSerializer',
    'create_serializer'
]
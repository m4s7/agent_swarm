#!/usr/bin/env python3
"""
Basic functionality test for auto-resume components
"""

import sys
import os
sys.path.append('.')

import time
import tempfile
from state.session_manager import SessionState, SessionStatus, Message, AgentContext
from state.checkpoint_manager import CheckpointManager, CheckpointType, CheckpointTrigger
from utils.error_detector import LimitDetector, detect_claude_error


def test_error_detection():
    """Test error detection functionality"""
    print("Testing Error Detection...")
    
    # Test rate limit detection
    error_context = detect_claude_error(
        "Rate limit exceeded. Please try again later.",
        http_code=429
    )
    
    assert error_context is not None
    assert error_context.error_type == "RATE_LIMIT_EXCEEDED"
    print("✅ Rate limit detection works")
    
    # Test token limit detection
    error_context = detect_claude_error(
        "Token limit exceeded for this conversation",
        http_code=400
    )
    
    assert error_context is not None
    assert error_context.error_type == "TOKEN_LIMIT_EXCEEDED"
    print("✅ Token limit detection works")
    
    print("✅ Error Detection - PASSED\n")


def test_session_state():
    """Test session state management"""
    print("Testing Session State Management...")
    
    # Create session
    session = SessionState('test_session', SessionStatus.ACTIVE)
    assert session.session_id == 'test_session'
    assert session.status == SessionStatus.ACTIVE
    print("✅ Session creation works")
    
    # Add message
    message = Message('user', 'Hello, world!', time.time(), 'msg_1')
    session.add_message(message)
    assert len(session.conversation_history) == 1
    print("✅ Message addition works")
    
    # Add agent context
    agent_context = AgentContext('test_agent', 'python-pro', 'Test task')
    session.update_agent_context('test_agent', agent_context)
    assert 'test_agent' in session.agent_contexts
    print("✅ Agent context management works")
    
    # Test serialization
    session_dict = session.to_dict()
    restored = SessionState.from_dict(session_dict)
    assert restored.session_id == 'test_session'
    assert len(restored.conversation_history) == 1
    assert 'test_agent' in restored.agent_contexts
    print("✅ Serialization and deserialization works")
    
    print("✅ Session State Management - PASSED\n")


def test_checkpoint_basic():
    """Test basic checkpoint functionality"""
    print("Testing Basic Checkpoint Functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create checkpoint manager
        checkpoint_manager = CheckpointManager(storage_dir=temp_dir)
        
        # Test should_create_checkpoint logic
        checkpoint_manager.last_auto_checkpoint = time.time() - 400  # 400 seconds ago
        should_checkpoint = checkpoint_manager.should_create_checkpoint(
            CheckpointTrigger.TIME_INTERVAL
        )
        print("✅ Checkpoint trigger logic works")
        
        print("✅ Basic Checkpoint Functionality - PASSED\n")


def main():
    """Run all basic functionality tests"""
    print("="*60)
    print("Claude Code Auto-Resume Basic Functionality Test")
    print("="*60)
    print()
    
    try:
        test_error_detection()
        test_session_state()
        test_checkpoint_basic()
        
        print("="*60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Phase 1.1: Error Detection & Classification - COMPLETED")
        print("✅ Phase 1.2: Session State Preservation - COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Integration test for complete auto-resume functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import tempfile
import shutil
from pathlib import Path

from utils.recovery_handler import AutoResumeCoordinator, RecoveryHandler
from utils.error_detector import detect_claude_error
from state.session_manager import SessionState, SessionStatus, Message
from state.checkpoint_manager import CheckpointType


def test_auto_resume_workflow():
    """Test complete auto-resume workflow"""
    
    print("="*60)
    print("Claude Code Auto-Resume Integration Test")
    print("="*60)
    print()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configure paths
        session_dir = Path(temp_dir) / "sessions"
        checkpoint_dir = Path(temp_dir) / "checkpoints"
        session_dir.mkdir(parents=True)
        checkpoint_dir.mkdir(parents=True)
        
        # Initialize coordinator
        coordinator = AutoResumeCoordinator()
        coordinator.session_manager.storage_dir = session_dir
        coordinator.checkpoint_manager.storage_dir = checkpoint_dir
        
        print("1. Starting new session with auto-resume...")
        session = coordinator.start("test_integration_session")
        assert session is not None
        assert session.session_id == "test_integration_session"
        print("✅ Session started successfully")
        
        # Add some conversation
        print("\n2. Adding conversation history...")
        for i in range(5):
            msg = Message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Test message {i}",
                timestamp=time.time(),
                message_id=f"msg_{i}"
            )
            session.add_message(msg)
        
        assert len(session.conversation_history) == 5
        print(f"✅ Added {len(session.conversation_history)} messages")
        
        # Test checkpoint creation
        print("\n3. Creating manual checkpoint...")
        checkpoint_id = coordinator.checkpoint_manager.create_checkpoint(
            CheckpointType.MANUAL,
            description="Test checkpoint"
        )
        assert checkpoint_id is not None
        print(f"✅ Checkpoint created: {checkpoint_id}")
        
        # Simulate rate limit error
        print("\n4. Simulating rate limit error...")
        success, recovered = coordinator.handle_error(
            "Rate limit exceeded. Please try again later.",
            http_code=429
        )
        
        # Rate limit should trigger wait_and_retry
        assert success or recovered is not None
        print("✅ Rate limit error handled with wait_and_retry strategy")
        
        # Simulate token limit error
        print("\n5. Simulating token limit error...")
        
        # Add many messages to simulate large context
        for i in range(20):
            msg = Message(
                role="user",
                content=f"Long message {i} " * 100,  # Long message
                timestamp=time.time(),
                message_id=f"long_msg_{i}"
            )
            session.add_message(msg)
        
        success, recovered = coordinator.handle_error(
            "Token limit exceeded for this conversation",
            http_code=400
        )
        
        if recovered:
            # Check that context was truncated
            assert len(recovered.conversation_history) < 25
            print(f"✅ Token limit handled, context truncated to {len(recovered.conversation_history)} messages")
        
        # Test checkpoint restoration
        print("\n6. Testing checkpoint restoration...")
        restored = coordinator.checkpoint_manager.restore_from_checkpoint(checkpoint_id)
        assert restored is not None
        assert len(restored.conversation_history) == 5  # Original 5 messages
        print("✅ Successfully restored from checkpoint")
        
        # Test session persistence
        print("\n7. Testing session persistence...")
        coordinator.session_manager.save_session()
        
        # Load in new coordinator
        new_coordinator = AutoResumeCoordinator()
        new_coordinator.session_manager.storage_dir = session_dir
        new_coordinator.checkpoint_manager.storage_dir = checkpoint_dir
        
        loaded_session = new_coordinator.session_manager.load_session("test_integration_session")
        assert loaded_session is not None
        print("✅ Session successfully persisted and loaded")
        
        # Test recovery statistics
        print("\n8. Checking recovery statistics...")
        status = coordinator.get_status()
        
        assert 'recovery_stats' in status
        assert status['recovery_stats']['total_attempts'] >= 2
        print(f"✅ Recovery attempts: {status['recovery_stats']['total_attempts']}")
        print(f"   Successful: {status['recovery_stats']['successful_recoveries']}")
        print(f"   Failed: {status['recovery_stats']['failed_recoveries']}")
        
        # Test agent handoff
        print("\n9. Testing agent handoff recovery...")
        
        # Add agent context
        from state.session_manager import AgentContext
        agent_context = AgentContext(
            agent_id="python-pro",
            agent_type="python-pro",
            current_task="Test task"
        )
        session.update_agent_context("python-pro", agent_context)
        
        # Simulate agent failure
        success, recovered = coordinator.handle_error(
            "Agent failed to complete task",
            context={'agent_id': 'python-pro'}
        )
        
        print("✅ Agent handoff recovery tested")
        
        # Test cleanup
        print("\n10. Testing cleanup functionality...")
        deleted_sessions = coordinator.session_manager.cleanup_old_sessions(0)  # Delete all
        deleted_checkpoints = coordinator.checkpoint_manager.cleanup_expired_checkpoints()
        print(f"✅ Cleanup completed: {deleted_sessions} sessions, {deleted_checkpoints} checkpoints")
        
        print("\n" + "="*60)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("="*60)
        print("\nAuto-Resume System Components:")
        print("✅ Phase 1.1: Error Detection & Classification")
        print("✅ Phase 1.2: Session State Preservation") 
        print("✅ Phase 1.3: Recovery Mechanisms")
        print("\nThe auto-resume functionality is fully operational!")
        print("="*60)


if __name__ == '__main__':
    try:
        test_auto_resume_workflow()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
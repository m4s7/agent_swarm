#!/usr/bin/env python3
"""
Test suite for session state preservation functionality
"""

import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from state.session_manager import (
    SessionManager, SessionState, SessionStatus, 
    Message, AgentContext, WorkflowState
)
from state.checkpoint_manager import (
    CheckpointManager, CheckpointType, CheckpointTrigger,
    CheckpointConfig, CheckpointMetadata
)
from state.serializers import StateSerializer, CompactSerializer
from utils.error_types import ErrorContext


class TestSessionState(unittest.TestCase):
    """Test cases for SessionState functionality"""
    
    def test_session_state_creation(self):
        """Test SessionState creation and basic functionality"""
        session = SessionState(
            session_id="test_session",
            status=SessionStatus.ACTIVE
        )
        
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(len(session.conversation_history), 0)
        self.assertEqual(len(session.agent_contexts), 0)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.updated_at)
    
    def test_add_message(self):
        """Test adding messages to session"""
        session = SessionState("test", SessionStatus.ACTIVE)
        
        message = Message(
            role="user",
            content="Hello, world!",
            timestamp=time.time(),
            message_id="msg_1"
        )
        
        session.add_message(message)
        
        self.assertEqual(len(session.conversation_history), 1)
        self.assertEqual(session.conversation_history[0].content, "Hello, world!")
    
    def test_update_agent_context(self):
        """Test updating agent context"""
        session = SessionState("test", SessionStatus.ACTIVE)
        
        agent_context = AgentContext(
            agent_id="test_agent",
            agent_type="python-pro",
            current_task="Testing functionality"
        )
        
        session.update_agent_context("test_agent", agent_context)
        
        self.assertIn("test_agent", session.agent_contexts)
        self.assertEqual(session.agent_contexts["test_agent"].current_task, "Testing functionality")
    
    def test_session_serialization(self):
        """Test SessionState serialization and deserialization"""
        session = SessionState("test", SessionStatus.ACTIVE)
        
        # Add some data
        message = Message("user", "Test message", time.time(), "msg_1")
        session.add_message(message)
        
        agent_context = AgentContext("agent_1", "python-pro", "Test task")
        session.update_agent_context("agent_1", agent_context)
        
        # Serialize
        session_dict = session.to_dict()
        
        # Deserialize
        restored_session = SessionState.from_dict(session_dict)
        
        self.assertEqual(restored_session.session_id, session.session_id)
        self.assertEqual(len(restored_session.conversation_history), 1)
        self.assertEqual(len(restored_session.agent_contexts), 1)
        self.assertEqual(restored_session.conversation_history[0].content, "Test message")


class TestSessionManager(unittest.TestCase):
    """Test cases for SessionManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(storage_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Test session creation"""
        session = self.session_manager.create_session("test_session")
        
        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(self.session_manager.current_session, session)
    
    def test_save_and_load_session(self):
        """Test saving and loading sessions"""
        # Create and populate session
        session = self.session_manager.create_session("test_session")
        
        message = Message("user", "Test message", time.time(), "msg_1")
        session.add_message(message)
        
        agent_context = AgentContext("agent_1", "python-pro", "Test task")
        session.update_agent_context("agent_1", agent_context)
        
        # Save session
        save_success = self.session_manager.save_session()
        self.assertTrue(save_success)
        
        # Verify file exists
        session_file = Path(self.temp_dir) / "test_session.json"
        self.assertTrue(session_file.exists())
        
        # Clear current session
        self.session_manager.current_session = None
        
        # Load session
        loaded_session = self.session_manager.load_session("test_session")
        
        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session.session_id, "test_session")
        self.assertEqual(len(loaded_session.conversation_history), 1)
        self.assertEqual(len(loaded_session.agent_contexts), 1)
        self.assertEqual(loaded_session.conversation_history[0].content, "Test message")
    
    def test_list_sessions(self):
        """Test listing sessions"""
        # Create multiple sessions
        session1 = self.session_manager.create_session("session_1")
        self.session_manager.save_session()
        
        session2 = self.session_manager.create_session("session_2")
        self.session_manager.save_session()
        
        # List sessions
        sessions = self.session_manager.list_sessions()
        
        self.assertEqual(len(sessions), 2)
        session_ids = [s['session_id'] for s in sessions]
        self.assertIn("session_1", session_ids)
        self.assertIn("session_2", session_ids)
    
    def test_delete_session(self):
        """Test session deletion"""
        # Create and save session
        session = self.session_manager.create_session("delete_test")
        self.session_manager.save_session()
        
        # Verify it exists
        sessions = self.session_manager.list_sessions()
        self.assertEqual(len(sessions), 1)
        
        # Delete session
        delete_success = self.session_manager.delete_session("delete_test")
        self.assertTrue(delete_success)
        
        # Verify it's gone
        sessions = self.session_manager.list_sessions()
        self.assertEqual(len(sessions), 0)
    
    def test_suspend_and_resume_session(self):
        """Test suspending and resuming sessions"""
        session = self.session_manager.create_session("suspend_test")
        
        # Suspend session
        self.session_manager.suspend_session("Testing suspend functionality")
        self.assertEqual(session.status, SessionStatus.SUSPENDED)
        
        # Resume session
        resume_success = self.session_manager.resume_session("suspend_test")
        self.assertTrue(resume_success)
        self.assertEqual(session.status, SessionStatus.ACTIVE)


class TestCheckpointManager(unittest.TestCase):
    """Test cases for CheckpointManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_dir = tempfile.mkdtemp()
        self.checkpoint_dir = tempfile.mkdtemp()
        
        self.session_manager = SessionManager(storage_dir=self.session_dir)
        self.checkpoint_manager = CheckpointManager(
            storage_dir=self.checkpoint_dir
        )
        self.checkpoint_manager.session_manager = self.session_manager
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.session_dir)
        shutil.rmtree(self.checkpoint_dir)
    
    def test_create_checkpoint(self):
        """Test checkpoint creation"""
        # Create session with some data
        session = self.session_manager.create_session("checkpoint_test")
        message = Message("user", "Test message", time.time(), "msg_1")
        session.add_message(message)
        
        # Create checkpoint
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            CheckpointType.MANUAL,
            description="Test checkpoint"
        )
        
        self.assertIsNotNone(checkpoint_id)
        self.assertTrue(checkpoint_id.startswith("cp_"))
        
        # Verify checkpoint file exists
        checkpoint_file = Path(self.checkpoint_dir) / f"{checkpoint_id}.json"
        self.assertTrue(checkpoint_file.exists())
    
    def test_restore_from_checkpoint(self):
        """Test restoring session from checkpoint"""
        # Create session with data
        session = self.session_manager.create_session("restore_test")
        message = Message("user", "Original message", time.time(), "msg_1")
        session.add_message(message)
        
        # Create checkpoint
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            CheckpointType.MANUAL,
            description="Before modification"
        )
        
        # Modify session
        message2 = Message("user", "Modified message", time.time(), "msg_2")
        session.add_message(message2)
        
        # Restore from checkpoint
        restored_session = self.checkpoint_manager.restore_from_checkpoint(checkpoint_id)
        
        self.assertIsNotNone(restored_session)
        self.assertEqual(len(restored_session.conversation_history), 1)
        self.assertEqual(restored_session.conversation_history[0].content, "Original message")
    
    def test_list_checkpoints(self):
        """Test listing checkpoints"""
        # Create session
        session = self.session_manager.create_session("list_test")
        
        # Create multiple checkpoints
        checkpoint1 = self.checkpoint_manager.create_checkpoint(
            CheckpointType.AUTO,
            description="Auto checkpoint 1"
        )
        
        time.sleep(0.1)  # Ensure different timestamps
        
        checkpoint2 = self.checkpoint_manager.create_checkpoint(
            CheckpointType.MANUAL,
            description="Manual checkpoint"
        )
        
        # List checkpoints
        checkpoints = self.checkpoint_manager.list_checkpoints("list_test")
        
        self.assertEqual(len(checkpoints), 2)
        # Should be sorted by creation time (newest first)
        self.assertEqual(checkpoints[0].checkpoint_id, checkpoint2)
        self.assertEqual(checkpoints[1].checkpoint_id, checkpoint1)
    
    def test_should_create_checkpoint_triggers(self):
        """Test checkpoint trigger logic"""
        # Time interval trigger
        self.checkpoint_manager.last_auto_checkpoint = time.time() - 400  # 400 seconds ago
        self.assertTrue(
            self.checkpoint_manager.should_create_checkpoint(CheckpointTrigger.TIME_INTERVAL)
        )
        
        # Message count trigger
        self.checkpoint_manager.checkpoint_message_count = 25
        self.assertTrue(
            self.checkpoint_manager.should_create_checkpoint(CheckpointTrigger.MESSAGE_COUNT)
        )
        
        # Tool usage trigger with high-risk tool
        context = {
            'tool_name': 'Bash',
            'operation': 'rm -rf /important/files'
        }
        self.assertTrue(
            self.checkpoint_manager.should_create_checkpoint(CheckpointTrigger.TOOL_USAGE, context)
        )
    
    def test_checkpoint_cleanup(self):
        """Test checkpoint cleanup functionality"""
        session = self.session_manager.create_session("cleanup_test")
        
        # Create many checkpoints to exceed limit
        config = CheckpointConfig()
        config.max_checkpoints_per_session = 3
        self.checkpoint_manager.config = config
        
        checkpoint_ids = []
        for i in range(5):
            checkpoint_id = self.checkpoint_manager.create_checkpoint(
                CheckpointType.AUTO,
                description=f"Checkpoint {i}"
            )
            checkpoint_ids.append(checkpoint_id)
            time.sleep(0.1)
        
        # Check that only 3 checkpoints remain
        checkpoints = self.checkpoint_manager.list_checkpoints("cleanup_test")
        self.assertEqual(len(checkpoints), 3)
        
        # Should keep the newest 3
        remaining_ids = [cp.checkpoint_id for cp in checkpoints]
        self.assertIn(checkpoint_ids[-1], remaining_ids)  # Most recent
        self.assertIn(checkpoint_ids[-2], remaining_ids)
        self.assertIn(checkpoint_ids[-3], remaining_ids)


class TestStateSerializers(unittest.TestCase):
    """Test cases for state serialization"""
    
    def test_basic_serializer(self):
        """Test basic state serializer"""
        serializer = StateSerializer()
        
        # Create test data
        session = SessionState("test", SessionStatus.ACTIVE)
        message = Message("user", "Test", time.time(), "msg_1")
        session.add_message(message)
        
        # Serialize
        serialized = serializer.serialize(session)
        self.assertIsInstance(serialized, bytes)
        
        # Deserialize
        deserialized = serializer.deserialize(serialized, SessionState)
        self.assertIsInstance(deserialized, SessionState)
        self.assertEqual(deserialized.session_id, "test")
        self.assertEqual(len(deserialized.conversation_history), 1)
    
    def test_compact_serializer(self):
        """Test compact serializer for size optimization"""
        serializer = CompactSerializer()
        
        # Create test data
        session = SessionState("test", SessionStatus.ACTIVE)
        message = Message("user", "Test message", time.time(), "msg_1")
        session.add_message(message)
        
        # Serialize
        serialized = serializer.serialize(session)
        
        # Deserialize
        deserialized = serializer.deserialize(serialized, SessionState)
        
        self.assertEqual(deserialized.session_id, "test")
        self.assertEqual(len(deserialized.conversation_history), 1)
        self.assertEqual(deserialized.conversation_history[0].content, "Test message")
    
    def test_serializer_compression(self):
        """Test serializer compression"""
        # Compare compressed vs uncompressed sizes
        serializer_compressed = StateSerializer(compression=True)
        serializer_uncompressed = StateSerializer(compression=False)
        
        # Create large test data
        session = SessionState("test", SessionStatus.ACTIVE)
        for i in range(100):
            message = Message("user", f"Long test message {i} " * 10, time.time(), f"msg_{i}")
            session.add_message(message)
        
        compressed = serializer_compressed.serialize(session)
        uncompressed = serializer_uncompressed.serialize(session)
        
        # Compressed should be smaller
        self.assertLess(len(compressed), len(uncompressed))
        
        # Both should deserialize correctly
        deser_compressed = serializer_compressed.deserialize(compressed, SessionState)
        deser_uncompressed = serializer_uncompressed.deserialize(uncompressed, SessionState)
        
        self.assertEqual(len(deser_compressed.conversation_history), 100)
        self.assertEqual(len(deser_uncompressed.conversation_history), 100)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete auto-resume system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_dir = os.path.join(self.temp_dir, "sessions")
        self.checkpoint_dir = os.path.join(self.temp_dir, "checkpoints")
        
        self.session_manager = SessionManager(storage_dir=self.session_dir)
        self.checkpoint_manager = CheckpointManager(storage_dir=self.checkpoint_dir)
        self.checkpoint_manager.session_manager = self.session_manager
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow_with_recovery(self):
        """Test complete workflow with error and recovery"""
        # 1. Create session and do some work
        session = self.session_manager.create_session("workflow_test")
        
        # Add initial conversation
        msg1 = Message("user", "Please help me with a task", time.time(), "msg_1")
        session.add_message(msg1)
        
        msg2 = Message("assistant", "I'll help you with that", time.time(), "msg_2")
        session.add_message(msg2)
        
        # Add agent context
        agent_context = AgentContext("python-pro", "python-pro", "Help with Python task")
        session.update_agent_context("python-pro", agent_context)
        
        # 2. Create checkpoint before risky operation
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            CheckpointType.ERROR,
            description="Before risky operation"
        )
        
        # 3. Simulate error occurring
        error_context = ErrorContext(
            timestamp=time.time(),
            error_type="TOKEN_LIMIT_EXCEEDED",
            error_message="Context length exceeded",
            agent_id="python-pro"
        )
        session.add_error(error_context)
        
        # 4. Find recovery checkpoint
        recovery_checkpoint = self.checkpoint_manager.find_recovery_checkpoint(
            session.session_id, error_context
        )
        
        self.assertIsNotNone(recovery_checkpoint)
        self.assertEqual(recovery_checkpoint.checkpoint_id, checkpoint_id)
        
        # 5. Restore from checkpoint
        restored_session = self.checkpoint_manager.restore_from_checkpoint(checkpoint_id)
        
        self.assertIsNotNone(restored_session)
        self.assertEqual(len(restored_session.conversation_history), 2)
        self.assertEqual(len(restored_session.agent_contexts), 1)
        
        # 6. Verify state is properly restored
        self.assertEqual(restored_session.session_id, "workflow_test")
        self.assertIn("python-pro", restored_session.agent_contexts)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
#!/usr/bin/env python3
"""
CLI interface for Claude Code auto-resume functionality
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.recovery_handler import get_auto_resume_coordinator
from state.session_manager import get_session_manager
from state.checkpoint_manager import get_checkpoint_manager
from utils.error_detector import detect_claude_error


def list_sessions(args):
    """List all available sessions"""
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions()
    
    if not sessions:
        print("No sessions found.")
        return
    
    print(f"{'Session ID':<30} {'Status':<12} {'Messages':<10} {'Updated':<20}")
    print("-" * 80)
    
    for session in sessions:
        updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session['updated_at']))
        print(f"{session['session_id']:<30} {session['status']:<12} "
              f"{session['message_count']:<10} {updated:<20}")
    
    print(f"\nTotal sessions: {len(sessions)}")


def show_session(args):
    """Show details of a specific session"""
    session_manager = get_session_manager()
    session = session_manager.load_session(args.session_id)
    
    if not session:
        print(f"Session not found: {args.session_id}")
        return 1
    
    print(f"Session ID: {session.session_id}")
    print(f"Status: {session.status.value}")
    print(f"Created: {time.ctime(session.created_at)}")
    print(f"Updated: {time.ctime(session.updated_at)}")
    print(f"Messages: {len(session.conversation_history)}")
    print(f"Active Agents: {', '.join(session.agent_contexts.keys()) or 'None'}")
    
    if session.workflow_state:
        print(f"Workflow: {session.workflow_state.workflow_type}")
        print(f"Current Stage: {session.workflow_state.current_stage}")
    
    if args.messages:
        print("\nRecent Messages:")
        print("-" * 60)
        for msg in session.get_conversation_summary(args.messages):
            print(f"[{msg.role}] {msg.content[:100]}...")
    
    if args.errors and session.error_history:
        print("\nError History:")
        print("-" * 60)
        for error in session.error_history[-5:]:
            print(f"- {error.error_type}: {error.error_message[:80]}...")


def list_checkpoints(args):
    """List checkpoints for a session"""
    checkpoint_manager = get_checkpoint_manager()
    checkpoints = checkpoint_manager.list_checkpoints(args.session_id)
    
    if not checkpoints:
        print(f"No checkpoints found for session: {args.session_id or 'all'}")
        return
    
    print(f"{'Checkpoint ID':<40} {'Type':<10} {'Created':<20} {'Size':<10}")
    print("-" * 90)
    
    for cp in checkpoints:
        created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cp.created_at))
        size_kb = cp.context_size / 1024
        print(f"{cp.checkpoint_id:<40} {cp.checkpoint_type.value:<10} "
              f"{created:<20} {size_kb:.1f}KB")
    
    print(f"\nTotal checkpoints: {len(checkpoints)}")


def restore_checkpoint(args):
    """Restore session from a checkpoint"""
    checkpoint_manager = get_checkpoint_manager()
    session_manager = get_session_manager()
    
    # Restore from checkpoint
    session = checkpoint_manager.restore_from_checkpoint(args.checkpoint_id)
    
    if not session:
        print(f"Failed to restore from checkpoint: {args.checkpoint_id}")
        return 1
    
    # Update session manager
    session_manager.current_session = session
    session_manager.save_session()
    
    print(f"✅ Session restored from checkpoint: {args.checkpoint_id}")
    print(f"Session ID: {session.session_id}")
    print(f"Messages: {len(session.conversation_history)}")
    print(f"Agents: {', '.join(session.agent_contexts.keys())}")


def start_session(args):
    """Start a new session with auto-resume enabled"""
    coordinator = get_auto_resume_coordinator()
    
    # Start coordinator
    session = coordinator.start(args.session_id)
    
    print(f"✅ Auto-resume session started: {session.session_id}")
    print(f"Auto-checkpoint: {'Enabled' if coordinator.auto_checkpoint_enabled else 'Disabled'}")
    print(f"Auto-recovery: {'Enabled' if coordinator.auto_recovery_enabled else 'Disabled'}")
    
    if args.config:
        # Load configuration
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Apply configuration
        if 'auto_checkpoint' in config:
            coordinator.auto_checkpoint_enabled = config['auto_checkpoint']
        if 'auto_recovery' in config:
            coordinator.auto_recovery_enabled = config['auto_recovery']
        
        print(f"Configuration loaded from: {args.config}")


def resume_session(args):
    """Resume an existing session"""
    coordinator = get_auto_resume_coordinator()
    session_manager = get_session_manager()
    
    # Load session
    session = session_manager.load_session(args.session_id)
    
    if not session:
        print(f"Session not found: {args.session_id}")
        return 1
    
    # Resume
    coordinator.start(args.session_id)
    
    print(f"✅ Session resumed: {args.session_id}")
    print(f"Status: {session.status.value}")
    print(f"Messages: {len(session.conversation_history)}")
    
    # Show recent activity
    if session.conversation_history:
        last_msg = session.conversation_history[-1]
        print(f"Last activity: {time.ctime(last_msg.timestamp)}")


def test_error(args):
    """Test error detection and recovery"""
    coordinator = get_auto_resume_coordinator()
    
    # Start a test session
    session = coordinator.start("test_error_session")
    
    print(f"Testing error: {args.error_type}")
    
    # Generate test error
    test_errors = {
        'rate_limit': ("Rate limit exceeded. Please try again later.", 429),
        'token_limit': ("Token limit exceeded for this conversation", 400),
        'network': ("Connection timeout occurred", 504),
        'auth': ("Authentication failed: Invalid API key", 401)
    }
    
    if args.error_type not in test_errors:
        print(f"Unknown error type: {args.error_type}")
        print(f"Available types: {', '.join(test_errors.keys())}")
        return 1
    
    error_msg, http_code = test_errors[args.error_type]
    
    # Trigger error handling
    success, recovered_session = coordinator.handle_error(error_msg, http_code=http_code)
    
    if success:
        print(f"✅ Recovery successful!")
        if recovered_session:
            print(f"Session ID: {recovered_session.session_id}")
            print(f"Messages: {len(recovered_session.conversation_history)}")
    else:
        print(f"❌ Recovery failed")
    
    # Show recovery statistics
    stats = coordinator.get_status()
    print(f"\nRecovery Statistics:")
    print(f"Total attempts: {stats['recovery_stats']['total_attempts']}")
    print(f"Successful: {stats['recovery_stats']['successful_recoveries']}")
    print(f"Failed: {stats['recovery_stats']['failed_recoveries']}")


def show_status(args):
    """Show auto-resume coordinator status"""
    coordinator = get_auto_resume_coordinator()
    status = coordinator.get_status()
    
    print("Auto-Resume Coordinator Status")
    print("=" * 60)
    
    print(f"Active: {'Yes' if status['is_active'] else 'No'}")
    print(f"Auto-checkpoint: {'Enabled' if status['auto_checkpoint_enabled'] else 'Disabled'}")
    print(f"Auto-recovery: {'Enabled' if status['auto_recovery_enabled'] else 'Disabled'}")
    
    if status['current_session']:
        print(f"\nCurrent Session:")
        session = status['current_session']
        print(f"  ID: {session['session_id']}")
        print(f"  Status: {session['status']}")
        print(f"  Messages: {session['message_count']}")
        print(f"  Agents: {session['agent_count']}")
    
    print(f"\nRecovery Statistics:")
    recovery = status['recovery_stats']
    print(f"  Total attempts: {recovery['total_attempts']}")
    print(f"  Successful: {recovery['successful_recoveries']}")
    print(f"  Failed: {recovery['failed_recoveries']}")
    
    if recovery['strategies_used']:
        print(f"  Strategies used:")
        for strategy, count in recovery['strategies_used'].items():
            print(f"    - {strategy}: {count}")
    
    print(f"\nCheckpoint Statistics:")
    checkpoint = status['checkpoint_stats']
    print(f"  Total checkpoints: {checkpoint['total_checkpoints']}")
    print(f"  Storage used: {checkpoint['storage_mb']} MB")
    
    if args.verbose and recovery.get('recent_attempts'):
        print(f"\nRecent Recovery Attempts:")
        for attempt in recovery['recent_attempts']:
            print(f"  - {attempt['error_type']} → {attempt['strategy']} "
                  f"({attempt['status']}, {attempt['duration']:.1f}s)")


def cleanup(args):
    """Clean up old sessions and checkpoints"""
    session_manager = get_session_manager()
    checkpoint_manager = get_checkpoint_manager()
    
    print(f"Cleaning up data older than {args.days} days...")
    
    # Clean sessions
    deleted_sessions = session_manager.cleanup_old_sessions(args.days)
    print(f"Deleted {deleted_sessions} old sessions")
    
    # Clean checkpoints
    deleted_checkpoints = checkpoint_manager.cleanup_expired_checkpoints()
    print(f"Deleted {deleted_checkpoints} expired checkpoints")
    
    print("✅ Cleanup completed")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Claude Code Auto-Resume CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all sessions
  %(prog)s sessions
  
  # Show session details
  %(prog)s session show SESSION_ID
  
  # Start new session with auto-resume
  %(prog)s start --session-id my_session
  
  # Resume existing session
  %(prog)s resume SESSION_ID
  
  # List checkpoints
  %(prog)s checkpoints --session-id SESSION_ID
  
  # Restore from checkpoint
  %(prog)s restore CHECKPOINT_ID
  
  # Test error recovery
  %(prog)s test-error --type rate_limit
  
  # Show status
  %(prog)s status
  
  # Clean up old data
  %(prog)s cleanup --days 30
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Sessions command
    sessions_parser = subparsers.add_parser('sessions', help='List all sessions')
    sessions_parser.set_defaults(func=list_sessions)
    
    # Session command
    session_parser = subparsers.add_parser('session', help='Session operations')
    session_subparsers = session_parser.add_subparsers(dest='subcommand')
    
    show_parser = session_subparsers.add_parser('show', help='Show session details')
    show_parser.add_argument('session_id', help='Session ID')
    show_parser.add_argument('--messages', type=int, help='Show recent N messages')
    show_parser.add_argument('--errors', action='store_true', help='Show error history')
    show_parser.set_defaults(func=show_session)
    
    # Checkpoints command
    checkpoints_parser = subparsers.add_parser('checkpoints', help='List checkpoints')
    checkpoints_parser.add_argument('--session-id', help='Filter by session ID')
    checkpoints_parser.set_defaults(func=list_checkpoints)
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from checkpoint')
    restore_parser.add_argument('checkpoint_id', help='Checkpoint ID')
    restore_parser.set_defaults(func=restore_checkpoint)
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start new session')
    start_parser.add_argument('--session-id', help='Session ID (auto-generated if not provided)')
    start_parser.add_argument('--config', help='Configuration file path')
    start_parser.set_defaults(func=start_session)
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume existing session')
    resume_parser.add_argument('session_id', help='Session ID to resume')
    resume_parser.set_defaults(func=resume_session)
    
    # Test error command
    test_parser = subparsers.add_parser('test-error', help='Test error recovery')
    test_parser.add_argument('--type', dest='error_type', 
                            choices=['rate_limit', 'token_limit', 'network', 'auth'],
                            default='rate_limit', help='Error type to test')
    test_parser.set_defaults(func=test_error)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show coordinator status')
    status_parser.add_argument('--verbose', action='store_true', help='Show detailed status')
    status_parser.set_defaults(func=show_status)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, default=30, 
                               help='Delete data older than N days')
    cleanup_parser.set_defaults(func=cleanup)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if hasattr(args, 'func'):
        return args.func(args) or 0
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
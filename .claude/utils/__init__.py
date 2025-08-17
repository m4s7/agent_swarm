"""
Utilities package for Claude Code auto-resume functionality
"""

from .error_types import (
    ErrorSeverity,
    RecoveryStrategy,
    ErrorPattern,
    ErrorContext,
    ERROR_PATTERNS
)

from .error_detector import (
    LimitDetector,
    detect_claude_error
)

__all__ = [
    'ErrorSeverity',
    'RecoveryStrategy',
    'ErrorPattern',
    'ErrorContext',
    'ERROR_PATTERNS',
    'LimitDetector',
    'detect_claude_error'
]
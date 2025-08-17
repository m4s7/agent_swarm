"""
Error type definitions for Claude Code auto-resume functionality
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    WAIT_AND_RETRY = "wait_and_retry"
    TRUNCATE_CONTEXT = "truncate_context"
    CHECKPOINT_AND_RETRY = "checkpoint_and_retry"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    AGENT_HANDOFF = "agent_handoff"
    GRACEFUL_DEGRADATION = "graceful_degradation"


@dataclass
class ErrorPattern:
    """Pattern definition for error detection"""
    error_type: str
    keywords: list[str]
    regex_patterns: list[str]
    http_codes: list[int]
    severity: ErrorSeverity
    recovery_strategy: RecoveryStrategy
    retry_count: int = 3
    backoff_multiplier: float = 2.0
    max_wait_time: float = 300.0  # 5 minutes
    context_preservation: bool = True


# Predefined error patterns
ERROR_PATTERNS = {
    "RATE_LIMIT_EXCEEDED": ErrorPattern(
        error_type="RATE_LIMIT_EXCEEDED",
        keywords=["rate limit", "rate_limit_exceeded", "too many requests", "quota exceeded"],
        regex_patterns=[r"rate\s*limit", r"429\s*error", r"quota.*exceeded"],
        http_codes=[429],
        severity=ErrorSeverity.MEDIUM,
        recovery_strategy=RecoveryStrategy.WAIT_AND_RETRY,
        retry_count=5,
        backoff_multiplier=2.0,
        max_wait_time=600.0,
        context_preservation=True
    ),
    
    "TOKEN_LIMIT_EXCEEDED": ErrorPattern(
        error_type="TOKEN_LIMIT_EXCEEDED",
        keywords=["token limit", "context_length_exceeded", "max_tokens", "context too long"],
        regex_patterns=[r"token.*limit", r"context.*length", r"max.*tokens"],
        http_codes=[400],
        severity=ErrorSeverity.HIGH,
        recovery_strategy=RecoveryStrategy.TRUNCATE_CONTEXT,
        retry_count=3,
        backoff_multiplier=1.0,
        max_wait_time=60.0,
        context_preservation=True
    ),
    
    "NETWORK_TIMEOUT": ErrorPattern(
        error_type="NETWORK_TIMEOUT",
        keywords=["timeout", "connection timeout", "read timeout", "network error"],
        regex_patterns=[r"timeout", r"connection.*error", r"network.*error"],
        http_codes=[408, 504, 502, 503],
        severity=ErrorSeverity.MEDIUM,
        recovery_strategy=RecoveryStrategy.CHECKPOINT_AND_RETRY,
        retry_count=3,
        backoff_multiplier=1.5,
        max_wait_time=120.0,
        context_preservation=True
    ),
    
    "API_QUOTA_EXHAUSTED": ErrorPattern(
        error_type="API_QUOTA_EXHAUSTED",
        keywords=["quota exhausted", "api quota", "daily limit", "monthly limit"],
        regex_patterns=[r"quota.*exhausted", r"daily.*limit", r"monthly.*limit"],
        http_codes=[402, 429],
        severity=ErrorSeverity.CRITICAL,
        recovery_strategy=RecoveryStrategy.ESCALATE_TO_HUMAN,
        retry_count=0,
        backoff_multiplier=1.0,
        max_wait_time=0.0,
        context_preservation=True
    ),
    
    "AUTHENTICATION_ERROR": ErrorPattern(
        error_type="AUTHENTICATION_ERROR",
        keywords=["authentication failed", "invalid token", "unauthorized", "auth error"],
        regex_patterns=[r"auth.*error", r"unauthorized", r"invalid.*token"],
        http_codes=[401, 403],
        severity=ErrorSeverity.CRITICAL,
        recovery_strategy=RecoveryStrategy.ESCALATE_TO_HUMAN,
        retry_count=1,
        backoff_multiplier=1.0,
        max_wait_time=10.0,
        context_preservation=True
    ),
    
    "MCP_SERVER_ERROR": ErrorPattern(
        error_type="MCP_SERVER_ERROR",
        keywords=["mcp server", "server error", "mcp connection", "protocol error"],
        regex_patterns=[r"mcp.*error", r"server.*error", r"protocol.*error"],
        http_codes=[500, 502, 503],
        severity=ErrorSeverity.HIGH,
        recovery_strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
        retry_count=3,
        backoff_multiplier=2.0,
        max_wait_time=180.0,
        context_preservation=True
    ),
    
    "AGENT_FAILURE": ErrorPattern(
        error_type="AGENT_FAILURE",
        keywords=["agent failed", "agent error", "task failed", "execution error"],
        regex_patterns=[r"agent.*failed", r"task.*failed", r"execution.*error"],
        http_codes=[],
        severity=ErrorSeverity.HIGH,
        recovery_strategy=RecoveryStrategy.AGENT_HANDOFF,
        retry_count=2,
        backoff_multiplier=1.0,
        max_wait_time=60.0,
        context_preservation=True
    ),
    
    "MEMORY_ERROR": ErrorPattern(
        error_type="MEMORY_ERROR",
        keywords=["out of memory", "memory error", "allocation failed"],
        regex_patterns=[r"memory.*error", r"out.*of.*memory", r"allocation.*failed"],
        http_codes=[],
        severity=ErrorSeverity.CRITICAL,
        recovery_strategy=RecoveryStrategy.CHECKPOINT_AND_RETRY,
        retry_count=2,
        backoff_multiplier=1.0,
        max_wait_time=30.0,
        context_preservation=False
    )
}


@dataclass
class ErrorContext:
    """Context information for an error occurrence"""
    timestamp: float
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    http_code: Optional[int] = None
    request_id: Optional[str] = None
    agent_id: Optional[str] = None
    workflow_stage: Optional[str] = None
    retry_count: int = 0
    recovery_attempts: list[str] = None
    
    def __post_init__(self):
        if self.recovery_attempts is None:
            self.recovery_attempts = []
    
    def add_recovery_attempt(self, strategy: RecoveryStrategy, result: str):
        """Add a recovery attempt to the context"""
        self.recovery_attempts.append({
            'timestamp': time.time(),
            'strategy': strategy.value,
            'result': result
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'stack_trace': self.stack_trace,
            'http_code': self.http_code,
            'request_id': self.request_id,
            'agent_id': self.agent_id,
            'workflow_stage': self.workflow_stage,
            'retry_count': self.retry_count,
            'recovery_attempts': self.recovery_attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorContext':
        """Create from dictionary"""
        return cls(**data)
"""
Error detection and classification system for Claude Code auto-resume functionality
"""

import re
import time
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import asdict

from .error_types import (
    ErrorPattern, 
    ErrorContext, 
    ERROR_PATTERNS, 
    ErrorSeverity, 
    RecoveryStrategy
)


class LimitDetector:
    """Detects various types of limits and errors that require auto-resume functionality"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Pattern matching confidence thresholds
        self.keyword_threshold = self.config.get('keyword_threshold', 0.5)
        self.regex_threshold = self.config.get('regex_threshold', 0.6)
        
        # Error history for pattern learning
        self.error_history: List[ErrorContext] = []
        self.max_history_size = self.config.get('max_history_size', 1000)
        
        # Custom patterns (learned or user-defined)
        self.custom_patterns: Dict[str, ErrorPattern] = {}
    
    def detect_error(self, 
                    error_message: str, 
                    http_code: Optional[int] = None,
                    stack_trace: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> Optional[ErrorContext]:
        """
        Detect and classify an error based on message, HTTP code, and context
        
        Args:
            error_message: The error message to analyze
            http_code: HTTP status code if applicable
            stack_trace: Full stack trace if available
            context: Additional context (agent_id, workflow_stage, etc.)
        
        Returns:
            ErrorContext if error is detected and classified, None otherwise
        """
        
        # Normalize error message for analysis
        normalized_message = error_message.lower().strip()
        
        # Try to match against known patterns
        matched_pattern = self._match_error_pattern(
            normalized_message, http_code, stack_trace
        )
        
        if matched_pattern:
            error_context = ErrorContext(
                timestamp=time.time(),
                error_type=matched_pattern.error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                http_code=http_code,
                agent_id=context.get('agent_id') if context else None,
                workflow_stage=context.get('workflow_stage') if context else None,
                request_id=context.get('request_id') if context else None,
                retry_count=0
            )
            
            # Add to history for learning
            self._add_to_history(error_context)
            
            self.logger.info(
                f"Error detected: {matched_pattern.error_type} "
                f"(severity: {matched_pattern.severity.value})"
            )
            
            return error_context
        
        # Log unrecognized errors for potential pattern learning
        self.logger.warning(f"Unrecognized error pattern: {error_message}")
        return None
    
    def _match_error_pattern(self, 
                           message: str, 
                           http_code: Optional[int],
                           stack_trace: Optional[str]) -> Optional[ErrorPattern]:
        """Match error against known patterns"""
        
        best_match = None
        best_score = 0.0
        
        # Check all patterns (built-in + custom)
        all_patterns = {**ERROR_PATTERNS, **self.custom_patterns}
        
        for pattern_name, pattern in all_patterns.items():
            score = self._calculate_pattern_score(
                pattern, message, http_code, stack_trace
            )
            
            if score > best_score and score >= self.keyword_threshold:
                best_score = score
                best_match = pattern
        
        return best_match
    
    def _calculate_pattern_score(self, 
                               pattern: ErrorPattern,
                               message: str,
                               http_code: Optional[int],
                               stack_trace: Optional[str]) -> float:
        """Calculate how well a pattern matches the error"""
        
        score = 0.0
        
        # HTTP code matching (gives immediate high score)
        if http_code and pattern.http_codes and http_code in pattern.http_codes:
            score += 0.8  # High confidence for HTTP code match
        
        # Keyword matching
        if pattern.keywords:
            keyword_matches = sum(
                1 for keyword in pattern.keywords 
                if keyword.lower() in message
            )
            if keyword_matches > 0:
                score += 0.6 * (keyword_matches / len(pattern.keywords))
        
        # Regex pattern matching
        if pattern.regex_patterns:
            regex_matches = 0
            for regex_pattern in pattern.regex_patterns:
                try:
                    if re.search(regex_pattern, message, re.IGNORECASE):
                        regex_matches += 1
                except re.error:
                    self.logger.warning(f"Invalid regex pattern: {regex_pattern}")
            
            if regex_matches > 0:
                score += 0.7 * (regex_matches / len(pattern.regex_patterns))
        
        # Cap the score at 1.0
        return min(1.0, score)
    
    def get_recovery_strategy(self, error_context: ErrorContext) -> RecoveryStrategy:
        """Get the recommended recovery strategy for an error"""
        
        pattern = self._get_pattern_for_error(error_context.error_type)
        if pattern:
            return pattern.recovery_strategy
        
        # Default fallback strategy
        return RecoveryStrategy.ESCALATE_TO_HUMAN
    
    def should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if an error should be retried"""
        
        pattern = self._get_pattern_for_error(error_context.error_type)
        if not pattern:
            return False
        
        return error_context.retry_count < pattern.retry_count
    
    def calculate_backoff_delay(self, error_context: ErrorContext) -> float:
        """Calculate the delay before retrying"""
        
        pattern = self._get_pattern_for_error(error_context.error_type)
        if not pattern:
            return 60.0  # Default 1 minute
        
        # Exponential backoff with jitter
        base_delay = 1.0
        delay = min(
            base_delay * (pattern.backoff_multiplier ** error_context.retry_count),
            pattern.max_wait_time
        )
        
        # Add jitter (±20%) to prevent thundering herd
        import random
        jitter = delay * 0.2 * (random.random() - 0.5)
        return max(1.0, delay + jitter)
    
    def _get_pattern_for_error(self, error_type: str) -> Optional[ErrorPattern]:
        """Get the pattern for a specific error type"""
        return ERROR_PATTERNS.get(error_type) or self.custom_patterns.get(error_type)
    
    def _add_to_history(self, error_context: ErrorContext):
        """Add error to history for pattern learning"""
        self.error_history.append(error_context)
        
        # Trim history if it exceeds max size
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def add_custom_pattern(self, pattern_name: str, pattern: ErrorPattern):
        """Add a custom error pattern"""
        self.custom_patterns[pattern_name] = pattern
        self.logger.info(f"Added custom error pattern: {pattern_name}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected errors"""
        if not self.error_history:
            return {}
        
        stats = {
            'total_errors': len(self.error_history),
            'error_types': {},
            'severity_distribution': {},
            'recent_errors': []
        }
        
        # Count by error type
        for error in self.error_history:
            error_type = error.error_type
            stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1
            
            # Get severity for this error type
            pattern = self._get_pattern_for_error(error_type)
            if pattern:
                severity = pattern.severity.value
                stats['severity_distribution'][severity] = (
                    stats['severity_distribution'].get(severity, 0) + 1
                )
        
        # Recent errors (last 10)
        recent_count = min(10, len(self.error_history))
        stats['recent_errors'] = [
            {
                'timestamp': error.timestamp,
                'error_type': error.error_type,
                'message': error.error_message[:100] + '...' if len(error.error_message) > 100 else error.error_message
            }
            for error in self.error_history[-recent_count:]
        ]
        
        return stats
    
    def export_error_patterns(self) -> str:
        """Export custom error patterns to JSON"""
        exportable_patterns = {}
        for name, pattern in self.custom_patterns.items():
            exportable_patterns[name] = {
                'error_type': pattern.error_type,
                'keywords': pattern.keywords,
                'regex_patterns': pattern.regex_patterns,
                'http_codes': pattern.http_codes,
                'severity': pattern.severity.value,
                'recovery_strategy': pattern.recovery_strategy.value,
                'retry_count': pattern.retry_count,
                'backoff_multiplier': pattern.backoff_multiplier,
                'max_wait_time': pattern.max_wait_time,
                'context_preservation': pattern.context_preservation
            }
        
        return json.dumps(exportable_patterns, indent=2)
    
    def import_error_patterns(self, patterns_json: str):
        """Import error patterns from JSON"""
        try:
            patterns_data = json.loads(patterns_json)
            
            for name, pattern_data in patterns_data.items():
                pattern = ErrorPattern(
                    error_type=pattern_data['error_type'],
                    keywords=pattern_data['keywords'],
                    regex_patterns=pattern_data['regex_patterns'],
                    http_codes=pattern_data['http_codes'],
                    severity=ErrorSeverity(pattern_data['severity']),
                    recovery_strategy=RecoveryStrategy(pattern_data['recovery_strategy']),
                    retry_count=pattern_data['retry_count'],
                    backoff_multiplier=pattern_data['backoff_multiplier'],
                    max_wait_time=pattern_data['max_wait_time'],
                    context_preservation=pattern_data['context_preservation']
                )
                
                self.add_custom_pattern(name, pattern)
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error(f"Failed to import error patterns: {e}")
            raise ValueError(f"Invalid pattern format: {e}")


# Convenience function for quick error detection
def detect_claude_error(error_message: str, 
                       http_code: Optional[int] = None,
                       **context) -> Optional[ErrorContext]:
    """
    Quick error detection function
    
    Args:
        error_message: The error message to analyze
        http_code: HTTP status code if applicable
        **context: Additional context (agent_id, workflow_stage, etc.)
    
    Returns:
        ErrorContext if error is detected, None otherwise
    """
    detector = LimitDetector()
    return detector.detect_error(error_message, http_code, context=context)
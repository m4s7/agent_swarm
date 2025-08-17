#!/usr/bin/env python3
"""
Test suite for error detection and classification system
"""

import unittest
import time
import json
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.error_detector import LimitDetector, detect_claude_error
from utils.error_types import (
    ErrorSeverity, 
    RecoveryStrategy, 
    ErrorPattern, 
    ErrorContext,
    ERROR_PATTERNS
)


class TestErrorDetection(unittest.TestCase):
    """Test cases for error detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = LimitDetector()
    
    def test_rate_limit_detection(self):
        """Test detection of rate limit errors"""
        test_cases = [
            "Rate limit exceeded. Please try again later.",
            "HTTP 429: Too many requests",
            "API rate_limit_exceeded error",
            "You have exceeded your quota limit"
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                error_context = self.detector.detect_error(message, http_code=429)
                self.assertIsNotNone(error_context)
                self.assertEqual(error_context.error_type, "RATE_LIMIT_EXCEEDED")
                
                # Check recovery strategy
                strategy = self.detector.get_recovery_strategy(error_context)
                self.assertEqual(strategy, RecoveryStrategy.WAIT_AND_RETRY)
    
    def test_token_limit_detection(self):
        """Test detection of token limit errors"""
        test_cases = [
            "Token limit exceeded for this conversation",
            "context_length_exceeded: Maximum context length reached",
            "Request exceeds max_tokens limit",
            "The context is too long for processing"
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                error_context = self.detector.detect_error(message, http_code=400)
                self.assertIsNotNone(error_context)
                self.assertEqual(error_context.error_type, "TOKEN_LIMIT_EXCEEDED")
                
                # Check recovery strategy
                strategy = self.detector.get_recovery_strategy(error_context)
                self.assertEqual(strategy, RecoveryStrategy.TRUNCATE_CONTEXT)
    
    def test_network_timeout_detection(self):
        """Test detection of network timeout errors"""
        test_cases = [
            "Connection timeout occurred",
            "Read timeout after 30 seconds",
            "Network error: Connection lost",
            "Request timed out"
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                error_context = self.detector.detect_error(message, http_code=504)
                self.assertIsNotNone(error_context)
                self.assertEqual(error_context.error_type, "NETWORK_TIMEOUT")
                
                # Check recovery strategy
                strategy = self.detector.get_recovery_strategy(error_context)
                self.assertEqual(strategy, RecoveryStrategy.CHECKPOINT_AND_RETRY)
    
    def test_authentication_error_detection(self):
        """Test detection of authentication errors"""
        test_cases = [
            "Authentication failed: Invalid API key",
            "Unauthorized access",
            "Invalid token provided",
            "Authentication error occurred"
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                error_context = self.detector.detect_error(message, http_code=401)
                self.assertIsNotNone(error_context)
                self.assertEqual(error_context.error_type, "AUTHENTICATION_ERROR")
                
                # Check recovery strategy
                strategy = self.detector.get_recovery_strategy(error_context)
                self.assertEqual(strategy, RecoveryStrategy.ESCALATE_TO_HUMAN)
    
    def test_http_code_matching(self):
        """Test error detection based on HTTP codes"""
        test_cases = [
            (429, "RATE_LIMIT_EXCEEDED"),
            (401, "AUTHENTICATION_ERROR"),
            (504, "NETWORK_TIMEOUT"),
            (502, "NETWORK_TIMEOUT"),
            (503, "NETWORK_TIMEOUT")
        ]
        
        for http_code, expected_type in test_cases:
            with self.subTest(http_code=http_code):
                error_context = self.detector.detect_error(
                    f"HTTP {http_code} error occurred", 
                    http_code=http_code
                )
                self.assertIsNotNone(error_context)
                self.assertEqual(error_context.error_type, expected_type)
    
    def test_unrecognized_error(self):
        """Test handling of unrecognized errors"""
        error_context = self.detector.detect_error(
            "This is a completely unknown error message"
        )
        self.assertIsNone(error_context)
    
    def test_retry_logic(self):
        """Test retry decision logic"""
        # Create an error context
        error_context = ErrorContext(
            timestamp=time.time(),
            error_type="RATE_LIMIT_EXCEEDED",
            error_message="Rate limit exceeded",
            retry_count=0
        )
        
        # Should retry initially
        self.assertTrue(self.detector.should_retry(error_context))
        
        # Increment retry count
        error_context.retry_count = 3
        self.assertTrue(self.detector.should_retry(error_context))
        
        # Exceed retry limit
        error_context.retry_count = 6
        self.assertFalse(self.detector.should_retry(error_context))
    
    def test_backoff_calculation(self):
        """Test exponential backoff calculation"""
        error_context = ErrorContext(
            timestamp=time.time(),
            error_type="RATE_LIMIT_EXCEEDED",
            error_message="Rate limit exceeded",
            retry_count=0
        )
        
        # Test increasing delays
        delays = []
        for retry_count in range(5):
            error_context.retry_count = retry_count
            delay = self.detector.calculate_backoff_delay(error_context)
            delays.append(delay)
            self.assertGreater(delay, 0)
        
        # Delays should generally increase (with jitter, may not be strictly increasing)
        self.assertGreater(delays[2], delays[0])
        self.assertGreater(delays[4], delays[1])
    
    def test_custom_pattern_addition(self):
        """Test adding custom error patterns"""
        custom_pattern = ErrorPattern(
            error_type="CUSTOM_TEST_ERROR",
            keywords=["custom error", "test failure"],
            regex_patterns=[r"custom.*error"],
            http_codes=[500],
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.AGENT_HANDOFF,
            retry_count=2
        )
        
        self.detector.add_custom_pattern("CUSTOM_TEST", custom_pattern)
        
        # Test detection with custom pattern
        error_context = self.detector.detect_error("Custom error occurred", http_code=500)
        self.assertIsNotNone(error_context)
        self.assertEqual(error_context.error_type, "CUSTOM_TEST_ERROR")
    
    def test_error_context_serialization(self):
        """Test ErrorContext serialization and deserialization"""
        original_context = ErrorContext(
            timestamp=time.time(),
            error_type="TEST_ERROR",
            error_message="Test error message",
            http_code=500,
            agent_id="test-agent",
            workflow_stage="testing",
            retry_count=1
        )
        
        # Test serialization
        context_dict = original_context.to_dict()
        self.assertIsInstance(context_dict, dict)
        self.assertEqual(context_dict['error_type'], "TEST_ERROR")
        
        # Test deserialization
        restored_context = ErrorContext.from_dict(context_dict)
        self.assertEqual(restored_context.error_type, original_context.error_type)
        self.assertEqual(restored_context.error_message, original_context.error_message)
        self.assertEqual(restored_context.retry_count, original_context.retry_count)
    
    def test_error_statistics(self):
        """Test error statistics generation"""
        # Generate some test errors
        test_errors = [
            ("Rate limit exceeded", 429, "RATE_LIMIT_EXCEEDED"),
            ("Token limit exceeded", 400, "TOKEN_LIMIT_EXCEEDED"),
            ("Connection timeout", 504, "NETWORK_TIMEOUT"),
            ("Rate limit exceeded again", 429, "RATE_LIMIT_EXCEEDED")
        ]
        
        for message, http_code, expected_type in test_errors:
            self.detector.detect_error(message, http_code=http_code)
        
        stats = self.detector.get_error_statistics()
        
        self.assertEqual(stats['total_errors'], 4)
        self.assertEqual(stats['error_types']['RATE_LIMIT_EXCEEDED'], 2)
        self.assertEqual(stats['error_types']['TOKEN_LIMIT_EXCEEDED'], 1)
        self.assertEqual(stats['error_types']['NETWORK_TIMEOUT'], 1)
        self.assertIn('recent_errors', stats)
        self.assertLessEqual(len(stats['recent_errors']), 10)
    
    def test_pattern_export_import(self):
        """Test export and import of custom patterns"""
        # Add a custom pattern
        custom_pattern = ErrorPattern(
            error_type="EXPORT_TEST_ERROR",
            keywords=["export test"],
            regex_patterns=[r"export.*test"],
            http_codes=[418],  # I'm a teapot
            severity=ErrorSeverity.LOW,
            recovery_strategy=RecoveryStrategy.WAIT_AND_RETRY,
            retry_count=1
        )
        
        self.detector.add_custom_pattern("EXPORT_TEST", custom_pattern)
        
        # Export patterns
        exported_json = self.detector.export_error_patterns()
        self.assertIsInstance(exported_json, str)
        
        # Create a new detector and import patterns
        new_detector = LimitDetector()
        new_detector.import_error_patterns(exported_json)
        
        # Test that the pattern works in the new detector
        error_context = new_detector.detect_error("Export test error", http_code=418)
        self.assertIsNotNone(error_context)
        self.assertEqual(error_context.error_type, "EXPORT_TEST_ERROR")
    
    def test_convenience_function(self):
        """Test the convenience function for error detection"""
        error_context = detect_claude_error(
            "Rate limit exceeded",
            http_code=429,
            agent_id="test-agent",
            workflow_stage="testing"
        )
        
        self.assertIsNotNone(error_context)
        self.assertEqual(error_context.error_type, "RATE_LIMIT_EXCEEDED")
        self.assertEqual(error_context.agent_id, "test-agent")
        self.assertEqual(error_context.workflow_stage, "testing")


class TestErrorPatterns(unittest.TestCase):
    """Test cases for predefined error patterns"""
    
    def test_pattern_completeness(self):
        """Test that all predefined patterns are valid"""
        for pattern_name, pattern in ERROR_PATTERNS.items():
            with self.subTest(pattern=pattern_name):
                self.assertIsInstance(pattern.error_type, str)
                self.assertIsInstance(pattern.keywords, list)
                self.assertIsInstance(pattern.regex_patterns, list)
                self.assertIsInstance(pattern.http_codes, list)
                self.assertIsInstance(pattern.severity, ErrorSeverity)
                self.assertIsInstance(pattern.recovery_strategy, RecoveryStrategy)
                self.assertGreaterEqual(pattern.retry_count, 0)
                self.assertGreater(pattern.backoff_multiplier, 0)
                self.assertGreaterEqual(pattern.max_wait_time, 0)
    
    def test_pattern_uniqueness(self):
        """Test that error types are unique"""
        error_types = [pattern.error_type for pattern in ERROR_PATTERNS.values()]
        self.assertEqual(len(error_types), len(set(error_types)))


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
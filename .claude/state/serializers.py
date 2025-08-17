"""
Serialization utilities for session state and checkpoint data
"""

import json
import pickle
import gzip
import base64
import time
from typing import Any, Dict, Optional, Union, List
from dataclasses import is_dataclass, asdict
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.session_manager import SessionState, Message, AgentContext, WorkflowState
from utils.error_types import ErrorContext


class StateSerializer:
    """Handles serialization and deserialization of session state"""
    
    def __init__(self, 
                 format: str = "json",
                 compression: bool = True,
                 encryption: bool = False):
        self.format = format.lower()
        self.compression = compression
        self.encryption = encryption
        self.logger = logging.getLogger(__name__)
        
        if self.format not in ["json", "pickle", "msgpack"]:
            raise ValueError(f"Unsupported format: {format}")
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize object to bytes"""
        try:
            # Convert to serializable format
            data = self._make_serializable(obj)
            
            # Serialize based on format
            if self.format == "json":
                serialized = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif self.format == "pickle":
                serialized = pickle.dumps(data)
            elif self.format == "msgpack":
                import msgpack
                serialized = msgpack.packb(data)
            else:
                raise ValueError(f"Unsupported format: {self.format}")
            
            # Apply compression
            if self.compression:
                serialized = gzip.compress(serialized)
            
            # Apply encryption (placeholder for future implementation)
            if self.encryption:
                serialized = self._encrypt(serialized)
            
            return serialized
            
        except Exception as e:
            self.logger.error(f"Serialization failed: {e}")
            raise
    
    def deserialize(self, data: bytes, target_type: Optional[type] = None) -> Any:
        """Deserialize bytes to object"""
        try:
            # Decrypt if needed
            if self.encryption:
                data = self._decrypt(data)
            
            # Decompress if needed
            if self.compression:
                data = gzip.decompress(data)
            
            # Deserialize based on format
            if self.format == "json":
                obj_data = json.loads(data.decode('utf-8'))
            elif self.format == "pickle":
                obj_data = pickle.loads(data)
            elif self.format == "msgpack":
                import msgpack
                obj_data = msgpack.unpackb(data)
            else:
                raise ValueError(f"Unsupported format: {self.format}")
            
            # Convert back to original type if specified
            if target_type:
                return self._restore_type(obj_data, target_type)
            
            return obj_data
            
        except Exception as e:
            self.logger.error(f"Deserialization failed: {e}")
            raise
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to serializable format"""
        
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        
        elif is_dataclass(obj):
            return {
                '__type__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                '__data__': asdict(obj)
            }
        
        elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return {
                '__type__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                '__data__': obj.to_dict()
            }
        
        elif isinstance(obj, Exception):
            return {
                '__type__': 'Exception',
                '__exception_type__': obj.__class__.__name__,
                '__data__': str(obj)
            }
        
        else:
            # Try to serialize as string representation
            self.logger.warning(f"Converting non-serializable object to string: {type(obj)}")
            return {
                '__type__': 'string_repr',
                '__original_type__': str(type(obj)),
                '__data__': str(obj)
            }
    
    def _restore_type(self, obj_data: Any, target_type: type) -> Any:
        """Restore object to original type"""
        
        if not isinstance(obj_data, dict) or '__type__' not in obj_data:
            return obj_data
        
        type_name = obj_data['__type__']
        data = obj_data['__data__']
        
        # Handle known types
        if target_type == SessionState:
            return SessionState.from_dict(data)
        elif target_type == Message:
            return Message.from_dict(data)
        elif target_type == AgentContext:
            return AgentContext.from_dict(data)
        elif target_type == WorkflowState:
            return WorkflowState.from_dict(data)
        elif target_type == ErrorContext:
            return ErrorContext.from_dict(data)
        
        # Try to find class dynamically
        try:
            module_name = obj_data.get('__module__', '__main__')
            module = __import__(module_name, fromlist=[type_name])
            cls = getattr(module, type_name)
            
            if hasattr(cls, 'from_dict'):
                return cls.from_dict(data)
            elif is_dataclass(cls):
                return cls(**data)
            else:
                return data
                
        except (ImportError, AttributeError) as e:
            self.logger.warning(f"Could not restore type {type_name}: {e}")
            return data
    
    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data (placeholder for future implementation)"""
        # TODO: Implement encryption using cryptography library
        # For now, just base64 encode as a placeholder
        return base64.b64encode(data)
    
    def _decrypt(self, data: bytes) -> bytes:
        """Decrypt data (placeholder for future implementation)"""
        # TODO: Implement decryption using cryptography library
        # For now, just base64 decode as a placeholder
        return base64.b64decode(data)


class CompactSerializer(StateSerializer):
    """Optimized serializer for minimal storage size"""
    
    def __init__(self):
        super().__init__(format="json", compression=True, encryption=False)
        self.field_mappings = {
            # Common field name abbreviations to reduce size
            'timestamp': 'ts',
            'session_id': 'sid',
            'agent_id': 'aid',
            'message_id': 'mid',
            'error_type': 'et',
            'error_message': 'em',
            'conversation_history': 'ch',
            'agent_contexts': 'ac',
            'workflow_state': 'ws',
            'created_at': 'ca',
            'updated_at': 'ua'
        }
        self.reverse_mappings = {v: k for k, v in self.field_mappings.items()}
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object with field compression"""
        result = super()._make_serializable(obj)
        return self._compress_fields(result)
    
    def _restore_type(self, obj_data: Any, target_type: type) -> Any:
        """Restore object with field decompression"""
        expanded_data = self._expand_fields(obj_data)
        return super()._restore_type(expanded_data, target_type)
    
    def _compress_fields(self, obj: Any) -> Any:
        """Compress field names to reduce size"""
        if isinstance(obj, dict):
            compressed = {}
            for key, value in obj.items():
                new_key = self.field_mappings.get(key, key)
                compressed[new_key] = self._compress_fields(value)
            return compressed
        elif isinstance(obj, (list, tuple)):
            return [self._compress_fields(item) for item in obj]
        else:
            return obj
    
    def _expand_fields(self, obj: Any) -> Any:
        """Expand compressed field names"""
        if isinstance(obj, dict):
            expanded = {}
            for key, value in obj.items():
                new_key = self.reverse_mappings.get(key, key)
                expanded[new_key] = self._expand_fields(value)
            return expanded
        elif isinstance(obj, (list, tuple)):
            return [self._expand_fields(item) for item in obj]
        else:
            return obj


class IncrementalSerializer:
    """Handles incremental serialization for large session states"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.serializer = StateSerializer()
        self.logger = logging.getLogger(__name__)
    
    def serialize_chunked(self, obj: Any) -> List[bytes]:
        """Serialize object into chunks"""
        try:
            # First serialize normally
            full_data = self.serializer.serialize(obj)
            
            # Split into chunks
            chunks = []
            for i in range(0, len(full_data), self.chunk_size):
                chunk = full_data[i:i + self.chunk_size]
                chunks.append(chunk)
            
            self.logger.debug(f"Serialized into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Chunked serialization failed: {e}")
            raise
    
    def deserialize_chunked(self, chunks: List[bytes], target_type: Optional[type] = None) -> Any:
        """Deserialize chunks back to object"""
        try:
            # Reconstruct full data
            full_data = b''.join(chunks)
            
            # Deserialize normally
            return self.serializer.deserialize(full_data, target_type)
            
        except Exception as e:
            self.logger.error(f"Chunked deserialization failed: {e}")
            raise


class AsyncSerializer:
    """Asynchronous serialization for non-blocking operations"""
    
    def __init__(self, serializer: Optional[StateSerializer] = None):
        self.serializer = serializer or StateSerializer()
        self.logger = logging.getLogger(__name__)
    
    async def serialize_async(self, obj: Any) -> bytes:
        """Serialize object asynchronously"""
        import asyncio
        
        try:
            # Run serialization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.serializer.serialize, obj)
            return result
            
        except Exception as e:
            self.logger.error(f"Async serialization failed: {e}")
            raise
    
    async def deserialize_async(self, data: bytes, target_type: Optional[type] = None) -> Any:
        """Deserialize data asynchronously"""
        import asyncio
        
        try:
            # Run deserialization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.serializer.deserialize, data, target_type)
            return result
            
        except Exception as e:
            self.logger.error(f"Async deserialization failed: {e}")
            raise


def create_serializer(config: Dict[str, Any]) -> StateSerializer:
    """Factory function to create serializer based on configuration"""
    
    serializer_type = config.get('type', 'standard')
    
    if serializer_type == 'compact':
        return CompactSerializer()
    elif serializer_type == 'incremental':
        chunk_size = config.get('chunk_size', 1024 * 1024)
        return IncrementalSerializer(chunk_size)
    elif serializer_type == 'async':
        base_serializer = create_serializer(config.get('base_config', {}))
        return AsyncSerializer(base_serializer)
    else:
        return StateSerializer(
            format=config.get('format', 'json'),
            compression=config.get('compression', True),
            encryption=config.get('encryption', False)
        )
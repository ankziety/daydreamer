"""
Memory Entry Module

Defines the core data structures for memory entries, including types,
metadata, and content management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List
import uuid
import json


class MemoryType(Enum):
    """Enumeration of memory types in the hierarchical memory structure."""
    
    EPISODIC = "episodic"      # Specific events and experiences
    SEMANTIC = "semantic"      # Facts, concepts, and knowledge
    PROCEDURAL = "procedural"  # Skills, procedures, and how-to knowledge
    EMOTIONAL = "emotional"    # Emotional associations and feelings
    WORKING = "working"        # Short-term active memory


class MemoryMetadata:
    """Metadata associated with a memory entry."""
    
    def __init__(
        self,
        memory_type: MemoryType,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        confidence: float = 1.0,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        last_accessed: Optional[datetime] = None,
        access_count: int = 0,
        decay_rate: float = 0.1
    ):
        self.memory_type = memory_type
        self.importance = max(0.0, min(1.0, importance))  # Clamp to [0, 1]
        self.emotional_valence = max(-1.0, min(1.0, emotional_valence))  # Clamp to [-1, 1]
        self.confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        self.source = source
        self.tags = tags or []
        self.created_at = created_at or datetime.now()
        self.last_accessed = last_accessed or datetime.now()
        self.access_count = max(0, access_count)
        self.decay_rate = max(0.0, min(1.0, decay_rate))  # Clamp to [0, 1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            'memory_type': self.memory_type.value,
            'importance': self.importance,
            'emotional_valence': self.emotional_valence,
            'confidence': self.confidence,
            'source': self.source,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'decay_rate': self.decay_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryMetadata':
        """Create metadata from dictionary."""
        return cls(
            memory_type=MemoryType(data['memory_type']),
            importance=data['importance'],
            emotional_valence=data['emotional_valence'],
            confidence=data['confidence'],
            source=data.get('source'),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            access_count=data['access_count'],
            decay_rate=data['decay_rate']
        )
    
    def update_access(self):
        """Update access statistics when memory is retrieved."""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def calculate_strength(self) -> float:
        """Calculate memory strength based on various factors."""
        # Base strength from importance and confidence
        base_strength = (self.importance + self.confidence) / 2.0
        
        # Time decay factor
        time_since_creation = (datetime.now() - self.created_at).total_seconds()
        time_decay = 1.0 / (1.0 + self.decay_rate * time_since_creation / 86400)  # Daily decay
        
        # Access boost factor
        access_boost = min(1.0, self.access_count / 10.0)  # Diminishing returns after 10 accesses
        
        # Emotional boost
        emotional_boost = 1.0 + abs(self.emotional_valence) * 0.2
        
        return base_strength * time_decay * (1.0 + access_boost * 0.3) * emotional_boost


class MemoryEntry:
    """Represents a single memory entry with content and metadata."""
    
    def __init__(
        self,
        content: Any,
        memory_type: MemoryType,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        confidence: float = 1.0,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        memory_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        decay_rate: float = 0.1
    ):
        self.memory_id = memory_id or str(uuid.uuid4())
        self.content = content
        self.metadata = MemoryMetadata(
            memory_type=memory_type,
            importance=importance,
            emotional_valence=emotional_valence,
            confidence=confidence,
            source=source,
            tags=tags,
            created_at=created_at,
            decay_rate=decay_rate
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary for serialization."""
        return {
            'memory_id': self.memory_id,
            'content': self.content,
            'metadata': self.metadata.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create memory entry from dictionary."""
        entry = cls(
            content=data['content'],
            memory_type=MemoryType(data['metadata']['memory_type']),
            importance=data['metadata']['importance'],
            emotional_valence=data['metadata']['emotional_valence'],
            confidence=data['metadata']['confidence'],
            source=data['metadata'].get('source'),
            tags=data['metadata'].get('tags', []),
            memory_id=data['memory_id'],
            created_at=datetime.fromisoformat(data['metadata']['created_at']),
            decay_rate=data['metadata']['decay_rate']
        )
        # Restore access statistics
        entry.metadata.last_accessed = datetime.fromisoformat(data['metadata']['last_accessed'])
        entry.metadata.access_count = data['metadata']['access_count']
        return entry
    
    def get_strength(self) -> float:
        """Get the current strength of this memory."""
        return self.metadata.calculate_strength()
    
    def update_access(self):
        """Mark this memory as accessed."""
        self.metadata.update_access()
    
    def add_tag(self, tag: str):
        """Add a tag to this memory."""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from this memory."""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if memory has a specific tag."""
        return tag in self.metadata.tags
    
    def __str__(self) -> str:
        """String representation of memory entry."""
        return f"MemoryEntry(id={self.memory_id}, type={self.metadata.memory_type.value}, strength={self.get_strength():.3f})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"MemoryEntry(memory_id='{self.memory_id}', content={repr(self.content)}, metadata={self.metadata})"
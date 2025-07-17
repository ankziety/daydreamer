"""
Memory Store Module

Main memory storage system that integrates hierarchical memory structures,
persistence, indexing, and retrieval mechanisms.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
import threading

from .memory_entry import MemoryEntry, MemoryType
from .memory_index import MemoryIndex
from .memory_persistence import MemoryPersistence


class MemoryStore:
    """
    Comprehensive memory storage system for agents.
    
    Provides hierarchical memory structure, persistence, indexing,
    and advanced retrieval capabilities with memory decay and consolidation.
    """
    
    def __init__(
        self,
        storage_path: str = "memory_store.db",
        backend: str = "sqlite",
        auto_save: bool = True,
        max_memories: Optional[int] = None,
        consolidation_interval: int = 3600  # 1 hour
    ):
        """
        Initialize the memory store.
        
        Args:
            storage_path: Path to storage file
            backend: Storage backend ('sqlite', 'json', 'pickle')
            auto_save: Whether to automatically save changes
            max_memories: Maximum number of memories to keep (None for unlimited)
            consolidation_interval: Seconds between consolidation runs
        """
        self.logger = logging.getLogger(__name__)
        self.auto_save = auto_save
        self.max_memories = max_memories
        self.consolidation_interval = consolidation_interval
        
        # Initialize components
        self.persistence = MemoryPersistence(storage_path, backend)
        self.index = MemoryIndex()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Load existing memories
        self._load_existing_memories()
        
        # Start consolidation thread if needed
        self._consolidation_thread = None
        self._stop_consolidation = False
        if consolidation_interval > 0:
            self._start_consolidation_thread()
    
    def _load_existing_memories(self):
        """Load all existing memories from persistence into index."""
        try:
            memories = self.persistence.load_all_memories()
            for memory in memories:
                self.index.add_memory(memory)
            self.logger.info(f"Loaded {len(memories)} existing memories")
        except Exception as e:
            self.logger.error(f"Failed to load existing memories: {e}")
    
    def _start_consolidation_thread(self):
        """Start background consolidation thread."""
        def consolidation_worker():
            while not self._stop_consolidation:
                try:
                    self._consolidate_memories()
                    # Sleep for consolidation interval
                    import time
                    time.sleep(self.consolidation_interval)
                except Exception as e:
                    self.logger.error(f"Consolidation error: {e}")
        
        self._consolidation_thread = threading.Thread(target=consolidation_worker, daemon=True)
        self._consolidation_thread.start()
    
    def store_memory(
        self,
        content: Any,
        memory_type: MemoryType,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        confidence: float = 1.0,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        memory_id: Optional[str] = None,
        decay_rate: float = 0.1
    ) -> str:
        """
        Store a new memory entry.
        
        Returns:
            The memory ID of the stored memory
        """
        with self._lock:
            # Create memory entry
            memory = MemoryEntry(
                content=content,
                memory_type=memory_type,
                importance=importance,
                emotional_valence=emotional_valence,
                confidence=confidence,
                source=source,
                tags=tags or [],
                memory_id=memory_id,
                decay_rate=decay_rate
            )
            
            # Add to index
            self.index.add_memory(memory)
            
            # Persist if auto-save is enabled
            if self.auto_save:
                self.persistence.save_memory(memory)
            
            # Check memory limits
            if self.max_memories and len(self.index) > self.max_memories:
                self._enforce_memory_limits()
            
            self.logger.debug(f"Stored memory {memory.memory_id}")
            return memory.memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID and update access statistics."""
        with self._lock:
            memory = self.index.get_by_id(memory_id)
            if memory:
                memory.update_access()
                if self.auto_save:
                    self.persistence.save_memory(memory)
                    self.index.update_memory(memory)
            return memory
    
    def search_memories(
        self,
        query: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        min_strength: float = 0.0,
        max_strength: float = 1.0,
        limit: Optional[int] = None,
        sort_by: str = "strength"
    ) -> List[MemoryEntry]:
        """
        Search memories using multiple criteria.
        
        Args:
            query: Text query for content search
            memory_type: Filter by memory type
            tags: Filter by tags (all must be present)
            source: Filter by source
            min_strength: Minimum memory strength
            max_strength: Maximum memory strength
            limit: Maximum number of results
            sort_by: Sort method ('strength', 'recent', 'importance')
        
        Returns:
            List of matching memory entries
        """
        with self._lock:
            # Start with all memories
            candidates = set(self.index._by_id.keys())
            
            # Apply filters
            if memory_type:
                type_memories = set(self.index._by_type.get(memory_type, set()))
                candidates &= type_memories
            
            if tags:
                for tag in tags:
                    tag_memories = set(self.index._by_tag.get(tag, set()))
                    candidates &= tag_memories
            
            if source:
                source_memories = set(self.index._by_source.get(source, set()))
                candidates &= source_memories
            
            # Get memory objects
            memories = [self.index._by_id[mid] for mid in candidates if mid in self.index._by_id]
            
            # Apply strength filter
            memories = [m for m in memories if min_strength <= m.get_strength() <= max_strength]
            
            # Apply content search if query provided
            if query:
                content_matches = self.index.search_content(query)
                content_ids = {m.memory_id for m in content_matches}
                memories = [m for m in memories if m.memory_id in content_ids]
            
            # Sort results
            if sort_by == "strength":
                memories.sort(key=lambda m: m.get_strength(), reverse=True)
            elif sort_by == "recent":
                memories.sort(key=lambda m: m.metadata.last_accessed, reverse=True)
            elif sort_by == "importance":
                memories.sort(key=lambda m: m.metadata.importance, reverse=True)
            elif sort_by == "creation":
                memories.sort(key=lambda m: m.metadata.created_at, reverse=True)
            
            # Apply limit
            if limit:
                memories = memories[:limit]
            
            # Update access statistics for retrieved memories
            for memory in memories:
                memory.update_access()
                if self.auto_save:
                    self.persistence.save_memory(memory)
                    self.index.update_memory(memory)
            
            return memories
    
    def get_memories_by_type(self, memory_type: MemoryType, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Get all memories of a specific type."""
        return self.search_memories(memory_type=memory_type, limit=limit)
    
    def get_memories_by_tag(self, tag: str, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Get all memories with a specific tag."""
        return self.search_memories(tags=[tag], limit=limit)
    
    def get_strongest_memories(self, limit: int = 10) -> List[MemoryEntry]:
        """Get the strongest memories."""
        return self.index.get_strongest_memories(limit)
    
    def get_recent_memories(self, hours: int = 24, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Get memories accessed within the last N hours."""
        memories = self.index.get_recently_accessed(hours)
        if limit:
            memories = memories[:limit]
        return memories
    
    def update_memory(
        self,
        memory_id: str,
        content: Optional[Any] = None,
        importance: Optional[float] = None,
        emotional_valence: Optional[float] = None,
        confidence: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Update an existing memory entry."""
        with self._lock:
            memory = self.index.get_by_id(memory_id)
            if not memory:
                return False
            
            # Update fields if provided
            if content is not None:
                memory.content = content
            if importance is not None:
                memory.metadata.importance = max(0.0, min(1.0, importance))
            if emotional_valence is not None:
                memory.metadata.emotional_valence = max(-1.0, min(1.0, emotional_valence))
            if confidence is not None:
                memory.metadata.confidence = max(0.0, min(1.0, confidence))
            if tags is not None:
                memory.metadata.tags = tags
            
            # Update index and persistence
            self.index.update_memory(memory)
            if self.auto_save:
                self.persistence.save_memory(memory)
            
            return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        with self._lock:
            success = self.index.remove_memory(memory_id)
            if success and self.auto_save:
                self.persistence.delete_memory(memory_id)
            return success
    
    def add_tag_to_memory(self, memory_id: str, tag: str) -> bool:
        """Add a tag to a memory entry."""
        with self._lock:
            memory = self.index.get_by_id(memory_id)
            if not memory:
                return False
            
            memory.add_tag(tag)
            self.index.update_memory(memory)
            if self.auto_save:
                self.persistence.save_memory(memory)
            
            return True
    
    def remove_tag_from_memory(self, memory_id: str, tag: str) -> bool:
        """Remove a tag from a memory entry."""
        with self._lock:
            memory = self.index.get_by_id(memory_id)
            if not memory:
                return False
            
            memory.remove_tag(tag)
            self.index.update_memory(memory)
            if self.auto_save:
                self.persistence.save_memory(memory)
            
            return True
    
    def _enforce_memory_limits(self):
        """Enforce memory limits by removing weakest memories."""
        if not self.max_memories:
            return
        
        excess = len(self.index) - self.max_memories
        if excess <= 0:
            return
        
        # Get all memories sorted by strength (weakest first)
        all_memories = list(self.index._by_id.values())
        all_memories.sort(key=lambda m: m.get_strength())
        
        # Remove excess memories (weakest ones)
        for memory in all_memories[:excess]:
            self.delete_memory(memory.memory_id)
        
        self.logger.info(f"Removed {excess} weak memories to enforce limit")
    
    def _consolidate_memories(self):
        """Run memory consolidation to strengthen important memories."""
        with self._lock:
            # Find memories that need consolidation
            all_memories = list(self.index._by_id.values())
            
            for memory in all_memories:
                # Strengthen memories that are frequently accessed
                if memory.metadata.access_count > 5:
                    # Boost importance slightly
                    new_importance = min(1.0, memory.metadata.importance + 0.05)
                    if new_importance != memory.metadata.importance:
                        memory.metadata.importance = new_importance
                        self.index.update_memory(memory)
                        if self.auto_save:
                            self.persistence.save_memory(memory)
                
                # Weaken very old, rarely accessed memories
                age_days = (datetime.now() - memory.metadata.created_at).days
                if age_days > 30 and memory.metadata.access_count < 2:
                    memory.metadata.decay_rate = min(1.0, memory.metadata.decay_rate + 0.1)
                    self.index.update_memory(memory)
                    if self.auto_save:
                        self.persistence.save_memory(memory)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory store statistics."""
        with self._lock:
            index_stats = self.index.get_statistics()
            persistence_stats = self.persistence.get_statistics()
            
            return {
                'index': index_stats,
                'persistence': persistence_stats,
                'auto_save': self.auto_save,
                'max_memories': self.max_memories,
                'consolidation_interval': self.consolidation_interval
            }
    
    def backup(self, backup_path: str) -> bool:
        """Create a backup of the memory store."""
        return self.persistence.backup(backup_path)
    
    def clear_all(self) -> bool:
        """Clear all memories from the store."""
        with self._lock:
            self.index.clear()
            return self.persistence.clear_all()
    
    def save_all(self) -> bool:
        """Manually save all memories to persistence."""
        with self._lock:
            try:
                for memory in self.index._by_id.values():
                    self.persistence.save_memory(memory)
                return True
            except Exception as e:
                self.logger.error(f"Failed to save all memories: {e}")
                return False
    
    def close(self):
        """Close the memory store and cleanup resources."""
        self._stop_consolidation = True
        if self._consolidation_thread:
            self._consolidation_thread.join(timeout=5.0)
        
        self.save_all()
        self.persistence.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __len__(self) -> int:
        """Return number of stored memories."""
        return len(self.index)
    
    def __contains__(self, memory_id: str) -> bool:
        """Check if memory ID exists in store."""
        return memory_id in self.index
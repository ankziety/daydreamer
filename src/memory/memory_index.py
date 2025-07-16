"""
Memory Index Module

Provides fast indexing and search capabilities for memory entries,
including tag-based, type-based, and content-based search.
"""

from typing import List, Dict, Set, Optional, Any, Tuple
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter

from .memory_entry import MemoryEntry, MemoryType


class MemoryIndex:
    """Fast indexing and search system for memory entries."""
    
    def __init__(self):
        # Core indices
        self._by_id: Dict[str, MemoryEntry] = {}
        self._by_type: Dict[MemoryType, Set[str]] = defaultdict(set)
        self._by_tag: Dict[str, Set[str]] = defaultdict(set)
        self._by_source: Dict[str, Set[str]] = defaultdict(set)
        
        # Content indexing
        self._content_index: Dict[str, Set[str]] = defaultdict(set)  # word -> memory_ids
        self._strength_index: List[Tuple[float, str]] = []  # (strength, memory_id) pairs
        
        # Time-based indices
        self._by_creation_date: Dict[str, Set[str]] = defaultdict(set)  # date -> memory_ids
        self._by_access_date: Dict[str, Set[str]] = defaultdict(set)    # date -> memory_ids
        
        # Statistics
        self._total_entries = 0
        self._type_counts = Counter()
        self._tag_counts = Counter()
    
    def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory entry to the index."""
        memory_id = memory.memory_id
        
        # Core indexing
        self._by_id[memory_id] = memory
        self._by_type[memory.metadata.memory_type].add(memory_id)
        
        # Tag indexing
        for tag in memory.metadata.tags:
            self._by_tag[tag].add(memory_id)
            self._tag_counts[tag] += 1
        
        # Source indexing
        if memory.metadata.source:
            self._by_source[memory.metadata.source].add(memory_id)
        
        # Content indexing (simple word-based)
        if isinstance(memory.content, str):
            words = self._extract_words(memory.content)
            for word in words:
                self._content_index[word.lower()].add(memory_id)
        
        # Time indexing
        creation_date = memory.metadata.created_at.date().isoformat()
        access_date = memory.metadata.last_accessed.date().isoformat()
        self._by_creation_date[creation_date].add(memory_id)
        self._by_access_date[access_date].add(memory_id)
        
        # Strength indexing (maintain sorted list)
        strength = memory.get_strength()
        self._strength_index.append((strength, memory_id))
        self._strength_index.sort(reverse=True)  # Highest strength first
        
        # Update statistics
        self._total_entries += 1
        self._type_counts[memory.metadata.memory_type] += 1
    
    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory entry from the index."""
        if memory_id not in self._by_id:
            return False
        
        memory = self._by_id[memory_id]
        
        # Remove from core indices
        del self._by_id[memory_id]
        self._by_type[memory.metadata.memory_type].discard(memory_id)
        
        # Remove from tag indices
        for tag in memory.metadata.tags:
            self._by_tag[tag].discard(memory_id)
            self._tag_counts[tag] -= 1
            if self._tag_counts[tag] <= 0:
                del self._tag_counts[tag]
        
        # Remove from source index
        if memory.metadata.source:
            self._by_source[memory.metadata.source].discard(memory_id)
        
        # Remove from content index
        if isinstance(memory.content, str):
            words = self._extract_words(memory.content)
            for word in words:
                self._content_index[word.lower()].discard(memory_id)
        
        # Remove from time indices
        creation_date = memory.metadata.created_at.date().isoformat()
        access_date = memory.metadata.last_accessed.date().isoformat()
        self._by_creation_date[creation_date].discard(memory_id)
        self._by_access_date[access_date].discard(memory_id)
        
        # Remove from strength index
        strength = memory.get_strength()
        self._strength_index = [(s, mid) for s, mid in self._strength_index if mid != memory_id]
        
        # Update statistics
        self._total_entries -= 1
        self._type_counts[memory.metadata.memory_type] -= 1
        
        return True
    
    def update_memory(self, memory: MemoryEntry) -> None:
        """Update an existing memory entry in the index."""
        if memory.memory_id in self._by_id:
            self.remove_memory(memory.memory_id)
        self.add_memory(memory)
    
    def get_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory entry by ID."""
        return self._by_id.get(memory_id)
    
    def get_by_type(self, memory_type: MemoryType) -> List[MemoryEntry]:
        """Get all memories of a specific type."""
        memory_ids = self._by_type.get(memory_type, set())
        return [self._by_id[mid] for mid in memory_ids if mid in self._by_id]
    
    def get_by_tag(self, tag: str) -> List[MemoryEntry]:
        """Get all memories with a specific tag."""
        memory_ids = self._by_tag.get(tag, set())
        return [self._by_id[mid] for mid in memory_ids if mid in self._by_id]
    
    def get_by_source(self, source: str) -> List[MemoryEntry]:
        """Get all memories from a specific source."""
        memory_ids = self._by_source.get(source, set())
        return [self._by_id[mid] for mid in memory_ids if mid in self._by_id]
    
    def search_content(self, query: str, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Search memories by content using word matching."""
        query_words = self._extract_words(query.lower())
        if not query_words:
            return []
        
        # Find memories that contain ALL query words (intersection of all word sets)
        matching_ids = None
        for word in query_words:
            word_memories = self._content_index.get(word, set())
            if matching_ids is None:
                matching_ids = word_memories
            else:
                matching_ids = matching_ids.intersection(word_memories)
        
        if not matching_ids:
            return []
        
        # Score results based on word overlap
        scored_results = []
        for memory_id in matching_ids:
            if memory_id not in self._by_id:
                continue
            
            memory = self._by_id[memory_id]
            if isinstance(memory.content, str):
                content_words = set(self._extract_words(memory.content.lower()))
                score = len(query_words.intersection(content_words)) / len(query_words)
                scored_results.append((score, memory))
        
        # Sort by score and return
        scored_results.sort(key=lambda x: x[0], reverse=True)
        results = [memory for score, memory in scored_results]
        
        if limit:
            results = results[:limit]
        
        return results
    
    def get_by_strength_range(self, min_strength: float = 0.0, max_strength: float = 1.0) -> List[MemoryEntry]:
        """Get memories within a strength range."""
        results = []
        for strength, memory_id in self._strength_index:
            if min_strength <= strength <= max_strength:
                if memory_id in self._by_id:
                    results.append(self._by_id[memory_id])
            elif strength < min_strength:
                break  # Early termination since list is sorted
        
        return results
    
    def get_strongest_memories(self, limit: int = 10) -> List[MemoryEntry]:
        """Get the strongest memories."""
        results = []
        for strength, memory_id in self._strength_index[:limit]:
            if memory_id in self._by_id:
                results.append(self._by_id[memory_id])
        return results
    
    def get_by_date_range(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        use_creation_date: bool = True
    ) -> List[MemoryEntry]:
        """Get memories within a date range."""
        if not start_date and not end_date:
            return list(self._by_id.values())
        
        results = []
        date_index = self._by_creation_date if use_creation_date else self._by_access_date
        
        for date_str, memory_ids in date_index.items():
            date = datetime.fromisoformat(date_str).date()
            
            if start_date and date < start_date.date():
                continue
            if end_date and date > end_date.date():
                continue
            
            for memory_id in memory_ids:
                if memory_id in self._by_id:
                    results.append(self._by_id[memory_id])
        
        return results
    
    def get_recently_accessed(self, hours: int = 24) -> List[MemoryEntry]:
        """Get memories accessed within the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.get_by_date_range(start_date=cutoff_time, use_creation_date=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        # Convert enum keys to string values for JSON serialization
        type_distribution = {k.value: v for k, v in self._type_counts.items()}
        
        return {
            'total_entries': self._total_entries,
            'type_distribution': type_distribution,
            'tag_distribution': dict(self._tag_counts.most_common(20)),
            'source_count': len(self._by_source),
            'content_words': len(self._content_index),
            'strongest_memory_strength': self._strength_index[0][0] if self._strength_index else 0.0,
            'weakest_memory_strength': self._strength_index[-1][0] if self._strength_index else 0.0
        }
    
    def get_popular_tags(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most popular tags."""
        return self._tag_counts.most_common(limit)
    
    def clear(self) -> None:
        """Clear all indices."""
        self._by_id.clear()
        self._by_type.clear()
        self._by_tag.clear()
        self._by_source.clear()
        self._content_index.clear()
        self._strength_index.clear()
        self._by_creation_date.clear()
        self._by_access_date.clear()
        self._total_entries = 0
        self._type_counts.clear()
        self._tag_counts.clear()
    
    def _extract_words(self, text: str) -> Set[str]:
        """Extract words from text for indexing."""
        # Simple word extraction - can be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return set(words)
    
    def __len__(self) -> int:
        """Return number of indexed memories."""
        return self._total_entries
    
    def __contains__(self, memory_id: str) -> bool:
        """Check if memory ID is in index."""
        return memory_id in self._by_id
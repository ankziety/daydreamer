"""
DMN Memory Curator - Enhanced memory management for Default Mode Network

This component handles DMN-specific memory retrieval and consolidation,
selecting relevant chunks from working and long-term memory for each cycle,
and managing memory consolidation during DEFAULT mode.
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import hashlib

from ..memory import MemoryStore, MemoryEntry, MemoryType

logger = logging.getLogger(__name__)


class MemoryRelevance(Enum):
    """Memory relevance levels for DMN processing"""
    HIGHLY_RELEVANT = "highly_relevant"    # Direct semantic match
    RELEVANT = "relevant"                  # Related concepts
    POTENTIALLY_RELEVANT = "potentially_relevant"  # Weak associations
    CONTEXTUAL = "contextual"              # Context-dependent relevance
    CREATIVE = "creative"                  # Creative/analogical connections
    RANDOM = "random"                      # Random access for creativity


@dataclass
class MemoryChunk:
    """A chunk of memory retrieved for DMN processing"""
    memory_id: str
    content: str
    relevance: MemoryRelevance
    relevance_score: float
    memory_type: MemoryType
    timestamp: datetime
    access_count: int
    associative_links: List[str] = field(default_factory=list)
    consolidation_level: float = 0.0
    dmn_context: str = ""


class DMNMemoryCurator:
    """
    Enhanced memory curator for Default Mode Network operations.
    
    Responsibilities:
    - Select chunks from working and long-term memory for next cycle (retrieval only)
    - Implement semantic search for memory retrieval
    - Manage memory consolidation during DEFAULT mode
    - Provide context for new thoughts
    - Support memory consolidation and pruning
    - Create associative links between memories
    - NO writing to long-term memory (retrieval only in ACTIVE/PARTIAL_WAKE)
    """
    
    def __init__(self,
                 memory_store: Optional[MemoryStore] = None,
                 max_chunks_per_cycle: int = 8,
                 relevance_threshold: float = 0.3,
                 consolidation_strength: float = 0.1):
        """
        Initialize the DMN Memory Curator.
        
        Args:
            memory_store: Underlying memory store
            max_chunks_per_cycle: Maximum memory chunks per cycle
            relevance_threshold: Minimum relevance for chunk selection
            consolidation_strength: Strength of memory consolidation
        """
        self.memory_store = memory_store or MemoryStore()
        self.max_chunks_per_cycle = max_chunks_per_cycle
        self.relevance_threshold = relevance_threshold
        self.consolidation_strength = consolidation_strength
        
        # DMN-specific state
        self.recent_chunks: List[MemoryChunk] = []
        self.associative_cache: Dict[str, List[str]] = {}
        self.consolidation_queue: List[str] = []
        
        # Semantic similarity cache (simple word-based)
        self.similarity_cache: Dict[str, Dict[str, float]] = {}
        
        # Retrieval patterns for different modes
        self.retrieval_patterns = {
            "ACTIVE": {
                "semantic_weight": 0.6,
                "recency_weight": 0.2,
                "importance_weight": 0.15,
                "random_weight": 0.05
            },
            "PARTIAL_WAKE": {
                "semantic_weight": 0.3,
                "recency_weight": 0.1,
                "importance_weight": 0.1,
                "random_weight": 0.2,
                "creative_weight": 0.3
            },
            "DEFAULT": {
                "consolidation_focus": True,
                "semantic_weight": 0.0,
                "recency_weight": 0.8,
                "importance_weight": 0.2
            }
        }
        
        # Statistics
        self.stats = {
            "total_retrievals": 0,
            "chunks_retrieved": 0,
            "consolidations_performed": 0,
            "associative_links_created": 0,
            "average_relevance": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def retrieve_chunks(self, context, mode, refresh: bool = False) -> List[str]:
        """
        Retrieve relevant memory chunks for the current DMN cycle.
        
        Args:
            context: Current DMN context
            mode: System mode (ACTIVE, PARTIAL_WAKE, DEFAULT)
            refresh: Whether to refresh from long-term memory
            
        Returns:
            List of memory chunk contents
        """
        self.stats["total_retrievals"] += 1
        
        if mode.value == "DEFAULT":
            # In DEFAULT mode, focus on consolidation
            return await self._retrieve_for_consolidation(context)
        
        # Get retrieval pattern for mode
        pattern = self.retrieval_patterns.get(mode.value, self.retrieval_patterns["ACTIVE"])
        
        # Generate query from context
        query_elements = []
        if context.chunks:
            query_elements.extend(context.chunks[-3:])  # Recent thoughts
        if context.hypothesis:
            query_elements.append(context.hypothesis)
        if context.intrusive_thoughts:
            query_elements.extend(context.intrusive_thoughts[-2:])  # Recent intrusive thoughts
        
        query = " ".join(query_elements) if query_elements else "general thoughts"
        
        # Retrieve chunks based on different strategies
        retrieved_chunks = []
        
        # Semantic retrieval
        if pattern.get("semantic_weight", 0) > 0:
            semantic_chunks = await self._semantic_retrieval(query, pattern["semantic_weight"])
            retrieved_chunks.extend(semantic_chunks)
        
        # Recency-based retrieval
        if pattern.get("recency_weight", 0) > 0:
            recent_chunks = await self._recency_retrieval(pattern["recency_weight"])
            retrieved_chunks.extend(recent_chunks)
        
        # Importance-based retrieval
        if pattern.get("importance_weight", 0) > 0:
            important_chunks = await self._importance_retrieval(pattern["importance_weight"])
            retrieved_chunks.extend(important_chunks)
        
        # Random retrieval (for creativity)
        if pattern.get("random_weight", 0) > 0:
            random_chunks = await self._random_retrieval(pattern["random_weight"])
            retrieved_chunks.extend(random_chunks)
        
        # Creative/associative retrieval (PARTIAL_WAKE mode)
        if pattern.get("creative_weight", 0) > 0:
            creative_chunks = await self._creative_retrieval(query, pattern["creative_weight"])
            retrieved_chunks.extend(creative_chunks)
        
        # Deduplicate and rank chunks
        unique_chunks = self._deduplicate_chunks(retrieved_chunks)
        ranked_chunks = self._rank_chunks(unique_chunks, context, mode)
        
        # Limit to max chunks
        final_chunks = ranked_chunks[:self.max_chunks_per_cycle]
        
        # Update recent chunks and statistics
        self.recent_chunks = final_chunks
        self.stats["chunks_retrieved"] += len(final_chunks)
        
        if final_chunks:
            avg_relevance = sum(chunk.relevance_score for chunk in final_chunks) / len(final_chunks)
            current_avg = self.stats.get("average_relevance", 0.0)
            total_retrievals = self.stats["total_retrievals"]
            self.stats["average_relevance"] = ((current_avg * (total_retrievals - 1)) + avg_relevance) / total_retrievals
        
        # Convert to content strings
        chunk_contents = [chunk.content for chunk in final_chunks]
        
        logger.debug(f" Retrieved {len(chunk_contents)} memory chunks for {mode.value} mode")
        return chunk_contents
    
    async def _semantic_retrieval(self, query: str, weight: float) -> List[MemoryChunk]:
        """Retrieve semantically similar memories"""
        # Search for semantically related memories
        memories = self.memory_store.search_memories(
            query=query,
            limit=self.max_chunks_per_cycle * 2
        )
        
        chunks = []
        for memory in memories:
            similarity = self._calculate_semantic_similarity(query, memory.content)
            if similarity >= self.relevance_threshold:
                chunk = self._memory_to_chunk(memory, MemoryRelevance.RELEVANT, similarity * weight)
                chunks.append(chunk)
        
        return chunks
    
    async def _recency_retrieval(self, weight: float) -> List[MemoryChunk]:
        """Retrieve recent memories"""
        recent_memories = self.memory_store.get_recent_memories(
            hours=24,
            limit=self.max_chunks_per_cycle
        )
        
        chunks = []
        for i, memory in enumerate(recent_memories):
            # Recency score decreases with age
            recency_score = (1.0 - (i / len(recent_memories))) * weight
            if recency_score >= self.relevance_threshold:
                chunk = self._memory_to_chunk(memory, MemoryRelevance.CONTEXTUAL, recency_score)
                chunks.append(chunk)
        
        return chunks
    
    async def _importance_retrieval(self, weight: float) -> List[MemoryChunk]:
        """Retrieve important memories"""
        important_memories = self.memory_store.get_strongest_memories(
            limit=self.max_chunks_per_cycle
        )
        
        chunks = []
        for memory in important_memories:
            importance_score = memory.get_strength() * weight
            if importance_score >= self.relevance_threshold:
                chunk = self._memory_to_chunk(memory, MemoryRelevance.HIGHLY_RELEVANT, importance_score)
                chunks.append(chunk)
        
        return chunks
    
    async def _random_retrieval(self, weight: float) -> List[MemoryChunk]:
        """Retrieve random memories for creativity"""
        # Get a random sample of memories
        all_memories = list(self.memory_store.index._by_id.values())
        if not all_memories:
            return []
        
        sample_size = min(self.max_chunks_per_cycle, len(all_memories))
        random_memories = random.sample(all_memories, sample_size)
        
        chunks = []
        for memory in random_memories:
            random_score = random.uniform(0.3, 0.8) * weight
            chunk = self._memory_to_chunk(memory, MemoryRelevance.RANDOM, random_score)
            chunks.append(chunk)
        
        return chunks
    
    async def _creative_retrieval(self, query: str, weight: float) -> List[MemoryChunk]:
        """Retrieve memories through creative/associative connections"""
        # Find memories with creative or analogical connections
        query_words = set(query.lower().split())
        
        chunks = []
        for memory_id, memory in self.memory_store.index._by_id.items():
            memory_words = set(memory.content.lower().split())
            
            # Look for creative connections (few shared words but interesting associations)
            overlap = len(query_words.intersection(memory_words))
            total_words = len(query_words.union(memory_words))
            
            if total_words > 0:
                # Creative connections have low overlap but high potential
                overlap_ratio = overlap / total_words
                if 0.1 <= overlap_ratio <= 0.3:  # Sweet spot for creative connections
                    creative_score = (0.3 - overlap_ratio) * weight * random.uniform(0.8, 1.2)
                    chunk = self._memory_to_chunk(memory, MemoryRelevance.CREATIVE, creative_score)
                    chunks.append(chunk)
        
        return chunks[:self.max_chunks_per_cycle // 2]  # Limit creative chunks
    
    async def _retrieve_for_consolidation(self, context) -> List[str]:
        """Retrieve memories for consolidation during DEFAULT mode"""
        # Get recent thoughts for consolidation
        recent_thoughts = context.recent_thoughts if hasattr(context, 'recent_thoughts') else []
        
        # Add to consolidation queue
        for thought in recent_thoughts:
            thought_hash = hashlib.md5(thought.encode()).hexdigest()
            if thought_hash not in self.consolidation_queue:
                self.consolidation_queue.append(thought_hash)
        
        # Return empty list since we don't provide content in DEFAULT mode
        logger.debug("🛌 DEFAULT mode: Preparing for memory consolidation")
        return []
    
    def _memory_to_chunk(self, memory: MemoryEntry, relevance: MemoryRelevance, 
                        relevance_score: float) -> MemoryChunk:
        """Convert MemoryEntry to MemoryChunk"""
        return MemoryChunk(
            memory_id=memory.memory_id,
            content=memory.content,
            relevance=relevance,
            relevance_score=relevance_score,
            memory_type=memory.metadata.memory_type,
            timestamp=memory.metadata.created_at,
            access_count=memory.metadata.access_count,
            consolidation_level=memory.metadata.importance
        )
    
    def _calculate_semantic_similarity(self, query: str, content: str) -> float:
        """Calculate semantic similarity between query and content"""
        # Simple word-based similarity (could be enhanced with embeddings)
        query_key = hashlib.md5(query.encode()).hexdigest()
        content_key = hashlib.md5(content.encode()).hexdigest()
        
        cache_key = f"{query_key}:{content_key}"
        if cache_key in self.similarity_cache:
            self.stats["cache_hits"] += 1
            return self.similarity_cache[cache_key]
        
        self.stats["cache_misses"] += 1
        
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words or not content_words:
            similarity = 0.0
        else:
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            similarity = len(intersection) / len(union) if union else 0.0
        
        # Cache the result
        if len(self.similarity_cache) < 1000:  # Limit cache size
            self.similarity_cache[cache_key] = similarity
        
        return similarity
    
    def _deduplicate_chunks(self, chunks: List[MemoryChunk]) -> List[MemoryChunk]:
        """Remove duplicate chunks based on memory ID"""
        seen_ids = set()
        unique_chunks = []
        
        for chunk in chunks:
            if chunk.memory_id not in seen_ids:
                seen_ids.add(chunk.memory_id)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _rank_chunks(self, chunks: List[MemoryChunk], context, mode) -> List[MemoryChunk]:
        """Rank chunks by relevance and other factors"""
        # Sort by relevance score (descending)
        ranked_chunks = sorted(chunks, key=lambda c: c.relevance_score, reverse=True)
        
        # Apply mode-specific adjustments
        if mode.value == "PARTIAL_WAKE":
            # Boost creative and random chunks
            for chunk in ranked_chunks:
                if chunk.relevance in [MemoryRelevance.CREATIVE, MemoryRelevance.RANDOM]:
                    chunk.relevance_score *= 1.2
        
        # Re-sort after adjustments
        ranked_chunks.sort(key=lambda c: c.relevance_score, reverse=True)
        
        return ranked_chunks
    
    async def consolidate_memories(self, recent_thoughts: List[str], context) -> Dict[str, Any]:
        """
        Consolidate memories during DEFAULT mode.
        
        Args:
            recent_thoughts: Recent thoughts to consolidate
            context: DMN context
            
        Returns:
            Consolidation results
        """
        if not recent_thoughts:
            return {"consolidated_count": 0, "new_associations": 0}
        
        consolidated_count = 0
        new_associations = 0
        
        # Store recent thoughts as memories
        for thought in recent_thoughts:
            try:
                # Determine memory type based on content
                memory_type = self._classify_memory_type(thought)
                
                # Calculate importance based on thought characteristics
                importance = self._calculate_thought_importance(thought, context)
                
                # Store as memory
                memory_id = self.memory_store.store_memory(
                    content=thought,
                    memory_type=memory_type,
                    importance=importance,
                    source="dmn_consolidation",
                    tags=["dmn", "consolidated"]
                )
                
                consolidated_count += 1
                
                # Create associative links
                associations = self._create_associative_links(thought, memory_id)
                new_associations += len(associations)
                
                logger.debug(f"💾 Consolidated memory: {thought[:50]}...")
                
            except Exception as e:
                logger.error(f"Error consolidating memory: {e}")
        
        # Update consolidation statistics
        self.stats["consolidations_performed"] += consolidated_count
        self.stats["associative_links_created"] += new_associations
        
        # Clean up consolidation queue
        self.consolidation_queue = self.consolidation_queue[-100:]  # Keep last 100
        
        logger.info(f" Consolidated {consolidated_count} memories, created {new_associations} associations")
        
        return {
            "consolidated_count": consolidated_count,
            "new_associations": new_associations,
            "queue_size": len(self.consolidation_queue)
        }
    
    def _classify_memory_type(self, thought: str) -> MemoryType:
        """Classify thought into memory type"""
        thought_lower = thought.lower()
        
        # Simple classification based on keywords
        if any(word in thought_lower for word in ["pattern", "connection", "insight", "understanding"]):
            return MemoryType.EPISODIC
        elif any(word in thought_lower for word in ["concept", "definition", "principle", "rule"]):
            return MemoryType.SEMANTIC
        elif any(word in thought_lower for word in ["procedure", "step", "method", "process"]):
            return MemoryType.PROCEDURAL
        else:
            return MemoryType.EPISODIC  # Default
    
    def _calculate_thought_importance(self, thought: str, context) -> float:
        """Calculate importance score for a thought"""
        base_importance = 0.5
        
        # Length bonus (longer thoughts might be more developed)
        length_bonus = min(0.2, len(thought.split()) / 50.0)
        
        # Keyword importance
        important_keywords = [
            "insight", "discovery", "realization", "understanding", "connection",
            "pattern", "principle", "hypothesis", "theory", "concept"
        ]
        keyword_bonus = sum(0.05 for keyword in important_keywords if keyword in thought.lower())
        
        # Context relevance
        context_bonus = 0.0
        if hasattr(context, 'hypothesis') and context.hypothesis:
            if any(word in thought.lower() for word in context.hypothesis.lower().split()[:5]):
                context_bonus = 0.1
        
        importance = base_importance + length_bonus + keyword_bonus + context_bonus
        return max(0.1, min(1.0, importance))
    
    def _create_associative_links(self, thought: str, memory_id: str) -> List[str]:
        """Create associative links between memories"""
        associations = []
        
        # Find semantically similar existing memories
        similar_memories = self.memory_store.search_memories(
            query=thought,
            limit=5,
            min_strength=0.3
        )
        
        for similar_memory in similar_memories:
            if similar_memory.memory_id != memory_id:
                # Create bidirectional association
                association_key = f"{memory_id}:{similar_memory.memory_id}"
                if association_key not in self.associative_cache:
                    self.associative_cache[association_key] = [thought, similar_memory.content]
                    associations.append(association_key)
        
        return associations
    
    def get_associative_memories(self, memory_id: str) -> List[MemoryChunk]:
        """Get memories associated with a given memory"""
        associated_chunks = []
        
        for association_key, contents in self.associative_cache.items():
            if memory_id in association_key:
                # Find the other memory in the association
                parts = association_key.split(':')
                other_id = parts[1] if parts[0] == memory_id else parts[0]
                
                # Retrieve the associated memory
                other_memory = self.memory_store.retrieve_memory(other_id)
                if other_memory:
                    chunk = self._memory_to_chunk(
                        other_memory, 
                        MemoryRelevance.RELEVANT,
                        0.7  # High relevance for associated memories
                    )
                    chunk.associative_links = [association_key]
                    associated_chunks.append(chunk)
        
        return associated_chunks
    
    def refresh_associative_cache(self):
        """Refresh the associative cache by removing old entries"""
        if len(self.associative_cache) > 1000:  # Limit cache size
            # Keep only the most recent half
            items = list(self.associative_cache.items())
            self.associative_cache = dict(items[-500:])
            logger.debug(" Refreshed associative cache")
    
    def get_memory_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in memory access and consolidation"""
        patterns = {
            "most_accessed_types": {},
            "consolidation_trends": {},
            "associative_clusters": 0,
            "memory_diversity": 0.0
        }
        
        # Analyze memory types
        if hasattr(self.memory_store, 'index'):
            type_counts = {}
            for memory in self.memory_store.index._by_id.values():
                memory_type = memory.metadata.memory_type.value
                type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
            patterns["most_accessed_types"] = type_counts
        
        # Analyze associative clusters
        patterns["associative_clusters"] = len(self.associative_cache)
        
        # Calculate memory diversity (simple measure)
        if self.recent_chunks:
            unique_types = set(chunk.memory_type.value for chunk in self.recent_chunks)
            patterns["memory_diversity"] = len(unique_types) / len(MemoryType)
        
        return patterns
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory curator statistics"""
        stats = self.stats.copy()
        stats.update({
            "recent_chunks_count": len(self.recent_chunks),
            "associative_cache_size": len(self.associative_cache),
            "consolidation_queue_size": len(self.consolidation_queue),
            "similarity_cache_size": len(self.similarity_cache),
            "memory_store_size": len(self.memory_store) if self.memory_store else 0
        })
        return stats


# Helper function for testing
async def test_dmn_memory_curator():
    """Test the DMN memory curator"""
    from .dmn_driver import DMNContext, SystemMode
    
    # Create memory curator with mock memory store
    curator = DMNMemoryCurator()
    
    # Add some test memories
    test_memories = [
        "I discovered an interesting pattern in how thoughts connect",
        "Creative insights often emerge during relaxed states",
        "Memory consolidation happens during rest periods",
        "Patterns in nature often reflect cognitive structures",
        "The brain processes information in parallel streams"
    ]
    
    for memory in test_memories:
        curator.memory_store.store_memory(
            content=memory,
            memory_type=MemoryType.EPISODIC,
            importance=random.uniform(0.3, 0.9),
            tags=["test", "cognition"]
        )
    
    # Test context
    context = DMNContext(
        mode=SystemMode.ACTIVE,
        chunks=["I'm thinking about cognitive patterns"],
        hypothesis="Thoughts follow natural patterns",
        intrusive_thoughts=["What about creativity?"]
    )
    
    print(" Testing DMN Memory Curator...")
    
    # Test ACTIVE mode retrieval
    chunks = await curator.retrieve_chunks(context, SystemMode.ACTIVE)
    print(f"🔍 ACTIVE mode retrieved {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   {i}. {chunk[:60]}...")
    
    # Test PARTIAL_WAKE mode retrieval
    context.mode = SystemMode.PARTIAL_WAKE
    creative_chunks = await curator.retrieve_chunks(context, SystemMode.PARTIAL_WAKE)
    print(f"\n🌙 PARTIAL_WAKE mode retrieved {len(creative_chunks)} chunks:")
    for i, chunk in enumerate(creative_chunks[:3], 1):
        print(f"   {i}. {chunk[:60]}...")
    
    # Test DEFAULT mode consolidation
    context.mode = SystemMode.DEFAULT
    context.recent_thoughts = [
        "New insight about pattern recognition",
        "Creative connections between ideas",
        "Understanding emerges from complexity"
    ]
    
    consolidation_result = await curator.consolidate_memories(context.recent_thoughts, context)
    print(f"\n💾 DEFAULT mode consolidation: {consolidation_result}")
    
    # Get memory patterns
    patterns = curator.get_memory_patterns()
    print(f"\n🔍 Memory patterns: {patterns}")
    
    # Get statistics
    stats = curator.get_stats()
    print(f"\n Memory curator stats: {stats}")
    
    print(" DMN Memory Curator test completed")


if __name__ == "__main__":
    asyncio.run(test_dmn_memory_curator())
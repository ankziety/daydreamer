"""
Memory System Tests

Comprehensive test suite for the memory storage system including
memory entries, indexing, persistence, and the main memory store.
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime, timedelta
import time

from src.memory import (
    MemoryStore, MemoryEntry, MemoryType, MemoryMetadata,
    MemoryIndex, MemoryPersistence
)


class TestMemoryEntry(unittest.TestCase):
    """Test memory entry creation and manipulation."""
    
    def setUp(self):
        self.test_content = "This is a test memory"
        self.test_tags = ["test", "memory", "unit"]
    
    def test_memory_entry_creation(self):
        """Test basic memory entry creation."""
        memory = MemoryEntry(
            content=self.test_content,
            memory_type=MemoryType.EPISODIC,
            importance=0.8,
            emotional_valence=0.5,
            confidence=0.9,
            source="test_source",
            tags=self.test_tags
        )
        
        self.assertEqual(memory.content, self.test_content)
        self.assertEqual(memory.metadata.memory_type, MemoryType.EPISODIC)
        self.assertEqual(memory.metadata.importance, 0.8)
        self.assertEqual(memory.metadata.emotional_valence, 0.5)
        self.assertEqual(memory.metadata.confidence, 0.9)
        self.assertEqual(memory.metadata.source, "test_source")
        self.assertEqual(memory.metadata.tags, self.test_tags)
        self.assertIsNotNone(memory.memory_id)
    
    def test_memory_entry_validation(self):
        """Test that values are properly clamped to valid ranges."""
        memory = MemoryEntry(
            content=self.test_content,
            memory_type=MemoryType.SEMANTIC,
            importance=1.5,  # Should be clamped to 1.0
            emotional_valence=-2.0,  # Should be clamped to -1.0
            confidence=2.0,  # Should be clamped to 1.0
            decay_rate=-0.5  # Should be clamped to 0.0
        )
        
        self.assertEqual(memory.metadata.importance, 1.0)
        self.assertEqual(memory.metadata.emotional_valence, -1.0)
        self.assertEqual(memory.metadata.confidence, 1.0)
        self.assertEqual(memory.metadata.decay_rate, 0.0)
    
    def test_memory_strength_calculation(self):
        """Test memory strength calculation."""
        memory = MemoryEntry(
            content=self.test_content,
            memory_type=MemoryType.EPISODIC,
            importance=0.8,
            emotional_valence=0.5,
            confidence=0.9
        )
        
        strength = memory.get_strength()
        self.assertGreater(strength, 0.0)
        self.assertLessEqual(strength, 1.0)
        
        # Test that access updates affect strength
        original_strength = strength
        memory.update_access()
        memory.update_access()
        memory.update_access()
        
        new_strength = memory.get_strength()
        self.assertGreater(new_strength, original_strength)
    
    def test_memory_serialization(self):
        """Test memory entry serialization and deserialization."""
        memory = MemoryEntry(
            content=self.test_content,
            memory_type=MemoryType.PROCEDURAL,
            importance=0.7,
            emotional_valence=0.3,
            confidence=0.8,
            source="test_source",
            tags=self.test_tags
        )
        
        # Test serialization
        memory_dict = memory.to_dict()
        self.assertEqual(memory_dict['content'], self.test_content)
        self.assertEqual(memory_dict['metadata']['memory_type'], 'procedural')
        self.assertEqual(memory_dict['metadata']['importance'], 0.7)
        
        # Test deserialization
        restored_memory = MemoryEntry.from_dict(memory_dict)
        self.assertEqual(restored_memory.content, memory.content)
        self.assertEqual(restored_memory.metadata.memory_type, memory.metadata.memory_type)
        self.assertEqual(restored_memory.metadata.importance, memory.metadata.importance)
        self.assertEqual(restored_memory.metadata.tags, memory.metadata.tags)
    
    def test_tag_operations(self):
        """Test tag addition and removal."""
        memory = MemoryEntry(
            content=self.test_content,
            memory_type=MemoryType.EMOTIONAL,
            tags=self.test_tags
        )
        
        # Test tag addition
        memory.add_tag("new_tag")
        self.assertIn("new_tag", memory.metadata.tags)
        
        # Test duplicate tag addition
        memory.add_tag("new_tag")
        self.assertEqual(memory.metadata.tags.count("new_tag"), 1)
        
        # Test tag removal
        memory.remove_tag("test")
        self.assertNotIn("test", memory.metadata.tags)
        
        # Test tag checking
        self.assertTrue(memory.has_tag("memory"))
        self.assertFalse(memory.has_tag("nonexistent"))


class TestMemoryIndex(unittest.TestCase):
    """Test memory indexing and search functionality."""
    
    def setUp(self):
        self.index = MemoryIndex()
        self.memories = []
        
        # Create test memories
        for i in range(10):
            memory = MemoryEntry(
                content=f"Test memory {i} with content",
                memory_type=MemoryType.EPISODIC if i % 2 == 0 else MemoryType.SEMANTIC,
                importance=0.5 + (i * 0.1),
                emotional_valence=0.0,
                confidence=0.8,
                source=f"source_{i}",
                tags=[f"tag_{i}", f"common_tag"]
            )
            self.memories.append(memory)
            self.index.add_memory(memory)
    
    def test_memory_addition(self):
        """Test adding memories to index."""
        self.assertEqual(len(self.index), 10)
        
        # Test that all memories are accessible by ID
        for memory in self.memories:
            retrieved = self.index.get_by_id(memory.memory_id)
            self.assertEqual(retrieved.memory_id, memory.memory_id)
    
    def test_memory_removal(self):
        """Test removing memories from index."""
        memory_to_remove = self.memories[0]
        success = self.index.remove_memory(memory_to_remove.memory_id)
        
        self.assertTrue(success)
        self.assertEqual(len(self.index), 9)
        self.assertIsNone(self.index.get_by_id(memory_to_remove.memory_id))
    
    def test_type_based_search(self):
        """Test searching memories by type."""
        episodic_memories = self.index.get_by_type(MemoryType.EPISODIC)
        semantic_memories = self.index.get_by_type(MemoryType.SEMANTIC)
        
        self.assertEqual(len(episodic_memories), 5)
        self.assertEqual(len(semantic_memories), 5)
        
        for memory in episodic_memories:
            self.assertEqual(memory.metadata.memory_type, MemoryType.EPISODIC)
    
    def test_tag_based_search(self):
        """Test searching memories by tag."""
        common_tag_memories = self.index.get_by_tag("common_tag")
        self.assertEqual(len(common_tag_memories), 10)
        
        tag_0_memories = self.index.get_by_tag("tag_0")
        self.assertEqual(len(tag_0_memories), 1)
    
    def test_content_search(self):
        """Test content-based search."""
        # Search for "memory"
        results = self.index.search_content("memory")
        self.assertEqual(len(results), 10)
        
        # Search for specific content
        results = self.index.search_content("Test memory 0")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Test memory 0 with content")
    
    def test_strength_based_search(self):
        """Test searching memories by strength range."""
        strong_memories = self.index.get_by_strength_range(min_strength=0.8)
        self.assertGreater(len(strong_memories), 0)
        
        strongest_memories = self.index.get_strongest_memories(limit=3)
        self.assertEqual(len(strongest_memories), 3)
        
        # Verify they're sorted by strength (with tolerance for floating point precision)
        strengths = [m.get_strength() for m in strongest_memories]
        sorted_strengths = sorted(strengths, reverse=True)
        for actual, expected in zip(strengths, sorted_strengths):
            self.assertAlmostEqual(actual, expected, places=10)
    
    def test_date_based_search(self):
        """Test searching memories by date range."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        recent_memories = self.index.get_by_date_range(start_date=yesterday)
        self.assertEqual(len(recent_memories), 10)
        
        future_memories = self.index.get_by_date_range(start_date=tomorrow)
        self.assertEqual(len(future_memories), 0)
    
    def test_statistics(self):
        """Test index statistics."""
        stats = self.index.get_statistics()
        
        self.assertEqual(stats['total_entries'], 10)
        self.assertIn('episodic', stats['type_distribution'])
        self.assertIn('semantic', stats['type_distribution'])
        self.assertEqual(stats['type_distribution']['episodic'], 5)
        self.assertEqual(stats['type_distribution']['semantic'], 5)


class TestMemoryPersistence(unittest.TestCase):
    """Test memory persistence functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_memory = MemoryEntry(
            content="Test persistent memory",
            memory_type=MemoryType.EPISODIC,
            importance=0.8,
            emotional_valence=0.5,
            confidence=0.9,
            source="test_source",
            tags=["test", "persistent"]
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_sqlite_persistence(self):
        """Test SQLite persistence backend."""
        db_path = os.path.join(self.temp_dir, "test.db")
        persistence = MemoryPersistence(db_path, "sqlite")
        
        # Test save and load
        success = persistence.save_memory(self.test_memory)
        self.assertTrue(success)
        
        loaded_memory = persistence.load_memory(self.test_memory.memory_id)
        self.assertIsNotNone(loaded_memory)
        self.assertEqual(loaded_memory.content, self.test_memory.content)
        self.assertEqual(loaded_memory.metadata.memory_type, self.test_memory.metadata.memory_type)
        
        # Test delete
        success = persistence.delete_memory(self.test_memory.memory_id)
        self.assertTrue(success)
        
        loaded_memory = persistence.load_memory(self.test_memory.memory_id)
        self.assertIsNone(loaded_memory)
        
        persistence.close()
    
    def test_json_persistence(self):
        """Test JSON persistence backend."""
        json_path = os.path.join(self.temp_dir, "test.json")
        persistence = MemoryPersistence(json_path, "json")
        
        # Test save and load
        success = persistence.save_memory(self.test_memory)
        self.assertTrue(success)
        
        loaded_memory = persistence.load_memory(self.test_memory.memory_id)
        self.assertIsNotNone(loaded_memory)
        self.assertEqual(loaded_memory.content, self.test_memory.content)
        
        persistence.close()
    
    def test_pickle_persistence(self):
        """Test pickle persistence backend."""
        pickle_path = os.path.join(self.temp_dir, "test.pkl")
        persistence = MemoryPersistence(pickle_path, "pickle")
        
        # Test save and load
        success = persistence.save_memory(self.test_memory)
        self.assertTrue(success)
        
        loaded_memory = persistence.load_memory(self.test_memory.memory_id)
        self.assertIsNotNone(loaded_memory)
        self.assertEqual(loaded_memory.content, self.test_memory.content)
        
        persistence.close()
    
    def test_load_all_memories(self):
        """Test loading all memories."""
        db_path = os.path.join(self.temp_dir, "test_all.db")
        persistence = MemoryPersistence(db_path, "sqlite")
        
        # Save multiple memories
        memories = []
        for i in range(5):
            memory = MemoryEntry(
                content=f"Memory {i}",
                memory_type=MemoryType.EPISODIC,
                importance=0.5
            )
            memories.append(memory)
            persistence.save_memory(memory)
        
        # Load all memories
        loaded_memories = persistence.load_all_memories()
        self.assertEqual(len(loaded_memories), 5)
        
        persistence.close()
    
    def test_backup_functionality(self):
        """Test backup functionality."""
        db_path = os.path.join(self.temp_dir, "test.db")
        backup_path = os.path.join(self.temp_dir, "backup.db")
        
        persistence = MemoryPersistence(db_path, "sqlite")
        persistence.save_memory(self.test_memory)
        
        # Create backup
        success = persistence.backup(backup_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))
        
        persistence.close()


class TestMemoryStore(unittest.TestCase):
    """Test the main memory store integration."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "memory_store.db")
        self.memory_store = MemoryStore(
            storage_path=self.db_path,
            backend="sqlite",
            auto_save=True,
            max_memories=100,
            consolidation_interval=0  # Disable consolidation for tests
        )
    
    def tearDown(self):
        self.memory_store.close()
        shutil.rmtree(self.temp_dir)
    
    def test_memory_storage_and_retrieval(self):
        """Test basic memory storage and retrieval."""
        # Store a memory
        memory_id = self.memory_store.store_memory(
            content="Test memory content",
            memory_type=MemoryType.EPISODIC,
            importance=0.8,
            emotional_valence=0.5,
            confidence=0.9,
            source="test_source",
            tags=["test", "memory"]
        )
        
        self.assertIsNotNone(memory_id)
        self.assertIn(memory_id, self.memory_store)
        
        # Retrieve the memory
        retrieved_memory = self.memory_store.retrieve_memory(memory_id)
        self.assertIsNotNone(retrieved_memory)
        self.assertEqual(retrieved_memory.content, "Test memory content")
        self.assertEqual(retrieved_memory.metadata.memory_type, MemoryType.EPISODIC)
    
    def test_memory_search(self):
        """Test memory search functionality."""
        # Store multiple memories
        for i in range(5):
            self.memory_store.store_memory(
                content=f"Memory {i} with specific content",
                memory_type=MemoryType.EPISODIC if i % 2 == 0 else MemoryType.SEMANTIC,
                importance=0.5 + (i * 0.1),
                tags=[f"tag_{i}", "common_tag"]
            )
        
        # Test type-based search
        episodic_memories = self.memory_store.get_memories_by_type(MemoryType.EPISODIC)
        self.assertEqual(len(episodic_memories), 3)
        
        # Test tag-based search
        common_tag_memories = self.memory_store.get_memories_by_tag("common_tag")
        self.assertEqual(len(common_tag_memories), 5)
        
        # Test content search
        search_results = self.memory_store.search_memories(query="specific content")
        self.assertEqual(len(search_results), 5)
        
        # Test strength-based search
        strong_memories = self.memory_store.search_memories(min_strength=0.8)
        self.assertGreater(len(strong_memories), 0)
    
    def test_memory_update(self):
        """Test memory update functionality."""
        memory_id = self.memory_store.store_memory(
            content="Original content",
            memory_type=MemoryType.EPISODIC,
            importance=0.5
        )
        
        # Update memory
        success = self.memory_store.update_memory(
            memory_id=memory_id,
            content="Updated content",
            importance=0.8,
            tags=["updated", "tag"]
        )
        
        self.assertTrue(success)
        
        # Verify update
        updated_memory = self.memory_store.retrieve_memory(memory_id)
        self.assertEqual(updated_memory.content, "Updated content")
        self.assertEqual(updated_memory.metadata.importance, 0.8)
        self.assertEqual(updated_memory.metadata.tags, ["updated", "tag"])
    
    def test_memory_deletion(self):
        """Test memory deletion."""
        memory_id = self.memory_store.store_memory(
            content="To be deleted",
            memory_type=MemoryType.EPISODIC
        )
        
        self.assertIn(memory_id, self.memory_store)
        
        # Delete memory
        success = self.memory_store.delete_memory(memory_id)
        self.assertTrue(success)
        
        self.assertNotIn(memory_id, self.memory_store)
        self.assertIsNone(self.memory_store.retrieve_memory(memory_id))
    
    def test_tag_operations(self):
        """Test tag addition and removal."""
        memory_id = self.memory_store.store_memory(
            content="Tag test memory",
            memory_type=MemoryType.EPISODIC,
            tags=["original_tag"]
        )
        
        # Add tag
        success = self.memory_store.add_tag_to_memory(memory_id, "new_tag")
        self.assertTrue(success)
        
        memory = self.memory_store.retrieve_memory(memory_id)
        self.assertIn("new_tag", memory.metadata.tags)
        
        # Remove tag
        success = self.memory_store.remove_tag_from_memory(memory_id, "original_tag")
        self.assertTrue(success)
        
        memory = self.memory_store.retrieve_memory(memory_id)
        self.assertNotIn("original_tag", memory.metadata.tags)
    
    def test_memory_limits(self):
        """Test memory limit enforcement."""
        # Create memory store with small limit
        limited_store = MemoryStore(
            storage_path=os.path.join(self.temp_dir, "limited.db"),
            backend="sqlite",
            max_memories=3,
            consolidation_interval=0
        )
        
        # Store more memories than limit
        for i in range(5):
            limited_store.store_memory(
                content=f"Memory {i}",
                memory_type=MemoryType.EPISODIC,
                importance=0.1 + (i * 0.2)  # Varying importance
            )
        
        # Should enforce limit
        self.assertLessEqual(len(limited_store), 3)
        
        limited_store.close()
    
    def test_statistics(self):
        """Test memory store statistics."""
        # Store some memories
        for i in range(3):
            self.memory_store.store_memory(
                content=f"Memory {i}",
                memory_type=MemoryType.EPISODIC,
                importance=0.5
            )
        
        stats = self.memory_store.get_statistics()
        
        self.assertEqual(stats['index']['total_entries'], 3)
        self.assertEqual(stats['persistence']['total_memories'], 3)
        self.assertTrue(stats['auto_save'])
        self.assertEqual(stats['max_memories'], 100)
    
    def test_backup_and_restore(self):
        """Test backup functionality."""
        # Store a memory
        memory_id = self.memory_store.store_memory(
            content="Backup test memory",
            memory_type=MemoryType.EPISODIC
        )
        
        # Create backup
        backup_path = os.path.join(self.temp_dir, "backup.db")
        success = self.memory_store.backup(backup_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(backup_path))


if __name__ == '__main__':
    unittest.main()
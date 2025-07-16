"""
Memory Persistence Module

Provides database integration and persistence capabilities for the memory system,
supporting multiple storage backends and data formats.
"""

import json
import sqlite3
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime
import logging

from .memory_entry import MemoryEntry, MemoryType


class MemoryPersistence:
    """Database persistence layer for memory entries."""
    
    def __init__(self, storage_path: str = "memory_store.db", backend: str = "sqlite"):
        """
        Initialize persistence layer.
        
        Args:
            storage_path: Path to storage file or database
            backend: Storage backend ('sqlite', 'json', 'pickle')
        """
        self.storage_path = Path(storage_path)
        self.backend = backend.lower()
        self.logger = logging.getLogger(__name__)
        
        # Ensure storage directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.backend == "sqlite":
            self._init_sqlite()
        elif self.backend == "json":
            self._init_json()
        elif self.backend == "pickle":
            self._init_pickle()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        self.connection = sqlite3.connect(self.storage_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables if they don't exist
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL NOT NULL,
                emotional_valence REAL NOT NULL,
                confidence REAL NOT NULL,
                source TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER NOT NULL,
                decay_rate REAL NOT NULL
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON memories(last_accessed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON memories(source)")
        
        self.connection.commit()
    
    def _init_json(self):
        """Initialize JSON storage."""
        if not self.storage_path.exists():
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
    
    def _init_pickle(self):
        """Initialize pickle storage."""
        if not self.storage_path.exists():
            with open(self.storage_path, 'wb') as f:
                pickle.dump([], f)
    
    def save_memory(self, memory: MemoryEntry) -> bool:
        """Save a memory entry to persistent storage."""
        try:
            if self.backend == "sqlite":
                return self._save_sqlite(memory)
            elif self.backend == "json":
                return self._save_json(memory)
            elif self.backend == "pickle":
                return self._save_pickle(memory)
        except Exception as e:
            self.logger.error(f"Failed to save memory {memory.memory_id}: {e}")
            return False
    
    def _save_sqlite(self, memory: MemoryEntry) -> bool:
        """Save memory to SQLite database."""
        cursor = self.connection.cursor()
        
        # Convert memory to database format
        data = {
            'memory_id': memory.memory_id,
            'content': json.dumps(memory.content),
            'memory_type': memory.metadata.memory_type.value,
            'importance': memory.metadata.importance,
            'emotional_valence': memory.metadata.emotional_valence,
            'confidence': memory.metadata.confidence,
            'source': memory.metadata.source,
            'tags': json.dumps(memory.metadata.tags),
            'created_at': memory.metadata.created_at.isoformat(),
            'last_accessed': memory.metadata.last_accessed.isoformat(),
            'access_count': memory.metadata.access_count,
            'decay_rate': memory.metadata.decay_rate
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (memory_id, content, memory_type, importance, emotional_valence, 
             confidence, source, tags, created_at, last_accessed, access_count, decay_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(data.values()))
        
        self.connection.commit()
        return True
    
    def _save_json(self, memory: MemoryEntry) -> bool:
        """Save memory to JSON file."""
        memories = self._load_all_json()
        
        # Update existing or add new
        memory_dict = memory.to_dict()
        
        # Find and replace existing memory
        for i, existing in enumerate(memories):
            if existing['memory_id'] == memory.memory_id:
                memories[i] = memory_dict
                break
        else:
            memories.append(memory_dict)
        
        with open(self.storage_path, 'w') as f:
            json.dump(memories, f, indent=2)
        
        return True
    
    def _save_pickle(self, memory: MemoryEntry) -> bool:
        """Save memory to pickle file."""
        memories = self._load_all_pickle()
        
        # Update existing or add new
        for i, existing in enumerate(memories):
            if existing.memory_id == memory.memory_id:
                memories[i] = memory
                break
        else:
            memories.append(memory)
        
        with open(self.storage_path, 'wb') as f:
            pickle.dump(memories, f)
        
        return True
    
    def load_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Load a memory entry from persistent storage."""
        try:
            if self.backend == "sqlite":
                return self._load_sqlite(memory_id)
            elif self.backend == "json":
                return self._load_json(memory_id)
            elif self.backend == "pickle":
                return self._load_pickle(memory_id)
        except Exception as e:
            self.logger.error(f"Failed to load memory {memory_id}: {e}")
            return None
    
    def _load_sqlite(self, memory_id: str) -> Optional[MemoryEntry]:
        """Load memory from SQLite database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert database row to memory entry format
        data = dict(row)
        try:
            content = json.loads(data['content'])
            tags = json.loads(data['tags'])
            
            # Create memory entry directly
            memory = MemoryEntry(
                content=content,
                memory_type=MemoryType(data['memory_type']),
                importance=data['importance'],
                emotional_valence=data['emotional_valence'],
                confidence=data['confidence'],
                source=data['source'],
                tags=tags,
                memory_id=data['memory_id'],
                created_at=datetime.fromisoformat(data['created_at']),
                decay_rate=data['decay_rate']
            )
            
            # Restore access statistics
            memory.metadata.last_accessed = datetime.fromisoformat(data['last_accessed'])
            memory.metadata.access_count = data['access_count']
            
            return memory
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error(f"Failed to load memory {memory_id}: {e}")
            return None
    
    def _load_json(self, memory_id: str) -> Optional[MemoryEntry]:
        """Load memory from JSON file."""
        memories = self._load_all_json()
        
        for memory_dict in memories:
            if memory_dict['memory_id'] == memory_id:
                return MemoryEntry.from_dict(memory_dict)
        
        return None
    
    def _load_pickle(self, memory_id: str) -> Optional[MemoryEntry]:
        """Load memory from pickle file."""
        memories = self._load_all_pickle()
        
        for memory in memories:
            if memory.memory_id == memory_id:
                return memory
        
        return None
    
    def load_all_memories(self) -> List[MemoryEntry]:
        """Load all memory entries from persistent storage."""
        try:
            if self.backend == "sqlite":
                return self._load_all_sqlite()
            elif self.backend == "json":
                return self._load_all_json()
            elif self.backend == "pickle":
                return self._load_all_pickle()
        except Exception as e:
            self.logger.error(f"Failed to load all memories: {e}")
            return []
    
    def _load_all_sqlite(self) -> List[MemoryEntry]:
        """Load all memories from SQLite database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM memories")
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            data = dict(row)
            try:
                content = json.loads(data['content'])
                tags = json.loads(data['tags'])
                
                # Create memory entry directly
                memory = MemoryEntry(
                    content=content,
                    memory_type=MemoryType(data['memory_type']),
                    importance=data['importance'],
                    emotional_valence=data['emotional_valence'],
                    confidence=data['confidence'],
                    source=data['source'],
                    tags=tags,
                    memory_id=data['memory_id'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    decay_rate=data['decay_rate']
                )
                
                # Restore access statistics
                memory.metadata.last_accessed = datetime.fromisoformat(data['last_accessed'])
                memory.metadata.access_count = data['access_count']
                
                memories.append(memory)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                self.logger.warning(f"Failed to load memory {data.get('memory_id', 'unknown')}: {e}")
                continue
        
        return memories
    
    def _load_all_json(self) -> List[Dict[str, Any]]:
        """Load all memories from JSON file."""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _load_all_pickle(self) -> List[MemoryEntry]:
        """Load all memories from pickle file."""
        try:
            with open(self.storage_path, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError):
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry from persistent storage."""
        try:
            if self.backend == "sqlite":
                return self._delete_sqlite(memory_id)
            elif self.backend == "json":
                return self._delete_json(memory_id)
            elif self.backend == "pickle":
                return self._delete_pickle(memory_id)
        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def _delete_sqlite(self, memory_id: str) -> bool:
        """Delete memory from SQLite database."""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def _delete_json(self, memory_id: str) -> bool:
        """Delete memory from JSON file."""
        memories = self._load_all_json()
        original_count = len(memories)
        
        memories = [m for m in memories if m['memory_id'] != memory_id]
        
        if len(memories) < original_count:
            with open(self.storage_path, 'w') as f:
                json.dump(memories, f, indent=2)
            return True
        
        return False
    
    def _delete_pickle(self, memory_id: str) -> bool:
        """Delete memory from pickle file."""
        memories = self._load_all_pickle()
        original_count = len(memories)
        
        memories = [m for m in memories if m.memory_id != memory_id]
        
        if len(memories) < original_count:
            with open(self.storage_path, 'wb') as f:
                pickle.dump(memories, f)
            return True
        
        return False
    
    def get_memory_count(self) -> int:
        """Get total number of stored memories."""
        try:
            if self.backend == "sqlite":
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                return cursor.fetchone()[0]
            elif self.backend == "json":
                return len(self._load_all_json())
            elif self.backend == "pickle":
                return len(self._load_all_pickle())
        except Exception as e:
            self.logger.error(f"Failed to get memory count: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all stored memories."""
        try:
            if self.backend == "sqlite":
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM memories")
                self.connection.commit()
            elif self.backend == "json":
                with open(self.storage_path, 'w') as f:
                    json.dump([], f)
            elif self.backend == "pickle":
                with open(self.storage_path, 'wb') as f:
                    pickle.dump([], f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear all memories: {e}")
            return False
    
    def backup(self, backup_path: str) -> bool:
        """Create a backup of the memory store."""
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.backend == "sqlite":
                # SQLite backup
                backup_conn = sqlite3.connect(backup_path)
                self.connection.backup(backup_conn)
                backup_conn.close()
            else:
                # File-based backup
                import shutil
                shutil.copy2(self.storage_path, backup_path)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {
                'backend': self.backend,
                'storage_path': str(self.storage_path),
                'total_memories': self.get_memory_count(),
                'file_size': self.storage_path.stat().st_size if self.storage_path.exists() else 0
            }
            
            if self.backend == "sqlite":
                cursor = self.connection.cursor()
                cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                type_counts = dict(cursor.fetchall())
                stats['type_distribution'] = type_counts
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def close(self):
        """Close database connections and cleanup."""
        if self.backend == "sqlite" and hasattr(self, 'connection'):
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
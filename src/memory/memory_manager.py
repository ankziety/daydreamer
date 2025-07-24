#!/usr/bin/env python3
"""
Persistent Memory Manager
=========================

This module implements persistent memory storage for chat history and insights
across sessions, providing the AI with continuity and context from previous
conversations.
"""

import sqlite3
import json
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class ConversationMemory:
    """Represents a stored conversation memory"""
    id: str
    timestamp: datetime
    user_input: str
    ai_response: str
    context: str
    importance: float
    tags: List[str]
    session_id: str
    cot_summary: Optional[str] = None
    daydream_insights: Optional[str] = None


@dataclass
class InsightMemory:
    """Represents a stored insight from chain of thought or daydreaming"""
    id: str
    timestamp: datetime
    insight_type: str  # "cot" or "daydream"
    insight_content: str
    creativity_score: float
    relevance_score: float
    context: str
    knowledge_domain: Optional[str] = None
    connections: Optional[List[str]] = None


@dataclass
class UserProfile:
    """Represents learned information about the user"""
    id: str
    interests: Dict[str, float]  # topic -> interest score
    communication_style: Dict[str, str]
    preferences: Dict[str, Any]
    conversation_patterns: Dict[str, float]
    last_updated: datetime


class PersistentMemoryManager:
    """
    Manages persistent storage of conversation history, insights, and user profile
    across sessions to provide continuity and context.
    """
    
    def __init__(self, db_path: str = "src/memory/daydreamer_memory.db"):
        """
        Initialize persistent memory manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the SQLite database with required tables"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        
        # Create tables
        self._create_tables()
        
        # Enable WAL mode for better concurrent access
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.commit()
    
    def _create_tables(self):
        """Create database tables for storing memories"""
        
        # Conversation memories table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS conversation_memories (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context TEXT,
                importance REAL DEFAULT 0.5,
                tags TEXT,  -- JSON array
                session_id TEXT NOT NULL,
                cot_summary TEXT,
                daydream_insights TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insight memories table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS insight_memories (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                insight_content TEXT NOT NULL,
                creativity_score REAL DEFAULT 0.0,
                relevance_score REAL DEFAULT 0.0,
                context TEXT,
                knowledge_domain TEXT,
                connections TEXT,  -- JSON array
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User profile table
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id TEXT PRIMARY KEY DEFAULT 'default',
                interests TEXT,  -- JSON dict
                communication_style TEXT,  -- JSON dict
                preferences TEXT,  -- JSON dict
                conversation_patterns TEXT,  -- JSON dict
                last_updated TEXT NOT NULL
            )
        """)
        
        # Sessions table for tracking conversation sessions
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                message_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                summary TEXT
            )
        """)
        
        # Create indexes for better query performance
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_memories(timestamp)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_memories(session_id)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_insight_timestamp ON insight_memories(timestamp)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_insight_type ON insight_memories(insight_type)")
        
        self.connection.commit()
    
    def store_conversation(self, 
                          user_input: str,
                          ai_response: str,
                          session_id: str,
                          context: str = "",
                          importance: float = 0.5,
                          tags: List[str] = None,
                          cot_summary: str = None,
                          daydream_insights: str = None) -> str:
        """
        Store a conversation exchange.
        
        Args:
            user_input: User's message
            ai_response: AI's response
            session_id: Current session identifier
            context: Conversation context
            importance: Importance score (0.0-1.0)
            tags: Optional tags for categorization
            cot_summary: Summary of chain of thought reasoning
            daydream_insights: Summary of daydream insights
            
        Returns:
            Memory ID
        """
        memory_id = self._generate_id(user_input, ai_response)
        timestamp = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])
        
        self.connection.execute("""
            INSERT OR REPLACE INTO conversation_memories 
            (id, timestamp, user_input, ai_response, context, importance, tags, session_id, cot_summary, daydream_insights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (memory_id, timestamp, user_input, ai_response, context, importance, tags_json, session_id, cot_summary, daydream_insights))
        
        # Update session message count
        self.connection.execute("""
            INSERT OR IGNORE INTO sessions (session_id, start_time, message_count) VALUES (?, ?, 0)
        """, (session_id, timestamp))
        
        self.connection.execute("""
            UPDATE sessions SET message_count = message_count + 1, end_time = ? WHERE session_id = ?
        """, (timestamp, session_id))
        
        self.connection.commit()
        return memory_id
    
    def store_insight(self,
                     insight_type: str,
                     insight_content: str,
                     creativity_score: float = 0.0,
                     relevance_score: float = 0.0,
                     context: str = "",
                     knowledge_domain: str = None,
                     connections: List[str] = None) -> str:
        """
        Store an insight from chain of thought or daydreaming.
        
        Args:
            insight_type: "cot" or "daydream"
            insight_content: The insight text
            creativity_score: Creativity rating (0.0-1.0)
            relevance_score: Relevance rating (0.0-1.0)
            context: Context when insight was generated
            knowledge_domain: Knowledge domain for daydreams
            connections: Connections made during insight
            
        Returns:
            Insight ID
        """
        insight_id = self._generate_id(insight_content, insight_type)
        timestamp = datetime.now().isoformat()
        connections_json = json.dumps(connections or [])
        
        self.connection.execute("""
            INSERT OR REPLACE INTO insight_memories 
            (id, timestamp, insight_type, insight_content, creativity_score, relevance_score, context, knowledge_domain, connections)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (insight_id, timestamp, insight_type, insight_content, creativity_score, relevance_score, context, knowledge_domain, connections_json))
        
        self.connection.commit()
        return insight_id
    
    def get_recent_conversations(self, 
                               limit: int = 10,
                               session_id: Optional[str] = None,
                               days_back: int = 7) -> List[ConversationMemory]:
        """
        Retrieve recent conversation memories.
        
        Args:
            limit: Maximum number of conversations to retrieve
            session_id: Optional filter by session
            days_back: Only get conversations from last N days
            
        Returns:
            List of conversation memories
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        if session_id:
            query = """
                SELECT * FROM conversation_memories 
                WHERE session_id = ? AND timestamp > ?
                ORDER BY timestamp DESC LIMIT ?
            """
            params = (session_id, cutoff_date, limit)
        else:
            query = """
                SELECT * FROM conversation_memories 
                WHERE timestamp > ?
                ORDER BY timestamp DESC LIMIT ?
            """
            params = (cutoff_date, limit)
        
        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = ConversationMemory(
                id=row['id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                user_input=row['user_input'],
                ai_response=row['ai_response'],
                context=row['context'] or "",
                importance=row['importance'],
                tags=json.loads(row['tags'] or '[]'),
                session_id=row['session_id'],
                cot_summary=row['cot_summary'],
                daydream_insights=row['daydream_insights']
            )
            memories.append(memory)
        
        return memories
    
    def get_relevant_memories(self, 
                            query_text: str,
                            limit: int = 5,
                            importance_threshold: float = 0.3) -> List[ConversationMemory]:
        """
        Retrieve memories relevant to a query using simple text matching.
        
        Args:
            query_text: Text to search for
            limit: Maximum number of memories to return
            importance_threshold: Minimum importance score
            
        Returns:
            List of relevant memories
        """
        # Simple keyword-based relevance (could be enhanced with embeddings)
        keywords = [word.lower() for word in query_text.split() if len(word) > 3]
        
        if not keywords:
            return []
        
        # Create search conditions
        search_conditions = " OR ".join([
            "(LOWER(user_input) LIKE ? OR LOWER(ai_response) LIKE ? OR LOWER(context) LIKE ?)"
            for _ in keywords
        ])
        
        query = f"""
            SELECT * FROM conversation_memories 
            WHERE importance >= ? AND ({search_conditions})
            ORDER BY importance DESC, timestamp DESC LIMIT ?
        """
        
        # Prepare parameters
        params = [importance_threshold]
        for keyword in keywords:
            pattern = f"%{keyword}%"
            params.extend([pattern, pattern, pattern])
        params.append(limit)
        
        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = ConversationMemory(
                id=row['id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                user_input=row['user_input'],
                ai_response=row['ai_response'],
                context=row['context'] or "",
                importance=row['importance'],
                tags=json.loads(row['tags'] or '[]'),
                session_id=row['session_id'],
                cot_summary=row['cot_summary'],
                daydream_insights=row['daydream_insights']
            )
            memories.append(memory)
        
        return memories
    
    def get_random_memory(self) -> Optional[ConversationMemory]:
        """Get a random conversation memory for daydreaming"""
        cursor = self.connection.execute("""
            SELECT * FROM conversation_memories 
            ORDER BY RANDOM() LIMIT 1
        """)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return ConversationMemory(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            user_input=row['user_input'],
            ai_response=row['ai_response'],
            context=row['context'] or "",
            importance=row['importance'],
            tags=json.loads(row['tags'] or '[]'),
            session_id=row['session_id'],
            cot_summary=row['cot_summary'],
            daydream_insights=row['daydream_insights']
        )
    
    def get_insights(self, 
                    insight_type: Optional[str] = None,
                    limit: int = 10,
                    min_score: float = 0.5) -> List[InsightMemory]:
        """
        Retrieve stored insights.
        
        Args:
            insight_type: Optional filter by "cot" or "daydream"
            limit: Maximum number of insights
            min_score: Minimum combined creativity+relevance score
            
        Returns:
            List of insights
        """
        if insight_type:
            query = """
                SELECT * FROM insight_memories 
                WHERE insight_type = ? AND (creativity_score + relevance_score) >= ?
                ORDER BY timestamp DESC LIMIT ?
            """
            params = (insight_type, min_score, limit)
        else:
            query = """
                SELECT * FROM insight_memories 
                WHERE (creativity_score + relevance_score) >= ?
                ORDER BY timestamp DESC LIMIT ?
            """
            params = (min_score, limit)
        
        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()
        
        insights = []
        for row in rows:
            insight = InsightMemory(
                id=row['id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                insight_type=row['insight_type'],
                insight_content=row['insight_content'],
                creativity_score=row['creativity_score'],
                relevance_score=row['relevance_score'],
                context=row['context'] or "",
                knowledge_domain=row['knowledge_domain'],
                connections=json.loads(row['connections'] or '[]')
            )
            insights.append(insight)
        
        return insights
    
    def update_user_profile(self, 
                           interests: Dict[str, float] = None,
                           communication_style: Dict[str, str] = None,
                           preferences: Dict[str, Any] = None,
                           conversation_patterns: Dict[str, float] = None):
        """
        Update or create user profile with learned information.
        
        Args:
            interests: Topic interests with scores
            communication_style: Communication style preferences
            preferences: General preferences
            conversation_patterns: Conversation pattern analysis
        """
        profile_id = "default"
        timestamp = datetime.now().isoformat()
        
        # Get existing profile
        existing_profile = self.get_user_profile()
        
        if existing_profile:
            # Merge with existing data
            merged_interests = existing_profile.interests.copy()
            if interests:
                merged_interests.update(interests)
            
            merged_style = existing_profile.communication_style.copy()
            if communication_style:
                merged_style.update(communication_style)
            
            merged_preferences = existing_profile.preferences.copy()
            if preferences:
                merged_preferences.update(preferences)
            
            merged_patterns = existing_profile.conversation_patterns.copy()
            if conversation_patterns:
                merged_patterns.update(conversation_patterns)
        else:
            # Create new profile
            merged_interests = interests or {}
            merged_style = communication_style or {}
            merged_preferences = preferences or {}
            merged_patterns = conversation_patterns or {}
        
        self.connection.execute("""
            INSERT OR REPLACE INTO user_profile 
            (id, interests, communication_style, preferences, conversation_patterns, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            json.dumps(merged_interests),
            json.dumps(merged_style),
            json.dumps(merged_preferences),
            json.dumps(merged_patterns),
            timestamp
        ))
        
        self.connection.commit()
    
    def get_user_profile(self) -> Optional[UserProfile]:
        """Get the current user profile"""
        cursor = self.connection.execute("""
            SELECT * FROM user_profile WHERE id = 'default'
        """)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return UserProfile(
            id=row['id'],
            interests=json.loads(row['interests'] or '{}'),
            communication_style=json.loads(row['communication_style'] or '{}'),
            preferences=json.loads(row['preferences'] or '{}'),
            conversation_patterns=json.loads(row['conversation_patterns'] or '{}'),
            last_updated=datetime.fromisoformat(row['last_updated'])
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        stats = {}
        
        # Conversation stats
        cursor = self.connection.execute("SELECT COUNT(*) as count FROM conversation_memories")
        stats['total_conversations'] = cursor.fetchone()['count']
        
        cursor = self.connection.execute("SELECT COUNT(DISTINCT session_id) as count FROM conversation_memories")
        stats['total_sessions'] = cursor.fetchone()['count']
        
        # Insight stats
        cursor = self.connection.execute("SELECT COUNT(*) as count FROM insight_memories")
        stats['total_insights'] = cursor.fetchone()['count']
        
        cursor = self.connection.execute("SELECT insight_type, COUNT(*) as count FROM insight_memories GROUP BY insight_type")
        insight_breakdown = {row['insight_type']: row['count'] for row in cursor.fetchall()}
        stats['insights_by_type'] = insight_breakdown
        
        # Recent activity
        recent_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        cursor = self.connection.execute("SELECT COUNT(*) as count FROM conversation_memories WHERE timestamp > ?", (recent_cutoff,))
        stats['recent_conversations'] = cursor.fetchone()['count']
        
        return stats
    
    def create_session_summary(self, session_id: str, summary: str):
        """Create a summary for a completed session"""
        self.connection.execute("""
            UPDATE sessions SET summary = ? WHERE session_id = ?
        """, (summary, session_id))
        self.connection.commit()
    
    def cleanup_old_memories(self, days_to_keep: int = 90):
        """Clean up old memories to prevent database bloat"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        # Keep important memories longer
        self.connection.execute("""
            DELETE FROM conversation_memories 
            WHERE timestamp < ? AND importance < 0.7
        """, (cutoff_date,))
        
        # Clean up old insights with low scores
        self.connection.execute("""
            DELETE FROM insight_memories 
            WHERE timestamp < ? AND (creativity_score + relevance_score) < 0.5
        """, (cutoff_date,))
        
        self.connection.commit()
    
    def _generate_id(self, *content: str) -> str:
        """Generate a unique ID for memory storage"""
        combined = "|".join(content)
        timestamp = datetime.now().isoformat()
        hash_input = f"{combined}|{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __del__(self):
        """Ensure database connection is closed"""
        self.close()


# Convenience functions
def create_memory_manager(db_path: str = "daydreamer_memory.db") -> PersistentMemoryManager:
    """Create a new persistent memory manager"""
    return PersistentMemoryManager(db_path)


def get_conversation_context(memory_manager: PersistentMemoryManager, 
                           current_session: str,
                           context_length: int = 5) -> str:
    """
    Get conversation context from recent memories.
    
    Args:
        memory_manager: Memory manager instance
        current_session: Current session ID
        context_length: Number of recent exchanges to include
        
    Returns:
        Formatted context string
    """
    recent_memories = memory_manager.get_recent_conversations(
        limit=context_length,
        session_id=current_session
    )
    
    if not recent_memories:
        return ""
    
    context_parts = []
    for memory in reversed(recent_memories):  # Reverse to get chronological order
        context_parts.append(f"User: {memory.user_input}")
        context_parts.append(f"AI: {memory.ai_response}")
    
    return "\n".join(context_parts)


def analyze_user_interests(memory_manager: PersistentMemoryManager) -> Dict[str, float]:
    """
    Analyze user interests from conversation history.
    
    Args:
        memory_manager: Memory manager instance
        
    Returns:
        Dictionary of interests with scores
    """
    recent_memories = memory_manager.get_recent_conversations(limit=50)
    
    # Simple keyword-based interest analysis
    interest_keywords = {
        'technology': ['ai', 'artificial', 'intelligence', 'computer', 'programming', 'software', 'code'],
        'science': ['science', 'research', 'discovery', 'experiment', 'theory', 'physics', 'biology'],
        'philosophy': ['philosophy', 'consciousness', 'meaning', 'existence', 'purpose', 'ethics'],
        'creativity': ['creative', 'art', 'imagination', 'design', 'innovation', 'artistic'],
        'learning': ['learn', 'education', 'knowledge', 'understanding', 'study', 'explore'],
        'psychology': ['emotion', 'behavior', 'mind', 'psychology', 'feelings', 'mental']
    }
    
    interest_scores = {topic: 0.0 for topic in interest_keywords.keys()}
    
    for memory in recent_memories:
        text = f"{memory.user_input} {memory.ai_response}".lower()
        for topic, keywords in interest_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    interest_scores[topic] += memory.importance
    
    # Normalize scores
    total_memories = len(recent_memories)
    if total_memories > 0:
        for topic in interest_scores:
            interest_scores[topic] = interest_scores[topic] / total_memories
    
    return interest_scores
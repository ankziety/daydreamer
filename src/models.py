"""
Core data models for the Daydreamer system.

This module defines the data structures used throughout the system,
including thoughts, memories, intrusions, and system states.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid


class SystemMode(Enum):
    """System operating modes as defined in the design document."""
    ACTIVE = "active"  # Full reasoning, chain-of-thought ON, memory read/write
    PARTIAL_WAKE = "partial_wake"  # Brain break mode, creative associations
    DEFAULT = "default"  # Sleep mode, memory consolidation only


class Thought(BaseModel):
    """Represents a single thought in the system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    priority: int = Field(ge=1, le=10)
    timestamp: datetime = Field(default_factory=datetime.now)
    source_agent: str
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chain_of_thought: Optional[str] = None
    quality_score: Optional[float] = None
    novelty_score: Optional[float] = None
    coherence_score: Optional[float] = None


class DriverContext(BaseModel):
    """Context passed to the driver for each cycle."""
    mode: SystemMode
    chunks: List[str] = Field(default_factory=list)
    hypothesis: str = ""
    critic_review: str = ""
    grant_proposal: str = ""
    working_memory_load: float = 0.0
    exhaustion_signals: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class Intrusion(BaseModel):
    """Represents an external interruption or intrusive thought."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    content: str
    urgency: int = Field(ge=1, le=10)  # 1-10 scale
    intensity: int = Field(ge=1, le=10)  # 1-10 scale for intrusive thoughts
    difficulty: int = Field(ge=1, le=10)  # Suppression effort required
    timestamp: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    processed: bool = False
    response: Optional[str] = None
    suppressed: bool = False


class BrainBreak(BaseModel):
    """Represents a brain break session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = Field(default_factory=datetime.now)
    duration: timedelta
    break_type: str  # "creative_association", "virtual_walk", "internet_browse"
    activities: List[str] = Field(default_factory=list)
    generated_associations: List[str] = Field(default_factory=list)
    mood_shift_achieved: bool = False


class Synthesis(BaseModel):
    """Represents a synthesis operation connecting multiple thoughts."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_thoughts: List[str] = Field(default_factory=list)
    output_insight: str
    confidence: float = Field(ge=0.0, le=1.0)
    synthesis_type: str  # "pattern", "abstraction", "connection", "analogy", "hypothesis"
    timestamp: datetime = Field(default_factory=datetime.now)
    chain_of_thought: str
    intrusive_thoughts_consulted: List[str] = Field(default_factory=list)


class ThoughtEvaluation(BaseModel):
    """Evaluation results for a thought."""
    thought_id: str
    quality_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    novelty_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    routing_decision: str
    memory_routing_flags: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    suppression_required: bool = False


class MemoryEntry(BaseModel):
    """Represents an entry in the memory system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    embedding: List[float] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    importance_score: float = Field(ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    related_memories: List[str] = Field(default_factory=list)
    memory_type: str  # "working", "long_term"
    consolidation_status: str = "pending"  # "pending", "consolidated", "pruned"


class ExternalSource(BaseModel):
    """Represents an external information source."""
    url: str
    content: str
    credibility_score: float = Field(ge=0.0, le=1.0)
    last_updated: datetime = Field(default_factory=datetime.now)
    relevance_tags: List[str] = Field(default_factory=list)
    integration_status: str = "pending"
    search_query: str = ""
    rate_limit_status: str = "available"


class NotepadEntry(BaseModel):
    """Represents an entry in the working memory notepad."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    linked_thoughts: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


class SystemState(BaseModel):
    """Current state of the entire system."""
    mode: SystemMode
    active_thoughts: List[Thought] = Field(default_factory=list)
    recent_intrusions: List[Intrusion] = Field(default_factory=list)
    memory_entries: List[MemoryEntry] = Field(default_factory=list)
    notepad_entries: List[NotepadEntry] = Field(default_factory=list)
    last_brain_break: Optional[BrainBreak] = None
    working_memory_load: float = 0.0
    exhaustion_level: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
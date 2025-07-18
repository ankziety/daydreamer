"""
Intrusive Thoughts System for Default Mode Network

This system captures and processes intrusive thoughts with parameterized intensity
and difficulty levels. It simulates the natural occurrence of unwanted or
random thoughts that can interrupt normal cognitive processing using AI-generated content.
"""

import asyncio
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum

from .ai_thought_generator import AIThoughtGenerator, ThoughtContext, AIThoughtConfig

logger = logging.getLogger(__name__)


class ThoughtType(Enum):
    """Types of intrusive thoughts - maps to AI thought contexts"""
    RANDOM = "random"           # Random, unrelated thoughts
    WORRY = "worry"             # Anxiety-inducing thoughts
    MEMORY = "memory"           # Sudden memory recalls
    CREATIVE = "creative"       # Creative interruptions
    SENSORY = "sensory"         # Sensory-triggered thoughts
    PHILOSOPHICAL = "philosophical"  # Deep questions
    ABSURD = "absurd"           # Absurd or surreal thoughts

    def to_thought_context(self) -> ThoughtContext:
        """Convert to AI thought context"""
        mapping = {
            self.RANDOM: ThoughtContext.RANDOM,
            self.WORRY: ThoughtContext.WORRY,
            self.MEMORY: ThoughtContext.MEMORY,
            self.CREATIVE: ThoughtContext.CREATIVE,
            self.SENSORY: ThoughtContext.SENSORY,
            self.PHILOSOPHICAL: ThoughtContext.PHILOSOPHICAL,
            self.ABSURD: ThoughtContext.ABSURD
        }
        return mapping.get(self, ThoughtContext.RANDOM)


@dataclass
class IntrusiveThought:
    """Represents an intrusive thought with intensity and difficulty parameters"""
    content: str
    intensity: int  # 1-10 scale, how intrusive/disruptive
    difficulty: int  # 1-10 scale, how hard to suppress
    thought_type: ThoughtType = ThoughtType.RANDOM
    source: str = "spontaneous"
    timestamp: datetime = field(default_factory=datetime.now)
    thought_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    suppressed: bool = False
    suppression_effort: int = 0  # Effort required to suppress
    triggers: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def requires_suppression(self) -> bool:
        """Check if this thought requires active suppression"""
        return self.intensity > 7 or self.difficulty > 6
    
    def calculate_disruption_score(self) -> float:
        """Calculate how disruptive this thought is to current processing"""
        base_score = (self.intensity * 0.6 + self.difficulty * 0.4) / 10.0
        
        # Type modifiers
        type_modifiers = {
            ThoughtType.WORRY: 1.3,
            ThoughtType.ABSURD: 1.2,
            ThoughtType.CREATIVE: 0.8,
            ThoughtType.PHILOSOPHICAL: 1.1,
            ThoughtType.RANDOM: 1.0,
            ThoughtType.MEMORY: 0.9,
            ThoughtType.SENSORY: 1.1
        }
        
        modifier = type_modifiers.get(self.thought_type, 1.0)
        return min(1.0, base_score * modifier)


class IntrusiveThoughtsSystem:
    """
    System for generating, managing and processing intrusive thoughts.
    
    This system:
    - Generates spontaneous intrusive thoughts
    - Processes external intrusive thoughts
    - Manages thought suppression
    - Tracks thought patterns and triggers
    - Provides thoughts to the DMN driver for processing
    """
    
    def __init__(self, 
                 spontaneous_rate: float = 0.1,  # thoughts per second
                 max_pending: int = 10,
                 suppression_decay: float = 0.95,
                 ai_config: AIThoughtConfig = None):
        """
        Initialize the intrusive thoughts system.
        
        Args:
            spontaneous_rate: Rate of spontaneous thought generation
            max_pending: Maximum pending thoughts to keep
            suppression_decay: Rate at which suppression effort decays
            ai_config: Configuration for AI thought generation
        """
        self.spontaneous_rate = spontaneous_rate
        self.max_pending = max_pending
        self.suppression_decay = suppression_decay
        
        # Initialize AI thought generator
        self.ai_generator = AIThoughtGenerator(ai_config or AIThoughtConfig())
        
        # Thought storage
        self.pending_thoughts: List[IntrusiveThought] = []
        self.processed_thoughts: List[IntrusiveThought] = []
        self.suppressed_thoughts: List[IntrusiveThought] = []
        
        # Generation state
        self.is_running = False
        self.generator_task: Optional[asyncio.Task] = None
        self.last_spontaneous = datetime.now()
        
        # Pattern tracking
        self.thought_patterns: Dict[str, int] = {}
        self.trigger_associations: Dict[str, List[str]] = {}
        
        # Statistics
        self.stats = {
            "total_generated": 0,
            "total_processed": 0,
            "total_suppressed": 0,
            "suppression_attempts": 0,
            "average_intensity": 0.0,
            "average_difficulty": 0.0,
            "most_common_type": None
        }
    
    async def start(self):
        """Start the intrusive thoughts generation system"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🌀 Starting Intrusive Thoughts System")
        
        # Initialize AI generator
        await self.ai_generator.initialize()
        logger.info(f" AI Generator Status: {self.ai_generator.get_status()}")
        
        # Start spontaneous thought generation
        self.generator_task = asyncio.create_task(self._spontaneous_generation_loop())
    
    async def stop(self):
        """Stop the intrusive thoughts system"""
        self.is_running = False
        
        if self.generator_task:
            self.generator_task.cancel()
            try:
                await self.generator_task
            except asyncio.CancelledError:
                pass
        
        logger.info(" Stopped Intrusive Thoughts System")
    
    async def _spontaneous_generation_loop(self):
        """Main loop for generating spontaneous intrusive thoughts"""
        while self.is_running:
            try:
                # Check if we should generate a new thought
                if (len(self.pending_thoughts) < self.max_pending and
                    random.random() < self.spontaneous_rate):
                    
                    thought = await self._generate_spontaneous_thought()
                    self.pending_thoughts.append(thought)
                    self.stats["total_generated"] += 1
                    
                    logger.debug(f" Generated intrusive thought: {thought.content[:50]}...")
                
                # Decay suppression efforts
                self._decay_suppression()
                
                # Update statistics
                self._update_statistics()
                
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in spontaneous thought generation: {e}")
                await asyncio.sleep(1.0)
    
    async def _generate_spontaneous_thought(self) -> IntrusiveThought:
        """Generate a spontaneous intrusive thought using AI"""
        # Choose thought type based on current patterns
        thought_type = self._choose_thought_type()
        
        # Assign intensity and difficulty
        intensity = random.randint(1, 10)
        difficulty = random.randint(1, 10)
        
        # Higher intensity thoughts are often harder to suppress
        if intensity > 7:
            difficulty = max(difficulty, random.randint(5, 10))
        
        # Generate AI-powered content
        try:
            context = thought_type.to_thought_context()
            content = await self.ai_generator.generate_thought(context, intensity, difficulty)
        except Exception as e:
            logger.warning(f"AI generation failed, using fallback: {e}")
            content = f"A {thought_type.value} thought emerges (intensity: {intensity})"
        
        return IntrusiveThought(
            content=content,
            intensity=intensity,
            difficulty=difficulty,
            thought_type=thought_type,
            source="spontaneous"
        )
    
    def _choose_thought_type(self) -> ThoughtType:
        """Choose thought type based on patterns and randomness"""
        # Weight types based on recent patterns
        weights = {
            ThoughtType.RANDOM: 3,
            ThoughtType.CREATIVE: 2,
            ThoughtType.MEMORY: 2,
            ThoughtType.PHILOSOPHICAL: 1,
            ThoughtType.SENSORY: 2,
            ThoughtType.WORRY: 1,
            ThoughtType.ABSURD: 1
        }
        
        # Increase worry thoughts if many high-intensity thoughts recently
        recent_high_intensity = sum(1 for t in self.processed_thoughts[-10:] if t.intensity > 7)
        if recent_high_intensity > 3:
            weights[ThoughtType.WORRY] = 3
        
        # Choose based on weights
        choices = []
        for thought_type, weight in weights.items():
            choices.extend([thought_type] * weight)
        
        return random.choice(choices)

    
    def add_thought(self, content: str, intensity: int = 5, difficulty: int = 3, 
                   thought_type: ThoughtType = ThoughtType.RANDOM, source: str = "external",
                   triggers: List[str] = None):
        """Add an external intrusive thought"""
        thought = IntrusiveThought(
            content=content,
            intensity=max(1, min(10, intensity)),
            difficulty=max(1, min(10, difficulty)),
            thought_type=thought_type,
            source=source,
            triggers=triggers or []
        )
        
        if len(self.pending_thoughts) < self.max_pending:
            self.pending_thoughts.append(thought)
            self.stats["total_generated"] += 1
            logger.debug(f" Added external intrusive thought: {content[:50]}...")
        else:
            logger.warning("Too many pending intrusive thoughts, dropping new thought")
    
    async def get_pending_thoughts(self) -> List[IntrusiveThought]:
        """Get all pending intrusive thoughts and mark them as processed"""
        thoughts = self.pending_thoughts.copy()
        self.pending_thoughts.clear()
        
        for thought in thoughts:
            self.processed_thoughts.append(thought)
            self.stats["total_processed"] += 1
        
        # Keep only recent processed thoughts
        if len(self.processed_thoughts) > 100:
            self.processed_thoughts = self.processed_thoughts[-50:]
        
        return thoughts
    
    def suppress_thought(self, thought_id: str, effort: int = 5) -> bool:
        """Attempt to suppress a specific thought"""
        self.stats["suppression_attempts"] += 1
        
        # Find the thought in pending or processed
        thought = None
        for t in self.pending_thoughts + self.processed_thoughts:
            if t.thought_id == thought_id:
                thought = t
                break
        
        if not thought:
            return False
        
        # Calculate suppression success
        success_chance = effort / (thought.difficulty + 5)
        success = random.random() < success_chance
        
        if success:
            thought.suppressed = True
            thought.suppression_effort = effort
            self.suppressed_thoughts.append(thought)
            self.stats["total_suppressed"] += 1
            
            # Remove from pending if it's there
            if thought in self.pending_thoughts:
                self.pending_thoughts.remove(thought)
            
            logger.debug(f"🤫 Successfully suppressed thought: {thought.content[:30]}...")
            return True
        else:
            # Failed suppression might increase intensity
            thought.intensity = min(10, thought.intensity + 1)
            logger.debug(f" Failed to suppress thought: {thought.content[:30]}...")
            return False
    
    def _decay_suppression(self):
        """Decay suppression efforts over time"""
        for thought in self.suppressed_thoughts:
            thought.suppression_effort = int(thought.suppression_effort * self.suppression_decay)
            
            # If suppression effort is too low, thought might resurface
            if thought.suppression_effort < 2 and random.random() < 0.1:
                thought.suppressed = False
                thought.intensity = max(1, thought.intensity - 1)  # Slightly weaker
                self.pending_thoughts.append(thought)
                self.suppressed_thoughts.remove(thought)
                logger.debug(f" Thought resurfaced: {thought.content[:30]}...")
    
    def _update_statistics(self):
        """Update system statistics"""
        if self.processed_thoughts:
            total_intensity = sum(t.intensity for t in self.processed_thoughts)
            total_difficulty = sum(t.difficulty for t in self.processed_thoughts)
            count = len(self.processed_thoughts)
            
            self.stats["average_intensity"] = total_intensity / count
            self.stats["average_difficulty"] = total_difficulty / count
            
            # Most common type
            type_counts = {}
            for thought in self.processed_thoughts:
                type_counts[thought.thought_type] = type_counts.get(thought.thought_type, 0) + 1
            
            if type_counts:
                self.stats["most_common_type"] = max(type_counts, key=type_counts.get).value
    
    def get_disruption_level(self) -> float:
        """Get current overall disruption level from pending thoughts"""
        if not self.pending_thoughts:
            return 0.0
        
        total_disruption = sum(t.calculate_disruption_score() for t in self.pending_thoughts)
        return min(1.0, total_disruption / len(self.pending_thoughts))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get intrusive thoughts system statistics"""
        stats = self.stats.copy()
        stats.update({
            "pending_thoughts": len(self.pending_thoughts),
            "processed_thoughts": len(self.processed_thoughts),
            "suppressed_thoughts": len(self.suppressed_thoughts),
            "current_disruption": self.get_disruption_level(),
            "is_running": self.is_running
        })
        return stats
    
    def get_thought_summary(self) -> Dict[str, Any]:
        """Get a summary of recent thoughts"""
        recent_thoughts = self.processed_thoughts[-10:]
        
        summary = {
            "recent_count": len(recent_thoughts),
            "high_intensity_count": sum(1 for t in recent_thoughts if t.intensity > 7),
            "types_distribution": {},
            "average_disruption": 0.0,
            "suppression_rate": 0.0
        }
        
        if recent_thoughts:
            # Type distribution
            for thought in recent_thoughts:
                thought_type = thought.thought_type.value
                summary["types_distribution"][thought_type] = summary["types_distribution"].get(thought_type, 0) + 1
            
            # Average disruption
            total_disruption = sum(t.calculate_disruption_score() for t in recent_thoughts)
            summary["average_disruption"] = total_disruption / len(recent_thoughts)
            
            # Suppression rate
            suppressed_count = sum(1 for t in recent_thoughts if t.suppressed)
            summary["suppression_rate"] = suppressed_count / len(recent_thoughts)
        
        return summary


# Helper function for testing
async def test_intrusive_thoughts_system():
    """Test the intrusive thoughts system"""
    system = IntrusiveThoughtsSystem(spontaneous_rate=0.5, max_pending=5)
    
    print("🌀 Testing Intrusive Thoughts System...")
    await system.start()
    
    # Let it generate some thoughts
    await asyncio.sleep(3)
    
    # Add some external thoughts
    system.add_thought("Why am I thinking about purple elephants?", intensity=8, difficulty=6)
    system.add_thought("Did I lock the door?", intensity=5, difficulty=3, thought_type=ThoughtType.WORRY)
    system.add_thought("What if gravity worked sideways?", intensity=9, difficulty=7, thought_type=ThoughtType.ABSURD)
    
    await asyncio.sleep(1)
    
    # Get pending thoughts
    thoughts = await system.get_pending_thoughts()
    print(f" Retrieved {len(thoughts)} thoughts:")
    for thought in thoughts:
        print(f"   - {thought.content} (intensity: {thought.intensity}, difficulty: {thought.difficulty})")
    
    # Try to suppress a high-intensity thought
    if thoughts:
        high_intensity_thoughts = [t for t in thoughts if t.intensity > 7]
        if high_intensity_thoughts:
            thought = high_intensity_thoughts[0]
            success = system.suppress_thought(thought.thought_id, effort=8)
            print(f"🤫 Suppression attempt on '{thought.content[:30]}...': {'Success' if success else 'Failed'}")
    
    # Get statistics
    stats = system.get_stats()
    print(f" System stats: {stats}")
    
    summary = system.get_thought_summary()
    print(f"📋 Thought summary: {summary}")
    
    await system.stop()
    print(" Intrusive Thoughts System test completed")


if __name__ == "__main__":
    asyncio.run(test_intrusive_thoughts_system())
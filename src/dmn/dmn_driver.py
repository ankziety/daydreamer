"""
DMN Driver - Central coordination and timing management for Default Mode Network

The Driver manages three distinct cognitive modes and coordinates transitions
based on exhaustion signals, working memory load, and consensus from other components.
"""

import asyncio
import logging
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import random

logger = logging.getLogger(__name__)


class SystemMode(Enum):
    """Three cognitive modes of the DMN system"""
    ACTIVE = "active"          # Full reasoning, chain-of-thought ON, memory read/write
    PARTIAL_WAKE = "partial_wake"  # Brain break mode, creative associations
    DEFAULT = "default"        # Sleep mode, memory consolidation only


@dataclass
class DMNContext:
    """Context information passed between DMN components"""
    mode: SystemMode
    chunks: List[str] = field(default_factory=list)
    hypothesis: str = ""
    critic_review: str = ""
    grant_proposal: str = ""
    working_memory_load: float = 0.0
    exhaustion_signals: List[str] = field(default_factory=list)
    intrusive_thoughts: List[str] = field(default_factory=list)
    recent_thoughts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    cycle_count: int = 0
    last_break: Optional[datetime] = None


class DMNDriver:
    """
    Central coordination component for the Default Mode Network.
    
    Responsibilities:
    - Orchestrate agent interactions across three modes
    - Manage mode transitions based on exhaustion signals and consensus
    - Handle priority queuing for thoughts and tasks
    - Coordinate timing for brain breaks and synthesis cycles
    - Monitor working-memory load and exhaustion signals
    - Send appropriate context based on current mode
    """
    
    def __init__(self, 
                 active_cycle_limit: int = 10,
                 break_duration: float = 30.0,
                 consolidation_interval: float = 300.0,  # 5 minutes
                 max_working_memory: int = 20):
        """
        Initialize the DMN Driver.
        
        Args:
            active_cycle_limit: Max cycles before forced break
            break_duration: Duration of brain breaks in seconds
            consolidation_interval: Time between consolidation cycles
            max_working_memory: Maximum working memory items
        """
        self.active_cycle_limit = active_cycle_limit
        self.break_duration = break_duration
        self.consolidation_interval = consolidation_interval
        self.max_working_memory = max_working_memory
        
        # Current state
        self.context = DMNContext(mode=SystemMode.ACTIVE)
        self.is_running = False
        self.driver_task: Optional[asyncio.Task] = None
        
        # Components (will be injected)
        self.components: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {
            "mode_change": [],
            "exhaustion_detected": [],
            "intrusive_thought": [],
            "synthesis_complete": []
        }
        
        # Statistics
        self.stats = {
            "total_cycles": 0,
            "active_cycles": 0,
            "break_cycles": 0,
            "consolidation_cycles": 0,
            "mode_transitions": 0,
            "exhaustion_events": 0,
            "intrusive_thoughts_processed": 0,
            "start_time": None,
            "uptime_seconds": 0
        }
        
    def register_component(self, name: str, component: Any):
        """Register a DMN component with the driver"""
        self.components[name] = component
        logger.info(f"Registered DMN component: {name}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered event handler for {event_type}")
    
    async def start(self):
        """Start the DMN driver main loop"""
        if self.is_running:
            logger.warning("DMN Driver is already running")
            return
        
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        self.context.timestamp = datetime.now()
        
        logger.info("🧠 Starting Default Mode Network Driver")
        
        # Start the main DMN loop
        self.driver_task = asyncio.create_task(self._dmn_main_loop())
    
    async def stop(self):
        """Stop the DMN driver"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.driver_task:
            self.driver_task.cancel()
            try:
                await self.driver_task
            except asyncio.CancelledError:
                pass
        
        # Update uptime
        if self.stats["start_time"]:
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
            self.stats["uptime_seconds"] = uptime
        
        logger.info("🛑 Stopped Default Mode Network Driver")
    
    async def _dmn_main_loop(self):
        """Main DMN coordination loop"""
        while self.is_running:
            try:
                self.stats["total_cycles"] += 1
                self.context.cycle_count += 1
                self.context.timestamp = datetime.now()
                
                # Check for mode transitions
                await self._check_mode_transitions()
                
                # Execute current mode
                if self.context.mode == SystemMode.ACTIVE:
                    await self._execute_active_mode()
                    self.stats["active_cycles"] += 1
                    
                elif self.context.mode == SystemMode.PARTIAL_WAKE:
                    await self._execute_partial_wake_mode()
                    self.stats["break_cycles"] += 1
                    
                elif self.context.mode == SystemMode.DEFAULT:
                    await self._execute_default_mode()
                    self.stats["consolidation_cycles"] += 1
                
                # Process any intrusive thoughts
                await self._process_intrusive_thoughts()
                
                # Update working memory load
                self._update_working_memory_load()
                
                # Sleep briefly between cycles
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DMN main loop: {e}")
                await asyncio.sleep(1)
    
    async def _check_mode_transitions(self):
        """Check if mode transitions are needed"""
        current_mode = self.context.mode
        new_mode = current_mode
        
        # Check for exhaustion signals (ACTIVE -> PARTIAL_WAKE)
        if (current_mode == SystemMode.ACTIVE and 
            (self.context.cycle_count % self.active_cycle_limit == 0 or
             len(self.context.exhaustion_signals) > 3 or
             self.context.working_memory_load > 0.8)):
            
            new_mode = SystemMode.PARTIAL_WAKE
            self.context.last_break = datetime.now()
            self.stats["exhaustion_events"] += 1
            await self._trigger_event("exhaustion_detected", self.context)
        
        # Check for break completion (PARTIAL_WAKE -> ACTIVE)
        elif (current_mode == SystemMode.PARTIAL_WAKE and
              self.context.last_break and
              (datetime.now() - self.context.last_break).total_seconds() > self.break_duration):
            
            new_mode = SystemMode.ACTIVE
            self.context.exhaustion_signals.clear()  # Reset exhaustion
        
        # Check for consolidation time (ACTIVE/PARTIAL_WAKE -> DEFAULT)
        elif (current_mode in [SystemMode.ACTIVE, SystemMode.PARTIAL_WAKE] and
              self.stats["start_time"] and
              (datetime.now() - self.stats["start_time"]).total_seconds() % self.consolidation_interval < 5):
            
            new_mode = SystemMode.DEFAULT
        
        # Check for consolidation completion (DEFAULT -> ACTIVE)
        elif (current_mode == SystemMode.DEFAULT and
              self.context.cycle_count % 10 == 0):  # Simple consolidation completion
            
            new_mode = SystemMode.ACTIVE
        
        # Perform transition if needed
        if new_mode != current_mode:
            await self._transition_mode(new_mode)
    
    async def _transition_mode(self, new_mode: SystemMode):
        """Transition to a new system mode"""
        old_mode = self.context.mode
        self.context.mode = new_mode
        self.stats["mode_transitions"] += 1
        
        logger.info(f"🔄 DMN Mode transition: {old_mode.value} → {new_mode.value}")
        
        # Mode-specific transition logic
        if new_mode == SystemMode.PARTIAL_WAKE:
            self.context.chunks.clear()  # Clear working context for break
            
        elif new_mode == SystemMode.ACTIVE:
            # Refresh context from memory
            if "memory_curator" in self.components:
                await self._refresh_context_from_memory()
        
        elif new_mode == SystemMode.DEFAULT:
            # Prepare for consolidation
            self.context.recent_thoughts = self.context.chunks.copy()
        
        await self._trigger_event("mode_change", {"old_mode": old_mode, "new_mode": new_mode})
    
    async def _execute_active_mode(self):
        """Execute ACTIVE mode operations"""
        # Full reasoning with chain-of-thought enabled
        logger.debug("🔥 Executing ACTIVE mode")
        
        # Retrieve relevant memory chunks
        if "memory_curator" in self.components:
            chunks = await self.components["memory_curator"].retrieve_chunks(
                context=self.context,
                mode=SystemMode.ACTIVE
            )
            self.context.chunks = chunks[:self.max_working_memory]
        
        # Generate new thoughts with synthesizer
        if "synthesizer" in self.components:
            synthesis = await self.components["synthesizer"].generate_thoughts(
                context=self.context,
                chain_of_thought=True
            )
            if synthesis:
                self.context.hypothesis = synthesis.output_insight
                self.context.chunks.append(synthesis.output_insight)
        
        # Evaluate thoughts with critic
        if "critic" in self.components:
            review = await self.components["critic"].evaluate_thoughts(self.context)
            self.context.critic_review = review
        
        # Check for new exhaustion signals
        await self._detect_exhaustion()
    
    async def _execute_partial_wake_mode(self):
        """Execute PARTIAL_WAKE mode operations (brain break)"""
        logger.debug("🌙 Executing PARTIAL_WAKE mode (brain break)")
        
        # Creative free-association with brain break manager
        if "brain_break_manager" in self.components:
            break_activities = await self.components["brain_break_manager"].generate_break_activities(
                context=self.context
            )
            
            # Generate shallow, rapid ideas for mood shifting
            if "synthesizer" in self.components:
                creative_synthesis = await self.components["synthesizer"].generate_thoughts(
                    context=self.context,
                    chain_of_thought=True,  # Still enabled in partial wake
                    creativity_boost=True
                )
                if creative_synthesis:
                    self.context.chunks.append(creative_synthesis.output_insight)
        
        # Allow internet browsing if available
        if "browser" in self.components:
            await self.components["browser"].virtual_walk(self.context)
    
    async def _execute_default_mode(self):
        """Execute DEFAULT mode operations (memory consolidation)"""
        logger.debug("💤 Executing DEFAULT mode (memory consolidation)")
        
        # Memory consolidation only - no new thought generation
        if "memory_curator" in self.components:
            await self.components["memory_curator"].consolidate_memories(
                recent_thoughts=self.context.recent_thoughts,
                context=self.context
            )
        
        # Chain-of-thought disabled, no memory writes to working memory
        # This is a rest period for the system
    
    async def _process_intrusive_thoughts(self):
        """Process any intrusive thoughts that have emerged"""
        if "intrusive_thoughts" in self.components:
            intrusive_thoughts = await self.components["intrusive_thoughts"].get_pending_thoughts()
            
            for thought in intrusive_thoughts:
                self.context.intrusive_thoughts.append(thought.content)
                self.stats["intrusive_thoughts_processed"] += 1
                
                # High-intensity thoughts might cause mode changes
                if thought.intensity > 7:
                    self.context.exhaustion_signals.append(f"high_intensity_intrusion_{thought.intensity}")
                
                await self._trigger_event("intrusive_thought", thought)
    
    def _update_working_memory_load(self):
        """Update working memory load metric"""
        current_load = len(self.context.chunks) / self.max_working_memory
        self.context.working_memory_load = min(1.0, current_load)
        
        # Add exhaustion signals if overloaded
        if self.context.working_memory_load > 0.9:
            self.context.exhaustion_signals.append("working_memory_overload")
    
    async def _detect_exhaustion(self):
        """Detect exhaustion signals in active mode"""
        exhaustion_factors = []
        
        # Repetitive thoughts
        if len(self.context.chunks) > 5:
            recent_chunks = self.context.chunks[-5:]
            if len(set(recent_chunks)) < 3:  # Too much repetition
                exhaustion_factors.append("repetitive_thoughts")
        
        # Long active periods
        if self.context.cycle_count % self.active_cycle_limit == 0:
            exhaustion_factors.append("active_cycle_limit_reached")
        
        # High cognitive load
        if self.context.working_memory_load > 0.8:
            exhaustion_factors.append("high_cognitive_load")
        
        # Random exhaustion (simulate natural fatigue)
        if random.random() < 0.05:  # 5% chance per cycle
            exhaustion_factors.append("natural_fatigue")
        
        self.context.exhaustion_signals.extend(exhaustion_factors)
    
    async def _refresh_context_from_memory(self):
        """Refresh context from long-term memory when returning to active mode"""
        if "memory_curator" in self.components:
            relevant_memories = await self.components["memory_curator"].retrieve_chunks(
                context=self.context,
                mode=SystemMode.ACTIVE,
                refresh=True
            )
            self.context.chunks = relevant_memories[:self.max_working_memory // 2]
    
    async def _trigger_event(self, event_type: str, data: Any):
        """Trigger event handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    def add_intrusive_thought(self, content: str, intensity: int = 5, difficulty: int = 3):
        """Add an intrusive thought to be processed"""
        if "intrusive_thoughts" in self.components:
            self.components["intrusive_thoughts"].add_thought(content, intensity, difficulty)
    
    def get_current_context(self) -> DMNContext:
        """Get the current DMN context"""
        return self.context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get DMN driver statistics"""
        stats = self.stats.copy()
        if self.stats["start_time"]:
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
            stats["uptime_seconds"] = uptime
        
        stats.update({
            "current_mode": self.context.mode.value,
            "cycle_count": self.context.cycle_count,
            "working_memory_load": self.context.working_memory_load,
            "exhaustion_signals_count": len(self.context.exhaustion_signals),
            "intrusive_thoughts_count": len(self.context.intrusive_thoughts),
            "working_memory_items": len(self.context.chunks)
        })
        
        return stats


# Helper function for testing
async def test_dmn_driver():
    """Test the DMN driver functionality"""
    driver = DMNDriver(active_cycle_limit=5, break_duration=10.0)
    
    # Mock components
    class MockComponent:
        async def retrieve_chunks(self, context, mode, refresh=False):
            return [f"memory_chunk_{i}" for i in range(3)]
        
        async def generate_thoughts(self, context, chain_of_thought=True, creativity_boost=False):
            from types import SimpleNamespace
            return SimpleNamespace(output_insight="Generated thought")
        
        async def evaluate_thoughts(self, context):
            return "Thoughts are coherent"
        
        async def generate_break_activities(self, context):
            return ["virtual_walk", "free_association"]
        
        async def consolidate_memories(self, recent_thoughts, context):
            logger.info("Consolidating memories...")
        
        async def get_pending_thoughts(self):
            return []
        
        async def virtual_walk(self, context):
            logger.info("Taking virtual walk...")
    
    mock = MockComponent()
    driver.register_component("memory_curator", mock)
    driver.register_component("synthesizer", mock)
    driver.register_component("critic", mock)
    driver.register_component("brain_break_manager", mock)
    driver.register_component("intrusive_thoughts", mock)
    driver.register_component("browser", mock)
    
    print("🧠 Testing DMN Driver...")
    await driver.start()
    
    # Let it run for a bit
    await asyncio.sleep(3)
    
    # Add some intrusive thoughts
    driver.add_intrusive_thought("What if I was a butterfly?", intensity=6)
    driver.add_intrusive_thought("Why is the sky blue?", intensity=4)
    
    await asyncio.sleep(2)
    
    stats = driver.get_stats()
    print(f"📊 DMN Stats after test: {stats}")
    
    await driver.stop()
    print("✅ DMN Driver test completed")


if __name__ == "__main__":
    asyncio.run(test_dmn_driver())
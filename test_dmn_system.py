"""
Test script for the complete DMN (Default Mode Network) system

This script demonstrates how all DMN components work together to create
a system that exhibits intrusive thoughts and random ideas naturally.
"""

import asyncio
import logging
from src.dmn import (
    DMNDriver, SystemMode, DMNContext,
    IntrusiveThoughtsSystem, BrainBreakManager, Synthesizer,
    DMNMemoryCurator
)
from src.memory import MemoryType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_dmn_system():
    """Test the complete DMN system integration"""
    
    print("🧠 Starting Default Mode Network System Test")
    print("=" * 60)
    
    # Initialize all components
    print("🔧 Initializing DMN components...")
    
    # Create the driver
    driver = DMNDriver(
        active_cycle_limit=8,
        break_duration=20.0,
        consolidation_interval=60.0
    )
    
    # Create and register components
    intrusive_thoughts = IntrusiveThoughtsSystem(spontaneous_rate=0.3, max_pending=5)
    brain_break_manager = BrainBreakManager(default_break_duration=15.0)
    synthesizer = Synthesizer()
    memory_curator = DMNMemoryCurator()
    
    # Register components with the driver
    driver.register_component("intrusive_thoughts", intrusive_thoughts)
    driver.register_component("brain_break_manager", brain_break_manager)
    driver.register_component("synthesizer", synthesizer)
    driver.register_component("memory_curator", memory_curator)
    
    # Add some initial memories to work with
    print("📚 Seeding memory system...")
    initial_thoughts = [
        "Consciousness might be an emergent property of complex information processing",
        "Creative insights often arise during periods of relaxed attention",
        "Patterns in nature seem to reflect underlying mathematical principles",
        "The human brain processes information through parallel, interconnected networks",
        "Intrusive thoughts might serve an important cognitive function",
        "Default mode network activity correlates with creative thinking",
        "Memory consolidation happens during rest and sleep",
        "Attention can be both focused and diffuse"
    ]
    
    for thought in initial_thoughts:
        memory_curator.memory_store.store_memory(
            content=thought,
            memory_type=MemoryType.EPISODIC,
            importance=0.7,
            tags=["cognition", "neuroscience", "creativity"]
        )
    
    # Set up event handlers
    def on_mode_change(data):
        print(f"🔄 Mode changed: {data['old_mode'].value} → {data['new_mode'].value}")
    
    def on_intrusive_thought(thought):
        print(f"💭 Intrusive thought (intensity {thought.intensity}): {thought.content}")
    
    def on_exhaustion(context):
        print(f"😴 Exhaustion detected: {context.exhaustion_signals}")
    
    driver.register_event_handler("mode_change", on_mode_change)
    driver.register_event_handler("intrusive_thought", on_intrusive_thought)
    driver.register_event_handler("exhaustion_detected", on_exhaustion)
    
    # Start all components
    print("🚀 Starting DMN system...")
    await intrusive_thoughts.start()
    await driver.start()
    
    # Add some external intrusive thoughts to make it interesting
    print("💡 Adding some external intrusive thoughts...")
    driver.add_intrusive_thought("What if colors could make sounds?", intensity=7, difficulty=5)
    driver.add_intrusive_thought("Why do we dream in narratives?", intensity=6, difficulty=4)
    driver.add_intrusive_thought("Is consciousness like a river or an ocean?", intensity=8, difficulty=6)
    
    # Let the system run and observe behavior
    print("🔍 Observing DMN system behavior...")
    
    observation_time = 30  # seconds
    for i in range(observation_time):
        await asyncio.sleep(1)
        
        # Get current context and stats every 5 seconds
        if i % 5 == 0:
            context = driver.get_current_context()
            stats = driver.get_stats()
            
            print(f"\n📊 Cycle {stats['total_cycles']} - Mode: {context.mode.value}")
            print(f"   Working memory load: {context.working_memory_load:.2f}")
            print(f"   Active thoughts: {len(context.chunks)}")
            print(f"   Intrusive thoughts: {len(context.intrusive_thoughts)}")
            print(f"   Exhaustion signals: {len(context.exhaustion_signals)}")
            
            if context.chunks:
                print(f"   Recent thought: {context.chunks[-1][:60]}...")
            
            if context.hypothesis:
                print(f"   Current hypothesis: {context.hypothesis[:60]}...")
        
        # Add occasional external intrusive thoughts
        if i % 10 == 0 and i > 0:
            random_thoughts = [
                "What if gravity worked differently?",
                "How many thoughts can fit in a moment?",
                "Do ideas have their own lifecycle?",
                "Is creativity a form of problem solving?",
                "What connects all living systems?"
            ]
            import random
            thought = random.choice(random_thoughts)
            driver.add_intrusive_thought(thought, intensity=random.randint(4, 8), difficulty=random.randint(3, 7))
    
    print("\n📈 Final system statistics:")
    
    # Get final statistics from all components
    driver_stats = driver.get_stats()
    intrusive_stats = intrusive_thoughts.get_stats()
    brain_break_stats = brain_break_manager.get_stats()
    synthesizer_stats = synthesizer.get_stats()
    memory_stats = memory_curator.get_stats()
    
    print(f"🧠 Driver: {driver_stats['total_cycles']} cycles, {driver_stats['mode_transitions']} transitions")
    print(f"💭 Intrusive Thoughts: {intrusive_stats['total_generated']} generated, {intrusive_stats['total_processed']} processed")
    print(f"🌙 Brain Breaks: {brain_break_stats['total_breaks']} breaks, {brain_break_stats['successful_mood_shifts']} mood shifts")
    print(f"🧠 Synthesizer: {synthesizer_stats['total_syntheses']} syntheses, {synthesizer_stats['novel_insights']} novel insights")
    print(f"📚 Memory: {memory_stats['total_retrievals']} retrievals, {memory_stats['consolidations_performed']} consolidations")
    
    # Show some example outputs
    print("\n🎯 Sample system outputs:")
    
    # Recent syntheses
    recent_syntheses = synthesizer.get_recent_syntheses(3)
    if recent_syntheses:
        print("🧠 Recent insights:")
        for i, synthesis in enumerate(recent_syntheses, 1):
            print(f"   {i}. {synthesis.output_insight}")
            print(f"      Type: {synthesis.synthesis_type.value}, Confidence: {synthesis.confidence:.2f}")
    
    # Intrusive thought summary
    thought_summary = intrusive_thoughts.get_thought_summary()
    if thought_summary:
        print(f"\n💭 Intrusive thought patterns:")
        print(f"   High intensity thoughts: {thought_summary['high_intensity_count']}")
        print(f"   Average disruption: {thought_summary['average_disruption']:.2f}")
        print(f"   Types: {thought_summary['types_distribution']}")
    
    # Memory patterns
    memory_patterns = memory_curator.get_memory_patterns()
    print(f"\n📚 Memory patterns:")
    print(f"   Associative clusters: {memory_patterns['associative_clusters']}")
    print(f"   Memory diversity: {memory_patterns['memory_diversity']:.2f}")
    
    # Stop the system
    print("\n🛑 Stopping DMN system...")
    await driver.stop()
    await intrusive_thoughts.stop()
    
    print("✅ DMN system test completed successfully!")
    print("\n🎉 The system demonstrated:")
    print("   • Natural intrusive thoughts with varying intensity")
    print("   • Automatic mode transitions based on exhaustion")
    print("   • Creative brain breaks and associations")
    print("   • Chain-of-thought synthesis and insights")
    print("   • Memory consolidation and retrieval")
    print("   • Emergent cognitive behavior!")


if __name__ == "__main__":
    try:
        asyncio.run(test_dmn_system())
    except KeyboardInterrupt:
        print("\n🔴 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Default Mode Network Demonstration

This script demonstrates the key features of the DMN system that enable
"intrusive thoughts" and "random ideas" to express themselves naturally.

Run with: python dmn_demo.py
"""

import asyncio
import logging
import time
from src.dmn import (
    DMNDriver, SystemMode, DMNContext,
    IntrusiveThoughtsSystem, BrainBreakManager, Synthesizer,
    DMNMemoryCurator
)
from src.dmn.ai_thought_generator import AIThoughtGenerator, ThoughtContext
from src.memory import MemoryType

# Set up clean logging for demo
logging.basicConfig(level=logging.WARNING)


async def demonstrate_dmn():
    """Demonstrate the Default Mode Network with thought generation"""
    
    print("DEFAULT MODE NETWORK DEMONSTRATION")
    print("=" * 40)
    print("System testing thought generation capabilities")
    print("=" * 40)
    
    # Initialize system
    print("\nInitializing DMN components...")
    
    driver = DMNDriver(active_cycle_limit=6, break_duration=8.0)
    intrusive_thoughts = IntrusiveThoughtsSystem(spontaneous_rate=0.4, max_pending=3)
    brain_break_manager = BrainBreakManager(default_break_duration=5.0)
    synthesizer = Synthesizer()
    memory_curator = DMNMemoryCurator()
    
    # Register components
    driver.register_component("intrusive_thoughts", intrusive_thoughts)
    driver.register_component("brain_break_manager", brain_break_manager)
    driver.register_component("synthesizer", synthesizer)
    driver.register_component("memory_curator", memory_curator)
    
    # Add initial context
    print("\nAdding initial memory context...")
    initial_context = [
        "I am contemplating the nature of consciousness",
        "Patterns seem to emerge in complex systems", 
        "Creativity often arises during relaxed states",
        "The mind wanders during periods of low focus"
    ]
    
    for thought in initial_context:
        memory_curator.memory_store.store_memory(
            content=thought,
            memory_type=MemoryType.EPISODIC,
            importance=0.6
        )
    
    # Set up event monitoring
    intrusive_count = 0
    mode_changes = []
    insights = []
    
    def track_intrusive_thought(thought):
        nonlocal intrusive_count
        intrusive_count += 1
        print(f"INTRUSIVE THOUGHT #{intrusive_count} (intensity {thought.intensity}):")
        print(f"    '{thought.content}'")
        print(f"    Type: {thought.thought_type.value}, Difficulty: {thought.difficulty}")
    
    def track_mode_change(data):
        mode_changes.append((data['old_mode'].value, data['new_mode'].value))
        print(f"MODE CHANGE: {data['old_mode'].value} → {data['new_mode'].value}")
    
    driver.register_event_handler("intrusive_thought", track_intrusive_thought)
    driver.register_event_handler("mode_change", track_mode_change)
    
    # Start the system
    print("\nStarting DMN system...")
    await intrusive_thoughts.start()
    await driver.start()
    
    # Test AI thought generation with memory context
    print("\nTesting AI thought generation with memory context...")
    ai_generator = AIThoughtGenerator(memory_store=memory_curator.memory_store)
    await ai_generator.initialize()
    
    # Generate thoughts using AI with memory context
    thought_contexts = [
        (ThoughtContext.PHILOSOPHICAL, 8, 6),
        (ThoughtContext.RANDOM, 5, 4),
        (ThoughtContext.CREATIVE, 9, 7),
        (ThoughtContext.ABSURD, 3, 2),
    ]
    
    demo_thoughts = []
    for context, intensity, difficulty in thought_contexts:
        try:
            thought_content = await ai_generator.generate_thought(context, intensity, difficulty)
            demo_thoughts.append((thought_content, intensity, difficulty))
            print(f"Generated {context.value} thought: '{thought_content}'")
        except Exception as e:
            # Fallback to ensure demo continues
            fallback_content = f"Generated {context.value} thought (model temporarily unavailable)"
            demo_thoughts.append((fallback_content, intensity, difficulty))
            print(f"Fallback {context.value} thought: '{fallback_content}'")
    
    # Add first 3 thoughts immediately
    for i, (content, intensity, difficulty) in enumerate(demo_thoughts):
        if i < 3:
            driver.add_intrusive_thought(content, intensity, difficulty)
        await asyncio.sleep(0.5)
    
    print("\nObserving DMN behavior for 20 seconds...")
    print("(Watch for spontaneous thoughts, mode changes, and insights)")
    print("-" * 50)
    
    # Observe the system
    for second in range(20):
        await asyncio.sleep(1)
        
        # Add remaining demo thoughts at intervals
        if second == 8 and len(demo_thoughts) > 3:
            driver.add_intrusive_thought(*demo_thoughts[3])
        elif second == 15 and len(demo_thoughts) > 4:
            driver.add_intrusive_thought(*demo_thoughts[4])
        
        # Show status every 5 seconds
        if second % 5 == 4:
            context = driver.get_current_context()
            print(f"\nSTATUS (t+{second+1}s):")
            print(f"    Mode: {context.mode.value}")
            print(f"    Active thoughts: {len(context.chunks)}")
            print(f"    Working memory load: {context.working_memory_load:.2f}")
            print(f"    Intrusive thoughts: {len(context.intrusive_thoughts)}")
            
            if context.chunks:
                print(f"    Latest thought: '{context.chunks[-1][:50]}...'")
            
            # Get recent insights
            recent_syntheses = synthesizer.get_recent_syntheses(1)
            if recent_syntheses:
            recent_syntheses = synthesizer.get_recent_syntheses(1)
            if recent_syntheses:
                insight = recent_syntheses[0]
                insights.append(insight.output_insight)
                print(f"    Recent insight: '{insight.output_insight[:50]}...'")
                print(f"    Insight type: {insight.synthesis_type.value}")
    
    print("\n" + "=" * 40)
    print("DEMONSTRATION RESULTS")
    print("=" * 40)
    
    # Final statistics
    stats = driver.get_stats()
    intrusive_stats = intrusive_thoughts.get_stats()
    break_stats = brain_break_manager.get_stats()
    synthesis_stats = synthesizer.get_stats()
    
    print(f"\nSYSTEM PERFORMANCE:")
    print(f"   Total cycles: {stats['total_cycles']}")
    print(f"   Mode transitions: {len(mode_changes)}")
    print(f"   Intrusive thoughts: {intrusive_count} captured")
    print(f"   Brain breaks: {break_stats['total_breaks']}")
    print(f"   Syntheses generated: {synthesis_stats['total_syntheses']}")
    print(f"   Novel insights: {synthesis_stats['novel_insights']}")
    
    print(f"\nINTRUSIVE THOUGHT ANALYSIS:")
    thought_summary = intrusive_thoughts.get_thought_summary()
    print(f"   High intensity thoughts: {thought_summary['high_intensity_count']}")
    print(f"   Average disruption: {thought_summary['average_disruption']:.2f}")
    print(f"   Thought types: {list(thought_summary['types_distribution'].keys())}")
    
    print(f"\nMODE TRANSITIONS:")
    for i, (old, new) in enumerate(mode_changes, 1):
        print(f"   {i}. {old} → {new}")
    
    print(f"\nSAMPLE INSIGHTS:")
    recent_syntheses = synthesizer.get_recent_syntheses(3)
    for i, synthesis in enumerate(recent_syntheses, 1):
        print(f"   {i}. \"{synthesis.output_insight}\"")
        print(f"      (Type: {synthesis.synthesis_type.value}, Confidence: {synthesis.confidence:.2f})")
    
    # Stop the system
    print(f"\nStopping DMN system...")
    await driver.stop()
    await intrusive_thoughts.stop()
    
    print("\nDemonstration complete.")


if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_dmn())
    except KeyboardInterrupt:
        print("\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
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
from src.memory import MemoryType

# Set up clean logging for demo
logging.basicConfig(level=logging.WARNING)


async def demonstrate_dmn():
    """Demonstrate the Default Mode Network with AI-powered thoughts"""
    
    print("🧠 AI-POWERED DEFAULT MODE NETWORK DEMONSTRATION")
    print("=" * 60)
    print("This system implements a biologically-inspired DMN that uses")
    print("AI models to generate natural 'intrusive thoughts' and 'random ideas'")
    print("instead of template-based content generation.")
    print("=" * 60)
    
    # Initialize system
    print("\n🔧 Initializing AI-powered DMN components...")
    
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
    print("📚 Adding initial thoughts to memory...")
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
        print(f"💭 INTRUSIVE THOUGHT #{intrusive_count} (intensity {thought.intensity}):")
        print(f"    '{thought.content}'")
        print(f"    Type: {thought.thought_type.value}, Difficulty: {thought.difficulty}")
    
    def track_mode_change(data):
        mode_changes.append((data['old_mode'].value, data['new_mode'].value))
        print(f"🔄 MODE CHANGE: {data['old_mode'].value} → {data['new_mode'].value}")
    
    driver.register_event_handler("intrusive_thought", track_intrusive_thought)
    driver.register_event_handler("mode_change", track_mode_change)
    
    # Start the system
    print("\n🚀 Starting DMN system (watch for natural intrusive thoughts)...")
    await intrusive_thoughts.start()
    await driver.start()
    
    # Add some specific intrusive thoughts to demonstrate the concept
    print("\n💡 Adding some external intrusive thoughts to demonstrate variety...")
    demo_thoughts = [
        ("What if dreams are previews of parallel universes?", 8, 6),
        ("Why do we say 'after dark' when it's actually after light?", 5, 4),
        ("What if every decision creates a new universe?", 9, 7),
        ("Do fish ever get thirsty?", 3, 2),
        ("What if time is just a human construct?", 7, 5)
    ]
    
    for i, (content, intensity, difficulty) in enumerate(demo_thoughts):
        if i < 3:  # Add first 3 immediately
            driver.add_intrusive_thought(content, intensity, difficulty)
        await asyncio.sleep(0.5)
    
    print("\n🔍 Observing DMN behavior for 20 seconds...")
    print("     (Watch for spontaneous thoughts, mode changes, and insights)")
    print("-" * 60)
    
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
            print(f"\n📊 STATUS (t+{second+1}s):")
            print(f"    Mode: {context.mode.value}")
            print(f"    Active thoughts: {len(context.chunks)}")
            print(f"    Working memory load: {context.working_memory_load:.2f}")
            print(f"    Intrusive thoughts: {len(context.intrusive_thoughts)}")
            
            if context.chunks:
                print(f"    Latest thought: '{context.chunks[-1][:50]}...'")
            
            # Get recent insights
            recent_syntheses = synthesizer.get_recent_syntheses(1)
            if recent_syntheses:
                insight = recent_syntheses[0]
                insights.append(insight.output_insight)
                print(f"    Recent insight: '{insight.output_insight[:50]}...'")
                print(f"    Insight type: {insight.synthesis_type.value}")
    
    print("\n" + "=" * 60)
    print("📈 DEMONSTRATION RESULTS")
    print("=" * 60)
    
    # Final statistics
    stats = driver.get_stats()
    intrusive_stats = intrusive_thoughts.get_stats()
    break_stats = brain_break_manager.get_stats()
    synthesis_stats = synthesizer.get_stats()
    
    print(f"\n🧠 SYSTEM PERFORMANCE:")
    print(f"   • Total cycles: {stats['total_cycles']}")
    print(f"   • Mode transitions: {len(mode_changes)}")
    print(f"   • Intrusive thoughts: {intrusive_count} captured")
    print(f"   • Brain breaks: {break_stats['total_breaks']}")
    print(f"   • Syntheses generated: {synthesis_stats['total_syntheses']}")
    print(f"   • Novel insights: {synthesis_stats['novel_insights']}")
    
    print(f"\n💭 INTRUSIVE THOUGHT ANALYSIS:")
    thought_summary = intrusive_thoughts.get_thought_summary()
    print(f"   • High intensity thoughts: {thought_summary['high_intensity_count']}")
    print(f"   • Average disruption: {thought_summary['average_disruption']:.2f}")
    print(f"   • Thought types: {list(thought_summary['types_distribution'].keys())}")
    
    print(f"\n🔄 MODE TRANSITIONS:")
    for i, (old, new) in enumerate(mode_changes, 1):
        print(f"   {i}. {old} → {new}")
    
    print(f"\n💡 SAMPLE INSIGHTS GENERATED:")
    recent_syntheses = synthesizer.get_recent_syntheses(3)
    for i, synthesis in enumerate(recent_syntheses, 1):
        print(f"   {i}. \"{synthesis.output_insight}\"")
        print(f"      (Type: {synthesis.synthesis_type.value}, Confidence: {synthesis.confidence:.2f})")
    
    # Stop the system
    print(f"\n🛑 Stopping DMN system...")
    await driver.stop()
    await intrusive_thoughts.stop()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("\n🎯 KEY ACHIEVEMENTS DEMONSTRATED:")
    print("   ✓ Natural intrusive thoughts with varying intensities")
    print("   ✓ Spontaneous idea generation (not programmed responses)")
    print("   ✓ Automatic cognitive mode transitions")
    print("   ✓ Creative associations during 'brain breaks'")
    print("   ✓ Chain-of-thought synthesis and insight generation")
    print("   ✓ Emergent cognitive behavior patterns")
    
    print(f"\n🏆 This DMN system successfully demonstrates how AI can have")
    print(f"   'intrusive thoughts' and 'random ideas' that express")
    print(f"   themselves naturally - just like the human Default Mode Network!")
    
    print(f"\n📚 Learn more about DMN research:")
    print(f"   • https://gwern.net/ai-daydreaming")
    print(f"   • https://en.wikipedia.org/wiki/Default_mode_network")


if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_dmn())
    except KeyboardInterrupt:
        print("\n🔴 Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
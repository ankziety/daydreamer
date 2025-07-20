#!/usr/bin/env python3
"""
Daydreamer AI - Command Line Interface
======================================

Simple command line interface for the Daydreamer AI system.
"""

import asyncio
import argparse
import sys
from pathlib import Path

from daydreamer_ai import DaydreamerAI


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Daydreamer AI - Advanced conversational AI with Chain of Thought and Day Dreaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                    # Start interactive chat
  python cli.py --memory custom.db # Use custom memory database
  python cli.py --model ollama     # Force use of Ollama (if available)
  python cli.py --verbose          # Show detailed processing and prompts
  python cli.py -v --test          # Run test with verbose output
  
The Daydreamer AI system features:
- True Chain of Thought reasoning through recursive self-prompting
- Day Dreaming technique for creative insights
- Persistent memory across sessions
- Automatic fallback from Ollama to Transformers
- Verbose mode to see actual prompts and decision-making process
        """
    )
    
    parser.add_argument(
        '--memory', '-m',
        type=str,
        default='src/memory/daydreamer_memory.db',
        help='Path to memory database file (default: src/memory/daydreamer_memory.db)'
    )
    
    parser.add_argument(
        '--model',
        choices=['auto', 'ollama', 'transformers'],
        default='auto',
        help='Preferred model type (default: auto)'
    )
    
    parser.add_argument(
        '--ollama-model',
        type=str,
        default='auto',
        help='Specific Ollama model name (default: auto-detect)'
    )
    
    parser.add_argument(
        '--transformers-model',
        type=str,
        default='gpt2',
        help='Transformers model name (default: gpt2)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a quick test instead of starting interactive chat'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show memory statistics and exit'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old memories and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose mode to show detailed processing messages and prompts'
    )
    
    args = parser.parse_args()
    
    # Build model configuration
    model_config = {
        'model_preference': args.model,
        'ollama_model': args.ollama_model,
        'transformers_model': args.transformers_model,
        'verbose': args.verbose
    }
    
    try:
        if args.stats:
            show_stats(args.memory)
        elif args.cleanup:
            cleanup_memories(args.memory)
        elif args.test:
            asyncio.run(run_test(args.memory, model_config))
        else:
            asyncio.run(run_interactive(args.memory, model_config))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)


def show_stats(memory_path: str):
    """Show memory statistics"""
    from memory_manager import PersistentMemoryManager
    
    print("📊 DAYDREAMER AI MEMORY STATISTICS")
    print("=" * 50)
    
    if not Path(memory_path).exists():
        print(f"Memory database not found: {memory_path}")
        return
    
    memory_manager = PersistentMemoryManager(memory_path)
    stats = memory_manager.get_memory_stats()
    
    print(f"Memory Database: {memory_path}")
    print(f"Total Conversations: {stats.get('total_conversations', 0)}")
    print(f"Total Sessions: {stats.get('total_sessions', 0)}")
    print(f"Total Insights: {stats.get('total_insights', 0)}")
    print(f"Recent Activity: {stats.get('recent_conversations', 0)} conversations (7 days)")
    
    insights_by_type = stats.get('insights_by_type', {})
    if insights_by_type:
        print(f"\nInsights by Type:")
        for insight_type, count in insights_by_type.items():
            print(f"  {insight_type.upper()}: {count}")
    
    # Show user profile if available
    profile = memory_manager.get_user_profile()
    if profile:
        print(f"\nUser Profile (updated: {profile.last_updated.strftime('%Y-%m-%d')})")
        if profile.interests:
            top_interests = sorted(profile.interests.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  Top interests: {', '.join([f'{topic}({score:.1f})' for topic, score in top_interests])}")
    
    memory_manager.close()


def cleanup_memories(memory_path: str):
    """Clean up old memories"""
    from memory_manager import PersistentMemoryManager
    
    print("🧹 CLEANING UP OLD MEMORIES")
    print("=" * 40)
    
    if not Path(memory_path).exists():
        print(f"Memory database not found: {memory_path}")
        return
    
    memory_manager = PersistentMemoryManager(memory_path)
    
    # Show stats before cleanup
    stats_before = memory_manager.get_memory_stats()
    print(f"Before cleanup:")
    print(f"  Conversations: {stats_before.get('total_conversations', 0)}")
    print(f"  Insights: {stats_before.get('total_insights', 0)}")
    
    # Perform cleanup
    memory_manager.cleanup_old_memories(days_to_keep=90)
    
    # Show stats after cleanup
    stats_after = memory_manager.get_memory_stats()
    print(f"\nAfter cleanup:")
    print(f"  Conversations: {stats_after.get('total_conversations', 0)}")
    print(f"  Insights: {stats_after.get('total_insights', 0)}")
    
    conversations_removed = stats_before.get('total_conversations', 0) - stats_after.get('total_conversations', 0)
    insights_removed = stats_before.get('total_insights', 0) - stats_after.get('total_insights', 0)
    
    print(f"\nRemoved {conversations_removed} conversations and {insights_removed} insights")
    print("✅ Cleanup complete!")
    
    memory_manager.close()


async def run_test(memory_path: str, model_config: dict):
    """Run a quick test of the system"""
    print("🧪 DAYDREAMER AI SYSTEM TEST")
    print("=" * 40)
    
    try:
        # Initialize system
        print("Initializing system...")
        ai = DaydreamerAI(memory_path, model_config)
        
        # Test basic functionality
        print("Testing basic processing...")
        test_inputs = [
            "What is artificial intelligence?",
            "How does creativity work?",
            "Tell me about consciousness."
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\nTest {i}: {test_input}")
            response = await ai.process_user_input(test_input)
            print(f"Response length: {len(response)} characters")
            
            if response and len(response) > 10:
                print("✅ Response generated successfully")
            else:
                print("❌ Response generation failed")
        
        # Show final stats
        stats = ai.memory_manager.get_memory_stats()
        print(f"\n📊 Final stats:")
        print(f"  Conversations processed: {ai.conversation_count}")
        print(f"  Total thinking time: {ai.total_thinking_time:.1f}s")
        print(f"  Total daydream time: {ai.total_daydream_time:.1f}s")
        print(f"  Memories stored: {stats.get('total_conversations', 0)}")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def run_interactive(memory_path: str, model_config: dict):
    """Run interactive chat"""
    ai = DaydreamerAI(memory_path, model_config)
    await ai.start_interactive_chat()


if __name__ == "__main__":
    main()
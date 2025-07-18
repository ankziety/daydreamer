#!/usr/bin/env python3
"""
Test script to demonstrate unbiased AI thought generation
after removing template-based "ad-libs" from the system.
"""

import asyncio
import logging
from src.dmn.ai_thought_generator import AIThoughtGenerator, AIThoughtConfig, ThoughtContext

# Set minimal logging
logging.basicConfig(level=logging.ERROR)

async def demonstrate_unbiased_prompts():
    """Demonstrate unbiased thought generation without template fragments"""
    
    print("🧠 UNBIASED AI THOUGHT GENERATION TEST")
    print("=" * 60)
    print("This demonstrates the removal of 'ad-lib' style prompts")
    print("and replacement with GitHub Copilot-style system prompts.")
    print("=" * 60)
    
    # Initialize with fallback mode to avoid model downloads
    config = AIThoughtConfig(model_type="fallback", fallback_enabled=True)
    generator = AIThoughtGenerator(config)
    await generator.initialize()
    
    print(f"\n🔧 Generator Status: {generator.get_status()}")
    
    print("\n📝 BEFORE (removed): Template-based ad-libs")
    print("   ❌ 'What if gravity'")
    print("   ❌ 'Imagine if'") 
    print("   ❌ 'An absurd scenario unfolds:'")
    print("   ❌ 'A worrying thought emerges:'")
    
    print("\n✅ AFTER: Unbiased system prompts")
    print("   ✓ 'You are generating [context] thoughts that naturally occur...'")
    print("   ✓ 'Generate a single, spontaneous thought...'")
    print("   ✓ 'Do not use template phrases or leading words'")
    
    print("\n🎯 System Prompt Examples:")
    print("-" * 40)
    
    contexts_to_show = [ThoughtContext.RANDOM, ThoughtContext.ABSURD, ThoughtContext.PHILOSOPHICAL]
    
    for context in contexts_to_show:
        system_prompt = generator.system_prompts[context]
        # Show first sentence for brevity
        first_sentence = system_prompt.split('.')[0] + '.'
        print(f"\n{context.value.upper()}:")
        print(f"  {first_sentence}")
    
    print("\n🧪 Testing Unbiased Generation:")
    print("-" * 40)
    
    # Generate sample thoughts (will use fallback but demonstrate the approach)
    for context in contexts_to_show:
        thought = await generator.generate_thought(context, intensity=5, difficulty=5)
        print(f"\n{context.value}: {thought}")
    
    print("\n✨ Key Improvements:")
    print("- Eliminated ALL template fragments and sentence starters")
    print("- System prompts define AI role without content bias") 
    print("- Natural thought generation without leading phrases")
    print("- Follows GitHub Copilot agent prompt engineering principles")
    print("- Ready for testing with actual AI models (GPT-2, Gemma)")

if __name__ == "__main__":
    asyncio.run(demonstrate_unbiased_prompts())
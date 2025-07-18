#!/usr/bin/env python3
"""
Simple test script to debug the chat interface
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.dmn.ai_thought_generator import AIThoughtGenerator, ThoughtContext
from src.memory import MemoryStore

async def test_simple_generation():
    """Test simple AI generation"""
    print("🧠 Testing AI generation...")
    
    # Create memory store
    memory_store = MemoryStore(storage_path="test_memory.db", auto_save=True)
    
    # Create AI generator
    ai_generator = AIThoughtGenerator(memory_store=memory_store)
    await ai_generator.initialize()
    
    print(f"AI Generator Status: {ai_generator.get_status()}")
    
    # Test thought generation
    print("Generating test thought...")
    thought = await ai_generator.generate_thought(
        context=ThoughtContext.CREATIVE,
        intensity=5,
        difficulty=3
    )
    
    print(f"Generated thought: {thought}")
    
    # Test conversation-style response
    print("Generating conversation response...")
    response_thought = await ai_generator.generate_thought(
        context=ThoughtContext.PHILOSOPHICAL,
        intensity=4,
        difficulty=2
    )
    
    response = f"That's fascinating! It makes me think: {response_thought}. What's your perspective on this?"
    print(f"Response: {response}")
    
    memory_store.close()
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_simple_generation())
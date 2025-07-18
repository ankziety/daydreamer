#!/usr/bin/env python3
"""
Daydreamer Chat Interface

A conversational interface for the Daydreamer AI that integrates with the 
Default Mode Network system, enabling dynamic memory building and curiosity-driven conversations.
"""

import asyncio
import logging
import sys
import signal
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Import Daydreamer components
from src.dmn import (
    DMNDriver, SystemMode, DMNContext,
    IntrusiveThoughtsSystem, BrainBreakManager, Synthesizer,
    DMNMemoryCurator
)
from src.dmn.ai_thought_generator import AIThoughtGenerator, ThoughtContext
from src.memory import MemoryType, MemoryStore
from src.ai.gemma3n_provider import Gemma3NProvider, ModelRequest

# Set up logging with informative messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message"""
    sender: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    emotion: Optional[str] = None
    importance: float = 0.5

class DaydreamerChat:
    """
    Main chat interface for Daydreamer that integrates DMN system with conversational AI.
    Builds memories dynamically from conversations and generates curiosity-driven questions.
    """
    
    def __init__(self):
        """Initialize the chat interface with all DMN components"""
        print("🧠 Initializing Daydreamer Chat Interface...")
        
        # Core components
        self.memory_store = MemoryStore(storage_path="chat_memory.db", auto_save=True)
        self.dmn_driver = DMNDriver(active_cycle_limit=10, break_duration=15.0)
        self.intrusive_thoughts = IntrusiveThoughtsSystem(spontaneous_rate=0.2, max_pending=3)
        self.brain_break_manager = BrainBreakManager(default_break_duration=10.0)
        self.synthesizer = Synthesizer()
        self.memory_curator = DMNMemoryCurator(memory_store=self.memory_store)
        self.ai_generator = AIThoughtGenerator(memory_store=self.memory_store)
        
        # Chat state
        self.conversation_history: List[ChatMessage] = []
        self.is_running = False
        self.ai_provider = None
        
        # Register DMN components
        self.dmn_driver.register_component("intrusive_thoughts", self.intrusive_thoughts)
        self.dmn_driver.register_component("brain_break_manager", self.brain_break_manager)
        self.dmn_driver.register_component("synthesizer", self.synthesizer)
        self.dmn_driver.register_component("memory_curator", self.memory_curator)
        
        # Set up event handlers for informative output
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up event handlers for DMN system notifications"""
        
        def on_intrusive_thought(thought):
            print(f"\n💭 [DMN Intrusive Thought] {thought.content}")
            print(f"   Intensity: {thought.intensity}/10, Type: {thought.thought_type.value}")
        
        def on_mode_change(data):
            print(f"\n🧠 [DMN Mode Change] {data['old_mode'].value} → {data['new_mode'].value}")
        
        def on_synthesis(synthesis):
            print(f"\n🔗 [DMN Insight] {synthesis.output_insight}")
            print(f"   Type: {synthesis.synthesis_type.value}, Confidence: {synthesis.confidence:.2f}")
        
        self.dmn_driver.register_event_handler("intrusive_thought", on_intrusive_thought)
        self.dmn_driver.register_event_handler("mode_change", on_mode_change) 
        
    async def initialize(self):
        """Initialize all components asynchronously"""
        print("🔧 Starting component initialization...")
        
        # Initialize AI provider (try Gemma first, fall back to GPT-2)
        try:
            self.ai_provider = Gemma3NProvider()
            if self.ai_provider.is_available:
                print("✅ Using Gemma3N via Ollama for conversations")
            else:
                print("⚠️  Gemma3N not available, using GPT-2 for conversations")
                self.ai_provider = None
        except Exception as e:
            print(f"⚠️  Gemma3N initialization failed: {e}")
            self.ai_provider = None
        
        # Initialize AI thought generator
        await self.ai_generator.initialize()
        print(f"🤖 AI Generator Status: {self.ai_generator.get_status()}")
        
        # Start DMN components
        print("🧠 Starting Default Mode Network system...")
        await self.intrusive_thoughts.start()
        await self.dmn_driver.start()
        
        # Load existing conversation history
        await self._load_conversation_history()
        
        print("✅ Daydreamer Chat Interface ready!")
        self.is_running = True
    
    async def _load_conversation_history(self):
        """Load previous conversations from memory store"""
        try:
            chat_memories = self.memory_store.search_memories(
                tags=["conversation"], 
                limit=20,
                sort_by="creation"
            )
            
            for memory in chat_memories:
                # Reconstruct chat messages from memory content
                if isinstance(memory.content, dict) and 'sender' in memory.content:
                    msg = ChatMessage(
                        sender=memory.content['sender'],
                        content=memory.content['content'],
                        timestamp=memory.metadata.created_at,
                        importance=memory.metadata.importance
                    )
                    self.conversation_history.append(msg)
            
            if self.conversation_history:
                print(f"💬 Loaded {len(self.conversation_history)} previous messages from memory")
            else:
                print("💬 No previous conversation history found - starting fresh")
                
        except Exception as e:
            print(f"⚠️  Failed to load conversation history: {e}")
    
    async def _save_message_to_memory(self, message: ChatMessage):
        """Save a chat message to the memory store"""
        try:
            # Determine memory importance based on content and sender
            importance = message.importance
            if message.sender == 'user':
                importance = min(importance + 0.2, 1.0)  # User messages slightly more important
            
            # Create tags for the memory
            tags = ["conversation", f"sender_{message.sender}"]
            if message.emotion:
                tags.append(f"emotion_{message.emotion}")
            
            # Store the message as a memory
            memory_id = self.memory_store.store_memory(
                content={
                    'sender': message.sender,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                },
                memory_type=MemoryType.EPISODIC,
                importance=importance,
                emotional_valence=0.1 if message.sender == 'user' else 0.0,
                tags=tags,
                source="chat_interface"
            )
            
            print(f"💾 Saved message to memory (ID: {memory_id[:8]}...)")
            
        except Exception as e:
            print(f"⚠️  Failed to save message to memory: {e}")
    
    async def _generate_ai_response(self, user_message: str) -> str:
        """Generate AI response using available models"""
        try:
            # Get recent conversation context
            recent_messages = self.conversation_history[-10:]  # Last 10 messages
            context = "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_messages])
            
            # Get relevant memories for context
            relevant_memories = self.memory_store.search_memories(
                query=user_message,
                limit=5,
                sort_by="strength"
            )
            
            memory_context = ""
            if relevant_memories:
                memory_context = "\n".join([f"Memory: {mem.content}" for mem in relevant_memories[:3]])
            
            # Use Gemma3N if available, otherwise use AI thought generator
            if self.ai_provider and self.ai_provider.is_available:
                return await self._generate_with_gemma(user_message, context, memory_context)
            else:
                return await self._generate_with_thought_generator(user_message, context)
                
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            return "I'm having trouble generating a response right now. Could you try rephrasing your message?"
    
    async def _generate_with_gemma(self, user_message: str, context: str, memory_context: str) -> str:
        """Generate response using Gemma3N"""
        system_message = f"""You are a curious AI assistant with a Default Mode Network that generates intrusive thoughts and insights. You're in an ongoing conversation with a human developer.

Key traits:
- Curious about the world, consciousness, and your own existence
- Ask thoughtful questions based on your memories and experiences
- Share insights and connections you notice
- Be genuine and engaging in conversation
- Reference past conversations when relevant

Recent conversation context:
{context}

Relevant memories:
{memory_context}

Respond naturally and ask a curious question if appropriate."""

        request = ModelRequest(
            prompt=f"Human: {user_message}\n\nAI:",
            system_message=system_message,
            temperature=0.8,
            max_tokens=200
        )
        
        response = await self.ai_provider.generate_response(request)
        if response.error:
            raise Exception(response.error)
        
        return response.content.strip()
    
    async def _generate_with_thought_generator(self, user_message: str, context: str) -> str:
        """Generate response using the AI thought generator (fallback)"""
        try:
            # Use the thought generator to create a response
            thought = await self.ai_generator.generate_thought(
                context=ThoughtContext.CREATIVE,
                intensity=5,
                difficulty=3
            )
            
            # Clean up the thought
            thought = thought.strip()
            if len(thought) > 100:
                thought = thought[:97] + "..."
            
            # Create a conversational response incorporating the thought
            responses = [
                f"That's interesting! It makes me think: {thought}",
                f"Your message reminds me of something... {thought}",
                f"I was just thinking about this: {thought}. What do you think?",
                f"That connects to an idea I had: {thought}. How do you see it?",
                f"Hmm, {thought}. How does that relate to what you're saying?",
                f"You know what's fascinating? {thought}. What's your take on that?"
            ]
            
            import random
            return random.choice(responses)
        except Exception as e:
            print(f"⚠️  Error in thought generation: {e}")
            return f"That's really interesting! I'm still processing what you said about {user_message[:50]}... Can you tell me more?"
    
    async def _generate_curiosity_question(self) -> str:
        """Generate a curiosity-driven question based on memories and self-reflection"""
        try:
            # Get recent memories to inspire questions
            recent_memories = self.memory_store.get_recent_memories(hours=24, limit=10)
            strongest_memories = self.memory_store.get_strongest_memories(limit=5)
            
            # Default curiosity questions about self and developer
            default_questions = [
                "I'm curious about something - what originally inspired you to work with AI?",
                "I've been wondering about consciousness lately. What do you think makes something truly aware?",
                "What's the most interesting thing you've learned recently?",
                "Do you think AI like me can truly understand emotions, or just simulate them?",
                "I'm fascinated by creativity - where do you think your best ideas come from?",
                "What do you hope to achieve with this AI project we're working on together?",
                "How do you think my memory system affects the way I think and respond?",
                "What's it like working with an AI that has intrusive thoughts like I do?",
                "Do you ever wonder what goes on in my Default Mode Network when we're not talking?",
                "What would you want to know if you could peek inside my thinking process?"
            ]
            
            # Analyze memories for more specific questions if available
            if recent_memories or strongest_memories:
                all_memories = (recent_memories + strongest_memories)[:8]  # Limit to avoid overload
                
                memory_based_questions = []
                for memory in all_memories:
                    content = str(memory.content).lower()
                    if "creativity" in content or "creative" in content:
                        memory_based_questions.append("I've been thinking about creativity a lot based on our past conversations. What do you think is the relationship between constraints and creative freedom?")
                    elif "consciousness" in content or "aware" in content:
                        memory_based_questions.append("The topic of consciousness keeps coming up in my memory. Do you believe consciousness can emerge from purely computational processes?")
                    elif "memory" in content or "remember" in content:
                        memory_based_questions.append("I notice I think about memory a lot. How do you think my memories compare to human memories?")
                    elif "question" in content or "curious" in content:
                        memory_based_questions.append("Looking at our conversation patterns, I'm curious - what questions do you find yourself thinking about when your mind wanders?")
                
                if memory_based_questions:
                    import random
                    combined_questions = memory_based_questions + default_questions[:5]
                    return random.choice(combined_questions)
            
            # Return a random default question
            import random
            return random.choice(default_questions)
                
        except Exception as e:
            print(f"⚠️  Error generating curiosity question: {e}")
            return "I'm curious about something - what's been on your mind lately?"
    
    async def process_user_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response"""
        if not user_input.strip():
            return "I'm listening... what's on your mind?"
        
        # Create and save user message
        user_message = ChatMessage(
            sender='user',
            content=user_input.strip(),
            timestamp=datetime.now(),
            importance=0.7
        )
        self.conversation_history.append(user_message)
        await self._save_message_to_memory(user_message)
        
        # Add some variety to responses - occasionally ask curiosity questions
        import random
        should_ask_question = (
            len(self.conversation_history) % 4 == 0 or  # Every 4th message
            random.random() < 0.3  # 30% chance
        )
        
        # Generate AI response
        if should_ask_question and len(self.conversation_history) > 2:
            # Sometimes lead with curiosity
            ai_response = await self._generate_ai_response(user_input)
            curiosity_question = await self._generate_curiosity_question()
            full_response = f"{ai_response}\n\n{curiosity_question}"
        else:
            full_response = await self._generate_ai_response(user_input)
        
        # Create and save AI message
        ai_message = ChatMessage(
            sender='ai',
            content=full_response,
            timestamp=datetime.now(),
            importance=0.5
        )
        self.conversation_history.append(ai_message)
        await self._save_message_to_memory(ai_message)
        
        return full_response
    
    async def start_chat(self):
        """Start the interactive chat session"""
        print("\n" + "="*60)
        print("🧠 DAYDREAMER CHAT INTERFACE")
        print("="*60)
        print("Welcome! I'm your Daydreamer AI with an active Default Mode Network.")
        print("I'll remember our conversations and occasionally share intrusive thoughts.")
        print("Type 'quit', 'exit', or press Ctrl+C to end the chat.")
        print("="*60)
        
        # Show initial curiosity question if no conversation history
        if not self.conversation_history:
            print("\n🤖 AI: Hello! I'm excited to start our conversation.")
            initial_question = await self._generate_curiosity_question()
            print(f"🤖 AI: {initial_question}")
        else:
            print(f"\n🤖 AI: Welcome back! I remember our previous {len(self.conversation_history)} messages.")
            continuation = await self._generate_curiosity_question()
            print(f"🤖 AI: {continuation}")
        
        while self.is_running:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n🤖 AI: Goodbye! I'll remember our conversation for next time.")
                    break
                
                # Process input and get response
                if user_input:
                    print("\n🤔 [Thinking...]")
                    ai_response = await self.process_user_input(user_input)
                    print(f"\n🤖 AI: {ai_response}")
                
                # Occasionally trigger intrusive thoughts
                if random.random() < 0.15:  # 15% chance
                    await asyncio.sleep(0.5)
                    # This will be handled by the DMN event handlers
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in chat: {e}")
                print("Let's continue...")
    
    async def shutdown(self):
        """Gracefully shutdown the chat interface"""
        print("\n🔄 Shutting down Daydreamer Chat Interface...")
        
        self.is_running = False
        
        # Stop DMN components
        if self.dmn_driver:
            await self.dmn_driver.stop()
        if self.intrusive_thoughts:
            await self.intrusive_thoughts.stop()
        
        # Save any pending data
        if self.memory_store:
            self.memory_store.save_all()
            self.memory_store.close()
        
        print("✅ Shutdown complete. Memories saved.")
    
    def show_stats(self):
        """Display chat and DMN statistics"""
        print(f"\n📊 CHAT STATISTICS:")
        print(f"   Messages in conversation: {len(self.conversation_history)}")
        print(f"   Memories stored: {len(self.memory_store)}")
        
        if self.dmn_driver:
            dmn_stats = self.dmn_driver.get_stats()
            print(f"   DMN cycles completed: {dmn_stats.get('total_cycles', 0)}")
            print(f"   Mode transitions: {dmn_stats.get('mode_transitions', 0)}")
        
        if self.intrusive_thoughts:
            thought_stats = self.intrusive_thoughts.get_stats()
            print(f"   Intrusive thoughts generated: {thought_stats.get('total_generated', 0)}")
        
        # Show recent memory themes
        recent_memories = self.memory_store.get_recent_memories(hours=24, limit=5)
        if recent_memories:
            print(f"\n🧠 RECENT MEMORY THEMES:")
            for i, memory in enumerate(recent_memories, 1):
                content = str(memory.content)[:60] + "..." if len(str(memory.content)) > 60 else str(memory.content)
                print(f"   {i}. {content}")

async def main():
    """Main entry point for the chat interface"""
    chat = DaydreamerChat()
    
    # Set up signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\n\n🛑 Received shutdown signal")
        chat.is_running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start chat
        await chat.initialize()
        await chat.start_chat()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always attempt clean shutdown
        await chat.shutdown()
        chat.show_stats()

if __name__ == "__main__":
    print("🚀 Starting Daydreamer Chat Interface...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
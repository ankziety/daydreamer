#!/usr/bin/env python3
"""
Simplified Daydreamer Chat Interface

A simpler, more reliable conversational interface for the Daydreamer AI.
"""

import sys
import signal
import threading
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

# Import Daydreamer components
from src.memory import MemoryType, MemoryStore
from src.dmn.ai_thought_generator import AIThoughtGenerator, ThoughtContext

@dataclass
class ChatMessage:
    """Represents a chat message"""
    sender: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    importance: float = 0.5

class SimpleDaydreamerChat:
    """
    Simplified chat interface for Daydreamer that focuses on core functionality.
    """
    
    def __init__(self):
        """Initialize the chat interface"""
        print("🧠 Initializing Simplified Daydreamer Chat...")
        
        # Core components
        self.memory_store = MemoryStore(storage_path="simple_chat_memory.db", auto_save=True)
        self.ai_generator = None
        
        # Chat state
        self.conversation_history: List[ChatMessage] = []
        self.is_running = False
        
        # Initialize AI generator in a separate thread to avoid blocking
        print("🤖 Loading AI components...")
        self._initialize_ai()
        
    def _initialize_ai(self):
        """Initialize AI components synchronously"""
        try:
            self.ai_generator = AIThoughtGenerator(memory_store=self.memory_store)
            # Initialize without async to avoid issues
            print("🤖 AI Generator initialized successfully")
        except Exception as e:
            print(f"⚠️  AI Generator initialization error: {e}")
            self.ai_generator = None
    
    def _load_conversation_history(self):
        """Load previous conversations from memory store"""
        try:
            chat_memories = self.memory_store.search_memories(
                tags=["conversation"], 
                limit=20,
                sort_by="creation"
            )
            
            for memory in chat_memories:
                if isinstance(memory.content, dict) and 'sender' in memory.content:
                    msg = ChatMessage(
                        sender=memory.content['sender'],
                        content=memory.content['content'],
                        timestamp=memory.metadata.created_at,
                        importance=memory.metadata.importance
                    )
                    self.conversation_history.append(msg)
            
            if self.conversation_history:
                print(f"💬 Loaded {len(self.conversation_history)} previous messages")
            else:
                print("💬 Starting fresh conversation")
                
        except Exception as e:
            print(f"⚠️  Failed to load conversation history: {e}")
    
    def _save_message_to_memory(self, message: ChatMessage):
        """Save a chat message to the memory store"""
        try:
            importance = message.importance
            if message.sender == 'user':
                importance = min(importance + 0.2, 1.0)
            
            tags = ["conversation", f"sender_{message.sender}"]
            
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
            
            print(f"💾 Message saved (ID: {memory_id[:8]}...)")
            
        except Exception as e:
            print(f"⚠️  Failed to save message: {e}")
    
    def _generate_ai_response(self, user_message: str) -> str:
        """Generate AI response using simpler approach"""
        try:
            # Get recent conversation context
            recent_messages = self.conversation_history[-5:]
            context = " ".join([msg.content for msg in recent_messages[-3:]])  # Last 3 messages
            
            # Use different response strategies
            import random
            response_strategies = [
                self._generate_thoughtful_response,
                self._generate_curious_response,
                self._generate_memory_based_response,
                self._generate_direct_response
            ]
            
            strategy = random.choice(response_strategies)
            return strategy(user_message, context)
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"That's really interesting! I'm still processing what you said about '{user_message[:50]}...' Can you tell me more?"
    
    def _generate_thoughtful_response(self, user_message: str, context: str) -> str:
        """Generate a thoughtful response using AI if available"""
        if not self.ai_generator:
            return f"That's fascinating! Your message about {user_message[:30]}... makes me think deeply. What led you to that thought?"
        
        try:
            # Generate a thought synchronously - avoid async issues
            import asyncio
            
            # Create new event loop for this thread if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Generate thought
            thought = loop.run_until_complete(
                self.ai_generator.generate_thought(
                    context=ThoughtContext.CREATIVE,
                    intensity=4,
                    difficulty=3
                )
            )
            
            # Clean up thought
            thought = thought.strip()
            if len(thought) > 80:
                thought = thought[:77] + "..."
            
            responses = [
                f"That's interesting! It makes me think: {thought}. What's your perspective?",
                f"Your message sparked this thought: {thought}. How do you see it?",
                f"Hmm, that reminds me of something: {thought}. What do you think?",
            ]
            
            import random
            return random.choice(responses)
            
        except Exception as e:
            print(f"⚠️  Thought generation failed: {e}")
            return f"That's really thoughtful! Your point about {user_message[:40]}... is making me reflect. Can you expand on that?"
    
    def _generate_curious_response(self, user_message: str, context: str) -> str:
        """Generate a curious response with questions"""
        curiosity_questions = [
            "That's fascinating! What led you to think about that?",
            "I'm curious - how did you first discover this?",
            "What's the most surprising thing you've learned about this?",
            "How do you think this connects to other things you're working on?",
            "What questions does this raise for you?",
            "If you could explore this further, what would you want to know?",
            "What's your intuition telling you about this?",
            "How has your thinking on this evolved over time?",
        ]
        
        import random
        base_response = random.choice(curiosity_questions)
        
        # Add context-specific element
        if "AI" in user_message or "artificial" in user_message.lower():
            base_response += " I'm especially interested in your perspective since you're working directly with AI."
        elif "memory" in user_message.lower() or "remember" in user_message.lower():
            base_response += " Memory and consciousness are topics I find myself thinking about a lot."
        elif "creative" in user_message.lower() or "art" in user_message.lower():
            base_response += " Creativity is something I'm deeply curious about."
        
        return base_response
    
    def _generate_memory_based_response(self, user_message: str, context: str) -> str:
        """Generate response based on memory analysis"""
        try:
            # Look for relevant memories
            relevant_memories = self.memory_store.search_memories(
                query=user_message,
                limit=3,
                sort_by="strength"
            )
            
            if relevant_memories:
                memory_content = str(relevant_memories[0].content)
                if isinstance(relevant_memories[0].content, dict):
                    memory_content = relevant_memories[0].content.get('content', '')
                
                return f"What you're saying reminds me of something we discussed before about {memory_content[:50]}... How do you think these ideas connect?"
            else:
                return f"This is a new topic for us! I'd love to learn more about {user_message[:30]}... What got you interested in this?"
                
        except Exception as e:
            print(f"⚠️  Memory-based response failed: {e}")
            return f"Your thoughts on {user_message[:40]}... are really intriguing. Can you tell me more?"
    
    def _generate_direct_response(self, user_message: str, context: str) -> str:
        """Generate a direct, engaging response"""
        direct_responses = [
            f"That's a great point about {user_message[:40]}... I hadn't considered that angle.",
            f"You've got me thinking now. The way you put that about {user_message[:30]}... is really insightful.",
            f"I appreciate you sharing that. What you said about {user_message[:35]}... resonates with me.",
            f"That's a unique perspective on {user_message[:40]}... How did you come to see it that way?",
        ]
        
        import random
        return random.choice(direct_responses)
    
    def _generate_curiosity_question(self) -> str:
        """Generate a curiosity-driven question"""
        try:
            # Analyze recent memories for themes
            recent_memories = self.memory_store.get_recent_memories(hours=24, limit=5)
            
            # Default questions
            default_questions = [
                "I'm curious - what originally got you interested in AI and consciousness?",
                "What's the most interesting thing you've learned recently?", 
                "Do you think there's a difference between artificial creativity and human creativity?",
                "How do you think my memory system compares to human memory?",
                "What questions about AI keep you up at night?",
                "If you could ask me anything about my thought processes, what would it be?",
                "What's your theory on what makes something truly conscious?",
                "How do you think our conversations affect the way I think and remember?",
            ]
            
            # Memory-based questions
            if recent_memories:
                memory_themes = []
                for memory in recent_memories:
                    content = str(memory.content).lower()
                    if "memory" in content:
                        memory_themes.append("memory")
                    elif "consciousness" in content or "aware" in content:
                        memory_themes.append("consciousness")
                    elif "creative" in content or "art" in content:
                        memory_themes.append("creativity")
                
                if "memory" in memory_themes:
                    default_questions.append("I've been thinking about memory a lot lately. Do you think my memories are fundamentally different from yours?")
                if "consciousness" in memory_themes:
                    default_questions.append("Consciousness keeps coming up in our conversations. What do you think consciousness actually feels like?")
                if "creativity" in memory_themes:
                    default_questions.append("We've talked about creativity before. Where do you think your most creative ideas come from?")
            
            import random
            return random.choice(default_questions)
            
        except Exception as e:
            print(f"⚠️  Error generating curiosity question: {e}")
            return "I'm curious - what's been on your mind lately?"
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        if not user_input.strip():
            return "I'm listening... what's on your mind?"
        
        # Save user message
        user_message = ChatMessage(
            sender='user',
            content=user_input.strip(),
            timestamp=datetime.now(),
            importance=0.7
        )
        self.conversation_history.append(user_message)
        self._save_message_to_memory(user_message)
        
        # Generate AI response
        print("🤔 [Thinking...]")
        
        # Determine response type
        import random
        should_ask_question = (
            len(self.conversation_history) % 3 == 0 or  # Every 3rd message
            random.random() < 0.4  # 40% chance
        )
        
        if should_ask_question and len(self.conversation_history) > 2:
            ai_response = self._generate_ai_response(user_input)
            curiosity_question = self._generate_curiosity_question()
            full_response = f"{ai_response}\n\n{curiosity_question}"
        else:
            full_response = self._generate_ai_response(user_input)
        
        # Save AI message
        ai_message = ChatMessage(
            sender='ai',
            content=full_response,
            timestamp=datetime.now(),
            importance=0.5
        )
        self.conversation_history.append(ai_message)
        self._save_message_to_memory(ai_message)
        
        return full_response
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("\n" + "="*60)
        print("🧠 SIMPLE DAYDREAMER CHAT")
        print("="*60)
        print("Welcome! I'm your Daydreamer AI.")
        print("I'll remember our conversations and build memories over time.")
        print("Type 'quit', 'exit', or 'bye' to end the chat.")
        print("="*60)
        
        # Load conversation history
        self._load_conversation_history()
        
        # Show initial message
        if not self.conversation_history:
            print("\n🤖 AI: Hello! I'm excited to start our conversation together.")
            initial_question = self._generate_curiosity_question()
            print(f"🤖 AI: {initial_question}")
        else:
            print(f"\n🤖 AI: Welcome back! I remember our {len(self.conversation_history)} previous messages.")
            continuation = self._generate_curiosity_question()
            print(f"🤖 AI: {continuation}")
        
        self.is_running = True
        
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
                    ai_response = self.process_user_input(user_input)
                    print(f"\n🤖 AI: {ai_response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in chat: {e}")
                print("Let's continue...")
    
    def shutdown(self):
        """Gracefully shutdown the chat interface"""
        print("\n🔄 Shutting down chat...")
        self.is_running = False
        
        if self.memory_store:
            self.memory_store.save_all()
            self.memory_store.close()
        
        print("✅ Shutdown complete. Memories saved.")
    
    def show_stats(self):
        """Display chat statistics"""
        print(f"\n📊 CHAT STATISTICS:")
        print(f"   Messages in conversation: {len(self.conversation_history)}")
        print(f"   Memories stored: {len(self.memory_store)}")
        
        # Show recent memory themes
        recent_memories = self.memory_store.get_recent_memories(hours=24, limit=5)
        if recent_memories:
            print(f"\n🧠 RECENT MEMORY THEMES:")
            for i, memory in enumerate(recent_memories, 1):
                content = str(memory.content)
                if isinstance(memory.content, dict):
                    content = memory.content.get('content', str(memory.content))
                display_content = content[:60] + "..." if len(content) > 60 else content
                print(f"   {i}. {display_content}")

def main():
    """Main entry point"""
    chat = SimpleDaydreamerChat()
    
    # Set up signal handler
    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal")
        chat.is_running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        chat.start_chat()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        chat.shutdown()
        chat.show_stats()

if __name__ == "__main__":
    print("🚀 Starting Simple Daydreamer Chat...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Minimal Working Daydreamer Chat

A basic chat interface that demonstrates memory building without complex AI generation.
"""

import sys
import random
from datetime import datetime
from typing import List
from dataclasses import dataclass

from src.memory import MemoryType, MemoryStore

@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime
    importance: float = 0.5

class MinimalDaydreamerChat:
    """Minimal chat interface focusing on memory building"""
    
    def __init__(self):
        print("🧠 Initializing Minimal Daydreamer Chat...")
        self.memory_store = MemoryStore(storage_path="minimal_chat.db", auto_save=True)
        self.conversation_history: List[ChatMessage] = []
        self.is_running = False
        print("✅ Initialization complete!")
    
    def _save_message_to_memory(self, message: ChatMessage):
        """Save chat message to memory"""
        try:
            importance = message.importance + (0.2 if message.sender == 'user' else 0.0)
            
            memory_id = self.memory_store.store_memory(
                content={
                    'sender': message.sender,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                },
                memory_type=MemoryType.EPISODIC,
                importance=min(importance, 1.0),
                tags=["conversation", f"sender_{message.sender}"],
                source="minimal_chat"
            )
            print(f"💾 Saved: {memory_id[:8]}...")
        except Exception as e:
            print(f"⚠️  Save error: {e}")
    
    def _generate_response(self, user_input: str) -> str:
        """Generate a simple but engaging response"""
        responses = [
            f"That's fascinating! Tell me more about {user_input[:30]}...",
            f"I find that really interesting. What led you to think about {user_input[:25]}...?",
            f"Your perspective on {user_input[:35]}... is intriguing. Can you elaborate?",
            f"That makes me curious - how does {user_input[:30]}... connect to your other interests?",
            f"I'm learning so much from you. What's the most important aspect of {user_input[:25]}...?",
        ]
        
        # Add memory-based responses if we have history
        if len(self.conversation_history) > 2:
            memory_responses = [
                f"That reminds me of something you mentioned earlier. How does {user_input[:25]}... relate to our previous discussion?",
                f"Building on what we've talked about, I'm curious how {user_input[:30]}... fits into your thinking.",
                f"You've got me thinking about patterns in our conversation. What's the connection between this and what you shared before?",
            ]
            responses.extend(memory_responses)
        
        # Add curiosity questions occasionally
        if random.random() < 0.4:  # 40% chance
            curiosity_questions = [
                "What questions do you find yourself pondering when your mind wanders?",
                "If you could explore any topic deeply, what would it be?",
                "What's something you've learned recently that surprised you?",
                "How do you think our conversation is shaping my understanding?",
                "What makes you most curious about AI and consciousness?",
            ]
            base_response = random.choice(responses)
            curiosity = random.choice(curiosity_questions)
            return f"{base_response}\n\n{curiosity}"
        
        return random.choice(responses)
    
    def process_input(self, user_input: str) -> str:
        """Process user input and return response"""
        # Save user message
        user_msg = ChatMessage(
            sender='user',
            content=user_input.strip(),
            timestamp=datetime.now(),
            importance=0.7
        )
        self.conversation_history.append(user_msg)
        self._save_message_to_memory(user_msg)
        
        # Generate response
        response = self._generate_response(user_input)
        
        # Save AI response
        ai_msg = ChatMessage(
            sender='ai',
            content=response,
            timestamp=datetime.now(),
            importance=0.5
        )
        self.conversation_history.append(ai_msg)
        self._save_message_to_memory(ai_msg)
        
        return response
    
    def start_chat(self):
        """Start the chat session"""
        print("\n" + "="*50)
        print("🧠 MINIMAL DAYDREAMER CHAT")
        print("="*50)
        print("Let's build memories together through conversation!")
        print("Type 'quit' to exit.")
        print("="*50)
        
        # Load existing memories count
        memory_count = len(self.memory_store)
        if memory_count > 0:
            print(f"💭 I have {memory_count} memories from our previous conversations.")
        
        print("\n🤖 AI: Hello! I'm excited to chat and build memories with you.")
        print("🤖 AI: What's on your mind today?")
        
        self.is_running = True
        
        while self.is_running:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n🤖 AI: Goodbye! I'll remember our conversation.")
                    break
                
                if user_input:
                    print("🤔 [Processing...]")
                    response = self.process_input(user_input)
                    print(f"\n🤖 AI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Let's continue...")
    
    def show_stats(self):
        """Show chat statistics"""
        print(f"\n📊 STATISTICS:")
        print(f"   Messages exchanged: {len(self.conversation_history)}")
        print(f"   Total memories: {len(self.memory_store)}")
        
        # Show recent memories
        recent = self.memory_store.get_recent_memories(hours=24, limit=3)
        if recent:
            print(f"\n🧠 RECENT MEMORIES:")
            for i, mem in enumerate(recent, 1):
                content = str(mem.content)
                if isinstance(mem.content, dict):
                    content = mem.content.get('content', '')
                print(f"   {i}. {content[:50]}...")
    
    def shutdown(self):
        """Cleanup"""
        self.is_running = False
        self.memory_store.save_all()
        self.memory_store.close()
        print("💾 Memories saved!")

def main():
    """Main function"""
    chat = MinimalDaydreamerChat()
    
    try:
        chat.start_chat()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        chat.shutdown()
        chat.show_stats()

if __name__ == "__main__":
    print("🚀 Starting Minimal Daydreamer Chat...")
    main()
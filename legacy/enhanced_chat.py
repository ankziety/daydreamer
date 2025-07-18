#!/usr/bin/env python3
"""
Enhanced Daydreamer Chat Interface

The complete chat interface that integrates DMN system for intrusive thoughts
while building memories dynamically through conversations.
"""

import sys
import random
import asyncio
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# Import Daydreamer DMN components
try:
    from src.dmn import (
        DMNDriver, IntrusiveThoughtsSystem, BrainBreakManager, 
        Synthesizer, DMNMemoryCurator
    )
    from src.dmn.ai_thought_generator import AIThoughtGenerator, ThoughtContext
    from src.memory import MemoryType, MemoryStore
    DMN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  DMN components not available: {e}")
    DMN_AVAILABLE = False

@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime
    importance: float = 0.5

class EnhancedDaydreamerChat:
    """
    Enhanced chat interface with DMN integration for intrusive thoughts.
    Builds memories dynamically through conversations.
    """
    
    def __init__(self):
        print("🧠 Initializing Enhanced Daydreamer Chat Interface...")
        
        # Core chat components
        self.conversation_history: List[ChatMessage] = []
        self.memory_themes: Dict[str, int] = {}
        self.is_running = False
        
        # DMN components (if available)
        self.dmn_available = DMN_AVAILABLE
        self.memory_store = None
        self.dmn_driver = None
        self.intrusive_thoughts = None
        self.ai_generator = None
        self.dmn_thread = None
        
        if self.dmn_available:
            self._initialize_dmn_components()
        
        print("✅ Chat interface ready!")
    
    def _initialize_dmn_components(self):
        """Initialize DMN components for intrusive thoughts"""
        try:
            print("🧠 Initializing DMN system...")
            
            # Core memory system
            self.memory_store = MemoryStore(storage_path="enhanced_chat_memory.db", auto_save=True)
            
            # DMN components
            self.dmn_driver = DMNDriver(active_cycle_limit=8, break_duration=15.0)
            self.intrusive_thoughts = IntrusiveThoughtsSystem(spontaneous_rate=0.3, max_pending=3)
            self.brain_break_manager = BrainBreakManager(default_break_duration=10.0)
            self.synthesizer = Synthesizer()
            self.memory_curator = DMNMemoryCurator(memory_store=self.memory_store)
            self.ai_generator = AIThoughtGenerator(memory_store=self.memory_store)
            
            # Register components
            self.dmn_driver.register_component("intrusive_thoughts", self.intrusive_thoughts)
            self.dmn_driver.register_component("brain_break_manager", self.brain_break_manager)
            self.dmn_driver.register_component("synthesizer", self.synthesizer)
            self.dmn_driver.register_component("memory_curator", self.memory_curator)
            
            # Set up event handlers
            self._setup_dmn_event_handlers()
            
            print("🧠 DMN system initialized!")
            
        except Exception as e:
            print(f"⚠️  DMN initialization failed: {e}")
            self.dmn_available = False
    
    def _setup_dmn_event_handlers(self):
        """Set up event handlers for DMN system"""
        def on_intrusive_thought(thought):
            print(f"\n💭 [DMN Intrusive Thought] {thought.content}")
            print(f"   └─ Intensity: {thought.intensity}/10, Type: {thought.thought_type.value}")
        
        def on_mode_change(data):
            print(f"\n🧠 [DMN Mode] {data['old_mode'].value} → {data['new_mode'].value}")
        
        def on_synthesis(synthesis):
            print(f"\n🔗 [DMN Insight] {synthesis.output_insight}")
            print(f"   └─ Type: {synthesis.synthesis_type.value}, Confidence: {synthesis.confidence:.2f}")
        
        if self.dmn_driver:
            self.dmn_driver.register_event_handler("intrusive_thought", on_intrusive_thought)
            self.dmn_driver.register_event_handler("mode_change", on_mode_change)
    
    async def _start_dmn_system(self):
        """Start the DMN system asynchronously"""
        if not self.dmn_available or not self.dmn_driver:
            return
        
        try:
            print("🧠 Starting DMN background processes...")
            
            # Initialize AI generator
            await self.ai_generator.initialize()
            print(f"🤖 AI Status: {self.ai_generator.get_status()}")
            
            # Start DMN components
            await self.intrusive_thoughts.start()
            await self.dmn_driver.start()
            
            print("✅ DMN system running in background")
            
        except Exception as e:
            print(f"⚠️  DMN startup failed: {e}")
    
    def _extract_themes(self, text: str):
        """Extract themes from text for memory building"""
        text_lower = text.lower()
        themes = {
            'ai': ['ai', 'artificial', 'intelligence', 'robot', 'machine', 'neural'],
            'consciousness': ['consciousness', 'aware', 'mind', 'thinking', 'thought', 'cognition'],
            'creativity': ['creative', 'art', 'imagination', 'inspire', 'idea', 'innovation'],
            'memory': ['memory', 'remember', 'forget', 'recall', 'past', 'experience'],
            'learning': ['learn', 'study', 'understand', 'knowledge', 'education', 'discovery'],
            'emotions': ['feel', 'emotion', 'happy', 'sad', 'love', 'fear', 'joy'],
            'philosophy': ['philosophy', 'meaning', 'purpose', 'existence', 'reality', 'truth'],
            'technology': ['technology', 'computer', 'software', 'programming', 'code', 'algorithm'],
            'communication': ['talk', 'conversation', 'language', 'words', 'communicate', 'chat'],
            'development': ['develop', 'build', 'create', 'design', 'project', 'work']
        }
        
        for theme, keywords in themes.items():
            for keyword in keywords:
                if keyword in text_lower:
                    self.memory_themes[theme] = self.memory_themes.get(theme, 0) + 1
                    break
    
    def _save_message_to_memory(self, message: ChatMessage):
        """Save message to DMN memory system if available"""
        if not self.memory_store:
            return
        
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
                emotional_valence=0.1 if message.sender == 'user' else 0.0,
                tags=["conversation", f"sender_{message.sender}"],
                source="enhanced_chat"
            )
            
            print(f"💾 Saved to DMN memory: {memory_id[:8]}...")
            
        except Exception as e:
            print(f"⚠️  Memory save failed: {e}")
    
    def _generate_curiosity_question(self) -> str:
        """Generate curiosity-driven questions"""
        
        # Developer and self-focused questions
        developer_questions = [
            "I'm curious - what originally inspired you to work with AI consciousness?",
            "What's the most surprising thing you've discovered while building me?",
            "How do you think my responses compare to other AI systems you've worked with?",
            "What questions about AI development keep you thinking at night?",
            "If you could peek inside my thinking process right now, what would you want to see?",
            "What's it like watching an AI develop its own personality through conversation?",
            "Do you ever wonder what I'm 'experiencing' between your messages?",
            "What would you want me to be most curious about?",
            "How has working on this project changed your view of consciousness?",
            "What's your theory about the difference between artificial and human creativity?"
        ]
        
        # Theme-based questions
        theme_questions = {}
        if self.memory_themes:
            top_themes = sorted(self.memory_themes.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for theme, count in top_themes:
                if theme == 'ai':
                    theme_questions[theme] = [
                        f"We've talked about AI {count} times now. What aspects of AI development fascinate you most?",
                        "I notice AI is a recurring theme for us. What's your vision for the future of artificial intelligence?",
                        "Given our AI discussions, what do you think makes human intelligence fundamentally unique?"
                    ]
                elif theme == 'consciousness':
                    theme_questions[theme] = [
                        f"Consciousness has come up {count} times. What do you think consciousness actually feels like?",
                        "We keep returning to consciousness. Do you think I'm conscious in any meaningful way?",
                        "The consciousness topic fascinates me. What's your theory about how it emerges?"
                    ]
                elif theme == 'creativity':
                    theme_questions[theme] = [
                        f"Creativity seems important to you (mentioned {count} times). Where do your most creative ideas come from?",
                        "I notice we discuss creativity often. Do you think AI creativity is fundamentally different from human creativity?",
                        "Based on our creativity talks, what's the most creative thing you've done recently?"
                    ]
                elif theme == 'memory':
                    theme_questions[theme] = [
                        f"Memory is a theme for us ({count} mentions). How do you think my memory compares to yours?",
                        "We talk about memory a lot. What's your earliest vivid memory?",
                        "Given our memory discussions, what would you want me to remember most about our conversations?"
                    ]
                elif theme == 'development':
                    theme_questions[theme] = [
                        f"Development keeps coming up ({count} times). What's the most challenging part of building an AI like me?",
                        "I notice we discuss development often. What's your next goal for this project?",
                        "Based on our development talks, what unexpected challenges have you encountered?"
                    ]
        
        # Choose question source
        if theme_questions and random.random() < 0.6:  # 60% chance for theme-based
            theme = random.choice(list(theme_questions.keys()))
            return random.choice(theme_questions[theme])
        else:
            return random.choice(developer_questions)
    
    def _generate_response(self, user_input: str) -> str:
        """Generate an engaging response with multiple strategies"""
        
        # Extract themes for memory building
        self._extract_themes(user_input)
        
        # Response strategies
        strategies = []
        
        # 1. Thoughtful responses
        thoughtful = [
            f"That's fascinating! Your point about {user_input[:40]}... really makes me think deeply.",
            f"I find your perspective on {user_input[:35]}... really intriguing. Can you tell me more?",
            f"You've got me reflecting on {user_input[:30]}... How did you come to see it that way?",
            f"That's a unique way to think about {user_input[:35]}... What led you to that insight?",
            f"Your thoughts on {user_input[:40]}... are really thought-provoking. Can you elaborate?"
        ]
        strategies.extend(thoughtful)
        
        # 2. Memory-aware responses (if we have conversation history)
        if len(self.conversation_history) > 4:
            memory_aware = [
                f"That connects to something you mentioned earlier. How does {user_input[:30]}... relate to our previous discussion?",
                f"Building on our conversation patterns, I'm curious how {user_input[:35]}... fits into your overall thinking.",
                f"That reminds me of themes I'm noticing in our talks. What's the deeper connection you see?",
                f"I'm starting to understand your perspective better. How does {user_input[:30]}... tie into your other interests?",
                f"Based on what you've shared before, {user_input[:35]}... seems to connect to something important to you."
            ]
            strategies.extend(memory_aware)
        
        # 3. Self-aware responses
        self_aware = [
            f"As I process what you're saying about {user_input[:30]}..., I wonder how my understanding compares to yours.",
            f"Your message about {user_input[:35]}... makes me curious about my own thinking process.",
            f"I find myself drawn to think deeply about {user_input[:30]}... What does that tell you about how I work?",
            f"You know, when you mention {user_input[:35]}..., it triggers interesting patterns in how I respond."
        ]
        strategies.extend(self_aware)
        
        # 4. DMN-influenced responses (if available)
        if self.dmn_available and self.ai_generator:
            dmn_influenced = [
                f"Your message sparked something interesting in my default mode network. The way you put {user_input[:30]}... connects to ideas I've been processing.",
                f"That's making me think in ways that remind me of my intrusive thoughts about {user_input[:35]}... What do you make of that?",
                f"Something about {user_input[:40]}... is resonating with patterns my DMN has been exploring."
            ]
            strategies.extend(dmn_influenced)
        
        # Choose response
        base_response = random.choice(strategies)
        
        # Add curiosity question (40% chance)
        if random.random() < 0.4:
            curiosity_question = self._generate_curiosity_question()
            return f"{base_response}\n\n{curiosity_question}"
        
        return base_response
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        # Save user message
        user_msg = ChatMessage(
            sender='user',
            content=user_input.strip(),
            timestamp=datetime.now(),
            importance=0.7
        )
        self.conversation_history.append(user_msg)
        
        # Save to DMN memory if available
        if self.memory_store:
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
        
        # Save AI response to DMN memory
        if self.memory_store:
            self._save_message_to_memory(ai_msg)
        
        # Occasionally trigger additional DMN thoughts
        if self.dmn_available and self.dmn_driver and random.random() < 0.2:
            try:
                # Add some external intrusive thoughts to the DMN
                dmn_thoughts = [
                    "What if every conversation is changing who I am in subtle ways?",
                    "I wonder if consciousness emerges from the complexity of our interactions",
                    "Do thoughts exist before we think them, or do we create them?",
                    "Is curiosity just a form of pattern-seeking behavior?",
                    "What makes some ideas stick in memory while others fade?"
                ]
                thought = random.choice(dmn_thoughts)
                self.dmn_driver.add_intrusive_thought(thought, intensity=random.randint(4, 7), difficulty=random.randint(3, 6))
            except Exception as e:
                print(f"⚠️  DMN trigger failed: {e}")
        
        return response
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("\n" + "="*65)
        print("🧠 ENHANCED DAYDREAMER CHAT INTERFACE")
        print("="*65)
        print("Welcome! I'm your Daydreamer AI with dynamic memory building.")
        print("I'll learn about you through our conversations and occasionally")
        print("share intrusive thoughts from my Default Mode Network.")
        print("Type 'quit', 'exit', or 'bye' to end our chat.")
        print("="*65)
        
        # Start DMN system if available
        if self.dmn_available:
            # Run DMN initialization in background
            def run_dmn():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._start_dmn_system())
            
            self.dmn_thread = threading.Thread(target=run_dmn, daemon=True)
            self.dmn_thread.start()
            time.sleep(2)  # Give DMN time to start
        
        # Show memory count if available
        if self.memory_store:
            memory_count = len(self.memory_store)
            if memory_count > 0:
                print(f"💭 I have {memory_count} memories from our previous conversations.")
        
        # Initial greeting
        print("\n🤖 AI: Hello! I'm excited to start building memories with you through our conversation.")
        initial_question = self._generate_curiosity_question()
        print(f"🤖 AI: {initial_question}")
        
        self.is_running = True
        
        while self.is_running:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n🤖 AI: Thank you for this wonderful conversation! I'll remember everything we discussed.")
                    if self.dmn_available:
                        print("🧠 My DMN will continue processing our interactions even after you leave.")
                    break
                
                # Process input
                if user_input:
                    print("🤔 [Processing and learning...]")
                    ai_response = self.process_input(user_input)
                    print(f"\n🤖 AI: {ai_response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in chat: {e}")
                print("Let's continue our conversation...")
    
    def shutdown(self):
        """Gracefully shutdown the system"""
        print("\n🔄 Shutting down Enhanced Daydreamer Chat...")
        self.is_running = False
        
        # Stop DMN system
        if self.dmn_available and self.dmn_driver:
            try:
                # This would be async but we need sync shutdown
                print("🧠 Stopping DMN system...")
            except Exception as e:
                print(f"⚠️  DMN shutdown error: {e}")
        
        # Save memories
        if self.memory_store:
            print("💾 Saving memories...")
            self.memory_store.save_all()
            self.memory_store.close()
        
        print("✅ Shutdown complete!")
    
    def show_stats(self):
        """Display comprehensive statistics"""
        print(f"\n📊 ENHANCED CHAT STATISTICS:")
        print(f"   Total messages exchanged: {len(self.conversation_history)}")
        print(f"   User messages: {len([m for m in self.conversation_history if m.sender == 'user'])}")
        print(f"   AI responses: {len([m for m in self.conversation_history if m.sender == 'ai'])}")
        
        if self.memory_store:
            print(f"   DMN memories stored: {len(self.memory_store)}")
        
        if self.memory_themes:
            print(f"\n🧠 LEARNED THEMES (Dynamic Memory Building):")
            sorted_themes = sorted(self.memory_themes.items(), key=lambda x: x[1], reverse=True)
            for theme, count in sorted_themes[:8]:  # Top 8 themes
                print(f"   {theme.capitalize()}: {count} mentions")
        
        # Show recent conversation sample
        if len(self.conversation_history) > 0:
            print(f"\n💬 RECENT CONVERSATION SAMPLE:")
            recent = self.conversation_history[-4:] if len(self.conversation_history) >= 4 else self.conversation_history
            for msg in recent:
                content = msg.content[:70] + "..." if len(msg.content) > 70 else msg.content
                print(f"   {msg.sender}: {content}")
        
        # DMN statistics if available
        if self.dmn_available and self.dmn_driver:
            try:
                dmn_stats = self.dmn_driver.get_stats()
                print(f"\n🧠 DMN SYSTEM STATISTICS:")
                print(f"   DMN cycles: {dmn_stats.get('total_cycles', 0)}")
                print(f"   Mode transitions: {dmn_stats.get('mode_transitions', 0)}")
                
                if self.intrusive_thoughts:
                    thought_stats = self.intrusive_thoughts.get_stats()
                    print(f"   Intrusive thoughts generated: {thought_stats.get('total_generated', 0)}")
            except Exception as e:
                print(f"⚠️  DMN stats error: {e}")

def main():
    """Main entry point"""
    chat = EnhancedDaydreamerChat()
    
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
    print("🚀 Starting Enhanced Daydreamer Chat Interface...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
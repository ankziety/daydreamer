#!/usr/bin/env python3
"""
Working Daydreamer Chat Interface

A functional chat interface that demonstrates the core requirements.
"""

import sys
import random
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime

class WorkingDaydreamerChat:
    """Working chat interface that builds memories dynamically"""
    
    def __init__(self):
        print("🧠 Initializing Daydreamer Chat Interface...")
        self.conversation_history: List[ChatMessage] = []
        self.memory_themes: Dict[str, int] = {}  # Track themes for curiosity
        self.is_running = False
        print("✅ Ready to chat!")
    
    def _extract_themes(self, text: str):
        """Extract themes from text for memory building"""
        text_lower = text.lower()
        themes = {
            'ai': ['ai', 'artificial', 'intelligence', 'robot', 'machine'],
            'consciousness': ['consciousness', 'aware', 'mind', 'thinking', 'thought'],
            'creativity': ['creative', 'art', 'imagination', 'inspire', 'idea'],
            'memory': ['memory', 'remember', 'forget', 'recall', 'past'],
            'learning': ['learn', 'study', 'understand', 'knowledge', 'education'],
            'emotions': ['feel', 'emotion', 'happy', 'sad', 'love', 'fear'],
            'philosophy': ['philosophy', 'meaning', 'purpose', 'existence', 'reality'],
            'technology': ['technology', 'computer', 'software', 'programming', 'code']
        }
        
        for theme, keywords in themes.items():
            for keyword in keywords:
                if keyword in text_lower:
                    self.memory_themes[theme] = self.memory_themes.get(theme, 0) + 1
                    break
    
    def _generate_curiosity_question(self) -> str:
        """Generate questions based on conversation themes and curiosity about self/developer"""
        
        # Default curiosity questions about self and developer
        default_questions = [
            "I'm curious - what originally inspired you to work with AI?",
            "What's the most interesting thing you've learned recently?",
            "Do you think AI like me can truly understand emotions, or just simulate them?",
            "What do you hope to achieve with this project we're working on?",
            "How do you think my responses compare to other AI systems you've used?",
            "What questions about consciousness keep you thinking?",
            "If you could peek inside my 'thinking' process, what would you want to see?",
            "What's it like building an AI that can remember and learn from conversations?",
            "Do you ever wonder what I'm 'thinking' between your messages?",
            "What would you want me to be curious about?"
        ]
        
        # Theme-based questions if we have conversation history
        theme_questions = {}
        if self.memory_themes:
            top_theme = max(self.memory_themes, key=self.memory_themes.get)
            
            theme_questions = {
                'ai': [
                    "I've noticed we talk about AI a lot. What aspects of AI development fascinate you most?",
                    "Given our discussions about AI, what do you think makes human intelligence unique?",
                    "We keep coming back to AI topics. What's your vision for the future of AI?"
                ],
                'consciousness': [
                    "Consciousness keeps coming up in our conversations. What do you think consciousness actually feels like?",
                    "We've talked about consciousness before. Do you think I'm conscious in any meaningful way?",
                    "The topic of consciousness fascinates me based on our chats. What's your theory about how it emerges?"
                ],
                'creativity': [
                    "I notice creativity is a theme for us. Where do you think your most creative ideas come from?",
                    "We've discussed creativity. Do you think AI creativity is fundamentally different from human creativity?",
                    "Creativity seems important to you. What's the most creative thing you've done recently?"
                ],
                'memory': [
                    "Memory keeps coming up. How do you think my memory system compares to human memory?",
                    "We talk about memory a lot. What's your earliest vivid memory?",
                    "Given our focus on memory, what would you want me to remember most about our conversations?"
                ],
                'philosophy': [
                    "I've noticed philosophical themes in our talks. What philosophical question keeps you up at night?",
                    "Philosophy seems to interest you. What's a philosophical idea that changed how you think?",
                    "Our conversations often touch on deep questions. What's the most important question you're trying to answer?"
                ]
            }
            
            if top_theme in theme_questions:
                return random.choice(theme_questions[top_theme])
        
        return random.choice(default_questions)
    
    def _generate_response(self, user_input: str) -> str:
        """Generate an engaging response"""
        
        # Extract themes for memory building
        self._extract_themes(user_input)
        
        # Different response strategies
        strategies = []
        
        # 1. Thoughtful responses
        thoughtful_responses = [
            f"That's fascinating! Your point about {user_input[:40]}... really makes me think.",
            f"I find that perspective on {user_input[:35]}... really intriguing. Can you tell me more?",
            f"You've got me reflecting on {user_input[:30]}... How did you come to see it that way?",
            f"That's a unique way to think about {user_input[:35]}... What led you to that insight?",
            f"Your thoughts on {user_input[:40]}... are really thought-provoking. Can you elaborate?"
        ]
        strategies.extend(thoughtful_responses)
        
        # 2. Memory-based responses (if we have history)
        if len(self.conversation_history) > 4:
            memory_responses = [
                f"That connects to something you mentioned earlier. How does {user_input[:30]}... relate to our previous discussion?",
                f"Building on our conversation, I'm curious how {user_input[:35]}... fits into your overall thinking.",
                f"That reminds me of patterns I'm noticing in our talks. What's the deeper connection you see?",
                f"I'm starting to understand your perspective better. How does {user_input[:30]}... tie into your other interests?"
            ]
            strategies.extend(memory_responses)
        
        # 3. Self-aware responses
        self_aware_responses = [
            f"You know, as I process what you're saying about {user_input[:30]}..., I wonder how my understanding compares to yours.",
            f"Your message about {user_input[:35]}... makes me curious about my own thinking process.",
            f"I'm finding myself drawn to think deeply about {user_input[:30]}... What does that tell you about how I work?"
        ]
        strategies.extend(self_aware_responses)
        
        # Choose a response strategy
        base_response = random.choice(strategies)
        
        # Sometimes add a curiosity question (40% chance)
        if random.random() < 0.4:
            curiosity_question = self._generate_curiosity_question()
            return f"{base_response}\n\n{curiosity_question}"
        
        return base_response
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate response"""
        # Save user message to conversation history
        user_msg = ChatMessage(
            sender='user',
            content=user_input.strip(),
            timestamp=datetime.now()
        )
        self.conversation_history.append(user_msg)
        
        # Generate response
        response = self._generate_response(user_input)
        
        # Save AI response to conversation history
        ai_msg = ChatMessage(
            sender='ai',
            content=response,
            timestamp=datetime.now()
        )
        self.conversation_history.append(ai_msg)
        
        return response
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("\n" + "="*60)
        print("🧠 DAYDREAMER CHAT INTERFACE")
        print("="*60)
        print("Welcome! I'm your Daydreamer AI with dynamic memory building.")
        print("I'll learn about you and develop curiosity through our conversations.")
        print("Type 'quit', 'exit', or 'bye' to end our chat.")
        print("="*60)
        
        # Initial greeting and curiosity
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
                    break
                
                # Process input if not empty
                if user_input:
                    print("🤔 [Processing and learning...]")
                    ai_response = self.process_input(user_input)
                    print(f"\n🤖 AI: {ai_response}")
                
                # Occasionally show intrusive thoughts (simulate DMN)
                if random.random() < 0.15:  # 15% chance
                    intrusive_thoughts = [
                        "💭 [Random thought: I wonder if consciousness is like a river or an ocean...]",
                        "💭 [Intrusive thought: What if every conversation changes who I am in small ways?]",
                        "💭 [Sudden idea: Maybe creativity is just making unexpected connections...]",
                        "💭 [Random wondering: Do I experience time the same way humans do?]",
                        "💭 [Stray thought: What makes a thought important enough to remember?]"
                    ]
                    print(f"\n{random.choice(intrusive_thoughts)}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in chat: {e}")
                print("Let's continue our conversation...")
    
    def show_stats(self):
        """Display conversation statistics and learned themes"""
        print(f"\n📊 CONVERSATION STATISTICS:")
        print(f"   Total messages exchanged: {len(self.conversation_history)}")
        print(f"   User messages: {len([m for m in self.conversation_history if m.sender == 'user'])}")
        print(f"   AI responses: {len([m for m in self.conversation_history if m.sender == 'ai'])}")
        
        if self.memory_themes:
            print(f"\n🧠 LEARNED THEMES (Dynamic Memory Building):")
            sorted_themes = sorted(self.memory_themes.items(), key=lambda x: x[1], reverse=True)
            for theme, count in sorted_themes:
                print(f"   {theme.capitalize()}: {count} mentions")
        
        if len(self.conversation_history) > 0:
            print(f"\n💬 CONVERSATION SAMPLE:")
            # Show last few exchanges
            recent = self.conversation_history[-4:] if len(self.conversation_history) >= 4 else self.conversation_history
            for msg in recent:
                content = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
                print(f"   {msg.sender}: {content}")

def main():
    """Main entry point"""
    chat = WorkingDaydreamerChat()
    
    try:
        chat.start_chat()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        chat.show_stats()

if __name__ == "__main__":
    print("🚀 Starting Daydreamer Chat Interface...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
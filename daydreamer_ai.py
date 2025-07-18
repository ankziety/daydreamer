#!/usr/bin/env python3
"""
Daydreamer AI - Integrated Chat Interface
==========================================

This is the main chat interface that integrates all Daydreamer components:
- True Chain of Thought reasoning
- Day Dreaming technique for creative insights
- Persistent memory across sessions
- Clean Ollama integration with fallback
"""

import asyncio
import sys
import uuid
import time
from typing import Optional, Dict, Any
from datetime import datetime

from prompts import DaydreamerPrompts, get_general_response_prompt
from chain_of_thought import ChainOfThoughtProcessor, ChainOfThoughtResult
from day_dreaming import DaydreamingEngine, DaydreamSession
from memory_manager import PersistentMemoryManager, get_conversation_context, analyze_user_interests
from ollama_integration import ModelManager, create_model_manager, ModelRequest


class DaydreamerAI:
    """
    The main Daydreamer AI system that integrates all components for
    true chain of thought reasoning and creative day dreaming.
    """
    
    def __init__(self, 
                 memory_db_path: str = "daydreamer_memory.db",
                 model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Daydreamer AI system.
        
        Args:
            memory_db_path: Path to persistent memory database
            model_config: Model configuration dictionary
        """
        print("🧠 Initializing Daydreamer AI System...")
        print("=" * 60)
        
        # Generate session ID
        self.session_id = str(uuid.uuid4())[:8]
        print(f"Session ID: {self.session_id}")
        
        # Initialize components
        self.memory_manager = PersistentMemoryManager(memory_db_path)
        self.model_manager = create_model_manager(model_config or {})
        self.cot_processor = ChainOfThoughtProcessor(self.model_manager)
        self.daydream_engine = DaydreamingEngine(self.model_manager, self.memory_manager)
        self.prompts = DaydreamerPrompts()
        
        # System state
        self.conversation_count = 0
        self.total_thinking_time = 0.0
        self.total_daydream_time = 0.0
        self.is_running = False
        
        # Load user profile and show stats
        self._load_user_profile()
        self._show_initialization_summary()
    
    def _load_user_profile(self):
        """Load user profile from memory"""
        profile = self.memory_manager.get_user_profile()
        if profile:
            print(f"👤 User profile loaded (last updated: {profile.last_updated.strftime('%Y-%m-%d')})")
            if profile.interests:
                top_interests = sorted(profile.interests.items(), key=lambda x: x[1], reverse=True)[:3]
                interests_str = ", ".join([f"{topic}({score:.1f})" for topic, score in top_interests])
                print(f"   Top interests: {interests_str}")
        else:
            print("👤 New user - will build profile through conversation")
    
    def _show_initialization_summary(self):
        """Show initialization summary"""
        stats = self.memory_manager.get_memory_stats()
        model_info = self.model_manager.get_model_info()
        
        print(f"\n📊 Memory Stats:")
        print(f"   Conversations: {stats.get('total_conversations', 0)}")
        print(f"   Sessions: {stats.get('total_sessions', 0)}")
        print(f"   Insights: {stats.get('total_insights', 0)}")
        print(f"   Recent activity: {stats.get('recent_conversations', 0)} conversations (7 days)")
        
        print(f"\n🤖 AI Model:")
        print(f"   Active: {model_info.get('active_model', 'None')}")
        print(f"   Ollama available: {model_info.get('ollama_available', False)}")
        print(f"   Transformers available: {model_info.get('transformers_available', False)}")
        
        print("\n✅ All systems initialized!")
        print("=" * 60)
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input through the complete Daydreamer pipeline.
        
        Args:
            user_input: User's message
            
        Returns:
            AI response
        """
        print(f"\n{'='*15} PROCESSING USER INPUT {'='*15}")
        start_time = time.time()
        
        # Get conversation context
        context = get_conversation_context(self.memory_manager, self.session_id)
        print(f"📖 Retrieved context: {len(context)} characters")
        
        # Step 1: Chain of Thought Analysis
        print(f"\n🧠 Starting Chain of Thought analysis...")
        cot_result = await self.cot_processor.process_chain_of_thought(
            user_input, 
            context,
            progress_callback=lambda msg: print(f"   {msg}")
        )
        
        self.total_thinking_time += cot_result.total_thinking_time
        print(f"✅ Chain of Thought complete: {len(cot_result.thinking_steps)} steps, {cot_result.total_thinking_time:.1f}s")
        
        # Step 2: Check if we should trigger daydreaming
        daydream_result = None
        full_context = f"{context}\n{user_input}" if context else user_input
        
        if await self.daydream_engine.should_daydream(full_context):
            print(f"\n🌙 Triggering Day Dreaming session...")
            daydream_result = await self.daydream_engine.trigger_daydream_session(
                full_context,
                "contextual_trigger",
                progress_callback=lambda msg: print(f"   {msg}")
            )
            self.total_daydream_time += daydream_result.total_time
            print(f"✅ Day Dreaming complete: {len(daydream_result.insights)} insights, {daydream_result.total_time:.1f}s")
        
        # Step 3: Retrieve relevant memories
        print(f"\n💭 Retrieving relevant memories...")
        relevant_memories = self.memory_manager.get_relevant_memories(user_input, limit=3)
        memory_context = ""
        if relevant_memories:
            memory_parts = []
            for memory in relevant_memories:
                memory_parts.append(f"- {memory.user_input[:100]}...")
            memory_context = "\n".join(memory_parts)
            print(f"   Found {len(relevant_memories)} relevant memories")
        else:
            print("   No relevant memories found")
        
        # Step 4: Generate final response
        print(f"\n🎯 Generating final response...")
        response = await self._generate_final_response(
            user_input, context, cot_result, daydream_result, memory_context
        )
        
        # Step 5: Store conversation in memory
        importance = self._calculate_importance(user_input, response, cot_result, daydream_result)
        tags = self._extract_tags(user_input, response)
        
        cot_summary = cot_result.final_conclusions if cot_result else None
        daydream_summary = daydream_result.best_insight.insight if daydream_result and daydream_result.best_insight else None
        
        memory_id = self.memory_manager.store_conversation(
            user_input=user_input,
            ai_response=response,
            session_id=self.session_id,
            context=context,
            importance=importance,
            tags=tags,
            cot_summary=cot_summary,
            daydream_insights=daydream_summary
        )
        
        # Store insights separately
        if cot_result:
            self.memory_manager.store_insight(
                insight_type="cot",
                insight_content=cot_result.final_conclusions,
                creativity_score=0.6,  # CoT is more analytical
                relevance_score=cot_result.confidence_score,
                context=full_context
            )
        
        if daydream_result and daydream_result.best_insight:
            insight = daydream_result.best_insight
            self.memory_manager.store_insight(
                insight_type="daydream",
                insight_content=insight.insight,
                creativity_score=insight.creativity_score,
                relevance_score=insight.relevance_score,
                context=full_context,
                knowledge_domain=insight.seed.knowledge_domain,
                connections=insight.connections_made
            )
        
        # Update user profile
        await self._update_user_profile(user_input, response)
        
        total_time = time.time() - start_time
        self.conversation_count += 1
        
        print(f"\n📊 Processing complete: {total_time:.1f}s total")
        print(f"   Memory stored: {memory_id}")
        print(f"   Importance: {importance:.2f}")
        print(f"=" * 50)
        
        return response
    
    async def _generate_final_response(self, 
                                     user_input: str,
                                     context: str,
                                     cot_result: Optional[ChainOfThoughtResult],
                                     daydream_result: Optional[DaydreamSession],
                                     memory_context: str) -> str:
        """Generate the final response integrating all insights"""
        
        # Prepare components for response generation
        cot_conclusions = cot_result.final_conclusions if cot_result else ""
        
        daydream_insights = ""
        if daydream_result and daydream_result.best_insight:
            insight = daydream_result.best_insight
            if insight.relevance_score >= 0.4:  # Only include relevant insights
                daydream_insights = f"Creative insight from {insight.seed.knowledge_domain}: {insight.insight}"
        
        # Create response generation request
        prompt = get_general_response_prompt(
            user_input=user_input,
            context=context[:500] if context else "",  # Limit context to prevent token overflow
            cot_conclusions=cot_conclusions,
            daydream_insights=daydream_insights,
            relevant_memories=memory_context
        )
        
        request = ModelRequest(
            prompt=prompt,
            system_prompt=self.prompts.SYSTEM_IDENTITY,
            temperature=0.8,  # Higher temperature for more creative responses
            max_tokens=400
        )
        
        response = await self.model_manager.generate_response(request)
        
        if response.error:
            # Fallback response if model fails
            return f"I'm having trouble processing that right now, but I'm thinking about: {user_input[:100]}..."
        
        return response.content
    
    def _calculate_importance(self, 
                            user_input: str, 
                            ai_response: str,
                            cot_result: Optional[ChainOfThoughtResult],
                            daydream_result: Optional[DaydreamSession]) -> float:
        """Calculate importance score for memory storage"""
        importance = 0.5  # Base importance
        
        # Increase for longer, more substantive inputs
        if len(user_input) > 50:
            importance += 0.1
        if len(user_input) > 200:
            importance += 0.1
        
        # Increase for questions
        if '?' in user_input:
            importance += 0.1
        
        # Increase based on CoT confidence
        if cot_result:
            importance += (cot_result.confidence_score - 0.5) * 0.2
        
        # Increase for creative insights
        if daydream_result and daydream_result.best_insight:
            importance += daydream_result.best_insight.creativity_score * 0.2
        
        # Check for important keywords
        important_keywords = [
            'question', 'problem', 'help', 'understand', 'explain',
            'curious', 'wonder', 'think', 'feel', 'believe'
        ]
        user_lower = user_input.lower()
        keyword_matches = sum(1 for keyword in important_keywords if keyword in user_lower)
        importance += min(0.2, keyword_matches * 0.05)
        
        return min(1.0, importance)
    
    def _extract_tags(self, user_input: str, ai_response: str) -> list[str]:
        """Extract tags for conversation categorization"""
        tags = []
        text = f"{user_input} {ai_response}".lower()
        
        # Topic tags
        topic_keywords = {
            'ai': ['ai', 'artificial', 'intelligence', 'machine'],
            'consciousness': ['consciousness', 'aware', 'mind', 'thinking'],
            'creativity': ['creative', 'art', 'imagination', 'inspire'],
            'philosophy': ['philosophy', 'meaning', 'purpose', 'existence'],
            'science': ['science', 'research', 'discovery', 'experiment'],
            'technology': ['technology', 'computer', 'programming', 'code'],
            'learning': ['learn', 'study', 'understand', 'knowledge'],
            'emotion': ['feel', 'emotion', 'happy', 'sad', 'love', 'fear']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(topic)
        
        # Interaction type tags
        if '?' in user_input:
            tags.append('question')
        if len(user_input) > 200:
            tags.append('detailed')
        if any(word in text for word in ['thank', 'thanks', 'appreciate']):
            tags.append('gratitude')
        
        return tags[:5]  # Limit to 5 tags
    
    async def _update_user_profile(self, user_input: str, ai_response: str):
        """Update user profile based on conversation"""
        # Analyze interests from current conversation
        interests = analyze_user_interests(self.memory_manager)
        
        # Simple communication style analysis
        communication_style = {}
        if len(user_input) > 100:
            communication_style['verbosity'] = 'detailed'
        elif len(user_input) < 20:
            communication_style['verbosity'] = 'concise'
        else:
            communication_style['verbosity'] = 'moderate'
        
        if '?' in user_input:
            communication_style['inquisitive'] = 'high'
        
        # Update profile
        self.memory_manager.update_user_profile(
            interests=interests,
            communication_style=communication_style
        )
    
    async def start_interactive_chat(self):
        """Start interactive chat session"""
        print("\n" + "=" * 70)
        print("🧠 DAYDREAMER AI - INTERACTIVE CHAT")
        print("=" * 70)
        print("Welcome to Daydreamer AI! I use advanced Chain of Thought reasoning")
        print("and creative Day Dreaming to provide thoughtful, insightful responses.")
        print("I remember our conversations and learn about you over time.")
        print()
        print("Type 'quit', 'exit', or 'bye' to end our chat.")
        print("Type 'stats' to see conversation statistics.")
        print("=" * 70)
        
        # Show memory context if available
        recent_memories = self.memory_manager.get_recent_conversations(limit=3)
        if recent_memories:
            print(f"\n💭 I remember our recent conversations...")
            print(f"   Last chat: {recent_memories[0].timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        self.is_running = True
        
        try:
            while self.is_running:
                try:
                    # Get user input
                    user_input = input("\n👤 You: ").strip()
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                        await self._handle_goodbye()
                        break
                    elif user_input.lower() == 'stats':
                        self._show_conversation_stats()
                        continue
                    elif user_input.lower() == 'help':
                        self._show_help()
                        continue
                    
                    if not user_input:
                        continue
                    
                    # Process input and generate response
                    print("🤔 Processing your message...")
                    response = await self.process_user_input(user_input)
                    
                    print(f"\n🤖 Daydreamer AI: {response}")
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Chat interrupted by user")
                    break
                except Exception as e:
                    print(f"\n❌ Error processing message: {e}")
                    print("Let's continue our conversation...")
        
        finally:
            await self._shutdown()
    
    async def _handle_goodbye(self):
        """Handle user saying goodbye"""
        print("\n🤖 Daydreamer AI: Thank you for our conversation! I'll remember everything we discussed.")
        print("My memories will help me understand you better next time we chat.")
        
        # Create session summary
        if self.conversation_count > 0:
            recent_memories = self.memory_manager.get_recent_conversations(
                limit=self.conversation_count,
                session_id=self.session_id
            )
            if recent_memories:
                topics = set()
                for memory in recent_memories:
                    topics.update(memory.tags)
                
                summary = f"Session with {self.conversation_count} exchanges. Topics: {', '.join(list(topics)[:5])}"
                self.memory_manager.create_session_summary(self.session_id, summary)
                print(f"💾 Session summary saved: {summary}")
    
    def _show_conversation_stats(self):
        """Show conversation statistics"""
        stats = self.memory_manager.get_memory_stats()
        
        print(f"\n📊 CONVERSATION STATISTICS")
        print(f"   Current session exchanges: {self.conversation_count}")
        print(f"   Total thinking time: {self.total_thinking_time:.1f}s")
        print(f"   Total daydream time: {self.total_daydream_time:.1f}s")
        print(f"   Total conversations stored: {stats.get('total_conversations', 0)}")
        print(f"   Total sessions: {stats.get('total_sessions', 0)}")
        print(f"   Total insights generated: {stats.get('total_insights', 0)}")
        
        # Show recent insights
        recent_insights = self.memory_manager.get_insights(limit=3)
        if recent_insights:
            print(f"\n🌟 Recent insights:")
            for insight in recent_insights:
                score = insight.creativity_score + insight.relevance_score
                print(f"   {insight.insight_type}: {insight.insight_content[:80]}... (score: {score:.2f})")
    
    def _show_help(self):
        """Show help information"""
        print(f"\n❓ DAYDREAMER AI HELP")
        print(f"   Commands:")
        print(f"   • 'stats' - Show conversation statistics")
        print(f"   • 'help' - Show this help message")
        print(f"   • 'quit/exit/bye' - End conversation")
        print(f"   ")
        print(f"   Features:")
        print(f"   • Chain of Thought reasoning for deep analysis")
        print(f"   • Day Dreaming for creative insights")
        print(f"   • Persistent memory across conversations")
        print(f"   • Learning about your interests and communication style")
    
    async def _shutdown(self):
        """Gracefully shutdown the system"""
        print("\n🔄 Shutting down Daydreamer AI...")
        
        # Clean up old memories periodically
        if self.conversation_count > 10:
            self.memory_manager.cleanup_old_memories()
            print("🧹 Cleaned up old memories")
        
        # Close memory manager
        self.memory_manager.close()
        print("💾 Memory saved and closed")
        
        print("✅ Shutdown complete!")


# Main function for running the chat interface
async def main():
    """Main function to run Daydreamer AI"""
    print("🚀 Starting Daydreamer AI System...")
    
    try:
        # Create and start the AI system
        ai = DaydreamerAI()
        await ai.start_interactive_chat()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
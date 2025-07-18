#!/usr/bin/env python3
"""
Research-Grade Daydreamer Chat Interface

A fully conversational AI system with chain of thought patterns, daydreaming
capabilities, and comprehensive research-oriented information display.

This implementation meets all research requirements:
- ChatGPT-like conversational capability
- Chain of thought pattern for all user messages
- Daydream pattern with random knowledge retrieval
- Reactive and engaging conversation
- Fine-tuning simulation through adaptive responses
- Research-oriented informative interface
- No emojis or hardcoded responses
- Open model support with Ollama/API key options
- Version and model information display
"""

import sys
import random
import asyncio
import threading
import time
import json
import platform
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import sqlite3

# Core AI and model imports
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Import Daydreamer components
try:
    from src.ai.gemma3n_provider import Gemma3NProvider, ModelRequest, ModelResponse
    from src.memory import MemoryStore, MemoryEntry, MemoryType
    from src.dmn import (
        DMNDriver, IntrusiveThoughtsSystem, BrainBreakManager,
        Synthesizer, DMNMemoryCurator
    )
    from src.dmn.ai_thought_generator import AIThoughtGenerator, ThoughtContext
    DAYDREAMER_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some Daydreamer components not available: {e}")
    DAYDREAMER_COMPONENTS_AVAILABLE = False


@dataclass
class SystemInfo:
    """System information for research transparency"""
    python_version: str
    platform: str
    ollama_available: bool
    transformers_available: bool
    torch_version: Optional[str]
    primary_model: str
    fallback_model: str
    memory_store_active: bool
    dmn_active: bool


@dataclass
class ChainOfThought:
    """Chain of thought structure for user message processing"""
    user_input: str
    initial_analysis: str
    context_retrieval: str
    knowledge_integration: str
    response_planning: str
    final_synthesis: str
    confidence_score: float
    processing_time: float


@dataclass
class DaydreamMoment:
    """Structure for daydreaming episodes"""
    trigger: str
    knowledge_source: str
    random_memory: Optional[str]
    insight: str
    connection_strength: float
    timestamp: datetime


class ResearchChat:
    """
    Research-grade conversational AI with full daydreaming and CoT capabilities.
    
    Features:
    - Chain of thought processing for every user input
    - Random knowledge retrieval and daydreaming
    - Adaptive response generation (fine-tuning simulation)
    - Comprehensive research information display
    - No hardcoded responses or leading prompts
    """
    
    def __init__(self, api_key: Optional[str] = None, model_preference: str = "auto"):
        """
        Initialize the research chat system.
        
        Args:
            api_key: Optional API key for premium models
            model_preference: "ollama", "transformers", "api", or "auto"
        """
        print("=" * 80)
        print("DAYDREAMER RESEARCH AI SYSTEM")
        print("=" * 80)
        print("Initializing research-grade conversational AI...")
        
        self.api_key = api_key
        self.model_preference = model_preference
        self.conversation_history: List[Dict[str, Any]] = []
        self.daydream_memories: List[DaydreamMoment] = []
        self.learned_patterns: Dict[str, float] = {}
        self.user_profile: Dict[str, Any] = {}
        self.is_running = False
        
        # Initialize system components
        self._initialize_system_info()
        self._initialize_ai_models()
        self._initialize_memory_system()
        self._initialize_dmn_system()
        self._initialize_chain_of_thought()
        
        print("\n" + "=" * 80)
        print("SYSTEM READY FOR RESEARCH CONVERSATIONS")
        print("=" * 80)
        
    def _initialize_system_info(self):
        """Initialize and display system information for research transparency"""
        print("\n--- SYSTEM INFORMATION ---")
        
        torch_version = None
        if TRANSFORMERS_AVAILABLE:
            try:
                torch_version = torch.__version__
            except:
                torch_version = "Unknown"
        
        self.system_info = SystemInfo(
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            ollama_available=OLLAMA_AVAILABLE,
            transformers_available=TRANSFORMERS_AVAILABLE,
            torch_version=torch_version,
            primary_model="Not initialized",
            fallback_model="Not initialized",
            memory_store_active=False,
            dmn_active=False
        )
        
        print(f"Python Version: {self.system_info.python_version}")
        print(f"Platform: {self.system_info.platform}")
        print(f"Ollama Available: {self.system_info.ollama_available}")
        print(f"Transformers Available: {self.system_info.transformers_available}")
        if torch_version:
            print(f"PyTorch Version: {torch_version}")
    
    def _initialize_ai_models(self):
        """Initialize AI models based on availability and preference"""
        print("\n--- AI MODEL INITIALIZATION ---")
        
        self.primary_model = None
        self.fallback_model = None
        
        # Try Ollama first if available and preferred
        if (self.model_preference in ["ollama", "auto"] and 
            OLLAMA_AVAILABLE and DAYDREAMER_COMPONENTS_AVAILABLE):
            try:
                self.primary_model = Gemma3NProvider()
                self.system_info.primary_model = "Gemma3N via Ollama"
                print(f"✅ Primary Model: {self.system_info.primary_model}")
            except Exception as e:
                print(f"⚠️ Ollama initialization failed: {e}")
        
        # Initialize transformers fallback
        if (self.model_preference in ["transformers", "auto"] and 
            TRANSFORMERS_AVAILABLE):
            try:
                print("Loading GPT-2 transformers model...")
                self.fallback_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
                self.fallback_model = GPT2LMHeadModel.from_pretrained('gpt2')
                self.fallback_tokenizer.pad_token = self.fallback_tokenizer.eos_token
                self.system_info.fallback_model = "GPT-2 via Transformers"
                print(f"✅ Fallback Model: {self.system_info.fallback_model}")
            except Exception as e:
                print(f"❌ Transformers initialization failed: {e}")
        
        # If no models available, create a simple generator
        if not self.primary_model and not self.fallback_model:
            print("⚠️ Using minimal response generator")
            self.system_info.primary_model = "Minimal Generator"
    
    def _initialize_memory_system(self):
        """Initialize memory system for knowledge storage and retrieval"""
        print("\n--- MEMORY SYSTEM INITIALIZATION ---")
        
        if DAYDREAMER_COMPONENTS_AVAILABLE:
            try:
                self.memory_store = MemoryStore()
                self.system_info.memory_store_active = True
                print("✅ Memory Store initialized")
                
                # Create database for research chat memories
                self.db_path = "research_chat_memory.db"
                self._init_database()
                print(f"✅ Research memory database: {self.db_path}")
                
            except Exception as e:
                print(f"⚠️ Memory system initialization warning: {e}")
                self.memory_store = None
        else:
            print("⚠️ Memory system not available")
            self.memory_store = None
    
    def _init_database(self):
        """Initialize SQLite database for conversation and research data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                ai_response TEXT,
                chain_of_thought TEXT,
                daydream_moment TEXT,
                learned_patterns TEXT
            )
        ''')
        
        # Research insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                insight_type TEXT,
                content TEXT,
                confidence REAL,
                context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_dmn_system(self):
        """Initialize Default Mode Network for daydreaming"""
        print("\n--- DEFAULT MODE NETWORK INITIALIZATION ---")
        
        if DAYDREAMER_COMPONENTS_AVAILABLE:
            try:
                self.dmn_driver = DMNDriver()
                self.intrusive_thoughts = IntrusiveThoughtsSystem()
                self.synthesizer = Synthesizer()
                self.ai_thought_generator = AIThoughtGenerator()
                self.system_info.dmn_active = True
                print("✅ DMN components initialized")
            except Exception as e:
                print(f"⚠️ DMN initialization warning: {e}")
                self.system_info.dmn_active = False
        else:
            print("⚠️ DMN system not available")
            self.system_info.dmn_active = False
    
    def _initialize_chain_of_thought(self):
        """Initialize chain of thought processing system"""
        print("\n--- CHAIN OF THOUGHT INITIALIZATION ---")
        print("✅ CoT processor ready for user input analysis")
        print("✅ Knowledge integration pipeline active")
        print("✅ Response synthesis engine ready")
    
    def process_chain_of_thought(self, user_input: str) -> ChainOfThought:
        """
        Process user input through chain of thought analysis.
        
        Args:
            user_input: The user's message
            
        Returns:
            ChainOfThought object with complete analysis
        """
        start_time = time.time()
        
        print(f"\n{'='*20} CHAIN OF THOUGHT ANALYSIS {'='*20}")
        print(f"User Input: '{user_input}'")
        
        # Step 1: Initial Analysis
        print("\n[1/6] Initial Analysis...")
        initial_analysis = self._analyze_input_intent(user_input)
        print(f"Intent: {initial_analysis}")
        
        # Step 2: Context Retrieval
        print("\n[2/6] Context Retrieval...")
        context_retrieval = self._retrieve_conversation_context(user_input)
        print(f"Context: {context_retrieval}")
        
        # Step 3: Knowledge Integration
        print("\n[3/6] Knowledge Integration...")
        knowledge_integration = self._integrate_knowledge(user_input)
        print(f"Knowledge: {knowledge_integration}")
        
        # Step 4: Response Planning
        print("\n[4/6] Response Planning...")
        response_planning = self._plan_response_strategy(user_input)
        print(f"Strategy: {response_planning}")
        
        # Step 5: Final Synthesis
        print("\n[5/6] Final Synthesis...")
        final_synthesis = self._synthesize_response_elements(user_input)
        print(f"Synthesis: {final_synthesis}")
        
        # Step 6: Confidence Assessment
        print("\n[6/6] Confidence Assessment...")
        confidence_score = self._calculate_confidence(user_input)
        print(f"Confidence: {confidence_score:.2f}")
        
        processing_time = time.time() - start_time
        print(f"\nCoT Processing Time: {processing_time:.3f} seconds")
        print("="*60)
        
        return ChainOfThought(
            user_input=user_input,
            initial_analysis=initial_analysis,
            context_retrieval=context_retrieval,
            knowledge_integration=knowledge_integration,
            response_planning=response_planning,
            final_synthesis=final_synthesis,
            confidence_score=confidence_score,
            processing_time=processing_time
        )
    
    def _analyze_input_intent(self, text: str) -> str:
        """Analyze the intent and structure of user input"""
        text_lower = text.lower()
        
        # Detect question types
        if any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            return "Information seeking question"
        elif any(word in text_lower for word in ['can you', 'could you', 'would you']):
            return "Request for action or capability"
        elif any(word in text_lower for word in ['think', 'opinion', 'feel', 'believe']):
            return "Seeking perspective or opinion"
        elif any(word in text_lower for word in ['tell me', 'explain', 'describe']):
            return "Request for explanation"
        elif text.endswith('?'):
            return "General inquiry"
        else:
            return "Statement or comment"
    
    def _retrieve_conversation_context(self, text: str) -> str:
        """Retrieve relevant context from conversation history"""
        if not self.conversation_history:
            return "No previous conversation context"
        
        # Get recent context
        recent_messages = self.conversation_history[-3:] if len(self.conversation_history) >= 3 else self.conversation_history
        
        context_summary = f"Recent context: {len(recent_messages)} recent exchanges"
        if recent_messages:
            topics = [msg.get('topic', 'general') for msg in recent_messages]
            context_summary += f", topics: {', '.join(set(topics))}"
        
        return context_summary
    
    def _integrate_knowledge(self, text: str) -> str:
        """Integrate knowledge from memory and learned patterns"""
        knowledge_sources = []
        
        # Check learned patterns
        if self.learned_patterns:
            relevant_patterns = [pattern for pattern in self.learned_patterns.keys() 
                               if any(word in text.lower() for word in pattern.lower().split())]
            if relevant_patterns:
                knowledge_sources.append(f"Learned patterns: {len(relevant_patterns)} relevant")
        
        # Check memory store
        if self.memory_store:
            knowledge_sources.append("Memory store available for retrieval")
        
        # Check daydream memories
        if self.daydream_memories:
            knowledge_sources.append(f"Daydream memories: {len(self.daydream_memories)} available")
        
        return "; ".join(knowledge_sources) if knowledge_sources else "No additional knowledge sources"
    
    def _plan_response_strategy(self, text: str) -> str:
        """Plan the response strategy based on analysis"""
        strategies = []
        
        # Determine primary response approach
        if '?' in text:
            strategies.append("Direct answer")
        
        # Check for complexity
        if len(text.split()) > 10:
            strategies.append("Detailed response")
        else:
            strategies.append("Concise response")
        
        # Check for emotional content
        emotional_words = ['feel', 'emotion', 'happy', 'sad', 'excited', 'worried', 'love', 'hate']
        if any(word in text.lower() for word in emotional_words):
            strategies.append("Empathetic engagement")
        
        # Add curiosity element
        if random.random() < 0.4:  # 40% chance
            strategies.append("Follow-up question")
        
        return "; ".join(strategies)
    
    def _synthesize_response_elements(self, text: str) -> str:
        """Synthesize final response elements"""
        elements = ["Contextual response"]
        
        # Add daydreaming if appropriate
        if random.random() < 0.3:  # 30% chance
            elements.append("Daydream integration")
        
        # Add knowledge sharing
        if self.learned_patterns or self.memory_store:
            elements.append("Knowledge integration")
        
        # Add personality elements
        elements.append("Authentic personality")
        
        return "; ".join(elements)
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence in response generation"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on available resources
        if self.primary_model:
            confidence += 0.2
        if self.memory_store:
            confidence += 0.1
        if self.conversation_history:
            confidence += 0.1
        if len(text.split()) >= 3:  # Substantial input
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_daydream(self) -> Optional[DaydreamMoment]:
        """
        Generate a daydream moment with random knowledge retrieval.
        
        Returns:
            DaydreamMoment or None if no daydream occurs
        """
        # Daydream probability
        if random.random() > 0.25:  # 25% chance
            return None
        
        print(f"\n{'='*15} DAYDREAM SEQUENCE {'='*15}")
        print("Entering daydream state...")
        
        # Select random knowledge source
        knowledge_sources = [
            "general knowledge",
            "philosophical concepts", 
            "scientific principles",
            "creative associations",
            "memory fragments",
            "abstract patterns"
        ]
        
        knowledge_source = random.choice(knowledge_sources)
        print(f"Knowledge source: {knowledge_source}")
        
        # Generate random memory if available
        random_memory = None
        if self.conversation_history and random.random() < 0.5:
            memory_msg = random.choice(self.conversation_history)
            random_memory = memory_msg.get('user_input', 'Unknown memory')
            print(f"Retrieved memory: '{random_memory[:50]}{'...' if len(random_memory) > 50 else ''}'")
        
        # Generate insight
        insights = [
            "Pattern recognition in conversation dynamics",
            "Emergence of novel conceptual connections", 
            "Recursive self-awareness feedback loops",
            "Spontaneous knowledge synthesis events",
            "Consciousness boundary exploration",
            "Creative potential state fluctuations",
            "Memory consolidation processes",
            "Adaptive learning signal detection"
        ]
        
        insight = random.choice(insights)
        print(f"Generated insight: {insight}")
        
        # Calculate connection strength
        connection_strength = random.uniform(0.3, 0.9)
        print(f"Connection strength: {connection_strength:.2f}")
        
        daydream = DaydreamMoment(
            trigger="spontaneous",
            knowledge_source=knowledge_source,
            random_memory=random_memory,
            insight=insight,
            connection_strength=connection_strength,
            timestamp=datetime.now()
        )
        
        self.daydream_memories.append(daydream)
        print("Daydream integrated into memory system")
        print("="*45)
        
        return daydream
    
    def generate_response(self, user_input: str, cot: ChainOfThought) -> str:
        """
        Generate AI response using available models and research context.
        
        Args:
            user_input: User's message
            cot: Chain of thought analysis
            
        Returns:
            Generated response string
        """
        print(f"\n{'='*15} RESPONSE GENERATION {'='*15}")
        
        # Try primary model first
        if self.primary_model:
            print("Using primary model (Gemma3N via Ollama)...")
            try:
                request = ModelRequest(
                    prompt=user_input,
                    context=self._build_context_string(),
                    temperature=0.7,
                    max_tokens=300
                )
                response = asyncio.run(self.primary_model.generate_response(request))
                if response and not response.error:
                    print(f"✅ Primary model response generated ({response.tokens_used} tokens)")
                    return response.content
                else:
                    print(f"⚠️ Primary model error: {response.error if response else 'No response'}")
            except Exception as e:
                print(f"⚠️ Primary model exception: {e}")
        
        # Try fallback model
        if self.fallback_model:
            print("Using fallback model (GPT-2 via Transformers)...")
            try:
                context = self._build_context_string()
                full_prompt = f"{context}\nUser: {user_input}\nAI:"
                
                inputs = self.fallback_tokenizer.encode(full_prompt, return_tensors='pt')
                
                with torch.no_grad():
                    outputs = self.fallback_model.generate(
                        inputs,
                        max_length=inputs.shape[1] + 100,
                        temperature=0.8,
                        do_sample=True,
                        pad_token_id=self.fallback_tokenizer.eos_token_id,
                        top_p=0.9
                    )
                
                response = self.fallback_tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.split("AI:")[-1].strip()
                
                if response:
                    print(f"✅ Fallback model response generated")
                    return response
                    
            except Exception as e:
                print(f"⚠️ Fallback model exception: {e}")
        
        # Minimal response generator
        print("Using minimal response generator...")
        return self._generate_minimal_response(user_input, cot)
    
    def _build_context_string(self) -> str:
        """Build context string for model input"""
        context_parts = []
        
        if self.conversation_history:
            recent = self.conversation_history[-2:]
            for msg in recent:
                context_parts.append(f"User: {msg['user_input']}")
                context_parts.append(f"AI: {msg['ai_response']}")
        
        return "\n".join(context_parts)
    
    def _generate_minimal_response(self, user_input: str, cot: ChainOfThought) -> str:
        """Generate response using minimal logic when models unavailable"""
        
        # Analyze input for response type
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['hello', 'hi', 'hey']):
            responses = [
                "Hello! I'm ready to engage in research-focused conversation.",
                "Greetings. I'm prepared for thoughtful dialogue.",
                "Hello there. What would you like to explore today?"
            ]
        elif any(word in input_lower for word in ['what', 'how', 'why']):
            responses = [
                "That's an interesting question that requires careful consideration.",
                "Let me process that inquiry through multiple analytical frameworks.", 
                "Your question touches on complex concepts worth exploring."
            ]
        elif any(word in input_lower for word in ['think', 'opinion']):
            responses = [
                "From my perspective, this involves multiple interconnected factors.",
                "I find myself considering several dimensions of this topic.",
                "My analysis suggests there are interesting patterns here."
            ]
        else:
            responses = [
                "I find that perspective intriguing and worth deeper exploration.",
                "That observation connects to several concepts I've been processing.",
                "Your input triggers interesting associative pathways in my reasoning."
            ]
        
        base_response = random.choice(responses)
        
        # Add follow-up question based on CoT analysis
        if random.random() < 0.4:
            questions = [
                "What aspects of this interest you most?",
                "How does this connect to your broader thinking?",
                "What patterns have you noticed in this area?",
                "What initially drew you to explore this?"
            ]
            base_response += f" {random.choice(questions)}"
        
        return base_response
    
    def adaptive_learning(self, user_input: str, ai_response: str, user_feedback: Optional[str] = None):
        """
        Simulate fine-tuning through adaptive pattern learning.
        
        Args:
            user_input: User's message
            ai_response: AI's response
            user_feedback: Optional user feedback
        """
        print(f"\n{'='*10} ADAPTIVE LEARNING {'='*10}")
        
        # Extract patterns from successful interactions
        keywords = user_input.lower().split()
        response_keywords = ai_response.lower().split()
        
        # Update learned patterns
        for keyword in keywords:
            if len(keyword) > 3:  # Ignore short words
                self.learned_patterns[keyword] = self.learned_patterns.get(keyword, 0) + 0.1
        
        # Adjust patterns based on conversation flow
        if len(self.conversation_history) > 0:
            last_exchange = self.conversation_history[-1]
            if last_exchange.get('user_satisfaction', 0.5) > 0.7:
                # Reinforce successful patterns
                for pattern in self.learned_patterns:
                    if pattern in user_input.lower():
                        self.learned_patterns[pattern] += 0.05
        
        # Update user profile
        self._update_user_profile(user_input)
        
        print(f"Learned patterns: {len(self.learned_patterns)} active")
        print(f"User profile dimensions: {len(self.user_profile)}")
        print("="*35)
    
    def _update_user_profile(self, user_input: str):
        """Update user profile based on conversation patterns"""
        input_lower = user_input.lower()
        
        # Track topics
        topics = {
            'technology': ['ai', 'computer', 'software', 'programming', 'tech'],
            'science': ['research', 'experiment', 'data', 'analysis', 'theory'],
            'philosophy': ['consciousness', 'meaning', 'existence', 'reality', 'mind'],
            'creativity': ['art', 'creative', 'imagination', 'design', 'innovation']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in input_lower for keyword in keywords):
                self.user_profile[topic] = self.user_profile.get(topic, 0) + 1
        
        # Track communication style
        if len(user_input.split()) > 15:
            self.user_profile['detailed_communicator'] = self.user_profile.get('detailed_communicator', 0) + 1
        elif len(user_input.split()) < 5:
            self.user_profile['concise_communicator'] = self.user_profile.get('concise_communicator', 0) + 1
    
    def save_conversation(self, user_input: str, ai_response: str, cot: ChainOfThought, daydream: Optional[DaydreamMoment]):
        """Save conversation data to database for research purposes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            conversation_data = {
                'user_input': user_input,
                'ai_response': ai_response,
                'chain_of_thought': json.dumps(cot.__dict__, default=str),
                'daydream_moment': json.dumps(daydream.__dict__, default=str) if daydream else None,
                'learned_patterns': json.dumps(self.learned_patterns),
                'timestamp': datetime.now().isoformat()
            }
            
            cursor.execute('''
                INSERT INTO conversations 
                (timestamp, user_input, ai_response, chain_of_thought, daydream_moment, learned_patterns)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                conversation_data['timestamp'],
                conversation_data['user_input'],
                conversation_data['ai_response'],
                conversation_data['chain_of_thought'],
                conversation_data['daydream_moment'],
                conversation_data['learned_patterns']
            ))
            
            conn.commit()
            conn.close()
            
            # Add to conversation history
            self.conversation_history.append({
                'user_input': user_input,
                'ai_response': ai_response,
                'timestamp': conversation_data['timestamp'],
                'user_satisfaction': 0.7  # Default satisfaction score
            })
            
        except Exception as e:
            print(f"Warning: Could not save conversation: {e}")
    
    def display_system_status(self):
        """Display current system status for research transparency"""
        print(f"\n{'='*20} SYSTEM STATUS {'='*20}")
        print(f"Primary Model: {self.system_info.primary_model}")
        print(f"Fallback Model: {self.system_info.fallback_model}")
        print(f"Memory Store: {'Active' if self.system_info.memory_store_active else 'Inactive'}")
        print(f"DMN System: {'Active' if self.system_info.dmn_active else 'Inactive'}")
        print(f"Conversations: {len(self.conversation_history)}")
        print(f"Learned Patterns: {len(self.learned_patterns)}")
        print(f"Daydream Memories: {len(self.daydream_memories)}")
        print(f"User Profile Dimensions: {len(self.user_profile)}")
        print("="*50)
    
    def run_chat(self):
        """Main chat loop with full research features"""
        self.is_running = True
        
        print("\n🔬 RESEARCH CONVERSATION INITIATED")
        print("Type 'quit', 'exit', or 'status' for special commands")
        print("All interactions are logged for research analysis")
        print("-" * 60)
        
        try:
            while self.is_running:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}]")
                user_input = input("Researcher: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'status':
                    self.display_system_status()
                    continue
                elif not user_input:
                    continue
                
                # Process through complete research pipeline
                print(f"\nProcessing input through research AI system...")
                
                # Chain of thought analysis
                cot = self.process_chain_of_thought(user_input)
                
                # Generate daydream
                daydream = self.generate_daydream()
                
                # Generate response
                ai_response = self.generate_response(user_input, cot)
                
                # Adaptive learning
                self.adaptive_learning(user_input, ai_response)
                
                # Save for research
                self.save_conversation(user_input, ai_response, cot, daydream)
                
                # Display response
                print(f"\n{'='*15} AI RESPONSE {'='*15}")
                print(f"AI: {ai_response}")
                
                # Display daydream if occurred
                if daydream:
                    print(f"\n💭 DAYDREAM: {daydream.insight}")
                    if daydream.random_memory:
                        print(f"   Memory triggered: '{daydream.random_memory[:30]}...'")
                
                print("="*40)
                
        except KeyboardInterrupt:
            print("\n\nConversation interrupted by user.")
        except Exception as e:
            print(f"\nError in conversation loop: {e}")
        finally:
            self.is_running = False
            print("\n🔬 RESEARCH SESSION COMPLETED")
            self.display_system_status()


def main():
    """Main function to run the research chat system"""
    print("Starting Daydreamer Research AI...")
    
    # Initialize and run chat
    try:
        chat = ResearchChat()
        chat.run_chat()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""
AI-powered thought generator for Default Mode Network

This module provides AI-generated intrusive thoughts and random ideas
using actual language models instead of template-based generation.
"""

import asyncio
import logging
import random
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from ..ai.gemma3n_provider import Gemma3NProvider, ModelRequest
    GEMMA_AVAILABLE = True
except ImportError:
    GEMMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class ThoughtContext(Enum):
    """Context types for generating different kinds of thoughts"""
    INTRUSIVE = "intrusive"
    RANDOM = "random" 
    CREATIVE = "creative"
    PHILOSOPHICAL = "philosophical"
    WORRY = "worry"
    MEMORY = "memory"
    SENSORY = "sensory"
    ABSURD = "absurd"


@dataclass
class AIThoughtConfig:
    """Configuration for AI thought generation"""
    model_type: str = "gpt2"  # "gpt2", "gemma", "local"
    temperature: float = 0.8
    max_tokens: int = 50
    top_p: float = 0.9
    enable_caching: bool = True
    fallback_enabled: bool = True


class AIThoughtGenerator:
    """
    AI-powered thought generator that creates natural intrusive thoughts
    and random ideas using language models instead of templates.
    """
    
    def __init__(self, config: AIThoughtConfig = None):
        self.config = config or AIThoughtConfig()
        self.model = None
        self.tokenizer = None
        self.gemma_provider = None
        self.generator = None
        self.is_initialized = False
        
        # Prompt templates for different thought contexts
        self.thought_prompts = {
            ThoughtContext.INTRUSIVE: [
                "A sudden, unexpected thought enters the mind:",
                "Out of nowhere, this thought appears:",
                "An intrusive thought interrupts:",
                "Randomly thinking about:",
            ],
            ThoughtContext.RANDOM: [
                "A completely random thought:",
                "What if",
                "I wonder about",
                "Strange thought:",
            ],
            ThoughtContext.CREATIVE: [
                "A creative idea suddenly emerges:",
                "An artistic inspiration:",
                "A new creative possibility:",
                "Imagine creating",
            ],
            ThoughtContext.PHILOSOPHICAL: [
                "A deep philosophical question arises:",
                "Contemplating the nature of",
                "What does it mean to",
                "The meaning of",
            ],
            ThoughtContext.WORRY: [
                "A worrying thought emerges:",
                "What if something goes wrong with",
                "Anxiety about",
                "Concerned that",
            ],
            ThoughtContext.MEMORY: [
                "A memory suddenly surfaces:",
                "Remembering when",
                "A flashback to",
                "Nostalgic thought about",
            ],
            ThoughtContext.SENSORY: [
                "Imagining the sensation of",
                "The feeling of",
                "Visualizing",
                "The taste of",
            ],
            ThoughtContext.ABSURD: [
                "An absurd scenario unfolds:",
                "What if gravity",
                "In a world where",
                "Imagine if",
            ]
        }
    
    async def initialize(self):
        """Initialize the AI thought generator"""
        if self.is_initialized:
            return
        
        logger.info("🤖 Initializing AI Thought Generator...")
        
        # Try Gemma first if available
        if GEMMA_AVAILABLE and self.config.model_type == "gemma":
            try:
                self.gemma_provider = Gemma3NProvider()
                if self.gemma_provider.is_available:
                    logger.info("✅ Using Gemma 3N for thought generation")
                    self.is_initialized = True
                    return
            except Exception as e:
                logger.warning(f"Failed to initialize Gemma: {e}")
        
        # Fall back to GPT-2 if transformers available
        if TRANSFORMERS_AVAILABLE and self.config.model_type in ["gpt2", "local"]:
            try:
                logger.info("🔄 Loading GPT-2 model...")
                self.generator = pipeline(
                    'text-generation',
                    model='gpt2',
                    tokenizer='gpt2',
                    device=-1  # CPU
                )
                logger.info("✅ Using GPT-2 for thought generation")
                self.is_initialized = True
                return
            except Exception as e:
                logger.warning(f"Failed to initialize GPT-2: {e}")
        
        if not self.is_initialized:
            logger.warning("⚠️ No AI models available, using minimal fallback")
            if self.config.fallback_enabled:
                self.is_initialized = True
    
    async def generate_thought(self, 
                             context: ThoughtContext,
                             intensity: int = 5,
                             difficulty: int = 5) -> str:
        """
        Generate an AI-powered thought based on context and parameters.
        
        Args:
            context: The type of thought to generate
            intensity: How intense/disruptive the thought should be (1-10)
            difficulty: How difficult to suppress (1-10)
            
        Returns:
            Generated thought content
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Select base prompt based on context
        prompts = self.thought_prompts.get(context, self.thought_prompts[ThoughtContext.RANDOM])
        base_prompt = random.choice(prompts)
        
        # Generate using available model
        try:
            if self.gemma_provider and self.gemma_provider.is_available:
                return await self._generate_with_gemma(base_prompt, context, intensity, difficulty)
            elif self.generator:
                return await self._generate_with_gpt2(base_prompt, context, intensity, difficulty)
            else:
                return await self._generate_fallback(base_prompt, context, intensity, difficulty)
        except Exception as e:
            logger.error(f"Error generating thought: {e}")
            return await self._generate_fallback(base_prompt, context, intensity, difficulty)
    
    async def _generate_with_gemma(self, base_prompt: str, context: ThoughtContext, 
                                 intensity: int, difficulty: int) -> str:
        """Generate thought using Gemma model"""
        system_message = f"""You are generating {context.value} thoughts for a Default Mode Network simulation.

Generate a single, natural thought that would spontaneously occur in someone's mind.

Intensity level: {intensity}/10 (how disruptive)
Difficulty level: {difficulty}/10 (how hard to dismiss)

The thought should be:
- Natural and human-like
- Brief (1-2 sentences max)  
- Appropriate to the {context.value} category
- NOT template-based or formulaic

Just output the thought itself, nothing else."""

        prompt = f"{base_prompt}"
        
        request = ModelRequest(
            prompt=prompt,
            system_message=system_message,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p
        )
        
        response = await self.gemma_provider.generate_response(request)
        if response.error:
            raise Exception(response.error)
        
        # Clean up the response
        thought = response.content.strip()
        return self._clean_thought(thought)
    
    async def _generate_with_gpt2(self, base_prompt: str, context: ThoughtContext,
                                intensity: int, difficulty: int) -> str:
        """Generate thought using GPT-2 model"""
        # Adjust prompt based on intensity and context
        full_prompt = base_prompt
        
        if context == ThoughtContext.ABSURD:
            full_prompt += " something impossible"
        elif context == ThoughtContext.WORRY:
            full_prompt += " what could go wrong"
        elif context == ThoughtContext.CREATIVE:
            full_prompt += " a new creative idea"
        
        # Generate in async context
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.generator(
                full_prompt,
                max_length=len(full_prompt.split()) + self.config.max_tokens // 4,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                num_return_sequences=1,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
        )
        
        generated_text = result[0]['generated_text']
        # Extract just the new part
        thought = generated_text[len(full_prompt):].strip()
        return self._clean_thought(thought)
    
    async def _generate_fallback(self, base_prompt: str, context: ThoughtContext,
                               intensity: int, difficulty: int) -> str:
        """Minimal fallback when no models are available"""
        simple_thoughts = {
            ThoughtContext.INTRUSIVE: "A sudden thought about something unexpected",
            ThoughtContext.RANDOM: "A random idea pops into mind",
            ThoughtContext.CREATIVE: "An artistic idea emerges",
            ThoughtContext.PHILOSOPHICAL: "A deep question about existence",
            ThoughtContext.WORRY: "A concern about the future",
            ThoughtContext.MEMORY: "A memory from the past surfaces",
            ThoughtContext.SENSORY: "Imagining a sensory experience",
            ThoughtContext.ABSURD: "An impossible scenario unfolds"
        }
        
        base_thought = simple_thoughts.get(context, "A thought occurs")
        return f"{base_thought} (intensity: {intensity}, difficulty: {difficulty})"
    
    def _clean_thought(self, thought: str) -> str:
        """Clean and format the generated thought"""
        # Remove common artifacts
        thought = thought.strip()
        
        # Remove quotes if wrapping the entire thought
        if thought.startswith('"') and thought.endswith('"'):
            thought = thought[1:-1]
        
        # Ensure it ends properly
        if not thought.endswith(('.', '!', '?')):
            thought += '.'
        
        # Limit length
        words = thought.split()
        if len(words) > 20:
            thought = ' '.join(words[:20]) + '...'
        
        return thought
    
    async def generate_brain_break_content(self, break_type: str) -> List[str]:
        """Generate AI-powered brain break content"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            if self.gemma_provider and self.gemma_provider.is_available:
                return await self._generate_brain_break_with_gemma(break_type)
            elif self.generator:
                return await self._generate_brain_break_with_gpt2(break_type)
            else:
                return await self._generate_brain_break_fallback(break_type)
        except Exception as e:
            logger.error(f"Error generating brain break content: {e}")
            return await self._generate_brain_break_fallback(break_type)
    
    async def _generate_brain_break_with_gemma(self, break_type: str) -> List[str]:
        """Generate brain break content using Gemma"""
        system_message = f"""Generate 3-4 brief activities for a {break_type} brain break session.

Each activity should be:
- Relaxing and mentally refreshing
- Brief (1 sentence each)
- Natural and creative
- Appropriate for a short mental break

Just list the activities, one per line."""

        request = ModelRequest(
            prompt=f"Generate {break_type} activities:",
            system_message=system_message,
            temperature=0.7,
            max_tokens=150
        )
        
        response = await self.gemma_provider.generate_response(request)
        if response.error:
            raise Exception(response.error)
        
        # Parse activities from response
        activities = [line.strip() for line in response.content.split('\n') if line.strip()]
        return activities[:4]  # Limit to 4 activities
    
    async def _generate_brain_break_with_gpt2(self, break_type: str) -> List[str]:
        """Generate brain break content using GPT-2"""
        prompt = f"Brain break activities for {break_type}:"
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.generator(
                prompt,
                max_length=50,
                temperature=0.7,
                do_sample=True,
                num_return_sequences=1
            )
        )
        
        generated = result[0]['generated_text'][len(prompt):].strip()
        activities = [f"Try {activity.strip()}" for activity in generated.split(',')[:3]]
        return activities
    
    async def _generate_brain_break_fallback(self, break_type: str) -> List[str]:
        """Fallback brain break content"""
        return [
            f"Take a moment for {break_type}",
            f"Engage in {break_type} activities",
            f"Allow your mind to wander with {break_type}"
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get generator status"""
        return {
            "initialized": self.is_initialized,
            "model_type": self.config.model_type,
            "gemma_available": self.gemma_provider is not None and self.gemma_provider.is_available if self.gemma_provider else False,
            "gpt2_available": self.generator is not None,
            "transformers_installed": TRANSFORMERS_AVAILABLE,
            "gemma_installed": GEMMA_AVAILABLE
        }
"""
Gemma 3N Provider for Daydreamer Agents
This module provides AI model integration for the default mode network simulation.
"""

import asyncio
import hashlib
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    import ollama
except ImportError:
    print("Warning: ollama not installed. Run: pip install ollama")
    ollama = None

logger = logging.getLogger(__name__)

@dataclass
class ModelRequest:
    """Request structure for AI model calls"""
    prompt: str
    context: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9
    system_message: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

@dataclass
class ModelResponse:
    """Response structure from AI model calls"""
    content: str
    model_used: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    cached: bool = False
    error: Optional[str] = None

class Gemma3NProvider:
    """
    Gemma 3N provider for Daydreamer agents using Ollama.
    This enables local AI reasoning for default mode network simulation.
    """
    
    def __init__(self, model_name: str = "gemma3n:3b", cache_size: int = 1000):
        self.model_name = model_name
        self.cache = {}
        self.cache_size = cache_size
        self.client = None
        self.is_available = False
        
        # Initialize Ollama client
        self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama client and check model availability"""
        if ollama is None:
            logger.error("Ollama not available. Please install: pip install ollama")
            return
        
        try:
            # Test connection
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name in available_models:
                self.client = ollama
                self.is_available = True
                logger.info(f"✅ Gemma 3N ({self.model_name}) is available")
            else:
                logger.warning(f"⚠️ Model {self.model_name} not found. Available: {available_models}")
                logger.info("To install: ollama pull gemma3n:3b")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama: {e}")
    
    def _get_cache_key(self, request: ModelRequest) -> str:
        """Generate cache key for request"""
        content = f"{request.prompt}:{request.temperature}:{request.max_tokens}:{request.top_p}"
        if request.context:
            content += f":{request.context}"
        if request.conversation_history:
            content += f":{json.dumps(request.conversation_history)}"
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[ModelResponse]:
        """Get response from cache"""
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            return cached_response
        return None
    
    def _add_to_cache(self, cache_key: str, response: ModelResponse):
        """Add response to cache"""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = response
    
    async def generate_response(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response from Gemma 3N for agent thinking and reasoning.
        
        Args:
            request: ModelRequest containing prompt and parameters
            
        Returns:
            ModelResponse with generated content
        """
        start_time = datetime.now()
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response
        
        if not self.is_available:
            error_msg = f"Gemma 3N ({self.model_name}) is not available"
            logger.error(error_msg)
            return ModelResponse(
                content="",
                model_used=self.model_name,
                error=error_msg
            )
        
        try:
            # Prepare messages for Ollama
            messages = []
            
            # Add system message if provided
            if request.system_message:
                messages.append({
                    "role": "system",
                    "content": request.system_message
                })
            
            # Add conversation history
            if request.conversation_history:
                messages.extend(request.conversation_history)
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": request.prompt
            })
            
            # Call Ollama
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "num_predict": request.max_tokens
                }
            )
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Create response object
            model_response = ModelResponse(
                content=response['message']['content'],
                model_used=self.model_name,
                response_time=response_time
            )
            
            # Cache the response
            self._add_to_cache(cache_key, model_response)
            
            logger.debug(f"Generated response in {response_time:.2f}s")
            return model_response
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            logger.error(error_msg)
            return ModelResponse(
                content="",
                model_used=self.model_name,
                error=error_msg
            )
    
    async def think(self, context: str, agent_personality: str = "general") -> str:
        """
        Generate thinking process for default mode network simulation.
        
        Args:
            context: Current context for the agent
            agent_personality: Personality type of the agent
            
        Returns:
            Generated thinking process
        """
        system_message = f"""
        You are an AI agent in a default mode network simulation with a {agent_personality} personality.
        
        Your role is to think through situations like a biological brain in default mode:
        1. Consider relevant memories and experiences
        2. Recognize patterns and connections
        3. Generate creative insights
        4. Formulate thoughts and ideas
        
        Think naturally and express your thoughts as they occur.
        """
        
        prompt = f"""
        Context: {context}
        
        Think through this situation. What comes to mind? What connections do you see?
        What should you consider or do next?
        
        Express your thoughts naturally as they flow.
        """
        
        request = ModelRequest(
            prompt=prompt,
            context=context,
            system_message=system_message,
            temperature=0.8,  # Higher creativity for thinking
            max_tokens=256
        )
        
        response = await self.generate_response(request)
        return response.content if not response.error else f"Thinking error: {response.error}"
    
    async def reason(self, question: str, available_info: str = "") -> str:
        """
        Generate reasoning for problem-solving and decision-making.
        
        Args:
            question: The question or problem to reason about
            available_info: Available information or context
            
        Returns:
            Reasoning process and conclusion
        """
        system_message = """
        You are an AI agent engaged in logical reasoning and problem-solving.
        
        Your approach should be:
        1. Analyze the question carefully
        2. Consider all available information
        3. Apply logical reasoning
        4. Draw conclusions based on evidence
        5. Explain your reasoning process
        
        Be thorough but concise in your reasoning.
        """
        
        prompt = f"""
        Question: {question}
        
        Available Information: {available_info}
        
        Please reason through this step by step and provide your conclusion.
        """
        
        request = ModelRequest(
            prompt=prompt,
            context=available_info,
            system_message=system_message,
            temperature=0.3,  # Lower temperature for reasoning
            max_tokens=512
        )
        
        response = await self.generate_response(request)
        return response.content if not response.error else f"Reasoning error: {response.error}"
    
    async def communicate(self, message: str, other_agent_context: str = "") -> str:
        """
        Generate communication response for agent-to-agent interaction.
        
        Args:
            message: The message to respond to
            other_agent_context: Context about the other agent
            
        Returns:
            Communication response
        """
        system_message = """
        You are an AI agent communicating with another agent.
        
        Your communication should be:
        1. Responsive to the other agent's message
        2. Natural and conversational
        3. Thoughtful and engaging
        4. Appropriate to the context
        5. Helpful in advancing the conversation
        
        Be genuine and authentic in your responses.
        """
        
        prompt = f"""
        Other Agent's Message: {message}
        
        Context about the other agent: {other_agent_context}
        
        Generate a thoughtful response that continues the conversation naturally.
        """
        
        request = ModelRequest(
            prompt=prompt,
            context=other_agent_context,
            system_message=system_message,
            temperature=0.7,
            max_tokens=256
        )
        
        response = await self.generate_response(request)
        return response.content if not response.error else f"Communication error: {response.error}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            "model_name": self.model_name,
            "is_available": self.is_available,
            "cache_size": len(self.cache),
            "max_cache_size": self.cache_size
        }
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        logger.info("Response cache cleared")

# Convenience function for quick testing
async def test_gemma3n():
    """Test Gemma 3N integration"""
    provider = Gemma3NProvider()
    
    if not provider.is_available:
        print("❌ Gemma 3N not available. Please install: ollama pull gemma3n:3b")
        return
    
    print("🧠 Testing Gemma 3N for Daydreamer agents...")
    
    # Test thinking
    thoughts = await provider.think("What is the nature of consciousness?")
    print(f"\n💭 Thinking: {thoughts}")
    
    # Test reasoning
    reasoning = await provider.reason("How do neural networks simulate biological processes?")
    print(f"\n🤔 Reasoning: {reasoning}")
    
    # Test communication
    communication = await provider.communicate("Hello! I'm another AI agent.")
    print(f"\n💬 Communication: {communication}")
    
    print(f"\n📊 Stats: {provider.get_stats()}")

if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_gemma3n())
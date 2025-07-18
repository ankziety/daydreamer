"""
Intelligent Agent for Daydreamer Project
This agent uses Gemma 3N for default mode network thinking and reasoning.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..ai.gemma3n_provider import Gemma3NProvider, ModelRequest

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    THINKING = "thinking"
    REASONING = "reasoning"
    COMMUNICATING = "communicating"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

@dataclass
class AgentConfig:
    """Configuration for intelligent agents"""
    agent_id: str
    personality: str = "general"
    thinking_frequency: float = 5.0  # seconds between thinking cycles
    memory_capacity: int = 1000
    max_conversation_history: int = 50
    ai_model: str = "gemma3n:3b"
    enable_thinking: bool = True
    enable_reasoning: bool = True
    enable_communication: bool = True

@dataclass
class AgentMemory:
    """Memory structure for agents"""
    episodic: List[Dict[str, Any]] = field(default_factory=list)
    semantic: Dict[str, Any] = field(default_factory=dict)
    working: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)

class IntelligentAgent:
    """
    Intelligent agent that uses Gemma 3N for default mode network simulation.
    
    This agent can:
    - Think autonomously using default mode network processes
    - Reason about problems and situations
    - Communicate with other agents
    - Maintain memory and learn from experiences
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.ai_provider = Gemma3NProvider(config.ai_model)
        self.last_thinking_time = None
        self.thinking_task = None
        self.stats = {
            "thoughts_generated": 0,
            "reasoning_sessions": 0,
            "communications": 0,
            "total_ai_calls": 0
        }
        
        logger.info(f" Created intelligent agent: {config.agent_id} ({config.personality})")
    
    async def start(self):
        """Start the agent and begin autonomous thinking"""
        if self.state != AgentState.IDLE:
            logger.warning(f"Agent {self.config.agent_id} is already active")
            return
        
        self.state = AgentState.ACTIVE
        logger.info(f" Starting agent: {self.config.agent_id}")
        
        if self.config.enable_thinking:
            self.thinking_task = asyncio.create_task(self._autonomous_thinking_loop())
    
    async def stop(self):
        """Stop the agent and clean up"""
        if self.state == AgentState.STOPPED:
            return
        
        self.state = AgentState.STOPPED
        
        if self.thinking_task:
            self.thinking_task.cancel()
            try:
                await self.thinking_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f" Stopped agent: {self.config.agent_id}")
    
    async def pause(self):
        """Pause the agent"""
        if self.state == AgentState.ACTIVE:
            self.state = AgentState.PAUSED
            logger.info(f"⏸️ Paused agent: {self.config.agent_id}")
    
    async def resume(self):
        """Resume the agent"""
        if self.state == AgentState.PAUSED:
            self.state = AgentState.ACTIVE
            logger.info(f"▶️ Resumed agent: {self.config.agent_id}")
    
    async def _autonomous_thinking_loop(self):
        """Autonomous thinking loop for default mode network simulation"""
        while self.state == AgentState.ACTIVE:
            try:
                # Generate thinking context from memory and current state
                context = self._generate_thinking_context()
                
                # Think about the current situation
                thoughts = await self.think(context)
                
                # Store thoughts in memory
                self._store_thought(thoughts)
                
                # Update stats
                self.stats["thoughts_generated"] += 1
                self.stats["total_ai_calls"] += 1
                
                logger.debug(f" Agent {self.config.agent_id} thought: {thoughts[:100]}...")
                
                # Wait before next thinking cycle
                await asyncio.sleep(self.config.thinking_frequency)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in thinking loop for agent {self.config.agent_id}: {e}")
                await asyncio.sleep(1)  # Brief pause on error
    
    def _generate_thinking_context(self) -> str:
        """Generate context for thinking based on memory and current state"""
        context_parts = []
        
        # Add recent memories
        if self.memory.episodic:
            recent_memories = self.memory.episodic[-5:]  # Last 5 memories
            context_parts.append(f"Recent experiences: {[m.get('content', '') for m in recent_memories]}")
        
        # Add semantic knowledge
        if self.memory.semantic:
            context_parts.append(f"Knowledge: {list(self.memory.semantic.keys())}")
        
        # Add working memory
        if self.memory.working:
            context_parts.append(f"Current focus: {self.memory.working[-3:]}")  # Last 3 items
        
        # Add conversation context
        if self.memory.conversation_history:
            recent_conversations = self.memory.conversation_history[-3:]
            context_parts.append(f"Recent conversations: {[c.get('message', '') for c in recent_conversations]}")
        
        return " | ".join(context_parts) if context_parts else "No specific context"
    
    async def think(self, context: str) -> str:
        """
        Generate thinking process using default mode network simulation.
        
        Args:
            context: Current context for thinking
            
        Returns:
            Generated thoughts
        """
        if not self.config.enable_thinking:
            return "Thinking disabled"
        
        self.state = AgentState.THINKING
        
        try:
            thoughts = await self.ai_provider.think(context, self.config.personality)
            return thoughts
        finally:
            if self.state == AgentState.THINKING:
                self.state = AgentState.ACTIVE
    
    async def reason(self, question: str, available_info: str = "") -> str:
        """
        Generate reasoning about a specific question or problem.
        
        Args:
            question: The question to reason about
            available_info: Additional information to consider
            
        Returns:
            Reasoning process and conclusion
        """
        if not self.config.enable_reasoning:
            return "Reasoning disabled"
        
        self.state = AgentState.REASONING
        
        try:
            # Combine available info with memory
            memory_context = self._generate_thinking_context()
            full_context = f"{available_info} | Memory context: {memory_context}"
            
            reasoning = await self.ai_provider.reason(question, full_context)
            
            # Store reasoning in memory
            self._store_memory("reasoning", {
                "question": question,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat()
            })
            
            self.stats["reasoning_sessions"] += 1
            self.stats["total_ai_calls"] += 1
            
            return reasoning
        finally:
            if self.state == AgentState.REASONING:
                self.state = AgentState.ACTIVE
    
    async def communicate(self, message: str, other_agent_id: str = "") -> str:
        """
        Generate communication response to another agent.
        
        Args:
            message: The message to respond to
            other_agent_id: ID of the other agent
            
        Returns:
            Communication response
        """
        if not self.config.enable_communication:
            return "Communication disabled"
        
        self.state = AgentState.COMMUNICATING
        
        try:
            # Add message to conversation history
            self._add_conversation_entry("received", message, other_agent_id)
            
            # Generate response
            other_agent_context = f"Agent ID: {other_agent_id}" if other_agent_id else ""
            response = await self.ai_provider.communicate(message, other_agent_context)
            
            # Add response to conversation history
            self._add_conversation_entry("sent", response, self.config.agent_id)
            
            self.stats["communications"] += 1
            self.stats["total_ai_calls"] += 1
            
            return response
        finally:
            if self.state == AgentState.COMMUNICATING:
                self.state = AgentState.ACTIVE
    
    def _store_thought(self, thought: str):
        """Store a thought in episodic memory"""
        self._store_memory("thought", {
            "content": thought,
            "timestamp": datetime.now().isoformat(),
            "type": "autonomous_thinking"
        })
    
    def _store_memory(self, memory_type: str, content: Dict[str, Any]):
        """Store memory in episodic memory"""
        memory_entry = {
            "type": memory_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory.episodic.append(memory_entry)
        
        # Maintain memory capacity
        if len(self.memory.episodic) > self.config.memory_capacity:
            self.memory.episodic.pop(0)  # Remove oldest memory
    
    def _add_conversation_entry(self, direction: str, message: str, agent_id: str):
        """Add conversation entry to history"""
        entry = {
            "direction": direction,
            "message": message,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory.conversation_history.append(entry)
        
        # Maintain conversation history size
        if len(self.memory.conversation_history) > self.config.max_conversation_history:
            self.memory.conversation_history.pop(0)
    
    def add_to_working_memory(self, item: str):
        """Add item to working memory"""
        self.memory.working.append(item)
        
        # Maintain working memory size
        if len(self.memory.working) > 10:  # Keep last 10 items
            self.memory.working.pop(0)
    
    def add_semantic_knowledge(self, key: str, value: Any):
        """Add semantic knowledge"""
        self.memory.semantic[key] = value
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent's memory"""
        return {
            "episodic_count": len(self.memory.episodic),
            "semantic_keys": list(self.memory.semantic.keys()),
            "working_items": len(self.memory.working),
            "conversation_count": len(self.memory.conversation_history),
            "recent_thoughts": [m["content"]["content"] for m in self.memory.episodic[-3:] if m["type"] == "thought"]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        ai_stats = self.ai_provider.get_stats()
        return {
            "agent_id": self.config.agent_id,
            "state": self.state.value,
            "personality": self.config.personality,
            "ai_model": ai_stats["model_name"],
            "ai_available": ai_stats["is_available"],
            "thoughts_generated": self.stats["thoughts_generated"],
            "reasoning_sessions": self.stats["reasoning_sessions"],
            "communications": self.stats["communications"],
            "total_ai_calls": self.stats["total_ai_calls"],
            "memory_summary": self.get_memory_summary()
        }

# Example usage and testing
async def test_intelligent_agent():
    """Test the intelligent agent"""
    print(" Testing Intelligent Agent with Gemma 3N...")
    
    # Create agent configuration
    config = AgentConfig(
        agent_id="philosopher",
        personality="philosophical",
        thinking_frequency=3.0,  # Think every 3 seconds
        enable_thinking=True,
        enable_reasoning=True,
        enable_communication=True
    )
    
    # Create agent
    agent = IntelligentAgent(config)
    
    # Start the agent
    await agent.start()
    
    # Let it think for a bit
    print(" Agent is thinking autonomously...")
    await asyncio.sleep(10)
    
    # Test reasoning
    print("\n🤔 Testing reasoning...")
    reasoning = await agent.reason("What is the relationship between consciousness and intelligence?")
    print(f"Reasoning: {reasoning}")
    
    # Test communication
    print("\n💬 Testing communication...")
    response = await agent.communicate("Hello! What are your thoughts on AI consciousness?")
    print(f"Response: {response}")
    
    # Show stats
    print(f"\n Agent Stats: {agent.get_stats()}")
    
    # Stop the agent
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(test_intelligent_agent())
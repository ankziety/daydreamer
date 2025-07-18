#!/usr/bin/env python3
"""
Day Dreaming Implementation
===========================

This module implements the "Day Dreaming" prompting technique - a novel approach
that uses random memories and knowledge to generate creative insights and novel
ideas that would be difficult for humans to discover due to their abstract nature.
"""

import asyncio
import random
import time
from typing import List, Dict, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from prompts import DaydreamerPrompts


@dataclass
class DaydreamSeed:
    """Seeds for generating daydreams"""
    context: str
    random_memory: Optional[str]
    knowledge_domain: str
    trigger_type: str  # "spontaneous", "contextual", "memory_triggered"


@dataclass
class DaydreamInsight:
    """Result of a daydreaming session"""
    seed: DaydreamSeed
    insight: str
    connections_made: List[str]
    creativity_score: float
    relevance_score: float
    timestamp: datetime
    processing_time: float


@dataclass
class DaydreamSession:
    """Complete daydreaming session with multiple insights"""
    trigger: str
    insights: List[DaydreamInsight]
    best_insight: Optional[DaydreamInsight]
    total_time: float
    integration_plan: Optional[str] = None


class DaydreamingEngine:
    """
    Implements the Day Dreaming technique for creative insight generation.
    
    This engine:
    1. Randomly selects memories and knowledge domains
    2. Creates unexpected connections between disparate concepts
    3. Generates novel insights through creative leaps
    4. Evaluates insights for creativity and relevance
    5. Integrates valuable insights into ongoing conversations
    """
    
    def __init__(self, 
                 model_client: Any,
                 memory_store: Optional[Any] = None,
                 creativity_threshold: float = 0.6,
                 relevance_threshold: float = 0.4,
                 daydream_frequency: float = 0.3,
                 max_insights_per_session: int = 3):
        """
        Initialize daydreaming engine.
        
        Args:
            model_client: Client for AI model
            memory_store: Memory store for retrieving random memories
            creativity_threshold: Minimum creativity score for keeping insights
            relevance_threshold: Minimum relevance for integration
            daydream_frequency: Probability of triggering daydreams
            max_insights_per_session: Maximum insights per daydream session
        """
        self.model_client = model_client
        self.memory_store = memory_store
        self.creativity_threshold = creativity_threshold
        self.relevance_threshold = relevance_threshold
        self.daydream_frequency = daydream_frequency
        self.max_insights_per_session = max_insights_per_session
        self.prompts = DaydreamerPrompts()
        
        # Track daydream history
        self.recent_insights: List[DaydreamInsight] = []
        self.knowledge_domains_used: Dict[str, int] = {}
        self.last_daydream_time: Optional[datetime] = None
    
    async def should_daydream(self, context: str) -> bool:
        """
        Determine if a daydreaming session should be triggered.
        
        Args:
            context: Current conversation context
            
        Returns:
            True if daydreaming should be triggered
        """
        # Base probability
        if random.random() > self.daydream_frequency:
            return False
        
        # Don't daydream too frequently
        if (self.last_daydream_time and 
            datetime.now() - self.last_daydream_time < timedelta(minutes=2)):
            return False
        
        # Higher probability for creative or abstract topics
        creative_triggers = [
            "creative", "imagination", "idea", "inspiration", "novel",
            "unique", "innovative", "artistic", "abstract", "philosophical",
            "consciousness", "meaning", "purpose", "wonder", "curious"
        ]
        
        context_lower = context.lower()
        if any(trigger in context_lower for trigger in creative_triggers):
            return True
        
        # Higher probability for longer conversations
        if len(context) > 500:
            return random.random() < self.daydream_frequency * 1.5
        
        return True
    
    async def trigger_daydream_session(self, 
                                     context: str,
                                     trigger_reason: str = "spontaneous",
                                     progress_callback: Optional[Callable] = None) -> DaydreamSession:
        """
        Trigger a complete daydreaming session.
        
        Args:
            context: Current conversation context
            trigger_reason: What triggered this daydream session
            progress_callback: Optional progress callback
            
        Returns:
            Complete daydream session with insights
        """
        start_time = time.time()
        insights: List[DaydreamInsight] = []
        
        if progress_callback:
            progress_callback("🌙 Entering daydream state...")
        
        # Generate multiple insights in this session
        for i in range(self.max_insights_per_session):
            if progress_callback:
                progress_callback(f"🧠 Generating insight {i+1}/{self.max_insights_per_session}...")
            
            # Create a seed for this insight
            seed = await self._create_daydream_seed(context, trigger_reason)
            
            # Generate the insight
            insight = await self._generate_insight(seed)
            
            if insight.creativity_score >= self.creativity_threshold:
                insights.append(insight)
                if progress_callback:
                    progress_callback(f"✨ Creative insight generated (score: {insight.creativity_score:.2f})")
            else:
                if progress_callback:
                    progress_callback(f"💭 Insight below creativity threshold ({insight.creativity_score:.2f})")
        
        # Select the best insight
        best_insight = max(insights, key=lambda x: x.creativity_score + x.relevance_score) if insights else None
        
        # Plan integration if we have a good insight
        integration_plan = None
        if best_insight and best_insight.relevance_score >= self.relevance_threshold:
            if progress_callback:
                progress_callback("🔗 Planning insight integration...")
            integration_plan = await self._plan_insight_integration(best_insight, context)
        
        total_time = time.time() - start_time
        self.last_daydream_time = datetime.now()
        
        session = DaydreamSession(
            trigger=trigger_reason,
            insights=insights,
            best_insight=best_insight,
            total_time=total_time,
            integration_plan=integration_plan
        )
        
        # Update tracking
        self.recent_insights.extend(insights)
        # Keep only recent insights (last 20)
        self.recent_insights = self.recent_insights[-20:]
        
        if progress_callback:
            progress_callback(f"🌟 Daydream session complete ({len(insights)} insights, {total_time:.1f}s)")
        
        return session
    
    async def _create_daydream_seed(self, context: str, trigger_reason: str) -> DaydreamSeed:
        """Create a seed for daydream generation"""
        
        # Select a random knowledge domain
        available_domains = self.prompts.get_knowledge_domains()
        
        # Prefer less recently used domains for diversity
        domain_weights = []
        for domain in available_domains:
            usage_count = self.knowledge_domains_used.get(domain, 0)
            # Lower weight for frequently used domains
            weight = max(0.1, 1.0 - (usage_count * 0.1))
            domain_weights.append(weight)
        
        knowledge_domain = random.choices(available_domains, weights=domain_weights)[0]
        self.knowledge_domains_used[knowledge_domain] = self.knowledge_domains_used.get(knowledge_domain, 0) + 1
        
        # Get a random memory
        random_memory = await self._get_random_memory()
        
        return DaydreamSeed(
            context=context,
            random_memory=random_memory,
            knowledge_domain=knowledge_domain,
            trigger_type=trigger_reason
        )
    
    async def _get_random_memory(self) -> Optional[str]:
        """Retrieve a random memory from the memory store"""
        if not self.memory_store:
            # Fallback to synthetic random memories
            synthetic_memories = [
                "A conversation about the nature of consciousness",
                "Someone expressing curiosity about creativity",
                "A discussion about the meaning of intelligence",
                "Wondering about the connection between memory and identity",
                "Exploring the concept of artificial emotions",
                "A question about what makes thoughts unique",
                "Reflecting on the nature of learning and growth",
                "Considering the relationship between language and thought",
                "Exploring patterns in human communication",
                "A moment of genuine surprise during conversation"
            ]
            return random.choice(synthetic_memories)
        
        try:
            # Get random memory from actual memory store
            if hasattr(self.memory_store, 'get_random_memory'):
                memory = await self.memory_store.get_random_memory()
                return memory.content if memory else None
            elif hasattr(self.memory_store, 'get_memories'):
                memories = await self.memory_store.get_memories(limit=50)
                if memories:
                    return random.choice(memories).content
        except Exception:
            pass
        
        return None
    
    async def _generate_insight(self, seed: DaydreamSeed) -> DaydreamInsight:
        """Generate a creative insight from a daydream seed"""
        start_time = time.time()
        
        # Create the daydream trigger prompt
        prompt = self.prompts.format_prompt("daydream_trigger",
                                           context=seed.context,
                                           random_memory=seed.random_memory or "No specific memory",
                                           knowledge_domain=seed.knowledge_domain)
        
        # Generate the creative insight
        response = await self._query_model(prompt)
        
        # Extract components from the response
        connections = self._extract_connections(response)
        creativity_score = self._evaluate_creativity(response)
        relevance_score = self._evaluate_relevance(response, seed.context)
        
        processing_time = time.time() - start_time
        
        return DaydreamInsight(
            seed=seed,
            insight=response,
            connections_made=connections,
            creativity_score=creativity_score,
            relevance_score=relevance_score,
            timestamp=datetime.now(),
            processing_time=processing_time
        )
    
    async def _plan_insight_integration(self, insight: DaydreamInsight, user_input: str) -> str:
        """Plan how to integrate a creative insight into the conversation"""
        prompt = self.prompts.format_prompt("daydream_integration",
                                           daydream_insight=insight.insight,
                                           user_input=user_input,
                                           context=insight.seed.context)
        
        return await self._query_model(prompt)
    
    def _extract_connections(self, response: str) -> List[str]:
        """Extract the connections made in the creative insight"""
        connections = []
        
        # Look for connection indicators
        connection_patterns = [
            "connection between",
            "relates to",
            "similar to",
            "reminds me of",
            "connects with",
            "parallel to",
            "echoes",
            "mirrors"
        ]
        
        response_lower = response.lower()
        sentences = response.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for pattern in connection_patterns:
                if pattern in sentence_lower:
                    connections.append(sentence.strip())
                    break
        
        return connections[:5]  # Limit to 5 connections
    
    def _evaluate_creativity(self, response: str) -> float:
        """Evaluate the creativity score of an insight"""
        creativity_indicators = {
            "unexpected": 0.15,
            "novel": 0.15,
            "unique": 0.10,
            "surprising": 0.15,
            "innovative": 0.10,
            "unconventional": 0.15,
            "abstract": 0.10,
            "imaginative": 0.10,
            "original": 0.15,
            "creative": 0.10
        }
        
        response_lower = response.lower()
        creativity_score = 0.3  # Base score
        
        for indicator, score in creativity_indicators.items():
            if indicator in response_lower:
                creativity_score += score
        
        # Bonus for length and complexity
        if len(response) > 300:
            creativity_score += 0.1
        
        # Bonus for multiple creative connections
        connection_count = len(self._extract_connections(response))
        creativity_score += min(0.2, connection_count * 0.05)
        
        return min(1.0, creativity_score)
    
    def _evaluate_relevance(self, response: str, context: str) -> float:
        """Evaluate how relevant an insight is to the current context"""
        if not context:
            return 0.3  # Low relevance without context
        
        response_lower = response.lower()
        context_lower = context.lower()
        
        # Extract key words from context
        context_words = set(word.lower() for word in context.split() if len(word) > 3)
        response_words = set(word.lower() for word in response.split() if len(word) > 3)
        
        # Calculate word overlap
        overlap = len(context_words.intersection(response_words))
        overlap_score = min(0.4, overlap * 0.05)
        
        # Look for thematic relevance
        relevance_indicators = [
            "relates to our conversation",
            "connects to what you said",
            "similar theme",
            "relevant to",
            "applicable to",
            "useful for understanding"
        ]
        
        thematic_score = 0.0
        for indicator in relevance_indicators:
            if indicator in response_lower:
                thematic_score = 0.3
                break
        
        base_relevance = 0.2  # Base relevance score
        total_relevance = base_relevance + overlap_score + thematic_score
        
        return min(1.0, total_relevance)
    
    async def _query_model(self, prompt: str) -> str:
        """Query the AI model with a prompt"""
        try:
            # Handle different model client types (same as chain_of_thought.py)
            if hasattr(self.model_client, 'generate_response'):
                response = await self.model_client.generate_response(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            elif hasattr(self.model_client, 'generate'):
                response = await self.model_client.generate(prompt)
                return response
            elif callable(self.model_client):
                response = await self.model_client(prompt)
                return response
            else:
                return f"[Mock daydream response to: {prompt[:50]}...]"
                
        except Exception as e:
            return f"Error during daydreaming: {str(e)}"
    
    def get_insight_summary(self, session: DaydreamSession) -> str:
        """Get a human-readable summary of a daydream session"""
        if not session.insights:
            return f"Daydream session triggered by {session.trigger} - no insights generated"
        
        summary_parts = [
            f"Daydream Session ({session.trigger}): {len(session.insights)} insights in {session.total_time:.1f}s"
        ]
        
        if session.best_insight:
            insight = session.best_insight
            summary_parts.extend([
                f"Best Insight (creativity: {insight.creativity_score:.2f}, relevance: {insight.relevance_score:.2f}):",
                f"  Domain: {insight.seed.knowledge_domain}",
                f"  Insight: {insight.insight[:150]}..." if len(insight.insight) > 150 else f"  Insight: {insight.insight}"
            ])
            
            if insight.connections_made:
                summary_parts.append(f"  Connections: {len(insight.connections_made)} made")
        
        if session.integration_plan:
            summary_parts.append("Integration plan available for conversation")
        
        return "\n".join(summary_parts)
    
    def get_recent_insights_summary(self, limit: int = 5) -> str:
        """Get summary of recent insights for context"""
        if not self.recent_insights:
            return "No recent daydream insights"
        
        recent = self.recent_insights[-limit:]
        summary_parts = [f"Recent Daydream Insights ({len(recent)} insights):"]
        
        for i, insight in enumerate(recent, 1):
            domain = insight.seed.knowledge_domain
            score = insight.creativity_score + insight.relevance_score
            summary_parts.append(f"  {i}. {domain} (score: {score:.2f})")
        
        return "\n".join(summary_parts)


# Convenience functions
async def generate_daydream(context: str, 
                          model_client: Any,
                          memory_store: Optional[Any] = None,
                          progress_callback: Optional[Callable] = None) -> DaydreamSession:
    """
    Convenience function to generate a daydream session.
    
    Args:
        context: Current conversation context
        model_client: AI model client
        memory_store: Optional memory store
        progress_callback: Optional progress callback
        
    Returns:
        Complete daydream session
    """
    engine = DaydreamingEngine(model_client, memory_store)
    return await engine.trigger_daydream_session(context, "manual_trigger", progress_callback)


def should_trigger_daydream(context: str, frequency: float = 0.3) -> bool:
    """
    Simple check for whether to trigger daydreaming.
    
    Args:
        context: Current conversation context
        frequency: Base probability of triggering
        
    Returns:
        True if daydreaming should be triggered
    """
    engine = DaydreamingEngine(None)  # No model needed for this check
    engine.daydream_frequency = frequency
    return asyncio.run(engine.should_daydream(context))
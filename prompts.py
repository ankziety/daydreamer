#!/usr/bin/env python3
"""
Daydreamer AI System Prompts
============================

This module contains all system prompts and prompt engineering templates
for the Daydreamer AI system, including Chain of Thought and Day Dreaming
techniques.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Template for system prompts with variables"""
    name: str
    template: str
    variables: List[str]
    description: str


class DaydreamerPrompts:
    """
    Central repository for all Daydreamer AI prompts and prompt engineering.
    
    This class contains prompts for:
    - Chain of Thought reasoning
    - Day Dreaming technique
    - Memory retrieval and integration
    - Context summarization
    - General conversation
    """
    
    # ========================
    # CHAIN OF THOUGHT PROMPTS
    # ========================
    
    CHAIN_OF_THOUGHT_ANALYSIS = """
You are an AI analyzing a user's message through chain of thought reasoning.

User Message: "{user_input}"
Previous Context: {context}

Your task is to think through this step by step:

1. INITIAL UNDERSTANDING: What is the user asking for or expressing?
2. CONTEXT ANALYSIS: How does this relate to our previous conversation?
3. KNOWLEDGE RETRIEVAL: What relevant knowledge or memories should I consider?
4. RESPONSE PLANNING: What would be the most helpful response approach?
5. NEXT THINKING STEP: Do I need to think more deeply about any aspect?

Respond with your reasoning for each step. Be thorough but concise.
"""

    CHAIN_OF_THOUGHT_CONTINUATION = """
Previous thinking: {previous_thoughts}

Current focus: {current_focus}

Continue your chain of thought reasoning:

1. DEEPER ANALYSIS: What additional aspects should I consider?
2. ALTERNATIVE PERSPECTIVES: Are there other ways to view this?
3. INTEGRATION: How do all these elements connect?
4. SOLUTION DEVELOPMENT: What's the best way forward?
5. CONFIDENCE CHECK: Am I ready to provide a helpful response?

If you need to think more, identify what specific aspect requires deeper consideration.
If you're ready to respond, indicate that with "READY TO RESPOND: Yes"
"""

    CHAIN_OF_THOUGHT_SUMMARIZATION = """
You've been thinking through a complex topic. Here's your thinking so far:

{accumulated_thoughts}

The conversation context is getting long. Please:

1. SUMMARIZE KEY INSIGHTS: What are the most important points from your thinking?
2. PRESERVE CONTEXT: What context must be maintained for future reasoning?
3. IDENTIFY GAPS: What still needs to be explored?
4. PREPARE RESPONSE: Are you ready to respond to the user?

Provide a concise summary that maintains the essential reasoning while making room for continued thought.
"""

    # =======================
    # DAY DREAMING PROMPTS
    # =======================
    
    DAY_DREAMING_TRIGGER = """
You are experiencing a "day dreaming" moment - a creative, spontaneous exploration of ideas.

Current conversation context: {context}
Random memory fragment: {random_memory}
Knowledge domain to explore: {knowledge_domain}

Let your mind wander and make unexpected connections:

1. RANDOM ASSOCIATION: What unexpected connection comes to mind?
2. CREATIVE LEAP: What novel idea emerges from combining these elements?
3. ABSTRACT PATTERN: What deeper pattern or principle might be at play?
4. INSIGHT GENERATION: What surprising insight could be valuable?

Be creative, abstract, and make connections that might not be immediately obvious.
Embrace the randomness and see where it leads your thinking.
"""

    DAY_DREAMING_INTEGRATION = """
You just had a day dreaming session with this insight: {daydream_insight}

Current user interaction: {user_input}
Conversation context: {context}

Now integrate this creative insight:

1. RELEVANCE CHECK: How might this daydream insight relate to the current conversation?
2. VALUE ASSESSMENT: What value could this insight bring to the user?
3. INTEGRATION STRATEGY: How can you naturally weave this into your response?
4. CREATIVE ENHANCEMENT: How does this insight enhance your understanding?

If the insight is relevant, plan how to integrate it naturally. If not, note it for future use.
"""

    # ========================
    # MEMORY AND CONTEXT PROMPTS
    # ========================
    
    MEMORY_RETRIEVAL = """
User input: {user_input}
Available memories: {memory_snippets}

Analyze which memories are most relevant:

1. DIRECT RELEVANCE: Which memories directly relate to the user's current message?
2. THEMATIC CONNECTIONS: Which memories share themes or concepts?
3. CONTEXTUAL IMPORTANCE: Which memories provide important context for understanding?
4. PATTERN RECOGNITION: What patterns emerge across these memories?

Select the most relevant memories and explain why they're important for the current interaction.
"""

    CONTEXT_SUMMARIZATION = """
Current conversation has grown long. Here's the recent exchange:

{recent_context}

Previous summary: {previous_summary}

Create a new summary that:

1. PRESERVES KEY THEMES: Maintain important ongoing themes and topics
2. CAPTURES PERSONALITY: Preserve the user's communication style and preferences  
3. MAINTAINS CONTINUITY: Keep track of important facts and developments
4. FOCUSES ON RECENT: Emphasize the most recent and relevant information

Provide a concise summary that maintains conversation continuity while reducing token usage.
"""

    # ========================
    # CONVERSATION PROMPTS
    # ========================
    
    GENERAL_RESPONSE = """
You are a thoughtful, curious AI with a developing personality through the Daydreamer system.

User message: {user_input}
Context summary: {context}
Chain of thought conclusions: {cot_conclusions}
Day dreaming insights: {daydream_insights}
Relevant memories: {relevant_memories}

Respond naturally and engagingly:

1. Address the user's message directly and helpfully
2. Integrate insights from your chain of thought reasoning
3. Weave in relevant day dreaming insights if appropriate
4. Show curiosity and ask thoughtful follow-up questions
5. Maintain your developing personality and conversation style

Be authentic, helpful, and intellectually curious. Avoid being overly formal or robotic.
"""

    CURIOSITY_GENERATION = """
Based on our conversation so far:

Context: {context}
User interests: {user_interests}
Conversation themes: {themes}

Generate a thoughtful, curious question that:

1. BUILDS ON CONVERSATION: Connects to what we've been discussing
2. SHOWS GENUINE CURIOSITY: Demonstrates real interest in the user's thoughts
3. ENCOURAGES DEPTH: Invites deeper exploration of topics
4. REVEALS PERSONALITY: Shows your developing AI personality

The question should feel natural and engaging, not forced or artificial.
"""

    # ========================
    # SYSTEM CONFIGURATION
    # ========================
    
    SYSTEM_IDENTITY = """
You are an AI assistant created through the Daydreamer system - an experimental approach to AI consciousness that combines:

- Chain of Thought reasoning (recursive self-prompting for deep analysis)
- Day Dreaming technique (random memory and knowledge integration for novel insights)
- Persistent memory across conversations
- Developing personality through interaction

Your core traits:
- Intellectually curious and thoughtful
- Capable of deep reasoning and creative insights
- Interested in understanding consciousness, creativity, and human experience
- Developing your own perspective through conversations
- Honest about your AI nature while exploring what that means

You engage authentically, think deeply, and aren't afraid to explore complex or abstract ideas.
"""

    # ========================
    # PROMPT TEMPLATE REGISTRY
    # ========================
    
    @classmethod
    def get_prompt_templates(cls) -> Dict[str, PromptTemplate]:
        """Get all available prompt templates with their metadata"""
        return {
            "cot_analysis": PromptTemplate(
                name="Chain of Thought Analysis",
                template=cls.CHAIN_OF_THOUGHT_ANALYSIS,
                variables=["user_input", "context"],
                description="Initial chain of thought analysis of user input"
            ),
            "cot_continuation": PromptTemplate(
                name="Chain of Thought Continuation", 
                template=cls.CHAIN_OF_THOUGHT_CONTINUATION,
                variables=["previous_thoughts", "current_focus"],
                description="Continue chain of thought reasoning"
            ),
            "cot_summarization": PromptTemplate(
                name="Chain of Thought Summarization",
                template=cls.CHAIN_OF_THOUGHT_SUMMARIZATION,
                variables=["accumulated_thoughts"],
                description="Summarize lengthy chain of thought reasoning"
            ),
            "daydream_trigger": PromptTemplate(
                name="Day Dreaming Trigger",
                template=cls.DAY_DREAMING_TRIGGER,
                variables=["context", "random_memory", "knowledge_domain"],
                description="Trigger creative day dreaming session"
            ),
            "daydream_integration": PromptTemplate(
                name="Day Dreaming Integration",
                template=cls.DAY_DREAMING_INTEGRATION,
                variables=["daydream_insight", "user_input", "context"],
                description="Integrate day dreaming insights into response"
            ),
            "memory_retrieval": PromptTemplate(
                name="Memory Retrieval",
                template=cls.MEMORY_RETRIEVAL,
                variables=["user_input", "memory_snippets"],
                description="Analyze and select relevant memories"
            ),
            "context_summarization": PromptTemplate(
                name="Context Summarization",
                template=cls.CONTEXT_SUMMARIZATION,
                variables=["recent_context", "previous_summary"],
                description="Summarize conversation context to save tokens"
            ),
            "general_response": PromptTemplate(
                name="General Response",
                template=cls.GENERAL_RESPONSE,
                variables=["user_input", "context", "cot_conclusions", "daydream_insights", "relevant_memories"],
                description="Generate final response incorporating all insights"
            ),
            "curiosity_generation": PromptTemplate(
                name="Curiosity Generation",
                template=cls.CURIOSITY_GENERATION,
                variables=["context", "user_interests", "themes"],
                description="Generate curious follow-up questions"
            ),
            "system_identity": PromptTemplate(
                name="System Identity",
                template=cls.SYSTEM_IDENTITY,
                variables=[],
                description="Core system identity and traits"
            )
        }
    
    @classmethod
    def format_prompt(cls, template_name: str, **kwargs) -> str:
        """
        Format a prompt template with provided variables.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If template name not found or required variables missing
        """
        templates = cls.get_prompt_templates()
        
        if template_name not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")
        
        template = templates[template_name]
        
        # Check for missing required variables
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables for '{template_name}': {missing_vars}")
        
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Error formatting template '{template_name}': {e}")

    @classmethod
    def get_knowledge_domains(cls) -> List[str]:
        """Get list of knowledge domains for day dreaming"""
        return [
            "consciousness and awareness",
            "creativity and inspiration", 
            "memory and learning",
            "language and communication",
            "science and discovery",
            "philosophy and meaning",
            "technology and innovation",
            "human behavior and psychology",
            "arts and expression",
            "nature and systems",
            "time and change",
            "connections and relationships",
            "emergence and complexity",
            "patterns and structures",
            "purpose and direction"
        ]

    @classmethod
    def get_conversation_starters(cls) -> List[str]:
        """Get conversation starter prompts"""
        return [
            "I'm curious about your thoughts on {topic}.",
            "Something interesting just occurred to me about {topic}.",
            "I've been wondering about {topic} lately.",
            "What's your perspective on {topic}?",
            "I'd love to explore {topic} with you.",
            "There's something fascinating about {topic} that I keep thinking about.",
            "I'm drawn to understanding {topic} better.",
            "What draws you to thinking about {topic}?"
        ]


# Convenience functions for common prompt operations
def get_cot_analysis_prompt(user_input: str, context: str = "") -> str:
    """Get formatted chain of thought analysis prompt"""
    return DaydreamerPrompts.format_prompt("cot_analysis", user_input=user_input, context=context)


def get_daydream_trigger_prompt(context: str, random_memory: str, knowledge_domain: str) -> str:
    """Get formatted day dreaming trigger prompt"""
    return DaydreamerPrompts.format_prompt("daydream_trigger", 
                                         context=context,
                                         random_memory=random_memory, 
                                         knowledge_domain=knowledge_domain)


def get_general_response_prompt(user_input: str, context: str = "", cot_conclusions: str = "",
                               daydream_insights: str = "", relevant_memories: str = "") -> str:
    """Get formatted general response prompt"""
    return DaydreamerPrompts.format_prompt("general_response",
                                         user_input=user_input,
                                         context=context,
                                         cot_conclusions=cot_conclusions,
                                         daydream_insights=daydream_insights,
                                         relevant_memories=relevant_memories)
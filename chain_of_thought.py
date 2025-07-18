#!/usr/bin/env python3
"""
Chain of Thought Implementation
===============================

This module implements true chain of thought reasoning through recursive
self-prompting, building context iteratively until reaching a satisfactory
answer or hitting context limits.
"""

import asyncio
import time
from typing import List, Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from prompts import DaydreamerPrompts


@dataclass
class ThinkingStep:
    """Represents one step in the chain of thought process"""
    step_number: int
    focus: str
    thoughts: str
    confidence: float
    timestamp: datetime
    ready_to_respond: bool = False
    needs_more_thinking: bool = False
    specific_focus: Optional[str] = None


@dataclass
class ChainOfThoughtResult:
    """Result of a complete chain of thought process"""
    original_input: str
    thinking_steps: List[ThinkingStep]
    final_conclusions: str
    total_thinking_time: float
    confidence_score: float
    context_summarized: bool = False
    summary: Optional[str] = None


class ChainOfThoughtProcessor:
    """
    Implements true chain of thought reasoning through recursive self-prompting.
    
    This processor:
    1. Takes user input and begins reasoning
    2. Recursively prompts itself to think deeper
    3. Builds context through multiple thinking steps
    4. Summarizes when approaching context limits
    5. Continues until reaching satisfactory conclusions
    """
    
    def __init__(self, 
                 model_client: Any,
                 max_thinking_steps: int = 10,
                 max_context_tokens: int = 2000,
                 confidence_threshold: float = 0.8,
                 thinking_timeout: float = 30.0,
                 verbose: bool = False):
        """
        Initialize chain of thought processor.
        
        Args:
            model_client: Client for AI model (Ollama or Transformers)
            max_thinking_steps: Maximum number of thinking iterations
            max_context_tokens: Context limit before summarization
            confidence_threshold: Confidence needed before stopping
            thinking_timeout: Maximum time to spend thinking
            verbose: Enable verbose logging of prompts and responses
        """
        self.model_client = model_client
        self.max_thinking_steps = max_thinking_steps
        self.max_context_tokens = max_context_tokens
        self.confidence_threshold = confidence_threshold
        self.thinking_timeout = thinking_timeout
        self.verbose = verbose
        self.prompts = DaydreamerPrompts()
    
    async def process_chain_of_thought(self, 
                                     user_input: str, 
                                     context: str = "",
                                     progress_callback: Optional[Callable] = None) -> ChainOfThoughtResult:
        """
        Process user input through chain of thought reasoning.
        
        Args:
            user_input: The user's message to analyze
            context: Previous conversation context
            progress_callback: Optional callback for progress updates
            
        Returns:
            ChainOfThoughtResult with complete reasoning process
        """
        start_time = time.time()
        thinking_steps: List[ThinkingStep] = []
        
        if progress_callback:
            progress_callback("Starting chain of thought analysis...")
        
        # Step 1: Initial analysis
        initial_step = await self._initial_analysis(user_input, context)
        thinking_steps.append(initial_step)
        
        if progress_callback:
            progress_callback(f"Initial analysis complete (confidence: {initial_step.confidence:.2f})")
        
        # Continue thinking until we reach a satisfactory conclusion
        current_step = initial_step
        step_count = 1
        
        while (step_count < self.max_thinking_steps and 
               time.time() - start_time < self.thinking_timeout and
               not current_step.ready_to_respond and
               current_step.confidence < self.confidence_threshold):
            
            # Check if we need to summarize due to context length
            if self._should_summarize_context(thinking_steps):
                if progress_callback:
                    progress_callback("Summarizing context to continue thinking...")
                    
                summary = await self._summarize_thinking(thinking_steps)
                # Create a summary step to maintain the chain
                summary_step = ThinkingStep(
                    step_number=step_count + 1,
                    focus="context_summarization",
                    thoughts=summary,
                    confidence=current_step.confidence,
                    timestamp=datetime.now()
                )
                thinking_steps.append(summary_step)
                step_count += 1
            
            # Continue thinking
            if progress_callback:
                progress_callback(f"Continuing chain of thought (step {step_count + 1})...")
                
            next_step = await self._continue_thinking(thinking_steps, current_step)
            step_count += 1
            thinking_steps.append(next_step)
            current_step = next_step
            
            if progress_callback:
                progress_callback(f"Step {step_count} complete (confidence: {current_step.confidence:.2f})")
        
        # Generate final conclusions
        if progress_callback:
            progress_callback("Generating final conclusions...")
            
        final_conclusions = await self._generate_conclusions(thinking_steps)
        
        total_time = time.time() - start_time
        final_confidence = current_step.confidence if thinking_steps else 0.5
        
        result = ChainOfThoughtResult(
            original_input=user_input,
            thinking_steps=thinking_steps,
            final_conclusions=final_conclusions,
            total_thinking_time=total_time,
            confidence_score=final_confidence,
            context_summarized=any(step.focus == "context_summarization" for step in thinking_steps)
        )
        
        if progress_callback:
            progress_callback(f"Chain of thought complete ({len(thinking_steps)} steps, {total_time:.1f}s)")
        
        return result
    
    async def _initial_analysis(self, user_input: str, context: str) -> ThinkingStep:
        """Perform initial chain of thought analysis"""
        prompt = self.prompts.format_prompt("cot_analysis", 
                                           user_input=user_input, 
                                           context=context)
        
        if self.verbose:
            print(f"   📝 INITIAL ANALYSIS PROMPT:")
            print(f"      {prompt[:200]}..." if len(prompt) > 200 else f"      {prompt}")
        
        response = await self._query_model(prompt)
        
        if self.verbose:
            print(f"   🤖 MODEL RESPONSE:")
            print(f"      {response[:300]}..." if len(response) > 300 else f"      {response}")
        
        confidence = self._extract_confidence(response)
        ready_to_respond = self._check_ready_to_respond(response)
        
        if self.verbose:
            print(f"   📊 ANALYSIS: confidence={confidence:.2f}, ready={ready_to_respond}")
        
        return ThinkingStep(
            step_number=1,
            focus="initial_analysis",
            thoughts=response,
            confidence=confidence,
            timestamp=datetime.now(),
            ready_to_respond=ready_to_respond,
            needs_more_thinking=not ready_to_respond,
            specific_focus=self._extract_next_focus(response) if not ready_to_respond else None
        )
    
    async def _continue_thinking(self, 
                               thinking_steps: List[ThinkingStep], 
                               current_step: ThinkingStep) -> ThinkingStep:
        """Continue the chain of thought with deeper analysis"""
        
        # Build context from previous thinking
        previous_thoughts = self._build_thinking_context(thinking_steps)
        current_focus = current_step.specific_focus or "deeper analysis"
        
        if self.verbose:
            print(f"   🎯 ATTENTION FOCUS: {current_focus}")
            print(f"   🧠 CONTEXT: {len(previous_thoughts)} chars from {len(thinking_steps)} previous steps")
        
        prompt = self.prompts.format_prompt("cot_continuation",
                                          previous_thoughts=previous_thoughts,
                                          current_focus=current_focus)
        
        if self.verbose:
            print(f"   📝 CONTINUATION PROMPT:")
            print(f"      {prompt[:200]}..." if len(prompt) > 200 else f"      {prompt}")
        
        response = await self._query_model(prompt)
        
        if self.verbose:
            print(f"   🤖 MODEL RESPONSE:")
            print(f"      {response[:300]}..." if len(response) > 300 else f"      {response}")
        
        confidence = self._extract_confidence(response)
        ready_to_respond = self._check_ready_to_respond(response)
        next_focus = self._extract_next_focus(response) if not ready_to_respond else None
        
        if self.verbose:
            print(f"   📊 ANALYSIS: confidence={confidence:.2f}, ready={ready_to_respond}")
            if next_focus:
                print(f"   ➡️  NEXT FOCUS: {next_focus}")
        
        return ThinkingStep(
            step_number=current_step.step_number + 1,
            focus=current_focus,
            thoughts=response,
            confidence=confidence,
            timestamp=datetime.now(),
            ready_to_respond=ready_to_respond,
            needs_more_thinking=not ready_to_respond,
            specific_focus=next_focus
        )
    
    async def _summarize_thinking(self, thinking_steps: List[ThinkingStep]) -> str:
        """Summarize accumulated thinking when context gets too long"""
        accumulated_thoughts = "\n\n".join([
            f"Step {step.step_number} ({step.focus}): {step.thoughts}"
            for step in thinking_steps
        ])
        
        if self.verbose:
            total_chars = len(accumulated_thoughts)
            estimated_tokens = total_chars // 4
            print(f"   ✂️  TRUNCATION TRIGGERED:")
            print(f"      Current context: {total_chars} chars (~{estimated_tokens} tokens)")
            print(f"      Limit: {self.max_context_tokens} tokens")
            print(f"      Summarizing {len(thinking_steps)} thinking steps...")
        
        prompt = self.prompts.format_prompt("cot_summarization",
                                          accumulated_thoughts=accumulated_thoughts)
        
        if self.verbose:
            print(f"   📝 SUMMARIZATION PROMPT:")
            print(f"      {prompt[:200]}..." if len(prompt) > 200 else f"      {prompt}")
        
        summary = await self._query_model(prompt)
        
        if self.verbose:
            print(f"   📋 SUMMARY RESULT:")
            print(f"      {summary[:200]}..." if len(summary) > 200 else f"      {summary}")
            print(f"   📉 Context reduced from {len(accumulated_thoughts)} to {len(summary)} chars")
        
        return summary
    
    async def _generate_conclusions(self, thinking_steps: List[ThinkingStep]) -> str:
        """Generate final conclusions from all thinking steps"""
        if not thinking_steps:
            return "No thinking steps available for conclusions."
        
        # Use the last few steps for conclusions, or summary if available
        recent_steps = thinking_steps[-3:] if len(thinking_steps) > 3 else thinking_steps
        
        conclusions_parts = []
        for step in recent_steps:
            if step.focus == "context_summarization":
                conclusions_parts.append(f"Summary: {step.thoughts}")
            else:
                conclusions_parts.append(f"{step.focus.replace('_', ' ').title()}: {step.thoughts}")
        
        # Extract key insights
        final_step = thinking_steps[-1]
        if final_step.ready_to_respond:
            conclusions_parts.append(f"Final Assessment: Ready to respond with confidence {final_step.confidence:.2f}")
        
        return "\n\n".join(conclusions_parts)
    
    def _should_summarize_context(self, thinking_steps: List[ThinkingStep]) -> bool:
        """Check if context should be summarized due to length"""
        # Rough token estimation: ~4 characters per token
        total_chars = sum(len(step.thoughts) for step in thinking_steps)
        estimated_tokens = total_chars // 4
        
        return estimated_tokens > self.max_context_tokens
    
    def _build_thinking_context(self, thinking_steps: List[ThinkingStep]) -> str:
        """Build context string from previous thinking steps"""
        context_parts = []
        
        for step in thinking_steps[-3:]:  # Use last 3 steps for context
            context_parts.append(f"Step {step.step_number} ({step.focus}): {step.thoughts[:200]}...")
        
        return "\n\n".join(context_parts)
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from model response"""
        # Look for confidence indicators in the response
        confidence_keywords = {
            "very confident": 0.9,
            "confident": 0.8,
            "moderately confident": 0.7,
            "somewhat confident": 0.6,
            "uncertain": 0.4,
            "very uncertain": 0.3,
            "ready to respond": 0.85,
            "need more thinking": 0.5,
            "requires deeper analysis": 0.4
        }
        
        response_lower = response.lower()
        
        for keyword, score in confidence_keywords.items():
            if keyword in response_lower:
                return score
        
        # Default confidence based on response length and completeness
        if len(response) > 200 and any(word in response_lower for word in ["because", "therefore", "conclusion"]):
            return 0.7
        elif len(response) > 100:
            return 0.6
        else:
            return 0.5
    
    def _check_ready_to_respond(self, response: str) -> bool:
        """Check if the model indicates it's ready to respond"""
        ready_indicators = [
            "ready to respond: yes",
            "ready to respond",
            "confident in response",
            "sufficient analysis",
            "clear understanding"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in ready_indicators)
    
    def _extract_next_focus(self, response: str) -> Optional[str]:
        """Extract what the model wants to focus on next"""
        response_lower = response.lower()
        
        # Look for focus indicators
        focus_patterns = [
            "need to explore",
            "should consider",
            "focus on",
            "analyze further", 
            "deeper analysis of",
            "examine"
        ]
        
        for pattern in focus_patterns:
            if pattern in response_lower:
                # Extract the next 50 characters after the pattern
                idx = response_lower.find(pattern)
                next_focus = response[idx:idx+100].split('.')[0]
                return next_focus.strip()
        
        return None
    
    async def _query_model(self, prompt: str) -> str:
        """Query the AI model with a prompt"""
        try:
            # Handle different model client types
            if hasattr(self.model_client, 'generate_response'):
                # Ollama-style client
                response = await self.model_client.generate_response(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            elif hasattr(self.model_client, 'generate'):
                # Transformers-style client
                response = await self.model_client.generate(prompt)
                return response
            elif callable(self.model_client):
                # Function-style client
                response = await self.model_client(prompt)
                return response
            else:
                # Fallback: treat as string generator
                return f"[Mock response to: {prompt[:50]}...]"
                
        except Exception as e:
            return f"Error during thinking: {str(e)}"
    
    def get_thinking_summary(self, result: ChainOfThoughtResult) -> str:
        """Get a human-readable summary of the thinking process"""
        summary_parts = [
            f"Chain of Thought Analysis ({len(result.thinking_steps)} steps, {result.total_thinking_time:.1f}s)",
            f"Final Confidence: {result.confidence_score:.2f}",
        ]
        
        if result.context_summarized:
            summary_parts.append("Context was summarized during thinking")
        
        # Add key insights from each step
        for step in result.thinking_steps:
            if step.focus != "context_summarization":
                step_summary = step.thoughts[:100] + "..." if len(step.thoughts) > 100 else step.thoughts
                summary_parts.append(f"  {step.focus}: {step_summary}")
        
        return "\n".join(summary_parts)


# Convenience function for easy usage
async def think_through(user_input: str, 
                       model_client: Any, 
                       context: str = "",
                       progress_callback: Optional[Callable] = None,
                       verbose: bool = False) -> ChainOfThoughtResult:
    """
    Convenience function to process user input through chain of thought.
    
    Args:
        user_input: User's message to analyze
        model_client: AI model client
        context: Previous conversation context
        progress_callback: Optional callback for progress updates
        verbose: Enable verbose logging
        
    Returns:
        Complete chain of thought result
    """
    processor = ChainOfThoughtProcessor(model_client, verbose=verbose)
    return await processor.process_chain_of_thought(user_input, context, progress_callback)
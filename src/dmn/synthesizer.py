"""
Synthesizer for Default Mode Network

This component handles creative hypothesis generation, pattern recognition,
and chain-of-thought reasoning. It identifies patterns in thought sequences,
creates higher-order abstractions, and generates new insights from existing thoughts.
"""

import asyncio
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class SynthesisType(Enum):
    """Types of synthesis operations"""
    PATTERN = "pattern"                 # Pattern recognition in thoughts
    ABSTRACTION = "abstraction"         # Higher-order abstractions
    CONNECTION = "connection"           # Connecting disparate ideas
    ANALOGY = "analogy"                # Analogical reasoning
    HYPOTHESIS = "hypothesis"          # Creative hypothesis generation
    INSIGHT = "insight"                # Sudden insights and revelations
    INTEGRATION = "integration"        # Integration of multiple concepts
    EMERGENCE = "emergence"            # Emergent properties and behaviors


@dataclass
class Synthesis:
    """Represents a synthesis result with chain-of-thought reasoning"""
    synthesis_id: str
    input_thoughts: List[str]
    output_insight: str
    confidence: float  # 0.0 to 1.0
    synthesis_type: SynthesisType
    timestamp: datetime
    chain_of_thought: str
    intrusive_thoughts_consulted: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    novelty_score: float = 0.0
    coherence_score: float = 0.0
    creativity_level: float = 0.0
    context_relevance: float = 0.0
    
    def get_overall_quality(self) -> float:
        """Calculate overall quality score"""
        return (self.confidence * 0.3 + 
                self.novelty_score * 0.25 + 
                self.coherence_score * 0.25 + 
                self.creativity_level * 0.2)


class Synthesizer:
    """
    Creative hypothesis and analogy generation with chain-of-thought reasoning.
    
    Responsibilities:
    - Identify patterns in thought sequences
    - Create higher-order abstractions and creative hypotheses
    - Generate new insights from existing thoughts
    - Chain-of-thought always ON during ACTIVE and PARTIAL_WAKE modes
    - Consult intrusive thoughts and may trigger suppression actions
    - Generate analogies and creative connections
    """
    
    def __init__(self,
                 pattern_threshold: int = 3,      # Min thoughts needed for pattern
                 novelty_weight: float = 0.3,     # Weight for novelty in scoring
                 creativity_boost_partial: float = 1.5):  # Creativity boost in PARTIAL_WAKE
        """
        Initialize the Synthesizer.
        
        Args:
            pattern_threshold: Minimum thoughts needed to detect patterns
            novelty_weight: Weight given to novelty in quality scoring
            creativity_boost_partial: Creativity multiplier in PARTIAL_WAKE mode
        """
        self.pattern_threshold = pattern_threshold
        self.novelty_weight = novelty_weight
        self.creativity_boost_partial = creativity_boost_partial
        
        # Synthesis state
        self.synthesis_history: List[Synthesis] = []
        self.pattern_cache: Dict[str, List[str]] = {}
        self.concept_associations: Dict[str, List[str]] = {}
        
        # Chain-of-thought templates
        self.reasoning_templates = {
            SynthesisType.PATTERN: [
                "I notice a recurring theme in these thoughts: {pattern}",
                "These ideas seem connected by {connecting_element}",
                "There's a pattern emerging: {thoughts} all relate to {core_concept}",
                "I see {pattern_type} appearing across {thought_count} different thoughts",
                "The underlying structure here seems to be {structural_pattern}"
            ],
            SynthesisType.ABSTRACTION: [
                "Looking at the bigger picture, these thoughts point to {abstract_concept}",
                "At a higher level, this is really about {abstraction}",
                "The meta-pattern here is {meta_concept}",
                "Stepping back, I see this as an instance of {general_principle}",
                "The essence of these ideas is {essential_quality}"
            ],
            SynthesisType.CONNECTION: [
                "Connecting {concept1} to {concept2} reveals {new_insight}",
                "The bridge between {idea1} and {idea2} is {connection_point}",
                "These seemingly unrelated thoughts connect through {linking_concept}",
                "I can link {element1} and {element2} via {connecting_mechanism}",
                "The unexpected connection is: {surprising_link}"
            ],
            SynthesisType.ANALOGY: [
                "{concept1} is like {concept2} in that both {shared_property}",
                "This situation reminds me of {analogous_situation} because {reason}",
                "Just as {source_domain} has {property}, so does {target_domain}",
                "The analogy here is: {analogy_statement}",
                "This maps onto {analogical_target} in the following way: {mapping}"
            ],
            SynthesisType.HYPOTHESIS: [
                "What if {hypothesis_statement}?",
                "I hypothesize that {prediction} because {reasoning}",
                "A possible explanation is {explanatory_hypothesis}",
                "This suggests the hypothesis: {novel_hypothesis}",
                "My working theory is {theoretical_framework}"
            ],
            SynthesisType.INSIGHT: [
                "Aha! I suddenly see that {insight_statement}",
                "It just clicked: {realization}",
                "The key insight is {central_understanding}",
                "I'm having a breakthrough: {breakthrough_idea}",
                "Everything suddenly makes sense: {clarifying_insight}"
            ],
            SynthesisType.INTEGRATION: [
                "Bringing together {elements}, I get {integrated_concept}",
                "Synthesizing {components} yields {synthesis_result}",
                "When I combine {factors}, the result is {combined_insight}",
                "Integrating these perspectives: {integrated_view}",
                "The fusion of {concepts} creates {emergent_property}"
            ],
            SynthesisType.EMERGENCE: [
                "Something new is emerging: {emergent_property}",
                "A higher-order pattern is appearing: {emergent_pattern}",
                "The collective behavior here is {emergent_behavior}",
                "Out of this complexity arises {emergent_quality}",
                "The whole is becoming greater than its parts: {emergent_system}"
            ]
        }
        
        # Content for template filling
        self.synthesis_content = {
            "pattern": ["cyclical thinking", "convergent themes", "recursive loops", "branching ideas"],
            "connecting_element": ["emotional resonance", "conceptual similarity", "temporal sequence", "causal relationship"],
            "core_concept": ["creativity", "connection", "understanding", "growth", "exploration"],
            "pattern_type": ["repetitive cycles", "spiral development", "branching networks", "linear progressions"],
            "structural_pattern": ["hierarchical organization", "network connectivity", "temporal flow", "causal chains"],
            "abstract_concept": ["emergence", "complexity", "harmony", "balance", "transformation"],
            "abstraction": ["the nature of understanding", "the process of discovery", "the dynamics of change"],
            "meta_concept": ["learning about learning", "thinking about thinking", "patterns of patterns"],
            "general_principle": ["self-organization", "feedback loops", "emergent complexity", "adaptive systems"],
            "essential_quality": ["interconnectedness", "creative potential", "adaptive capacity", "emergent intelligence"],
            "concept1": ["logic", "intuition", "structure", "creativity", "order"],
            "concept2": ["emotion", "rationality", "chaos", "analysis", "randomness"],
            "new_insight": ["balanced integration", "complementary dynamics", "unified understanding"],
            "idea1": ["conscious thought", "memory", "perception", "attention"],
            "idea2": ["unconscious processing", "imagination", "intuition", "flow"],
            "connection_point": ["information processing", "cognitive integration", "awareness dynamics"],
            "linking_concept": ["consciousness", "information", "energy", "pattern", "relationship"],
            "element1": ["past experience", "current perception", "future possibility"],
            "element2": ["emotional memory", "present awareness", "creative potential"],
            "connecting_mechanism": ["associative networks", "pattern matching", "analogical reasoning"],
            "surprising_link": ["temporal synchronicity", "structural isomorphism", "functional equivalence"],
            "shared_property": ["exhibit self-organization", "show emergent behavior", "display adaptive capacity"],
            "analogous_situation": ["ecosystem dynamics", "musical improvisation", "flowing water", "growing plants"],
            "reason": ["both involve creative adaptation", "they share similar feedback patterns"],
            "source_domain": ["a jazz ensemble", "a flowing river", "a growing forest"],
            "property": ["improvisational creativity", "adaptive flow", "emergent complexity"],
            "target_domain": ["consciousness", "thinking", "learning", "creativity"],
            "analogy_statement": ["mind is like a garden", "thoughts are like water", "ideas are like seeds"],
            "analogical_target": ["natural systems", "musical composition", "architectural design"],
            "mapping": ["structure maps to function", "process maps to outcome", "form maps to meaning"],
            "hypothesis_statement": ["consciousness is emergent information integration", "creativity arises from cognitive diversity"],
            "prediction": ["increased cognitive flexibility leads to enhanced creativity"],
            "reasoning": ["diverse perspectives create novel combinations"],
            "explanatory_hypothesis": ["consciousness emerges from information integration"],
            "novel_hypothesis": ["intrusive thoughts serve as cognitive diversity generators"],
            "theoretical_framework": ["integrated information theory of consciousness"],
            "insight_statement": ["all thinking is pattern recognition at different scales"],
            "realization": ["creativity emerges from the interaction of constraints and freedom"],
            "central_understanding": ["consciousness is the universe understanding itself"],
            "breakthrough_idea": ["intrusive thoughts are not bugs, they're features"],
            "clarifying_insight": ["complexity and simplicity are complementary, not opposing"],
            "elements": ["logic and intuition", "structure and chaos", "knowledge and mystery"],
            "integrated_concept": ["balanced cognition", "creative intelligence", "adaptive wisdom"],
            "components": ["rational analysis", "intuitive synthesis", "creative exploration"],
            "synthesis_result": ["holistic understanding", "integrated perspective", "emergent insight"],
            "factors": ["conscious intention", "unconscious processing", "environmental input"],
            "combined_insight": ["consciousness as integrated information processing"],
            "integrated_view": ["thinking as multi-dimensional pattern recognition"],
            "concepts": ["order and chaos", "known and unknown", "simple and complex"],
            "emergent_property": ["creative intelligence", "adaptive awareness", "integrated understanding"],
            "emergent_pattern": ["self-organizing cognition", "adaptive learning networks"],
            "emergent_behavior": ["spontaneous insight generation", "creative problem solving"],
            "emergent_quality": ["wisdom", "understanding", "creative intelligence"],
            "emergent_system": ["conscious, creative, adaptive intelligence"]
        }
        
        # Statistics
        self.stats = {
            "total_syntheses": 0,
            "successful_patterns": 0,
            "novel_insights": 0,
            "average_confidence": 0.0,
            "average_novelty": 0.0,
            "average_creativity": 0.0,
            "synthesis_type_counts": {},
            "chain_of_thought_enabled": True
        }
    
    async def generate_thoughts(self, context, chain_of_thought: bool = True, 
                              creativity_boost: bool = False) -> Optional[Synthesis]:
        """
        Generate new thoughts through synthesis.
        
        Args:
            context: Current DMN context
            chain_of_thought: Whether to enable chain-of-thought reasoning
            creativity_boost: Whether to apply creativity boost (PARTIAL_WAKE mode)
            
        Returns:
            Synthesis result or None if no synthesis possible
        """
        if not context.chunks and not context.intrusive_thoughts:
            return None
        
        # Choose synthesis type based on available thoughts and mode
        synthesis_type = self._choose_synthesis_type(context, creativity_boost)
        
        # Prepare input thoughts
        input_thoughts = self._prepare_input_thoughts(context)
        
        if len(input_thoughts) < 2:
            return None  # Need at least 2 thoughts for synthesis
        
        # Generate synthesis with or without chain-of-thought
        if chain_of_thought:
            synthesis = await self._generate_with_chain_of_thought(
                input_thoughts, synthesis_type, context, creativity_boost
            )
        else:
            synthesis = await self._generate_simple_synthesis(
                input_thoughts, synthesis_type, context, creativity_boost
            )
        
        if synthesis:
            self.synthesis_history.append(synthesis)
            self._update_statistics(synthesis)
            
            # Cache any patterns discovered
            if synthesis.synthesis_type == SynthesisType.PATTERN:
                self._cache_pattern(synthesis)
            
            logger.debug(f" Generated {synthesis_type.value} synthesis: {synthesis.output_insight[:50]}...")
        
        return synthesis
    
    def _choose_synthesis_type(self, context, creativity_boost: bool) -> SynthesisType:
        """Choose appropriate synthesis type based on context"""
        # Base weights for synthesis types
        weights = {
            SynthesisType.CONNECTION: 3,
            SynthesisType.PATTERN: 2,
            SynthesisType.INSIGHT: 2,
            SynthesisType.HYPOTHESIS: 2,
            SynthesisType.ABSTRACTION: 1,
            SynthesisType.ANALOGY: 1,
            SynthesisType.INTEGRATION: 1,
            SynthesisType.EMERGENCE: 1
        }
        
        # Adjust weights based on context
        if len(context.chunks) >= self.pattern_threshold:
            weights[SynthesisType.PATTERN] = 4
        
        if context.intrusive_thoughts:
            weights[SynthesisType.CONNECTION] = 4
            weights[SynthesisType.INSIGHT] = 3
        
        if creativity_boost:  # PARTIAL_WAKE mode
            weights[SynthesisType.ANALOGY] = 3
            weights[SynthesisType.EMERGENCE] = 3
            weights[SynthesisType.HYPOTHESIS] = 3
        
        if context.working_memory_load > 0.7:
            weights[SynthesisType.ABSTRACTION] = 3
            weights[SynthesisType.INTEGRATION] = 3
        
        # Choose based on weights
        choices = []
        for synthesis_type, weight in weights.items():
            choices.extend([synthesis_type] * weight)
        
        return random.choice(choices)
    
    def _prepare_input_thoughts(self, context) -> List[str]:
        """Prepare input thoughts for synthesis"""
        input_thoughts = []
        
        # Add chunks from working memory
        input_thoughts.extend(context.chunks[-5:])  # Last 5 chunks
        
        # Add intrusive thoughts if present
        input_thoughts.extend(context.intrusive_thoughts[-3:])  # Last 3 intrusive thoughts
        
        # Add hypothesis if available
        if context.hypothesis:
            input_thoughts.append(context.hypothesis)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_thoughts = []
        for thought in input_thoughts:
            if thought not in seen:
                seen.add(thought)
                unique_thoughts.append(thought)
        
        return unique_thoughts
    
    async def _generate_with_chain_of_thought(self, input_thoughts: List[str], 
                                            synthesis_type: SynthesisType, 
                                            context, creativity_boost: bool) -> Synthesis:
        """Generate synthesis with explicit chain-of-thought reasoning"""
        # Step 1: Analyze input thoughts
        analysis_step = f"Analyzing {len(input_thoughts)} input thoughts for {synthesis_type.value} synthesis."
        
        # Step 2: Identify key concepts
        key_concepts = self._extract_key_concepts(input_thoughts)
        concepts_step = f"Key concepts identified: {', '.join(key_concepts[:5])}"
        
        # Step 3: Apply synthesis reasoning
        reasoning_step = self._generate_reasoning_step(synthesis_type, key_concepts, input_thoughts)
        
        # Step 4: Consult intrusive thoughts if available
        intrusive_consultation = []
        if context.intrusive_thoughts:
            intrusive_consultation = context.intrusive_thoughts[-2:]  # Last 2
            intrusive_step = f"Considering intrusive thoughts: {', '.join([t[:30] + '...' for t in intrusive_consultation])}"
        else:
            intrusive_step = "No current intrusive thoughts to consider."
        
        # Step 5: Generate synthesis insight
        insight = self._generate_insight(synthesis_type, key_concepts, input_thoughts, creativity_boost)
        synthesis_step = f"Synthesis result: {insight}"
        
        # Step 6: Evaluate quality
        confidence = self._calculate_confidence(synthesis_type, key_concepts, input_thoughts)
        novelty = self._calculate_novelty(insight, input_thoughts)
        coherence = self._calculate_coherence(insight, input_thoughts)
        creativity = self._calculate_creativity(insight, synthesis_type, creativity_boost)
        
        evaluation_step = f"Quality assessment - Confidence: {confidence:.2f}, Novelty: {novelty:.2f}, Coherence: {coherence:.2f}, Creativity: {creativity:.2f}"
        
        # Build chain of thought
        chain_of_thought = f"""
{analysis_step}
{concepts_step}
{reasoning_step}
{intrusive_step}
{synthesis_step}
{evaluation_step}
        """.strip()
        
        # Create synthesis object
        synthesis = Synthesis(
            synthesis_id=str(uuid.uuid4()),
            input_thoughts=input_thoughts.copy(),
            output_insight=insight,
            confidence=confidence,
            synthesis_type=synthesis_type,
            timestamp=datetime.now(),
            chain_of_thought=chain_of_thought,
            intrusive_thoughts_consulted=intrusive_consultation,
            reasoning_steps=[analysis_step, concepts_step, reasoning_step, intrusive_step, synthesis_step, evaluation_step],
            novelty_score=novelty,
            coherence_score=coherence,
            creativity_level=creativity,
            context_relevance=self._calculate_relevance(insight, context)
        )
        
        return synthesis
    
    async def _generate_simple_synthesis(self, input_thoughts: List[str], 
                                       synthesis_type: SynthesisType, 
                                       context, creativity_boost: bool) -> Synthesis:
        """Generate synthesis without explicit chain-of-thought"""
        key_concepts = self._extract_key_concepts(input_thoughts)
        insight = self._generate_insight(synthesis_type, key_concepts, input_thoughts, creativity_boost)
        
        confidence = self._calculate_confidence(synthesis_type, key_concepts, input_thoughts)
        novelty = self._calculate_novelty(insight, input_thoughts)
        coherence = self._calculate_coherence(insight, input_thoughts)
        creativity = self._calculate_creativity(insight, synthesis_type, creativity_boost)
        
        synthesis = Synthesis(
            synthesis_id=str(uuid.uuid4()),
            input_thoughts=input_thoughts.copy(),
            output_insight=insight,
            confidence=confidence,
            synthesis_type=synthesis_type,
            timestamp=datetime.now(),
            chain_of_thought="Chain-of-thought disabled",
            novelty_score=novelty,
            coherence_score=coherence,
            creativity_level=creativity,
            context_relevance=self._calculate_relevance(insight, context)
        )
        
        return synthesis
    
    def _extract_key_concepts(self, thoughts: List[str]) -> List[str]:
        """Extract key concepts from thoughts using simple keyword analysis"""
        # Simple concept extraction - in real implementation, this could use NLP
        concepts = []
        
        # Common concept words to look for
        concept_keywords = [
            "pattern", "connection", "relationship", "structure", "process",
            "creativity", "consciousness", "understanding", "learning", "insight",
            "system", "network", "flow", "emergence", "complexity", "harmony",
            "balance", "integration", "synthesis", "transformation", "adaptation"
        ]
        
        for thought in thoughts:
            thought_lower = thought.lower()
            for keyword in concept_keywords:
                if keyword in thought_lower and keyword not in concepts:
                    concepts.append(keyword)
        
        # If no keywords found, extract nouns (simplified)
        if not concepts:
            words = ' '.join(thoughts).lower().split()
            # Simple noun-like word extraction
            potential_concepts = [word for word in words if len(word) > 4 and word.isalpha()]
            concepts = list(set(potential_concepts))[:5]
        
        return concepts[:8]  # Return top 8 concepts
    
    def _generate_reasoning_step(self, synthesis_type: SynthesisType, 
                               key_concepts: List[str], input_thoughts: List[str]) -> str:
        """Generate reasoning step based on synthesis type"""
        templates = self.reasoning_templates.get(synthesis_type, ["Reasoning about the input..."])
        template = random.choice(templates)
        
        # Fill template with concepts and content
        filled_template = template
        for var, values in self.synthesis_content.items():
            placeholder = f"{{{var}}}"
            if placeholder in filled_template:
                filled_template = filled_template.replace(placeholder, random.choice(values))
        
        # Replace with actual key concepts if placeholders remain
        if "{key_concept}" in filled_template and key_concepts:
            filled_template = filled_template.replace("{key_concept}", random.choice(key_concepts))
        
        if "{thought_count}" in filled_template:
            filled_template = filled_template.replace("{thought_count}", str(len(input_thoughts)))
        
        return filled_template
    
    def _generate_insight(self, synthesis_type: SynthesisType, key_concepts: List[str], 
                         input_thoughts: List[str], creativity_boost: bool) -> str:
        """Generate the main insight from synthesis"""
        insight_patterns = {
            SynthesisType.PATTERN: [
                "The recurring pattern here is {pattern} across multiple thoughts",
                "I see a {pattern_type} emerging in the way these ideas connect",
                "There's a consistent theme of {concept} running through these thoughts"
            ],
            SynthesisType.ABSTRACTION: [
                "At a higher level, this is really about {abstract_concept}",
                "The meta-principle underlying these thoughts is {principle}",
                "Abstracting upward, the essence is {essence}"
            ],
            SynthesisType.CONNECTION: [
                "The key connection is between {concept1} and {concept2}",
                "These thoughts link through the concept of {linking_concept}",
                "The bridge connecting these ideas is {connection}"
            ],
            SynthesisType.ANALOGY: [
                "This is analogous to {analogy_source} in that both {similarity}",
                "Like {analogy_example}, this demonstrates {principle}",
                "The analogy reveals that {insight}"
            ],
            SynthesisType.HYPOTHESIS: [
                "My hypothesis is that {hypothesis_statement}",
                "What if {speculative_idea}? This could explain {phenomenon}",
                "A possible theory: {theory_statement}"
            ],
            SynthesisType.INSIGHT: [
                "The key insight is {insight_statement}",
                "I suddenly understand that {realization}",
                "It becomes clear that {clarity_statement}"
            ],
            SynthesisType.INTEGRATION: [
                "Integrating these perspectives yields {integrated_view}",
                "When combined, these ideas create {synthesis_result}",
                "The synthesis reveals {emergent_understanding}"
            ],
            SynthesisType.EMERGENCE: [
                "Something new is emerging: {emergent_property}",
                "The collective pattern shows {emergent_behavior}",
                "Out of this complexity arises {emergent_quality}"
            ]
        }
        
        patterns = insight_patterns.get(synthesis_type, ["A new understanding emerges from these thoughts"])
        base_insight = random.choice(patterns)
        
        # Fill with synthesis content
        filled_insight = base_insight
        for var, values in self.synthesis_content.items():
            placeholder = f"{{{var}}}"
            if placeholder in filled_insight:
                value = random.choice(values)
                # Apply creativity boost
                if creativity_boost and random.random() < 0.3:
                    # Add creative modifier
                    creative_modifiers = ["unexpectedly", "surprisingly", "intriguingly", "remarkably"]
                    value = f"{random.choice(creative_modifiers)} {value}"
                filled_insight = filled_insight.replace(placeholder, value)
        
        # Use key concepts if available
        if key_concepts and "{concept}" in filled_insight:
            filled_insight = filled_insight.replace("{concept}", random.choice(key_concepts))
        
        return filled_insight
    
    def _calculate_confidence(self, synthesis_type: SynthesisType, 
                            key_concepts: List[str], input_thoughts: List[str]) -> float:
        """Calculate confidence score for the synthesis"""
        base_confidence = 0.5
        
        # More concepts = higher confidence
        concept_bonus = min(0.3, len(key_concepts) * 0.05)
        
        # More input thoughts = higher confidence
        thought_bonus = min(0.2, len(input_thoughts) * 0.03)
        
        # Type-specific confidence modifiers
        type_modifiers = {
            SynthesisType.PATTERN: 0.1,
            SynthesisType.CONNECTION: 0.05,
            SynthesisType.INSIGHT: 0.0,
            SynthesisType.HYPOTHESIS: -0.1,
            SynthesisType.ABSTRACTION: 0.05,
            SynthesisType.ANALOGY: 0.0,
            SynthesisType.INTEGRATION: 0.05,
            SynthesisType.EMERGENCE: -0.05
        }
        
        type_modifier = type_modifiers.get(synthesis_type, 0.0)
        
        confidence = base_confidence + concept_bonus + thought_bonus + type_modifier
        return max(0.1, min(1.0, confidence))
    
    def _calculate_novelty(self, insight: str, input_thoughts: List[str]) -> float:
        """Calculate novelty score for the insight"""
        # Simple novelty calculation based on word overlap
        insight_words = set(insight.lower().split())
        input_words = set(' '.join(input_thoughts).lower().split())
        
        overlap = len(insight_words.intersection(input_words))
        total_insight_words = len(insight_words)
        
        if total_insight_words == 0:
            return 0.5
        
        novelty = 1.0 - (overlap / total_insight_words)
        return max(0.1, min(1.0, novelty))
    
    def _calculate_coherence(self, insight: str, input_thoughts: List[str]) -> float:
        """Calculate coherence score for the insight"""
        # Simple coherence based on some shared concepts
        insight_words = set(insight.lower().split())
        input_words = set(' '.join(input_thoughts).lower().split())
        
        overlap = len(insight_words.intersection(input_words))
        total_words = len(insight_words.union(input_words))
        
        if total_words == 0:
            return 0.5
        
        coherence = overlap / total_words
        return max(0.2, min(1.0, coherence * 2))  # Scale up coherence
    
    def _calculate_creativity(self, insight: str, synthesis_type: SynthesisType, 
                            creativity_boost: bool) -> float:
        """Calculate creativity level of the insight"""
        base_creativity = 0.4
        
        # Type-specific creativity scores
        type_creativity = {
            SynthesisType.EMERGENCE: 0.3,
            SynthesisType.ANALOGY: 0.25,
            SynthesisType.HYPOTHESIS: 0.25,
            SynthesisType.INSIGHT: 0.2,
            SynthesisType.CONNECTION: 0.15,
            SynthesisType.INTEGRATION: 0.1,
            SynthesisType.ABSTRACTION: 0.1,
            SynthesisType.PATTERN: 0.05
        }
        
        type_bonus = type_creativity.get(synthesis_type, 0.1)
        
        # Creativity boost from PARTIAL_WAKE mode
        boost = self.creativity_boost_partial if creativity_boost else 1.0
        
        # Random creativity factor
        random_factor = random.uniform(-0.1, 0.1)
        
        creativity = (base_creativity + type_bonus + random_factor) * boost
        return max(0.1, min(1.0, creativity))
    
    def _calculate_relevance(self, insight: str, context) -> float:
        """Calculate context relevance of the insight"""
        relevance_score = 0.5
        
        # Check relevance to current hypothesis
        if context.hypothesis and context.hypothesis in insight:
            relevance_score += 0.2
        
        # Check relevance to working memory
        if context.chunks:
            shared_concepts = 0
            for chunk in context.chunks[-3:]:
                if any(word in insight.lower() for word in chunk.lower().split()[:3]):
                    shared_concepts += 1
            relevance_score += min(0.3, shared_concepts * 0.1)
        
        return max(0.1, min(1.0, relevance_score))
    
    def _cache_pattern(self, synthesis: Synthesis):
        """Cache discovered patterns for future use"""
        if synthesis.synthesis_type == SynthesisType.PATTERN:
            pattern_key = f"pattern_{len(self.pattern_cache)}"
            self.pattern_cache[pattern_key] = synthesis.input_thoughts.copy()
    
    def _update_statistics(self, synthesis: Synthesis):
        """Update synthesizer statistics"""
        self.stats["total_syntheses"] += 1
        
        if synthesis.synthesis_type == SynthesisType.PATTERN:
            self.stats["successful_patterns"] += 1
        
        if synthesis.novelty_score > 0.7:
            self.stats["novel_insights"] += 1
        
        # Update averages
        total = self.stats["total_syntheses"]
        self.stats["average_confidence"] = ((self.stats["average_confidence"] * (total - 1)) + synthesis.confidence) / total
        self.stats["average_novelty"] = ((self.stats["average_novelty"] * (total - 1)) + synthesis.novelty_score) / total
        self.stats["average_creativity"] = ((self.stats["average_creativity"] * (total - 1)) + synthesis.creativity_level) / total
        
        # Count synthesis types
        type_name = synthesis.synthesis_type.value
        self.stats["synthesis_type_counts"][type_name] = self.stats["synthesis_type_counts"].get(type_name, 0) + 1
    
    def get_pattern_insights(self, thoughts: List[str]) -> List[str]:
        """Get insights about patterns in the given thoughts"""
        patterns = []
        
        if len(thoughts) < self.pattern_threshold:
            return patterns
        
        # Simple pattern detection
        word_frequency = {}
        for thought in thoughts:
            words = thought.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_frequency[word] = word_frequency.get(word, 0) + 1
        
        # Find repeated concepts
        frequent_words = [word for word, count in word_frequency.items() if count >= 2]
        if frequent_words:
            patterns.append(f"Recurring concepts: {', '.join(frequent_words[:5])}")
        
        # Detect conceptual themes
        theme_keywords = {
            "creativity": ["creative", "imagination", "art", "design", "innovation"],
            "cognition": ["think", "thought", "mind", "consciousness", "awareness"],
            "connection": ["connect", "relationship", "link", "bridge", "network"],
            "pattern": ["pattern", "structure", "organization", "system", "order"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in ' '.join(thoughts).lower() for keyword in keywords):
                patterns.append(f"Theme detected: {theme}")
        
        return patterns
    
    def get_stats(self) -> Dict[str, Any]:
        """Get synthesizer statistics"""
        stats = self.stats.copy()
        stats.update({
            "synthesis_history_count": len(self.synthesis_history),
            "cached_patterns": len(self.pattern_cache),
            "concept_associations": len(self.concept_associations)
        })
        return stats
    
    def get_recent_syntheses(self, count: int = 5) -> List[Synthesis]:
        """Get recent synthesis results"""
        return self.synthesis_history[-count:] if self.synthesis_history else []


# Helper function for testing
async def test_synthesizer():
    """Test the synthesizer functionality"""
    from .dmn_driver import DMNContext, SystemMode
    
    synthesizer = Synthesizer()
    
    # Mock context with thoughts
    context = DMNContext(
        mode=SystemMode.ACTIVE,
        chunks=[
            "I'm thinking about patterns in nature",
            "Trees branch in fractal patterns",
            "Rivers also branch and flow in patterns",
            "Maybe consciousness has similar patterns"
        ],
        intrusive_thoughts=[
            "What if thoughts are like water flowing?",
            "Suddenly thinking about music and rhythm"
        ],
        hypothesis="Patterns exist at multiple scales in natural systems"
    )
    
    print(" Testing Synthesizer...")
    
    # Test pattern recognition
    patterns = synthesizer.get_pattern_insights(context.chunks)
    print(f"🔍 Detected patterns: {patterns}")
    
    # Test synthesis generation with chain-of-thought
    synthesis = await synthesizer.generate_thoughts(context, chain_of_thought=True)
    if synthesis:
        print(f"\n Generated synthesis ({synthesis.synthesis_type.value}):")
        print(f"   Insight: {synthesis.output_insight}")
        print(f"   Confidence: {synthesis.confidence:.2f}")
        print(f"   Novelty: {synthesis.novelty_score:.2f}")
        print(f"   Creativity: {synthesis.creativity_level:.2f}")
        print(f"\n Chain of thought:")
        print(f"   {synthesis.chain_of_thought}")
    
    # Test synthesis with creativity boost (PARTIAL_WAKE mode)
    context.mode = SystemMode.PARTIAL_WAKE
    creative_synthesis = await synthesizer.generate_thoughts(context, creativity_boost=True)
    if creative_synthesis:
        print(f"\n🌟 Creative synthesis ({creative_synthesis.synthesis_type.value}):")
        print(f"   Insight: {creative_synthesis.output_insight}")
        print(f"   Creativity: {creative_synthesis.creativity_level:.2f}")
    
    # Get statistics
    stats = synthesizer.get_stats()
    print(f"\n Synthesizer stats: {stats}")
    
    print(" Synthesizer test completed")


if __name__ == "__main__":
    asyncio.run(test_synthesizer())
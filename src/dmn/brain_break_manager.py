"""
Brain Break Manager for Default Mode Network PARTIAL_WAKE mode

This component manages natural cognitive rest periods with creative free-association,
generating AI-powered associations to clear thought stagnation and
shift mood/environment through virtual activities.
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum

from .ai_thought_generator import AIThoughtGenerator, AIThoughtConfig

logger = logging.getLogger(__name__)


class BreakType(Enum):
    """Types of brain break activities"""
    CREATIVE_ASSOCIATION = "creative_association"
    VIRTUAL_WALK = "virtual_walk"
    INTERNET_BROWSE = "internet_browse"
    SENSORY_EXPLORATION = "sensory_exploration"
    ABSTRACT_THINKING = "abstract_thinking"
    MUSICAL_JOURNEY = "musical_journey"
    MEMORY_DRIFT = "memory_drift"
    IMAGINATIVE_PLAY = "imaginative_play"


@dataclass
class BrainBreak:
    """Represents a brain break activity session"""
    break_id: str
    break_type: BreakType
    start_time: datetime
    duration: timedelta
    activities: List[str] = field(default_factory=list)
    generated_associations: List[str] = field(default_factory=list)
    mood_shift_achieved: bool = False
    creativity_boost: float = 0.0
    environment_change: str = ""
    end_time: Optional[datetime] = None
    
    def is_complete(self) -> bool:
        """Check if the break is complete"""
        if self.end_time:
            return True
        elapsed = datetime.now() - self.start_time
        return elapsed >= self.duration


class BrainBreakManager:
    """
    Manages brain break activities during PARTIAL_WAKE mode.
    
    Responsibilities:
    - Schedule periodic breaks in intensive thinking
    - Trigger PARTIAL_WAKE mode after exhaustion signals
    - Generate enjoyable, abstract associations
    - Create shallow, rapid ideas for mood/environment shifting
    - Support virtual walks, internet browsing, random prompts
    - Indirectly modify memory state via new associative links
    """
    
    def __init__(self,
                 default_break_duration: float = 30.0,  # seconds
                 min_break_interval: float = 120.0,     # minimum time between breaks
                 creativity_boost_factor: float = 1.5,
                 ai_config: AIThoughtConfig = None):
        """
        Initialize the Brain Break Manager.
        
        Args:
            default_break_duration: Default duration of breaks in seconds
            min_break_interval: Minimum time between breaks
            creativity_boost_factor: Multiplier for creativity during breaks
            ai_config: Configuration for AI content generation
        """
        self.default_break_duration = default_break_duration
        self.min_break_interval = min_break_interval
        self.creativity_boost_factor = creativity_boost_factor
        
        # Initialize AI generator for break content
        self.ai_generator = AIThoughtGenerator(ai_config or AIThoughtConfig())
        
        # Current break state
        self.current_break: Optional[BrainBreak] = None
        self.last_break_time: Optional[datetime] = None
        self.break_history: List[BrainBreak] = []
        
        # Statistics
        self.stats = {
            "total_breaks": 0,
            "successful_mood_shifts": 0,
            "average_creativity_boost": 0.0,
            "most_used_break_type": None,
            "total_associations_generated": 0,
            "average_break_duration": 0.0
        }
        
        # Association templates and content
        self.association_templates = {
            BreakType.CREATIVE_ASSOCIATION: [
                "Imagine {concept1} dancing with {concept2}",
                "What if {object} had the personality of {emotion}?",
                "Picture {color} sound waves carrying {abstract_idea}",
                "Visualize {texture} made of {element} and {feeling}",
                "Connect {natural_phenomenon} to {human_activity}",
                "Blend {artistic_style} with {everyday_object}",
                "Transform {simple_action} into {magical_event}"
            ],
            BreakType.VIRTUAL_WALK: [
                "Strolling through a {environment} where {unusual_feature}",
                "Walking along {path_type} while observing {interesting_sight}",
                "Exploring {imaginary_place} filled with {whimsical_element}",
                "Wandering through {time_period} {location}",
                "Following {guide} through {mysterious_realm}",
                "Stepping carefully on {unusual_ground} under {sky_condition}",
                "Discovering {hidden_treasure} in {unexpected_place}"
            ],
            BreakType.SENSORY_EXPLORATION: [
                "Feel the {texture} of {element} against {body_part}",
                "Hear the {sound_quality} of {sound_source} in {acoustic_space}",
                "Taste the {flavor_profile} of {imaginary_food}",
                "Smell the {scent_quality} of {scent_source} mixed with {secondary_scent}",
                "See the {visual_quality} of {color_combination} {shape_description}",
                "Experience {synesthetic_sensation} when {trigger_event}",
                "Notice how {sensation} changes when {context_shift}"
            ],
            BreakType.ABSTRACT_THINKING: [
                "Contemplate the {philosophical_concept} of {abstract_noun}",
                "Wonder about the relationship between {idea1} and {idea2}",
                "Explore how {emotion} might look if it were {physical_form}",
                "Consider what {intangible_thing} would taste like",
                "Imagine {mathematical_concept} as {living_creature}",
                "Think about {temporal_concept} having {physical_property}",
                "Ponder the {metaphysical_question} of {existence_aspect}"
            ],
            BreakType.MUSICAL_JOURNEY: [
                "Listen to {imaginary_instrument} playing {musical_style}",
                "Hear {environmental_sound} harmonizing with {melody_type}",
                "Experience {rhythm_pattern} synchronized with {natural_rhythm}",
                "Imagine {emotion} expressed through {musical_technique}",
                "Create {sound_texture} by blending {sound1} and {sound2}",
                "Follow {musical_journey} from {starting_mood} to {ending_mood}",
                "Compose {musical_piece} inspired by {unusual_inspiration}"
            ],
            BreakType.MEMORY_DRIFT: [
                "Drift back to {nostalgic_moment} and notice {forgotten_detail}",
                "Remember {childhood_experience} with new {adult_perspective}",
                "Recall {sensory_memory} from {time_period}",
                "Revisit {emotional_memory} and feel {different_emotion}",
                "Connect {recent_event} to {distant_memory}",
                "Float through {memory_sequence} like {floating_metaphor}",
                "Rediscover {lost_memory} hidden in {memory_location}"
            ],
            BreakType.IMAGINATIVE_PLAY: [
                "Play with {toy_concept} that responds to {interaction_type}",
                "Build {imaginary_structure} using {unusual_material}",
                "Create {fantasy_scenario} where {impossible_rule}",
                "Design {magical_tool} that {magical_function}",
                "Invent {silly_game} involving {random_objects}",
                "Role-play as {fantasy_character} in {whimsical_situation}",
                "Construct {dream_world} governed by {dream_logic}"
            ]
        }
        
        # Content variables for templates
        self.content_variables = {
            "concept1": ["gravity", "music", "time", "laughter", "whispers", "shadows"],
            "concept2": ["butterflies", "moonlight", "equations", "memories", "colors", "dreams"],
            "object": ["chair", "cloud", "book", "tree", "mirror", "doorway"],
            "emotion": ["curiosity", "serenity", "playfulness", "wonder", "mischief", "wisdom"],
            "color": ["crystalline blue", "warm amber", "deep violet", "soft silver", "bright coral"],
            "abstract_idea": ["forgotten songs", "whispered secrets", "floating thoughts", "liquid time"],
            "texture": ["velvet", "liquid silk", "crystalline", "feathery", "ethereal", "prismatic"],
            "element": ["starlight", "ocean mist", "morning dew", "autumn breeze", "crystal"],
            "feeling": ["nostalgia", "anticipation", "contentment", "wonder", "tranquility"],
            "natural_phenomenon": ["aurora borealis", "ocean waves", "falling leaves", "sunrise"],
            "human_activity": ["writing poetry", "solving puzzles", "creating art", "telling stories"],
            "artistic_style": ["impressionist", "cubist", "watercolor", "mosaic", "origami"],
            "everyday_object": ["coffee cup", "pencil", "doorknob", "pillow", "bookmark"],
            "simple_action": ["turning a page", "lighting a candle", "opening a window"],
            "magical_event": ["stars rearranging", "colors singing", "time flowering"],
            
            "environment": ["crystal forest", "floating garden", "library of clouds", "musical meadow"],
            "unusual_feature": ["books grow on trees", "flowers ring like bells", "paths shift colors"],
            "path_type": ["winding cobblestone", "bridge of light", "stepping stones of music"],
            "interesting_sight": ["dancing shadows", "color-changing leaves", "singing stones"],
            "imaginary_place": ["city of mirrors", "valley of echoes", "mountain of stories"],
            "whimsical_element": ["floating lanterns", "giggling streams", "rainbow bridges"],
            "time_period": ["Victorian", "future", "medieval", "prehistoric", "steampunk"],
            "location": ["marketplace", "garden", "observatory", "workshop", "library"],
            "guide": ["wise owl", "friendly robot", "talking cat", "glowing orb", "gentle wind"],
            "mysterious_realm": ["dream dimension", "memory palace", "emotion landscape"],
            "unusual_ground": ["bouncy moss", "musical tiles", "cloud steps", "mirror surface"],
            "sky_condition": ["aurora lights", "floating islands", "cascading colors"],
            "hidden_treasure": ["bottle of laughter", "map of thoughts", "key to dreams"],
            "unexpected_place": ["inside a dewdrop", "behind a yawn", "within a melody"],
            
            "body_part": ["fingertips", "palms", "cheek", "forehead", "shoulder"],
            "sound_quality": ["crystalline", "velvety", "shimmering", "deep", "melodic"],
            "sound_source": ["wind chimes", "distant ocean", "flowing water", "bird songs"],
            "acoustic_space": ["cathedral", "forest clearing", "underwater cave", "crystal dome"],
            "flavor_profile": ["sweet complexity", "warm spiciness", "fresh brightness"],
            "imaginary_food": ["cloud cake", "rainbow soup", "stardust tea", "moonbeam pie"],
            "scent_quality": ["delicate", "rich", "fresh", "warm", "mysterious"],
            "scent_source": ["blooming jasmine", "old books", "ocean breeze", "cedar wood"],
            "secondary_scent": ["vanilla", "mint", "citrus", "lavender", "sage"],
            "visual_quality": ["shimmering", "flowing", "geometric", "organic", "luminous"],
            "color_combination": ["blue-green", "gold-purple", "silver-pink", "coral-turquoise"],
            "shape_description": ["spiraling upward", "flowing like water", "crystalline formations"],
            "synesthetic_sensation": ["seeing music", "tasting colors", "hearing textures"],
            "trigger_event": ["touching smooth stone", "hearing distant music", "seeing sunset"],
            "sensation": ["warmth", "smoothness", "lightness", "vibration", "coolness"],
            "context_shift": ["eyes close", "focus changes", "breathing deepens"],
            
            "philosophical_concept": ["essence", "nature", "possibility", "connection", "meaning"],
            "abstract_noun": ["beauty", "truth", "freedom", "creativity", "consciousness"],
            "idea1": ["pattern", "rhythm", "structure", "flow", "balance"],
            "idea2": ["chaos", "silence", "space", "energy", "potential"],
            "physical_form": ["flowing water", "growing plant", "dancing flame", "shifting cloud"],
            "intangible_thing": ["happiness", "silence", "possibility", "mystery", "hope"],
            "mathematical_concept": ["infinity", "fractal", "spiral", "symmetry", "proportion"],
            "living_creature": ["butterfly", "dolphin", "tree", "bird", "flower"],
            "temporal_concept": ["past", "future", "moment", "eternity", "change"],
            "physical_property": ["weight", "color", "texture", "temperature", "sound"],
            "metaphysical_question": ["purpose", "origin", "destiny", "meaning", "connection"],
            "existence_aspect": ["consciousness", "reality", "time", "space", "identity"],
            
            "imaginary_instrument": ["cloud harp", "crystal drums", "wind flute", "light piano"],
            "musical_style": ["ethereal ambient", "rhythmic cascades", "melodic whispers"],
            "environmental_sound": ["rustling leaves", "gentle rain", "distant waves"],
            "melody_type": ["ascending spirals", "gentle curves", "rhythmic pulses"],
            "rhythm_pattern": ["heartbeat tempo", "breathing rhythm", "walking pace"],
            "natural_rhythm": ["ocean waves", "bird calls", "wind gusts", "cricket songs"],
            "musical_technique": ["harmony", "counterpoint", "resonance", "improvisation"],
            "sound_texture": ["layered whispers", "flowing resonance", "crystalline echoes"],
            "sound1": ["soft rain", "distant bells", "gentle wind", "flowing water"],
            "sound2": ["bird songs", "string vibrations", "crystal chimes", "soft humming"],
            "musical_journey": ["ascending melody", "rhythmic adventure", "harmonic exploration"],
            "starting_mood": ["peaceful", "curious", "energetic", "contemplative"],
            "ending_mood": ["serene", "inspired", "refreshed", "content"],
            "musical_piece": ["gentle symphony", "playful composition", "ambient soundscape"],
            "unusual_inspiration": ["falling snow", "growing plants", "shifting clouds"],
            
            "nostalgic_moment": ["summer evening", "first snow", "birthday surprise"],
            "forgotten_detail": ["specific color", "background sound", "facial expression"],
            "childhood_experience": ["playground adventure", "bedtime story", "holiday tradition"],
            "adult_perspective": ["understanding", "appreciation", "new meaning", "deeper value"],
            "sensory_memory": ["taste of ice cream", "feeling of sand", "smell of rain"],
            "emotional_memory": ["excitement", "comfort", "joy", "wonder", "safety"],
            "different_emotion": ["gratitude", "understanding", "peace", "love", "wisdom"],
            "recent_event": ["conversation", "discovery", "realization", "moment of beauty"],
            "distant_memory": ["childhood friend", "old home", "favorite teacher", "beloved pet"],
            "memory_sequence": ["growing up", "learning", "friendship", "seasons changing"],
            "floating_metaphor": ["leaf on water", "cloud in sky", "note in air"],
            "lost_memory": ["forgotten name", "old song", "childhood game", "special place"],
            "memory_location": ["corner of mind", "heart's archive", "soul's library"],
            
            "toy_concept": ["shape-shifting blocks", "emotion marbles", "memory puzzles"],
            "interaction_type": ["gentle touch", "focused thought", "musical humming"],
            "imaginary_structure": ["bridge of light", "tower of books", "garden of ideas"],
            "unusual_material": ["solidified laughter", "woven starlight", "crystallized music"],
            "fantasy_scenario": ["underwater tea party", "flying library", "singing garden"],
            "impossible_rule": ["gravity flows upward", "time moves sideways", "colors make sounds"],
            "magical_tool": ["thought painter", "dream catcher", "memory weaver", "emotion lens"],
            "magical_function": ["captures wonder", "transforms sadness", "amplifies joy"],
            "silly_game": ["cloud tag", "shadow dancing", "color mixing", "echo catching"],
            "random_objects": ["spoons and starlight", "pillows and poetry", "buttons and breeze"],
            "fantasy_character": ["wise dragon", "curious sprite", "gentle giant", "clever fox"],
            "whimsical_situation": ["tea party with clouds", "hide and seek with shadows"],
            "dream_world": ["floating islands", "upside-down forest", "inside-out castle"],
            "dream_logic": ["thoughts become visible", "emotions have colors", "time is circular"]
        }
        
        # Statistics
        self.stats = {
            "total_breaks": 0,
            "successful_mood_shifts": 0,
            "average_creativity_boost": 0.0,
            "most_used_break_type": None,
            "total_associations_generated": 0,
            "average_break_duration": 0.0
        }
    
    async def generate_break_activities(self, context) -> List[str]:
        """
        Generate brain break activities based on current context.
        
        Args:
            context: Current DMN context
            
        Returns:
            List of break activity descriptions
        """
        # Choose break type based on context
        break_type = self._choose_break_type(context)
        
        # Generate break session
        break_session = await self._create_break_session(break_type, context)
        self.current_break = break_session
        
        # Generate activities for this break
        activities = await self._generate_activities(break_session, context)
        break_session.activities = activities
        
        # Generate creative associations
        associations = await self._generate_associations(break_session)
        break_session.generated_associations = associations
        
        # Calculate mood shift and creativity boost
        mood_shift = await self._calculate_mood_shift(break_session, context)
        break_session.mood_shift_achieved = mood_shift
        break_session.creativity_boost = self._calculate_creativity_boost(break_session)
        
        logger.info(f"🌙 Generated {break_type.value} break with {len(activities)} activities")
        
        return activities + associations
    
    def _choose_break_type(self, context) -> BreakType:
        """Choose appropriate break type based on context"""
        # Analyze exhaustion signals to choose appropriate break
        exhaustion_signals = context.exhaustion_signals
        
        weights = {
            BreakType.CREATIVE_ASSOCIATION: 2,
            BreakType.VIRTUAL_WALK: 2,
            BreakType.SENSORY_EXPLORATION: 1,
            BreakType.ABSTRACT_THINKING: 1,
            BreakType.MUSICAL_JOURNEY: 1,
            BreakType.MEMORY_DRIFT: 1,
            BreakType.IMAGINATIVE_PLAY: 1,
            BreakType.INTERNET_BROWSE: 1
        }
        
        # Adjust weights based on exhaustion signals
        if "repetitive_thoughts" in exhaustion_signals:
            weights[BreakType.CREATIVE_ASSOCIATION] = 4
            weights[BreakType.IMAGINATIVE_PLAY] = 3
        
        if "high_cognitive_load" in exhaustion_signals:
            weights[BreakType.SENSORY_EXPLORATION] = 3
            weights[BreakType.MUSICAL_JOURNEY] = 3
        
        if "working_memory_overload" in exhaustion_signals:
            weights[BreakType.VIRTUAL_WALK] = 4
            weights[BreakType.MEMORY_DRIFT] = 3
        
        # Choose based on weights
        choices = []
        for break_type, weight in weights.items():
            choices.extend([break_type] * weight)
        
        return random.choice(choices)
    
    async def _create_break_session(self, break_type: BreakType, context) -> BrainBreak:
        """Create a new break session"""
        import uuid
        
        duration = timedelta(seconds=self.default_break_duration)
        
        # Adjust duration based on exhaustion level
        exhaustion_level = len(context.exhaustion_signals) / 5.0  # Normalize to 0-1
        duration_multiplier = 1.0 + exhaustion_level * 0.5  # Up to 50% longer
        duration = timedelta(seconds=self.default_break_duration * duration_multiplier)
        
        break_session = BrainBreak(
            break_id=str(uuid.uuid4()),
            break_type=break_type,
            start_time=datetime.now(),
            duration=duration
        )
        
        self.stats["total_breaks"] += 1
        self.last_break_time = datetime.now()
        
        return break_session
    
    async def _generate_activities(self, break_session: BrainBreak, context) -> List[str]:
        """Generate AI-powered activities for the break session"""
        break_type = break_session.break_type
        
        # Ensure AI generator is initialized
        if not self.ai_generator.is_initialized:
            await self.ai_generator.initialize()
        
        try:
            # Use AI to generate activities
            activities = await self.ai_generator.generate_brain_break_content(break_type.value)
            return activities[:4]  # Limit to 4 activities
        except Exception as e:
            logger.warning(f"AI activity generation failed, using fallback: {e}")
            # Simple fallback activities
            return [
                f"Take a moment for {break_type.value} activity",
                f"Allow mind to wander with {break_type.value}",
                f"Engage in brief {break_type.value} experience"
            ]
    
    async def _generate_associations(self, break_session: BrainBreak) -> List[str]:
        """Generate creative associations during the break"""
        associations = []
        
        # Generate rapid, shallow associations for mood shifting
        association_count = random.randint(3, 6)
        
        for _ in range(association_count):
            # Choose random elements to associate
            concept1 = random.choice(self.content_variables["concept1"])
            concept2 = random.choice(self.content_variables["concept2"])
            color = random.choice(self.content_variables["color"])
            texture = random.choice(self.content_variables["texture"])
            
            # Create whimsical associations
            association_patterns = [
                f"If {concept1} were {color}, it would feel like {texture}",
                f"Connecting {concept1} to {concept2} through {color} pathways",
                f"Imagine {concept1} and {concept2} having a conversation in {color}",
                f"The {texture} bridge between {concept1} and {concept2}",
                f"When {concept1} dreams, it sees {concept2} in {color}"
            ]
            
            association = random.choice(association_patterns)
            associations.append(association)
        
        self.stats["total_associations_generated"] += len(associations)
        return associations
    
    async def _calculate_mood_shift(self, break_session: BrainBreak, context) -> bool:
        """Calculate if the break achieved a mood shift"""
        # Factors that contribute to mood shift
        factors = []
        
        # Variety of activities
        if len(break_session.activities) >= 3:
            factors.append("activity_variety")
        
        # Creative associations
        if len(break_session.generated_associations) >= 4:
            factors.append("rich_associations")
        
        # Break type effectiveness
        if break_session.break_type in [BreakType.CREATIVE_ASSOCIATION, BreakType.IMAGINATIVE_PLAY]:
            factors.append("creative_type")
        
        # Context appropriateness
        if "repetitive_thoughts" in context.exhaustion_signals and break_session.break_type == BreakType.CREATIVE_ASSOCIATION:
            factors.append("context_match")
        
        # Random success factor
        if random.random() < 0.7:  # 70% base success rate
            factors.append("natural_shift")
        
        success = len(factors) >= 2
        if success:
            self.stats["successful_mood_shifts"] += 1
        
        return success
    
    def _calculate_creativity_boost(self, break_session: BrainBreak) -> float:
        """Calculate creativity boost from the break"""
        base_boost = 0.2  # 20% base boost
        
        # Break type multipliers
        type_multipliers = {
            BreakType.CREATIVE_ASSOCIATION: 1.5,
            BreakType.IMAGINATIVE_PLAY: 1.4,
            BreakType.ABSTRACT_THINKING: 1.3,
            BreakType.MUSICAL_JOURNEY: 1.2,
            BreakType.SENSORY_EXPLORATION: 1.1,
            BreakType.VIRTUAL_WALK: 1.0,
            BreakType.MEMORY_DRIFT: 0.9,
            BreakType.INTERNET_BROWSE: 0.8
        }
        
        multiplier = type_multipliers.get(break_session.break_type, 1.0)
        
        # Activity and association bonuses
        activity_bonus = len(break_session.activities) * 0.05
        association_bonus = len(break_session.generated_associations) * 0.03
        
        # Mood shift bonus
        mood_bonus = 0.1 if break_session.mood_shift_achieved else 0.0
        
        total_boost = (base_boost + activity_bonus + association_bonus + mood_bonus) * multiplier
        
        # Apply creativity boost factor and cap at 2.0 (200% boost)
        final_boost = min(2.0, total_boost * self.creativity_boost_factor)
        
        # Update statistics
        current_avg = self.stats.get("average_creativity_boost", 0.0)
        total_breaks = self.stats.get("total_breaks", 1)
        self.stats["average_creativity_boost"] = ((current_avg * (total_breaks - 1)) + final_boost) / total_breaks
        
        return final_boost
    
    def complete_current_break(self):
        """Mark the current break as complete"""
        if self.current_break:
            self.current_break.end_time = datetime.now()
            self.break_history.append(self.current_break)
            
            # Update statistics
            duration = (self.current_break.end_time - self.current_break.start_time).total_seconds()
            current_avg = self.stats.get("average_break_duration", 0.0)
            total_breaks = self.stats.get("total_breaks", 1)
            self.stats["average_break_duration"] = ((current_avg * (total_breaks - 1)) + duration) / total_breaks
            
            # Update most used break type
            type_counts = {}
            for break_session in self.break_history:
                break_type = break_session.break_type.value
                type_counts[break_type] = type_counts.get(break_type, 0) + 1
            
            if type_counts:
                self.stats["most_used_break_type"] = max(type_counts, key=type_counts.get)
            
            logger.info(f"🏁 Completed break: {self.current_break.break_type.value}")
            self.current_break = None
    
    def get_current_break(self) -> Optional[BrainBreak]:
        """Get the current active break session"""
        return self.current_break
    
    def is_break_time(self, last_break_time: Optional[datetime] = None) -> bool:
        """Check if it's time for a break"""
        if not last_break_time:
            last_break_time = self.last_break_time
        
        if not last_break_time:
            return True  # First break
        
        time_since_break = (datetime.now() - last_break_time).total_seconds()
        return time_since_break >= self.min_break_interval
    
    def get_environment_change_suggestions(self) -> List[str]:
        """Get suggestions for environment changes during breaks"""
        suggestions = [
            "Imagine changing the lighting to soft, warm tones",
            "Picture opening a window to let in fresh air and natural sounds",
            "Visualize rearranging the space for better energy flow",
            "Think about adding plants or natural elements to the environment",
            "Consider playing gentle, ambient background music",
            "Imagine the temperature becoming perfectly comfortable",
            "Picture adding artwork or inspiring visuals to the space",
            "Visualize clearing clutter and creating more open space"
        ]
        
        return random.sample(suggestions, random.randint(2, 4))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get brain break manager statistics"""
        stats = self.stats.copy()
        stats.update({
            "current_break_active": self.current_break is not None,
            "breaks_in_history": len(self.break_history),
            "last_break_time": self.last_break_time.isoformat() if self.last_break_time else None,
            "time_since_last_break": (datetime.now() - self.last_break_time).total_seconds() if self.last_break_time else None
        })
        
        if self.current_break:
            stats["current_break_type"] = self.current_break.break_type.value
            stats["current_break_duration"] = (datetime.now() - self.current_break.start_time).total_seconds()
        
        return stats


# Helper function for testing
async def test_brain_break_manager():
    """Test the brain break manager"""
    from .dmn_driver import DMNContext, SystemMode
    
    manager = BrainBreakManager(default_break_duration=15.0)
    
    # Mock context with exhaustion signals
    context = DMNContext(
        mode=SystemMode.PARTIAL_WAKE,
        exhaustion_signals=["repetitive_thoughts", "high_cognitive_load"],
        working_memory_load=0.8
    )
    
    print("🌙 Testing Brain Break Manager...")
    
    # Generate break activities
    activities = await manager.generate_break_activities(context)
    
    print(f"🎯 Generated {len(activities)} break activities:")
    for i, activity in enumerate(activities, 1):
        print(f"   {i}. {activity}")
    
    current_break = manager.get_current_break()
    if current_break:
        print(f"\n🔄 Current break: {current_break.break_type.value}")
        print(f"   Duration: {current_break.duration.total_seconds()}s")
        print(f"   Mood shift achieved: {current_break.mood_shift_achieved}")
        print(f"   Creativity boost: {current_break.creativity_boost:.2f}")
    
    # Get environment change suggestions
    env_suggestions = manager.get_environment_change_suggestions()
    print(f"\n🏠 Environment change suggestions:")
    for suggestion in env_suggestions:
        print(f"   - {suggestion}")
    
    # Complete the break
    manager.complete_current_break()
    
    # Get statistics
    stats = manager.get_stats()
    print(f"\n📊 Brain Break Manager stats: {stats}")
    
    print("✅ Brain Break Manager test completed")


if __name__ == "__main__":
    asyncio.run(test_brain_break_manager())
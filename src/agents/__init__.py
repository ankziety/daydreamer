"""
Agents Package
Contains intelligent agent implementations
"""

from .agent import Agent, AgentConfig, AgentState, AgentEvent

# Import intelligent agent components conditionally to avoid import issues
try:
    from .intelligent_agent import IntelligentAgent, AgentConfig as IntelligentAgentConfig, AgentState as IntelligentAgentState, AgentMemory
    __all__ = [
        "Agent", 
        "AgentConfig", 
        "AgentState", 
        "AgentEvent",
        "IntelligentAgent", 
        "IntelligentAgentConfig", 
        "IntelligentAgentState", 
        "AgentMemory"
    ]
except ImportError:
    __all__ = [
        "Agent", 
        "AgentConfig", 
        "AgentState", 
        "AgentEvent"
    ]
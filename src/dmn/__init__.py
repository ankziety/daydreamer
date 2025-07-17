"""
Default Mode Network (DMN) module for Daydreamer Project

This module implements the core DMN architecture with three cognitive modes:
- ACTIVE: Full reasoning, chain-of-thought ON, memory read/write
- PARTIAL_WAKE: Brain break mode, creative associations
- DEFAULT: Sleep mode, memory consolidation only

The DMN system allows AI agents to have intrusive thoughts and random ideas 
that express themselves naturally, similar to biological DMN processes.
"""

from .dmn_driver import DMNDriver, SystemMode, DMNContext
from .intrusive_thoughts import IntrusiveThoughtsSystem, IntrusiveThought
from .brain_break_manager import BrainBreakManager, BrainBreak
from .synthesizer import Synthesizer, Synthesis
from .memory_curator import DMNMemoryCurator

__all__ = [
    'DMNDriver',
    'SystemMode', 
    'DMNContext',
    'IntrusiveThoughtsSystem',
    'IntrusiveThought',
    'BrainBreakManager',
    'BrainBreak',
    'Synthesizer',
    'Synthesis',
    'DMNMemoryCurator'
]
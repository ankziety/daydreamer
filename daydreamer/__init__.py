"""
Daydreamer: A Default Mode Network AI

This package implements a neural network architecture inspired by the brain's
default mode network, capable of self-prompting thoughts and generating 
coherent streams of consciousness using biological-inspired algorithms.
"""

__version__ = "0.1.0"
__author__ = "ankziety"

from .core import DefaultModeNetwork, ThoughtGenerator
from .models import AttentionNetwork, MemoryBuffer
from .utils import load_model, save_model

__all__ = [
    "DefaultModeNetwork",
    "ThoughtGenerator", 
    "AttentionNetwork",
    "MemoryBuffer",
    "load_model",
    "save_model",
]
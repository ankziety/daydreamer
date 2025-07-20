#!/usr/bin/env python3
"""
Daydreamer AI - Main Entry Point
================================

Main entry point for the Daydreamer AI system after directory restructuring.
This file provides easy access to the system from the root directory.
"""

import sys
import os

# Add src and src/core directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ai_engines'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'memory'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'integration'))

# Import and run the main function
if __name__ == "__main__":
    from core.daydreamer_ai import main as daydreamer_main
    daydreamer_main()
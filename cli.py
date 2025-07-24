#!/usr/bin/env python3
"""
Daydreamer AI - CLI Entry Point
===============================

CLI entry point for the Daydreamer AI system after directory restructuring.
This file provides easy access to the CLI from the root directory.
"""

import sys
import os

# Add src and subdirectories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ai_engines'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'memory'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'integration'))

from cli.cli import main

if __name__ == "__main__":
    # Run the CLI
    main()
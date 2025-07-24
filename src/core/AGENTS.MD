# Core Module - Agent Information

## Overview
Core module contains the main Daydreamer AI system components and interface. This is the central coordination point for all AI functionality.

## Components
- `daydreamer_ai.py` - Main AI system class that integrates all components
- `prompts.py` - Prompt templates and management for all AI interactions

## Current Status
- Files moved from root directory
- Import paths need updating
- Main entry point needs updating

## Active Tasks
1. Update import statements to reflect new directory structure
2. Update configuration file paths
3. Update database path references
4. Test core functionality after restructuring

## Dependencies
- `src/ai_engines/` - Chain of thought and daydreaming engines
- `src/memory/` - Memory management system
- `src/integration/` - Model integration
- `src/config/` - Configuration files

## Rules for Core Module
- Maintain clean interfaces between components
- Ensure proper error handling and fallbacks
- Keep the main AI class as the central coordinator
- Update all import paths to use relative imports

## Important Notes
- The main DaydreamerAI class is the entry point for the system
- All other modules are imported and used by the core module
- Configuration paths need to be updated to point to src/config/
- Database paths need to be updated to point to src/memory/

## Next Steps
1. Update import statements in daydreamer_ai.py
2. Update import statements in prompts.py
3. Test core functionality
4. Update main entry points
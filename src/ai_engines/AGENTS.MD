# AI Engines Module - Agent Information

## Overview
AI Engines module contains the core reasoning and creative thinking components: Chain of Thought processor and Daydreaming engine.

## Components
- `chain_of_thought.py` - True chain of thought reasoning through recursive self-prompting
- `day_dreaming.py` - Creative daydreaming technique for generating novel insights

## Current Status
- Files moved from root directory
- Import paths need updating
- Both engines are functional but need path updates

## Active Tasks
1. Update import statements to reflect new directory structure
2. Update prompts import path
3. Test both engines after restructuring
4. Ensure proper integration with core module

## Dependencies
- `src/core/prompts.py` - Prompt templates
- `src/integration/` - Model integration for AI calls
- `src/memory/` - Memory system for daydreaming context

## Rules for AI Engines
- Maintain separation between chain of thought and daydreaming logic
- Ensure proper error handling for model failures
- Keep engines modular and testable
- Update all import paths to use relative imports

## Important Notes
- ChainOfThoughtProcessor handles recursive reasoning
- DaydreamingEngine generates creative insights using random memories
- Both engines depend on the model integration module
- Daydreaming engine uses memory system for context

## Next Steps
1. Update import statements in chain_of_thought.py
2. Update import statements in day_dreaming.py
3. Test both engines independently
4. Test integration with core module
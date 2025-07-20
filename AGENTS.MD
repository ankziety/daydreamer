# Daydreamer AI - Agent Coordination

## Project Overview
Daydreamer AI is an advanced conversational AI system that implements true chain-of-thought reasoning and creative daydreaming techniques. The system provides persistent memory, adaptive learning, and integration with multiple AI model backends.

## Directory Structure
- `src/core/` - Core AI system components and main interface
- `src/ai_engines/` - Chain of thought and daydreaming engines
- `src/memory/` - Persistent memory management system
- `src/integration/` - Model integration (Ollama, Transformers)
- `src/config/` - Configuration files and settings
- `src/cli/` - Command-line interface components
- `src/utils/` - Utility functions and helpers
- `tests/` - Test suite
- `docs/` - Documentation
- `.agents/` - Agent progress tracking (not committed to main)

## Current Status
- Directory restructuring completed
- Core modules organized by functionality
- AGENTS.MD system being implemented

## Active Tasks
1. Update import paths in all modules after restructuring
2. Create AGENTS.MD files for each subdirectory
3. Update configuration paths
4. Create progress tracking in .agents directory
5. Update main entry points

## Rules for Agents
- Always check the .agents directory for current progress before starting work
- Update progress files when completing tasks
- Follow the established directory structure
- Maintain backward compatibility during refactoring
- Test changes before committing

## Important Notes
- The .agents directory and AGENTS.MD files should not be committed to main branch
- All configuration paths need updating after restructuring
- Import statements need to be updated across all modules
- Database path references need updating

## Next Steps
1. Create AGENTS.MD files for each subdirectory
2. Update import paths in all Python files
3. Test the restructured system
4. Update documentation
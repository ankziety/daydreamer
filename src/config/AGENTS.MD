# Config Module - Agent Information

## Overview
Config module contains all configuration files and settings for the Daydreamer AI system.

## Components
- `research_config.ini` - Main configuration file for AI models and system settings

## Current Status
- Files moved from root directory
- Configuration paths need updating in code
- All settings are preserved

## Active Tasks
1. Update configuration file paths in code
2. Test configuration loading after restructuring
3. Ensure all modules can access config properly
4. Update default paths in configuration

## Dependencies
- Core system for configuration loading
- All modules that need configuration settings

## Rules for Config Module
- Keep configuration files well-documented
- Maintain backward compatibility when possible
- Update all path references to reflect new structure
- Ensure configuration is accessible to all modules

## Important Notes
- Configuration file is now in src/config/ directory
- All code that loads configuration needs path updates
- Configuration includes model settings, research settings, and interface settings
- Used by core system and AI engines

## Next Steps
1. Update configuration file paths in all modules
2. Test configuration loading
3. Update default paths in configuration
4. Verify all settings are accessible
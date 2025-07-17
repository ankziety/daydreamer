# Daydreamer Project - Organizer Agent System

This directory contains the task organization and assignment system for the Daydreamer project. The Organizer Agent breaks down high-level modules into discrete, well-scoped tasks suitable for parallel development.

## Quick Start for Builders

### 1. Identify Your Team
First, determine which builder team you belong to:

- **Builder Team A**: Core Engine & AI Integration
- **Builder Team B**: Scheduler & Communication  
- **Builder Team C**: Memory System & Intelligence
- **Builder Team D**: UI System & Interfaces

### 2. Get Your Tasks
Use the task assignment script to retrieve your assigned tasks:

```bash
# From the project root directory
./organizer/get_tasks.sh "Builder Team A"
```

### 3. Get Detailed Task Information
To see the full builder prompt and requirements:

```bash
./organizer/get_tasks.sh "Builder Team A" --detailed
```

### 4. Get Specific Task Details
To view details for a specific task:

```bash
./organizer/get_tasks.sh --task CE-001
```

### 5. Create Standalone Task File
To create a markdown file with all task information:

```bash
./organizer/get_tasks.sh --task CE-001 --create-file
```

## Available Commands

### List All Teams
```bash
./organizer/get_tasks.sh --list-teams
```

### View Team Tasks
```bash
./organizer/get_tasks.sh "Builder Team A"
./organizer/get_tasks.sh "Builder Team B"
./organizer/get_tasks.sh "Builder Team C"
./organizer/get_tasks.sh "Builder Team D"
```

### View Detailed Task Information
```bash
./organizer/get_tasks.sh "Builder Team A" --detailed
```

### View Specific Task
```bash
./organizer/get_tasks.sh --task CE-001
./organizer/get_tasks.sh --task MS-001
./organizer/get_tasks.sh --task SC-001
```

### Create Task File
```bash
./organizer/get_tasks.sh --task CE-001 --create-file
```

## Task Structure

Each task contains the following information:

- **Task ID**: Unique identifier (e.g., CE-001, MS-001)
- **Description**: Brief description of the task
- **Workstream**: Which major system this belongs to
- **Priority**: High, Medium, or Low
- **Assigned Team**: Which builder team is responsible
- **Estimated Hours**: Time estimate for completion
- **Dependencies**: Other tasks that must be completed first
- **Git Branch**: Branch to work on (always `dev`)
- **Builder Prompt**: Detailed instructions and requirements

## Workstreams

### Core Engine (CE)
- **CE-001**: Implement core Agent class with basic lifecycle management
- **CE-002**: Implement Simulation Engine with time management
- **CE-003**: Create Agent Communication Protocol

### Memory System (MS)
- **MS-001**: Implement Memory Store with persistence
- **MS-002**: Implement Working Memory Manager

### Scheduler (SC)
- **SC-001**: Implement Task Scheduler with priority queues
- **SC-002**: Create Resource Manager

### UI System (UI)
- **UI-001**: Create Web Dashboard for simulation monitoring
- **UI-002**: Implement CLI interface for system control

### AI Integration (AI)
- **AI-001**: Implement AI Model Integration Layer
- **AI-002**: Create Agent Intelligence Framework

## Git Workflow

For each task, follow these Git instructions:

```bash
# 1. Checkout the dev branch
git checkout dev

# 2. Pull latest changes
git pull origin dev

# 3. Create feature branch
git checkout -b feature/TASK-ID-lowercase

# 4. Push and set upstream
git push -u origin feature/TASK-ID-lowercase
```

Example for task CE-001:
```bash
git checkout dev
git pull origin dev
git checkout -b feature/ce-001-core-agent-class
git push -u origin feature/ce-001-core-agent-class
```

## Task Dependencies

Tasks are organized with dependencies to ensure proper development order:

- **CE-001** (Agent class) has no dependencies
- **CE-002** (Simulation Engine) depends on **CE-001**
- **CE-003** (Communication) depends on **CE-001**
- **MS-001** (Memory Store) has no dependencies
- **MS-002** (Working Memory) depends on **MS-001**
- **SC-001** (Task Scheduler) depends on **CE-001**
- **SC-002** (Resource Manager) depends on **SC-001**
- **UI-001** (Web Dashboard) depends on **CE-002**
- **UI-002** (CLI Interface) depends on **CE-002**
- **AI-001** (Model Integration) depends on **CE-001**
- **AI-002** (Intelligence Framework) depends on **AI-001** and **MS-001**

## Builder Team Assignments

### Builder Team A (High Capacity)
- **Focus**: Core Engine & AI Integration
- **Tasks**: CE-001, CE-002, AI-001
- **Total Hours**: 64 hours

### Builder Team B (Medium Capacity)
- **Focus**: Scheduler & Communication
- **Tasks**: CE-003, SC-001, SC-002
- **Total Hours**: 44 hours

### Builder Team C (Medium Capacity)
- **Focus**: Memory System & Intelligence
- **Tasks**: MS-001, MS-002, AI-002
- **Total Hours**: 80 hours

### Builder Team D (Low Capacity)
- **Focus**: UI System & Interfaces
- **Tasks**: UI-001, UI-002
- **Total Hours**: 48 hours

## Getting Started

1. **Identify your team** from the list above
2. **Run the task assignment script** to see your tasks
3. **Review the builder prompt** for each task
4. **Check dependencies** to ensure prerequisites are met
5. **Create your feature branch** using the provided Git instructions
6. **Start implementing** according to the detailed requirements

## Support

If you need clarification on any task or have questions about the system:

1. Review the builder prompt carefully - it contains all necessary information
2. Check the task dependencies to understand the development order
3. Use the `--detailed` flag to see full task information
4. Create a standalone task file for offline reference

## File Structure

```
organizer/
├── README.md                 # This file
├── task_registry.json        # Main task database
├── builder_assignment.py     # Python task assignment system
└── get_tasks.sh             # Shell script wrapper
```

The system is designed to be self-contained and provide all necessary information for builders to begin work immediately without further clarification.
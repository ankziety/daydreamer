# Daydreamer

An attempt to create a default mode network AI that can self prompt thoughts using similar algorithms to biological processes.

## 🚀 Quick Start for Builders

If you're a builder working on the Daydreamer project, here's how to get started:

### 1. Identify Your Team
Run the builder setup script to identify your team and get your assigned tasks:

```bash
./organizer/setup_builder.sh
```

This will guide you through an interactive process to:
- Select your builder team
- View your assigned tasks
- Get personalized recommendations

### 2. View Your Tasks
Once you know your team, you can view your tasks:

```bash
# List all available teams
./organizer/get_tasks.sh --list-teams

# View tasks for your team
./organizer/get_tasks.sh "Builder Team A"

# View detailed task information
./organizer/get_tasks.sh "Builder Team A" --detailed

# View a specific task
./organizer/get_tasks.sh --task CE-001
```

### 3. Available Builder Teams

- **Builder Team A**: Core Engine & AI Integration (High Capacity)
- **Builder Team B**: Scheduler & Communication (Medium Capacity)
- **Builder Team C**: Memory System & Intelligence (Medium Capacity)
- **Builder Team D**: UI System & Interfaces (Low Capacity)

## 📋 Project Overview

The Daydreamer project is organized into several key workstreams:

### Core Engine (CE)
- Agent lifecycle management
- Simulation engine with time management
- Agent communication protocols

### Memory System (MS)
- Long-term memory storage with persistence
- Working memory management
- Memory consolidation and retrieval

### Scheduler (SC)
- Task scheduling with priority queues
- Resource management and allocation
- Dependency resolution

### UI System (UI)
- Web dashboard for simulation monitoring
- CLI interface for system control
- Real-time visualization

### AI Integration (AI)
- AI model integration layer
- Agent intelligence framework
- Behavior trees and decision-making

## 🛠️ Development Workflow

1. **Setup**: Run `./organizer/setup_builder.sh` to identify your team
2. **Review**: Use `./organizer/get_tasks.sh` to view your assigned tasks
3. **Branch**: Create feature branches from the `dev` branch
4. **Implement**: Follow the detailed builder prompts for each task
5. **Test**: Write tests and documentation as specified
6. **Merge**: Submit pull requests to the `dev` branch

## 📁 Project Structure

```
daydreamer/
├── organizer/                 # Task organization system
│   ├── task_registry.json    # Main task database
│   ├── builder_assignment.py # Task assignment system
│   ├── builder_setup.py      # Builder identification
│   ├── get_tasks.sh         # Task viewing script
│   ├── setup_builder.sh     # Builder setup script
│   └── README.md            # Organizer documentation
├── tasks/                    # Generated task files
└── README.md                # This file
```

## 🎯 Getting Help

- **Task Information**: Use `./organizer/get_tasks.sh --task <TASK-ID>` for detailed task info
- **Team Overview**: Use `./organizer/get_tasks.sh --list-teams` to see all teams
- **Setup Issues**: Run `./organizer/setup_builder.sh --reset` to reconfigure
- **Documentation**: Check `organizer/README.md` for detailed organizer system docs

## 🌟 Contributing

This project uses a structured task assignment system to coordinate parallel development. Each builder is assigned to a specific team with focused responsibilities. The organizer system ensures that all tasks are well-scoped, properly documented, and ready for immediate implementation.

For more information about the organizer system and task management, see the [organizer documentation](organizer/README.md).

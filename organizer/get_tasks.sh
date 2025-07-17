#!/bin/bash

# Daydreamer Builder Task Assignment Script
# Usage: ./get_tasks.sh <team_name> [options]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
show_usage() {
    echo -e "${BLUE}Daydreamer Builder Task Assignment System${NC}"
    echo "=================================================="
    echo ""
    echo "Usage:"
    echo "  ./get_tasks.sh <team_name> [options]"
    echo ""
    echo "Options:"
    echo "  --detailed          Show detailed task information"
    echo "  --task <task_id>    Show details for specific task"
    echo "  --create-file       Create standalone task file"
    echo "  --list-teams        List all available teams"
    echo ""
    echo "Examples:"
    echo "  ./get_tasks.sh 'Builder Team A'"
    echo "  ./get_tasks.sh 'Builder Team A' --detailed"
    echo "  ./get_tasks.sh --task CE-001"
    echo "  ./get_tasks.sh --task CE-001 --create-file"
    echo "  ./get_tasks.sh --list-teams"
    echo ""
    echo "Available Teams:"
    echo "  - Builder Team A (Core Engine & AI Integration)"
    echo "  - Builder Team B (Scheduler & Communication)"
    echo "  - Builder Team C (Memory System & Intelligence)"
    echo "  - Builder Team D (UI System & Interfaces)"
}

# Check if Python script exists
if [ ! -f "organizer/builder_assignment.py" ]; then
    echo -e "${RED}Error: builder_assignment.py not found in organizer directory${NC}"
    exit 1
fi

# Check if task registry exists
if [ ! -f "organizer/task_registry.json" ]; then
    echo -e "${RED}Error: task_registry.json not found in organizer directory${NC}"
    exit 1
fi

# If no arguments provided, show usage
if [ $# -eq 0 ]; then
    show_usage
    exit 0
fi

# Change to the organizer directory and run the Python script
cd "$(dirname "$0")"
python3 builder_assignment.py "$@"
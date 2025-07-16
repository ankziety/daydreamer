#!/bin/bash

# Daydreamer Builder Setup Script
# Usage: ./setup_builder.sh [--reset]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
show_usage() {
    echo -e "${BLUE}Daydreamer Builder Setup System${NC}"
    echo "====================================="
    echo ""
    echo "Usage:"
    echo "  ./setup_builder.sh [options]"
    echo ""
    echo "Options:"
    echo "  --reset    Reset your builder configuration"
    echo ""
    echo "This script will help you identify your team and get started with your tasks."
    echo ""
    echo "Available Teams:"
    echo "  - Builder Team A (Core Engine & AI Integration)"
    echo "  - Builder Team B (Scheduler & Communication)"
    echo "  - Builder Team C (Memory System & Intelligence)"
    echo "  - Builder Team D (UI System & Interfaces)"
}

# Check if Python script exists
if [ ! -f "organizer/builder_setup.py" ]; then
    echo -e "${RED}Error: builder_setup.py not found in organizer directory${NC}"
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
    echo ""
    echo -e "${YELLOW}Starting interactive setup...${NC}"
    echo ""
fi

# Change to the organizer directory and run the Python script
cd "$(dirname "$0")"
python3 builder_setup.py "$@"
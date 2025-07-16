#!/usr/bin/env python3
"""
Daydreamer Project - Builder Assignment System
Allows builders to identify themselves and retrieve their assigned tasks.
"""

import json
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

class BuilderAssignmentSystem:
    def __init__(self, task_registry_path: str = "task_registry.json"):
        self.task_registry_path = task_registry_path
        self.task_registry = self._load_task_registry()
        
    def _load_task_registry(self) -> Dict:
        """Load the task registry from JSON file."""
        try:
            with open(self.task_registry_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Task registry not found at {self.task_registry_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in task registry {self.task_registry_path}")
            sys.exit(1)
    
    def get_builder_tasks(self, team_name: str) -> List[Dict]:
        """Get all tasks assigned to a specific builder team."""
        tasks = []
        for workstream_name, workstream in self.task_registry["workstreams"].items():
            for task in workstream["tasks"]:
                if task["assigned_to"] == team_name:
                    task["workstream"] = workstream_name
                    task["workstream_name"] = workstream["name"]
                    tasks.append(task)
        return tasks
    
    def get_available_teams(self) -> List[str]:
        """Get list of available builder teams."""
        return list(self.task_registry["builder_teams"].keys())
    
    def get_team_info(self, team_name: str) -> Optional[Dict]:
        """Get information about a specific team."""
        return self.task_registry["builder_teams"].get(team_name)
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by its ID."""
        for workstream_name, workstream in self.task_registry["workstreams"].items():
            for task in workstream["tasks"]:
                if task["task_id"] == task_id:
                    task["workstream"] = workstream_name
                    task["workstream_name"] = workstream["name"]
                    return task
        return None
    
    def get_dependent_tasks(self, task_id: str) -> List[Dict]:
        """Get all tasks that depend on the given task."""
        dependent_tasks = []
        for workstream_name, workstream in self.task_registry["workstreams"].items():
            for task in workstream["tasks"]:
                if task_id in task.get("dependencies", []):
                    task["workstream"] = workstream_name
                    task["workstream_name"] = workstream["name"]
                    dependent_tasks.append(task)
        return dependent_tasks
    
    def display_team_tasks(self, team_name: str, detailed: bool = False):
        """Display all tasks for a team in a formatted way."""
        tasks = self.get_builder_tasks(team_name)
        team_info = self.get_team_info(team_name)
        
        if not team_info:
            print(f"Error: Team '{team_name}' not found.")
            return
        
        print(f"\n{'='*80}")
        print(f"BUILDER TEAM: {team_name}")
        print(f"Focus: {team_info['focus']}")
        print(f"Capacity: {team_info['capacity']}")
        print(f"Total Tasks: {len(tasks)}")
        print(f"{'='*80}")
        
        if not tasks:
            print("No tasks assigned to this team.")
            return
        
        # Group tasks by priority
        high_priority = [t for t in tasks if t["priority"] == "High"]
        medium_priority = [t for t in tasks if t["priority"] == "Medium"]
        low_priority = [t for t in tasks if t["priority"] == "Low"]
        
        for priority, task_list in [("HIGH PRIORITY", high_priority), 
                                   ("MEDIUM PRIORITY", medium_priority), 
                                   ("LOW PRIORITY", low_priority)]:
            if task_list:
                print(f"\n{priority} ({len(task_list)} tasks):")
                print("-" * 50)
                
                for task in task_list:
                    print(f"\nTask ID: {task['task_id']}")
                    print(f"Description: {task['description']}")
                    print(f"Workstream: {task['workstream_name']}")
                    print(f"Estimated Hours: {task['estimated_hours']}")
                    print(f"Dependencies: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
                    
                    if detailed:
                        print(f"\nBuilder Prompt:")
                        print("-" * 30)
                        print(task['builder_prompt'])
                        print("-" * 30)
                    
                    print(f"Git Branch: {task['branch']}")
                    print(f"Status: Ready to start")
                    print()
    
    def display_task_details(self, task_id: str):
        """Display detailed information about a specific task."""
        task = self.get_task_by_id(task_id)
        if not task:
            print(f"Error: Task '{task_id}' not found.")
            return
        
        print(f"\n{'='*80}")
        print(f"TASK DETAILS: {task_id}")
        print(f"{'='*80}")
        print(f"Description: {task['description']}")
        print(f"Workstream: {task['workstream_name']}")
        print(f"Priority: {task['priority']}")
        print(f"Assigned to: {task['assigned_to']}")
        print(f"Estimated Hours: {task['estimated_hours']}")
        print(f"Dependencies: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
        print(f"Git Branch: {task['branch']}")
        
        # Show dependent tasks
        dependent_tasks = self.get_dependent_tasks(task_id)
        if dependent_tasks:
            print(f"\nTasks that depend on this task:")
            for dep_task in dependent_tasks:
                print(f"  - {dep_task['task_id']}: {dep_task['description']}")
        
        print(f"\n{'='*80}")
        print("BUILDER PROMPT:")
        print(f"{'='*80}")
        print(task['builder_prompt'])
        print(f"{'='*80}")
    
    def create_task_file(self, task_id: str, output_dir: str = "tasks"):
        """Create a standalone task file for a specific task."""
        task = self.get_task_by_id(task_id)
        if not task:
            print(f"Error: Task '{task_id}' not found.")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create task file
        filename = f"{output_dir}/{task_id}_{task['description'].replace(' ', '_').lower()}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Task: {task_id}\n")
            f.write(f"**Description:** {task['description']}\n\n")
            f.write(f"**Workstream:** {task['workstream_name']}\n")
            f.write(f"**Priority:** {task['priority']}\n")
            f.write(f"**Assigned to:** {task['assigned_to']}\n")
            f.write(f"**Estimated Hours:** {task['estimated_hours']}\n")
            f.write(f"**Dependencies:** {', '.join(task['dependencies']) if task['dependencies'] else 'None'}\n")
            f.write(f"**Git Branch:** {task['branch']}\n\n")
            
            f.write("## Builder Prompt\n\n")
            f.write(task['builder_prompt'])
            f.write("\n\n")
            
            f.write("## Git Instructions\n\n")
            f.write("```bash\n")
            f.write("git checkout dev\n")
            f.write("git pull origin dev\n")
            f.write(f"git checkout -b feature/{task_id.lower()}\n")
            f.write(f"git push -u origin feature/{task_id.lower()}\n")
            f.write("```\n")
        
        print(f"Task file created: {filename}")

def main():
    """Main function to handle command line interface."""
    if len(sys.argv) < 2:
        print("Daydreamer Builder Assignment System")
        print("=" * 50)
        print("\nUsage:")
        print("  python builder_assignment.py <team_name> [options]")
        print("\nOptions:")
        print("  --detailed          Show detailed task information")
        print("  --task <task_id>    Show details for specific task")
        print("  --create-file       Create standalone task file")
        print("  --list-teams        List all available teams")
        print("\nExamples:")
        print("  python builder_assignment.py 'Builder Team A'")
        print("  python builder_assignment.py 'Builder Team A' --detailed")
        print("  python builder_assignment.py --task CE-001")
        print("  python builder_assignment.py --task CE-001 --create-file")
        print("  python builder_assignment.py --list-teams")
        return
    
    system = BuilderAssignmentSystem()
    
    if "--list-teams" in sys.argv:
        print("Available Builder Teams:")
        print("-" * 30)
        for team in system.get_available_teams():
            team_info = system.get_team_info(team)
            print(f"{team}")
            print(f"  Focus: {team_info['focus']}")
            print(f"  Capacity: {team_info['capacity']}")
            print()
        return
    
    if "--task" in sys.argv:
        try:
            task_index = sys.argv.index("--task")
            task_id = sys.argv[task_index + 1]
            system.display_task_details(task_id)
            
            if "--create-file" in sys.argv:
                system.create_task_file(task_id)
            return
        except (IndexError, ValueError):
            print("Error: Please provide a valid task ID with --task option")
            return
    
    # Handle team name
    team_name = sys.argv[1]
    detailed = "--detailed" in sys.argv
    
    system.display_team_tasks(team_name, detailed)

if __name__ == "__main__":
    main()
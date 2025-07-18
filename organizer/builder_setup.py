#!/usr/bin/env python3
"""
Daydreamer Project - Builder Setup and Identification System
Helps builders identify themselves and get started with their tasks.
"""

import json
import sys
import os
from typing import Dict, List

class BuilderSetup:
    def __init__(self, task_registry_path: str = "organizer/task_registry.json"):
        self.task_registry_path = task_registry_path
        self.task_registry = self._load_task_registry()
        self.builder_config_file = "organizer/builder_config.json"
        
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
    
    def get_available_teams(self) -> List[str]:
        """Get list of available builder teams."""
        return list(self.task_registry["builder_teams"].keys())
    
    def get_team_info(self, team_name: str) -> Dict:
        """Get information about a specific team."""
        return self.task_registry["builder_teams"].get(team_name, {})
    
    def get_team_tasks(self, team_name: str) -> List[Dict]:
        """Get all tasks assigned to a specific team."""
        tasks = []
        for workstream_name, workstream in self.task_registry["workstreams"].items():
            for task in workstream["tasks"]:
                if task["assigned_to"] == team_name:
                    task["workstream"] = workstream_name
                    task["workstream_name"] = workstream["name"]
                    tasks.append(task)
        return tasks
    
    def save_builder_config(self, team_name: str, builder_name: str = ""):
        """Save builder configuration."""
        config = {
            "team_name": team_name,
            "builder_name": builder_name,
            "setup_date": "2024-01-01"
        }
        
        os.makedirs(os.path.dirname(self.builder_config_file), exist_ok=True)
        with open(self.builder_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_builder_config(self) -> Dict:
        """Load builder configuration if it exists."""
        try:
            with open(self.builder_config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def display_welcome(self, team_name: str, builder_name: str = ""):
        """Display welcome message and team information."""
        team_info = self.get_team_info(team_name)
        tasks = self.get_team_tasks(team_name)
        
        print("\n" + "="*80)
        print(" WELCOME TO THE DAYDREAMER PROJECT! ")
        print("="*80)
        
        if builder_name:
            print(f"👋 Hello, {builder_name}!")
        
        print(f"🏢 You are assigned to: {team_name}")
        print(f" Team Focus: {team_info['focus']}")
        print(f" Team Capacity: {team_info['capacity']}")
        print(f"📋 Total Tasks Assigned: {len(tasks)}")
        
        # Calculate total hours
        total_hours = sum(task["estimated_hours"] for task in tasks)
        print(f"⏱️  Total Estimated Hours: {total_hours}")
        
        print("\n" + "="*80)
        print("📋 YOUR ASSIGNED TASKS:")
        print("="*80)
        
        # Group by priority
        high_priority = [t for t in tasks if t["priority"] == "High"]
        medium_priority = [t for t in tasks if t["priority"] == "Medium"]
        low_priority = [t for t in tasks if t["priority"] == "Low"]
        
        for priority, task_list, emoji in [
            ("HIGH PRIORITY", high_priority, ""),
            ("MEDIUM PRIORITY", medium_priority, "🟡"),
            ("LOW PRIORITY", low_priority, "🟢")
        ]:
            if task_list:
                print(f"\n{emoji} {priority} ({len(task_list)} tasks):")
                print("-" * 60)
                
                for task in task_list:
                    print(f"\n📝 {task['task_id']}: {task['description']}")
                    print(f"   🏷️  Workstream: {task['workstream_name']}")
                    print(f"   ⏱️  Estimated Hours: {task['estimated_hours']}")
                    print(f"   🔗 Dependencies: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
                    print(f"   🌿 Git Branch: {task['branch']}")
        
        print("\n" + "="*80)
        print(" GETTING STARTED:")
        print("="*80)
        print("1. To see detailed task information:")
        print(f"   ./organizer/get_tasks.sh '{team_name}' --detailed")
        print("\n2. To view a specific task:")
        print("   ./organizer/get_tasks.sh --task <TASK-ID>")
        print("\n3. To create a standalone task file:")
        print("   ./organizer/get_tasks.sh --task <TASK-ID> --create-file")
        print("\n4. To see all available teams:")
        print("   ./organizer/get_tasks.sh --list-teams")
        
        print("\n" + "="*80)
        print(" NEXT STEPS:")
        print("="*80)
        print("1. Review your high-priority tasks first")
        print("2. Check task dependencies before starting")
        print("3. Create your feature branch using the provided Git instructions")
        print("4. Follow the detailed builder prompt for each task")
        print("5. Write tests and documentation as specified")
        
        print("\n" + "="*80)
        print(" RECOMMENDED STARTING TASK:")
        print("="*80)
        
        # Recommend the first high-priority task with no dependencies
        recommended_task = None
        for task in high_priority:
            if not task["dependencies"]:
                recommended_task = task
                break
        
        if recommended_task:
            print(f"Start with: {recommended_task['task_id']} - {recommended_task['description']}")
            print(f"Reason: High priority with no dependencies")
        else:
            print("Review your task dependencies and start with the foundational tasks")
        
        print("\n" + "="*80)
        print("🌟 Happy coding! Let's build something amazing together! 🌟")
        print("="*80 + "\n")
    
    def interactive_setup(self):
        """Interactive setup process for builders."""
        print(" Daydreamer Project - Builder Setup")
        print("="*50)
        print("\nWelcome! Let's get you set up with your assigned tasks.")
        
        # Check if already configured
        existing_config = self.load_builder_config()
        if existing_config:
            print(f"\n You're already configured as: {existing_config.get('team_name', 'Unknown')}")
            if input("Would you like to reconfigure? (y/N): ").lower() != 'y':
                self.display_welcome(existing_config['team_name'], existing_config.get('builder_name', ''))
                return
        
        # Get builder name
        builder_name = input("\nWhat's your name? (optional): ").strip()
        
        # Show available teams
        print("\nAvailable Builder Teams:")
        print("-" * 40)
        teams = self.get_available_teams()
        for i, team in enumerate(teams, 1):
            team_info = self.get_team_info(team)
            print(f"{i}. {team}")
            print(f"   Focus: {team_info['focus']}")
            print(f"   Capacity: {team_info['capacity']}")
            print()
        
        # Get team selection
        while True:
            try:
                choice = input(f"Which team are you on? (1-{len(teams)}): ").strip()
                team_index = int(choice) - 1
                if 0 <= team_index < len(teams):
                    selected_team = teams[team_index]
                    break
                else:
                    print("Invalid choice. Please select a valid team number.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Save configuration
        self.save_builder_config(selected_team, builder_name)
        
        # Display welcome
        self.display_welcome(selected_team, builder_name)

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # Reset configuration
        config_file = "organizer/builder_config.json"
        if os.path.exists(config_file):
            os.remove(config_file)
            print(" Builder configuration reset.")
        return
    
    setup = BuilderSetup()
    setup.interactive_setup()

if __name__ == "__main__":
    main()
"""
CLI Interface for Daydreamer System Control

This module provides a command-line interface for controlling Daydreamer simulations,
managing agents, viewing logs, and configuring the system.
"""

import asyncio
import cmd
import json
import logging
import readline
import shlex
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from ..simulation.multi_agent_simulation import MultiAgentSimulation, SimulationConfig

logger = logging.getLogger(__name__)

@dataclass
class CLICommand:
    """CLI command definition"""
    name: str
    description: str
    usage: str
    handler: Callable
    requires_simulation: bool = False

class CommandRegistry:
    """Registry for CLI commands"""
    
    def __init__(self):
        self.commands: Dict[str, CLICommand] = {}
        self._register_default_commands()
    
    def register(self, command: CLICommand):
        """Register a new command"""
        self.commands[command.name] = command
    
    def get_command(self, name: str) -> Optional[CLICommand]:
        """Get a command by name"""
        return self.commands.get(name)
    
    def list_commands(self) -> List[str]:
        """List all available commands"""
        return list(self.commands.keys())
    
    def _register_default_commands(self):
        """Register default CLI commands"""
        # Note: Command handlers will be set after CLIInterface is created
        pass

class ConfigurationManager:
    """Manages CLI configuration"""
    
    def __init__(self):
        self.config = {
            "default_simulation_id": "cli-simulation",
            "default_duration": 300,
            "default_agent_count": 3,
            "default_interaction_frequency": 10.0,
            "log_level": "INFO",
            "log_file": "daydreamer_cli.log",
            "history_file": ".daydreamer_history"
        }
        self.config_file = Path("daydreamer_cli_config.json")
        self._load_config()
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self._save_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

class LogViewer:
    """Manages log viewing and filtering"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.log_buffer: List[str] = []
        self.max_buffer_size = 1000
    
    def add_log(self, message: str, level: str = "INFO"):
        """Add a log message to the buffer"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.log_buffer.append(log_entry)
        
        # Keep buffer size manageable
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
    
    def get_logs(self, lines: int = 50, level: str = None) -> List[str]:
        """Get recent logs with optional filtering"""
        logs = self.log_buffer[-lines:] if lines > 0 else self.log_buffer
        
        if level:
            logs = [log for log in logs if f" {level}:" in log]
        
        return logs
    
    def clear_logs(self):
        """Clear log buffer"""
        self.log_buffer.clear()

class CLIInterface(cmd.Cmd):
    """
    Command-line interface for Daydreamer system control.
    
    Features:
    - Simulation start/stop/pause commands
    - Agent management commands
    - Configuration management
    - Log viewing and filtering
    - Interactive shell with command history
    """
    
    intro = """
🧠 Daydreamer CLI Interface
==========================
Type 'help' for available commands or 'exit' to quit.
"""
    prompt = "daydreamer> "
    
    def __init__(self):
        super().__init__()
        self.simulation: Optional[MultiAgentSimulation] = None
        self.command_registry = CommandRegistry()
        self.config_manager = ConfigurationManager()
        self.log_viewer = LogViewer(self.config_manager)
        
        # Register commands
        self._register_commands()
        
        # Setup command history
        self._setup_history()
        
        # Setup logging
        self._setup_logging()
        
        logger.info("🎛️ CLI Interface initialized")
    
    def _register_commands(self):
        """Register CLI commands with handlers"""
        # Simulation control commands
        self.command_registry.register(CLICommand(
            name="start",
            description="Start a new simulation",
            usage="start [--id SIMULATION_ID] [--duration SECONDS] [--agents COUNT]",
            handler=self._cmd_start,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="stop",
            description="Stop the current simulation",
            usage="stop",
            handler=self._cmd_stop,
            requires_simulation=True
        ))
        
        self.command_registry.register(CLICommand(
            name="status",
            description="Show simulation status",
            usage="status",
            handler=self._cmd_status,
            requires_simulation=False
        ))
        
        # Agent management commands
        self.command_registry.register(CLICommand(
            name="agents",
            description="List all agents",
            usage="agents",
            handler=self._cmd_agents,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="agent",
            description="Show detailed agent information",
            usage="agent AGENT_ID",
            handler=self._cmd_agent,
            requires_simulation=False
        ))
        
        # Configuration commands
        self.command_registry.register(CLICommand(
            name="config",
            description="Show or modify configuration",
            usage="config [KEY] [VALUE]",
            handler=self._cmd_config,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="save-config",
            description="Save current configuration to file",
            usage="save-config [FILENAME]",
            handler=self._cmd_save_config,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="load-config",
            description="Load configuration from file",
            usage="load-config [FILENAME]",
            handler=self._cmd_load_config,
            requires_simulation=False
        ))
        
        # Logging commands
        self.command_registry.register(CLICommand(
            name="logs",
            description="Show recent logs",
            usage="logs [--lines N] [--level LEVEL]",
            handler=self._cmd_logs,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="clear-logs",
            description="Clear log history",
            usage="clear-logs",
            handler=self._cmd_clear_logs,
            requires_simulation=False
        ))
        
        # System commands
        self.command_registry.register(CLICommand(
            name="help",
            description="Show help information",
            usage="help [COMMAND]",
            handler=self._cmd_help,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="exit",
            description="Exit the CLI",
            usage="exit",
            handler=self._cmd_exit,
            requires_simulation=False
        ))
        
        self.command_registry.register(CLICommand(
            name="quit",
            description="Exit the CLI",
            usage="quit",
            handler=self._cmd_exit,
            requires_simulation=False
        ))
    
    def _setup_history(self):
        """Setup command history"""
        history_file = Path(self.config_manager.get("history_file"))
        if history_file.exists():
            try:
                readline.read_history_file(str(history_file))
            except Exception as e:
                logger.warning(f"Failed to load history: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config_manager.get("log_level", "INFO"))
        log_file = self.config_manager.get("log_file", "daydreamer_cli.log")
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def do_start(self, arg):
        """Start a new simulation"""
        return self._execute_command("start", arg)
    
    def do_stop(self, arg):
        """Stop the current simulation"""
        return self._execute_command("stop", arg)
    
    def do_status(self, arg):
        """Show simulation status"""
        return self._execute_command("status", arg)
    
    def do_agents(self, arg):
        """List all agents"""
        return self._execute_command("agents", arg)
    
    def do_agent(self, arg):
        """Show detailed agent information"""
        return self._execute_command("agent", arg)
    
    def do_config(self, arg):
        """Show or modify configuration"""
        return self._execute_command("config", arg)
    
    def do_save_config(self, arg):
        """Save current configuration to file"""
        return self._execute_command("save-config", arg)
    
    def do_load_config(self, arg):
        """Load configuration from file"""
        return self._execute_command("load-config", arg)
    
    def do_logs(self, arg):
        """Show recent logs"""
        return self._execute_command("logs", arg)
    
    def do_clear_logs(self, arg):
        """Clear log history"""
        return self._execute_command("clear-logs", arg)
    
    def do_help(self, arg):
        """Show help information"""
        return self._execute_command("help", arg)
    
    def do_exit(self, arg):
        """Exit the CLI"""
        return self._execute_command("exit", arg)
    
    def do_quit(self, arg):
        """Exit the CLI"""
        return self._execute_command("quit", arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        print()
        return self.do_exit(arg)
    
    def _execute_command(self, command_name: str, arg: str):
        """Execute a command from the registry"""
        command = self.command_registry.get_command(command_name)
        if not command:
            print(f"❌ Unknown command: {command_name}")
            return False
        
        if command.requires_simulation and not self.simulation:
            print("❌ No simulation running. Use 'start' to create one.")
            return False
        
        try:
            # Parse arguments
            args = shlex.split(arg) if arg.strip() else []
            
            # Execute command
            result = command.handler(self, args)
            
            # Log command execution
            self.log_viewer.add_log(f"Executed command: {command_name} {' '.join(args)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error executing {command_name}: {e}")
            self.log_viewer.add_log(f"Command error: {command_name} - {e}", "ERROR")
            return False
    
    def _cmd_start(self, args: List[str]):
        """Start a new simulation"""
        if self.simulation and self.simulation.is_running:
            print("❌ Simulation already running. Use 'stop' first.")
            return False
        
        # Parse arguments
        simulation_id = self.config_manager.get("default_simulation_id")
        duration = self.config_manager.get("default_duration")
        agent_count = self.config_manager.get("default_agent_count")
        interaction_frequency = self.config_manager.get("default_interaction_frequency")
        
        # Override with command line arguments
        for i, arg in enumerate(args):
            if arg == "--id" and i + 1 < len(args):
                simulation_id = args[i + 1]
            elif arg == "--duration" and i + 1 < len(args):
                duration = int(args[i + 1])
            elif arg == "--agents" and i + 1 < len(args):
                agent_count = int(args[i + 1])
        
        # Create simulation config
        config = SimulationConfig(
            simulation_id=simulation_id,
            duration_seconds=duration,
            agent_count=agent_count,
            interaction_frequency=interaction_frequency,
            enable_autonomous_thinking=True,
            enable_agent_communication=True,
            enable_reasoning_tasks=True
        )
        
        # Create and start simulation
        self.simulation = MultiAgentSimulation(config)
        self.simulation.create_agents()
        
        # Start simulation in background
        asyncio.create_task(self.simulation.start_simulation())
        
        print(f"🚀 Started simulation: {simulation_id}")
        print(f"   Duration: {duration} seconds")
        print(f"   Agents: {agent_count}")
        print(f"   Interaction frequency: {interaction_frequency}s")
        
        return True
    
    def _cmd_stop(self, args: List[str]):
        """Stop the current simulation"""
        if not self.simulation:
            print("❌ No simulation running")
            return False
        
        asyncio.create_task(self.simulation.stop_simulation())
        print("🛑 Stopping simulation...")
        return True
    
    def _cmd_status(self, args: List[str]):
        """Show simulation status"""
        if not self.simulation:
            print("📊 Status: No simulation running")
            return True
        
        stats = self.simulation.get_simulation_stats()
        
        print("📊 Simulation Status:")
        print(f"   ID: {self.simulation.config.simulation_id}")
        print(f"   Running: {'✅ Yes' if self.simulation.is_running else '❌ No'}")
        print(f"   Agents: {len(self.simulation.agents)}")
        print(f"   Total Thoughts: {stats.get('total_thoughts', 0)}")
        print(f"   Total Communications: {stats.get('total_communications', 0)}")
        print(f"   Reasoning Sessions: {stats.get('total_reasoning_sessions', 0)}")
        print(f"   Agent Interactions: {stats.get('agent_interactions', 0)}")
        
        return True
    
    def _cmd_agents(self, args: List[str]):
        """List all agents"""
        if not self.simulation:
            print("❌ No simulation running")
            return False
        
        print("🤖 Agents:")
        for agent_id, agent in self.simulation.agents.items():
            status = "🟢 Active" if agent.is_running else "🔴 Inactive"
            print(f"   {agent_id} ({agent.config.personality}) - {status}")
        
        return True
    
    def _cmd_agent(self, args: List[str]):
        """Show detailed agent information"""
        if not self.simulation:
            print("❌ No simulation running")
            return False
        
        if not args:
            print("❌ Please specify an agent ID")
            return False
        
        agent_id = args[0]
        if agent_id not in self.simulation.agents:
            print(f"❌ Agent '{agent_id}' not found")
            return False
        
        agent = self.simulation.agents[agent_id]
        
        print(f"🤖 Agent: {agent_id}")
        print(f"   Personality: {agent.config.personality}")
        print(f"   Thinking Frequency: {agent.config.thinking_frequency}s")
        print(f"   Status: {'🟢 Active' if agent.is_running else '🔴 Inactive'}")
        print(f"   Thoughts Generated: {getattr(agent, 'thought_count', 0)}")
        print(f"   Communications: {getattr(agent, 'communication_count', 0)}")
        
        return True
    
    def _cmd_config(self, args: List[str]):
        """Show or modify configuration"""
        if not args:
            # Show all configuration
            print("⚙️ Configuration:")
            for key, value in self.config_manager.config.items():
                print(f"   {key}: {value}")
        elif len(args) == 1:
            # Show specific configuration
            key = args[0]
            value = self.config_manager.get(key)
            if value is not None:
                print(f"⚙️ {key}: {value}")
            else:
                print(f"❌ Configuration key '{key}' not found")
        elif len(args) == 2:
            # Set configuration
            key, value = args
            try:
                # Try to convert value to appropriate type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                
                self.config_manager.set(key, value)
                print(f"✅ Set {key} = {value}")
            except Exception as e:
                print(f"❌ Failed to set configuration: {e}")
        
        return True
    
    def _cmd_save_config(self, args: List[str]):
        """Save current configuration to file"""
        filename = args[0] if args else "daydreamer_cli_config.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.config_manager.config, f, indent=2)
            print(f"✅ Configuration saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
        
        return True
    
    def _cmd_load_config(self, args: List[str]):
        """Load configuration from file"""
        filename = args[0] if args else "daydreamer_cli_config.json"
        
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                self.config_manager.config.update(config)
            print(f"✅ Configuration loaded from {filename}")
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
        
        return True
    
    def _cmd_logs(self, args: List[str]):
        """Show recent logs"""
        lines = 50
        level = None
        
        # Parse arguments
        for i, arg in enumerate(args):
            if arg == "--lines" and i + 1 < len(args):
                lines = int(args[i + 1])
            elif arg == "--level" and i + 1 < len(args):
                level = args[i + 1].upper()
        
        logs = self.log_viewer.get_logs(lines, level)
        
        if not logs:
            print("📝 No logs to display")
        else:
            print("📝 Recent Logs:")
            for log in logs:
                print(f"   {log}")
        
        return True
    
    def _cmd_clear_logs(self, args: List[str]):
        """Clear log history"""
        self.log_viewer.clear_logs()
        print("✅ Log history cleared")
        return True
    
    def _cmd_help(self, args: List[str]):
        """Show help information"""
        if not args:
            # Show general help
            print("🧠 Daydreamer CLI - Available Commands:")
            print()
            
            commands = self.command_registry.list_commands()
            for cmd_name in sorted(commands):
                cmd = self.command_registry.get_command(cmd_name)
                print(f"   {cmd_name:<15} - {cmd.description}")
            
            print()
            print("Type 'help COMMAND' for detailed usage information.")
        else:
            # Show specific command help
            cmd_name = args[0]
            cmd = self.command_registry.get_command(cmd_name)
            
            if cmd:
                print(f"📖 Help for '{cmd_name}':")
                print(f"   Description: {cmd.description}")
                print(f"   Usage: {cmd.usage}")
            else:
                print(f"❌ Unknown command: {cmd_name}")
        
        return True
    
    def _cmd_exit(self, args: List[str]):
        """Exit the CLI"""
        if self.simulation and self.simulation.is_running:
            print("🛑 Stopping simulation before exit...")
            asyncio.create_task(self.simulation.stop_simulation())
        
        # Save command history
        history_file = Path(self.config_manager.get("history_file"))
        try:
            readline.write_history_file(str(history_file))
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")
        
        print("👋 Goodbye!")
        return True
    
    def run(self):
        """Run the CLI interface"""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            return self.do_exit("")

# Demo function
def demo_cli_interface():
    """Demo the CLI interface"""
    cli = CLIInterface()
    
    print("🎛️ Starting Daydreamer CLI Interface...")
    print("Type 'help' for available commands")
    
    cli.run()

if __name__ == "__main__":
    demo_cli_interface()
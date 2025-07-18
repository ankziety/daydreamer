#!/usr/bin/env python3
"""
Test script for Daydreamer UI components
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.web_dashboard import WebDashboard, DashboardConfig
from src.ui.cli_interface import CLIInterface

async def test_web_dashboard():
    """Test the web dashboard"""
    print(" Testing Web Dashboard...")
    
    try:
        # Create dashboard with test config
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            debug=True
        )
        
        dashboard = WebDashboard(config)
        
        # Test dashboard creation
        print(" Web Dashboard created successfully")
        print(f"   Host: {config.host}")
        print(f"   Port: {config.port}")
        
        # Test API endpoints
        status = dashboard._get_simulation_status()
        print(f" Status endpoint: {status}")
        
        metrics = dashboard._get_metrics()
        print(f" Metrics endpoint: {metrics}")
        
        agents = dashboard._get_agent_info()
        print(f" Agents endpoint: {agents}")
        
        print(" Web Dashboard tests passed!")
        return True
        
    except Exception as e:
        print(f" Web Dashboard test failed: {e}")
        return False

def test_cli_interface():
    """Test the CLI interface"""
    print(" Testing CLI Interface...")
    
    try:
        # Create CLI interface
        cli = CLIInterface()
        
        # Test command registry
        commands = cli.command_registry.list_commands()
        print(f" Registered commands: {len(commands)}")
        
        # Test configuration manager
        config_value = cli.config_manager.get("default_simulation_id")
        print(f" Config manager: {config_value}")
        
        # Test log viewer
        cli.log_viewer.add_log("Test log message")
        logs = cli.log_viewer.get_logs(1)
        print(f" Log viewer: {len(logs)} logs")
        
        # Test command execution
        result = cli._execute_command("status", "")
        print(f" Command execution: {result}")
        
        print(" CLI Interface tests passed!")
        return True
        
    except Exception as e:
        print(f" CLI Interface test failed: {e}")
        return False

async def main():
    """Run all UI tests"""
    print(" Daydreamer UI System Tests")
    print("=" * 40)
    
    # Test CLI interface
    cli_success = test_cli_interface()
    
    # Test web dashboard
    web_success = await test_web_dashboard()
    
    print("\n" + "=" * 40)
    if cli_success and web_success:
        print(" All UI tests passed!")
        print("\nTo run the interfaces:")
        print("  Web Dashboard: python -m src.ui.web_dashboard")
        print("  CLI Interface: python -m src.ui.cli_interface")
    else:
        print(" Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
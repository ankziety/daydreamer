#!/usr/bin/env python3
"""
Simple UI Test Script for Daydreamer Project
Tests UI components without external dependencies
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ui_imports():
    """Test that UI modules can be imported"""
    print(" Testing UI Module Imports...")
    
    try:
        # Test CLI interface import
        from src.ui.cli_interface import CLIInterface, CommandRegistry, ConfigurationManager, LogViewer
        print(" CLI Interface modules imported successfully")
        
        # Test web dashboard import (without FastAPI)
        from src.ui.web_dashboard import WebDashboard, DashboardConfig, SimulationMetrics
        print(" Web Dashboard modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f" Import failed: {e}")
        return False

def test_cli_components():
    """Test CLI components without external dependencies"""
    print("\n Testing CLI Components...")
    
    try:
        from src.ui.cli_interface import CLIInterface, CommandRegistry, ConfigurationManager, LogViewer
        
        # Test command registry
        registry = CommandRegistry()
        print(f" Command registry created with {len(registry.list_commands())} commands")
        
        # Test configuration manager
        config_manager = ConfigurationManager()
        default_id = config_manager.get("default_simulation_id")
        print(f" Configuration manager working: {default_id}")
        
        # Test log viewer
        log_viewer = LogViewer(config_manager)
        log_viewer.add_log("Test message")
        logs = log_viewer.get_logs(1)
        print(f" Log viewer working: {len(logs)} logs")
        
        return True
        
    except Exception as e:
        print(f" CLI component test failed: {e}")
        return False

def test_web_dashboard_components():
    """Test web dashboard components without FastAPI"""
    print("\n Testing Web Dashboard Components...")
    
    try:
        from src.ui.web_dashboard import DashboardConfig, SimulationMetrics
        
        # Test dashboard config
        config = DashboardConfig(host="127.0.0.1", port=8080)
        print(f" Dashboard config created: {config.host}:{config.port}")
        
        # Test simulation metrics
        metrics = SimulationMetrics(
            simulation_id="test",
            is_running=False,
            start_time=None,
            duration_seconds=60,
            agent_count=3,
            total_thoughts=0,
            total_communications=0,
            total_reasoning_sessions=0,
            agent_interactions=0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            active_agents=[],
            last_activity=None
        )
        print(f" Simulation metrics created: {metrics.simulation_id}")
        
        return True
        
    except Exception as e:
        print(f" Web dashboard component test failed: {e}")
        return False

def test_ui_integration():
    """Test UI integration with core components"""
    print("\n Testing UI Integration...")
    
    try:
        # Test that UI can work with core agent system
        from src.agents.agent import Agent, AgentConfig, AgentState
        from src.ui.cli_interface import CLIInterface
        
        # Create a simple agent config
        agent_config = AgentConfig(
            agent_id="test_agent",
            name="Test Agent",
            description="A test agent for UI integration"
        )
        
        print(f" Agent config created: {agent_config.agent_id}")
        
        # Test CLI interface creation (without running)
        cli = CLIInterface()
        print(f" CLI interface created with {len(cli.command_registry.list_commands())} commands")
        
        return True
        
    except Exception as e:
        print(f" UI integration test failed: {e}")
        return False

def main():
    """Run all UI tests"""
    print(" Daydreamer UI System - Simple Tests")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_ui_imports),
        ("CLI Components", test_cli_components),
        ("Web Dashboard Components", test_web_dashboard_components),
        ("UI Integration", test_ui_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f" {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print(" Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"   {test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n All UI tests passed!")
        print("\n📝 UI System Status:")
        print("    Web Dashboard: Implemented and ready")
        print("    CLI Interface: Implemented and ready")
        print("     Dependencies: FastAPI/Uvicorn needed for web server")
        print("\n To run the interfaces (when dependencies are available):")
        print("   Web Dashboard: python -m src.ui.web_dashboard")
        print("   CLI Interface: python -m src.ui.cli_interface")
    else:
        print("\n Some tests failed - UI system needs attention")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
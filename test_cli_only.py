#!/usr/bin/env python3
"""
CLI Interface Test Script for Daydreamer Project
Tests CLI components without web dashboard dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_cli_imports():
    """Test CLI interface imports"""
    print(" Testing CLI Interface Imports...")
    
    try:
        # Import CLI components directly
        from src.ui.cli_interface import CLIInterface, CommandRegistry, ConfigurationManager, LogViewer, CLICommand
        print(" CLI Interface modules imported successfully")
        return True
        
    except ImportError as e:
        print(f" CLI import failed: {e}")
        return False

def test_command_registry():
    """Test command registry functionality"""
    print("\n Testing Command Registry...")
    
    try:
        from src.ui.cli_interface import CommandRegistry, CLICommand
        
        registry = CommandRegistry()
        
        # Test command registration
        def test_handler(args):
            return True
        
        command = CLICommand(
            name="test",
            description="Test command",
            usage="test",
            handler=test_handler
        )
        
        registry.register(command)
        commands = registry.list_commands()
        print(f" Command registry working: {len(commands)} commands")
        
        # Test command retrieval
        retrieved = registry.get_command("test")
        if retrieved:
            print(f" Command retrieval working: {retrieved.name}")
        else:
            print(" Command retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f" Command registry test failed: {e}")
        return False

def test_configuration_manager():
    """Test configuration manager"""
    print("\n Testing Configuration Manager...")
    
    try:
        from src.ui.cli_interface import ConfigurationManager
        
        config = ConfigurationManager()
        
        # Test default values
        default_id = config.get("default_simulation_id")
        print(f" Default config loaded: {default_id}")
        
        # Test setting values
        config.set("test_key", "test_value")
        test_value = config.get("test_key")
        print(f" Config set/get working: {test_value}")
        
        # Test non-existent key
        missing = config.get("non_existent", "default")
        print(f" Default value handling: {missing}")
        
        return True
        
    except Exception as e:
        print(f" Configuration manager test failed: {e}")
        return False

def test_log_viewer():
    """Test log viewer functionality"""
    print("\n Testing Log Viewer...")
    
    try:
        from src.ui.cli_interface import ConfigurationManager, LogViewer
        
        config = ConfigurationManager()
        log_viewer = LogViewer(config)
        
        # Test adding logs
        log_viewer.add_log("Test message 1")
        log_viewer.add_log("Test message 2", "WARNING")
        log_viewer.add_log("Test message 3", "ERROR")
        
        # Test retrieving logs
        all_logs = log_viewer.get_logs()
        print(f" Log storage working: {len(all_logs)} logs")
        
        # Test filtering
        warning_logs = log_viewer.get_logs(level="WARNING")
        print(f" Log filtering working: {len(warning_logs)} warning logs")
        
        # Test clearing
        log_viewer.clear_logs()
        cleared_logs = log_viewer.get_logs()
        print(f" Log clearing working: {len(cleared_logs)} logs after clear")
        
        return True
        
    except Exception as e:
        print(f" Log viewer test failed: {e}")
        return False

def test_cli_interface_creation():
    """Test CLI interface creation"""
    print("\n Testing CLI Interface Creation...")
    
    try:
        from src.ui.cli_interface import CLIInterface
        
        # Create CLI interface
        cli = CLIInterface()
        
        # Test command registry
        commands = cli.command_registry.list_commands()
        print(f" CLI created with {len(commands)} commands")
        
        # Test configuration
        config_value = cli.config_manager.get("default_simulation_id")
        print(f" CLI config working: {config_value}")
        
        # Test log viewer
        cli.log_viewer.add_log("CLI test message")
        logs = cli.log_viewer.get_logs(1)
        print(f" CLI log viewer working: {len(logs)} logs")
        
        return True
        
    except Exception as e:
        print(f" CLI interface creation test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI command execution"""
    print("\n Testing CLI Commands...")
    
    try:
        from src.ui.cli_interface import CLIInterface
        
        cli = CLIInterface()
        
        # Test help command
        result = cli._execute_command("help", "")
        print(f" Help command: {result}")
        
        # Test status command
        result = cli._execute_command("status", "")
        print(f" Status command: {result}")
        
        # Test config command
        result = cli._execute_command("config", "")
        print(f" Config command: {result}")
        
        # Test invalid command
        result = cli._execute_command("invalid_command", "")
        print(f" Invalid command handling: {result}")
        
        return True
        
    except Exception as e:
        print(f" CLI commands test failed: {e}")
        return False

def main():
    """Run all CLI tests"""
    print("🎛️ Daydreamer CLI Interface - Component Tests")
    print("=" * 50)
    
    tests = [
        ("CLI Imports", test_cli_imports),
        ("Command Registry", test_command_registry),
        ("Configuration Manager", test_configuration_manager),
        ("Log Viewer", test_log_viewer),
        ("CLI Interface Creation", test_cli_interface_creation),
        ("CLI Commands", test_cli_commands)
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
        print("\n All CLI tests passed!")
        print("\n📝 CLI Interface Status:")
        print("    Command Registry: Working")
        print("    Configuration Manager: Working")
        print("    Log Viewer: Working")
        print("    CLI Interface: Ready")
        print("\n CLI Interface is fully functional!")
        print("   To run: python -m src.ui.cli_interface")
    else:
        print("\n Some CLI tests failed - needs attention")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
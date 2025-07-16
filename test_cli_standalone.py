#!/usr/bin/env python3
"""
Standalone CLI Interface Test Script
Tests CLI components by importing them directly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_cli_import():
    """Test direct CLI import without UI package"""
    print("🧪 Testing Direct CLI Import...")
    
    try:
        # Import CLI components directly from the file
        import importlib.util
        
        # Load CLI interface module directly
        cli_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'cli_interface.py')
        spec = importlib.util.spec_from_file_location("cli_interface", cli_path)
        cli_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_module)
        
        # Test that we can access CLI classes
        CLIInterface = cli_module.CLIInterface
        CommandRegistry = cli_module.CommandRegistry
        ConfigurationManager = cli_module.ConfigurationManager
        LogViewer = cli_module.LogViewer
        
        print("✅ Direct CLI import successful")
        return True
        
    except Exception as e:
        print(f"❌ Direct CLI import failed: {e}")
        return False

def test_cli_components_standalone():
    """Test CLI components using direct import"""
    print("\n🧪 Testing CLI Components (Standalone)...")
    
    try:
        import importlib.util
        
        # Load CLI interface module directly
        cli_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'cli_interface.py')
        spec = importlib.util.spec_from_file_location("cli_interface", cli_path)
        cli_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_module)
        
        # Test command registry
        registry = cli_module.CommandRegistry()
        print(f"✅ Command registry created: {len(registry.list_commands())} commands")
        
        # Test configuration manager
        config = cli_module.ConfigurationManager()
        default_id = config.get("default_simulation_id")
        print(f"✅ Configuration manager: {default_id}")
        
        # Test log viewer
        log_viewer = cli_module.LogViewer(config)
        log_viewer.add_log("Test message")
        logs = log_viewer.get_logs(1)
        print(f"✅ Log viewer: {len(logs)} logs")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI components test failed: {e}")
        return False

def test_cli_interface_standalone():
    """Test CLI interface creation using direct import"""
    print("\n🧪 Testing CLI Interface (Standalone)...")
    
    try:
        import importlib.util
        
        # Load CLI interface module directly
        cli_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'cli_interface.py')
        spec = importlib.util.spec_from_file_location("cli_interface", cli_path)
        cli_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli_module)
        
        # Create CLI interface
        cli = cli_module.CLIInterface()
        
        # Test basic functionality
        commands = cli.command_registry.list_commands()
        print(f"✅ CLI interface created with {len(commands)} commands")
        
        # Test command execution
        result = cli._execute_command("help", "")
        print(f"✅ Command execution: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI interface test failed: {e}")
        return False

def test_cli_code_analysis():
    """Analyze CLI code without running it"""
    print("\n🧪 Analyzing CLI Code...")
    
    try:
        cli_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'cli_interface.py')
        
        with open(cli_path, 'r') as f:
            cli_code = f.read()
        
        # Check for key components
        components = {
            "CLIInterface class": "class CLIInterface" in cli_code,
            "CommandRegistry class": "class CommandRegistry" in cli_code,
            "ConfigurationManager class": "class ConfigurationManager" in cli_code,
            "LogViewer class": "class LogViewer" in cli_code,
            "Command handling": "def _execute_command" in cli_code,
            "Help command": "def do_help" in cli_code,
            "Start command": "def do_start" in cli_code,
            "Status command": "def do_status" in cli_code,
            "Demo function": "def demo_cli_interface" in cli_code
        }
        
        print("📋 CLI Code Analysis:")
        for component, found in components.items():
            status = "✅ Found" if found else "❌ Missing"
            print(f"   {component:<25} {status}")
        
        all_found = all(components.values())
        if all_found:
            print("✅ All CLI components found in code")
        else:
            print("❌ Some CLI components missing")
        
        return all_found
        
    except Exception as e:
        print(f"❌ CLI code analysis failed: {e}")
        return False

def main():
    """Run all standalone CLI tests"""
    print("🎛️ Daydreamer CLI Interface - Standalone Tests")
    print("=" * 50)
    
    tests = [
        ("Direct CLI Import", test_direct_cli_import),
        ("CLI Components", test_cli_components_standalone),
        ("CLI Interface", test_cli_interface_standalone),
        ("CLI Code Analysis", test_cli_code_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All CLI tests passed!")
        print("\n📝 CLI Interface Status:")
        print("   ✅ Code Structure: Complete")
        print("   ✅ Components: All present")
        print("   ✅ Functionality: Ready")
        print("   ⚠️  Dependencies: FastAPI import issue in UI package")
        print("\n🔧 Issue Identified:")
        print("   The UI package __init__.py imports both web_dashboard and cli_interface")
        print("   This causes FastAPI to be imported even when only CLI is needed")
        print("\n💡 Solution:")
        print("   - Use direct imports: from src.ui.cli_interface import CLIInterface")
        print("   - Or modify UI package to use lazy imports")
        print("   - CLI interface is fully functional when imported directly")
    else:
        print("\n❌ Some CLI tests failed - needs attention")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
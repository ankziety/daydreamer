#!/usr/bin/env python3
"""
Test Lazy Import Fix for UI System
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_lazy_cli_import():
    """Test that CLI can be imported without FastAPI"""
    print("🧪 Testing Lazy CLI Import...")
    
    try:
        # Test the new lazy import system
        from src.ui import get_cli_interface
        
        # Get the CLI class
        CLIInterface = get_cli_interface()
        
        # Create an instance
        cli = CLIInterface()
        
        # Test basic functionality
        commands = cli.command_registry.list_commands()
        print(f"✅ Lazy CLI import successful: {len(commands)} commands")
        
        return True
        
    except Exception as e:
        print(f"❌ Lazy CLI import failed: {e}")
        return False

def test_lazy_web_import():
    """Test that web dashboard can be imported (will fail without FastAPI)"""
    print("\n🧪 Testing Lazy Web Dashboard Import...")
    
    try:
        # Test the new lazy import system
        from src.ui import get_web_dashboard
        
        # This should fail gracefully without FastAPI
        print("⚠️  Web dashboard import attempted (will fail without FastAPI)")
        
        # Try to get the class (this will fail)
        WebDashboard = get_web_dashboard()
        print("❌ Web dashboard import should have failed")
        return False
        
    except ImportError as e:
        print(f"✅ Web dashboard import correctly failed: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ui_package_import():
    """Test that UI package can be imported without errors"""
    print("\n🧪 Testing UI Package Import...")
    
    try:
        # Import the UI package itself
        import src.ui
        
        print("✅ UI package imported successfully")
        
        # Check available attributes
        attrs = dir(src.ui)
        print(f"✅ Available attributes: {len(attrs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI package import failed: {e}")
        return False

def main():
    """Run lazy import tests"""
    print("🔧 Testing Lazy Import Fix")
    print("=" * 40)
    
    tests = [
        ("UI Package Import", test_ui_package_import),
        ("Lazy CLI Import", test_lazy_cli_import),
        ("Lazy Web Import", test_lazy_web_import)
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
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Lazy import fix successful!")
        print("\n📝 Import Usage:")
        print("   CLI Interface: from src.ui import get_cli_interface")
        print("   Web Dashboard: from src.ui import get_web_dashboard")
        print("\n💡 Benefits:")
        print("   ✅ CLI can be used without FastAPI")
        print("   ✅ Web dashboard only loads when needed")
        print("   ✅ No more import conflicts")
    else:
        print("\n❌ Some tests failed - fix needs attention")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
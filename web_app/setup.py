#!/usr/bin/env python3
"""
Setup script for Daydreamer AI Web Application
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_node_version():
    """Check if Node.js is installed and has compatible version"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ Node.js {version} detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed or not in PATH")
        print("Please install Node.js 16 or higher from https://nodejs.org/")
        return False

def check_npm():
    """Check if npm is available"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ npm {version} detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm is not installed or not in PATH")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def install_node_dependencies():
    """Install Node.js dependencies"""
    return run_command("npm install", "Installing Node.js dependencies")

def build_frontend():
    """Build the frontend application"""
    return run_command("npm run build", "Building frontend application")

def create_data_directory():
    """Create data directory for SQLite database"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created data directory: {data_dir}")
    else:
        print(f"✅ Data directory already exists: {data_dir}")
    return True

def run_tests():
    """Run the test suite"""
    return run_command("python -m pytest test_main.py -v", "Running tests")

def main():
    """Main setup function"""
    print("🚀 Setting up Daydreamer AI Web Application")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    if not check_npm():
        sys.exit(1)
    
    # Create data directory
    if not create_data_directory():
        sys.exit(1)
    
    # Install dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    if not install_node_dependencies():
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    # Build frontend
    if not build_frontend():
        print("❌ Failed to build frontend")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("1. Run: python main.py")
    print("2. Open: http://localhost:8000")
    print("\nFor development:")
    print("1. Terminal 1: python main.py")
    print("2. Terminal 2: npm run dev")
    print("3. Open: http://localhost:3000")

if __name__ == "__main__":
    main()
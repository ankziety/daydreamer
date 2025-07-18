#!/usr/bin/env python3
"""
Quick Start Script for Daydreamer Project
Sets up Ollama, Gemma 3N, and runs a demo
"""

import os
import sys
import subprocess
import asyncio
import logging

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print(" Python 3.8 or higher is required")
        sys.exit(1)
    print(f" Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_ollama():
    """Install Ollama if not already installed"""
    try:
        # Check if ollama is installed
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f" Ollama is already installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("📦 Installing Ollama...")
    
    # Install Ollama based on OS
    if sys.platform.startswith("linux"):
        try:
            subprocess.run([
                "curl", "-fsSL", "https://ollama.ai/install.sh"
            ], shell=True, check=True)
            print(" Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(" Failed to install Ollama automatically")
            print("Please install manually: https://ollama.ai/download")
            return False
    elif sys.platform == "darwin":  # macOS
        try:
            subprocess.run([
                "curl", "-fsSL", "https://ollama.ai/install.sh"
            ], shell=True, check=True)
            print(" Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(" Failed to install Ollama automatically")
            print("Please install manually: https://ollama.ai/download")
            return False
    else:
        print(" Automatic Ollama installation not supported on this platform")
        print("Please install manually: https://ollama.ai/download")
        return False

def download_gemma3n():
    """Download Gemma 3N model"""
    print(" Downloading Gemma 3N model...")
    
    try:
        # Pull the model
        result = subprocess.run([
            "ollama", "pull", "gemma3n:3b"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(" Gemma 3N model downloaded successfully")
            return True
        else:
            print(f" Failed to download Gemma 3N: {result.stderr}")
            return False
    except Exception as e:
        print(f" Error downloading Gemma 3N: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "ollama"
        ], check=True)
        print(" Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Failed to install Python dependencies: {e}")
        return False

def test_gemma3n():
    """Test Gemma 3N integration"""
    print(" Testing Gemma 3N integration...")
    
    try:
        import ollama
        
        # Test basic connection
        response = ollama.chat(
            model='gemma3n:3b',
            messages=[{'role': 'user', 'content': 'Hello! Are you working?'}]
        )
        
        print(" Gemma 3N is working!")
        print(f"Response: {response['message']['content'][:100]}...")
        return True
        
    except ImportError:
        print(" Ollama Python package not installed")
        return False
    except Exception as e:
        print(f" Gemma 3N test failed: {e}")
        return False

async def run_demo():
    """Run the Daydreamer demo"""
    print("\n🎬 Running Daydreamer Demo...")
    print("=" * 50)
    
    try:
        # Import demo function
        from src.simulation.multi_agent_simulation import demo_multi_agent_simulation
        
        # Run demo
        await demo_multi_agent_simulation()
        
    except ImportError as e:
        print(f" Failed to import demo: {e}")
        print("Make sure you're in the project root directory")
        return False
    except Exception as e:
        print(f" Demo failed: {e}")
        return False
    
    return True

def main():
    """Main setup and demo function"""
    print(" Daydreamer Project - Quick Start")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Install Ollama
    if not install_ollama():
        print(" Ollama installation failed. Please install manually.")
        return
    
    # Download Gemma 3N
    if not download_gemma3n():
        print(" Gemma 3N download failed.")
        return
    
    # Install Python dependencies
    if not install_python_dependencies():
        print(" Python dependencies installation failed.")
        return
    
    # Test Gemma 3N
    if not test_gemma3n():
        print(" Gemma 3N test failed.")
        return
    
    print("\n Setup completed successfully!")
    print(" Ready to run Daydreamer demo...")
    
    # Ask user if they want to run the demo
    response = input("\nRun the demo now? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        # Run demo
        asyncio.run(run_demo())
    else:
        print("\nTo run the demo later, use:")
        print("python quick_start.py --demo")
        print("or")
        print("python -m src.simulation.multi_agent_simulation")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run demo directly
        asyncio.run(run_demo())
    else:
        main()
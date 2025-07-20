#!/usr/bin/env python3
"""
Startup script for Daydreamer AI Web Application
Runs both backend and frontend development servers
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shutdown"""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def run_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("Backend server stopped")
    except Exception as e:
        print(f"Backend server error: {e}")

def run_frontend():
    """Start the Vite development server"""
    print("🚀 Starting frontend development server...")
    try:
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("Frontend server stopped")
    except Exception as e:
        print(f"Frontend server error: {e}")

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js dependencies
    node_modules = Path("node_modules")
    if not node_modules.exists():
        print("❌ Node.js dependencies not installed")
        print("Run: npm install")
        return False
    
    print("✅ Node.js dependencies OK")
    return True

def main():
    """Main startup function"""
    print("🎯 Daydreamer AI Web Application")
    print("=" * 40)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the web_app directory.")
        sys.exit(1)
    
    print("\n🌐 Starting servers...")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all servers")
    print("-" * 40)
    
    # Start backend in a separate process
    backend_process = subprocess.Popen([sys.executable, "main.py"])
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    # Start frontend
    try:
        frontend_process = subprocess.Popen(["npm", "run", "dev"])
        
        # Wait for processes
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for processes to terminate
        backend_process.wait()
        frontend_process.wait()
        
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
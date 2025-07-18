#!/usr/bin/env python3
"""
Ollama System Check

Checks if Ollama is installed, running, and has the required models.
Provides instructions for setup if needed.
"""

import subprocess
import sys

def check_ollama_installation():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            print(f"Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is installed but not responding properly")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama service is running")
            return True, result.stdout
        else:
            print("❌ Ollama service is not running")
            return False, result.stderr
    except Exception as e:
        print(f"❌ Error checking Ollama service: {e}")
        return False, str(e)

def check_models(model_list):
    """Check if required models are available"""
    recommended_models = ['gemma3n:3b', 'llama3.2:3b', 'phi3:mini']
    available_models = []
    
    print("\nChecking available models...")
    lines = model_list.split('\n')
    for line in lines[1:]:  # Skip header
        if line.strip():
            model_name = line.split()[0]
            available_models.append(model_name)
            print(f"  📦 {model_name}")
    
    print(f"\nRecommended models for research:")
    for model in recommended_models:
        if any(model.startswith(available.split(':')[0]) for available in available_models):
            print(f"  ✅ {model} (or compatible version available)")
        else:
            print(f"  ❌ {model} (not available)")
    
    return available_models

def provide_setup_instructions():
    """Provide setup instructions if Ollama is not properly configured"""
    print("\n" + "="*60)
    print("OLLAMA SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. Install Ollama:")
    print("   Visit: https://ollama.com/download")
    print("   Or use: curl -fsSL https://ollama.ai/install.sh | sh")
    
    print("\n2. Start Ollama service:")
    print("   ollama serve")
    
    print("\n3. Install recommended models:")
    print("   ollama pull gemma3n:3b")
    print("   ollama pull llama3.2:3b")
    print("   ollama pull phi3:mini")
    
    print("\n4. Test installation:")
    print("   ollama list")
    print("   python check_ollama.py")
    
    print("\nNote: The research chat system will work without Ollama")
    print("using the transformers fallback, but Ollama provides")
    print("better open-source model capabilities.")

def main():
    """Main function to check Ollama setup"""
    print("🔍 OLLAMA SYSTEM CHECK")
    print("="*40)
    
    # Check installation
    if not check_ollama_installation():
        provide_setup_instructions()
        return
    
    # Check service
    is_running, output = check_ollama_service()
    if not is_running:
        print(f"\nError output: {output}")
        print("\n💡 Try starting Ollama with: ollama serve")
        provide_setup_instructions()
        return
    
    # Check models
    available_models = check_models(output)
    
    if available_models:
        print(f"\n✅ Ollama is ready for research chat!")
        print(f"Found {len(available_models)} available models")
    else:
        print(f"\n⚠️ No models found. Install models with:")
        print("   ollama pull gemma3n:3b")
    
    print("\n🔬 You can now run: python research_chat.py")

if __name__ == "__main__":
    main()
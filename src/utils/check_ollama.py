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
    """Check available models and show compatibility"""
    recommended_models = ['gemma3n:3b', 'llama3.2:3b', 'phi3:mini']
    available_models = []
    
    print("\nAvailable models:")
    lines = model_list.split('\n')
    for line in lines[1:]:  # Skip header
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                model_name = parts[0]
                model_id = parts[1]
                model_size = parts[2]
                available_models.append(model_name)
                print(f"  📦 {model_name} (ID: {model_id[:12]}..., Size: {model_size})")
    
    if available_models:
        print(f"\nModel compatibility analysis:")
        gemma_models = [m for m in available_models if m.startswith('gemma')]
        llama_models = [m for m in available_models if m.startswith('llama')]
        phi_models = [m for m in available_models if m.startswith('phi')]
        
        if gemma_models:
            print(f"  ✅ Gemma models: {', '.join(gemma_models)}")
        if llama_models:
            print(f"  ✅ Llama models: {', '.join(llama_models)}")
        if phi_models:
            print(f"  ✅ Phi models: {', '.join(phi_models)}")
        
        print(f"\nRecommended models for research:")
        for model in recommended_models:
            base_name = model.split(':')[0]
            compatible = [m for m in available_models if m.startswith(base_name)]
            if compatible:
                print(f"  ✅ {model} (available: {', '.join(compatible)})")
            else:
                print(f"  ❌ {model} (not available)")
    
    return available_models

def get_best_available_model(available_models):
    """Determine the best available model based on preferences"""
    if not available_models:
        return None
    
    # Priority order for model selection
    model_preferences = [
        'gemma3n:e4b',      # High-end variant
        'gemma3n:latest',   # Latest version
        'gemma3n:8b',       # Larger model
        'gemma3n:3b',       # Standard model
        'gemma3n',          # Any gemma3n
        'gemma:7b',         # Gemma family
        'gemma:latest',
        'llama3.2:latest',  # Llama family
        'llama3.2:8b',
        'llama3.2:3b',
        'llama3.2',
        'phi3:latest',      # Phi family
        'phi3:mini',
        'phi3'
    ]
    
    # Find the best match
    for preferred in model_preferences:
        for available in available_models:
            if available == preferred or (preferred.endswith(':') and available.startswith(preferred[:-1])):
                return available
            # Partial match for base model names
            if ':' not in preferred and available.startswith(preferred):
                return available
    
    # If no preferred match, return the first available
    return available_models[0] if available_models else None

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
        best_model = get_best_available_model(available_models)
        print(f"\n✅ Ollama is ready for research chat!")
        print(f"Found {len(available_models)} available models")
        print(f"🎯 Recommended model: {best_model}")
    else:
        print(f"\n⚠️ No models found. Install models with:")
        print("   ollama pull gemma3n:3b")
    
    print("\n🔬 You can now run: python research_chat.py")

def get_available_models():
    """Get list of available Ollama models (for use by other modules)"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            available_models = []
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        model_name = parts[0]
                        available_models.append(model_name)
            return available_models
    except Exception:
        pass
    return []

def get_recommended_model():
    """Get the recommended Ollama model for research chat"""
    available_models = get_available_models()
    return get_best_available_model(available_models)

if __name__ == "__main__":
    main()
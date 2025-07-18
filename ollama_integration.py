#!/usr/bin/env python3
"""
Ollama Integration Module
=========================

This module provides a clean interface for Ollama integration with fallback
to transformers when Ollama is not available.
"""

import asyncio
import json
import subprocess
import time
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from datetime import datetime

# Try to import Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Try to import transformers for fallback
try:
    from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class ModelResponse:
    """Response from AI model"""
    content: str
    tokens_used: int
    processing_time: float
    model_name: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelRequest:
    """Request to AI model"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 300
    top_p: float = 0.9
    context: Optional[str] = None


class OllamaClient:
    """Client for Ollama API integration"""
    
    def __init__(self, model_name: str = "gemma3n:3b", host: str = "localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of the Ollama model to use
            host: Ollama server host and port
        """
        self.model_name = model_name
        self.host = host
        self.client = None
        
        if OLLAMA_AVAILABLE:
            try:
                # Test connection
                ollama.list()
                self.client = ollama
                print(f"✅ Connected to Ollama with model: {model_name}")
            except Exception as e:
                print(f"⚠️ Failed to connect to Ollama: {e}")
                self.client = None
        else:
            print("⚠️ Ollama not available")
    
    async def generate_response(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response using Ollama.
        
        Args:
            request: Model request parameters
            
        Returns:
            Model response
        """
        if not self.client:
            return ModelResponse(
                content="Ollama client not available",
                tokens_used=0,
                processing_time=0.0,
                model_name=self.model_name,
                error="Ollama client not initialized"
            )
        
        start_time = time.time()
        
        try:
            # Build the prompt
            full_prompt = request.prompt
            if request.context:
                full_prompt = f"{request.context}\n\n{request.prompt}"
            
            # Make the request
            response = await asyncio.to_thread(
                self.client.generate,
                model=self.model_name,
                prompt=full_prompt,
                options={
                    'temperature': request.temperature,
                    'top_p': request.top_p,
                    'num_predict': request.max_tokens
                }
            )
            
            processing_time = time.time() - start_time
            content = response.get('response', '')
            
            return ModelResponse(
                content=content,
                tokens_used=len(content.split()),  # Rough token estimate
                processing_time=processing_time,
                model_name=self.model_name,
                metadata={
                    'total_duration': response.get('total_duration'),
                    'load_duration': response.get('load_duration'),
                    'prompt_eval_count': response.get('prompt_eval_count'),
                    'eval_count': response.get('eval_count')
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ModelResponse(
                content="",
                tokens_used=0,
                processing_time=processing_time,
                model_name=self.model_name,
                error=f"Ollama generation error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """Check if Ollama is available and working"""
        return self.client is not None
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        if not self.client:
            return []
        
        try:
            models = self.client.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception:
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if not self.client:
            return {}
        
        try:
            models = self.client.list()
            for model in models.get('models', []):
                if model['name'] == self.model_name:
                    return model
        except Exception:
            pass
        
        return {}


class TransformersClient:
    """Fallback client using HuggingFace Transformers"""
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize Transformers client.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if TRANSFORMERS_AVAILABLE:
            try:
                print(f"🔄 Loading transformers model: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Set pad token if not available
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Move to device
                self.model.to(self.device)
                
                print(f"✅ Transformers model loaded on {self.device}")
            except Exception as e:
                print(f"⚠️ Failed to load transformers model: {e}")
                self.model = None
                self.tokenizer = None
        else:
            print("⚠️ Transformers not available")
    
    async def generate_response(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response using Transformers.
        
        Args:
            request: Model request parameters
            
        Returns:
            Model response
        """
        if not self.model or not self.tokenizer:
            return ModelResponse(
                content="Transformers client not available",
                tokens_used=0,
                processing_time=0.0,
                model_name=self.model_name,
                error="Transformers client not initialized"
            )
        
        start_time = time.time()
        
        try:
            # Build the prompt
            full_prompt = request.prompt
            if request.context:
                full_prompt = f"{request.context}\n\nUser: {request.prompt}\nAI:"
            else:
                full_prompt = f"User: {request.prompt}\nAI:"
            
            # Tokenize
            inputs = self.tokenizer.encode(full_prompt, return_tensors='pt', truncation=True, max_length=1024)
            inputs = inputs.to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = await asyncio.to_thread(
                    self.model.generate,
                    inputs,
                    max_length=inputs.shape[1] + request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract AI response part
            if "AI:" in full_response:
                response = full_response.split("AI:")[-1].strip()
            else:
                response = full_response[len(full_prompt):].strip()
            
            processing_time = time.time() - start_time
            
            return ModelResponse(
                content=response,
                tokens_used=len(outputs[0]) - len(inputs[0]),
                processing_time=processing_time,
                model_name=self.model_name,
                metadata={
                    'device': self.device,
                    'input_tokens': len(inputs[0]),
                    'output_tokens': len(outputs[0])
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ModelResponse(
                content="",
                tokens_used=0,
                processing_time=processing_time,
                model_name=self.model_name,
                error=f"Transformers generation error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """Check if Transformers is available and working"""
        return self.model is not None and self.tokenizer is not None


class ModelManager:
    """
    Manages multiple model clients with automatic fallback.
    
    Tries Ollama first, falls back to Transformers if needed.
    """
    
    def __init__(self, 
                 ollama_model: str = "gemma3n:3b",
                 transformers_model: str = "gpt2",
                 ollama_host: str = "localhost:11434"):
        """
        Initialize model manager.
        
        Args:
            ollama_model: Ollama model name
            transformers_model: Transformers model name
            ollama_host: Ollama server host
        """
        self.ollama_client = None
        self.transformers_client = None
        self.active_client = None
        
        # Try to initialize Ollama first
        if OLLAMA_AVAILABLE:
            self.ollama_client = OllamaClient(ollama_model, ollama_host)
            if self.ollama_client.is_available():
                self.active_client = self.ollama_client
                print(f"🎯 Using Ollama as primary model: {ollama_model}")
        
        # Initialize Transformers as fallback
        if not self.active_client and TRANSFORMERS_AVAILABLE:
            self.transformers_client = TransformersClient(transformers_model)
            if self.transformers_client.is_available():
                self.active_client = self.transformers_client
                print(f"🎯 Using Transformers as fallback model: {transformers_model}")
        
        if not self.active_client:
            print("❌ No AI models available")
    
    async def generate_response(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response using the best available model.
        
        Args:
            request: Model request
            
        Returns:
            Model response
        """
        if not self.active_client:
            return ModelResponse(
                content="No AI models available",
                tokens_used=0,
                processing_time=0.0,
                model_name="none",
                error="No models initialized"
            )
        
        # Try primary client
        response = await self.active_client.generate_response(request)
        
        # If primary failed and we have a fallback, try it
        if response.error and self.active_client == self.ollama_client and self.transformers_client:
            print("🔄 Ollama failed, trying Transformers fallback...")
            response = await self.transformers_client.generate_response(request)
        
        return response
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        info = {
            'active_model': None,
            'ollama_available': False,
            'transformers_available': False,
            'available_models': []
        }
        
        if self.active_client:
            info['active_model'] = self.active_client.model_name
        
        if self.ollama_client and self.ollama_client.is_available():
            info['ollama_available'] = True
            info['available_models'].extend(self.ollama_client.get_available_models())
        
        if self.transformers_client and self.transformers_client.is_available():
            info['transformers_available'] = True
            info['available_models'].append(self.transformers_client.model_name)
        
        return info
    
    def switch_model(self, model_type: str, model_name: str = None) -> bool:
        """
        Switch to a different model.
        
        Args:
            model_type: "ollama" or "transformers"
            model_name: Optional specific model name
            
        Returns:
            True if switch was successful
        """
        if model_type == "ollama" and self.ollama_client:
            if model_name:
                # Create new Ollama client with different model
                new_client = OllamaClient(model_name)
                if new_client.is_available():
                    self.ollama_client = new_client
                    self.active_client = new_client
                    return True
            elif self.ollama_client.is_available():
                self.active_client = self.ollama_client
                return True
        
        elif model_type == "transformers" and self.transformers_client:
            if model_name:
                # Create new Transformers client with different model
                new_client = TransformersClient(model_name)
                if new_client.is_available():
                    self.transformers_client = new_client
                    self.active_client = new_client
                    return True
            elif self.transformers_client.is_available():
                self.active_client = self.transformers_client
                return True
        
        return False


# Utility functions
def detect_available_ollama_models() -> List[str]:
    """Detect available Ollama models"""
    if not OLLAMA_AVAILABLE:
        return []
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = []
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        models.append(parts[0])
            return models
    except Exception:
        pass
    
    return []


def get_best_available_model(available_models: List[str]) -> Optional[str]:
    """Get the best available Ollama model"""
    if not available_models:
        return None
    
    # Preference order
    preferences = [
        'gemma3n:e4b', 'gemma3n:latest', 'gemma3n:8b', 'gemma3n:3b', 'gemma3n',
        'gemma:7b', 'gemma:latest', 'llama3.2:latest', 'llama3.2:8b', 'llama3.2:3b',
        'phi3:latest', 'phi3:mini'
    ]
    
    for preferred in preferences:
        for available in available_models:
            if available == preferred or available.startswith(preferred.split(':')[0]):
                return available
    
    return available_models[0]


async def test_model_client(client: Union[OllamaClient, TransformersClient, ModelManager]) -> Dict[str, Any]:
    """
    Test a model client with a simple request.
    
    Args:
        client: Model client to test
        
    Returns:
        Test results
    """
    test_request = ModelRequest(
        prompt="Hello! Please respond with a brief greeting.",
        max_tokens=50
    )
    
    start_time = time.time()
    response = await client.generate_response(test_request)
    total_time = time.time() - start_time
    
    return {
        'success': not bool(response.error),
        'response_content': response.content,
        'processing_time': response.processing_time,
        'total_time': total_time,
        'tokens_used': response.tokens_used,
        'model_name': response.model_name,
        'error': response.error
    }


# Convenience function to create a configured model manager
def create_model_manager(config: Dict[str, Any] = None) -> ModelManager:
    """
    Create a model manager with configuration.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured ModelManager
    """
    if not config:
        config = {}
    
    ollama_model = config.get('ollama_model', 'gemma3n:3b')
    transformers_model = config.get('transformers_model', 'gpt2')
    ollama_host = config.get('ollama_host', 'localhost:11434')
    
    # Auto-detect best Ollama model if requested
    if ollama_model == 'auto':
        available_models = detect_available_ollama_models()
        if available_models:
            ollama_model = get_best_available_model(available_models)
            print(f"🔍 Auto-detected Ollama model: {ollama_model}")
        else:
            ollama_model = 'gemma3n:3b'  # fallback
    
    return ModelManager(ollama_model, transformers_model, ollama_host)
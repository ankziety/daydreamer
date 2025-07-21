#!/usr/bin/env python3
"""
Test file for the Daydreamer AI Web Application
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add the parent directory to Python path to import Daydreamer modules
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

# Mock the relative imports that the Daydreamer AI system expects
mock_prompts = Mock()
mock_chain_of_thought = Mock()
mock_day_dreaming = Mock()
mock_memory_manager = Mock()
mock_ollama_integration = Mock()

# Create mock classes and functions
class MockDaydreamerPrompts:
    pass

class MockChainOfThoughtProcessor:
    pass

class MockChainOfThoughtResult:
    pass

class MockDaydreamingEngine:
    pass

class MockDaydreamSession:
    pass

class MockPersistentMemoryManager:
    pass

class MockModelManager:
    pass

def mock_get_general_response_prompt():
    return "Mock prompt"

def mock_get_conversation_context():
    return "Mock context"

def mock_analyze_user_interests():
    return "Mock interests"

def mock_create_model_manager():
    return MockModelManager()

# Set up the mock modules
sys.modules['prompts'] = Mock()
sys.modules['prompts'].DaydreamerPrompts = MockDaydreamerPrompts
sys.modules['prompts'].get_general_response_prompt = mock_get_general_response_prompt

sys.modules['chain_of_thought'] = Mock()
sys.modules['chain_of_thought'].ChainOfThoughtProcessor = MockChainOfThoughtProcessor
sys.modules['chain_of_thought'].ChainOfThoughtResult = MockChainOfThoughtResult

sys.modules['day_dreaming'] = Mock()
sys.modules['day_dreaming'].DaydreamingEngine = MockDaydreamingEngine
sys.modules['day_dreaming'].DaydreamSession = MockDaydreamSession

sys.modules['memory_manager'] = Mock()
sys.modules['memory_manager'].PersistentMemoryManager = MockPersistentMemoryManager
sys.modules['memory_manager'].get_conversation_context = mock_get_conversation_context
sys.modules['memory_manager'].analyze_user_interests = mock_analyze_user_interests

sys.modules['ollama_integration'] = Mock()
sys.modules['ollama_integration'].ModelManager = MockModelManager
sys.modules['ollama_integration'].create_model_manager = mock_create_model_manager

# Now import the actual Daydreamer AI modules
try:
    from src.core.daydreamer_ai import DaydreamerAI
    from src.memory.memory_manager import PersistentMemoryManager
    from src.integration.ollama_integration import ModelManager, create_model_manager
    DAYDREAMER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Daydreamer AI modules: {e}")
    DAYDREAMER_AVAILABLE = False

# Import the web app
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_settings_endpoint():
    """Test the settings endpoint"""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "theme" in data
    assert "notifications" in data

def test_models_endpoint():
    """Test the models endpoint"""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)

def test_analytics_endpoint():
    """Test the analytics endpoint"""
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "conversation_stats" in data
    assert "system_metrics" in data

def test_conversations_endpoint():
    """Test the conversations endpoint"""
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert isinstance(data["conversations"], list)

def test_chat_endpoint():
    """Test the chat endpoint with a simple message"""
    chat_data = {
        "message": "Hello, this is a test message",
        "conversation_id": None
    }
    response = client.post("/api/chat", json=chat_data)
    # The response might be 200 (success) or 503 (service unavailable if Ollama is not running)
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data

def test_websocket_endpoint():
    """Test the WebSocket endpoint"""
    with client.websocket_connect("/ws") as websocket:
        # Send a test message
        websocket.send_json({"message": "Hello WebSocket"})
        # We should receive a response
        data = websocket.receive_json()
        assert "response" in data

@pytest.mark.skipif(not DAYDREAMER_AVAILABLE, reason="Daydreamer AI system not available")
def test_daydreamer_ai_import():
    """Test that we can import and create DaydreamerAI instance"""
    # This test verifies that the actual Daydreamer AI system is accessible
    try:
        # Try to create a DaydreamerAI instance
        # Note: This might fail if Ollama is not running, but the import should work
        daydreamer = DaydreamerAI()
        assert daydreamer is not None
    except Exception as e:
        # If it fails due to Ollama not running, that's expected
        # But the import should still work
        assert "DaydreamerAI" in str(type(e)) or "ollama" in str(e).lower()

@pytest.mark.skipif(not DAYDREAMER_AVAILABLE, reason="Daydreamer AI system not available")
def test_memory_manager_import():
    """Test that we can import and create PersistentMemoryManager instance"""
    try:
        memory_manager = PersistentMemoryManager()
        assert memory_manager is not None
    except Exception as e:
        # Should be able to create the memory manager
        assert "PersistentMemoryManager" in str(type(e))

@pytest.mark.skipif(not DAYDREAMER_AVAILABLE, reason="Daydreamer AI system not available")
def test_model_manager_import():
    """Test that we can import and create ModelManager instance"""
    try:
        model_manager = create_model_manager()
        assert model_manager is not None
    except Exception as e:
        # If it fails due to Ollama not running, that's expected
        assert "ModelManager" in str(type(e)) or "ollama" in str(e).lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
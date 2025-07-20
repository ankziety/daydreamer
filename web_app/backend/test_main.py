#!/usr/bin/env python3
"""
Test suite for Daydreamer Web Application Backend
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_chat_endpoint():
    """Test chat endpoint"""
    response = client.post("/api/chat", json={
        "message": "Hello, how are you?",
        "conversation_id": None
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert "thinking_time" in data
    assert "daydream_time" in data

def test_conversations_endpoint():
    """Test conversations endpoint"""
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_settings_endpoint():
    """Test settings endpoint"""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "theme" in data
    assert "language" in data
    assert "auto_save" in data

def test_models_endpoint():
    """Test models endpoint"""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_analytics_endpoint():
    """Test analytics endpoint"""
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversations" in data
    assert "total_messages" in data
    assert "average_response_time" in data

def test_tests_endpoint():
    """Test tests endpoint"""
    response = client.get("/api/tests")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/api/metrics/current")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data

if __name__ == "__main__":
    pytest.main([__file__])
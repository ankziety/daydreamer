#!/usr/bin/env python3
"""
Test file for the Daydreamer AI Web Application
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_models_endpoint():
    """Test the models API endpoint"""
    response = client.get("/api/models")
    # This might return 503 if Daydreamer AI is not initialized
    assert response.status_code in [200, 503]

def test_api_settings_endpoint():
    """Test the settings API endpoint"""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "theme" in data

def test_api_analytics_endpoint():
    """Test the analytics API endpoint"""
    response = client.get("/api/analytics")
    # This might return 503 if Daydreamer AI is not initialized
    assert response.status_code in [200, 503]

def test_api_conversations_endpoint():
    """Test the conversations API endpoint"""
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

if __name__ == "__main__":
    pytest.main([__file__])
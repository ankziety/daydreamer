#!/usr/bin/env python3
"""
Daydreamer Web Application - Main Backend
=========================================

FastAPI backend for the Daydreamer web interface with:
- Chat interface with daydreamer AI
- Settings management
- Analytics and monitoring
- Test automation
- Persistent SQLite storage
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Add the parent directory to Python path to import daydreamer modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

from database import init_db, get_db_session
from models import (
    Conversation, UserSettings, AIModelConfig, TestResult, 
    SystemMetrics, ChatMessage, ConversationCreate, SettingsUpdate
)
from services.daydreamer_service import DaydreamerService
from services.analytics_service import AnalyticsService
from services.test_service import TestService
from services.metrics_service import MetricsService
from utils.auth import get_current_user, create_access_token
from utils.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global settings
settings = Settings()

# Global services
daydreamer_service: Optional[DaydreamerService] = None
analytics_service: Optional[AnalyticsService] = None
test_service: Optional[TestService] = None
metrics_service: Optional[MetricsService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global daydreamer_service, analytics_service, test_service, metrics_service
    
    # Startup
    logger.info("Starting Daydreamer Web Application...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    daydreamer_service = DaydreamerService()
    analytics_service = AnalyticsService()
    test_service = TestService()
    metrics_service = MetricsService()
    
    # Start background tasks
    asyncio.create_task(metrics_service.start_monitoring())
    
    logger.info("Daydreamer Web Application started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Daydreamer Web Application...")
    if metrics_service:
        await metrics_service.stop_monitoring()

# Create FastAPI app
app = FastAPI(
    title="Daydreamer Web Interface",
    description="Web interface for Daydreamer AI system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for frontend)
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuing chat")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    thinking_time: float = Field(..., description="Time spent thinking")
    daydream_time: float = Field(..., description="Time spent daydreaming")

class ModelConfigUpdate(BaseModel):
    model_name: str = Field(..., description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Max tokens")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Top P")
    verbose: bool = Field(False, description="Verbose mode")

class TestRequest(BaseModel):
    test_type: str = Field(..., description="Type of test to run")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Test parameters")

# API Routes

@app.get("/")
async def root():
    """Serve the main application"""
    return HTMLResponse(open("frontend/dist/index.html").read())

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message with daydreamer"""
    try:
        response = await daydreamer_service.process_message(
            request.message, 
            request.conversation_id
        )
        return response
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def get_conversations(skip: int = 0, limit: int = 50):
    """Get conversation history"""
    try:
        conversations = await daydreamer_service.get_conversations(skip, limit)
        return conversations
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    try:
        conversation = await daydreamer_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        await daydreamer_service.delete_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations/clear")
async def clear_all_conversations():
    """Clear all conversations"""
    try:
        await daydreamer_service.clear_conversations()
        return {"message": "All conversations cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    try:
        settings = await daydreamer_service.get_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/settings")
async def update_settings(settings_update: SettingsUpdate):
    """Update settings"""
    try:
        updated_settings = await daydreamer_service.update_settings(settings_update)
        return updated_settings
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """Get available AI models"""
    try:
        models = await daydreamer_service.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/models/config")
async def update_model_config(config: ModelConfigUpdate):
    """Update AI model configuration"""
    try:
        updated_config = await daydreamer_service.update_model_config(config)
        return updated_config
    except Exception as e:
        logger.error(f"Error updating model config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/models/restart")
async def restart_model():
    """Restart the AI model"""
    try:
        await daydreamer_service.restart_model()
        return {"message": "Model restarted successfully"}
    except Exception as e:
        logger.error(f"Error restarting model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        overview = await analytics_service.get_overview()
        return overview
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/conversations")
async def get_conversation_analytics(days: int = 30):
    """Get conversation analytics"""
    try:
        analytics = await analytics_service.get_conversation_analytics(days)
        return analytics
    except Exception as e:
        logger.error(f"Error getting conversation analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance")
async def get_performance_analytics(days: int = 30):
    """Get performance analytics"""
    try:
        analytics = await analytics_service.get_performance_analytics(days)
        return analytics
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/current")
async def get_current_metrics():
    """Get current system metrics"""
    try:
        metrics = await metrics_service.get_current_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/history")
async def get_metrics_history(hours: int = 24):
    """Get metrics history"""
    try:
        history = await metrics_service.get_metrics_history(hours)
        return history
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests")
async def get_tests():
    """Get available tests"""
    try:
        tests = await test_service.get_available_tests()
        return tests
    except Exception as e:
        logger.error(f"Error getting tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tests/run")
async def run_test(request: TestRequest):
    """Run a test"""
    try:
        result = await test_service.run_test(request.test_type, request.parameters)
        return result
    except Exception as e:
        logger.error(f"Error running test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tests/results")
async def get_test_results(limit: int = 50):
    """Get test results"""
    try:
        results = await test_service.get_test_results(limit)
        return results
    except Exception as e:
        logger.error(f"Error getting test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            conversation_id = data.get("conversation_id")
            
            # Process message
            response = await daydreamer_service.process_message(message, conversation_id)
            
            # Send response back
            await websocket.send_json({
                "type": "response",
                "data": response.dict()
            })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
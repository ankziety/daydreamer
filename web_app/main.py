#!/usr/bin/env python3
"""
Daydreamer AI Web Application
=============================

FastAPI backend for the Daydreamer AI web interface.
Provides REST API endpoints for chat, settings, analytics, and model management.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# Add the parent directory to Python path to import Daydreamer modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.daydreamer_ai import DaydreamerAI
from src.memory.memory_manager import PersistentMemoryManager
from src.integration.ollama_integration import ModelManager, create_model_manager

# Initialize FastAPI app
app = FastAPI(
    title="Daydreamer AI Web Interface",
    description="Web interface for the Daydreamer AI system with chat, analytics, and model management",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
daydreamer_instance: Optional[DaydreamerAI] = None
memory_manager: Optional[PersistentMemoryManager] = None
model_manager: Optional[ModelManager] = None
conversation_history: List[Dict[str, Any]] = []
system_metrics: Dict[str, Any] = {}

# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(..., description="Response timestamp")
    thinking_time: float = Field(..., description="Time spent thinking")
    daydream_time: float = Field(..., description="Time spent daydreaming")

class ModelConfig(BaseModel):
    model_name: str = Field(..., description="Model name")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: int = Field(2048, description="Maximum tokens")
    verbose: bool = Field(False, description="Verbose mode")

class Settings(BaseModel):
    theme: str = Field("dark", description="UI theme")
    auto_save: bool = Field(True, description="Auto-save conversations")
    max_history: int = Field(100, description="Maximum conversation history")
    notifications: bool = Field(True, description="Enable notifications")

class AnalyticsData(BaseModel):
    total_conversations: int
    total_messages: int
    average_response_time: float
    popular_topics: List[Dict[str, Any]]
    daily_activity: List[Dict[str, Any]]
    system_uptime: float

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Initialize Daydreamer AI system
async def initialize_daydreamer():
    """Initialize the Daydreamer AI system"""
    global daydreamer_instance, memory_manager, model_manager
    
    try:
        # Initialize memory manager
        memory_db_path = os.path.join(os.path.dirname(__file__), "data", "daydreamer_memory.db")
        os.makedirs(os.path.dirname(memory_db_path), exist_ok=True)
        memory_manager = PersistentMemoryManager(memory_db_path)
        
        # Initialize model manager
        model_config = {
            "model_name": "llama2",
            "temperature": 0.7,
            "max_tokens": 2048,
            "verbose": False
        }
        model_manager = create_model_manager(model_config)
        
        # Initialize Daydreamer AI
        daydreamer_instance = DaydreamerAI(
            memory_db_path=memory_db_path,
            model_config=model_config
        )
        
        print("Daydreamer AI system initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing Daydreamer AI: {e}")
        return False

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    await initialize_daydreamer()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "daydreamer_initialized": daydreamer_instance is not None
    }

# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message"""
    if not daydreamer_instance:
        raise HTTPException(status_code=503, detail="Daydreamer AI not initialized")
    
    try:
        start_time = datetime.now()
        
        # Process the message through Daydreamer AI
        response = await daydreamer_instance.process_user_input(request.message)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Store in conversation history
        conversation_history.append({
            "id": conversation_id,
            "user_message": request.message,
            "ai_response": response,
            "timestamp": start_time.isoformat(),
            "processing_time": processing_time
        })
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            timestamp=end_time,
            thinking_time=processing_time * 0.6,  # Estimate
            daydream_time=processing_time * 0.4   # Estimate
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if not daydreamer_instance:
                await websocket.send_text(json.dumps({
                    "error": "Daydreamer AI not initialized"
                }))
                continue
            
            # Process message
            response = await daydreamer_instance.process_user_input(message_data["message"])
            
            # Send response back
            await websocket.send_text(json.dumps({
                "response": response,
                "timestamp": datetime.now().isoformat()
            }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Settings endpoints
@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    # Load settings from file or return defaults
    settings_file = os.path.join(os.path.dirname(__file__), "data", "settings.json")
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    
    return Settings().dict()

@app.post("/api/settings")
async def update_settings(settings: Settings):
    """Update settings"""
    settings_file = os.path.join(os.path.dirname(__file__), "data", "settings.json")
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    
    with open(settings_file, 'w') as f:
        json.dump(settings.dict(), f, indent=2)
    
    return {"message": "Settings updated successfully"}

# Model management endpoints
@app.get("/api/models")
async def get_models():
    """Get available models and current configuration"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    
    model_info = model_manager.get_model_info()
    return {
        "available_models": model_info.get("available_models", []),
        "current_model": model_info.get("active_model", "None"),
        "configuration": model_info.get("configuration", {})
    }

@app.post("/api/models/restart")
async def restart_model(config: ModelConfig):
    """Restart the AI model with new configuration"""
    global daydreamer_instance
    
    try:
        # Reinitialize with new config
        model_config = config.dict()
        daydreamer_instance = DaydreamerAI(
            memory_db_path=os.path.join(os.path.dirname(__file__), "data", "daydreamer_memory.db"),
            model_config=model_config
        )
        
        return {"message": "Model restarted successfully", "config": model_config}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting model: {str(e)}")

# Analytics endpoints
@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data"""
    if not memory_manager:
        raise HTTPException(status_code=503, detail="Memory manager not initialized")
    
    try:
        # Get memory stats
        stats = memory_manager.get_memory_stats()
        
        # Calculate analytics
        total_conversations = len(conversation_history)
        total_messages = sum(len(conv.get("messages", [])) for conv in conversation_history)
        
        # Calculate average response time
        response_times = [conv.get("processing_time", 0) for conv in conversation_history]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Generate daily activity data (mock for now)
        daily_activity = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            daily_activity.append({
                "date": date.strftime("%Y-%m-%d"),
                "conversations": len([c for c in conversation_history 
                                   if c.get("timestamp", "").startswith(date.strftime("%Y-%m-%d"))])
            })
        
        return AnalyticsData(
            total_conversations=total_conversations,
            total_messages=total_messages,
            average_response_time=avg_response_time,
            popular_topics=[],  # Would need to implement topic extraction
            daily_activity=daily_activity,
            system_uptime=0.0  # Would need to implement uptime tracking
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

# Conversation management endpoints
@app.get("/api/conversations")
async def get_conversations():
    """Get conversation history"""
    return conversation_history

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a specific conversation"""
    global conversation_history
    conversation_history = [c for c in conversation_history if c.get("id") != conversation_id]
    return {"message": "Conversation deleted successfully"}

@app.delete("/api/conversations")
async def clear_conversations():
    """Clear all conversations"""
    global conversation_history
    conversation_history = []
    return {"message": "All conversations cleared successfully"}

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_file):
        with open(html_file, 'r') as f:
            return f.read()
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daydreamer AI</title>
        </head>
        <body>
            <h1>Daydreamer AI Web Interface</h1>
            <p>Frontend not found. Please build the frontend application.</p>
        </body>
        </html>
        """

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
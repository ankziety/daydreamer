#!/usr/bin/env python3
"""
Database Models
==============

SQLAlchemy models for the Daydreamer web application.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field

from database import Base

# SQLAlchemy Models

class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    message_count = Column(Integer, default=0)
    total_thinking_time = Column(Float, default=0.0)
    total_daydream_time = Column(Float, default=0.0)
    tags = Column(JSON, default=list)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    thinking_time = Column(Float, default=0.0)
    daydream_time = Column(Float, default=0.0)
    tokens_used = Column(Integer, default=0)
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

class UserSettings(Base):
    """User settings model"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String(20), default="dark")  # 'dark' or 'light'
    language = Column(String(10), default="en")
    auto_save = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    max_conversation_history = Column(Integer, default=100)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AIModelConfig(Base):
    """AI model configuration model"""
    __tablename__ = "ai_model_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2048)
    top_p = Column(Float, default=0.9)
    verbose = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SystemMetrics(Base):
    """System metrics model"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    active_conversations = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    model_status = Column(String(50), default="unknown")

class TestResult(Base):
    """Test result model"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(100), nullable=False)
    test_type = Column(String(50), nullable=False)
    status = Column(String(20))  # 'passed', 'failed', 'error'
    duration = Column(Float)
    parameters = Column(JSON, default=dict)
    results = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

# Pydantic Models for API

class ChatMessageCreate(BaseModel):
    """Pydantic model for creating chat messages"""
    conversation_id: str
    role: str
    content: str
    thinking_time: float = 0.0
    daydream_time: float = 0.0
    tokens_used: int = 0

class ChatMessageResponse(BaseModel):
    """Pydantic model for chat message responses"""
    id: int
    conversation_id: str
    role: str
    content: str
    timestamp: datetime
    thinking_time: float
    daydream_time: float
    tokens_used: int

class ConversationCreate(BaseModel):
    """Pydantic model for creating conversations"""
    title: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ConversationResponse(BaseModel):
    """Pydantic model for conversation responses"""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    total_thinking_time: float
    total_daydream_time: float
    tags: List[str]
    messages: List[ChatMessageResponse] = Field(default_factory=list)

class SettingsUpdate(BaseModel):
    """Pydantic model for updating settings"""
    theme: Optional[str] = None
    language: Optional[str] = None
    auto_save: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    max_conversation_history: Optional[int] = None

class UserSettingsResponse(BaseModel):
    """Pydantic model for user settings responses"""
    id: int
    theme: str
    language: str
    auto_save: bool
    notifications_enabled: bool
    max_conversation_history: int
    created_at: datetime
    updated_at: datetime

class AIModelConfigUpdate(BaseModel):
    """Pydantic model for updating AI model config"""
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    verbose: bool = False

class AIModelConfigResponse(BaseModel):
    """Pydantic model for AI model config responses"""
    id: int
    model_name: str
    temperature: float
    max_tokens: int
    top_p: float
    verbose: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SystemMetricsResponse(BaseModel):
    """Pydantic model for system metrics responses"""
    id: int
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_conversations: int
    total_requests: int
    average_response_time: float
    model_status: str

class TestResultCreate(BaseModel):
    """Pydantic model for creating test results"""
    test_name: str
    test_type: str
    status: str
    duration: float
    parameters: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

class TestResultResponse(BaseModel):
    """Pydantic model for test result responses"""
    id: int
    test_name: str
    test_type: str
    status: str
    duration: float
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    error_message: Optional[str]
    created_at: datetime

# Analytics Models

class AnalyticsOverview(BaseModel):
    """Analytics overview model"""
    total_conversations: int
    total_messages: int
    average_response_time: float
    total_thinking_time: float
    total_daydream_time: float
    active_conversations_today: int
    messages_today: int
    system_uptime_hours: float

class ConversationAnalytics(BaseModel):
    """Conversation analytics model"""
    date: str
    conversations: int
    messages: int
    average_thinking_time: float
    average_daydream_time: float

class PerformanceAnalytics(BaseModel):
    """Performance analytics model"""
    date: str
    average_response_time: float
    total_requests: int
    cpu_usage: float
    memory_usage: float
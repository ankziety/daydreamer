#!/usr/bin/env python3
"""
Database Models and SQLite Integration
=====================================

SQLAlchemy models and database utilities for the Daydreamer AI web interface.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()

class Conversation(Base):
    """Model for storing conversation data"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float, default=0.0)
    thinking_time = Column(Float, default=0.0)
    daydream_time = Column(Float, default=0.0)
    conversation_id = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    importance_score = Column(Float, default=0.0)

class Settings(Base):
    """Model for storing application settings"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelConfig(Base):
    """Model for storing AI model configurations"""
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2048)
    verbose = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemMetrics(Base):
    """Model for storing system metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)
    active_conversations = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)

class TestResult(Base):
    """Model for storing automated test results"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True)
    test_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # 'passed', 'failed', 'error'
    duration = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)

class DatabaseManager:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_path: str = "data/daydreamer_web.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create SQLite engine
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close a database session"""
        session.close()
    
    # Conversation methods
    def save_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """Save a conversation to the database"""
        session = self.get_session()
        try:
            conversation = Conversation(
                id=conversation_data.get("id"),
                user_message=conversation_data.get("user_message"),
                ai_response=conversation_data.get("ai_response"),
                timestamp=datetime.fromisoformat(conversation_data.get("timestamp")),
                processing_time=conversation_data.get("processing_time", 0.0),
                thinking_time=conversation_data.get("thinking_time", 0.0),
                daydream_time=conversation_data.get("daydream_time", 0.0),
                conversation_id=conversation_data.get("conversation_id"),
                tags=conversation_data.get("tags", []),
                importance_score=conversation_data.get("importance_score", 0.0)
            )
            session.add(conversation)
            session.commit()
            return conversation.id
        finally:
            self.close_session(session)
    
    def get_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get conversations from the database"""
        session = self.get_session()
        try:
            conversations = session.query(Conversation)\
                .order_by(Conversation.timestamp.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            return [
                {
                    "id": conv.id,
                    "user_message": conv.user_message,
                    "ai_response": conv.ai_response,
                    "timestamp": conv.timestamp.isoformat(),
                    "processing_time": conv.processing_time,
                    "thinking_time": conv.thinking_time,
                    "daydream_time": conv.daydream_time,
                    "conversation_id": conv.conversation_id,
                    "tags": conv.tags,
                    "importance_score": conv.importance_score
                }
                for conv in conversations
            ]
        finally:
            self.close_session(session)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from the database"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                session.delete(conversation)
                session.commit()
                return True
            return False
        finally:
            self.close_session(session)
    
    def clear_conversations(self) -> int:
        """Clear all conversations from the database"""
        session = self.get_session()
        try:
            count = session.query(Conversation).count()
            session.query(Conversation).delete()
            session.commit()
            return count
        finally:
            self.close_session(session)
    
    # Settings methods
    def save_setting(self, key: str, value: Any) -> bool:
        """Save a setting to the database"""
        session = self.get_session()
        try:
            # Convert value to JSON string
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            # Check if setting exists
            existing = session.query(Settings).filter(Settings.key == key).first()
            if existing:
                existing.value = value_str
                existing.updated_at = datetime.utcnow()
            else:
                setting = Settings(key=key, value=value_str)
                session.add(setting)
            
            session.commit()
            return True
        finally:
            self.close_session(session)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from the database"""
        session = self.get_session()
        try:
            setting = session.query(Settings).filter(Settings.key == key).first()
            if setting:
                try:
                    return json.loads(setting.value)
                except json.JSONDecodeError:
                    return setting.value
            return default
        finally:
            self.close_session(session)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings from the database"""
        session = self.get_session()
        try:
            settings = session.query(Settings).all()
            result = {}
            for setting in settings:
                try:
                    result[setting.key] = json.loads(setting.value)
                except json.JSONDecodeError:
                    result[setting.key] = setting.value
            return result
        finally:
            self.close_session(session)
    
    # Model configuration methods
    def save_model_config(self, config_data: Dict[str, Any]) -> int:
        """Save a model configuration to the database"""
        session = self.get_session()
        try:
            # Deactivate all other configs if this one is active
            if config_data.get("is_active", False):
                session.query(ModelConfig).update({"is_active": False})
            
            config = ModelConfig(
                name=config_data.get("name"),
                model_name=config_data.get("model_name"),
                temperature=config_data.get("temperature", 0.7),
                max_tokens=config_data.get("max_tokens", 2048),
                verbose=config_data.get("verbose", False),
                is_active=config_data.get("is_active", False)
            )
            session.add(config)
            session.commit()
            return config.id
        finally:
            self.close_session(session)
    
    def get_active_model_config(self) -> Optional[Dict[str, Any]]:
        """Get the active model configuration"""
        session = self.get_session()
        try:
            config = session.query(ModelConfig).filter(ModelConfig.is_active == True).first()
            if config:
                return {
                    "id": config.id,
                    "name": config.name,
                    "model_name": config.model_name,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "verbose": config.verbose,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat()
                }
            return None
        finally:
            self.close_session(session)
    
    def get_all_model_configs(self) -> List[Dict[str, Any]]:
        """Get all model configurations"""
        session = self.get_session()
        try:
            configs = session.query(ModelConfig).order_by(ModelConfig.created_at.desc()).all()
            return [
                {
                    "id": config.id,
                    "name": config.name,
                    "model_name": config.model_name,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "verbose": config.verbose,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat()
                }
                for config in configs
            ]
        finally:
            self.close_session(session)
    
    # System metrics methods
    def save_system_metrics(self, metrics_data: Dict[str, Any]) -> int:
        """Save system metrics to the database"""
        session = self.get_session()
        try:
            metrics = SystemMetrics(
                cpu_usage=metrics_data.get("cpu_usage", 0.0),
                memory_usage=metrics_data.get("memory_usage", 0.0),
                disk_usage=metrics_data.get("disk_usage", 0.0),
                active_conversations=metrics_data.get("active_conversations", 0),
                total_requests=metrics_data.get("total_requests", 0),
                average_response_time=metrics_data.get("average_response_time", 0.0)
            )
            session.add(metrics)
            session.commit()
            return metrics.id
        finally:
            self.close_session(session)
    
    def get_recent_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent system metrics"""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            metrics = session.query(SystemMetrics)\
                .filter(SystemMetrics.timestamp >= cutoff_time)\
                .order_by(SystemMetrics.timestamp.desc())\
                .all()
            
            return [
                {
                    "id": metric.id,
                    "timestamp": metric.timestamp.isoformat(),
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "disk_usage": metric.disk_usage,
                    "active_conversations": metric.active_conversations,
                    "total_requests": metric.total_requests,
                    "average_response_time": metric.average_response_time
                }
                for metric in metrics
            ]
        finally:
            self.close_session(session)
    
    # Test results methods
    def save_test_result(self, test_data: Dict[str, Any]) -> int:
        """Save a test result to the database"""
        session = self.get_session()
        try:
            test_result = TestResult(
                test_name=test_data.get("test_name"),
                status=test_data.get("status"),
                duration=test_data.get("duration", 0.0),
                details=test_data.get("details", {}),
                error_message=test_data.get("error_message")
            )
            session.add(test_result)
            session.commit()
            return test_result.id
        finally:
            self.close_session(session)
    
    def get_recent_test_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent test results"""
        session = self.get_session()
        try:
            results = session.query(TestResult)\
                .order_by(TestResult.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return [
                {
                    "id": result.id,
                    "test_name": result.test_name,
                    "status": result.status,
                    "duration": result.duration,
                    "timestamp": result.timestamp.isoformat(),
                    "details": result.details,
                    "error_message": result.error_message
                }
                for result in results
            ]
        finally:
            self.close_session(session)
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get test statistics"""
        session = self.get_session()
        try:
            total_tests = session.query(TestResult).count()
            passed_tests = session.query(TestResult).filter(TestResult.status == "passed").count()
            failed_tests = session.query(TestResult).filter(TestResult.status == "failed").count()
            error_tests = session.query(TestResult).filter(TestResult.status == "error").count()
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            }
        finally:
            self.close_session(session)

# Global database manager instance
db_manager = DatabaseManager()
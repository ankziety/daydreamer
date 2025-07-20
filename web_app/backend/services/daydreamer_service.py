#!/usr/bin/env python3
"""
Daydreamer Service
==================

Service layer for integrating with the Daydreamer AI system.
"""

import os
import sys
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

# Add the parent directory to Python path to import daydreamer modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from database import AsyncSessionLocal
from models import (
    Conversation, ChatMessage, UserSettings, AIModelConfig,
    ConversationCreate, ChatMessageCreate, SettingsUpdate,
    ConversationResponse, ChatMessageResponse, UserSettingsResponse,
    AIModelConfigResponse
)

# Import daydreamer modules
try:
    from src.core.daydreamer_ai import DaydreamerAI
    from src.ai_engines.ollama_integration import ModelManager
    DAYDREAMER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Daydreamer AI not available: {e}")
    DAYDREAMER_AVAILABLE = False

logger = logging.getLogger(__name__)

class DaydreamerService:
    """Service for interacting with the Daydreamer AI system"""
    
    def __init__(self):
        """Initialize the service"""
        self.daydreamer_ai: Optional[DaydreamerAI] = None
        self.model_manager: Optional[ModelManager] = None
        self._initialize_daydreamer()
    
    def _initialize_daydreamer(self):
        """Initialize the daydreamer AI system"""
        if not DAYDREAMER_AVAILABLE:
            logger.warning("Daydreamer AI not available - using mock responses")
            return
        
        try:
            # Initialize with default configuration
            model_config = {
                'verbose': False,
                'model_name': 'llama3.2:3b',
                'temperature': 0.7,
                'max_tokens': 2048,
                'top_p': 0.9
            }
            
            self.daydreamer_ai = DaydreamerAI(
                memory_db_path="src/memory/daydreamer_memory.db",
                model_config=model_config
            )
            
            logger.info("Daydreamer AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Daydreamer AI: {e}")
            self.daydreamer_ai = None
    
    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a message with the daydreamer AI"""
        start_time = datetime.now()
        
        # Create or get conversation
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            await self._create_conversation(conversation_id, message[:100])
        
        # Save user message
        await self._save_message(conversation_id, "user", message)
        
        # Process with daydreamer AI
        if self.daydreamer_ai and DAYDREAMER_AVAILABLE:
            try:
                response = await self.daydreamer_ai.process_user_input(message)
                thinking_time = 0.5  # Mock values for now
                daydream_time = 0.3
            except Exception as e:
                logger.error(f"Error processing with daydreamer: {e}")
                response = f"I apologize, but I encountered an error: {str(e)}"
                thinking_time = 0.0
                daydream_time = 0.0
        else:
            # Mock response when daydreamer is not available
            response = f"Mock response to: {message}"
            thinking_time = 0.1
            daydream_time = 0.1
        
        # Save AI response
        await self._save_message(
            conversation_id, 
            "assistant", 
            response, 
            thinking_time, 
            daydream_time
        )
        
        # Update conversation stats
        await self._update_conversation_stats(conversation_id)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        return {
            "response": response,
            "conversation_id": conversation_id,
            "thinking_time": thinking_time,
            "daydream_time": daydream_time,
            "total_time": total_time
        }
    
    async def _create_conversation(self, conversation_id: str, title: str):
        """Create a new conversation"""
        async with AsyncSessionLocal() as session:
            conversation = Conversation(
                id=conversation_id,
                title=title,
                tags=[]
            )
            session.add(conversation)
            await session.commit()
    
    async def _save_message(self, conversation_id: str, role: str, content: str, 
                          thinking_time: float = 0.0, daydream_time: float = 0.0):
        """Save a message to the database"""
        async with AsyncSessionLocal() as session:
            message = ChatMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                thinking_time=thinking_time,
                daydream_time=daydream_time,
                tokens_used=len(content.split())  # Simple token estimation
            )
            session.add(message)
            await session.commit()
    
    async def _update_conversation_stats(self, conversation_id: str):
        """Update conversation statistics"""
        async with AsyncSessionLocal() as session:
            # Get conversation with messages
            stmt = select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
            result = await session.execute(stmt)
            conversation = result.scalar_one()
            
            # Calculate stats
            conversation.message_count = len(conversation.messages)
            conversation.total_thinking_time = sum(msg.thinking_time for msg in conversation.messages)
            conversation.total_daydream_time = sum(msg.daydream_time for msg in conversation.messages)
            conversation.updated_at = datetime.now()
            
            await session.commit()
    
    async def get_conversations(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        async with AsyncSessionLocal() as session:
            stmt = select(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit)
            result = await session.execute(stmt)
            conversations = result.scalars().all()
            
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at,
                    "updated_at": conv.updated_at,
                    "message_count": conv.message_count,
                    "total_thinking_time": conv.total_thinking_time,
                    "total_daydream_time": conv.total_daydream_time,
                    "tags": conv.tags
                }
                for conv in conversations
            ]
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation with messages"""
        async with AsyncSessionLocal() as session:
            stmt = select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
            result = await session.execute(stmt)
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return None
            
            return {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "message_count": conversation.message_count,
                "total_thinking_time": conversation.total_thinking_time,
                "total_daydream_time": conversation.total_daydream_time,
                "tags": conversation.tags,
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "thinking_time": msg.thinking_time,
                        "daydream_time": msg.daydream_time,
                        "tokens_used": msg.tokens_used
                    }
                    for msg in conversation.messages
                ]
            }
    
    async def delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        async with AsyncSessionLocal() as session:
            stmt = delete(Conversation).where(Conversation.id == conversation_id)
            await session.execute(stmt)
            await session.commit()
    
    async def clear_conversations(self):
        """Clear all conversations"""
        async with AsyncSessionLocal() as session:
            stmt = delete(Conversation)
            await session.execute(stmt)
            await session.commit()
    
    async def get_settings(self) -> Dict[str, Any]:
        """Get current user settings"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserSettings).order_by(UserSettings.id.desc()).limit(1)
            result = await session.execute(stmt)
            settings = result.scalar_one_or_none()
            
            if not settings:
                # Create default settings
                settings = UserSettings()
                session.add(settings)
                await session.commit()
            
            return {
                "id": settings.id,
                "theme": settings.theme,
                "language": settings.language,
                "auto_save": settings.auto_save,
                "notifications_enabled": settings.notifications_enabled,
                "max_conversation_history": settings.max_conversation_history,
                "created_at": settings.created_at,
                "updated_at": settings.updated_at
            }
    
    async def update_settings(self, settings_update: SettingsUpdate) -> Dict[str, Any]:
        """Update user settings"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserSettings).order_by(UserSettings.id.desc()).limit(1)
            result = await session.execute(stmt)
            settings = result.scalar_one_or_none()
            
            if not settings:
                settings = UserSettings()
                session.add(settings)
            
            # Update fields
            update_data = settings_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(settings, field, value)
            
            settings.updated_at = datetime.now()
            await session.commit()
            
            return {
                "id": settings.id,
                "theme": settings.theme,
                "language": settings.language,
                "auto_save": settings.auto_save,
                "notifications_enabled": settings.notifications_enabled,
                "max_conversation_history": settings.max_conversation_history,
                "created_at": settings.created_at,
                "updated_at": settings.updated_at
            }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available AI models"""
        if self.daydreamer_ai and DAYDREAMER_AVAILABLE:
            try:
                model_info = self.daydreamer_ai.model_manager.get_model_info()
                return [
                    {
                        "name": model_info.get('active_model', 'Unknown'),
                        "available": True,
                        "ollama_available": model_info.get('ollama_available', False),
                        "transformers_available": model_info.get('transformers_available', False)
                    }
                ]
            except Exception as e:
                logger.error(f"Error getting model info: {e}")
        
        # Return mock data
        return [
            {
                "name": "llama3.2:3b",
                "available": True,
                "ollama_available": True,
                "transformers_available": False
            }
        ]
    
    async def update_model_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update AI model configuration"""
        async with AsyncSessionLocal() as session:
            # Deactivate all current configs
            stmt = update(AIModelConfig).values(is_active=False)
            await session.execute(stmt)
            
            # Create new config
            model_config = AIModelConfig(
                model_name=config['model_name'],
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 2048),
                top_p=config.get('top_p', 0.9),
                verbose=config.get('verbose', False),
                is_active=True
            )
            session.add(model_config)
            await session.commit()
            
            # Update daydreamer AI if available
            if self.daydreamer_ai and DAYDREAMER_AVAILABLE:
                try:
                    # This would need to be implemented in the daydreamer AI
                    logger.info(f"Updated model config: {config}")
                except Exception as e:
                    logger.error(f"Error updating daydreamer config: {e}")
            
            return {
                "id": model_config.id,
                "model_name": model_config.model_name,
                "temperature": model_config.temperature,
                "max_tokens": model_config.max_tokens,
                "top_p": model_config.top_p,
                "verbose": model_config.verbose,
                "is_active": model_config.is_active,
                "created_at": model_config.created_at,
                "updated_at": model_config.updated_at
            }
    
    async def restart_model(self):
        """Restart the AI model"""
        if self.daydreamer_ai and DAYDREAMER_AVAILABLE:
            try:
                # Reinitialize the daydreamer AI
                self._initialize_daydreamer()
                logger.info("Model restarted successfully")
            except Exception as e:
                logger.error(f"Error restarting model: {e}")
                raise
        else:
            logger.info("Mock model restart - no actual model to restart")
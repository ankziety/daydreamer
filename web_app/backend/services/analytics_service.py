#!/usr/bin/env python3
"""
Analytics Service
================

Service for generating analytics and insights from conversation and performance data.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models import (
    Conversation, ChatMessage, SystemMetrics,
    AnalyticsOverview, ConversationAnalytics, PerformanceAnalytics
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for generating analytics and insights"""
    
    def __init__(self):
        """Initialize the analytics service"""
        self.start_time = datetime.now()
    
    async def get_overview(self) -> Dict[str, Any]:
        """Get analytics overview"""
        async with AsyncSessionLocal() as session:
            # Get total conversations
            stmt = select(func.count(Conversation.id))
            result = await session.execute(stmt)
            total_conversations = result.scalar() or 0
            
            # Get total messages
            stmt = select(func.count(ChatMessage.id))
            result = await session.execute(stmt)
            total_messages = result.scalar() or 0
            
            # Get average response time (from thinking + daydream time)
            stmt = select(
                func.avg(ChatMessage.thinking_time + ChatMessage.daydream_time)
            ).where(ChatMessage.role == "assistant")
            result = await session.execute(stmt)
            avg_response_time = result.scalar() or 0.0
            
            # Get total thinking and daydream time
            stmt = select(
                func.sum(ChatMessage.thinking_time),
                func.sum(ChatMessage.daydream_time)
            ).where(ChatMessage.role == "assistant")
            result = await session.execute(stmt)
            total_thinking, total_daydream = result.first() or (0.0, 0.0)
            
            # Get today's stats
            today = datetime.now().date()
            stmt = select(func.count(Conversation.id)).where(
                func.date(Conversation.created_at) == today
            )
            result = await session.execute(stmt)
            conversations_today = result.scalar() or 0
            
            stmt = select(func.count(ChatMessage.id)).where(
                func.date(ChatMessage.timestamp) == today
            )
            result = await session.execute(stmt)
            messages_today = result.scalar() or 0
            
            # Calculate uptime
            uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "average_response_time": round(avg_response_time, 2),
                "total_thinking_time": round(total_thinking or 0.0, 2),
                "total_daydream_time": round(total_daydream or 0.0, 2),
                "active_conversations_today": conversations_today,
                "messages_today": messages_today,
                "system_uptime_hours": round(uptime_hours, 2)
            }
    
    async def get_conversation_analytics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get conversation analytics over time"""
        async with AsyncSessionLocal() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get daily conversation counts
            stmt = select(
                func.date(Conversation.created_at).label('date'),
                func.count(Conversation.id).label('conversations'),
                func.count(ChatMessage.id).label('messages'),
                func.avg(ChatMessage.thinking_time).label('avg_thinking'),
                func.avg(ChatMessage.daydream_time).label('avg_daydream')
            ).outerjoin(ChatMessage).where(
                Conversation.created_at >= start_date
            ).group_by(func.date(Conversation.created_at)).order_by(
                func.date(Conversation.created_at)
            )
            
            result = await session.execute(stmt)
            rows = result.all()
            
            analytics = []
            for row in rows:
                analytics.append({
                    "date": row.date.strftime('%Y-%m-%d'),
                    "conversations": row.conversations,
                    "messages": row.messages,
                    "average_thinking_time": round(row.avg_thinking or 0.0, 2),
                    "average_daydream_time": round(row.avg_daydream or 0.0, 2)
                })
            
            return analytics
    
    async def get_performance_analytics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get performance analytics over time"""
        async with AsyncSessionLocal() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get daily performance metrics
            stmt = select(
                func.date(ChatMessage.timestamp).label('date'),
                func.avg(ChatMessage.thinking_time + ChatMessage.daydream_time).label('avg_response_time'),
                func.count(ChatMessage.id).label('total_requests')
            ).where(
                ChatMessage.timestamp >= start_date,
                ChatMessage.role == "assistant"
            ).group_by(func.date(ChatMessage.timestamp)).order_by(
                func.date(ChatMessage.timestamp)
            )
            
            result = await session.execute(stmt)
            rows = result.all()
            
            # Get system metrics for the same period
            stmt = select(
                func.date(SystemMetrics.timestamp).label('date'),
                func.avg(SystemMetrics.cpu_usage).label('avg_cpu'),
                func.avg(SystemMetrics.memory_usage).label('avg_memory')
            ).where(
                SystemMetrics.timestamp >= start_date
            ).group_by(func.date(SystemMetrics.timestamp))
            
            result = await session.execute(stmt)
            metrics_rows = result.all()
            
            # Create metrics lookup
            metrics_lookup = {row.date: row for row in metrics_rows}
            
            analytics = []
            for row in rows:
                metrics = metrics_lookup.get(row.date)
                analytics.append({
                    "date": row.date.strftime('%Y-%m-%d'),
                    "average_response_time": round(row.avg_response_time or 0.0, 2),
                    "total_requests": row.total_requests,
                    "cpu_usage": round(metrics.avg_cpu or 0.0, 2) if metrics else 0.0,
                    "memory_usage": round(metrics.avg_memory or 0.0, 2) if metrics else 0.0
                })
            
            return analytics
    
    async def get_user_engagement_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get user engagement metrics"""
        async with AsyncSessionLocal() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get conversation length distribution
            stmt = select(
                Conversation.message_count,
                func.count(Conversation.id).label('count')
            ).where(
                Conversation.created_at >= start_date
            ).group_by(Conversation.message_count).order_by(Conversation.message_count)
            
            result = await session.execute(stmt)
            length_distribution = {row.message_count: row.count for row in result.all()}
            
            # Get average conversation length
            stmt = select(func.avg(Conversation.message_count))
            result = await session.execute(stmt)
            avg_conversation_length = result.scalar() or 0.0
            
            # Get most active hours
            stmt = select(
                func.extract('hour', ChatMessage.timestamp).label('hour'),
                func.count(ChatMessage.id).label('count')
            ).where(
                ChatMessage.timestamp >= start_date
            ).group_by(func.extract('hour', ChatMessage.timestamp)).order_by(
                func.count(ChatMessage.id).desc()
            ).limit(5)
            
            result = await session.execute(stmt)
            active_hours = [{"hour": int(row.hour), "count": row.count} for row in result.all()]
            
            return {
                "conversation_length_distribution": length_distribution,
                "average_conversation_length": round(avg_conversation_length, 2),
                "most_active_hours": active_hours
            }
    
    async def get_model_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get AI model performance metrics"""
        async with AsyncSessionLocal() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get thinking vs daydream time analysis
            stmt = select(
                func.avg(ChatMessage.thinking_time).label('avg_thinking'),
                func.avg(ChatMessage.daydream_time).label('avg_daydream'),
                func.sum(ChatMessage.thinking_time).label('total_thinking'),
                func.sum(ChatMessage.daydream_time).label('total_daydream'),
                func.count(ChatMessage.id).label('total_responses')
            ).where(
                ChatMessage.timestamp >= start_date,
                ChatMessage.role == "assistant"
            )
            
            result = await session.execute(stmt)
            row = result.first()
            
            if row:
                return {
                    "average_thinking_time": round(row.avg_thinking or 0.0, 2),
                    "average_daydream_time": round(row.avg_daydream or 0.0, 2),
                    "total_thinking_time": round(row.total_thinking or 0.0, 2),
                    "total_daydream_time": round(row.total_daydream or 0.0, 2),
                    "total_responses": row.total_responses,
                    "thinking_daydream_ratio": round(
                        (row.avg_thinking or 0.0) / (row.avg_daydream or 1.0), 2
                    )
                }
            
            return {
                "average_thinking_time": 0.0,
                "average_daydream_time": 0.0,
                "total_thinking_time": 0.0,
                "total_daydream_time": 0.0,
                "total_responses": 0,
                "thinking_daydream_ratio": 0.0
            }
    
    async def get_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get trend analysis for key metrics"""
        async with AsyncSessionLocal() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get daily trends
            stmt = select(
                func.date(ChatMessage.timestamp).label('date'),
                func.count(ChatMessage.id).label('messages'),
                func.avg(ChatMessage.thinking_time + ChatMessage.daydream_time).label('response_time')
            ).where(
                ChatMessage.timestamp >= start_date,
                ChatMessage.role == "assistant"
            ).group_by(func.date(ChatMessage.timestamp)).order_by(
                func.date(ChatMessage.timestamp)
            )
            
            result = await session.execute(stmt)
            rows = result.all()
            
            if len(rows) < 2:
                return {"trend": "insufficient_data", "growth_rate": 0.0}
            
            # Calculate growth rate
            first_day = rows[0].messages
            last_day = rows[-1].messages
            
            if first_day > 0:
                growth_rate = ((last_day - first_day) / first_day) * 100
            else:
                growth_rate = 0.0
            
            # Determine trend
            if growth_rate > 5:
                trend = "increasing"
            elif growth_rate < -5:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "growth_rate": round(growth_rate, 2),
                "daily_data": [
                    {
                        "date": row.date.strftime('%Y-%m-%d'),
                        "messages": row.messages,
                        "response_time": round(row.response_time or 0.0, 2)
                    }
                    for row in rows
                ]
            }
#!/usr/bin/env python3
"""
Metrics Service
==============

Service for monitoring system performance and collecting real-time metrics.
"""

import asyncio
import logging
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models import SystemMetrics

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for collecting and managing system metrics"""
    
    def __init__(self):
        """Initialize the metrics service"""
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        self.monitoring_interval = 60  # seconds
    
    async def start_monitoring(self):
        """Start the monitoring task"""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("System metrics monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring task"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("System metrics monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self):
        """Collect current system metrics"""
        try:
            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get application-specific metrics
            active_conversations = await self._get_active_conversations()
            total_requests = await self._get_total_requests()
            average_response_time = await self._get_average_response_time()
            model_status = await self._get_model_status()
            
            # Save metrics to database
            await self._save_metrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_conversations=active_conversations,
                total_requests=total_requests,
                average_response_time=average_response_time,
                model_status=model_status
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    async def _get_active_conversations(self) -> int:
        """Get number of active conversations (last 24 hours)"""
        async with AsyncSessionLocal() as session:
            yesterday = datetime.now() - timedelta(hours=24)
            stmt = select(func.count()).select_from(SystemMetrics).where(
                SystemMetrics.timestamp >= yesterday
            )
            result = await session.execute(stmt)
            return result.scalar() or 0
    
    async def _get_total_requests(self) -> int:
        """Get total number of requests"""
        async with AsyncSessionLocal() as session:
            stmt = select(func.count()).select_from(SystemMetrics)
            result = await session.execute(stmt)
            return result.scalar() or 0
    
    async def _get_average_response_time(self) -> float:
        """Get average response time from recent metrics"""
        async with AsyncSessionLocal() as session:
            yesterday = datetime.now() - timedelta(hours=24)
            stmt = select(func.avg(SystemMetrics.average_response_time)).where(
                SystemMetrics.timestamp >= yesterday
            )
            result = await session.execute(stmt)
            return result.scalar() or 0.0
    
    async def _get_model_status(self) -> str:
        """Get current model status"""
        # This would integrate with the actual daydreamer model
        # For now, return a mock status
        return "active"
    
    async def _save_metrics(self, **metrics):
        """Save metrics to database"""
        async with AsyncSessionLocal() as session:
            system_metrics = SystemMetrics(
                timestamp=datetime.now(),
                **metrics
            )
            session.add(system_metrics)
            await session.commit()
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # Get real-time system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process-specific metrics
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Get network metrics
            network = psutil.net_io_counters()
            
            # Get latest database metrics
            async with AsyncSessionLocal() as session:
                stmt = select(SystemMetrics).order_by(SystemMetrics.timestamp.desc()).limit(1)
                result = await session.execute(stmt)
                latest_metrics = result.scalar_one_or_none()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage": round(cpu_usage, 2),
                    "memory_usage": round(memory.percent, 2),
                    "memory_available": round(memory.available / 1024 / 1024 / 1024, 2),  # GB
                    "disk_usage": round(disk.percent, 2),
                    "disk_free": round(disk.free / 1024 / 1024 / 1024, 2),  # GB
                },
                "application": {
                    "process_memory_mb": round(process_memory, 2),
                    "process_cpu_percent": round(process.cpu_percent(), 2),
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv,
                },
                "database": {
                    "active_conversations": latest_metrics.active_conversations if latest_metrics else 0,
                    "total_requests": latest_metrics.total_requests if latest_metrics else 0,
                    "average_response_time": round(latest_metrics.average_response_time, 2) if latest_metrics else 0.0,
                    "model_status": latest_metrics.model_status if latest_metrics else "unknown"
                }
            }
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified number of hours"""
        async with AsyncSessionLocal() as session:
            start_time = datetime.now() - timedelta(hours=hours)
            
            stmt = select(SystemMetrics).where(
                SystemMetrics.timestamp >= start_time
            ).order_by(SystemMetrics.timestamp)
            
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            
            return [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "disk_usage": metric.disk_usage,
                    "active_conversations": metric.active_conversations,
                    "total_requests": metric.total_requests,
                    "average_response_time": metric.average_response_time,
                    "model_status": metric.model_status
                }
                for metric in metrics
            ]
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health assessment"""
        try:
            current_metrics = await self.get_current_metrics()
            
            # Define health thresholds
            cpu_threshold = 80.0
            memory_threshold = 85.0
            disk_threshold = 90.0
            
            # Assess health
            cpu_healthy = current_metrics["system"]["cpu_usage"] < cpu_threshold
            memory_healthy = current_metrics["system"]["memory_usage"] < memory_threshold
            disk_healthy = current_metrics["system"]["disk_usage"] < disk_threshold
            
            # Calculate overall health score
            health_score = 100
            if not cpu_healthy:
                health_score -= 30
            if not memory_healthy:
                health_score -= 30
            if not disk_healthy:
                health_score -= 40
            
            # Determine status
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "status": status,
                "health_score": health_score,
                "checks": {
                    "cpu": {
                        "healthy": cpu_healthy,
                        "value": current_metrics["system"]["cpu_usage"],
                        "threshold": cpu_threshold
                    },
                    "memory": {
                        "healthy": memory_healthy,
                        "value": current_metrics["system"]["memory_usage"],
                        "threshold": memory_threshold
                    },
                    "disk": {
                        "healthy": disk_healthy,
                        "value": current_metrics["system"]["disk_usage"],
                        "threshold": disk_threshold
                    }
                },
                "timestamp": current_metrics["timestamp"]
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "unknown",
                "health_score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the specified period"""
        async with AsyncSessionLocal() as session:
            start_time = datetime.now() - timedelta(hours=hours)
            
            # Get aggregated metrics
            stmt = select(
                func.avg(SystemMetrics.cpu_usage).label('avg_cpu'),
                func.max(SystemMetrics.cpu_usage).label('max_cpu'),
                func.avg(SystemMetrics.memory_usage).label('avg_memory'),
                func.max(SystemMetrics.memory_usage).label('max_memory'),
                func.avg(SystemMetrics.average_response_time).label('avg_response_time'),
                func.max(SystemMetrics.average_response_time).label('max_response_time'),
                func.sum(SystemMetrics.total_requests).label('total_requests')
            ).where(SystemMetrics.timestamp >= start_time)
            
            result = await session.execute(stmt)
            row = result.first()
            
            if row:
                return {
                    "period_hours": hours,
                    "cpu": {
                        "average": round(row.avg_cpu or 0.0, 2),
                        "maximum": round(row.max_cpu or 0.0, 2)
                    },
                    "memory": {
                        "average": round(row.avg_memory or 0.0, 2),
                        "maximum": round(row.max_memory or 0.0, 2)
                    },
                    "response_time": {
                        "average": round(row.avg_response_time or 0.0, 2),
                        "maximum": round(row.max_response_time or 0.0, 2)
                    },
                    "requests": {
                        "total": row.total_requests or 0
                    }
                }
            
            return {
                "period_hours": hours,
                "cpu": {"average": 0.0, "maximum": 0.0},
                "memory": {"average": 0.0, "maximum": 0.0},
                "response_time": {"average": 0.0, "maximum": 0.0},
                "requests": {"total": 0}
            }
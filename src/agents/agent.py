"""
Core Agent class for Daydreamer Project
This module provides the foundational Agent class that serves as the base for all AI agents.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class AgentConfig:
    """Configuration for agents"""
    agent_id: str
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    log_level: str = "INFO"
    max_memory_usage: int = 1000
    cleanup_interval: float = 60.0  # seconds


@dataclass
class AgentEvent:
    """Event structure for agent communication"""
    event_id: str
    event_type: str
    source_agent_id: str
    target_agent_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10 scale


class Agent(ABC):
    """
    Base Agent class that provides core functionality for all AI agents.
    
    This class implements:
    - Basic lifecycle management (initialize, start, pause, stop, cleanup)
    - State management (idle, active, paused, stopped)
    - Event handling system for agent communication
    - Configuration management for agent parameters
    - Logging and monitoring capabilities
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with configuration.
        
        Args:
            config: Agent configuration parameters
        """
        self.config = config
        self.state = AgentState.IDLE
        self.start_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.stats = {
            "events_processed": 0,
            "events_sent": 0,
            "errors": 0,
            "uptime_seconds": 0
        }
        
        # Setup logging
        self._setup_logging()
        
        # Initialize the agent
        self._initialize()
        
        logger.info(f"🤖 Created agent: {config.agent_id} ({config.name})")
    
    def _setup_logging(self):
        """Setup agent-specific logging"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    def _initialize(self):
        """Initialize agent-specific resources"""
        self._register_default_event_handlers()
        logger.debug(f"Agent {self.config.agent_id} initialized")
    
    def _register_default_event_handlers(self):
        """Register default event handlers"""
        self.register_event_handler("ping", self._handle_ping)
        self.register_event_handler("status", self._handle_status_request)
        self.register_event_handler("shutdown", self._handle_shutdown)
    
    async def start(self) -> bool:
        """
        Start the agent and begin operation.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.state != AgentState.IDLE:
            logger.warning(f"Agent {self.config.agent_id} is already active (state: {self.state})")
            return False
        
        try:
            self.state = AgentState.ACTIVE
            self.start_time = datetime.now()
            self.last_activity = datetime.now()
            
            # Call the abstract method for agent-specific startup
            await self._on_start()
            
            logger.info(f"🚀 Started agent: {self.config.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.config.agent_id}: {e}")
            self.state = AgentState.IDLE
            return False
    
    async def stop(self) -> bool:
        """
        Stop the agent and clean up resources.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if self.state == AgentState.STOPPED:
            return True
        
        try:
            self.state = AgentState.STOPPED
            
            # Call the abstract method for agent-specific cleanup
            await self._on_stop()
            
            # Update uptime
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
                self.stats["uptime_seconds"] = uptime
            
            logger.info(f"🛑 Stopped agent: {self.config.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping agent {self.config.agent_id}: {e}")
            return False
    
    async def pause(self) -> bool:
        """
        Pause the agent operation.
        
        Returns:
            True if paused successfully, False otherwise
        """
        if self.state == AgentState.ACTIVE:
            self.state = AgentState.PAUSED
            await self._on_pause()
            logger.info(f"⏸️ Paused agent: {self.config.agent_id}")
            return True
        else:
            logger.warning(f"Cannot pause agent {self.config.agent_id} in state {self.state}")
            return False
    
    async def resume(self) -> bool:
        """
        Resume the agent operation.
        
        Returns:
            True if resumed successfully, False otherwise
        """
        if self.state == AgentState.PAUSED:
            self.state = AgentState.ACTIVE
            await self._on_resume()
            logger.info(f"▶️ Resumed agent: {self.config.agent_id}")
            return True
        else:
            logger.warning(f"Cannot resume agent {self.config.agent_id} in state {self.state}")
            return False
    
    async def cleanup(self):
        """Clean up agent resources"""
        try:
            await self._on_cleanup()
            logger.debug(f"Cleaned up agent: {self.config.agent_id}")
        except Exception as e:
            logger.error(f"Error during cleanup for agent {self.config.agent_id}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered event handler for {event_type} in agent {self.config.agent_id}")
    
    async def handle_event(self, event: AgentEvent) -> bool:
        """
        Handle an incoming event.
        
        Args:
            event: Event to handle
            
        Returns:
            True if event was handled successfully, False otherwise
        """
        if not self.config.enabled or self.state == AgentState.STOPPED:
            return False
        
        try:
            # Find handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            
            if not handlers:
                logger.debug(f"No handlers for event type {event.event_type} in agent {self.config.agent_id}")
                return False
            
            # Update activity and counter only if we have handlers
            self.last_activity = datetime.now()
            self.stats["events_processed"] += 1
            
            # Call all registered handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__} for agent {self.config.agent_id}: {e}")
                    self.stats["errors"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling event in agent {self.config.agent_id}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def send_event(self, event: AgentEvent) -> bool:
        """
        Send an event to another agent or broadcast.
        
        Args:
            event: Event to send
            
        Returns:
            True if event was sent successfully, False otherwise
        """
        try:
            self.stats["events_sent"] += 1
            # This would typically send to an event bus or message queue
            # For now, we'll just log it
            logger.debug(f"Agent {self.config.agent_id} sent event {event.event_type} to {event.target_agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending event from agent {self.config.agent_id}: {e}")
            self.stats["errors"] += 1
            return False
    
    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        stats = self.stats.copy()
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
            stats["uptime_seconds"] = uptime
        stats["state"] = self.state.value
        stats["enabled"] = self.config.enabled
        return stats
    
    def get_config(self) -> AgentConfig:
        """Get agent configuration"""
        return self.config
    
    # Default event handlers
    async def _handle_ping(self, event: AgentEvent):
        """Handle ping events"""
        response = AgentEvent(
            event_id=f"pong_{event.event_id}",
            event_type="pong",
            source_agent_id=self.config.agent_id,
            target_agent_id=event.source_agent_id,
            data={"timestamp": datetime.now().isoformat()}
        )
        await self.send_event(response)
    
    async def _handle_status_request(self, event: AgentEvent):
        """Handle status request events"""
        response = AgentEvent(
            event_id=f"status_response_{event.event_id}",
            event_type="status_response",
            source_agent_id=self.config.agent_id,
            target_agent_id=event.source_agent_id,
            data={
                "state": self.state.value,
                "stats": self.get_stats(),
                "config": {
                    "agent_id": self.config.agent_id,
                    "name": self.config.name,
                    "enabled": self.config.enabled
                }
            }
        )
        await self.send_event(response)
    
    async def _handle_shutdown(self, event: AgentEvent):
        """Handle shutdown events"""
        logger.info(f"Agent {self.config.agent_id} received shutdown request")
        await self.stop()
    
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    async def _on_start(self):
        """Called when the agent starts. Override for agent-specific startup logic."""
        pass
    
    @abstractmethod
    async def _on_stop(self):
        """Called when the agent stops. Override for agent-specific cleanup logic."""
        pass
    
    @abstractmethod
    async def _on_pause(self):
        """Called when the agent is paused. Override for agent-specific pause logic."""
        pass
    
    @abstractmethod
    async def _on_resume(self):
        """Called when the agent resumes. Override for agent-specific resume logic."""
        pass
    
    @abstractmethod
    async def _on_cleanup(self):
        """Called during cleanup. Override for agent-specific cleanup logic."""
        pass
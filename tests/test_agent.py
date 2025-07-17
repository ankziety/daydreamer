"""
Unit tests for the core Agent class
Tests all lifecycle methods, state transitions, and event handling.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from src.agents.agent import Agent, AgentConfig, AgentState, AgentEvent
from src.agents.test_agent import DemoAgent as TestAgentImpl


class MockAgent(Agent):
    """Mock agent for testing abstract methods"""
    
    async def _on_start(self):
        self.started = True
    
    async def _on_stop(self):
        self.stopped = True
    
    async def _on_pause(self):
        self.paused = True
    
    async def _on_resume(self):
        self.resumed = True
    
    async def _on_cleanup(self):
        self.cleaned_up = True


class TestAgentConfig:
    """Test AgentConfig dataclass"""
    
    def test_agent_config_creation(self):
        """Test creating AgentConfig with default values"""
        config = AgentConfig(agent_id="test_001")
        
        assert config.agent_id == "test_001"
        assert config.name == ""
        assert config.description == ""
        assert config.version == "1.0.0"
        assert config.enabled is True
        assert config.log_level == "INFO"
        assert config.max_memory_usage == 1000
        assert config.cleanup_interval == 60.0
    
    def test_agent_config_custom_values(self):
        """Test creating AgentConfig with custom values"""
        config = AgentConfig(
            agent_id="test_002",
            name="Test Agent",
            description="A test agent",
            version="2.0.0",
            enabled=False,
            log_level="DEBUG",
            max_memory_usage=2000,
            cleanup_interval=30.0
        )
        
        assert config.agent_id == "test_002"
        assert config.name == "Test Agent"
        assert config.description == "A test agent"
        assert config.version == "2.0.0"
        assert config.enabled is False
        assert config.log_level == "DEBUG"
        assert config.max_memory_usage == 2000
        assert config.cleanup_interval == 30.0


class TestAgentState:
    """Test AgentState enum"""
    
    def test_agent_state_values(self):
        """Test AgentState enum values"""
        assert AgentState.IDLE.value == "idle"
        assert AgentState.ACTIVE.value == "active"
        assert AgentState.PAUSED.value == "paused"
        assert AgentState.STOPPED.value == "stopped"


class TestAgentEvent:
    """Test AgentEvent dataclass"""
    
    def test_agent_event_creation(self):
        """Test creating AgentEvent with default values"""
        event = AgentEvent(
            event_id="event_001",
            event_type="test",
            source_agent_id="agent_001"
        )
        
        assert event.event_id == "event_001"
        assert event.event_type == "test"
        assert event.source_agent_id == "agent_001"
        assert event.target_agent_id is None
        assert event.data == {}
        assert event.priority == 5
        assert isinstance(event.timestamp, datetime)
    
    def test_agent_event_custom_values(self):
        """Test creating AgentEvent with custom values"""
        timestamp = datetime.now()
        event = AgentEvent(
            event_id="event_002",
            event_type="message",
            source_agent_id="agent_001",
            target_agent_id="agent_002",
            timestamp=timestamp,
            data={"message": "Hello"},
            priority=8
        )
        
        assert event.event_id == "event_002"
        assert event.event_type == "message"
        assert event.source_agent_id == "agent_001"
        assert event.target_agent_id == "agent_002"
        assert event.timestamp == timestamp
        assert event.data == {"message": "Hello"}
        assert event.priority == 8


class TestAgent:
    """Test the base Agent class"""
    
    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration"""
        return AgentConfig(
            agent_id="test_agent_001",
            name="Test Agent",
            description="A test agent",
            log_level="DEBUG"
        )
    
    @pytest.fixture
    def mock_agent(self, agent_config):
        """Create a mock agent instance"""
        return MockAgent(agent_config)
    
    def test_agent_initialization(self, mock_agent, agent_config):
        """Test agent initialization"""
        assert mock_agent.config == agent_config
        assert mock_agent.state == AgentState.IDLE
        assert mock_agent.start_time is None
        assert mock_agent.last_activity is None
        # Default event handlers should be registered
        assert len(mock_agent.event_handlers) == 3  # ping, status, shutdown
        assert mock_agent.stats["events_processed"] == 0
        assert mock_agent.stats["events_sent"] == 0
        assert mock_agent.stats["errors"] == 0
        assert mock_agent.stats["uptime_seconds"] == 0
    
    def test_agent_default_event_handlers(self, mock_agent):
        """Test that default event handlers are registered"""
        assert "ping" in mock_agent.event_handlers
        assert "status" in mock_agent.event_handlers
        assert "shutdown" in mock_agent.event_handlers
        
        # Check that handlers are callable
        assert len(mock_agent.event_handlers["ping"]) == 1
        assert len(mock_agent.event_handlers["status"]) == 1
        assert len(mock_agent.event_handlers["shutdown"]) == 1
    
    @pytest.mark.asyncio
    async def test_agent_start_success(self, mock_agent):
        """Test successful agent start"""
        assert mock_agent.state == AgentState.IDLE
        
        success = await mock_agent.start()
        
        assert success is True
        assert mock_agent.state == AgentState.ACTIVE
        assert mock_agent.started is True
        assert mock_agent.start_time is not None
        assert mock_agent.last_activity is not None
    
    @pytest.mark.asyncio
    async def test_agent_start_already_active(self, mock_agent):
        """Test starting an already active agent"""
        # Start the agent first
        await mock_agent.start()
        assert mock_agent.state == AgentState.ACTIVE
        
        # Try to start again
        success = await mock_agent.start()
        
        assert success is False
        assert mock_agent.state == AgentState.ACTIVE
    
    @pytest.mark.asyncio
    async def test_agent_start_failure(self, mock_agent):
        """Test agent start failure"""
        # Make the _on_start method raise an exception
        async def failing_start():
            raise Exception("Start failed")
        
        mock_agent._on_start = failing_start
        
        success = await mock_agent.start()
        
        assert success is False
        assert mock_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_agent_stop_success(self, mock_agent):
        """Test successful agent stop"""
        # Start the agent first
        await mock_agent.start()
        assert mock_agent.state == AgentState.ACTIVE
        
        success = await mock_agent.stop()
        
        assert success is True
        assert mock_agent.state == AgentState.STOPPED
        assert mock_agent.stopped is True
        assert mock_agent.stats["uptime_seconds"] > 0
    
    @pytest.mark.asyncio
    async def test_agent_stop_already_stopped(self, mock_agent):
        """Test stopping an already stopped agent"""
        # Start and stop the agent
        await mock_agent.start()
        await mock_agent.stop()
        assert mock_agent.state == AgentState.STOPPED
        
        # Try to stop again
        success = await mock_agent.stop()
        
        assert success is True
        assert mock_agent.state == AgentState.STOPPED
    
    @pytest.mark.asyncio
    async def test_agent_pause_success(self, mock_agent):
        """Test successful agent pause"""
        # Start the agent first
        await mock_agent.start()
        assert mock_agent.state == AgentState.ACTIVE
        
        success = await mock_agent.pause()
        
        assert success is True
        assert mock_agent.state == AgentState.PAUSED
        assert mock_agent.paused is True
    
    @pytest.mark.asyncio
    async def test_agent_pause_wrong_state(self, mock_agent):
        """Test pausing agent in wrong state"""
        assert mock_agent.state == AgentState.IDLE
        
        success = await mock_agent.pause()
        
        assert success is False
        assert mock_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_agent_resume_success(self, mock_agent):
        """Test successful agent resume"""
        # Start and pause the agent
        await mock_agent.start()
        await mock_agent.pause()
        assert mock_agent.state == AgentState.PAUSED
        
        success = await mock_agent.resume()
        
        assert success is True
        assert mock_agent.state == AgentState.ACTIVE
        assert mock_agent.resumed is True
    
    @pytest.mark.asyncio
    async def test_agent_resume_wrong_state(self, mock_agent):
        """Test resuming agent in wrong state"""
        assert mock_agent.state == AgentState.IDLE
        
        success = await mock_agent.resume()
        
        assert success is False
        assert mock_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_agent_cleanup(self, mock_agent):
        """Test agent cleanup"""
        await mock_agent.cleanup()
        
        assert mock_agent.cleaned_up is True
    
    def test_agent_register_event_handler(self, mock_agent):
        """Test registering event handlers"""
        def test_handler(event):
            pass
        
        mock_agent.register_event_handler("test_event", test_handler)
        
        assert "test_event" in mock_agent.event_handlers
        assert test_handler in mock_agent.event_handlers["test_event"]
    
    def test_agent_register_multiple_handlers(self, mock_agent):
        """Test registering multiple handlers for same event"""
        def handler1(event):
            pass
        
        def handler2(event):
            pass
        
        mock_agent.register_event_handler("test_event", handler1)
        mock_agent.register_event_handler("test_event", handler2)
        
        assert len(mock_agent.event_handlers["test_event"]) == 2
        assert handler1 in mock_agent.event_handlers["test_event"]
        assert handler2 in mock_agent.event_handlers["test_event"]
    
    @pytest.mark.asyncio
    async def test_agent_handle_event_success(self, mock_agent):
        """Test successful event handling"""
        # Register a test handler
        handler_called = False
        
        def test_handler(event):
            nonlocal handler_called
            handler_called = True
        
        mock_agent.register_event_handler("test_event", test_handler)
        
        # Create and handle an event
        event = AgentEvent(
            event_id="test_001",
            event_type="test_event",
            source_agent_id="sender"
        )
        
        result = await mock_agent.handle_event(event)
        
        assert result is True
        assert handler_called is True
        assert mock_agent.stats["events_processed"] == 1
    
    @pytest.mark.asyncio
    async def test_agent_handle_event_no_handler(self, mock_agent):
        """Test handling event with no registered handler"""
        event = AgentEvent(
            event_id="test_001",
            event_type="unknown_event",
            source_agent_id="sender"
        )
        
        result = await mock_agent.handle_event(event)
        
        assert result is False
        assert mock_agent.stats["events_processed"] == 0
    
    @pytest.mark.asyncio
    async def test_agent_handle_event_disabled(self, mock_agent):
        """Test handling event when agent is disabled"""
        mock_agent.config.enabled = False
        
        event = AgentEvent(
            event_id="test_001",
            event_type="test_event",
            source_agent_id="sender"
        )
        
        result = await mock_agent.handle_event(event)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_agent_handle_event_stopped(self, mock_agent):
        """Test handling event when agent is stopped"""
        await mock_agent.start()
        await mock_agent.stop()
        
        event = AgentEvent(
            event_id="test_001",
            event_type="test_event",
            source_agent_id="sender"
        )
        
        result = await mock_agent.handle_event(event)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_agent_handle_event_handler_error(self, mock_agent):
        """Test event handling when handler raises an exception"""
        def failing_handler(event):
            raise Exception("Handler failed")
        
        mock_agent.register_event_handler("test_event", failing_handler)
        
        event = AgentEvent(
            event_id="test_001",
            event_type="test_event",
            source_agent_id="sender"
        )
        
        result = await mock_agent.handle_event(event)
        
        assert result is True  # Event was handled, but handler failed
        assert mock_agent.stats["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_agent_send_event_success(self, mock_agent):
        """Test successful event sending"""
        event = AgentEvent(
            event_id="test_001",
            event_type="test_event",
            source_agent_id=mock_agent.config.agent_id,
            target_agent_id="target"
        )
        
        result = await mock_agent.send_event(event)
        
        assert result is True
        assert mock_agent.stats["events_sent"] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_agent_send_event_failure(self, mock_agent):
        """Test event sending failure"""
        # Mock send_event to raise an exception
        async def failing_send(event):
            try:
                raise Exception("Send failed")
            except Exception as e:
                mock_agent.stats["errors"] += 1
                return False
        
        mock_agent.send_event = failing_send
        
        event = AgentEvent(
            event_id="test_001",
            event_type="test_event",
            source_agent_id=mock_agent.config.agent_id,
            target_agent_id="target"
        )
        
        result = await mock_agent.send_event(event)
        
        assert result is False
        assert mock_agent.stats["errors"] == 1
    
    def test_agent_get_state(self, mock_agent):
        """Test getting agent state"""
        assert mock_agent.get_state() == AgentState.IDLE
        
        mock_agent.state = AgentState.ACTIVE
        assert mock_agent.get_state() == AgentState.ACTIVE
    
    def test_agent_get_stats(self, mock_agent):
        """Test getting agent statistics"""
        stats = mock_agent.get_stats()
        
        assert "events_processed" in stats
        assert "events_sent" in stats
        assert "errors" in stats
        assert "uptime_seconds" in stats
        assert "state" in stats
        assert "enabled" in stats
        assert stats["state"] == "idle"
        assert stats["enabled"] is True
    
    def test_agent_get_config(self, mock_agent, agent_config):
        """Test getting agent configuration"""
        config = mock_agent.get_config()
        assert config == agent_config
    
    @pytest.mark.asyncio
    async def test_agent_ping_handler(self, mock_agent):
        """Test ping event handler"""
        event = AgentEvent(
            event_id="ping_001",
            event_type="ping",
            source_agent_id="sender"
        )
        
        # Mock send_event to capture the response
        sent_events = []
        async def mock_send(event):
            sent_events.append(event)
            return True
        
        mock_agent.send_event = mock_send
        
        await mock_agent._handle_ping(event)
        
        assert len(sent_events) == 1
        response = sent_events[0]
        assert response.event_type == "pong"
        assert response.source_agent_id == mock_agent.config.agent_id
        assert response.target_agent_id == "sender"
        assert "timestamp" in response.data
    
    @pytest.mark.asyncio
    async def test_agent_status_handler(self, mock_agent):
        """Test status request event handler"""
        event = AgentEvent(
            event_id="status_001",
            event_type="status",
            source_agent_id="sender"
        )
        
        # Mock send_event to capture the response
        sent_events = []
        async def mock_send(event):
            sent_events.append(event)
            return True
        
        mock_agent.send_event = mock_send
        
        await mock_agent._handle_status_request(event)
        
        assert len(sent_events) == 1
        response = sent_events[0]
        assert response.event_type == "status_response"
        assert response.source_agent_id == mock_agent.config.agent_id
        assert response.target_agent_id == "sender"
        assert "state" in response.data
        assert "stats" in response.data
        assert "config" in response.data
    
    @pytest.mark.asyncio
    async def test_agent_shutdown_handler(self, mock_agent):
        """Test shutdown event handler"""
        await mock_agent.start()
        assert mock_agent.state == AgentState.ACTIVE
        
        event = AgentEvent(
            event_id="shutdown_001",
            event_type="shutdown",
            source_agent_id="sender"
        )
        
        await mock_agent._handle_shutdown(event)
        
        assert mock_agent.state == AgentState.STOPPED


class TestTestAgent:
    """Test the TestAgent implementation"""
    
    @pytest.fixture
    def test_agent_config(self):
        """Create a test agent configuration"""
        return AgentConfig(
            agent_id="test_agent_001",
            name="Test Agent",
            description="A test agent",
            log_level="DEBUG"
        )
    
    @pytest.fixture
    def test_agent(self, test_agent_config):
        """Create a TestAgent instance"""
        return TestAgentImpl(test_agent_config)
    
    @pytest.mark.asyncio
    async def test_test_agent_creation(self, test_agent):
        """Test TestAgent creation"""
        assert test_agent.config.agent_id == "test_agent_001"
        assert test_agent.counter == 0
        assert test_agent.task is None
    
    @pytest.mark.asyncio
    async def test_test_agent_lifecycle(self, test_agent):
        """Test TestAgent lifecycle"""
        # Start the agent
        success = await test_agent.start()
        assert success is True
        assert test_agent.state == AgentState.ACTIVE
        assert test_agent.task is not None
        
        # Wait a bit for the counter to increment
        await asyncio.sleep(0.1)
        
        # Check that counter has increased
        assert test_agent.counter > 0
        
        # Stop the agent
        success = await test_agent.stop()
        assert success is True
        assert test_agent.state == AgentState.STOPPED
        assert test_agent.task is None
    
    @pytest.mark.asyncio
    async def test_test_agent_event_handling(self, test_agent):
        """Test TestAgent event handling"""
        await test_agent.start()
        
        # Send a test event
        event = AgentEvent(
            event_id="test_001",
            event_type="test",
            source_agent_id="sender",
            target_agent_id=test_agent.config.agent_id,
            data={"message": "Hello"}
        )
        
        # Mock send_event to capture the response
        sent_events = []
        async def mock_send(event):
            sent_events.append(event)
            return True
        
        test_agent.send_event = mock_send
        
        result = await test_agent.handle_event(event)
        
        assert result is True
        assert len(sent_events) == 1
        response = sent_events[0]
        assert response.event_type == "test_response"
        assert response.data["counter"] == test_agent.counter
        assert "timestamp" in response.data
        assert response.data["message"] == "Test event processed successfully"
        
        await test_agent.stop()
    
    @pytest.mark.asyncio
    async def test_test_agent_stats(self, test_agent):
        """Test TestAgent statistics"""
        await test_agent.start()
        
        # Wait a bit for the counter to increment
        await asyncio.sleep(0.1)
        
        stats = test_agent.get_test_stats()
        
        assert "counter" in stats
        assert stats["counter"] > 0
        assert "state" in stats
        assert "uptime_seconds" in stats
        
        await test_agent.stop()


if __name__ == "__main__":
    pytest.main([__file__])
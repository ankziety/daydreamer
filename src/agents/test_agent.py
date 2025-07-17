"""
Test Agent implementation
A simple agent that extends the base Agent class for testing and demonstration.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from .agent import Agent, AgentConfig, AgentEvent

logger = logging.getLogger(__name__)


class DemoAgent(Agent):
    """
    A simple test agent that demonstrates the base Agent functionality.
    
    This agent:
    - Responds to ping events
    - Maintains a simple counter
    - Logs all activities
    - Demonstrates lifecycle management
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.counter = 0
        self.task = None
        # Register test event handler
        self.register_event_handler("test", self._handle_test_event)
        logger.info(f"Test agent {config.agent_id} created")
    
    async def _on_start(self):
        """Start the test agent's main loop"""
        logger.info(f"Test agent {self.config.agent_id} starting main loop")
        self.task = asyncio.create_task(self._main_loop())
    
    async def _on_stop(self):
        """Stop the test agent's main loop"""
        logger.info(f"Test agent {self.config.agent_id} stopping main loop")
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
    
    async def _on_pause(self):
        """Pause the test agent"""
        logger.info(f"Test agent {self.config.agent_id} paused")
    
    async def _on_resume(self):
        """Resume the test agent"""
        logger.info(f"Test agent {self.config.agent_id} resumed")
    
    async def _on_cleanup(self):
        """Clean up test agent resources"""
        logger.info(f"Test agent {self.config.agent_id} cleaning up")
        self.counter = 0
    
    async def _main_loop(self):
        """Main loop for the test agent"""
        while self.state.value in ["active", "paused"]:
            try:
                if self.state.value == "active":
                    self.counter += 1
                    logger.debug(f"Test agent {self.config.agent_id} counter: {self.counter}")
                
                await asyncio.sleep(1)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in test agent main loop: {e}")
                await asyncio.sleep(1)
    
    async def handle_event(self, event: AgentEvent) -> bool:
        """Override event handling to add test-specific logic"""
        # Call parent implementation which will handle registered handlers
        return await super().handle_event(event)
    
    async def _handle_test_event(self, event: AgentEvent):
        """Handle test-specific events"""
        logger.info(f"Test agent {self.config.agent_id} received test event: {event.data}")
        
        # Send a response
        response = AgentEvent(
            event_id=f"test_response_{event.event_id}",
            event_type="test_response",
            source_agent_id=self.config.agent_id,
            target_agent_id=event.source_agent_id,
            data={
                "counter": self.counter,
                "timestamp": datetime.now().isoformat(),
                "message": "Test event processed successfully"
            }
        )
        await self.send_event(response)
    
    def get_test_stats(self) -> Dict[str, Any]:
        """Get test-specific statistics"""
        stats = self.get_stats()
        stats["counter"] = self.counter
        return stats


async def test_agent_functionality():
    """Test the agent functionality"""
    # Create test agent configuration
    config = AgentConfig(
        agent_id="test_agent_001",
        name="Test Agent",
        description="A simple test agent",
        log_level="DEBUG"
    )
    
    # Create and start the agent
    agent = DemoAgent(config)
    
    print("🤖 Testing Agent Functionality")
    print("=" * 50)
    
    # Test 1: Agent creation and initialization
    print(f"1. Agent created: {agent.config.agent_id}")
    print(f"   State: {agent.get_state().value}")
    print(f"   Enabled: {agent.config.enabled}")
    
    # Test 2: Start the agent
    print("\n2. Starting agent...")
    success = await agent.start()
    print(f"   Start successful: {success}")
    print(f"   State: {agent.get_state().value}")
    
    # Test 3: Send a test event
    print("\n3. Sending test event...")
    test_event = AgentEvent(
        event_id="test_001",
        event_type="test",
        source_agent_id="test_sender",
        target_agent_id=agent.config.agent_id,
        data={"message": "Hello from test!"}
    )
    result = await agent.handle_event(test_event)
    print(f"   Event handled: {result}")
    
    # Test 4: Check stats
    print("\n4. Agent statistics:")
    stats = agent.get_test_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test 5: Pause and resume
    print("\n5. Testing pause/resume...")
    await agent.pause()
    print(f"   Paused: {agent.get_state().value}")
    await agent.resume()
    print(f"   Resumed: {agent.get_state().value}")
    
    # Test 6: Stop the agent
    print("\n6. Stopping agent...")
    success = await agent.stop()
    print(f"   Stop successful: {success}")
    print(f"   State: {agent.get_state().value}")
    
    # Test 7: Final stats
    print("\n7. Final statistics:")
    final_stats = agent.get_test_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Agent functionality test completed!")


if __name__ == "__main__":
    asyncio.run(test_agent_functionality())
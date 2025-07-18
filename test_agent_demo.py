#!/usr/bin/env python3
"""
Simple test script to demonstrate the Agent class functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.agent import Agent, AgentConfig, AgentState, AgentEvent


class DemoAgent(Agent):
    """Simple demo agent for testing"""
    
    async def _on_start(self):
        print(f" Demo agent {self.config.agent_id} started")
    
    async def _on_stop(self):
        print(f" Demo agent {self.config.agent_id} stopped")
    
    async def _on_pause(self):
        print(f"⏸️ Demo agent {self.config.agent_id} paused")
    
    async def _on_resume(self):
        print(f"▶️ Demo agent {self.config.agent_id} resumed")
    
    async def _on_cleanup(self):
        print(f"🧹 Demo agent {self.config.agent_id} cleaned up")


async def test_agent_lifecycle():
    """Test the agent lifecycle"""
    print(" Testing Agent Lifecycle")
    print("=" * 50)
    
    # Create agent configuration
    config = AgentConfig(
        agent_id="demo_001",
        name="Demo Agent",
        description="A demonstration agent",
        log_level="INFO"
    )
    
    # Create agent
    agent = DemoAgent(config)
    print(f" Agent created: {agent.config.agent_id}")
    print(f"   State: {agent.get_state().value}")
    
    # Test start
    print("\n Starting agent...")
    success = await agent.start()
    print(f"   Start successful: {success}")
    print(f"   State: {agent.get_state().value}")
    
    # Test pause/resume
    print("\n⏸️ Testing pause/resume...")
    await agent.pause()
    print(f"   Paused: {agent.get_state().value}")
    await agent.resume()
    print(f"   Resumed: {agent.get_state().value}")
    
    # Test event handling
    print("\n📨 Testing event handling...")
    event = AgentEvent(
        event_id="test_001",
        event_type="ping",
        source_agent_id="tester",
        target_agent_id=agent.config.agent_id
    )
    result = await agent.handle_event(event)
    print(f"   Event handled: {result}")
    
    # Test stats
    print("\n Agent statistics:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test stop
    print("\n Stopping agent...")
    success = await agent.stop()
    print(f"   Stop successful: {success}")
    print(f"   State: {agent.get_state().value}")
    
    # Test cleanup
    print("\n🧹 Testing cleanup...")
    await agent.cleanup()
    
    print("\n Agent lifecycle test completed!")


async def test_event_handling():
    """Test event handling functionality"""
    print("\n📨 Testing Event Handling")
    print("=" * 50)
    
    config = AgentConfig(
        agent_id="event_test_001",
        name="Event Test Agent",
        log_level="INFO"
    )
    
    agent = DemoAgent(config)
    await agent.start()
    
    # Test ping event
    print("Testing ping event...")
    ping_event = AgentEvent(
        event_id="ping_001",
        event_type="ping",
        source_agent_id="tester"
    )
    result = await agent.handle_event(ping_event)
    print(f"   Ping handled: {result}")
    
    # Test status event
    print("Testing status event...")
    status_event = AgentEvent(
        event_id="status_001",
        event_type="status",
        source_agent_id="tester"
    )
    result = await agent.handle_event(status_event)
    print(f"   Status handled: {result}")
    
    # Test custom event
    print("Testing custom event...")
    custom_event = AgentEvent(
        event_id="custom_001",
        event_type="custom_event",
        source_agent_id="tester",
        data={"message": "Hello from custom event"}
    )
    result = await agent.handle_event(custom_event)
    print(f"   Custom event handled: {result}")
    
    await agent.stop()
    print(" Event handling test completed!")


async def test_state_transitions():
    """Test state transition logic"""
    print("\n Testing State Transitions")
    print("=" * 50)
    
    config = AgentConfig(
        agent_id="state_test_001",
        name="State Test Agent",
        log_level="INFO"
    )
    
    agent = DemoAgent(config)
    
    # Test invalid transitions
    print("Testing invalid state transitions...")
    
    # Try to pause from IDLE
    result = await agent.pause()
    print(f"   Pause from IDLE: {result}")
    
    # Try to resume from IDLE
    result = await agent.resume()
    print(f"   Resume from IDLE: {result}")
    
    # Try to start twice
    await agent.start()
    result = await agent.start()
    print(f"   Start twice: {result}")
    
    # Try to pause from ACTIVE
    result = await agent.pause()
    print(f"   Pause from ACTIVE: {result}")
    
    # Try to resume from PAUSED
    result = await agent.resume()
    print(f"   Resume from PAUSED: {result}")
    
    # Try to stop
    result = await agent.stop()
    print(f"   Stop: {result}")
    
    # Try to stop again
    result = await agent.stop()
    print(f"   Stop again: {result}")
    
    print(" State transition test completed!")


async def main():
    """Main test function"""
    print(" Agent Class Test Suite")
    print("=" * 60)
    
    try:
        await test_agent_lifecycle()
        await test_event_handling()
        await test_state_transitions()
        
        print("\n All tests completed successfully!")
        print(" Agent class is working correctly!")
        
    except Exception as e:
        print(f"\n Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
"""
Multi-Agent Simulation for Daydreamer Project
This system demonstrates multiple intelligent agents interacting using Gemma 3N.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

from ..agents.intelligent_agent import IntelligentAgent, AgentConfig

logger = logging.getLogger(__name__)

@dataclass
class SimulationConfig:
    """Configuration for multi-agent simulation"""
    simulation_id: str
    duration_seconds: int = 60
    agent_count: int = 3
    interaction_frequency: float = 10.0  # seconds between interactions
    enable_autonomous_thinking: bool = True
    enable_agent_communication: bool = True
    enable_reasoning_tasks: bool = True
    log_level: str = "INFO"

class MultiAgentSimulation:
    """
    Multi-agent simulation system for Daydreamer project.
    
    This system creates multiple intelligent agents that:
    - Think autonomously using default mode network processes
    - Communicate with each other
    - Reason about shared problems
    - Demonstrate biological process simulation
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.agents: Dict[str, IntelligentAgent] = {}
        self.simulation_task = None
        self.is_running = False
        self.start_time = None
        self.stats = {
            "total_thoughts": 0,
            "total_communications": 0,
            "total_reasoning_sessions": 0,
            "agent_interactions": 0
        }
        
        # Configure logging
        logging.basicConfig(level=getattr(logging, config.log_level))
        
        logger.info(f"🎬 Created multi-agent simulation: {config.simulation_id}")
    
    def create_agents(self):
        """Create intelligent agents with different personalities"""
        agent_configs = [
            AgentConfig(
                agent_id="philosopher",
                personality="philosophical",
                thinking_frequency=4.0,
                enable_thinking=self.config.enable_autonomous_thinking,
                enable_reasoning=self.config.enable_reasoning_tasks,
                enable_communication=self.config.enable_agent_communication
            ),
            AgentConfig(
                agent_id="scientist",
                personality="analytical",
                thinking_frequency=3.5,
                enable_thinking=self.config.enable_autonomous_thinking,
                enable_reasoning=self.config.enable_reasoning_tasks,
                enable_communication=self.config.enable_agent_communication
            ),
            AgentConfig(
                agent_id="artist",
                personality="creative",
                thinking_frequency=5.0,
                enable_thinking=self.config.enable_autonomous_thinking,
                enable_reasoning=self.config.enable_reasoning_tasks,
                enable_communication=self.config.enable_agent_communication
            )
        ]
        
        # Create agents
        for agent_config in agent_configs[:self.config.agent_count]:
            agent = IntelligentAgent(agent_config)
            self.agents[agent_config.agent_id] = agent
        
        logger.info(f"🤖 Created {len(self.agents)} agents: {list(self.agents.keys())}")
    
    async def start_simulation(self):
        """Start the multi-agent simulation"""
        if self.is_running:
            logger.warning("Simulation is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info(f"🚀 Starting multi-agent simulation: {self.config.simulation_id}")
        
        # Start all agents
        for agent in self.agents.values():
            await agent.start()
        
        # Start simulation tasks
        tasks = []
        
        if self.config.enable_agent_communication:
            tasks.append(self._agent_communication_loop())
        
        if self.config.enable_reasoning_tasks:
            tasks.append(self._reasoning_tasks_loop())
        
        tasks.append(self._simulation_monitoring_loop())
        
        # Run all tasks concurrently
        self.simulation_task = asyncio.gather(*tasks)
        
        try:
            await self.simulation_task
        except asyncio.CancelledError:
            logger.info("Simulation was cancelled")
        finally:
            await self.stop_simulation()
    
    async def stop_simulation(self):
        """Stop the simulation and clean up"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        # Cancel simulation task if running
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"🛑 Stopped simulation: {self.config.simulation_id}")
    
    async def _agent_communication_loop(self):
        """Loop for agent-to-agent communication"""
        agent_ids = list(self.agents.keys())
        
        while self.is_running:
            try:
                # Select two random agents for communication
                if len(agent_ids) >= 2:
                    import random
                    agent1_id, agent2_id = random.sample(agent_ids, 2)
                    
                    agent1 = self.agents[agent1_id]
                    agent2 = self.agents[agent2_id]
                    
                    # Generate a topic for discussion
                    topics = [
                        "What is consciousness?",
                        "How do neural networks work?",
                        "What is creativity?",
                        "The nature of intelligence",
                        "The future of AI",
                        "Biological vs artificial intelligence"
                    ]
                    
                    topic = random.choice(topics)
                    
                    # Agent 1 initiates conversation
                    message = f"Hello {agent2_id}! I'd like to discuss: {topic}"
                    response = await agent1.communicate(message, agent2_id)
                    
                    # Agent 2 responds
                    reply = await agent2.communicate(response, agent1_id)
                    
                    # Update stats
                    self.stats["total_communications"] += 2
                    self.stats["agent_interactions"] += 1
                    
                    logger.info(f"💬 {agent1_id} ↔ {agent2_id}: {topic}")
                    logger.debug(f"  {agent1_id}: {message}")
                    logger.debug(f"  {agent2_id}: {response}")
                    logger.debug(f"  {agent1_id}: {reply}")
                
                # Wait before next interaction
                await asyncio.sleep(self.config.interaction_frequency)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in communication loop: {e}")
                await asyncio.sleep(1)
    
    async def _reasoning_tasks_loop(self):
        """Loop for collaborative reasoning tasks"""
        reasoning_tasks = [
            "How can we improve AI agent communication?",
            "What are the key components of consciousness?",
            "How do biological processes differ from computational ones?",
            "What makes an AI system truly intelligent?",
            "How can we simulate default mode network processes?",
            "What are the ethical implications of AI consciousness?"
        ]
        
        task_index = 0
        
        while self.is_running:
            try:
                if task_index < len(reasoning_tasks):
                    task = reasoning_tasks[task_index]
                    
                    logger.info(f"🤔 Collaborative reasoning task: {task}")
                    
                    # Have each agent reason about the task
                    for agent_id, agent in self.agents.items():
                        reasoning = await agent.reason(task)
                        logger.info(f"  {agent_id}: {reasoning[:100]}...")
                        
                        # Share reasoning with other agents
                        for other_agent in self.agents.values():
                            if other_agent.config.agent_id != agent_id:
                                other_agent.add_to_working_memory(f"{agent_id}'s reasoning: {reasoning[:50]}...")
                    
                    self.stats["total_reasoning_sessions"] += len(self.agents)
                    task_index += 1
                
                # Wait before next reasoning session
                await asyncio.sleep(self.config.interaction_frequency * 2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in reasoning loop: {e}")
                await asyncio.sleep(1)
    
    async def _simulation_monitoring_loop(self):
        """Monitor simulation progress and stats"""
        while self.is_running:
            try:
                # Update total thoughts from all agents
                total_thoughts = sum(agent.stats["thoughts_generated"] for agent in self.agents.values())
                self.stats["total_thoughts"] = total_thoughts
                
                # Log simulation status
                elapsed = (datetime.now() - self.start_time).total_seconds()
                remaining = max(0, self.config.duration_seconds - elapsed)
                
                logger.info(f"📊 Simulation Status - Elapsed: {elapsed:.1f}s, Remaining: {remaining:.1f}s")
                logger.info(f"  Thoughts: {self.stats['total_thoughts']}, Communications: {self.stats['total_communications']}")
                
                # Check if simulation should end
                if elapsed >= self.config.duration_seconds:
                    logger.info("⏰ Simulation duration reached, stopping...")
                    break
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1)
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get comprehensive simulation statistics"""
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = agent.get_stats()
        
        return {
            "simulation_id": self.config.simulation_id,
            "duration_seconds": self.config.duration_seconds,
            "agent_count": len(self.agents),
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "elapsed_time": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "simulation_stats": self.stats,
            "agent_stats": agent_stats
        }
    
    def export_simulation_data(self, filename: str = None):
        """Export simulation data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{self.config.simulation_id}_{timestamp}.json"
        
        data = {
            "simulation_config": {
                "simulation_id": self.config.simulation_id,
                "duration_seconds": self.config.duration_seconds,
                "agent_count": self.config.agent_count,
                "interaction_frequency": self.config.interaction_frequency
            },
            "simulation_stats": self.get_simulation_stats(),
            "agent_memories": {}
        }
        
        # Export agent memories
        for agent_id, agent in self.agents.items():
            data["agent_memories"][agent_id] = {
                "episodic": agent.memory.episodic,
                "semantic": agent.memory.semantic,
                "working": agent.memory.working,
                "conversation_history": agent.memory.conversation_history
            }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 Exported simulation data to: {filename}")

# Demo function for hackathon
async def demo_multi_agent_simulation():
    """Demo the multi-agent simulation for hackathon presentation"""
    print("🎬 Daydreamer Multi-Agent Simulation Demo")
    print("=" * 50)
    
    # Create simulation configuration
    config = SimulationConfig(
        simulation_id="hackathon_demo",
        duration_seconds=30,  # 30 second demo
        agent_count=3,
        interaction_frequency=5.0,
        enable_autonomous_thinking=True,
        enable_agent_communication=True,
        enable_reasoning_tasks=True,
        log_level="INFO"
    )
    
    # Create simulation
    simulation = MultiAgentSimulation(config)
    
    # Create agents
    simulation.create_agents()
    
    print("🤖 Agents created and ready")
    print("🚀 Starting simulation...")
    
    # Start simulation
    try:
        await simulation.start_simulation()
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    finally:
        await simulation.stop_simulation()
    
    # Show final stats
    stats = simulation.get_simulation_stats()
    print("\n📊 Final Simulation Statistics:")
    print(f"  Total Thoughts: {stats['simulation_stats']['total_thoughts']}")
    print(f"  Total Communications: {stats['simulation_stats']['total_communications']}")
    print(f"  Total Reasoning Sessions: {stats['simulation_stats']['total_reasoning_sessions']}")
    print(f"  Agent Interactions: {stats['simulation_stats']['agent_interactions']}")
    
    # Export data
    simulation.export_simulation_data("hackathon_demo_results.json")
    
    print("\n✅ Demo completed! Check hackathon_demo_results.json for detailed data.")

if __name__ == "__main__":
    asyncio.run(demo_multi_agent_simulation())
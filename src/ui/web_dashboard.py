"""
Web Dashboard for Daydreamer Simulation Monitoring

This module provides a modern web dashboard for monitoring Daydreamer simulations
with real-time updates, agent activity visualization, and interactive controls.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from ..simulation.multi_agent_simulation import MultiAgentSimulation, SimulationConfig

logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """Configuration for the web dashboard"""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    static_dir: str = "static"
    template_dir: str = "templates"

@dataclass
class SimulationMetrics:
    """Real-time simulation metrics"""
    simulation_id: str
    is_running: bool
    start_time: Optional[datetime]
    duration_seconds: int
    agent_count: int
    total_thoughts: int
    total_communications: int
    total_reasoning_sessions: int
    agent_interactions: int
    memory_usage_mb: float
    cpu_usage_percent: float
    active_agents: List[str]
    last_activity: datetime

class WebDashboard:
    """
    Modern web dashboard for monitoring Daydreamer simulations.
    
    Features:
    - Real-time simulation status and metrics
    - Agent activity visualization
    - Memory usage and performance charts
    - Interactive controls for simulation management
    - Responsive design for multiple screen sizes
    """
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        self.app = FastAPI(title="Daydreamer Dashboard", version="1.0.0")
        self.simulation: Optional[MultiAgentSimulation] = None
        self.active_connections: List[WebSocket] = []
        self.metrics_history: List[SimulationMetrics] = []
        
        # Setup routes
        self._setup_routes()
        self._setup_websockets()
        
        logger.info(f"🎛️ Created web dashboard on {self.config.host}:{self.config.port}")
    
    def _setup_routes(self):
        """Setup API routes and static file serving"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            """Serve the main dashboard HTML"""
            return self._get_dashboard_html()
        
        @self.app.get("/api/status")
        async def get_status():
            """Get current simulation status"""
            return self._get_simulation_status()
        
        @self.app.post("/api/simulation/start")
        async def start_simulation(config: Dict[str, Any]):
            """Start a new simulation"""
            return await self._start_simulation(config)
        
        @self.app.post("/api/simulation/stop")
        async def stop_simulation():
            """Stop the current simulation"""
            return await self._stop_simulation()
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get simulation metrics"""
            return self._get_metrics()
        
        @self.app.get("/api/agents")
        async def get_agents():
            """Get agent information"""
            return self._get_agent_info()
        
        # Mount static files
        static_path = Path(__file__).parent / self.config.static_dir
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    def _setup_websockets(self):
        """Setup WebSocket connections for real-time updates"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await asyncio.sleep(1)
                    if websocket in self.active_connections:
                        await websocket.send_text(json.dumps(self._get_realtime_data()))
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    def _get_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daydreamer Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #4a5568;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #718096;
            font-size: 1.1rem;
        }
        
        .controls {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .control-buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .metric-card h3 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .metric-label {
            color: #718096;
            font-size: 0.9rem;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .chart-container h3 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-running {
            background: #48bb78;
            animation: pulse 2s infinite;
        }
        
        .status-stopped {
            background: #f56565;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .control-buttons {
                flex-direction: column;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Daydreamer Dashboard</h1>
            <p>Real-time monitoring of AI agent simulations</p>
        </div>
        
        <div class="controls">
            <h3>Simulation Controls</h3>
            <div class="control-buttons">
                <button class="btn btn-primary" onclick="startSimulation()">Start Simulation</button>
                <button class="btn btn-danger" onclick="stopSimulation()">Stop Simulation</button>
                <button class="btn btn-primary" onclick="refreshData()">Refresh Data</button>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Simulation Status</h3>
                <div class="metric-value">
                    <span class="status-indicator" id="status-indicator"></span>
                    <span id="status-text">Stopped</span>
                </div>
                <div class="metric-label">Current simulation state</div>
            </div>
            
            <div class="metric-card">
                <h3>Active Agents</h3>
                <div class="metric-value" id="agent-count">0</div>
                <div class="metric-label">Number of active agents</div>
            </div>
            
            <div class="metric-card">
                <h3>Total Thoughts</h3>
                <div class="metric-value" id="total-thoughts">0</div>
                <div class="metric-label">Autonomous thoughts generated</div>
            </div>
            
            <div class="metric-card">
                <h3>Communications</h3>
                <div class="metric-value" id="total-communications">0</div>
                <div class="metric-label">Agent interactions</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Activity Over Time</h3>
            <canvas id="activityChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>Agent Activity</h3>
            <canvas id="agentChart" width="400" height="200"></canvas>
        </div>
    </div>
    
    <script>
        let activityChart, agentChart;
        let ws;
        
        // Initialize charts
        function initCharts() {
            const activityCtx = document.getElementById('activityChart').getContext('2d');
            activityChart = new Chart(activityCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Thoughts',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Communications',
                        data: [],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            const agentCtx = document.getElementById('agentChart').getContext('2d');
            agentChart = new Chart(agentCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#f5576c',
                            '#4facfe'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                }
            });
        }
        
        // Connect to WebSocket
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                setTimeout(connectWebSocket, 1000);
            };
        }
        
        // Update dashboard with real-time data
        function updateDashboard(data) {
            // Update status
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            
            if (data.is_running) {
                statusIndicator.className = 'status-indicator status-running';
                statusText.textContent = 'Running';
            } else {
                statusIndicator.className = 'status-indicator status-stopped';
                statusText.textContent = 'Stopped';
            }
            
            // Update metrics
            document.getElementById('agent-count').textContent = data.agent_count;
            document.getElementById('total-thoughts').textContent = data.total_thoughts;
            document.getElementById('total-communications').textContent = data.total_communications;
            
            // Update charts
            updateCharts(data);
        }
        
        // Update charts with new data
        function updateCharts(data) {
            const now = new Date().toLocaleTimeString();
            
            // Activity chart
            if (activityChart.data.labels.length > 20) {
                activityChart.data.labels.shift();
                activityChart.data.datasets[0].data.shift();
                activityChart.data.datasets[1].data.shift();
            }
            
            activityChart.data.labels.push(now);
            activityChart.data.datasets[0].data.push(data.total_thoughts);
            activityChart.data.datasets[1].data.push(data.total_communications);
            activityChart.update();
            
            // Agent chart
            if (data.agents) {
                agentChart.data.labels = data.agents.map(a => a.agent_id);
                agentChart.data.datasets[0].data = data.agents.map(a => a.thought_count);
                agentChart.update();
            }
        }
        
        // API functions
        async function startSimulation() {
            try {
                const response = await fetch('/api/simulation/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        simulation_id: 'dashboard-demo',
                        duration_seconds: 300,
                        agent_count: 3,
                        interaction_frequency: 10.0,
                        enable_autonomous_thinking: true,
                        enable_agent_communication: true,
                        enable_reasoning_tasks: true
                    })
                });
                
                if (response.ok) {
                    console.log('Simulation started');
                } else {
                    console.error('Failed to start simulation');
                }
            } catch (error) {
                console.error('Error starting simulation:', error);
            }
        }
        
        async function stopSimulation() {
            try {
                const response = await fetch('/api/simulation/stop', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    console.log('Simulation stopped');
                } else {
                    console.error('Failed to stop simulation');
                }
            } catch (error) {
                console.error('Error stopping simulation:', error);
            }
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            connectWebSocket();
            refreshData();
        });
    </script>
</body>
</html>
        """
    
    def _get_simulation_status(self) -> Dict[str, Any]:
        """Get current simulation status"""
        if not self.simulation:
            return {
                "is_running": False,
                "simulation_id": None,
                "agent_count": 0,
                "total_thoughts": 0,
                "total_communications": 0,
                "total_reasoning_sessions": 0,
                "agent_interactions": 0,
                "active_agents": [],
                "last_activity": datetime.now().isoformat()
            }
        
        stats = self.simulation.get_simulation_stats()
        return {
            "is_running": self.simulation.is_running,
            "simulation_id": self.simulation.config.simulation_id,
            "agent_count": len(self.simulation.agents),
            "total_thoughts": stats.get("total_thoughts", 0),
            "total_communications": stats.get("total_communications", 0),
            "total_reasoning_sessions": stats.get("total_reasoning_sessions", 0),
            "agent_interactions": stats.get("agent_interactions", 0),
            "active_agents": list(self.simulation.agents.keys()),
            "last_activity": datetime.now().isoformat()
        }
    
    async def _start_simulation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new simulation"""
        try:
            if self.simulation and self.simulation.is_running:
                raise HTTPException(status_code=400, detail="Simulation already running")
            
            # Create simulation config
            sim_config = SimulationConfig(
                simulation_id=config.get("simulation_id", f"sim-{datetime.now().timestamp()}"),
                duration_seconds=config.get("duration_seconds", 60),
                agent_count=config.get("agent_count", 3),
                interaction_frequency=config.get("interaction_frequency", 10.0),
                enable_autonomous_thinking=config.get("enable_autonomous_thinking", True),
                enable_agent_communication=config.get("enable_agent_communication", True),
                enable_reasoning_tasks=config.get("enable_reasoning_tasks", True)
            )
            
            # Create and start simulation
            self.simulation = MultiAgentSimulation(sim_config)
            self.simulation.create_agents()
            
            # Start simulation in background
            asyncio.create_task(self.simulation.start_simulation())
            
            logger.info(f" Started simulation: {sim_config.simulation_id}")
            
            return {
                "success": True,
                "simulation_id": sim_config.simulation_id,
                "message": "Simulation started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting simulation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _stop_simulation(self) -> Dict[str, Any]:
        """Stop the current simulation"""
        try:
            if not self.simulation:
                raise HTTPException(status_code=400, detail="No simulation running")
            
            await self.simulation.stop_simulation()
            
            logger.info(" Stopped simulation")
            
            return {
                "success": True,
                "message": "Simulation stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Error stopping simulation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _get_metrics(self) -> Dict[str, Any]:
        """Get simulation metrics"""
        if not self.simulation:
            return {"error": "No simulation running"}
        
        stats = self.simulation.get_simulation_stats()
        return {
            "simulation_id": self.simulation.config.simulation_id,
            "stats": stats,
            "agents": self._get_agent_info()
        }
    
    def _get_agent_info(self) -> List[Dict[str, Any]]:
        """Get agent information"""
        if not self.simulation:
            return []
        
        agents = []
        for agent_id, agent in self.simulation.agents.items():
            agents.append({
                "agent_id": agent_id,
                "personality": agent.config.personality,
                "thinking_frequency": agent.config.thinking_frequency,
                "is_active": agent.is_running,
                "thought_count": getattr(agent, 'thought_count', 0),
                "communication_count": getattr(agent, 'communication_count', 0)
            })
        
        return agents
    
    def _get_realtime_data(self) -> Dict[str, Any]:
        """Get real-time data for WebSocket updates"""
        status = self._get_simulation_status()
        status["agents"] = self._get_agent_info()
        return status
    
    async def start(self):
        """Start the web dashboard server"""
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info" if self.config.debug else "warning"
        )
        
        server = uvicorn.Server(config)
        logger.info(f"🌐 Starting web dashboard on http://{self.config.host}:{self.config.port}")
        await server.serve()
    
    def run(self):
        """Run the dashboard in a blocking manner"""
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info" if self.config.debug else "warning"
        )

# Demo function
async def demo_web_dashboard():
    """Demo the web dashboard"""
    dashboard = WebDashboard(DashboardConfig(debug=True))
    
    print("🌐 Starting Daydreamer Web Dashboard...")
    print(f" Dashboard will be available at: http://localhost:{dashboard.config.port}")
    print("🎮 Use the dashboard to start and monitor simulations")
    
    await dashboard.start()

if __name__ == "__main__":
    asyncio.run(demo_web_dashboard())
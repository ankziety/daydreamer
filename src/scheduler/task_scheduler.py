"""
Task Scheduler module for Daydreamer Project
This module provides the main TaskScheduler class for managing task execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import threading
import time

from .task import Task, TaskPriority, TaskState
from .scheduling_algorithm import SchedulingAlgorithm, PriorityAlgorithm
from .resource_manager import ResourceManager, Resource, ResourceType

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Sophisticated task scheduling system for agent activities.
    
    This class provides:
    - Priority-based task queuing
    - Resource allocation and management
    - Task dependency resolution
    - Scheduling algorithms (round-robin, priority, deadline-based)
    - Task monitoring and statistics
    """
    
    def __init__(self, 
                 algorithm: Optional[SchedulingAlgorithm] = None,
                 max_concurrent_tasks: int = 10,
                 enable_resource_management: bool = True):
        """
        Initialize the task scheduler.
        
        Args:
            algorithm: Scheduling algorithm to use (defaults to PriorityAlgorithm)
            max_concurrent_tasks: Maximum number of tasks to run concurrently
            enable_resource_management: Whether to enable resource management
        """
        self.algorithm = algorithm or PriorityAlgorithm()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.enable_resource_management = enable_resource_management
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.ready_queue: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # Resource management
        self.resource_manager = ResourceManager() if enable_resource_management else None
        
        # Scheduling state
        self.is_running = False
        self.scheduler_task = None
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            "total_tasks_submitted": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "total_tasks_cancelled": 0,
            "average_completion_time": 0.0,
            "scheduler_uptime": 0.0,
            "start_time": None
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "task_cancelled": [],
            "resource_allocated": [],
            "resource_deallocated": []
        }
        
        logger.info(f"Task Scheduler initialized with {self.algorithm.name} algorithm")
    
    def submit_task(self, task: Task) -> bool:
        """
        Submit a task to the scheduler.
        
        Args:
            task: Task to submit
            
        Returns:
            True if task was submitted successfully
        """
        with self.lock:
            if task.task_id in self.tasks:
                logger.warning(f"Task {task.task_id} already exists in scheduler")
                return False
            
            # Validate task dependencies
            if not self._validate_dependencies(task):
                logger.warning(f"Task {task.name} has invalid dependencies")
                return False
            
            self.tasks[task.task_id] = task
            self.stats["total_tasks_submitted"] += 1
            
            # Check if task is ready to run
            if self._are_dependencies_met(task):
                task.mark_ready()
                self.ready_queue.append(task)
                logger.info(f"Submitted task: {task.name} (ready to run)")
            else:
                task.mark_blocked()
                logger.info(f"Submitted task: {task.name} (blocked by dependencies)")
            
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if task was cancelled successfully
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task = self.tasks[task_id]
            
            if task.state == TaskState.RUNNING:
                # Task is currently running, mark it for cancellation
                task.mark_cancelled()
                self.stats["total_tasks_cancelled"] += 1
                self._trigger_event("task_cancelled", task)
                logger.info(f"Cancelled running task: {task.name}")
                return True
            
            elif task.state in [TaskState.PENDING, TaskState.READY, TaskState.BLOCKED]:
                # Remove from queues
                task.mark_cancelled()
                if task in self.ready_queue:
                    self.ready_queue.remove(task)
                
                self.stats["total_tasks_cancelled"] += 1
                self._trigger_event("task_cancelled", task)
                logger.info(f"Cancelled queued task: {task.name}")
                return True
            
            else:
                logger.warning(f"Cannot cancel task {task_id} in state {task.state}")
                return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskState]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task state, or None if task not found
        """
        with self.lock:
            if task_id in self.tasks:
                return self.tasks[task_id].state
            return None
    
    def get_ready_tasks(self) -> List[Task]:
        """
        Get all tasks that are ready to run.
        
        Returns:
            List of ready tasks
        """
        with self.lock:
            return self.ready_queue.copy()
    
    def get_running_tasks(self) -> List[Task]:
        """
        Get all currently running tasks.
        
        Returns:
            List of running tasks
        """
        with self.lock:
            return list(self.running_tasks.values())
    
    def get_completed_tasks(self) -> List[Task]:
        """
        Get all completed tasks.
        
        Returns:
            List of completed tasks
        """
        with self.lock:
            return self.completed_tasks.copy()
    
    def get_failed_tasks(self) -> List[Task]:
        """
        Get all failed tasks.
        
        Returns:
            List of failed tasks
        """
        with self.lock:
            return self.failed_tasks.copy()
    
    async def start(self):
        """Start the task scheduler"""
        if self.is_running:
            logger.warning("Task scheduler is already running")
            return
        
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        
        logger.info("Starting task scheduler")
        
        # Start the main scheduling loop
        self.scheduler_task = asyncio.create_task(self._scheduling_loop())
        
        # Start resource conflict resolution loop if enabled
        if self.enable_resource_management:
            asyncio.create_task(self._resource_conflict_resolution_loop())
    
    async def stop(self):
        """Stop the task scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel the scheduler task
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Update uptime
        if self.stats["start_time"]:
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
            self.stats["scheduler_uptime"] = uptime
        
        logger.info("Task scheduler stopped")
    
    async def _scheduling_loop(self):
        """Main scheduling loop"""
        while self.is_running:
            try:
                with self.lock:
                    # Check if we can start more tasks
                    if (len(self.running_tasks) < self.max_concurrent_tasks and 
                        self.ready_queue):
                        
                        # Select next task using the scheduling algorithm
                        start_time = time.time()
                        next_task = self.algorithm.select_next_task(self.ready_queue)
                        scheduling_time = time.time() - start_time
                        
                        if next_task:
                            # Remove from ready queue
                            self.ready_queue.remove(next_task)
                            
                            # Check resource availability
                            if self._can_allocate_resources(next_task):
                                # Allocate resources
                                if self._allocate_resources(next_task):
                                    # Start the task
                                    await self._start_task(next_task)
                                    
                                    # Update algorithm statistics
                                    self.algorithm.update_stats(scheduling_time)
                                else:
                                    # Resource allocation failed, put back in queue
                                    self.ready_queue.append(next_task)
                            else:
                                # Resources not available, put back in queue
                                self.ready_queue.append(next_task)
                
                # Check for completed tasks
                await self._check_completed_tasks()
                
                # Update dependency status
                self._update_dependencies()
                
                # Sleep briefly to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduling loop: {e}")
                await asyncio.sleep(1)
    
    async def _resource_conflict_resolution_loop(self):
        """Loop for resolving resource conflicts"""
        while self.is_running:
            try:
                if self.resource_manager:
                    conflicts_resolved = self.resource_manager.resolve_conflicts()
                    if conflicts_resolved > 0:
                        logger.info(f"Resolved {conflicts_resolved} resource conflicts")
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in resource conflict resolution: {e}")
                await asyncio.sleep(1)
    
    async def _start_task(self, task: Task):
        """Start a task"""
        task.mark_running()
        self.running_tasks[task.task_id] = task
        
        # Create task execution coroutine
        task_coro = self._execute_task(task)
        asyncio.create_task(task_coro)
        
        self._trigger_event("task_started", task)
        logger.info(f"Started task: {task.name}")
    
    async def _execute_task(self, task: Task):
        """Execute a task"""
        try:
            # Simulate task execution (in a real system, this would execute the actual task)
            await asyncio.sleep(task.estimated_duration)
            
            # Mark task as completed
            task.mark_completed()
            
            # Move to completed list
            with self.lock:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
                self.completed_tasks.append(task)
                
                # Deallocate resources
                if self.enable_resource_management:
                    self.resource_manager.deallocate_resources(task.task_id)
            
            self.stats["total_tasks_completed"] += 1
            self._trigger_event("task_completed", task)
            
            logger.info(f"Completed task: {task.name}")
            
        except asyncio.CancelledError:
            # Task was cancelled
            task.mark_cancelled()
            with self.lock:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
            
            self.stats["total_tasks_cancelled"] += 1
            self._trigger_event("task_cancelled", task)
            
            logger.info(f"Cancelled task: {task.name}")
            
        except Exception as e:
            # Task failed
            task.mark_failed(str(e))
            with self.lock:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
                self.failed_tasks.append(task)
                
                # Deallocate resources
                if self.enable_resource_management:
                    self.resource_manager.deallocate_resources(task.task_id)
            
            self.stats["total_tasks_failed"] += 1
            self._trigger_event("task_failed", task)
            
            logger.error(f"Task {task.name} failed: {e}")
    
    async def _check_completed_tasks(self):
        """Check for completed tasks and update statistics"""
        # This is handled in _execute_task for simplicity
        pass
    
    def _validate_dependencies(self, task: Task) -> bool:
        """Validate that all dependencies exist"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
        return True
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            dep_task = self.tasks[dep_id]
            if not dep_task.is_completed():
                return False
        return True
    
    def _update_dependencies(self):
        """Update dependency status for blocked tasks"""
        for task in self.tasks.values():
            if task.state == TaskState.BLOCKED:
                if self._are_dependencies_met(task):
                    task.mark_ready()
                    if task not in self.ready_queue:
                        self.ready_queue.append(task)
                    logger.debug(f"Task {task.name} dependencies met, moved to ready queue")
    
    def _can_allocate_resources(self, task: Task) -> bool:
        """Check if resources can be allocated for the task"""
        if not self.enable_resource_management or not task.resources_required:
            return True
        
        # Check if required resources are available
        for resource_type in task.resources_required:
            available_resources = self.resource_manager.get_available_resources(
                ResourceType(resource_type)
            )
            if not available_resources:
                return False
        
        return True
    
    def _allocate_resources(self, task: Task) -> bool:
        """Allocate resources for the task"""
        if not self.enable_resource_management or not task.resources_required:
            return True
        
        # Create resource requirements dictionary
        resource_requirements = {}
        for resource_type in task.resources_required:
            available_resources = self.resource_manager.get_available_resources(
                ResourceType(resource_type)
            )
            if available_resources:
                # Allocate from the first available resource
                resource = available_resources[0]
                resource_requirements[resource.resource_id] = 1.0  # Default amount
        
        return self.resource_manager.allocate_resources(task.task_id, resource_requirements)
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """
        Add an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def _trigger_event(self, event_type: str, task: Task):
        """Trigger an event"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(task)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.
        
        Returns:
            Dictionary containing scheduler statistics
        """
        with self.lock:
            stats = self.stats.copy()
            
            # Calculate average completion time
            completed_tasks = [t for t in self.completed_tasks if t.get_execution_time() is not None]
            if completed_tasks:
                avg_time = sum(t.get_execution_time() for t in completed_tasks) / len(completed_tasks)
                stats["average_completion_time"] = avg_time
            
            # Add current state information
            stats.update({
                "total_tasks": len(self.tasks),
                "ready_tasks": len(self.ready_queue),
                "running_tasks": len(self.running_tasks),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "algorithm_stats": self.algorithm.get_stats()
            })
            
            # Add resource manager stats if enabled
            if self.enable_resource_management:
                stats["resource_manager_stats"] = self.resource_manager.get_stats()
            
            return stats
    
    def get_task_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all tasks.
        
        Returns:
            Dictionary containing task summary
        """
        with self.lock:
            summary = {
                "total_tasks": len(self.tasks),
                "tasks_by_state": {},
                "tasks_by_priority": {},
                "overdue_tasks": [],
                "recent_tasks": []
            }
            
            # Group tasks by state
            for task in self.tasks.values():
                state = task.state.value
                if state not in summary["tasks_by_state"]:
                    summary["tasks_by_state"][state] = []
                summary["tasks_by_state"][state].append({
                    "task_id": task.task_id,
                    "name": task.name,
                    "priority": task.priority.value
                })
            
            # Group tasks by priority
            for task in self.tasks.values():
                priority = task.priority.value
                if priority not in summary["tasks_by_priority"]:
                    summary["tasks_by_priority"][priority] = []
                summary["tasks_by_priority"][priority].append({
                    "task_id": task.task_id,
                    "name": task.name,
                    "state": task.state.value
                })
            
            # Find overdue tasks
            for task in self.tasks.values():
                if task.is_overdue():
                    summary["overdue_tasks"].append({
                        "task_id": task.task_id,
                        "name": task.name,
                        "deadline": task.deadline.isoformat() if task.deadline else None,
                        "priority": task.priority.value
                    })
            
            # Get recent tasks (last 10)
            recent_tasks = sorted(
                self.tasks.values(),
                key=lambda t: t.created_at,
                reverse=True
            )[:10]
            
            summary["recent_tasks"] = [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "state": task.state.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat()
                }
                for task in recent_tasks
            ]
            
            return summary
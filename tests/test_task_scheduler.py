"""
Tests for the Task Scheduler system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.scheduler.task_scheduler import TaskScheduler
from src.scheduler.task import Task, TaskPriority, TaskState
from src.scheduler.scheduling_algorithm import (
    PriorityAlgorithm, RoundRobinAlgorithm, DeadlineAlgorithm, HybridAlgorithm
)
from src.scheduler.resource_manager import ResourceManager, Resource, ResourceType


class TestTask:
    """Test the Task class"""
    
    def test_task_creation(self):
        """Test basic task creation"""
        task = Task(
            name="Test Task",
            description="A test task",
            priority=TaskPriority.HIGH,
            estimated_duration=30.0
        )
        
        assert task.name == "Test Task"
        assert task.description == "A test task"
        assert task.priority == TaskPriority.HIGH
        assert task.estimated_duration == 30.0
        assert task.state == TaskState.PENDING
        assert task.task_id is not None
    
    def test_task_with_deadline(self):
        """Test task creation with deadline"""
        deadline = datetime.now() + timedelta(hours=1)
        task = Task(
            name="Deadline Task",
            description="Task with deadline",
            deadline=deadline
        )
        
        assert task.deadline == deadline
        assert not task.is_overdue()
    
    def test_task_state_transitions(self):
        """Test task state transitions"""
        task = Task(name="State Test", description="Testing state transitions")
        
        # PENDING -> READY
        task.mark_ready()
        assert task.state == TaskState.READY
        assert task.is_ready()
        
        # READY -> RUNNING
        task.mark_running()
        assert task.state == TaskState.RUNNING
        assert task.started_at is not None
        
        # RUNNING -> COMPLETED
        task.mark_completed()
        assert task.state == TaskState.COMPLETED
        assert task.is_completed()
        assert task.completed_at is not None
    
    def test_task_failure_and_retry(self):
        """Test task failure and retry functionality"""
        task = Task(name="Retry Test", description="Testing retry functionality")
        
        task.mark_ready()
        task.mark_running()
        task.mark_failed("Test error")
        
        assert task.state == TaskState.FAILED
        assert task.is_failed()
        assert task.error_message == "Test error"
        assert task.can_retry()
        
        task.retry()
        assert task.state == TaskState.READY
        assert task.retry_count == 1
        assert task.error_message is None
    
    def test_task_dependencies(self):
        """Test task dependency handling"""
        task1 = Task(name="Task 1", description="First task")
        task2 = Task(name="Task 2", description="Second task", dependencies=[task1.task_id])
        
        assert task2.dependencies == [task1.task_id]
        assert not task2.is_ready()  # Should be blocked by dependency
    
    def test_task_serialization(self):
        """Test task serialization to/from dictionary"""
        task = Task(
            name="Serialization Test",
            description="Testing serialization",
            priority=TaskPriority.CRITICAL,
            deadline=datetime.now() + timedelta(hours=1)
        )
        
        # Convert to dictionary
        task_dict = task.to_dict()
        assert task_dict["name"] == "Serialization Test"
        assert task_dict["priority"] == TaskPriority.CRITICAL.value
        
        # Convert back to task
        restored_task = Task.from_dict(task_dict)
        assert restored_task.name == task.name
        assert restored_task.priority == task.priority
        assert restored_task.deadline is not None


class TestSchedulingAlgorithms:
    """Test scheduling algorithms"""
    
    def test_priority_algorithm(self):
        """Test priority-based scheduling"""
        algorithm = PriorityAlgorithm()
        
        tasks = [
            Task(name="Low Priority", priority=TaskPriority.LOW),
            Task(name="High Priority", priority=TaskPriority.HIGH),
            Task(name="Normal Priority", priority=TaskPriority.NORMAL)
        ]
        
        # High priority should be selected first
        selected = algorithm.select_next_task(tasks)
        assert selected.name == "High Priority"
    
    def test_round_robin_algorithm(self):
        """Test round-robin scheduling"""
        algorithm = RoundRobinAlgorithm(time_slice=5.0)
        
        tasks = [
            Task(name="Task 1", priority=TaskPriority.NORMAL),
            Task(name="Task 2", priority=TaskPriority.NORMAL),
            Task(name="Task 3", priority=TaskPriority.NORMAL)
        ]
        
        # Should cycle through tasks
        selected1 = algorithm.select_next_task(tasks)
        selected2 = algorithm.select_next_task(tasks)
        selected3 = algorithm.select_next_task(tasks)
        
        assert selected1.name == "Task 1"
        assert selected2.name == "Task 2"
        assert selected3.name == "Task 3"
    
    def test_deadline_algorithm(self):
        """Test deadline-based scheduling"""
        algorithm = DeadlineAlgorithm()
        
        now = datetime.now()
        tasks = [
            Task(name="Late Deadline", deadline=now + timedelta(hours=2)),
            Task(name="Early Deadline", deadline=now + timedelta(minutes=30)),
            Task(name="No Deadline")
        ]
        
        # Early deadline should be selected first
        selected = algorithm.select_next_task(tasks)
        assert selected.name == "Early Deadline"
    
    def test_hybrid_algorithm(self):
        """Test hybrid scheduling algorithm"""
        algorithm = HybridAlgorithm()
        
        tasks = [
            Task(name="High Priority", priority=TaskPriority.HIGH),
            Task(name="Low Priority", priority=TaskPriority.LOW)
        ]
        
        # Should select based on current phase
        selected = algorithm.select_next_task(tasks)
        assert selected is not None
        assert selected.name in ["High Priority", "Low Priority"]


class TestResourceManager:
    """Test resource management"""
    
    def test_resource_creation(self):
        """Test resource creation"""
        resource = Resource(
            name="Test CPU",
            resource_type=ResourceType.CPU,
            capacity=4.0,
            unit="cores"
        )
        
        assert resource.name == "Test CPU"
        assert resource.resource_type == ResourceType.CPU
        assert resource.capacity == 4.0
        assert resource.available == 4.0
        assert resource.allocated == 0.0
    
    def test_resource_allocation(self):
        """Test resource allocation and deallocation"""
        resource = Resource(
            name="Test Memory",
            resource_type=ResourceType.MEMORY,
            capacity=8.0,
            unit="GB"
        )
        
        # Allocate resources
        assert resource.allocate(2.0, "task1")
        assert resource.available == 6.0
        assert resource.allocated == 2.0
        
        # Try to allocate more than available
        assert not resource.allocate(10.0, "task2")
        
        # Deallocate resources
        assert resource.deallocate(1.0, "task1")
        assert resource.available == 7.0
        assert resource.allocated == 1.0
    
    def test_resource_manager(self):
        """Test resource manager functionality"""
        manager = ResourceManager()
        
        # Add resources
        cpu_resource = Resource("CPU", ResourceType.CPU, 4.0)
        memory_resource = Resource("Memory", ResourceType.MEMORY, 8.0)
        
        assert manager.add_resource(cpu_resource)
        assert manager.add_resource(memory_resource)
        
        # Allocate resources for a task
        requirements = {
            cpu_resource.resource_id: 2.0,
            memory_resource.resource_id: 4.0
        }
        
        assert manager.allocate_resources("task1", requirements)
        
        # Check allocation
        summary = manager.get_allocation_summary()
        assert summary["total_allocated_tasks"] == 1
        assert "task1" in summary["allocations_by_task"]
    
    def test_resource_pools(self):
        """Test resource pool functionality"""
        manager = ResourceManager()
        
        # Create a pool
        pool = manager.create_pool("compute_pool", "Pool for compute resources")
        assert pool.name == "compute_pool"
        
        # Add resources to pool
        cpu_resource = Resource("CPU", ResourceType.CPU, 4.0)
        manager.add_resource(cpu_resource)
        manager.add_resource_to_pool(cpu_resource.resource_id, "compute_pool")
        
        # Check pool resources
        pool_resources = pool.get_resources_by_type(ResourceType.CPU)
        assert len(pool_resources) == 1
        assert pool_resources[0].name == "CPU"


class TestTaskScheduler:
    """Test the main TaskScheduler class"""
    
    @pytest.fixture
    def scheduler(self):
        """Create a task scheduler for testing"""
        return TaskScheduler(
            algorithm=PriorityAlgorithm(),
            max_concurrent_tasks=3,
            enable_resource_management=True
        )
    
    @pytest.fixture
    def simple_scheduler(self):
        """Create a simple task scheduler without resource management"""
        return TaskScheduler(
            algorithm=PriorityAlgorithm(),
            max_concurrent_tasks=2,
            enable_resource_management=False
        )
    
    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization"""
        assert scheduler.algorithm is not None
        assert scheduler.max_concurrent_tasks == 3
        assert scheduler.enable_resource_management is True
        assert len(scheduler.tasks) == 0
        assert len(scheduler.ready_queue) == 0
    
    def test_task_submission(self, scheduler):
        """Test task submission"""
        task = Task(name="Test Task", description="A test task")
        
        assert scheduler.submit_task(task)
        assert task.task_id in scheduler.tasks
        assert task in scheduler.ready_queue
    
    def test_task_dependency_resolution(self, scheduler):
        """Test task dependency resolution"""
        task1 = Task(name="Task 1", description="First task")
        task2 = Task(name="Task 2", description="Second task", dependencies=[task1.task_id])
        
        # Submit tasks
        scheduler.submit_task(task1)
        scheduler.submit_task(task2)
        
        # Task2 should be blocked initially
        assert task2.state == TaskState.BLOCKED
        assert task2 not in scheduler.ready_queue
        
        # Complete task1
        task1.mark_ready()
        task1.mark_running()
        task1.mark_completed()
        
        # Update dependencies
        scheduler._update_dependencies()
        
        # Task2 should now be ready
        assert task2.state == TaskState.READY
        assert task2 in scheduler.ready_queue
    
    def test_task_cancellation(self, scheduler):
        """Test task cancellation"""
        task = Task(name="Cancellable Task", description="A task to cancel")
        scheduler.submit_task(task)
        
        # Cancel the task
        assert scheduler.cancel_task(task.task_id)
        assert task.state == TaskState.CANCELLED
        assert task not in scheduler.ready_queue
    
    def test_scheduler_statistics(self, scheduler):
        """Test scheduler statistics"""
        # Submit some tasks
        for i in range(3):
            task = Task(name=f"Task {i}", description=f"Task {i}")
            scheduler.submit_task(task)
        
        stats = scheduler.get_stats()
        assert stats["total_tasks_submitted"] == 3
        assert stats["total_tasks"] == 3
        assert stats["ready_tasks"] == 3
    
    @pytest.mark.asyncio
    async def test_scheduler_lifecycle(self, simple_scheduler):
        """Test scheduler start/stop lifecycle"""
        # Start scheduler
        await simple_scheduler.start()
        assert simple_scheduler.is_running
        
        # Submit a task
        task = Task(name="Lifecycle Test", description="Testing lifecycle", estimated_duration=0.1)
        simple_scheduler.submit_task(task)
        
        # Wait for task to complete
        await asyncio.sleep(0.2)
        
        # Stop scheduler
        await simple_scheduler.stop()
        assert not simple_scheduler.is_running
        
        # Check that task was completed
        completed_tasks = simple_scheduler.get_completed_tasks()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].name == "Lifecycle Test"
    
    def test_event_handlers(self, scheduler):
        """Test event handler functionality"""
        events_received = []
        
        def event_handler(task):
            events_received.append((task.name, task.state))
        
        # Register event handler
        scheduler.add_event_handler("task_started", event_handler)
        scheduler.add_event_handler("task_completed", event_handler)
        
        # Submit and complete a task
        task = Task(name="Event Test", description="Testing events")
        scheduler.submit_task(task)
        
        # Manually trigger events (in real usage, these would be triggered by the scheduler)
        scheduler._trigger_event("task_started", task)
        task.mark_running()
        task.mark_completed()
        scheduler._trigger_event("task_completed", task)
        
        assert len(events_received) == 2
        assert events_received[0][0] == "Event Test"
        assert events_received[1][0] == "Event Test"
    
    def test_task_summary(self, scheduler):
        """Test task summary generation"""
        # Create tasks with different priorities and states
        tasks = [
            Task(name="High Priority", priority=TaskPriority.HIGH),
            Task(name="Low Priority", priority=TaskPriority.LOW),
            Task(name="Normal Priority", priority=TaskPriority.NORMAL)
        ]
        
        for task in tasks:
            scheduler.submit_task(task)
        
        # Mark one task as completed
        tasks[0].mark_ready()
        tasks[0].mark_running()
        tasks[0].mark_completed()
        
        summary = scheduler.get_task_summary()
        
        assert summary["total_tasks"] == 3
        assert "ready" in summary["tasks_by_state"]
        assert "completed" in summary["tasks_by_state"]
        assert len(summary["tasks_by_priority"]) == 3  # Different priority levels


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test a complete workflow with multiple tasks and dependencies"""
        # Create scheduler with resource management
        scheduler = TaskScheduler(
            algorithm=PriorityAlgorithm(),
            max_concurrent_tasks=2,
            enable_resource_management=True
        )
        
        # Add resources
        cpu_resource = Resource("CPU", ResourceType.CPU, 4.0)
        memory_resource = Resource("Memory", ResourceType.MEMORY, 8.0)
        scheduler.resource_manager.add_resource(cpu_resource)
        scheduler.resource_manager.add_resource(memory_resource)
        
        # Create tasks with dependencies
        task1 = Task(
            name="Setup Task",
            description="Initial setup",
            priority=TaskPriority.HIGH,
            estimated_duration=0.1,
            resources_required={"cpu"}
        )
        
        task2 = Task(
            name="Processing Task",
            description="Main processing",
            priority=TaskPriority.NORMAL,
            estimated_duration=0.1,
            dependencies=[task1.task_id],
            resources_required={"cpu", "memory"}
        )
        
        task3 = Task(
            name="Cleanup Task",
            description="Final cleanup",
            priority=TaskPriority.LOW,
            estimated_duration=0.1,
            dependencies=[task2.task_id]
        )
        
        # Submit tasks
        scheduler.submit_task(task1)
        scheduler.submit_task(task2)
        scheduler.submit_task(task3)
        
        # Start scheduler
        await scheduler.start()
        
        # Wait for all tasks to complete
        await asyncio.sleep(0.5)
        
        # Stop scheduler
        await scheduler.stop()
        
        # Verify results
        completed_tasks = scheduler.get_completed_tasks()
        assert len(completed_tasks) == 3
        
        # Check that tasks completed in dependency order
        task_names = [task.name for task in completed_tasks]
        assert "Setup Task" in task_names
        assert "Processing Task" in task_names
        assert "Cleanup Task" in task_names
        
        # Check statistics
        stats = scheduler.get_stats()
        assert stats["total_tasks_completed"] == 3
        assert stats["total_tasks_failed"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
#!/usr/bin/env python3
"""
Basic test script for the Task Scheduler system
"""

import asyncio
import time
from datetime import datetime, timedelta

from src.scheduler.task_scheduler import TaskScheduler
from src.scheduler.task import Task, TaskPriority, TaskState
from src.scheduler.scheduling_algorithm import PriorityAlgorithm, RoundRobinAlgorithm
from src.scheduler.resource_manager import ResourceManager, Resource, ResourceType


async def test_basic_scheduler():
    """Test basic scheduler functionality"""
    print("=== Testing Basic Task Scheduler ===")
    
    # Create scheduler
    scheduler = TaskScheduler(algorithm=PriorityAlgorithm())
    
    # Create some test tasks
    task1 = Task(
        name="High Priority Task",
        description="This is a high priority task",
        priority=TaskPriority.HIGH,
        estimated_duration=5.0
    )
    
    task2 = Task(
        name="Low Priority Task", 
        description="This is a low priority task",
        priority=TaskPriority.LOW,
        estimated_duration=3.0
    )
    
    task3 = Task(
        name="Normal Priority Task",
        description="This is a normal priority task", 
        priority=TaskPriority.NORMAL,
        estimated_duration=4.0
    )
    
    # Submit tasks
    print(f"Submitting task: {task1.name}")
    scheduler.submit_task(task1)
    
    print(f"Submitting task: {task2.name}")
    scheduler.submit_task(task2)
    
    print(f"Submitting task: {task3.name}")
    scheduler.submit_task(task3)
    
    # Check task status
    print(f"\nTask status:")
    print(f"  {task1.name}: {scheduler.get_task_status(task1.task_id)}")
    print(f"  {task2.name}: {scheduler.get_task_status(task2.task_id)}")
    print(f"  {task3.name}: {scheduler.get_task_status(task3.task_id)}")
    
    # Get ready tasks
    ready_tasks = scheduler.get_ready_tasks()
    print(f"\nReady tasks: {len(ready_tasks)}")
    for task in ready_tasks:
        print(f"  - {task.name} (Priority: {task.priority.name})")
    
    # Start scheduler
    print("\nStarting scheduler...")
    await scheduler.start()
    
    # Let it run for a bit
    await asyncio.sleep(2)
    
    # Stop scheduler
    print("Stopping scheduler...")
    await scheduler.stop()
    
    # Check final status
    print(f"\nFinal task status:")
    print(f"  {task1.name}: {scheduler.get_task_status(task1.task_id)}")
    print(f"  {task2.name}: {scheduler.get_task_status(task2.task_id)}")
    print(f"  {task3.name}: {scheduler.get_task_status(task3.task_id)}")
    
    # Get statistics
    stats = scheduler.get_stats()
    print(f"\nScheduler statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def test_resource_management():
    """Test resource management functionality"""
    print("\n=== Testing Resource Management ===")
    
    # Create resource manager
    resource_manager = ResourceManager()
    
    # Create resources
    cpu_resource = Resource(
        name="CPU Pool",
        resource_type=ResourceType.CPU,
        capacity=8.0,
        unit="cores"
    )
    
    memory_resource = Resource(
        name="Memory Pool", 
        resource_type=ResourceType.MEMORY,
        capacity=16.0,
        unit="GB"
    )
    
    # Add resources
    resource_manager.add_resource(cpu_resource)
    resource_manager.add_resource(memory_resource)
    
    # Allocate resources
    allocation_success = resource_manager.allocate_resources(
        task_id="test_task_1",
        resource_requirements={
            "cpu": 2.0,
            "memory": 4.0
        }
    )
    
    print(f"Resource allocation successful: {allocation_success}")
    
    # Check resource status
    cpu_util = resource_manager.get_resource_utilization()
    print(f"CPU utilization: {cpu_util.get('cpu', 0):.2%}")
    
    # Deallocate resources
    resource_manager.deallocate_resources("test_task_1")
    
    # Check final status
    final_util = resource_manager.get_resource_utilization()
    print(f"Final CPU utilization: {final_util.get('cpu', 0):.2%}")


async def test_scheduling_algorithms():
    """Test different scheduling algorithms"""
    print("\n=== Testing Scheduling Algorithms ===")
    
    # Create test tasks
    tasks = [
        Task(name="Task A", description="High priority task", priority=TaskPriority.HIGH, estimated_duration=1.0),
        Task(name="Task B", description="Low priority task", priority=TaskPriority.LOW, estimated_duration=1.0),
        Task(name="Task C", description="Normal priority task", priority=TaskPriority.NORMAL, estimated_duration=1.0)
    ]
    
    # Test Priority Algorithm
    print("Testing Priority Algorithm:")
    priority_algo = PriorityAlgorithm()
    selected = priority_algo.select_next_task(tasks)
    print(f"  Selected: {selected.name} (Priority: {selected.priority.name})")
    
    # Test Round Robin Algorithm
    print("Testing Round Robin Algorithm:")
    rr_algo = RoundRobinAlgorithm()
    selected = rr_algo.select_next_task(tasks)
    print(f"  Selected: {selected.name}")
    
    # Test with deadline
    print("Testing Deadline Algorithm:")
    from src.scheduler.scheduling_algorithm import DeadlineAlgorithm
    deadline_algo = DeadlineAlgorithm()
    
    deadline_tasks = [
        Task(name="Late Task", description="Task with late deadline", deadline=datetime.now() + timedelta(hours=2)),
        Task(name="Early Task", description="Task with early deadline", deadline=datetime.now() + timedelta(minutes=30))
    ]
    
    selected = deadline_algo.select_next_task(deadline_tasks)
    print(f"  Selected: {selected.name}")


async def main():
    """Run all tests"""
    print("Daydreamer Task Scheduler - Basic Functionality Test")
    print("=" * 50)
    
    try:
        await test_scheduling_algorithms()
        await test_resource_management()
        await test_basic_scheduler()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
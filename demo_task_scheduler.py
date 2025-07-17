#!/usr/bin/env python3
"""
Task Scheduler Demo for Daydreamer Project
This script demonstrates the capabilities of the task scheduling system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
import time

from src.scheduler.task_scheduler import TaskScheduler
from src.scheduler.task import Task, TaskPriority, TaskState
from src.scheduler.scheduling_algorithm import (
    PriorityAlgorithm, RoundRobinAlgorithm, DeadlineAlgorithm, HybridAlgorithm
)
from src.scheduler.resource_manager import Resource, ResourceType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title: str):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_task_info(task: Task):
    """Print task information"""
    print(f"  📋 {task.name}")
    print(f"     ID: {task.task_id}")
    print(f"     State: {task.state.value}")
    print(f"     Priority: {task.priority.name}")
    print(f"     Duration: {task.estimated_duration}s")
    if task.deadline:
        print(f"     Deadline: {task.deadline.strftime('%H:%M:%S')}")
    if task.dependencies:
        print(f"     Dependencies: {task.dependencies}")
    print()


async def demo_basic_scheduling():
    """Demonstrate basic task scheduling"""
    print_separator("Basic Task Scheduling Demo")
    
    # Create scheduler with priority algorithm
    scheduler = TaskScheduler(
        algorithm=PriorityAlgorithm(),
        max_concurrent_tasks=2,
        enable_resource_management=False
    )
    
    # Create tasks with different priorities
    tasks = [
        Task(
            name="High Priority Task",
            description="This should run first",
            priority=TaskPriority.HIGH,
            estimated_duration=1.0
        ),
        Task(
            name="Low Priority Task",
            description="This should run second",
            priority=TaskPriority.LOW,
            estimated_duration=1.0
        ),
        Task(
            name="Normal Priority Task",
            description="This should run third",
            priority=TaskPriority.NORMAL,
            estimated_duration=1.0
        )
    ]
    
    print("📝 Creating tasks...")
    for task in tasks:
        print_task_info(task)
        scheduler.submit_task(task)
    
    print("🚀 Starting scheduler...")
    await scheduler.start()
    
    # Wait for tasks to complete
    await asyncio.sleep(4.0)
    
    print("🛑 Stopping scheduler...")
    await scheduler.stop()
    
    # Show results
    print("\n📊 Results:")
    completed_tasks = scheduler.get_completed_tasks()
    for task in completed_tasks:
        print(f"  ✅ {task.name} - Completed in {task.get_execution_time():.2f}s")
    
    # Show statistics
    stats = scheduler.get_stats()
    print(f"\n📈 Statistics:")
    print(f"  Total tasks submitted: {stats['total_tasks_submitted']}")
    print(f"  Total tasks completed: {stats['total_tasks_completed']}")
    print(f"  Average completion time: {stats['average_completion_time']:.2f}s")


async def demo_dependency_resolution():
    """Demonstrate task dependency resolution"""
    print_separator("Task Dependency Resolution Demo")
    
    scheduler = TaskScheduler(
        algorithm=PriorityAlgorithm(),
        max_concurrent_tasks=3,
        enable_resource_management=False
    )
    
    # Create tasks with dependencies
    setup_task = Task(
        name="Setup Database",
        description="Initialize database connection",
        priority=TaskPriority.HIGH,
        estimated_duration=0.5
    )
    
    process_task = Task(
        name="Process Data",
        description="Process data from database",
        priority=TaskPriority.NORMAL,
        estimated_duration=1.0,
        dependencies=[setup_task.task_id]
    )
    
    cleanup_task = Task(
        name="Cleanup Resources",
        description="Clean up database connection",
        priority=TaskPriority.LOW,
        estimated_duration=0.5,
        dependencies=[process_task.task_id]
    )
    
    print("📝 Creating tasks with dependencies...")
    tasks = [setup_task, process_task, cleanup_task]
    for task in tasks:
        print_task_info(task)
        scheduler.submit_task(task)
    
    print("🚀 Starting scheduler...")
    await scheduler.start()
    
    # Wait for all tasks to complete
    await asyncio.sleep(3.0)
    
    print("🛑 Stopping scheduler...")
    await scheduler.stop()
    
    # Show execution order
    print("\n📊 Execution Order:")
    completed_tasks = scheduler.get_completed_tasks()
    for i, task in enumerate(completed_tasks, 1):
        print(f"  {i}. {task.name} - {task.get_execution_time():.2f}s")


async def demo_resource_management():
    """Demonstrate resource management"""
    print_separator("Resource Management Demo")
    
    scheduler = TaskScheduler(
        algorithm=PriorityAlgorithm(),
        max_concurrent_tasks=3,
        enable_resource_management=True
    )
    
    # Add resources
    cpu_resource = Resource("CPU", ResourceType.CPU, 2.0, "cores")
    memory_resource = Resource("Memory", ResourceType.MEMORY, 4.0, "GB")
    
    scheduler.resource_manager.add_resource(cpu_resource)
    scheduler.resource_manager.add_resource(memory_resource)
    
    print("🔧 Available Resources:")
    print(f"  CPU: {cpu_resource.capacity} cores")
    print(f"  Memory: {memory_resource.capacity} GB")
    
    # Create tasks with resource requirements
    tasks = [
        Task(
            name="CPU Intensive Task",
            description="Requires CPU resources",
            priority=TaskPriority.HIGH,
            estimated_duration=1.0,
            resources_required={"cpu"}
        ),
        Task(
            name="Memory Intensive Task",
            description="Requires memory resources",
            priority=TaskPriority.NORMAL,
            estimated_duration=1.0,
            resources_required={"memory"}
        ),
        Task(
            name="Both Resources Task",
            description="Requires both CPU and memory",
            priority=TaskPriority.LOW,
            estimated_duration=1.0,
            resources_required={"cpu", "memory"}
        )
    ]
    
    print("\n📝 Creating tasks with resource requirements...")
    for task in tasks:
        print_task_info(task)
        scheduler.submit_task(task)
    
    print("🚀 Starting scheduler...")
    await scheduler.start()
    
    # Wait for tasks to complete
    await asyncio.sleep(4.0)
    
    print("🛑 Stopping scheduler...")
    await scheduler.stop()
    
    # Show resource utilization
    print("\n📊 Resource Utilization:")
    resource_stats = scheduler.resource_manager.get_stats()
    print(f"  Total allocations: {resource_stats['total_allocations']}")
    print(f"  Total deallocations: {resource_stats['total_deallocations']}")
    
    # Show final resource state
    print("\n🔧 Final Resource State:")
    for resource in [cpu_resource, memory_resource]:
        print(f"  {resource.name}: {resource.available}/{resource.capacity} {resource.unit} available")


async def demo_different_algorithms():
    """Demonstrate different scheduling algorithms"""
    print_separator("Scheduling Algorithms Comparison Demo")
    
    algorithms = [
        ("Priority Algorithm", PriorityAlgorithm()),
        ("Round Robin Algorithm", RoundRobinAlgorithm(time_slice=0.5)),
        ("Deadline Algorithm", DeadlineAlgorithm()),
        ("Hybrid Algorithm", HybridAlgorithm())
    ]
    
    for algorithm_name, algorithm in algorithms:
        print(f"\n🔄 Testing {algorithm_name}...")
        
        scheduler = TaskScheduler(
            algorithm=algorithm,
            max_concurrent_tasks=2,
            enable_resource_management=False
        )
        
        # Create tasks with different characteristics
        now = datetime.now()
        tasks = [
            Task(
                name="Task A",
                description="High priority, early deadline",
                priority=TaskPriority.HIGH,
                deadline=now + timedelta(seconds=5),
                estimated_duration=0.5
            ),
            Task(
                name="Task B",
                description="Low priority, late deadline",
                priority=TaskPriority.LOW,
                deadline=now + timedelta(seconds=10),
                estimated_duration=0.5
            ),
            Task(
                name="Task C",
                description="Normal priority, no deadline",
                priority=TaskPriority.NORMAL,
                estimated_duration=0.5
            )
        ]
        
        for task in tasks:
            scheduler.submit_task(task)
        
        await scheduler.start()
        await asyncio.sleep(2.0)
        await scheduler.stop()
        
        # Show execution order
        completed_tasks = scheduler.get_completed_tasks()
        print(f"  Execution order: {[task.name for task in completed_tasks]}")
        
        # Show algorithm statistics
        algo_stats = algorithm.get_stats()
        print(f"  Tasks scheduled: {algo_stats['tasks_scheduled']}")
        print(f"  Average scheduling time: {algo_stats['average_scheduling_time']:.4f}s")


async def demo_event_handlers():
    """Demonstrate event handling"""
    print_separator("Event Handling Demo")
    
    scheduler = TaskScheduler(
        algorithm=PriorityAlgorithm(),
        max_concurrent_tasks=2,
        enable_resource_management=False
    )
    
    # Track events
    events = []
    
    def task_started_handler(task):
        events.append(f"Started: {task.name}")
        print(f"  🚀 Event: Task '{task.name}' started")
    
    def task_completed_handler(task):
        events.append(f"Completed: {task.name}")
        print(f"  ✅ Event: Task '{task.name}' completed")
    
    def task_failed_handler(task):
        events.append(f"Failed: {task.name}")
        print(f"  ❌ Event: Task '{task.name}' failed: {task.error_message}")
    
    # Register event handlers
    scheduler.add_event_handler("task_started", task_started_handler)
    scheduler.add_event_handler("task_completed", task_completed_handler)
    scheduler.add_event_handler("task_failed", task_failed_handler)
    
    # Create tasks
    tasks = [
        Task(name="Event Test 1", description="Testing events", estimated_duration=0.5),
        Task(name="Event Test 2", description="Testing events", estimated_duration=0.5)
    ]
    
    print("📝 Creating tasks for event testing...")
    for task in tasks:
        scheduler.submit_task(task)
    
    print("🚀 Starting scheduler with event handlers...")
    await scheduler.start()
    
    # Wait for tasks to complete
    await asyncio.sleep(2.0)
    
    print("🛑 Stopping scheduler...")
    await scheduler.stop()
    
    print(f"\n📊 Total events received: {len(events)}")


async def demo_task_monitoring():
    """Demonstrate task monitoring and statistics"""
    print_separator("Task Monitoring and Statistics Demo")
    
    scheduler = TaskScheduler(
        algorithm=PriorityAlgorithm(),
        max_concurrent_tasks=3,
        enable_resource_management=True
    )
    
    # Add resources
    cpu_resource = Resource("CPU", ResourceType.CPU, 2.0, "cores")
    scheduler.resource_manager.add_resource(cpu_resource)
    
    # Create various tasks
    tasks = [
        Task(
            name="Quick Task",
            description="Fast execution",
            priority=TaskPriority.HIGH,
            estimated_duration=0.3,
            resources_required={"cpu"}
        ),
        Task(
            name="Slow Task",
            description="Slow execution",
            priority=TaskPriority.LOW,
            estimated_duration=1.0,
            resources_required={"cpu"}
        ),
        Task(
            name="Medium Task",
            description="Medium execution",
            priority=TaskPriority.NORMAL,
            estimated_duration=0.5,
            resources_required={"cpu"}
        )
    ]
    
    print("📝 Creating tasks for monitoring...")
    for task in tasks:
        scheduler.submit_task(task)
    
    print("🚀 Starting scheduler...")
    await scheduler.start()
    
    # Monitor progress
    print("\n📊 Monitoring progress...")
    for i in range(5):
        stats = scheduler.get_stats()
        summary = scheduler.get_task_summary()
        
        print(f"\n  Time {i+1}:")
        print(f"    Running tasks: {stats['running_tasks']}")
        print(f"    Completed tasks: {stats['total_tasks_completed']}")
        print(f"    Ready tasks: {stats['ready_tasks']}")
        
        await asyncio.sleep(0.5)
    
    print("🛑 Stopping scheduler...")
    await scheduler.stop()
    
    # Show final statistics
    print("\n📈 Final Statistics:")
    final_stats = scheduler.get_stats()
    print(f"  Total tasks submitted: {final_stats['total_tasks_submitted']}")
    print(f"  Total tasks completed: {final_stats['total_tasks_completed']}")
    print(f"  Total tasks failed: {final_stats['total_tasks_failed']}")
    print(f"  Average completion time: {final_stats['average_completion_time']:.2f}s")
    print(f"  Scheduler uptime: {final_stats['scheduler_uptime']:.2f}s")
    
    # Show task summary
    print("\n📋 Task Summary:")
    task_summary = scheduler.get_task_summary()
    print(f"  Total tasks: {task_summary['total_tasks']}")
    print(f"  Tasks by state: {task_summary['tasks_by_state']}")
    print(f"  Overdue tasks: {len(task_summary['overdue_tasks'])}")


async def main():
    """Run all demos"""
    print("🎬 Task Scheduler Demo for Daydreamer Project")
    print("This demo showcases the capabilities of the task scheduling system.")
    
    try:
        # Run all demos
        await demo_basic_scheduling()
        await demo_dependency_resolution()
        await demo_resource_management()
        await demo_different_algorithms()
        await demo_event_handlers()
        await demo_task_monitoring()
        
        print_separator("Demo Complete")
        print("✅ All demos completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("  • Priority-based task scheduling")
        print("  • Task dependency resolution")
        print("  • Resource allocation and management")
        print("  • Multiple scheduling algorithms")
        print("  • Event handling and monitoring")
        print("  • Comprehensive statistics and reporting")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
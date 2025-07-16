"""
Scheduling Algorithm module for Daydreamer Project
This module provides different scheduling algorithms for task execution.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import logging

from .task import Task, TaskPriority, TaskState

logger = logging.getLogger(__name__)


class SchedulingAlgorithm(ABC):
    """
    Abstract base class for scheduling algorithms.
    
    This interface defines the contract that all scheduling algorithms
    must implement to be used by the TaskScheduler.
    """
    
    def __init__(self, name: str):
        """
        Initialize the scheduling algorithm.
        
        Args:
            name: Name of the algorithm
        """
        self.name = name
        self.stats = {
            "tasks_scheduled": 0,
            "total_scheduling_time": 0.0,
            "average_scheduling_time": 0.0
        }
    
    @abstractmethod
    def select_next_task(self, ready_tasks: List[Task]) -> Optional[Task]:
        """
        Select the next task to execute from the list of ready tasks.
        
        Args:
            ready_tasks: List of tasks that are ready for execution
            
        Returns:
            The selected task, or None if no task should be executed
        """
        pass
    
    def update_stats(self, scheduling_time: float):
        """
        Update algorithm statistics.
        
        Args:
            scheduling_time: Time taken for the last scheduling decision
        """
        self.stats["tasks_scheduled"] += 1
        self.stats["total_scheduling_time"] += scheduling_time
        self.stats["average_scheduling_time"] = (
            self.stats["total_scheduling_time"] / self.stats["tasks_scheduled"]
        )
    
    def get_stats(self) -> dict:
        """
        Get algorithm statistics.
        
        Returns:
            Dictionary containing algorithm statistics
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset algorithm statistics"""
        self.stats = {
            "tasks_scheduled": 0,
            "total_scheduling_time": 0.0,
            "average_scheduling_time": 0.0
        }


class RoundRobinAlgorithm(SchedulingAlgorithm):
    """
    Round-robin scheduling algorithm.
    
    This algorithm cycles through tasks in a round-robin fashion,
    giving each task equal time slices.
    """
    
    def __init__(self, time_slice: float = 10.0):
        """
        Initialize round-robin algorithm.
        
        Args:
            time_slice: Time slice allocated to each task (seconds)
        """
        super().__init__("Round Robin")
        self.time_slice = time_slice
        self.current_index = 0
        self.last_execution_time = {}  # task_id -> last execution time
    
    def select_next_task(self, ready_tasks: List[Task]) -> Optional[Task]:
        """
        Select the next task using round-robin scheduling.
        
        Args:
            ready_tasks: List of tasks that are ready for execution
            
        Returns:
            The selected task, or None if no task should be executed
        """
        if not ready_tasks:
            return None
        
        current_time = datetime.now()
        
        # Filter tasks that haven't exceeded their time slice
        eligible_tasks = []
        for task in ready_tasks:
            last_exec = self.last_execution_time.get(task.task_id)
            if last_exec is None:
                eligible_tasks.append(task)
            elif (current_time - last_exec).total_seconds() >= self.time_slice:
                eligible_tasks.append(task)
        
        if not eligible_tasks:
            # If no tasks are eligible, reset and use all ready tasks
            eligible_tasks = ready_tasks
            self.last_execution_time.clear()
        
        # Select task in round-robin order
        if self.current_index >= len(eligible_tasks):
            self.current_index = 0
        
        selected_task = eligible_tasks[self.current_index]
        self.current_index = (self.current_index + 1) % len(eligible_tasks)
        
        # Update last execution time
        self.last_execution_time[selected_task.task_id] = current_time
        
        logger.debug(f"Round-robin selected task: {selected_task.name}")
        return selected_task


class PriorityAlgorithm(SchedulingAlgorithm):
    """
    Priority-based scheduling algorithm.
    
    This algorithm selects tasks based on their priority levels,
    with higher priority tasks being selected first.
    """
    
    def __init__(self, aging_factor: float = 0.1):
        """
        Initialize priority algorithm.
        
        Args:
            aging_factor: Factor to increase priority of waiting tasks
        """
        super().__init__("Priority Based")
        self.aging_factor = aging_factor
        self.task_wait_times = {}  # task_id -> wait time
    
    def select_next_task(self, ready_tasks: List[Task]) -> Optional[Task]:
        """
        Select the next task using priority-based scheduling.
        
        Args:
            ready_tasks: List of tasks that are ready for execution
            
        Returns:
            The selected task, or None if no task should be executed
        """
        if not ready_tasks:
            return None
        
        current_time = datetime.now()
        
        # Calculate effective priority for each task
        task_priorities = []
        for task in ready_tasks:
            # Get base priority
            base_priority = task.priority.value
            
            # Apply aging (increase priority based on wait time)
            wait_time = self.task_wait_times.get(task.task_id, 0.0)
            aged_priority = base_priority + (wait_time * self.aging_factor)
            
            task_priorities.append((task, aged_priority))
        
        # Sort by effective priority (highest first)
        task_priorities.sort(key=lambda x: x[1], reverse=True)
        
        selected_task = task_priorities[0][0]
        
        # Update wait times
        for task in ready_tasks:
            if task.task_id not in self.task_wait_times:
                self.task_wait_times[task.task_id] = 0.0
            else:
                self.task_wait_times[task.task_id] += 1.0
        
        # Reset wait time for selected task
        self.task_wait_times[selected_task.task_id] = 0.0
        
        logger.debug(f"Priority algorithm selected task: {selected_task.name} "
                    f"(priority: {selected_task.priority.name})")
        return selected_task


class DeadlineAlgorithm(SchedulingAlgorithm):
    """
    Deadline-based scheduling algorithm (Earliest Deadline First).
    
    This algorithm selects tasks based on their deadlines,
    with tasks having earlier deadlines being selected first.
    """
    
    def __init__(self, deadline_weight: float = 1.0, priority_weight: float = 0.3):
        """
        Initialize deadline algorithm.
        
        Args:
            deadline_weight: Weight given to deadline proximity
            priority_weight: Weight given to task priority
        """
        super().__init__("Deadline Based")
        self.deadline_weight = deadline_weight
        self.priority_weight = priority_weight
    
    def select_next_task(self, ready_tasks: List[Task]) -> Optional[Task]:
        """
        Select the next task using deadline-based scheduling.
        
        Args:
            ready_tasks: List of tasks that are ready for execution
            
        Returns:
            The selected task, or None if no task should be executed
        """
        if not ready_tasks:
            return None
        
        current_time = datetime.now()
        
        # Calculate deadline scores for each task
        task_scores = []
        for task in ready_tasks:
            score = 0.0
            
            # Deadline component
            if task.deadline:
                remaining_time = (task.deadline - current_time).total_seconds()
                if remaining_time <= 0:
                    # Task is overdue, give it very high priority
                    score += 1000.0
                else:
                    # Normal deadline scoring (closer deadline = higher score)
                    score += self.deadline_weight / (remaining_time + 1.0)
            else:
                # No deadline, use a default score
                score += 0.1
            
            # Priority component
            score += self.priority_weight * task.priority.value
            
            task_scores.append((task, score))
        
        # Sort by score (highest first)
        task_scores.sort(key=lambda x: x[1], reverse=True)
        
        selected_task = task_scores[0][0]
        
        logger.debug(f"Deadline algorithm selected task: {selected_task.name} "
                    f"(deadline: {selected_task.deadline}, score: {task_scores[0][1]:.2f})")
        return selected_task


class HybridAlgorithm(SchedulingAlgorithm):
    """
    Hybrid scheduling algorithm that combines multiple strategies.
    
    This algorithm uses a combination of priority, deadline, and
    round-robin scheduling based on task characteristics.
    """
    
    def __init__(self):
        """Initialize hybrid algorithm"""
        super().__init__("Hybrid")
        self.priority_algorithm = PriorityAlgorithm()
        self.deadline_algorithm = DeadlineAlgorithm()
        self.round_robin_algorithm = RoundRobinAlgorithm()
        self.current_phase = "priority"  # priority, deadline, round_robin
        self.phase_counter = 0
        self.phase_length = 10  # Number of tasks per phase
    
    def select_next_task(self, ready_tasks: List[Task]) -> Optional[Task]:
        """
        Select the next task using hybrid scheduling.
        
        Args:
            ready_tasks: List of tasks that are ready for execution
            
        Returns:
            The selected task, or None if no task should be executed
        """
        if not ready_tasks:
            return None
        
        # Determine which algorithm to use based on current phase
        if self.current_phase == "priority":
            selected_task = self.priority_algorithm.select_next_task(ready_tasks)
        elif self.current_phase == "deadline":
            selected_task = self.deadline_algorithm.select_next_task(ready_tasks)
        else:  # round_robin
            selected_task = self.round_robin_algorithm.select_next_task(ready_tasks)
        
        # Update phase counter and switch phases if needed
        self.phase_counter += 1
        if self.phase_counter >= self.phase_length:
            self.phase_counter = 0
            self._switch_phase()
        
        logger.debug(f"Hybrid algorithm selected task: {selected_task.name} "
                    f"(phase: {self.current_phase})")
        return selected_task
    
    def _switch_phase(self):
        """Switch to the next scheduling phase"""
        if self.current_phase == "priority":
            self.current_phase = "deadline"
        elif self.current_phase == "deadline":
            self.current_phase = "round_robin"
        else:  # round_robin
            self.current_phase = "priority"
        
        logger.debug(f"Hybrid algorithm switched to {self.current_phase} phase")
    
    def get_stats(self) -> dict:
        """
        Get combined statistics from all algorithms.
        
        Returns:
            Dictionary containing combined statistics
        """
        stats = super().get_stats()
        stats.update({
            "priority_stats": self.priority_algorithm.get_stats(),
            "deadline_stats": self.deadline_algorithm.get_stats(),
            "round_robin_stats": self.round_robin_algorithm.get_stats(),
            "current_phase": self.current_phase
        })
        return stats
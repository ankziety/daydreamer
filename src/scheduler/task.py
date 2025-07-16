"""
Task module for Daydreamer Project
This module defines the Task class and related enums for task scheduling.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class TaskState(Enum):
    """Task execution states"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


@dataclass
class Task:
    """
    Represents a task that can be scheduled and executed by the scheduler.
    
    Attributes:
        task_id: Unique identifier for the task
        name: Human-readable name for the task
        description: Detailed description of what the task does
        priority: Priority level of the task
        deadline: When the task must be completed by
        estimated_duration: Estimated time to complete the task (seconds)
        dependencies: List of task IDs that must complete before this task
        agent_id: ID of the agent responsible for this task
        resources_required: Set of resource types required by this task
        data: Additional data associated with the task
        created_at: When the task was created
        started_at: When the task started execution
        completed_at: When the task completed
        state: Current state of the task
        retry_count: Number of times the task has been retried
        max_retries: Maximum number of retry attempts
        error_message: Error message if task failed
    """
    
    name: str
    description: str
    priority: TaskPriority = TaskPriority.NORMAL
    deadline: Optional[datetime] = None
    estimated_duration: float = 60.0  # seconds
    dependencies: List[str] = field(default_factory=list)
    agent_id: Optional[str] = None
    resources_required: Set[str] = field(default_factory=set)
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Auto-generated fields
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    state: TaskState = TaskState.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate task configuration after initialization"""
        if self.estimated_duration <= 0:
            raise ValueError("Estimated duration must be positive")
        
        if self.priority not in TaskPriority:
            raise ValueError(f"Invalid priority: {self.priority}")
        
        if self.deadline and self.deadline <= datetime.now():
            logger.warning(f"Task {self.name} has a deadline in the past")
    
    def is_ready(self) -> bool:
        """
        Check if the task is ready to be executed.
        
        Returns:
            True if the task is in READY state and all dependencies are met
        """
        return self.state == TaskState.READY
    
    def is_blocked(self) -> bool:
        """
        Check if the task is blocked by dependencies.
        
        Returns:
            True if the task is in BLOCKED state
        """
        return self.state == TaskState.BLOCKED
    
    def is_completed(self) -> bool:
        """
        Check if the task has completed successfully.
        
        Returns:
            True if the task is in COMPLETED state
        """
        return self.state == TaskState.COMPLETED
    
    def is_failed(self) -> bool:
        """
        Check if the task has failed.
        
        Returns:
            True if the task is in FAILED state
        """
        return self.state == TaskState.FAILED
    
    def is_overdue(self) -> bool:
        """
        Check if the task has passed its deadline.
        
        Returns:
            True if the task has a deadline and it has passed
        """
        if not self.deadline:
            return False
        return datetime.now() > self.deadline and not self.is_completed()
    
    def get_remaining_time(self) -> Optional[float]:
        """
        Get the remaining time until deadline.
        
        Returns:
            Remaining time in seconds, or None if no deadline
        """
        if not self.deadline:
            return None
        
        remaining = (self.deadline - datetime.now()).total_seconds()
        return max(0, remaining)
    
    def get_execution_time(self) -> Optional[float]:
        """
        Get the actual execution time of the task.
        
        Returns:
            Execution time in seconds, or None if not completed
        """
        if not self.started_at or not self.completed_at:
            return None
        
        return (self.completed_at - self.started_at).total_seconds()
    
    def mark_ready(self):
        """Mark the task as ready for execution"""
        if self.state == TaskState.PENDING:
            self.state = TaskState.READY
            logger.debug(f"Task {self.name} marked as ready")
    
    def mark_running(self):
        """Mark the task as running"""
        if self.state == TaskState.READY:
            self.state = TaskState.RUNNING
            self.started_at = datetime.now()
            logger.debug(f"Task {self.name} started running")
    
    def mark_completed(self):
        """Mark the task as completed successfully"""
        if self.state == TaskState.RUNNING:
            self.state = TaskState.COMPLETED
            self.completed_at = datetime.now()
            logger.debug(f"Task {self.name} completed successfully")
    
    def mark_failed(self, error_message: str = None):
        """Mark the task as failed"""
        if self.state == TaskState.RUNNING:
            self.state = TaskState.FAILED
            self.completed_at = datetime.now()
            self.error_message = error_message
            logger.error(f"Task {self.name} failed: {error_message}")
    
    def mark_blocked(self):
        """Mark the task as blocked by dependencies"""
        if self.state in [TaskState.PENDING, TaskState.READY]:
            self.state = TaskState.BLOCKED
            logger.debug(f"Task {self.name} blocked by dependencies")
    
    def mark_cancelled(self):
        """Mark the task as cancelled"""
        if self.state not in [TaskState.COMPLETED, TaskState.FAILED]:
            self.state = TaskState.CANCELLED
            self.completed_at = datetime.now()
            logger.info(f"Task {self.name} cancelled")
    
    def can_retry(self) -> bool:
        """
        Check if the task can be retried.
        
        Returns:
            True if the task has failed and hasn't exceeded max retries
        """
        return (self.state == TaskState.FAILED and 
                self.retry_count < self.max_retries)
    
    def retry(self):
        """Retry the task after failure"""
        if self.can_retry():
            self.retry_count += 1
            self.state = TaskState.READY
            self.started_at = None
            self.completed_at = None
            self.error_message = None
            logger.info(f"Retrying task {self.name} (attempt {self.retry_count})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary representation.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'priority': self.priority.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'estimated_duration': self.estimated_duration,
            'dependencies': self.dependencies,
            'agent_id': self.agent_id,
            'resources_required': list(self.resources_required),
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'state': self.state.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task from a dictionary representation.
        
        Args:
            data: Dictionary containing task data
            
        Returns:
            Task instance
        """
        # Convert priority back to enum
        if 'priority' in data:
            data['priority'] = TaskPriority(data['priority'])
        
        # Convert state back to enum
        if 'state' in data:
            data['state'] = TaskState(data['state'])
        
        # Convert datetime strings back to datetime objects
        for field in ['deadline', 'created_at', 'started_at', 'completed_at']:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert resources_required back to set
        if 'resources_required' in data:
            data['resources_required'] = set(data['resources_required'])
        
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of the task"""
        return f"Task({self.name}, priority={self.priority.name}, state={self.state.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the task"""
        return (f"Task(task_id='{self.task_id}', name='{self.name}', "
                f"priority={self.priority.name}, state={self.state.value}, "
                f"agent_id='{self.agent_id}')")
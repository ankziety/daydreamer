"""
Resource Manager module for Daydreamer Project
This module provides resource allocation and management capabilities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import logging
import threading

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be managed"""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    GPU = "gpu"
    CUSTOM = "custom"


@dataclass
class Resource:
    """
    Represents a resource that can be allocated to tasks.
    
    Attributes:
        resource_id: Unique identifier for the resource
        name: Human-readable name for the resource
        resource_type: Type of the resource
        capacity: Total capacity of the resource
        available: Currently available capacity
        allocated: Currently allocated capacity
        unit: Unit of measurement for the resource
        metadata: Additional metadata about the resource
        created_at: When the resource was created
        last_updated: When the resource was last updated
    """
    
    name: str
    resource_type: ResourceType
    capacity: float
    unit: str = "units"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Auto-generated fields
    resource_id: str = field(default_factory=lambda: f"res_{datetime.now().timestamp()}")
    available: float = field(init=False)
    allocated: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize the resource after creation"""
        self.available = self.capacity
        if self.capacity <= 0:
            raise ValueError("Resource capacity must be positive")
    
    def is_available(self, amount: float = 1.0) -> bool:
        """
        Check if the specified amount is available.
        
        Args:
            amount: Amount to check for availability
            
        Returns:
            True if the amount is available
        """
        return self.available >= amount
    
    def allocate(self, amount: float, task_id: str) -> bool:
        """
        Allocate the specified amount to a task.
        
        Args:
            amount: Amount to allocate
            task_id: ID of the task requesting allocation
            
        Returns:
            True if allocation was successful
        """
        if not self.is_available(amount):
            logger.warning(f"Cannot allocate {amount} {self.unit} of {self.name} "
                          f"(available: {self.available})")
            return False
        
        self.available -= amount
        self.allocated += amount
        self.last_updated = datetime.now()
        
        logger.debug(f"Allocated {amount} {self.unit} of {self.name} to task {task_id}")
        return True
    
    def deallocate(self, amount: float, task_id: str) -> bool:
        """
        Deallocate the specified amount from a task.
        
        Args:
            amount: Amount to deallocate
            task_id: ID of the task releasing allocation
            
        Returns:
            True if deallocation was successful
        """
        if amount > self.allocated:
            logger.warning(f"Cannot deallocate {amount} {self.unit} of {self.name} "
                          f"(allocated: {self.allocated})")
            return False
        
        self.available += amount
        self.allocated -= amount
        self.last_updated = datetime.now()
        
        logger.debug(f"Deallocated {amount} {self.unit} of {self.name} from task {task_id}")
        return True
    
    def get_utilization(self) -> float:
        """
        Get the current utilization percentage.
        
        Returns:
            Utilization percentage (0.0 to 1.0)
        """
        if self.capacity == 0:
            return 0.0
        return self.allocated / self.capacity
    
    def get_availability_percentage(self) -> float:
        """
        Get the current availability percentage.
        
        Returns:
            Availability percentage (0.0 to 1.0)
        """
        if self.capacity == 0:
            return 0.0
        return self.available / self.capacity
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the resource to a dictionary representation.
        
        Returns:
            Dictionary representation of the resource
        """
        return {
            'resource_id': self.resource_id,
            'name': self.name,
            'resource_type': self.resource_type.value,
            'capacity': self.capacity,
            'available': self.available,
            'allocated': self.allocated,
            'unit': self.unit,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'utilization': self.get_utilization(),
            'availability_percentage': self.get_availability_percentage()
        }


class ResourcePool:
    """
    A pool of related resources that can be managed together.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a resource pool.
        
        Args:
            name: Name of the resource pool
            description: Description of the pool
        """
        self.name = name
        self.description = description
        self.resources: Dict[str, Resource] = {}
        self.created_at = datetime.now()
    
    def add_resource(self, resource: Resource) -> bool:
        """
        Add a resource to the pool.
        
        Args:
            resource: Resource to add
            
        Returns:
            True if added successfully
        """
        if resource.resource_id in self.resources:
            logger.warning(f"Resource {resource.resource_id} already exists in pool {self.name}")
            return False
        
        self.resources[resource.resource_id] = resource
        logger.debug(f"Added resource {resource.name} to pool {self.name}")
        return True
    
    def remove_resource(self, resource_id: str) -> bool:
        """
        Remove a resource from the pool.
        
        Args:
            resource_id: ID of the resource to remove
            
        Returns:
            True if removed successfully
        """
        if resource_id not in self.resources:
            logger.warning(f"Resource {resource_id} not found in pool {self.name}")
            return False
        
        resource = self.resources[resource_id]
        if resource.allocated > 0:
            logger.warning(f"Cannot remove resource {resource_id} with active allocations")
            return False
        
        del self.resources[resource_id]
        logger.debug(f"Removed resource {resource_id} from pool {self.name}")
        return True
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """
        Get all resources of a specific type.
        
        Args:
            resource_type: Type of resources to retrieve
            
        Returns:
            List of resources of the specified type
        """
        return [r for r in self.resources.values() if r.resource_type == resource_type]
    
    def get_total_capacity(self, resource_type: ResourceType) -> float:
        """
        Get total capacity for a resource type.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            Total capacity
        """
        return sum(r.capacity for r in self.get_resources_by_type(resource_type))
    
    def get_total_available(self, resource_type: ResourceType) -> float:
        """
        Get total available capacity for a resource type.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            Total available capacity
        """
        return sum(r.available for r in self.get_resources_by_type(resource_type))


class ResourceManager:
    """
    Manages resource allocation and deallocation for tasks.
    
    This class provides:
    - Resource allocation and deallocation
    - Resource conflict resolution
    - Resource pooling and optimization
    - Resource monitoring and reporting
    - Integration with task scheduler
    """
    
    def __init__(self):
        """Initialize the resource manager"""
        self.resources: Dict[str, Resource] = {}
        self.pools: Dict[str, ResourcePool] = {}
        self.allocations: Dict[str, Dict[str, float]] = {}  # task_id -> {resource_id: amount}
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "allocation_failures": 0,
            "deallocation_failures": 0,
            "conflicts_resolved": 0
        }
        
        logger.info("Resource Manager initialized")
    
    def add_resource(self, resource: Resource) -> bool:
        """
        Add a resource to the manager.
        
        Args:
            resource: Resource to add
            
        Returns:
            True if added successfully
        """
        with self.lock:
            if resource.resource_id in self.resources:
                logger.warning(f"Resource {resource.resource_id} already exists")
                return False
            
            self.resources[resource.resource_id] = resource
            logger.info(f"Added resource: {resource.name} ({resource.resource_type.value})")
            return True
    
    def remove_resource(self, resource_id: str) -> bool:
        """
        Remove a resource from the manager.
        
        Args:
            resource_id: ID of the resource to remove
            
        Returns:
            True if removed successfully
        """
        with self.lock:
            if resource_id not in self.resources:
                logger.warning(f"Resource {resource_id} not found")
                return False
            
            resource = self.resources[resource_id]
            if resource.allocated > 0:
                logger.warning(f"Cannot remove resource {resource_id} with active allocations")
                return False
            
            del self.resources[resource_id]
            logger.info(f"Removed resource: {resource.name}")
            return True
    
    def create_pool(self, name: str, description: str = "") -> ResourcePool:
        """
        Create a new resource pool.
        
        Args:
            name: Name of the pool
            description: Description of the pool
            
        Returns:
            Created resource pool
        """
        with self.lock:
            if name in self.pools:
                logger.warning(f"Pool {name} already exists")
                return self.pools[name]
            
            pool = ResourcePool(name, description)
            self.pools[name] = pool
            logger.info(f"Created resource pool: {name}")
            return pool
    
    def add_resource_to_pool(self, resource_id: str, pool_name: str) -> bool:
        """
        Add a resource to a pool.
        
        Args:
            resource_id: ID of the resource
            pool_name: Name of the pool
            
        Returns:
            True if added successfully
        """
        with self.lock:
            if resource_id not in self.resources:
                logger.warning(f"Resource {resource_id} not found")
                return False
            
            if pool_name not in self.pools:
                logger.warning(f"Pool {pool_name} not found")
                return False
            
            resource = self.resources[resource_id]
            pool = self.pools[pool_name]
            
            return pool.add_resource(resource)
    
    def allocate_resources(self, task_id: str, resource_requirements: Dict[str, float]) -> bool:
        """
        Allocate resources for a task.
        
        Args:
            task_id: ID of the task
            resource_requirements: Dictionary mapping resource IDs to required amounts
            
        Returns:
            True if all allocations were successful
        """
        with self.lock:
            # Check if all resources are available
            for resource_id, amount in resource_requirements.items():
                if resource_id not in self.resources:
                    logger.error(f"Resource {resource_id} not found for task {task_id}")
                    return False
                
                resource = self.resources[resource_id]
                if not resource.is_available(amount):
                    logger.warning(f"Insufficient {resource.name} for task {task_id}")
                    self.stats["allocation_failures"] += 1
                    return False
            
            # Perform allocations
            for resource_id, amount in resource_requirements.items():
                resource = self.resources[resource_id]
                if not resource.allocate(amount, task_id):
                    # Rollback previous allocations
                    self._rollback_allocations(task_id)
                    return False
            
            # Record allocations
            self.allocations[task_id] = resource_requirements.copy()
            self.stats["total_allocations"] += 1
            
            logger.info(f"Allocated resources for task {task_id}: {resource_requirements}")
            return True
    
    def deallocate_resources(self, task_id: str) -> bool:
        """
        Deallocate all resources for a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            True if deallocation was successful
        """
        with self.lock:
            if task_id not in self.allocations:
                logger.warning(f"No allocations found for task {task_id}")
                return False
            
            task_allocations = self.allocations[task_id]
            success = True
            
            for resource_id, amount in task_allocations.items():
                if resource_id in self.resources:
                    resource = self.resources[resource_id]
                    if not resource.deallocate(amount, task_id):
                        success = False
                        self.stats["deallocation_failures"] += 1
                else:
                    logger.warning(f"Resource {resource_id} not found during deallocation")
                    success = False
            
            if success:
                del self.allocations[task_id]
                self.stats["total_deallocations"] += 1
                logger.info(f"Deallocated resources for task {task_id}")
            else:
                logger.error(f"Failed to deallocate some resources for task {task_id}")
            
            return success
    
    def _rollback_allocations(self, task_id: str):
        """Rollback allocations for a task"""
        if task_id in self.allocations:
            task_allocations = self.allocations[task_id]
            for resource_id, amount in task_allocations.items():
                if resource_id in self.resources:
                    resource = self.resources[resource_id]
                    resource.deallocate(amount, task_id)
            del self.allocations[task_id]
    
    def get_available_resources(self, resource_type: Optional[ResourceType] = None) -> List[Resource]:
        """
        Get all available resources, optionally filtered by type.
        
        Args:
            resource_type: Optional resource type filter
            
        Returns:
            List of available resources
        """
        with self.lock:
            if resource_type is None:
                return [r for r in self.resources.values() if r.available > 0]
            else:
                return [r for r in self.resources.values() 
                       if r.resource_type == resource_type and r.available > 0]
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """
        Get utilization for all resources.
        
        Returns:
            Dictionary mapping resource IDs to utilization percentages
        """
        with self.lock:
            return {resource_id: resource.get_utilization() 
                   for resource_id, resource in self.resources.items()}
    
    def resolve_conflicts(self) -> int:
        """
        Resolve resource conflicts by identifying and resolving deadlocks.
        
        Returns:
            Number of conflicts resolved
        """
        with self.lock:
            conflicts_resolved = 0
            
            # Simple conflict resolution: identify tasks with overdue deadlines
            # and preempt their resources if necessary
            for task_id, allocations in self.allocations.items():
                # This is a simplified conflict resolution
                # In a real system, you'd implement more sophisticated deadlock detection
                pass
            
            self.stats["conflicts_resolved"] += conflicts_resolved
            return conflicts_resolved
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get resource manager statistics.
        
        Returns:
            Dictionary containing statistics
        """
        with self.lock:
            stats = self.stats.copy()
            stats.update({
                "total_resources": len(self.resources),
                "total_pools": len(self.pools),
                "active_allocations": len(self.allocations),
                "resource_utilization": self.get_resource_utilization()
            })
            return stats
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current allocations.
        
        Returns:
            Dictionary containing allocation summary
        """
        with self.lock:
            summary = {
                "total_allocated_tasks": len(self.allocations),
                "allocations_by_task": {},
                "resource_usage": {}
            }
            
            for task_id, allocations in self.allocations.items():
                summary["allocations_by_task"][task_id] = allocations.copy()
            
            for resource_id, resource in self.resources.items():
                summary["resource_usage"][resource_id] = {
                    "name": resource.name,
                    "type": resource.resource_type.value,
                    "capacity": resource.capacity,
                    "allocated": resource.allocated,
                    "available": resource.available,
                    "utilization": resource.get_utilization()
                }
            
            return summary
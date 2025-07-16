"""
Message Queue module for Daydreamer Project
This module provides message queuing and buffering capabilities.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any
from collections import deque
import threading
import time

from .message import Message, MessagePriority, MessageStatus

logger = logging.getLogger(__name__)


@dataclass
class QueueConfig:
    """Configuration for message queues"""
    max_size: int = 1000
    max_priority_queues: int = 5
    enable_priority_queuing: bool = True
    enable_persistence: bool = False
    flush_interval: float = 1.0  # seconds
    retry_interval: float = 5.0  # seconds
    max_retry_attempts: int = 3
    enable_compression: bool = False
    enable_encryption: bool = False


class MessageQueue:
    """
    Message queue for buffering and managing message delivery.
    
    This class provides:
    - Priority-based message queuing
    - Message buffering and persistence
    - Retry mechanisms for failed messages
    - Message filtering and routing
    - Queue monitoring and statistics
    """
    
    def __init__(self, name: str, config: Optional[QueueConfig] = None):
        """
        Initialize the message queue.
        
        Args:
            name: Name of the queue
            config: Queue configuration
        """
        self.name = name
        self.config = config or QueueConfig()
        
        # Priority queues (higher index = higher priority)
        self.priority_queues: List[deque] = [
            deque(maxlen=self.config.max_size) 
            for _ in range(self.config.max_priority_queues)
        ]
        
        # Failed messages queue
        self.failed_queue: deque = deque(maxlen=self.config.max_size)
        
        # Processing queue
        self.processing_queue: deque = deque(maxlen=self.config.max_size)
        
        # Queue state
        self.is_running = False
        self.processing_task = None
        self.retry_task = None
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            "messages_enqueued": 0,
            "messages_dequeued": 0,
            "messages_failed": 0,
            "messages_retried": 0,
            "queue_size": 0,
            "failed_queue_size": 0,
            "processing_queue_size": 0
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "message_enqueued": [],
            "message_dequeued": [],
            "message_failed": [],
            "message_retried": [],
            "queue_full": [],
            "queue_empty": []
        }
        
        logger.info(f"Message Queue '{name}' initialized")
    
    def enqueue(self, message: Message) -> bool:
        """
        Add a message to the queue.
        
        Args:
            message: Message to enqueue
            
        Returns:
            True if message was enqueued successfully
        """
        with self.lock:
            # Check if queue is full
            if self._is_full():
                logger.warning(f"Queue '{self.name}' is full, cannot enqueue message")
                self._trigger_event("queue_full", message)
                return False
            
            # Determine priority queue index
            if self.config.enable_priority_queuing:
                priority_index = min(message.priority.value - 1, len(self.priority_queues) - 1)
                self.priority_queues[priority_index].append(message)
            else:
                # Use first queue if priority queuing is disabled
                self.priority_queues[0].append(message)
            
            self.stats["messages_enqueued"] += 1
            self.stats["queue_size"] = self._get_total_size()
            
            self._trigger_event("message_enqueued", message)
            logger.debug(f"Enqueued message {message.message_id} in queue '{self.name}'")
            return True
    
    def dequeue(self) -> Optional[Message]:
        """
        Remove and return the next message from the queue.
        
        Returns:
            Next message, or None if queue is empty
        """
        with self.lock:
            # Check priority queues in order (highest priority first)
            for i in range(len(self.priority_queues) - 1, -1, -1):
                if self.priority_queues[i]:
                    message = self.priority_queues[i].popleft()
                    self.stats["messages_dequeued"] += 1
                    self.stats["queue_size"] = self._get_total_size()
                    
                    self._trigger_event("message_dequeued", message)
                    logger.debug(f"Dequeued message {message.message_id} from queue '{self.name}'")
                    return message
            
            return None
    
    def peek(self) -> Optional[Message]:
        """
        Return the next message without removing it.
        
        Returns:
            Next message, or None if queue is empty
        """
        with self.lock:
            # Check priority queues in order (highest priority first)
            for i in range(len(self.priority_queues) - 1, -1, -1):
                if self.priority_queues[i]:
                    return self.priority_queues[i][0]
            return None
    
    def add_failed_message(self, message: Message):
        """
        Add a failed message to the retry queue.
        
        Args:
            message: Failed message to retry
        """
        with self.lock:
            if message.can_retry():
                self.failed_queue.append(message)
                self.stats["messages_failed"] += 1
                self.stats["failed_queue_size"] = len(self.failed_queue)
                
                self._trigger_event("message_failed", message)
                logger.debug(f"Added failed message {message.message_id} to retry queue")
            else:
                logger.warning(f"Message {message.message_id} cannot be retried")
    
    def retry_failed_messages(self) -> int:
        """
        Retry failed messages that can be retried.
        
        Returns:
            Number of messages retried
        """
        with self.lock:
            retried_count = 0
            messages_to_retry = []
            
            # Collect messages that can be retried
            while self.failed_queue:
                message = self.failed_queue.popleft()
                if message.can_retry():
                    message.retry()
                    messages_to_retry.append(message)
                    retried_count += 1
                else:
                    # Message cannot be retried, log it
                    logger.warning(f"Message {message.message_id} exceeded max retries")
            
            # Re-enqueue retryable messages
            for message in messages_to_retry:
                if self.enqueue(message):
                    self.stats["messages_retried"] += 1
                    self._trigger_event("message_retried", message)
                else:
                    # Queue is full, put back in failed queue
                    self.failed_queue.append(message)
            
            self.stats["failed_queue_size"] = len(self.failed_queue)
            return retried_count
    
    def clear(self):
        """Clear all messages from the queue"""
        with self.lock:
            for queue in self.priority_queues:
                queue.clear()
            self.failed_queue.clear()
            self.processing_queue.clear()
            
            self.stats["queue_size"] = 0
            self.stats["failed_queue_size"] = 0
            self.stats["processing_queue_size"] = 0
            
            logger.info(f"Cleared all messages from queue '{self.name}'")
    
    def get_size(self) -> int:
        """
        Get the total number of messages in the queue.
        
        Returns:
            Total number of messages
        """
        with self.lock:
            return self._get_total_size()
    
    def get_failed_size(self) -> int:
        """
        Get the number of failed messages.
        
        Returns:
            Number of failed messages
        """
        with self.lock:
            return len(self.failed_queue)
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if queue is empty
        """
        with self.lock:
            return self._get_total_size() == 0
    
    def is_full(self) -> bool:
        """
        Check if the queue is full.
        
        Returns:
            True if queue is full
        """
        with self.lock:
            return self._is_full()
    
    def _get_total_size(self) -> int:
        """Get total size of all priority queues"""
        return sum(len(queue) for queue in self.priority_queues)
    
    def _is_full(self) -> bool:
        """Check if all priority queues are full"""
        return all(len(queue) >= queue.maxlen for queue in self.priority_queues)
    
    async def start_processing(self, processor: Callable[[Message], bool]):
        """
        Start processing messages from the queue.
        
        Args:
            processor: Function to process messages (returns True if successful)
        """
        if self.is_running:
            logger.warning(f"Queue '{self.name}' is already processing")
            return
        
        self.is_running = True
        logger.info(f"Starting message processing for queue '{self.name}'")
        
        # Start processing task
        self.processing_task = asyncio.create_task(self._processing_loop(processor))
        
        # Start retry task
        self.retry_task = asyncio.create_task(self._retry_loop())
    
    async def stop_processing(self):
        """Stop processing messages"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Cancel retry task
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"Stopped message processing for queue '{self.name}'")
    
    async def _processing_loop(self, processor: Callable[[Message], bool]):
        """Main processing loop"""
        while self.is_running:
            try:
                # Get next message
                message = self.dequeue()
                if message:
                    # Add to processing queue
                    with self.lock:
                        self.processing_queue.append(message)
                        self.stats["processing_queue_size"] = len(self.processing_queue)
                    
                    # Process the message
                    try:
                        success = processor(message)
                        if not success:
                            self.add_failed_message(message)
                    except Exception as e:
                        logger.error(f"Error processing message {message.message_id}: {e}")
                        self.add_failed_message(message)
                    finally:
                        # Remove from processing queue
                        with self.lock:
                            if message in self.processing_queue:
                                self.processing_queue.remove(message)
                                self.stats["processing_queue_size"] = len(self.processing_queue)
                else:
                    # Queue is empty, check if we should trigger event
                    if self.stats["queue_size"] == 0:
                        self._trigger_event("queue_empty", None)
                    
                    # Wait before checking again
                    await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _retry_loop(self):
        """Retry loop for failed messages"""
        while self.is_running:
            try:
                # Retry failed messages
                retried_count = self.retry_failed_messages()
                if retried_count > 0:
                    logger.info(f"Retried {retried_count} failed messages in queue '{self.name}'")
                
                # Wait before next retry cycle
                await asyncio.sleep(self.config.retry_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry loop: {e}")
                await asyncio.sleep(1)
    
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
    
    def _trigger_event(self, event_type: str, message: Optional[Message]):
        """Trigger an event"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary containing queue statistics
        """
        with self.lock:
            stats = self.stats.copy()
            stats.update({
                "queue_name": self.name,
                "is_running": self.is_running,
                "priority_queue_sizes": [len(queue) for queue in self.priority_queues],
                "config": {
                    "max_size": self.config.max_size,
                    "enable_priority_queuing": self.config.enable_priority_queuing,
                    "retry_interval": self.config.retry_interval
                }
            })
            return stats
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the queue contents.
        
        Returns:
            Dictionary containing queue summary
        """
        with self.lock:
            summary = {
                "queue_name": self.name,
                "total_messages": self._get_total_size(),
                "failed_messages": len(self.failed_queue),
                "processing_messages": len(self.processing_queue),
                "priority_breakdown": {},
                "recent_messages": []
            }
            
            # Priority breakdown
            for i, queue in enumerate(self.priority_queues):
                priority_name = f"Priority {i + 1}"
                summary["priority_breakdown"][priority_name] = len(queue)
            
            # Recent messages (last 10)
            all_messages = []
            for queue in self.priority_queues:
                all_messages.extend(queue)
            
            recent_messages = sorted(
                all_messages,
                key=lambda m: m.created_at,
                reverse=True
            )[:10]
            
            summary["recent_messages"] = [
                {
                    "message_id": msg.message_id,
                    "subject": msg.subject,
                    "type": msg.message_type.value,
                    "priority": msg.priority.value,
                    "status": msg.status.value,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in recent_messages
            ]
            
            return summary
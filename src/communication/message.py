"""
Message module for Daydreamer Project
This module defines the Message class and related enums for inter-agent communication.
"""

import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages that can be sent between agents"""
    COMMAND = "command"
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"
    PRIVATE = "private"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MessageStatus(Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class Message:
    """
    Represents a message that can be sent between agents.
    
    Attributes:
        message_id: Unique identifier for the message
        message_type: Type of the message
        source_agent_id: ID of the agent sending the message
        target_agent_id: ID of the agent receiving the message (None for broadcast)
        priority: Priority level of the message
        subject: Brief description of the message
        body: Main content of the message
        headers: Additional metadata headers
        metadata: Extended metadata for the message
        created_at: When the message was created
        expires_at: When the message expires (None for no expiration)
        status: Current delivery status
        retry_count: Number of delivery attempts
        max_retries: Maximum number of retry attempts
        error_message: Error message if delivery failed
        delivered_at: When the message was delivered
        read_at: When the message was read
    """
    
    message_type: MessageType
    source_agent_id: str
    subject: str
    body: str
    target_agent_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    # Auto-generated fields
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate message configuration after initialization"""
        if not self.source_agent_id:
            raise ValueError("Source agent ID is required")
        
        if not self.subject:
            raise ValueError("Message subject is required")
        
        if not self.body:
            raise ValueError("Message body is required")
        
        if self.message_type not in MessageType:
            raise ValueError(f"Invalid message type: {self.message_type}")
        
        if self.priority not in MessagePriority:
            raise ValueError(f"Invalid priority: {self.priority}")
        
        if self.expires_at and self.expires_at <= datetime.now():
            logger.warning(f"Message {self.subject} has an expiration time in the past")
    
    def is_expired(self) -> bool:
        """
        Check if the message has expired.
        
        Returns:
            True if the message has an expiration time and it has passed
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def is_broadcast(self) -> bool:
        """
        Check if this is a broadcast message.
        
        Returns:
            True if the message has no specific target agent
        """
        return self.target_agent_id is None
    
    def is_private(self) -> bool:
        """
        Check if this is a private message.
        
        Returns:
            True if the message has a specific target agent
        """
        return self.target_agent_id is not None
    
    def can_retry(self) -> bool:
        """
        Check if the message can be retried.
        
        Returns:
            True if the message has failed and hasn't exceeded max retries
        """
        return (self.status == MessageStatus.FAILED and 
                self.retry_count < self.max_retries and 
                not self.is_expired())
    
    def mark_sent(self):
        """Mark the message as sent"""
        if self.status == MessageStatus.PENDING:
            self.status = MessageStatus.SENT
            logger.debug(f"Message {self.message_id} marked as sent")
    
    def mark_delivered(self):
        """Mark the message as delivered"""
        if self.status in [MessageStatus.SENT, MessageStatus.PENDING]:
            self.status = MessageStatus.DELIVERED
            self.delivered_at = datetime.now()
            logger.debug(f"Message {self.message_id} marked as delivered")
    
    def mark_read(self):
        """Mark the message as read"""
        if self.status == MessageStatus.DELIVERED:
            self.status = MessageStatus.READ
            self.read_at = datetime.now()
            logger.debug(f"Message {self.message_id} marked as read")
    
    def mark_failed(self, error_message: str = None):
        """Mark the message as failed"""
        if self.status not in [MessageStatus.READ, MessageStatus.EXPIRED, MessageStatus.CANCELLED]:
            self.status = MessageStatus.FAILED
            self.error_message = error_message
            logger.error(f"Message {self.message_id} failed: {error_message}")
    
    def mark_expired(self):
        """Mark the message as expired"""
        if self.status not in [MessageStatus.READ, MessageStatus.CANCELLED]:
            self.status = MessageStatus.EXPIRED
            logger.warning(f"Message {self.message_id} expired")
    
    def mark_cancelled(self):
        """Mark the message as cancelled"""
        if self.status not in [MessageStatus.READ, MessageStatus.EXPIRED]:
            self.status = MessageStatus.CANCELLED
            logger.info(f"Message {self.message_id} cancelled")
    
    def retry(self):
        """Retry the message after failure"""
        if self.can_retry():
            self.retry_count += 1
            self.status = MessageStatus.PENDING
            self.error_message = None
            logger.info(f"Retrying message {self.message_id} (attempt {self.retry_count})")
    
    def get_delivery_time(self) -> Optional[float]:
        """
        Get the time it took to deliver the message.
        
        Returns:
            Delivery time in seconds, or None if not delivered
        """
        if not self.delivered_at:
            return None
        
        return (self.delivered_at - self.created_at).total_seconds()
    
    def get_read_time(self) -> Optional[float]:
        """
        Get the time it took for the message to be read.
        
        Returns:
            Read time in seconds, or None if not read
        """
        if not self.read_at:
            return None
        
        return (self.read_at - self.created_at).total_seconds()
    
    def add_header(self, key: str, value: str):
        """
        Add a header to the message.
        
        Args:
            key: Header key
            value: Header value
        """
        self.headers[key] = value
    
    def get_header(self, key: str, default: str = None) -> Optional[str]:
        """
        Get a header value.
        
        Args:
            key: Header key
            default: Default value if header not found
            
        Returns:
            Header value or default
        """
        return self.headers.get(key, default)
    
    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to the message.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            default: Default value if metadata not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary representation.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'source_agent_id': self.source_agent_id,
            'target_agent_id': self.target_agent_id,
            'priority': self.priority.value,
            'subject': self.subject,
            'body': self.body,
            'headers': self.headers,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error_message': self.error_message,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a message from a dictionary representation.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            Message instance
        """
        # Convert enums back from values
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        
        if 'priority' in data:
            data['priority'] = MessagePriority(data['priority'])
        
        if 'status' in data:
            data['status'] = MessageStatus(data['status'])
        
        # Convert datetime strings back to datetime objects
        for field in ['created_at', 'expires_at', 'delivered_at', 'read_at']:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """
        Convert the message to JSON string.
        
        Returns:
            JSON string representation of the message
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """
        Create a message from JSON string.
        
        Args:
            json_str: JSON string containing message data
            
        Returns:
            Message instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of the message"""
        return f"Message({self.message_type.name}, {self.subject}, {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the message"""
        return (f"Message(message_id='{self.message_id}', "
                f"type={self.message_type.name}, "
                f"subject='{self.subject}', "
                f"status={self.status.value}, "
                f"source='{self.source_agent_id}', "
                f"target='{self.target_agent_id}')")


class MessageBuilder:
    """
    Builder class for creating messages with a fluent interface.
    """
    
    def __init__(self):
        """Initialize the message builder"""
        self._message_type = MessageType.NOTIFICATION
        self._source_agent_id = None
        self._target_agent_id = None
        self._subject = ""
        self._body = ""
        self._priority = MessagePriority.NORMAL
        self._headers = {}
        self._metadata = {}
        self._expires_at = None
    
    def set_type(self, message_type: MessageType) -> 'MessageBuilder':
        """Set the message type"""
        self._message_type = message_type
        return self
    
    def set_source(self, source_agent_id: str) -> 'MessageBuilder':
        """Set the source agent ID"""
        self._source_agent_id = source_agent_id
        return self
    
    def set_target(self, target_agent_id: str) -> 'MessageBuilder':
        """Set the target agent ID"""
        self._target_agent_id = target_agent_id
        return self
    
    def set_subject(self, subject: str) -> 'MessageBuilder':
        """Set the message subject"""
        self._subject = subject
        return self
    
    def set_body(self, body: str) -> 'MessageBuilder':
        """Set the message body"""
        self._body = body
        return self
    
    def set_priority(self, priority: MessagePriority) -> 'MessageBuilder':
        """Set the message priority"""
        self._priority = priority
        return self
    
    def add_header(self, key: str, value: str) -> 'MessageBuilder':
        """Add a header"""
        self._headers[key] = value
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'MessageBuilder':
        """Add metadata"""
        self._metadata[key] = value
        return self
    
    def set_expiration(self, expires_at: datetime) -> 'MessageBuilder':
        """Set the expiration time"""
        self._expires_at = expires_at
        return self
    
    def build(self) -> Message:
        """Build and return the message"""
        return Message(
            message_type=self._message_type,
            source_agent_id=self._source_agent_id,
            target_agent_id=self._target_agent_id,
            subject=self._subject,
            body=self._body,
            priority=self._priority,
            headers=self._headers,
            metadata=self._metadata,
            expires_at=self._expires_at
        )
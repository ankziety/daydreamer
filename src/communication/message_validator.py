"""
Message Validator module for Daydreamer Project
This module provides message validation and security capabilities.
"""

import re
import hashlib
import hmac
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
import json

from .message import Message, MessageType, MessagePriority

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for message validation"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ValidationRule:
    """Rule for message validation"""
    name: str
    description: str
    validator: Callable[[Message], bool]
    error_message: str
    security_level: SecurityLevel = SecurityLevel.LOW
    enabled: bool = True


class ValidationResult:
    """Result of message validation"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether the message is valid
            errors: List of validation errors
            warnings: List of validation warnings
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.timestamp = datetime.now()
    
    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)
    
    def __str__(self) -> str:
        """String representation of validation result"""
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult({status}, {len(self.errors)} errors, {len(self.warnings)} warnings)"


class MessageValidator:
    """
    Validates messages for security and integrity.
    
    This class provides:
    - Message content validation
    - Security checks and authentication
    - Rate limiting and spam detection
    - Message integrity verification
    - Custom validation rules
    """
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """
        Initialize the message validator.
        
        Args:
            security_level: Security level for validation
        """
        self.security_level = security_level
        self.validation_rules: List[ValidationRule] = []
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.blocked_sources: set = set()
        self.allowed_sources: set = set()
        
        # Statistics
        self.stats = {
            "messages_validated": 0,
            "messages_passed": 0,
            "messages_failed": 0,
            "validation_errors": 0,
            "security_violations": 0
        }
        
        # Initialize default validation rules
        self._initialize_default_rules()
        
        logger.info(f"Message Validator initialized with security level: {security_level.name}")
    
    def _initialize_default_rules(self):
        """Initialize default validation rules"""
        # Basic validation rules
        self.add_rule(ValidationRule(
            name="required_fields",
            description="Check that all required fields are present",
            validator=self._validate_required_fields,
            error_message="Missing required fields",
            security_level=SecurityLevel.LOW
        ))
        
        self.add_rule(ValidationRule(
            name="message_size",
            description="Check message size limits",
            validator=self._validate_message_size,
            error_message="Message size exceeds limits",
            security_level=SecurityLevel.LOW
        ))
        
        self.add_rule(ValidationRule(
            name="source_agent",
            description="Validate source agent ID",
            validator=self._validate_source_agent,
            error_message="Invalid source agent ID",
            security_level=SecurityLevel.MEDIUM
        ))
        
        self.add_rule(ValidationRule(
            name="target_agent",
            description="Validate target agent ID",
            validator=self._validate_target_agent,
            error_message="Invalid target agent ID",
            security_level=SecurityLevel.MEDIUM
        ))
        
        self.add_rule(ValidationRule(
            name="message_type",
            description="Validate message type",
            validator=self._validate_message_type,
            error_message="Invalid message type",
            security_level=SecurityLevel.LOW
        ))
        
        self.add_rule(ValidationRule(
            name="priority",
            description="Validate message priority",
            validator=self._validate_priority,
            error_message="Invalid message priority",
            security_level=SecurityLevel.LOW
        ))
        
        # Security rules (higher security levels)
        if self.security_level.value >= SecurityLevel.MEDIUM.value:
            self.add_rule(ValidationRule(
                name="rate_limiting",
                description="Check rate limiting",
                validator=self._validate_rate_limiting,
                error_message="Rate limit exceeded",
                security_level=SecurityLevel.MEDIUM
            ))
            
            self.add_rule(ValidationRule(
                name="content_safety",
                description="Check message content for safety",
                validator=self._validate_content_safety,
                error_message="Message content violates safety rules",
                security_level=SecurityLevel.MEDIUM
            ))
        
        if self.security_level.value >= SecurityLevel.HIGH.value:
            self.add_rule(ValidationRule(
                name="signature_verification",
                description="Verify message signature",
                validator=self._validate_signature,
                error_message="Message signature verification failed",
                security_level=SecurityLevel.HIGH
            ))
            
            self.add_rule(ValidationRule(
                name="encryption_check",
                description="Check message encryption",
                validator=self._validate_encryption,
                error_message="Message encryption check failed",
                security_level=SecurityLevel.HIGH
            ))
    
    def add_rule(self, rule: ValidationRule):
        """
        Add a custom validation rule.
        
        Args:
            rule: Validation rule to add
        """
        self.validation_rules.append(rule)
        logger.debug(f"Added validation rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a validation rule.
        
        Args:
            rule_name: Name of the rule to remove
            
        Returns:
            True if rule was removed
        """
        for i, rule in enumerate(self.validation_rules):
            if rule.name == rule_name:
                del self.validation_rules[i]
                logger.debug(f"Removed validation rule: {rule_name}")
                return True
        return False
    
    def validate(self, message: Message) -> ValidationResult:
        """
        Validate a message.
        
        Args:
            message: Message to validate
            
        Returns:
            Validation result
        """
        result = ValidationResult(True)
        self.stats["messages_validated"] += 1
        
        # Run all enabled validation rules
        for rule in self.validation_rules:
            if not rule.enabled:
                continue
            
            # Skip rules above current security level
            if rule.security_level.value > self.security_level.value:
                continue
            
            try:
                if not rule.validator(message):
                    result.add_error(f"{rule.name}: {rule.error_message}")
                    self.stats["validation_errors"] += 1
                    
                    # For high security violations, increment security violation counter
                    if rule.security_level.value >= SecurityLevel.HIGH.value:
                        self.stats["security_violations"] += 1
            except Exception as e:
                logger.error(f"Error in validation rule {rule.name}: {e}")
                result.add_error(f"{rule.name}: Validation error occurred")
        
        # Update statistics
        if result.is_valid:
            self.stats["messages_passed"] += 1
        else:
            self.stats["messages_failed"] += 1
        
        return result
    
    def _validate_required_fields(self, message: Message) -> bool:
        """Validate that all required fields are present"""
        required_fields = ['message_id', 'message_type', 'source_agent_id', 'subject', 'body']
        
        for field in required_fields:
            if not hasattr(message, field) or getattr(message, field) is None:
                return False
        
        return True
    
    def _validate_message_size(self, message: Message) -> bool:
        """Validate message size limits"""
        # Check body size (max 10KB)
        if len(message.body.encode('utf-8')) > 10240:
            return False
        
        # Check subject size (max 256 characters)
        if len(message.subject) > 256:
            return False
        
        # Check headers size (max 1KB total)
        headers_size = sum(len(k.encode('utf-8')) + len(v.encode('utf-8')) 
                          for k, v in message.headers.items())
        if headers_size > 1024:
            return False
        
        return True
    
    def _validate_source_agent(self, message: Message) -> bool:
        """Validate source agent ID"""
        # Check if source is blocked
        if message.source_agent_id in self.blocked_sources:
            return False
        
        # If allowed sources are specified, check if source is allowed
        if self.allowed_sources and message.source_agent_id not in self.allowed_sources:
            return False
        
        # Basic format validation (alphanumeric with hyphens and underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', message.source_agent_id):
            return False
        
        return True
    
    def _validate_target_agent(self, message: Message) -> bool:
        """Validate target agent ID"""
        # Skip validation for broadcast messages
        if message.is_broadcast():
            return True
        
        # Basic format validation (alphanumeric with hyphens and underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', message.target_agent_id):
            return False
        
        return True
    
    def _validate_message_type(self, message: Message) -> bool:
        """Validate message type"""
        return message.message_type in MessageType
    
    def _validate_priority(self, message: Message) -> bool:
        """Validate message priority"""
        return message.priority in MessagePriority
    
    def _validate_rate_limiting(self, message: Message) -> bool:
        """Validate rate limiting"""
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=1)  # 1-minute window
        
        # Clean old entries
        if message.source_agent_id in self.rate_limits:
            self.rate_limits[message.source_agent_id] = [
                t for t in self.rate_limits[message.source_agent_id]
                if t > window_start
            ]
        
        # Check rate limit (max 10 messages per minute per source)
        if message.source_agent_id in self.rate_limits:
            if len(self.rate_limits[message.source_agent_id]) >= 10:
                return False
        
        # Add current message timestamp
        if message.source_agent_id not in self.rate_limits:
            self.rate_limits[message.source_agent_id] = []
        self.rate_limits[message.source_agent_id].append(current_time)
        
        return True
    
    def _validate_content_safety(self, message: Message) -> bool:
        """Validate message content for safety"""
        # Check for potentially harmful content
        harmful_patterns = [
            r'script\s*:',  # Script injection
            r'javascript:',  # JavaScript injection
            r'<script',      # HTML script tags
            r'exec\s*\(',    # Function execution
            r'eval\s*\(',    # Code evaluation
        ]
        
        content_to_check = f"{message.subject} {message.body}".lower()
        
        for pattern in harmful_patterns:
            if re.search(pattern, content_to_check, re.IGNORECASE):
                return False
        
        return True
    
    def _validate_signature(self, message: Message) -> bool:
        """Validate message signature"""
        # This is a placeholder for signature verification
        # In a real implementation, you would verify cryptographic signatures
        
        # Check if signature header is present
        signature = message.get_header('signature')
        if not signature:
            return False
        
        # For now, just check that signature is not empty
        return len(signature) > 0
    
    def _validate_encryption(self, message: Message) -> bool:
        """Validate message encryption"""
        # This is a placeholder for encryption validation
        # In a real implementation, you would check encryption status
        
        # Check if encryption header is present
        encryption = message.get_header('encryption')
        if not encryption:
            return False
        
        # For now, just check that encryption field is not empty
        return len(encryption) > 0
    
    def block_source(self, source_agent_id: str):
        """
        Block messages from a specific source.
        
        Args:
            source_agent_id: ID of the agent to block
        """
        self.blocked_sources.add(source_agent_id)
        logger.info(f"Blocked source agent: {source_agent_id}")
    
    def unblock_source(self, source_agent_id: str):
        """
        Unblock messages from a specific source.
        
        Args:
            source_agent_id: ID of the agent to unblock
        """
        self.blocked_sources.discard(source_agent_id)
        logger.info(f"Unblocked source agent: {source_agent_id}")
    
    def allow_source(self, source_agent_id: str):
        """
        Allow messages from a specific source.
        
        Args:
            source_agent_id: ID of the agent to allow
        """
        self.allowed_sources.add(source_agent_id)
        logger.info(f"Allowed source agent: {source_agent_id}")
    
    def disallow_source(self, source_agent_id: str):
        """
        Disallow messages from a specific source.
        
        Args:
            source_agent_id: ID of the agent to disallow
        """
        self.allowed_sources.discard(source_agent_id)
        logger.info(f"Disallowed source agent: {source_agent_id}")
    
    def set_security_level(self, security_level: SecurityLevel):
        """
        Set the security level for validation.
        
        Args:
            security_level: New security level
        """
        self.security_level = security_level
        logger.info(f"Security level set to: {security_level.name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get validator statistics.
        
        Returns:
            Dictionary containing validator statistics
        """
        stats = self.stats.copy()
        stats.update({
            "security_level": self.security_level.name,
            "validation_rules": len(self.validation_rules),
            "blocked_sources": len(self.blocked_sources),
            "allowed_sources": len(self.allowed_sources),
            "rate_limited_sources": len(self.rate_limits)
        })
        return stats
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation rules and their status.
        
        Returns:
            Dictionary containing validation summary
        """
        summary = {
            "security_level": self.security_level.name,
            "total_rules": len(self.validation_rules),
            "enabled_rules": len([r for r in self.validation_rules if r.enabled]),
            "rules_by_security_level": {},
            "rules": []
        }
        
        # Group rules by security level
        for rule in self.validation_rules:
            level_name = rule.security_level.name
            if level_name not in summary["rules_by_security_level"]:
                summary["rules_by_security_level"][level_name] = 0
            summary["rules_by_security_level"][level_name] += 1
            
            summary["rules"].append({
                "name": rule.name,
                "description": rule.description,
                "security_level": rule.security_level.name,
                "enabled": rule.enabled
            })
        
        return summary
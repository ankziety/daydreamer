#!/usr/bin/env python3
"""
Configuration Management
========================

Configuration management for the Daydreamer web application.
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "Daydreamer Web Interface"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "sqlite+aiosqlite:///./daydreamer_web.db"
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # Daydreamer integration settings
    daydreamer_memory_db_path: str = "src/memory/daydreamer_memory.db"
    daydreamer_model_name: str = "llama3.2:3b"
    daydreamer_temperature: float = 0.7
    daydreamer_max_tokens: int = 2048
    daydreamer_top_p: float = 0.9
    daydreamer_verbose: bool = False
    
    # Monitoring settings
    metrics_collection_interval: int = 60  # seconds
    metrics_retention_hours: int = 24
    
    # Test settings
    test_timeout_default: int = 30  # seconds
    test_max_concurrent: int = 5
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
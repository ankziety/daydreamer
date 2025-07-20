#!/usr/bin/env python3
"""
Authentication Utilities
========================

Authentication and authorization utilities for the Daydreamer web application.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.config import Settings

settings = Settings()
security = HTTPBearer()

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

# For now, we'll use a simple authentication system
# In a production environment, you'd want proper user management

def create_mock_user_token(user_id: str = "default_user") -> str:
    """Create a mock user token for development"""
    data = {
        "sub": user_id,
        "username": "default_user",
        "role": "user"
    }
    return create_access_token(data)

def get_mock_user() -> Dict[str, Any]:
    """Get mock user data for development"""
    return {
        "user_id": "default_user",
        "username": "default_user",
        "role": "user"
    }
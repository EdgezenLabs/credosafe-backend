from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
import hashlib

def hash_password(password: str) -> str:
    # Ensure password doesn't exceed bcrypt's 72 byte limit
    if len(password.encode('utf-8')) > 72:
        # Use SHA256 for longer passwords and then hash that
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Hash the password using bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    # Ensure password doesn't exceed bcrypt's 72 byte limit during verification
    if len(plain.encode('utf-8')) > 72:
        # Use SHA256 for longer passwords and then verify that
        plain = hashlib.sha256(plain.encode('utf-8')).hexdigest()
    # Verify the password using bcrypt
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

security = HTTPBearer()

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user information from JWT token"""
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    user_email = payload.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id, 
        "email": user_email,
        "tenant_id": payload.get("tenant_id"), 
        "role": payload.get("role")
    }

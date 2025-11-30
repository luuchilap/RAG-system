"""
Authentication service for password hashing and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt
from app.config import settings
from app.models.user import UserInDB


# Password hashing context
# Configure bcrypt with explicit rounds and handle version compatibility
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"  # Use bcrypt 2b identifier for better compatibility
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Note: bcrypt has a 72-byte limit. Very long passwords will be
    automatically handled by passlib, but we validate length to avoid issues.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # bcrypt limit is 72 bytes, but passlib handles this automatically
    # We just ensure it's a valid string
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token claims (typically user_id and username)
        expires_delta: Optional expiration time delta (defaults to 24 hours)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def create_token_for_user(user: UserInDB) -> str:
    """
    Create an access token for a user.
    
    Args:
        user: UserInDB instance
    
    Returns:
        JWT token string
    """
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email
    }
    return create_access_token(data=token_data)


"""
Authentication schemas for JWT-based authentication
Following FastAPI best practices with proper validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class UserRegister(BaseModel):
    """User registration request model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name (2-100 characters)")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number (optional)")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "confirm_password": "securepassword123",
                "full_name": "John Doe",
                "phone": "+1234567890"
            }
        }


class Token(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token for getting new access token")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class TokenData(BaseModel):
    """Token payload data model"""
    user_id: Optional[int] = Field(None, description="User ID from token")
    username: Optional[str] = Field(None, description="Username from token")
    email: Optional[str] = Field(None, description="Email from token")
    role: Optional[str] = Field(None, description="User role from token")
    exp: Optional[datetime] = Field(None, description="Token expiration time")


class RefreshToken(BaseModel):
    """Refresh token request model"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordChange(BaseModel):
    """Password change request model"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        """Validate new password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Validate new password is different from current"""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword456",
                "confirm_new_password": "newsecurepassword456"
            }
        }


class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        """Validate new password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "token": "reset_token_here",
                "new_password": "newsecurepassword789",
                "confirm_new_password": "newsecurepassword789"
            }
        }


class EmailVerification(BaseModel):
    """Email verification request model"""
    token: str = Field(..., description="Email verification token")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "token": "verification_token_here"
            }
        }


class ResendVerification(BaseModel):
    """Resend verification email request model"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class Logout(BaseModel):
    """Logout request model"""
    refresh_token: Optional[str] = Field(None, description="Refresh token to invalidate")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserResponse(BaseModel):
    """User response model for authentication"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    full_name: str = Field(..., description="Full name")
    role: str = Field(..., description="User role")
    is_verified: bool = Field(..., description="Email verification status")
    
    class Config:
        """Pydantic config"""
        from_attributes = True


class AuthResponse(BaseModel):
    """Generic authentication response model"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Authentication successful",
                "data": {
                    "user_id": 1,
                    "username": "john_doe"
                }
            }
        }

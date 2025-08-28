"""
User management schemas
Following FastAPI best practices with proper validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name (2-100 characters)")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number (optional)")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar image URL (optional)")


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    
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
                "phone": "+1234567890",
                "avatar_url": "https://example.com/avatar.jpg",
                "role": "user"
            }
        }


class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format if provided"""
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "full_name": "John Smith",
                "phone": "+1987654321",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }


class UserResponse(UserBase):
    """User response model"""
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verification status")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserDetailResponse(UserResponse):
    """Detailed user response model (for admins)"""
    password_hash: Optional[str] = Field(None, description="Password hash (admin only)")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserListResponse(BaseModel):
    """User list response model"""
    users: List[UserResponse] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "users": [],
                "total_count": 0,
                "page": 1,
                "page_size": 10,
                "total_pages": 0
            }
        }


class UserQueryParams(BaseModel):
    """User query parameters model"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    username: Optional[str] = Field(None, description="Filter by username")
    email: Optional[str] = Field(None, description="Filter by email")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    status: Optional[str] = Field(None, description="Filter by status (active/inactive)")
    is_verified: Optional[bool] = Field(None, description="Filter by verification status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    search: Optional[str] = Field(None, description="Search in username, email, and full name")


class UserBulkUpdate(BaseModel):
    """Bulk user update model"""
    user_ids: List[int] = Field(..., min_items=1, description="List of user IDs to update")
    updates: UserUpdate = Field(..., description="Update data to apply")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "user_ids": [1, 2, 3],
                "updates": {
                    "is_active": False,
                    "role": "moderator"
                }
            }
        }


class UserBulkDelete(BaseModel):
    """Bulk user deletion model"""
    user_ids: List[int] = Field(..., min_items=1, description="List of user IDs to delete")
    force: bool = Field(False, description="Force deletion (bypass soft delete)")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "user_ids": [1, 2, 3],
                "force": False
            }
        }


class UserProfileUpdate(BaseModel):
    """User profile update model (for self-update)"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "full_name": "John Smith",
                "phone": "+1987654321",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }


class UserPasswordUpdate(BaseModel):
    """User password update model"""
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


class UserAvatarUpload(BaseModel):
    """User avatar upload model"""
    avatar_url: str = Field(..., max_length=500, description="Avatar image URL")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }


class UserStatistics(BaseModel):
    """User statistics model"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    verified_users: int = Field(..., description="Number of verified users")
    users_by_role: Dict[str, int] = Field(..., description="User count by role")
    new_users_today: int = Field(..., description="New users registered today")
    new_users_this_week: int = Field(..., description="New users registered this week")
    new_users_this_month: int = Field(..., description="New users registered this month")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "total_users": 1000,
                "active_users": 850,
                "verified_users": 750,
                "users_by_role": {
                    "user": 950,
                    "moderator": 40,
                    "admin": 10
                },
                "new_users_today": 15,
                "new_users_this_week": 120,
                "new_users_this_month": 500
            }
        }


class UserActivityLog(BaseModel):
    """User activity log model"""
    id: int = Field(..., description="Log entry ID")
    user_id: int = Field(..., description="User ID")
    action: str = Field(..., description="Action performed")
    details: Optional[Dict[str, Any]] = Field(None, description="Action details")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Log timestamp")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserSessionInfo(BaseModel):
    """User session information model"""
    id: int = Field(..., description="Session ID")
    user_id: int = Field(..., description="User ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    is_active: bool = Field(..., description="Session active status")
    created_at: datetime = Field(..., description="Session creation timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserFilter(BaseModel):
    """User filtering model"""
    username: Optional[str] = Field(None, description="Filter by username (partial match)")
    email: Optional[str] = Field(None, description="Filter by email (partial match)")
    role: Optional[UserRole] = Field(None, description="Filter by user role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_verified: Optional[bool] = Field(None, description="Filter by verification status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "username": "john",
                "role": "user",
                "is_active": True
            }
        }


class UserSort(BaseModel):
    """User sorting model"""
    field: str = Field(..., description="Sort field (id, username, email, created_at, last_login_at)")
    desc: bool = Field(default=False, description="Sort in descending order")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "field": "created_at",
                "desc": True
            }
        }

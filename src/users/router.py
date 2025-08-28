"""
User management router
Comprehensive user management endpoints with proper documentation
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse

from src.users.schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserRole, UserStatus, UserFilter, UserSort
)
from src.users.service import UserService
from src.users.exceptions import (
    handle_user_exception, UserNotFoundError, UserAlreadyExistsError,
    InvalidUserOperationError, InsufficientPermissionsError
)
from src.auth.dependencies import get_current_user, get_current_admin_user, get_current_moderator_user
from src.database import get_db_session_dependency
from src.models import User

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# Dependency for user service
async def get_user_service(
    db_session = Depends(get_db_session_dependency)
) -> UserService:
    """Get user service instance"""
    return UserService(db_session)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Create a new user account (Admin/Moderator only)",
    responses={
        status.HTTP_201_CREATED: {
            "description": "User created successfully",
            "model": UserResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data or user already exists"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error"
        }
    }
)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_moderator_user),
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user account"""
    try:
        user = await user_service.create_user(user_data, current_user)
        return UserResponse.from_orm(user)
        
    except Exception as e:
        error_response = handle_user_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Get Users",
    description="Get paginated list of users with filtering and sorting",
    responses={
        status.HTTP_200_OK: {
            "description": "Users retrieved successfully",
            "model": UserListResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        }
    }
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    username: Optional[str] = Query(None, description="Filter by username (partial match)"),
    email: Optional[str] = Query(None, description="Filter by email (partial match)"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    sort_by: str = Query("id", description="Sort field (id, username, email, created_at, last_login_at)"),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    current_user: User = Depends(get_current_moderator_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get paginated list of users with filtering and sorting"""
    try:
        # Build filters
        filters = UserFilter(
            username=username,
            email=email,
            role=role,
            is_active=is_active,
            is_verified=is_verified
        )
        
        # Build sorting
        sort = UserSort(field=sort_by, desc=sort_desc)
        
        # Get users
        users, total_count = await user_service.get_users(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort,
            current_user=current_user
        )
        
        # Convert to response models
        user_responses = [UserResponse.from_orm(user) for user in users]
        
        return UserListResponse(
            users=user_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=(total_count + page_size - 1) // page_size
        )
        
    except Exception as e:
        error_response = handle_user_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Get user details by ID",
    responses={
        status.HTTP_200_OK: {
            "description": "User retrieved successfully",
            "model": UserResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found"
        }
    }
)
async def get_user(
    user_id: int = Path(..., description="User ID"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user details by ID"""
    try:
        # Users can only view themselves unless they're admin/moderator
        if current_user.role not in ["admin", "moderator"] and current_user.id != user_id:
            raise InsufficientPermissionsError("Can only view your own profile")
        
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        return UserResponse.from_orm(user)
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, UserNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response
            )
        elif isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update User",
    description="Update user information",
    responses={
        status.HTTP_200_OK: {
            "description": "User updated successfully",
            "model": UserResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data or operation failed"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error"
        }
    }
)
async def update_user(
    user_id: int = Path(..., description="User ID"),
    user_data: UserUpdate = ...,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update user information"""
    try:
        user = await user_service.update_user(user_id, user_data, current_user)
        return UserResponse.from_orm(user)
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, UserNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response
            )
        elif isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Delete user account (soft delete)",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User deleted successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found"
        }
    }
)
async def delete_user(
    user_id: int = Path(..., description="User ID"),
    current_user: User = Depends(get_current_moderator_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete user account (soft delete)"""
    try:
        await user_service.delete_user(user_id, current_user)
        return None
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, UserNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response
            )
        elif isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )


@router.post(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate User",
    description="Activate a user account",
    responses={
        status.HTTP_200_OK: {
            "description": "User activated successfully",
            "model": UserResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found"
        }
    }
)
async def activate_user(
    user_id: int = Path(..., description="User ID"),
    current_user: User = Depends(get_current_moderator_user),
    user_service: UserService = Depends(get_user_service)
):
    """Activate a user account"""
    try:
        user = await user_service.activate_user(user_id, current_user)
        return UserResponse.from_orm(user)
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, UserNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response
            )
        elif isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )


@router.post(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate User",
    description="Deactivate a user account",
    responses={
        status.HTTP_200_OK: {
            "description": "User deactivated successfully",
            "model": UserResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found"
        }
    }
)
async def deactivate_user(
    user_id: int = Path(..., description="User ID"),
    current_user: User = Depends(get_current_moderator_user),
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate a user account"""
    try:
        user = await user_service.deactivate_user(user_id, current_user)
        return UserResponse.from_orm(user)
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, UserNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response
            )
        elif isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )


@router.post(
    "/{user_id}/change-role",
    response_model=UserResponse,
    summary="Change User Role",
    description="Change user role (Admin only)",
    responses={
        status.HTTP_200_OK: {
            "description": "User role changed successfully",
            "model": UserResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid operation or operation failed"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found"
        }
    }
)
async def change_user_role(
    user_id: int = Path(..., description="User ID"),
    new_role: UserRole = ...,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """Change user role"""
    try:
        user = await user_service.change_user_role(user_id, new_role, current_user)
        return UserResponse.from_orm(user)
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, UserNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response
            )
        elif isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )


@router.get(
    "/statistics/overview",
    summary="Get User Statistics",
    description="Get user statistics overview (Admin/Moderator only)",
    responses={
        status.HTTP_200_OK: {
            "description": "Statistics retrieved successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions"
        }
    }
)
async def get_user_statistics(
    current_user: User = Depends(get_current_moderator_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user statistics overview"""
    try:
        stats = await user_service.get_user_statistics(current_user)
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        error_response = handle_user_exception(e)
        if isinstance(e, InsufficientPermissionsError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_response
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response
            )

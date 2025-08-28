"""
Authentication dependencies for FastAPI
JWT token validation and user authentication
"""
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import AuthService
from src.auth.schemas import TokenData
from src.auth.exceptions import InvalidTokenError, AuthenticationError
from src.database import get_db_session_dependency
from src.models import User

logger = logging.getLogger(__name__)

# HTTP Bearer scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db_session: AsyncSession = Depends(get_db_session_dependency)
) -> User:
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Verify token
        token_data = auth_service.verify_token(credentials.credentials)
        
        # Get user from database
        user = await auth_service.get_user_by_id(token_data.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check for active status)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user (additional check for email verification)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user (role-based access control)"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_super_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current super admin user (highest level access)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def get_optional_current_user(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session_dependency)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None (for optional auth)"""
    try:
        # Extract token from request headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Verify token
        token_data = auth_service.verify_token(token)
        
        # Get user from database
        user = await auth_service.get_user_by_id(token_data.user_id)
        
        if not user or not user.is_active:
            return None
        
        return user
        
    except Exception:
        # If any error occurs, return None (user not authenticated)
        return None


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        # TODO: Implement permission checking logic
        # For now, just check if user is admin
        if current_user.role not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_checker


def require_role(role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return current_user
    
    return role_checker


def require_roles(roles: list):
    """Decorator to require one of specific roles"""
    def roles_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {roles} required"
            )
        return current_user
    
    return roles_checker


# Rate limiting dependency (placeholder)
async def check_rate_limit(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Check rate limiting for requests"""
    # TODO: Implement rate limiting logic
    # For now, just pass through
    return True


# IP address extraction
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"


# User agent extraction
def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")


# Request logging dependency
async def log_request(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Log request details for audit purposes"""
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    user_id = current_user.id if current_user else None
    
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"IP: {client_ip} - "
        f"User: {user_id} - "
        f"User-Agent: {user_agent[:100]}..."
    )
    
    return True

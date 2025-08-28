"""
Authentication router with comprehensive Swagger documentation
JWT-based authentication endpoints
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer

from src.auth.schemas import (
    UserLogin, UserRegister, Token, AuthResponse, PasswordChange,
    PasswordReset, PasswordResetConfirm, EmailVerification, 
    ResendVerification, Logout, RefreshToken
)
from src.auth.service import AuthService
from src.auth.dependencies import get_client_ip, get_user_agent, get_current_user
from src.auth.exceptions import (
    handle_auth_exception, AuthenticationError, InvalidCredentialsError,
    UserAlreadyExistsError, UserNotFoundError, InvalidTokenError
)
from src.database import get_db_session_dependency
from src.models import User

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# HTTP Bearer scheme for Swagger UI
security_scheme = HTTPBearer()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="""
    **Register a new user account**
    
    Creates a new user account with the provided information.
    
    **Features:**
    - Username validation (3-50 characters, alphanumeric + underscore/hyphen)
    - Email validation and uniqueness check
    - Password strength requirements (min 8 characters)
    - Password confirmation validation
    - Automatic password hashing with bcrypt
    
    **Validation Rules:**
    - Username must be unique
    - Email must be unique and valid format
    - Password must be at least 8 characters
    - Confirm password must match password
    - Full name must be 2-100 characters
    
    **Response:**
    - Success message with user details
    - User ID and basic information
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "User registered successfully",
                        "data": {
                            "user_id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "full_name": "John Doe",
                            "role": "user",
                            "is_verified": False
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Validation error or user already exists",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Username already exists",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db_session = Depends(get_db_session_dependency)
):
    """Register new user account"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Get client information
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Register user
        user = await auth_service.register_user(user_data)
        
        logger.info(f"User {user.username} registered from IP: {client_ip}")
        
        return AuthResponse(
            success=True,
            message="User registered successfully",
            data={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified
            }
        )
        
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/login",
    response_model=Token,
    summary="User Login",
    description="""
    **Authenticate user and get access tokens**
    
    Authenticates user credentials and returns JWT access and refresh tokens.
    
    **Authentication Flow:**
    1. Validate email and password
    2. Check user account status (active/verified)
    3. Verify password hash with bcrypt
    4. Generate JWT access token (30 minutes)
    5. Generate JWT refresh token (7 days)
    6. Create user session record
    7. Update last login timestamp
    
    **Security Features:**
    - Password hashing with bcrypt
    - JWT token expiration
    - Session tracking with IP and User-Agent
    - Account status validation
    
    **Token Information:**
    - Access Token: Short-lived (30 min) for API calls
    - Refresh Token: Long-lived (7 days) for token renewal
    - Token Type: Bearer (for Authorization header)
    
    **Usage:**
    Include access token in Authorization header:
    ```
    Authorization: Bearer <access_token>
    ```
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "full_name": "John Doe",
                            "role": "user",
                            "is_verified": False
                        }
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials or account deactivated",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid email or password"
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def login_user(
    login_data: UserLogin,
    request: Request,
    response: Response,
    db_session = Depends(get_db_session_dependency)
):
    """Authenticate user and return tokens"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Get client information
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Login user
        login_result = await auth_service.login_user(
            login_data, 
            client_ip, 
            user_agent
        )
        
        logger.info(f"User {login_result['user']['username']} logged in from IP: {client_ip}")
        
        # Set secure cookie for refresh token (optional)
        response.set_cookie(
            key="refresh_token",
            value=login_result["refresh_token"],
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return Token(**login_result)
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh Access Token",
    description="""
    **Refresh expired access token using refresh token**
    
    Generates a new access token using a valid refresh token.
    
    **Token Refresh Flow:**
    1. Validate refresh token signature and expiration
    2. Check if refresh token exists in active sessions
    3. Verify user account is still active
    4. Generate new access token (30 minutes)
    5. Return new token with user information
    
    **Security Features:**
    - Refresh token validation
    - Session existence check
    - User status verification
    - Automatic token rotation
    
    **Usage:**
    Send refresh token in request body:
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    
    **Response:**
    - New access token
    - Same refresh token
    - Updated user information
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "full_name": "John Doe",
                            "role": "user",
                            "is_verified": False
                        }
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid or expired refresh token"
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def refresh_token(
    refresh_data: RefreshToken,
    db_session = Depends(get_db_session_dependency)
):
    """Refresh access token using refresh token"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Refresh token
        refresh_result = await auth_service.refresh_access_token(
            refresh_data.refresh_token
        )
        
        return Token(**refresh_result)
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="User Logout",
    description="""
    **Logout user and invalidate session**
    
    Logs out the current user and invalidates their session.
    
    **Logout Options:**
    1. **Logout current session only**: Include refresh token
    2. **Logout all sessions**: Don't include refresh token
    
    **Session Invalidation:**
    - Marks session as inactive
    - Prevents token refresh
    - Maintains audit trail
    
    **Security Features:**
    - Session invalidation
    - Token blacklisting (optional)
    - Audit logging
    
    **Usage:**
    - Include refresh token to logout specific session
    - Don't include refresh token to logout all sessions
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Logout successful",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "User logged out successfully",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def logout_user(
    logout_data: Logout,
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db_session_dependency)
):
    """Logout user and invalidate session"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Logout user
        await auth_service.logout_user(
            current_user.id, 
            logout_data.refresh_token
        )
        
        logger.info(f"User {current_user.username} logged out")
        
        return AuthResponse(
            success=True,
            message="User logged out successfully",
            data=None
        )
        
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/change-password",
    response_model=AuthResponse,
    summary="Change Password",
    description="""
    **Change user password**
    
    Allows authenticated users to change their password.
    
    **Password Change Flow:**
    1. Verify current password
    2. Validate new password requirements
    3. Check password confirmation
    4. Hash new password with bcrypt
    5. Update user record
    
    **Password Requirements:**
    - Minimum 8 characters
    - Must be different from current password
    - Confirmation must match
    
    **Security Features:**
    - Current password verification
    - Password strength validation
    - Secure password hashing
    - Audit logging
    
    **Usage:**
    Requires authentication token in header:
    ```
    Authorization: Bearer <access_token>
    ```
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Password changed successfully",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid current password or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Current password is incorrect"
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db_session = Depends(get_db_session_dependency)
):
    """Change user password"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Change password
        await auth_service.change_password(
            current_user.id, 
            password_data
        )
        
        logger.info(f"Password changed for user {current_user.username}")
        
        return AuthResponse(
            success=True,
            message="Password changed successfully",
            data=None
        )
        
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/request-password-reset",
    response_model=AuthResponse,
    summary="Request Password Reset",
    description="""
    **Request password reset for user account**
    
    Initiates password reset process by sending reset token to user's email.
    
    **Password Reset Flow:**
    1. Validate email address
    2. Generate secure reset token
    3. Store token with expiration
    4. Send email with reset link
    5. Return success response
    
    **Security Features:**
    - Secure token generation
    - Token expiration (24 hours)
    - Email-based delivery
    - Rate limiting protection
    
    **Privacy Protection:**
    - Always returns success (doesn't reveal if email exists)
    - No user information disclosure
    - Secure token handling
    
    **Usage:**
    Send email address in request body:
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Note:** Check user's email for reset instructions
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Password reset requested",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "If the email exists, password reset instructions have been sent",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def request_password_reset(
    reset_data: PasswordReset,
    db_session = Depends(get_db_session_dependency)
):
    """Request password reset"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Request password reset
        await auth_service.request_password_reset(reset_data.email)
        
        logger.info(f"Password reset requested for email: {reset_data.email}")
        
        return AuthResponse(
            success=True,
            message="If the email exists, password reset instructions have been sent",
            data=None
        )
        
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/confirm-password-reset",
    response_model=AuthResponse,
    summary="Confirm Password Reset",
    description="""
    **Confirm password reset with token**
    
    Completes password reset process using the token from email.
    
    **Reset Confirmation Flow:**
    1. Validate reset token
    2. Check token expiration
    3. Verify new password requirements
    4. Hash new password
    5. Update user record
    6. Invalidate reset token
    
    **Token Requirements:**
    - Must be valid reset token
    - Must not be expired
    - Single-use only
    
    **Password Requirements:**
    - Minimum 8 characters
    - Confirmation must match
    - Different from current password
    
    **Usage:**
    Send reset token and new password:
    ```json
    {
        "token": "reset_token_here",
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123"
    }
    ```
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Password reset confirmed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Password reset successfully",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid token or validation error"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db_session = Depends(get_db_session_dependency)
):
    """Confirm password reset"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Confirm password reset
        await auth_service.confirm_password_reset(
            reset_data.token, 
            reset_data.new_password
        )
        
        logger.info("Password reset confirmed successfully")
        
        return AuthResponse(
            success=True,
            message="Password reset successfully",
            data=None
        )
        
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/verify-email",
    response_model=AuthResponse,
    summary="Verify Email Address",
    description="""
    **Verify user email address with token**
    
    Confirms user's email address using verification token.
    
    **Email Verification Flow:**
    1. Validate verification token
    2. Check token expiration
    3. Update user verification status
    4. Invalidate verification token
    5. Send confirmation email
    
    **Verification Benefits:**
    - Full account access
    - Password reset capability
    - Email notifications
    - Account security
    
    **Usage:**
    Send verification token:
    ```json
    {
        "token": "verification_token_here"
    }
    ```
    
    **Note:** Check email for verification link
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Email verified successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Email verified successfully",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid token or verification failed"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def verify_email(
    verification_data: EmailVerification,
    db_session = Depends(get_db_session_dependency)
):
    """Verify email address"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # Verify email
        await auth_service.verify_email(verification_data.token)
        
        logger.info("Email verification completed successfully")
        
        return AuthResponse(
            success=True,
            message="Email verified successfully",
            data=None
        )
        
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/resend-verification",
    response_model=AuthResponse,
    summary="Resend Email Verification",
    description="""
    **Resend email verification link**
    
    Sends a new verification email to unverified users.
    
    **Resend Flow:**
    1. Validate email address
    2. Check if user exists and is unverified
    3. Generate new verification token
    4. Send verification email
    5. Return success response
    
    **Rate Limiting:**
    - Maximum 3 requests per hour per email
    - Prevents email spam
    - Protects against abuse
    
    **Usage:**
    Send email address:
    ```json
    {
        "email": "user@example.com"
    }
    ```
    
    **Note:** Check email for new verification link
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Verification email sent",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Verification email sent if account exists and is unverified",
                        "data": None
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error"
        }
    }
)
async def resend_verification(
    resend_data: ResendVerification,
    db_session = Depends(get_db_session_dependency)
):
    """Resend email verification"""
    try:
        # Create auth service
        auth_service = AuthService(db_session)
        
        # TODO: Implement resend verification logic
        logger.info(f"Verification resend requested for email: {resend_data.email}")
        
        return AuthResponse(
            success=True,
            message="Verification email sent if account exists and is unverified",
            data=None
        )
        
    except Exception as e:
        error_response = handle_auth_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/me",
    summary="Get Current User",
    description="""
    **Get current authenticated user information**
    
    Returns detailed information about the currently authenticated user.
    
    **Authentication Required:**
    - Valid JWT access token in Authorization header
    - Token must not be expired
    - User account must be active
    
    **Response Information:**
    - User ID and basic details
    - Account status and verification
    - Role and permissions
    - Account creation and update timestamps
    
    **Usage:**
    Include authentication token:
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Security:**
    - Token validation
    - User status verification
    - Role-based access control
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Current user information",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "phone": "+1234567890",
                        "avatar_url": "https://example.com/avatar.jpg",
                        "is_active": True,
                        "is_verified": True,
                        "role": "user",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "last_login_at": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required or invalid token"
        }
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

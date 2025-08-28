"""
Custom exceptions for User management module
Following Python best practices for exception handling
"""
from typing import Optional, Any, Dict


class UserBaseException(Exception):
    """Base exception for user management module"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": True,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class UserNotFoundError(UserBaseException):
    """Raised when user is not found"""
    
    def __init__(self, message: str = "User not found", **kwargs):
        super().__init__(message, "USER_NOT_FOUND", **kwargs)


class UserAlreadyExistsError(UserBaseException):
    """Raised when trying to create user that already exists"""
    
    def __init__(self, message: str = "User already exists", **kwargs):
        super().__init__(message, "USER_ALREADY_EXISTS", **kwargs)


class InvalidUserOperationError(UserBaseException):
    """Raised when user operation is invalid"""
    
    def __init__(self, message: str = "Invalid user operation", **kwargs):
        super().__init__(message, "INVALID_USER_OPERATION", **kwargs)


class InsufficientPermissionsError(UserBaseException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, "INSUFFICIENT_PERMISSIONS", **kwargs)


class UserValidationError(UserBaseException):
    """Raised when user data validation fails"""
    
    def __init__(self, message: str = "User validation failed", **kwargs):
        super().__init__(message, "USER_VALIDATION_ERROR", **kwargs)


class UserAccountError(UserBaseException):
    """Raised when user account has issues"""
    
    def __init__(self, message: str = "User account error", **kwargs):
        super().__init__(message, "USER_ACCOUNT_ERROR", **kwargs)


class UserRoleError(UserBaseException):
    """Raised when user role operation fails"""
    
    def __init__(self, message: str = "User role error", **kwargs):
        super().__init__(message, "USER_ROLE_ERROR", **kwargs)


class UserStatusError(UserBaseException):
    """Raised when user status operation fails"""
    
    def __init__(self, message: str = "User status error", **kwargs):
        super().__init__(message, "USER_STATUS_ERROR", **kwargs)


def handle_user_exception(exc: Exception) -> Dict[str, Any]:
    """Handle user management exceptions and return standardized error response"""
    if isinstance(exc, UserBaseException):
        return exc.to_dict()
    
    # Handle other exceptions
    return {
        "error": True,
        "message": "An unexpected error occurred",
        "error_code": "INTERNAL_SERVER_ERROR",
        "details": {
            "exception_type": exc.__class__.__name__,
            "error_message": str(exc)
        }
    }

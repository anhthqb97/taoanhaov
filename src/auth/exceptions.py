"""
Custom exceptions for Authentication module
Following Python best practices for exception handling
"""
from typing import Optional, Any, Dict


class AuthBaseException(Exception):
    """Base exception for authentication module"""
    
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


class AuthenticationError(AuthBaseException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, "AUTHENTICATION_ERROR", **kwargs)


class InvalidCredentialsError(AuthBaseException):
    """Raised when credentials are invalid"""
    
    def __init__(self, message: str = "Invalid credentials", **kwargs):
        super().__init__(message, "INVALID_CREDENTIALS", **kwargs)


class UserAlreadyExistsError(AuthBaseException):
    """Raised when trying to create user that already exists"""
    
    def __init__(self, message: str = "User already exists", **kwargs):
        super().__init__(message, "USER_ALREADY_EXISTS", **kwargs)


class UserNotFoundError(AuthBaseException):
    """Raised when user is not found"""
    
    def __init__(self, message: str = "User not found", **kwargs):
        super().__init__(message, "USER_NOT_FOUND", **kwargs)


class InvalidTokenError(AuthBaseException):
    """Raised when token is invalid or expired"""
    
    def __init__(self, message: str = "Invalid token", **kwargs):
        super().__init__(message, "INVALID_TOKEN", **kwargs)


class PasswordMismatchError(AuthBaseException):
    """Raised when password verification fails"""
    
    def __init__(self, message: str = "Password mismatch", **kwargs):
        super().__init__(message, "PASSWORD_MISMATCH", **kwargs)


class AccountDeactivatedError(AuthBaseException):
    """Raised when account is deactivated"""
    
    def __init__(self, message: str = "Account is deactivated", **kwargs):
        super().__init__(message, "ACCOUNT_DEACTIVATED", **kwargs)


class EmailNotVerifiedError(AuthBaseException):
    """Raised when email is not verified"""
    
    def __init__(self, message: str = "Email not verified", **kwargs):
        super().__init__(message, "EMAIL_NOT_VERIFIED", **kwargs)


class RateLimitExceededError(AuthBaseException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", **kwargs)


def handle_auth_exception(exc: Exception) -> Dict[str, Any]:
    """Handle authentication exceptions and convert to API response format"""
    if isinstance(exc, AuthBaseException):
        return exc.to_dict()
    
    # Handle unexpected exceptions
    return {
        "error": True,
        "message": str(exc),
        "error_code": "UNEXPECTED_ERROR",
        "details": {
            "exception_type": type(exc).__name__,
            "traceback": str(exc)
        }
    }

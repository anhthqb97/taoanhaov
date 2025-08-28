"""
Custom exceptions for Automation module
Following Python best practices for exception handling
"""
from typing import Optional, Any, Dict


class AutomationBaseException(Exception):
    """Base exception for automation module"""
    
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


class WorkflowNotFoundError(AutomationBaseException):
    """Raised when workflow is not found or access denied"""
    
    def __init__(self, message: str = "Workflow not found", **kwargs):
        super().__init__(message, "WORKFLOW_NOT_FOUND", **kwargs)


class WorkflowAlreadyRunningError(AutomationBaseException):
    """Raised when trying to execute a workflow that is already running"""
    
    def __init__(self, message: str = "Workflow is already running", **kwargs):
        super().__init__(message, "WORKFLOW_ALREADY_RUNNING", **kwargs)


class WorkflowExecutionError(AutomationBaseException):
    """Raised when workflow execution fails"""
    
    def __init__(self, message: str = "Workflow execution failed", **kwargs):
        super().__init__(message, "WORKFLOW_EXECUTION_ERROR", **kwargs)


class EmulatorNotAvailableError(AutomationBaseException):
    """Raised when emulator is not available or not running"""
    
    def __init__(self, message: str = "Emulator is not available", **kwargs):
        super().__init__(message, "EMULATOR_NOT_AVAILABLE", **kwargs)


class EmulatorConnectionError(AutomationBaseException):
    """Raised when cannot connect to emulator"""
    
    def __init__(self, message: str = "Cannot connect to emulator", **kwargs):
        super().__init__(message, "EMULATOR_CONNECTION_ERROR", **kwargs)


class ScreenshotCaptureError(AutomationBaseException):
    """Raised when screenshot capture fails"""
    
    def __init__(self, message: str = "Screenshot capture failed", **kwargs):
        super().__init__(message, "SCREENSHOT_CAPTURE_ERROR", **kwargs)


class InstallationError(AutomationBaseException):
    """Raised when app installation fails"""
    
    def __init__(self, message: str = "App installation failed", **kwargs):
        super().__init__(message, "INSTALLATION_ERROR", **kwargs)


class InstallationTimeoutError(AutomationBaseException):
    """Raised when installation times out"""
    
    def __init__(self, message: str = "Installation timed out", **kwargs):
        super().__init__(message, "INSTALLATION_TIMEOUT", **kwargs)


class ADBCommandError(AutomationBaseException):
    """Raised when ADB command fails"""
    
    def __init__(self, message: str = "ADB command failed", **kwargs):
        super().__init__(message, "ADB_COMMAND_ERROR", **kwargs)


class UIElementNotFoundError(AutomationBaseException):
    """Raised when required UI element is not found"""
    
    def __init__(self, message: str = "UI element not found", **kwargs):
        super().__init__(message, "UI_ELEMENT_NOT_FOUND", **kwargs)


class ValidationError(AutomationBaseException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, "VALIDATION_ERROR", **kwargs)


class PermissionError(AutomationBaseException):
    """Raised when user doesn't have permission for operation"""
    
    def __init__(self, message: str = "Permission denied", **kwargs):
        super().__init__(message, "PERMISSION_ERROR", **kwargs)


class DatabaseError(AutomationBaseException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, "DATABASE_ERROR", **kwargs)


class ConfigurationError(AutomationBaseException):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, "CONFIGURATION_ERROR", **kwargs)


class NetworkError(AutomationBaseException):
    """Raised when network operation fails"""
    
    def __init__(self, message: str = "Network operation failed", **kwargs):
        super().__init__(message, "NETWORK_ERROR", **kwargs)


class TimeoutError(AutomationBaseException):
    """Raised when operation times out"""
    
    def __init__(self, message: str = "Operation timed out", **kwargs):
        super().__init__(message, "TIMEOUT_ERROR", **kwargs)


class ResourceNotFoundError(AutomationBaseException):
    """Raised when required resource is not found"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, "RESOURCE_NOT_FOUND", **kwargs)


class RateLimitExceededError(AutomationBaseException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", **kwargs)


class AuthenticationError(AutomationBaseException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, "AUTHENTICATION_ERROR", **kwargs)


class AuthorizationError(AutomationBaseException):
    """Raised when user is not authorized for operation"""
    
    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(message, "AUTHORIZATION_ERROR", **kwargs)


# Exception mapping for error codes
EXCEPTION_MAPPING = {
    "WORKFLOW_NOT_FOUND": WorkflowNotFoundError,
    "WORKFLOW_ALREADY_RUNNING": WorkflowAlreadyRunningError,
    "WORKFLOW_EXECUTION_ERROR": WorkflowExecutionError,
    "EMULATOR_NOT_AVAILABLE": EmulatorNotAvailableError,
    "EMULATOR_CONNECTION_ERROR": EmulatorConnectionError,
    "SCREENSHOT_CAPTURE_ERROR": ScreenshotCaptureError,
    "INSTALLATION_ERROR": InstallationError,
    "INSTALLATION_TIMEOUT": InstallationTimeoutError,
    "ADB_COMMAND_ERROR": ADBCommandError,
    "UI_ELEMENT_NOT_FOUND": UIElementNotFoundError,
    "VALIDATION_ERROR": ValidationError,
    "PERMISSION_ERROR": PermissionError,
    "DATABASE_ERROR": DatabaseError,
    "CONFIGURATION_ERROR": ConfigurationError,
    "NETWORK_ERROR": NetworkError,
    "TIMEOUT_ERROR": TimeoutError,
    "RESOURCE_NOT_FOUND": ResourceNotFoundError,
    "RATE_LIMIT_EXCEEDED": RateLimitExceededError,
    "AUTHENTICATION_ERROR": AuthenticationError,
    "AUTHORIZATION_ERROR": AuthorizationError,
}


def create_exception(error_code: str, message: str, **kwargs) -> AutomationBaseException:
    """Factory function to create exceptions by error code"""
    exception_class = EXCEPTION_MAPPING.get(error_code, AutomationBaseException)
    return exception_class(message, error_code, **kwargs)


def handle_automation_exception(exc: Exception) -> Dict[str, Any]:
    """Handle automation exceptions and convert to API response format"""
    if isinstance(exc, AutomationBaseException):
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

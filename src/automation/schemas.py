"""
Pydantic schemas for Automation module
Following FastAPI best practices with proper validation and documentation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class WorkflowType(str, Enum):
    """Workflow type enumeration"""
    INSTALL = "install"
    SCREENSHOT = "screenshot"
    BOTH = "both"


class WorkflowStatus(str, Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScreenshotType(str, Enum):
    """Screenshot type enumeration"""
    LOGIN = "login"
    GAME_LOADING = "game_loading"
    GAME_PLAY = "game_play"
    ERROR = "error"


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Base Models
class AutomationWorkflowBase(BaseModel):
    """Base model for automation workflow"""
    name: str = Field(..., min_length=1, max_length=100, description="Workflow name")
    description: Optional[str] = Field(None, max_length=1000, description="Workflow description")
    workflow_type: WorkflowType = Field(..., description="Type of workflow to execute")
    emulator_config_id: int = Field(..., gt=0, description="ID of emulator configuration to use")


class AutomationWorkflowCreate(AutomationWorkflowBase):
    """Model for creating new automation workflow"""
    pass


class AutomationWorkflowUpdate(BaseModel):
    """Model for updating automation workflow"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[WorkflowStatus] = None
    error_message: Optional[str] = None


class AutomationWorkflowResponse(AutomationWorkflowBase):
    """Model for automation workflow response"""
    id: int = Field(..., description="Workflow ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    user_id: int = Field(..., description="User ID who created the workflow")
    started_at: Optional[datetime] = Field(None, description="When workflow started")
    completed_at: Optional[datetime] = Field(None, description="When workflow completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="When workflow was created")
    updated_at: datetime = Field(..., description="When workflow was last updated")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScreenshotBase(BaseModel):
    """Base model for screenshot"""
    file_name: str = Field(..., description="Screenshot file name")
    file_size_bytes: int = Field(..., gt=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    width: int = Field(..., gt=0, description="Image width in pixels")
    height: int = Field(..., gt=0, description="Image height in pixels")
    screenshot_type: ScreenshotType = Field(..., description="Type of screenshot")
    metadata_json: Optional[dict] = Field(None, description="Additional metadata")


class ScreenshotCreate(ScreenshotBase):
    """Model for creating new screenshot"""
    workflow_id: int = Field(..., gt=0, description="ID of the workflow")
    file_path: str = Field(..., description="Path to the screenshot file")


class ScreenshotResponse(ScreenshotBase):
    """Model for screenshot response"""
    id: int = Field(..., description="Screenshot ID")
    workflow_id: int = Field(..., description="ID of the workflow")
    file_path: str = Field(..., description="Path to the screenshot file")
    created_at: datetime = Field(..., description="When screenshot was created")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkflowLogBase(BaseModel):
    """Base model for workflow log"""
    log_level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    step_name: Optional[str] = Field(None, max_length=100, description="Name of the workflow step")
    execution_time_ms: Optional[int] = Field(None, ge=0, description="Execution time in milliseconds")


class WorkflowLogCreate(WorkflowLogBase):
    """Model for creating new workflow log"""
    workflow_id: int = Field(..., gt=0, description="ID of the workflow")


class WorkflowLogResponse(WorkflowLogBase):
    """Model for workflow log response"""
    id: int = Field(..., description="Log ID")
    workflow_id: int = Field(..., description="ID of the workflow")
    created_at: datetime = Field(..., description="When log was created")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request/Response Models
class WorkflowExecutionRequest(BaseModel):
    """Model for workflow execution request"""
    workflow_id: int = Field(..., gt=0, description="ID of the workflow to execute")
    force_restart: bool = Field(False, description="Force restart if workflow is already running")


class WorkflowExecutionResponse(BaseModel):
    """Model for workflow execution response"""
    workflow_id: int = Field(..., description="ID of the workflow")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    message: str = Field(..., description="Execution message")
    started_at: Optional[datetime] = Field(None, description="When workflow started")
    
    class Config:
        """Pydantic config"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkflowStatusResponse(BaseModel):
    """Model for workflow status response"""
    workflow_id: int = Field(..., description="ID of the workflow")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current step being executed")
    started_at: Optional[datetime] = Field(None, description="When workflow started")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    class Config:
        """Pydantic config"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# List Response Models
class AutomationWorkflowListResponse(BaseModel):
    """Model for automation workflow list response"""
    workflows: List[AutomationWorkflowResponse] = Field(..., description="List of workflows")
    total_count: int = Field(..., description="Total number of workflows")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ScreenshotListResponse(BaseModel):
    """Model for screenshot list response"""
    screenshots: List[ScreenshotResponse] = Field(..., description="List of screenshots")
    total_count: int = Field(..., description="Total number of screenshots")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class WorkflowLogListResponse(BaseModel):
    """Model for workflow log list response"""
    logs: List[WorkflowLogResponse] = Field(..., description="List of workflow logs")
    total_count: int = Field(..., description="Total number of logs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


# Query Models
class WorkflowQueryParams(BaseModel):
    """Model for workflow query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    status: Optional[WorkflowStatus] = Field(None, description="Filter by status")
    workflow_type: Optional[WorkflowType] = Field(None, description="Filter by workflow type")
    user_id: Optional[int] = Field(None, gt=0, description="Filter by user ID")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")


class ScreenshotQueryParams(BaseModel):
    """Model for screenshot query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    workflow_id: Optional[int] = Field(None, gt=0, description="Filter by workflow ID")
    screenshot_type: Optional[ScreenshotType] = Field(None, description="Filter by screenshot type")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")


# Statistics Models
class WorkflowStatistics(BaseModel):
    """Model for workflow statistics"""
    total_workflows: int = Field(..., description="Total number of workflows")
    completed_workflows: int = Field(..., description="Number of completed workflows")
    failed_workflows: int = Field(..., description="Number of failed workflows")
    running_workflows: int = Field(..., description="Number of currently running workflows")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    average_execution_time: Optional[float] = Field(None, description="Average execution time in seconds")
    
    @validator('success_rate')
    def validate_success_rate(cls, v):
        """Validate success rate is between 0 and 100"""
        if not 0 <= v <= 100:
            raise ValueError('Success rate must be between 0 and 100')
        return v

"""
Emulator management schemas
Following FastAPI best practices with proper validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class EmulatorStatus(str, Enum):
    """Emulator status enumeration"""
    OFFLINE = "offline"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class EmulatorType(str, Enum):
    """Emulator type enumeration"""
    ANDROID_STUDIO = "android_studio"
    GENYMOTION = "genymotion"
    BLUESTACKS = "bluestacks"
    NOX_PLAYER = "nox_player"
    LD_PLAYER = "ld_player"


class AndroidVersion(str, Enum):
    """Android version enumeration"""
    ANDROID_7 = "7.0"
    ANDROID_8 = "8.0"
    ANDROID_9 = "9.0"
    ANDROID_10 = "10.0"
    ANDROID_11 = "11.0"
    ANDROID_12 = "12.0"
    ANDROID_13 = "13.0"
    ANDROID_14 = "14.0"


class EmulatorBase(BaseModel):
    """Base emulator model"""
    name: str = Field(..., min_length=1, max_length=100, description="Emulator name")
    avd_name: str = Field(..., min_length=1, max_length=100, description="AVD name")
    emulator_type: EmulatorType = Field(..., description="Emulator type")
    android_version: AndroidVersion = Field(..., description="Android version")
    api_level: int = Field(..., ge=21, le=34, description="API level (21-34)")
    screen_resolution: str = Field(..., description="Screen resolution (e.g., 2400x1080)")
    ram_size_mb: int = Field(..., ge=1024, le=8192, description="RAM size in MB (1024-8192)")
    storage_size_gb: int = Field(..., ge=4, le=64, description="Storage size in GB (4-64)")
    cpu_cores: int = Field(..., ge=1, le=8, description="CPU cores (1-8)")
    gpu_enabled: bool = Field(default=True, description="GPU acceleration enabled")
    network_enabled: bool = Field(default=True, description="Network connectivity enabled")
    description: Optional[str] = Field(None, max_length=500, description="Emulator description")


class EmulatorCreate(EmulatorBase):
    """Emulator creation model"""
    pass


class EmulatorUpdate(BaseModel):
    """Emulator update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avd_name: Optional[str] = Field(None, min_length=1, max_length=100)
    emulator_type: Optional[EmulatorType] = None
    android_version: Optional[AndroidVersion] = None
    api_level: Optional[int] = Field(None, ge=21, le=34)
    screen_resolution: Optional[str] = None
    ram_size_mb: Optional[int] = Field(None, ge=1024, le=8192)
    storage_size_gb: Optional[int] = Field(None, ge=4, le=64)
    cpu_cores: Optional[int] = Field(None, ge=1, le=8)
    gpu_enabled: Optional[bool] = None
    network_enabled: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class EmulatorResponse(EmulatorBase):
    """Emulator response model"""
    id: int = Field(..., description="Emulator ID")
    status: EmulatorStatus = Field(..., description="Current emulator status")
    is_active: bool = Field(..., description="Emulator active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorDetailResponse(EmulatorResponse):
    """Detailed emulator response model"""
    process_id: Optional[int] = Field(None, description="Emulator process ID")
    port: Optional[int] = Field(None, description="Emulator port")
    device_id: Optional[str] = Field(None, description="Device ID (e.g., emulator-5554)")
    last_started_at: Optional[datetime] = Field(None, description="Last start timestamp")
    last_stopped_at: Optional[datetime] = Field(None, description="Last stop timestamp")
    uptime_seconds: Optional[int] = Field(None, description="Current uptime in seconds")
    error_message: Optional[str] = Field(None, description="Last error message")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorListResponse(BaseModel):
    """Emulator list response model"""
    emulators: List[EmulatorResponse] = Field(..., description="List of emulators")
    total_count: int = Field(..., description="Total number of emulators")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class EmulatorQueryParams(BaseModel):
    """Emulator query parameters model"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    name: Optional[str] = Field(None, description="Filter by name")
    avd_name: Optional[str] = Field(None, description="Filter by AVD name")
    emulator_type: Optional[EmulatorType] = Field(None, description="Filter by emulator type")
    android_version: Optional[AndroidVersion] = Field(None, description="Filter by Android version")
    api_level: Optional[int] = Field(None, description="Filter by API level")
    status: Optional[EmulatorStatus] = Field(None, description="Filter by status")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date (before)")


class EmulatorStartRequest(BaseModel):
    """Emulator start request model"""
    wait_for_boot: bool = Field(default=True, description="Wait for emulator to fully boot")
    timeout_seconds: int = Field(default=300, ge=60, le=600, description="Startup timeout in seconds")
    headless: bool = Field(default=False, description="Run in headless mode")
    additional_args: Optional[List[str]] = Field(None, description="Additional emulator arguments")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "wait_for_boot": True,
                "timeout_seconds": 300,
                "headless": False,
                "additional_args": ["-no-snapshot-load", "-no-snapshot-save"]
            }
        }


class EmulatorStopRequest(BaseModel):
    """Emulator stop request model"""
    force: bool = Field(default=False, description="Force stop emulator")
    timeout_seconds: int = Field(default=60, ge=10, le=300, description="Stop timeout in seconds")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "force": False,
                "timeout_seconds": 60
            }
        }


class EmulatorRestartRequest(BaseModel):
    """Emulator restart request model"""
    wait_for_boot: bool = Field(default=True, description="Wait for emulator to fully boot")
    timeout_seconds: int = Field(default=300, ge=60, le=600, description="Startup timeout in seconds")
    headless: bool = Field(default=False, description="Run in headless mode")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "wait_for_boot": True,
                "timeout_seconds": 300,
                "headless": False
            }
        }


class EmulatorStatusResponse(BaseModel):
    """Emulator status response model"""
    id: int = Field(..., description="Emulator ID")
    name: str = Field(..., description="Emulator name")
    avd_name: str = Field(..., description="AVD name")
    status: EmulatorStatus = Field(..., description="Current status")
    process_id: Optional[int] = Field(None, description="Process ID")
    port: Optional[int] = Field(None, description="Port number")
    device_id: Optional[str] = Field(None, description="Device ID")
    uptime_seconds: Optional[int] = Field(None, description="Uptime in seconds")
    last_started_at: Optional[datetime] = Field(None, description="Last start timestamp")
    error_message: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorHealthCheck(BaseModel):
    """Emulator health check model"""
    emulator_id: int = Field(..., description="Emulator ID")
    status: EmulatorStatus = Field(..., description="Health status")
    is_healthy: bool = Field(..., description="Health check result")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    adb_connected: bool = Field(..., description="ADB connection status")
    network_available: bool = Field(..., description="Network connectivity status")
    disk_space_gb: float = Field(..., description="Available disk space in GB")
    memory_usage_percent: float = Field(..., description="Memory usage percentage")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    last_check_at: datetime = Field(..., description="Last health check timestamp")
    error_details: Optional[str] = Field(None, description="Error details if unhealthy")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorPerformanceMetrics(BaseModel):
    """Emulator performance metrics model"""
    emulator_id: int = Field(..., description="Emulator ID")
    timestamp: datetime = Field(..., description="Metrics timestamp")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    memory_usage_mb: int = Field(..., description="Memory usage in MB")
    memory_usage_percent: float = Field(..., description="Memory usage percentage")
    disk_io_read_mbps: float = Field(..., description="Disk read speed in MB/s")
    disk_io_write_mbps: float = Field(..., description="Disk write speed in MB/s")
    network_rx_mbps: float = Field(..., description="Network receive speed in MB/s")
    network_tx_mbps: float = Field(..., description="Network transmit speed in MB/s")
    gpu_usage_percent: Optional[float] = Field(None, description="GPU usage percentage")
    temperature_celsius: Optional[float] = Field(None, description="Temperature in Celsius")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorLogEntry(BaseModel):
    """Emulator log entry model"""
    id: int = Field(..., description="Log entry ID")
    emulator_id: int = Field(..., description="Emulator ID")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(..., description="Log timestamp")
    source: str = Field(..., description="Log source")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional log details")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorSnapshot(BaseModel):
    """Emulator snapshot model"""
    id: int = Field(..., description="Snapshot ID")
    emulator_id: int = Field(..., description="Emulator ID")
    name: str = Field(..., description="Snapshot name")
    description: Optional[str] = Field(None, description="Snapshot description")
    file_path: str = Field(..., description="Snapshot file path")
    file_size_mb: float = Field(..., description="Snapshot file size in MB")
    created_at: datetime = Field(..., description="Snapshot creation timestamp")
    is_auto: bool = Field(..., description="Is automatic snapshot")
    
    class Config:
        """Pydantic config"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmulatorSnapshotCreate(BaseModel):
    """Emulator snapshot creation model"""
    name: str = Field(..., min_length=1, max_length=100, description="Snapshot name")
    description: Optional[str] = Field(None, max_length=500, description="Snapshot description")
    is_auto: bool = Field(default=False, description="Is automatic snapshot")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "name": "Clean State",
                "description": "Fresh installation state",
                "is_auto": False
            }
        }


class EmulatorBulkOperation(BaseModel):
    """Emulator bulk operation model"""
    emulator_ids: List[int] = Field(..., min_items=1, description="List of emulator IDs")
    operation: str = Field(..., description="Operation to perform (start/stop/restart/delete)")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "emulator_ids": [1, 2, 3],
                "operation": "start"
            }
        }


class EmulatorStatistics(BaseModel):
    """Emulator statistics model"""
    total_emulators: int = Field(..., description="Total number of emulators")
    running_emulators: int = Field(..., description="Number of running emulators")
    offline_emulators: int = Field(..., description="Number of offline emulators")
    emulators_by_type: Dict[str, int] = Field(..., description="Emulator count by type")
    emulators_by_android_version: Dict[str, int] = Field(..., description="Emulator count by Android version")
    average_uptime_hours: float = Field(..., description="Average uptime in hours")
    total_disk_usage_gb: float = Field(..., description="Total disk usage in GB")
    health_score: float = Field(..., description="Overall health score (0-100)")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "total_emulators": 10,
                "running_emulators": 5,
                "offline_emulators": 5,
                "emulators_by_type": {
                    "android_studio": 8,
                    "genymotion": 2
                },
                "emulators_by_android_version": {
                    "14.0": 5,
                    "13.0": 3,
                    "12.0": 2
                },
                "average_uptime_hours": 24.5,
                "total_disk_usage_gb": 45.2,
                "health_score": 85.5
            }
        }

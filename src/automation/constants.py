"""
Constants for Automation module
Centralized configuration and constants
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"
TEMP_DIR = PROJECT_ROOT / "temp"

# Ensure directories exist
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Timeouts (in seconds)
EMULATOR_TIMEOUT = 30
INSTALLATION_TIMEOUT = 300  # 5 minutes
SCREENSHOT_TIMEOUT = 60
WORKFLOW_TIMEOUT = 600  # 10 minutes

# Workflow steps
WORKFLOW_STEPS = {
    "install": [
        "check_emulator",
        "reset_home",
        "open_play_store",
        "search_game",
        "click_install",
        "wait_installation"
    ],
    "screenshot": [
        "check_installation",
        "reset_home",
        "launch_game",
        "wait_load",
        "take_screenshot",
        "save_screenshot"
    ],
    "both": [
        "install_workflow",
        "screenshot_workflow"
    ]
}

# Emulator configurations
DEFAULT_EMULATOR_CONFIG = {
    "name": "Medium Phone API 36.0",
    "avd_name": "Medium_Phone_API_36.0",
    "android_version": "14.0",
    "api_level": 34,
    "screen_resolution": "2400x1080",
    "ram_size_mb": 2048,
    "storage_size_gb": 8
}

# ADB commands
ADB_COMMANDS = {
    "devices": ["adb", "devices"],
    "home": ["adb", "shell", "input", "keyevent", "3"],
    "back": ["adb", "shell", "input", "keyevent", "4"],
    "menu": ["adb", "shell", "input", "keyevent", "82"],
    "enter": ["adb", "shell", "input", "keyevent", "66"],
    "screenshot": ["adb", "shell", "screencap", "/sdcard/screenshot.png"],
    "ui_dump": ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"]
}

# Package names
PACKAGES = {
    "lienquan": "com.garena.game.kgvn",
    "play_store": "com.android.vending",
    "google_services": "com.google.android.gms"
}

# Activities
ACTIVITIES = {
    "lienquan_login": "com.garena.game.kgvn/com.garena.game.kgtw.SGameActivity",
    "lienquan_game": "com.garena.game.kgvn/com.garena.game.kgtw.SGameRealActivity",
    "play_store_main": "com.android.vending/.AssetBrowserActivity"
}

# UI Elements coordinates (from previous testing)
UI_COORDINATES = {
    "install_button": (2117, 350),
    "search_button": (1200, 200),
    "play_button": (1200, 400),
    "uninstall_button": (1200, 400)
}

# Screenshot settings
SCREENSHOT_SETTINGS = {
    "format": "PNG",
    "quality": 100,
    "max_width": 2400,
    "max_height": 1080,
    "naming_pattern": "lienquan_workflow_{workflow_id}_{timestamp}.png"
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "automation.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Database settings
DB_SETTINGS = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False
}

# Pagination defaults
PAGINATION_DEFAULTS = {
    "default_page": 1,
    "default_page_size": 10,
    "max_page_size": 100
}

# Workflow status colors (for UI)
STATUS_COLORS = {
    "pending": "#FFA500",      # Orange
    "running": "#0000FF",      # Blue
    "completed": "#008000",    # Green
    "failed": "#FF0000",       # Red
    "cancelled": "#808080"     # Gray
}

# Error messages
ERROR_MESSAGES = {
    "emulator_not_available": "Emulator is not available or not running",
    "workflow_not_found": "Workflow not found or access denied",
    "workflow_already_running": "Workflow is already running",
    "installation_timeout": "Installation timed out",
    "screenshot_failed": "Failed to capture screenshot",
    "permission_denied": "Permission denied for this operation",
    "invalid_workflow_type": "Invalid workflow type specified",
    "database_error": "Database operation failed",
    "network_error": "Network connection failed",
    "unknown_error": "An unexpected error occurred"
}

# Success messages
SUCCESS_MESSAGES = {
    "workflow_created": "Workflow created successfully",
    "workflow_updated": "Workflow updated successfully",
    "workflow_deleted": "Workflow deleted successfully",
    "workflow_executed": "Workflow executed successfully",
    "screenshot_captured": "Screenshot captured successfully",
    "installation_completed": "Installation completed successfully"
}

# Validation rules
VALIDATION_RULES = {
    "workflow_name": {
        "min_length": 1,
        "max_length": 100,
        "pattern": r"^[a-zA-Z0-9\s\-_]+$"
    },
    "description": {
        "max_length": 1000
    },
    "page": {
        "min_value": 1
    },
    "page_size": {
        "min_value": 1,
        "max_value": 100
    }
}

# Rate limiting
RATE_LIMITS = {
    "workflow_creation": 10,      # 10 workflows per hour
    "workflow_execution": 5,      # 5 executions per hour
    "screenshot_capture": 20,     # 20 screenshots per hour
    "api_requests": 100           # 100 API requests per hour
}

# Cache settings
CACHE_SETTINGS = {
    "workflow_status_ttl": 300,   # 5 minutes
    "screenshot_ttl": 3600,       # 1 hour
    "statistics_ttl": 1800,       # 30 minutes
    "user_session_ttl": 86400     # 24 hours
}

# Security settings
SECURITY_SETTINGS = {
    "session_timeout": 86400,     # 24 hours
    "max_login_attempts": 5,
    "password_min_length": 8,
    "jwt_secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key"),
    "jwt_algorithm": "HS256",
    "jwt_expiration": 86400       # 24 hours
}

# Monitoring and metrics
MONITORING_SETTINGS = {
    "enable_metrics": True,
    "metrics_port": 9090,
    "health_check_interval": 30,  # seconds
    "performance_threshold": 30,   # seconds
    "error_threshold": 5          # max errors before alert
}

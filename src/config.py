"""
Configuration settings for the application
Using Pydantic Settings for environment variable management
"""
import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Liên Quân Mobile Automation API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Database
    DATABASE_URL: str = Field(
        default="mysql+asyncmy://lienquan_user:lienquan_pass123@mysql:3306/lienquan_db"
    )
    TEST_DATABASE_URL: Optional[str] = Field(
        default=None
    )
    
    # Database connection settings
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=30)
    DB_POOL_PRE_PING: bool = Field(default=True)
    DB_POOL_RECYCLE: int = Field(default=3600)
    DB_USE_NULL_POOL: bool = Field(default=False)
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    )
    
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"]
    )
    
    # Authentication
    JWT_SECRET_KEY: str = Field(
        default="your-jwt-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION: int = Field(default=86400)  # 24 hours
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=3600)  # 1 hour
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://redis:6379/0"
    )
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    # File upload settings
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    )
    
    # Screenshot settings
    SCREENSHOT_DIR: str = Field(default="screenshots")
    SCREENSHOT_FORMAT: str = Field(default="png")
    SCREENSHOT_QUALITY: int = Field(default=85)
    
    # Emulator settings
    EMULATOR_TIMEOUT: int = Field(default=300)  # 5 minutes
    EMULATOR_RETRY_ATTEMPTS: int = Field(default=3)
    EMULATOR_RETRY_DELAY: int = Field(default=5)
    
    # ADB settings
    ADB_HOST: str = Field(default="localhost")
    ADB_PORT: int = Field(default=5037)
    ADB_DEVICE_TIMEOUT: int = Field(default=30)
    
    # Game automation settings
    GAME_PACKAGE_NAME: str = Field(
        default="com.garena.liengquan"
    )
    GAME_ACTIVITY_NAME: str = Field(
        default="com.garena.liengquan.MainActivity"
    )
    
    # Validation methods
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        elif v is None:
            return ["localhost", "127.0.0.1", "0.0.0.0"]
        return v
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        elif v is None:
            return ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions from string or list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    class Config:
        """Pydantic config"""
        case_sensitive = False


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            # Fallback to hardcoded values if environment parsing fails
            print(f"Warning: Environment parsing failed, using fallback values: {e}")
            _settings = Settings(
                ALLOWED_HOSTS=["localhost", "127.0.0.1", "0.0.0.0"],
                ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
                DATABASE_URL="mysql+asyncmy://lienquan_user:lienquan_pass123@localhost:3306/lienquan_db",
                REDIS_URL="redis://localhost:6379/0"
            )
    return _settings


# Export settings for easy access
settings = get_settings()

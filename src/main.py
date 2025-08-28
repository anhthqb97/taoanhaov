"""
Main FastAPI application entry point
Following FastAPI best practices with proper configuration and middleware
"""
import os
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# from src.config import get_settings
from src.database import init_db, close_db
# from automation.router import router as automation_router
from src.auth.router import router as auth_router
from src.users.router import router as users_router
# from emulator.router import router as emulator_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Liên Quân Mobile Automation API...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized successfully")
    
    # Initialize other services
    logger.info("✅ Services initialization skipped for testing")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Liên Quân Mobile Automation API...")
    
    # Close database connections
    await close_db()
    logger.info("✅ Database connections cleaned up successfully")


# Create FastAPI app
app = FastAPI(
    title="Liên Quân Mobile Automation API",
    description="""
    **Liên Quân Mobile Automation API** 🎮
    
    A comprehensive API for automating Liên Quân Mobile game operations on Android emulators.
    
    ## Features
    
    * 🚀 **Automation Workflows**: Install, screenshot, and combined workflows
    * 📱 **Emulator Management**: Android emulator configuration and control
    * 📸 **Screenshot Capture**: Automated game screenshot capture
    * 🔐 **User Authentication**: Secure user management and access control
    * 📊 **Workflow Monitoring**: Real-time status tracking and logging
    * 🎯 **Smart Detection**: Intelligent app installation and UI element detection
    
    ## Workflows
    
    ### Flow 1: Installation
    - Reset to home screen
    - Open Google Play Store
    - Search and install Liên Quân Mobile
    - Monitor installation progress
    
    ### Flow 2: Screenshot
    - Reset to home screen
    - Launch Liên Quân Mobile
    - Capture login/game screenshots
    - Save to database with metadata
    
    ## Technology Stack
    
    * **Backend**: FastAPI, SQLAlchemy, AsyncIO
    * **Database**: MySQL (3NF normalized)
    * **Authentication**: JWT tokens
    * **Automation**: ADB commands, UIAutomator
    * **Platform**: Android emulator (AVD)
    
    ## Getting Started
    
    1. Set up Android Studio and AVD
    2. Install ADB tools
    3. Configure database connection
    4. Run the API server
    5. Create and execute automation workflows
    
    For detailed setup instructions, see the project documentation.
    """,
    version="1.0.0",
    contact={
        "name": "Liên Quân Automation Team",
        "email": "support@lienquan-automation.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Get settings
# settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": {
                "validation_errors": exc.errors(),
                "request_path": str(request.url)
            }
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": str(exc.detail),
            "error_code": f"HTTP_{exc.status_code}",
            "details": {
                "request_path": str(request.url),
                "status_code": exc.status_code
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": {
                "request_path": str(request.url),
                "exception_type": type(exc).__name__,
                "error_message": str(exc)
            }
        }
    )


# Health check endpoint
@app.get(
    "/health",
    summary="Health Check",
    description="Check API health status",
    tags=["Health"]
)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Liên Quân Mobile Automation API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - start_time
    }


# Root endpoint
@app.get(
    "/",
    summary="API Root",
    description="API root endpoint with basic information",
    tags=["Root"]
)
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Welcome to Liên Quân Mobile Automation API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# Test endpoint
@app.get(
    "/test",
    summary="Test Endpoint",
    description="Simple test endpoint to verify API is working",
    tags=["Test"]
)
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint"""
    return {
        "message": "API is working!",
        "test": True,
        "timestamp": datetime.now().isoformat()
    }





# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
# app.include_router(automation_router, prefix="/api/v1")
# app.include_router(emulator_router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🎯 Liên Quân Mobile Automation API is starting up...")
    
    # Log configuration
    logger.info("Environment: development")
    logger.info("Debug mode: true")
    logger.info("Database URL: SQLite (testing)")
    logger.info("Allowed origins: localhost")
    logger.info("Allowed hosts: localhost")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Liên Quân Mobile Automation API is shutting down...")


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Process Time: {process_time:.4f}s"
    )
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Custom middleware for rate limiting (placeholder)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware (placeholder implementation)"""
    # TODO: Implement proper rate limiting
    # For now, just pass through
    response = await call_next(request)
    return response


# Custom middleware for authentication (placeholder)
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Authentication middleware (placeholder implementation)"""
    # TODO: Implement proper authentication middleware
    # For now, just pass through
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    import time
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

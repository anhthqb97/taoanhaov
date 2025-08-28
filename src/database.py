"""
Database configuration and connection management
Following SQLAlchemy best practices with async support
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Database engine
engine: AsyncEngine = None
async_session_maker: async_sessionmaker[AsyncSession] = None


async def init_db():
    """Initialize database connection"""
    global engine, async_session_maker
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            pool_recycle=settings.DB_POOL_RECYCLE,
            poolclass=NullPool if settings.DB_USE_NULL_POOL else None
        )
        
        # Create async session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        logger.info("✅ Database connection initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise


async def close_db():
    """Close database connections"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("✅ Database connections closed")


async def get_db_session() -> AsyncSession:
    """Get database session"""
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    return async_session_maker()


async def get_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency for FastAPI"""
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


# Database health check
async def check_db_health() -> bool:
    """Check database health"""
    try:
        async with async_session_maker() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


# Database initialization for testing
async def init_test_db():
    """Initialize test database"""
    global engine, async_session_maker
    
    # Use test database URL
    test_db_url = settings.TEST_DATABASE_URL or settings.DATABASE_URL
    
    engine = create_async_engine(
        test_db_url,
        echo=False,
        poolclass=NullPool
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("✅ Test database initialized")


# Database cleanup for testing
async def cleanup_test_db():
    """Cleanup test database"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("✅ Test database cleaned up")

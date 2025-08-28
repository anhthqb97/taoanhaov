#!/usr/bin/env python3
"""
Simple database test script
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from database import get_db_session, init_db
from models import Base
from sqlalchemy import text


async def test_database():
    """Test database connection and create tables"""
    print("🔄 Testing database connection...")
    
    try:
        # Use SQLite for testing
        import os
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
        
        # Initialize database first
        await init_db()
        print("✅ Database initialized")
        
        session = await get_db_session()
        # Test connection
        await session.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create tables
        await session.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
        
        # Cleanup test database
        await session.close()
        if os.path.exists("./test.db"):
            os.remove("./test.db")
            print("✅ Test database cleaned up")
        
        return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def main():
    """Main function"""
    print("🚀 Database Test Script")
    print("=" * 50)
    
    success = await test_database()
    
    if success:
        print("\n🎉 Database test completed successfully!")
        print("You can now start the API server.")
    else:
        print("\n❌ Database test failed!")
        print("Please check your database configuration.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

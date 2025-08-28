#!/usr/bin/env python3
"""
MySQL Database initialization script for Liên Quân Automation API
Creates database, tables, and initial data
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database import init_db, engine
from models import Base


async def create_tables():
    """Create all database tables"""
    print("🔄 Creating database tables...")
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully")
        
        # Create tables
        from database import engine
        if engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully")
        else:
            print("❌ Engine not initialized")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


async def create_initial_data():
    """Create initial data (admin user, default emulator config)"""
    print("🔄 Creating initial data...")
    
    try:
        # TODO: Create admin user and emulator config
        print("ℹ️ Initial data creation skipped for now")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
        return False


async def main():
    """Main initialization function"""
    print("🚀 Starting MySQL database initialization...")
    
    # Create tables
    if not await create_tables():
        print("❌ Failed to create tables")
        sys.exit(1)
    
    # Create initial data
    if not await create_initial_data():
        print("❌ Failed to create initial data")
        sys.exit(1)
    
    print("🎉 Database initialization completed successfully!")
    print("\n📋 Next steps:")
    print("1. Enable Auth module")
    print("2. Enable Users module") 
    print("3. Enable Emulator module")
    print("4. Enable Automation module")


if __name__ == "__main__":
    asyncio.run(main())

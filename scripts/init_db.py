#!/usr/bin/env python3
"""
Database initialization script for Liên Quân Automation API
Creates database, tables, and initial data
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database import init_db, get_db_session
from models import Base, User, EmulatorConfig
from auth.service import AuthService
from config import get_settings


async def create_tables():
    """Create all database tables"""
    print("🔄 Creating database tables...")
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully")
        
        # Create tables
        async with get_db_session() as session:
            # Create all tables
            await session.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


async def create_initial_data():
    """Create initial data (admin user, default emulator config)"""
    print("🔄 Creating initial data...")
    
    try:
        async with get_db_session() as session:
            # Create admin user
            auth_service = AuthService(session)
            
            # Check if admin user exists
            admin_user = await auth_service.get_user_by_username("admin")
            if not admin_user:
                admin_data = {
                    "username": "admin",
                    "email": "admin@lienquan.com",
                    "password": "admin123456",
                    "full_name": "System Administrator",
                    "role": "admin",
                    "is_verified": True
                }
                
                admin_user = await auth_service.create_user(admin_data)
                print(f"✅ Admin user created: {admin_user.username}")
            else:
                print("ℹ️ Admin user already exists")
            
            # Create default emulator config
            # TODO: Implement emulator config creation
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
        return False


async def main():
    """Main initialization function"""
    print("🚀 Starting database initialization...")
    
    # Load settings
    settings = get_settings()
    print(f"📊 Database URL: {settings.database_url}")
    
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
    print("1. Start the application: docker-compose up -d")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Access Adminer: http://localhost:8080")
    print("4. Login with admin/admin123456")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Script to update admin user role from "user" to "admin"
Run this script to fix the role issue for testing Users module
"""
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import get_db_session_dependency, init_db, close_db
from models import User
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


async def update_admin_role():
    """Update admin user role to admin"""
    try:
        # Create local database engine for localhost
        local_db_url = "mysql+asyncmy://root:password@localhost:3306/lienquan"
        print(f"🔧 Using localhost database: {local_db_url}")
        
        # Create engine and session
        engine = create_async_engine(local_db_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # Test connection
        async with engine.begin() as conn:
            print("✅ Database connection successful!")
        
        # Get database session
        async with async_session() as db_session:
            # Find admin user by email
            admin_user = await db_session.get(User, 2)  # ID 2 from registration
            
            if not admin_user:
                print("❌ Admin user not found!")
                return
            
            print(f"🔍 Found admin user: {admin_user.username} (ID: {admin_user.id})")
            print(f"📋 Current role: {admin_user.role}")
            
            # Update role to admin
            admin_user.role = "admin"
            await db_session.commit()
            
            print("✅ Successfully updated admin user role to 'admin'")
            print(f"📋 New role: {admin_user.role}")
        
        # Close engine
        await engine.dispose()
            
    except Exception as e:
        print(f"❌ Error updating admin role: {str(e)}")
        raise


if __name__ == "__main__":
    print("🚀 Starting admin role update...")
    asyncio.run(update_admin_role())
    print("✨ Admin role update completed!")

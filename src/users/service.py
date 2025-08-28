"""
User management service
Following FastAPI best practices with proper business logic
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext

from src.models import User
from src.users.schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserRole, UserStatus, UserFilter, UserSort
)
from src.users.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, 
    InvalidUserOperationError, InsufficientPermissionsError
)

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """User management service class"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    async def create_user(self, user_data: UserCreate, created_by: Optional[User] = None) -> User:
        """Create a new user"""
        try:
            # Check if username already exists
            existing_user = await self.get_user_by_username(user_data.username)
            if existing_user:
                raise UserAlreadyExistsError(f"Username '{user_data.username}' already exists")
            
            # Check if email already exists
            existing_email = await self.get_user_by_email(user_data.email)
            if existing_email:
                raise UserAlreadyExistsError(f"Email '{user_data.email}' already exists")
            
            # Create user object
            user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=self.get_password_hash(user_data.password),
                full_name=user_data.full_name,
                phone=user_data.phone,
                avatar_url=user_data.avatar_url,
                role=user_data.role.value,
                is_active=True,
                is_verified=False,
                created_by=created_by.id if created_by else None
            )
            
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
            
            logger.info(f"Created user {user.username} (ID: {user.id})")
            return user
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        query = select(User).where(User.username == username)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_users(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[UserFilter] = None,
        sort_by: Optional[UserSort] = None,
        current_user: Optional[User] = None
    ) -> Tuple[List[User], int]:
        """Get paginated users with filtering and sorting"""
        try:
            # Build base query
            base_query = select(User)
            
            # Apply filters
            if filters:
                if filters.username:
                    base_query = base_query.where(User.username.ilike(f"%{filters.username}%"))
                if filters.email:
                    base_query = base_query.where(User.email.ilike(f"%{filters.email}%"))
                if filters.role:
                    base_query = base_query.where(User.role == filters.role.value)
                if filters.is_active is not None:
                    base_query = base_query.where(User.is_active == filters.is_active)
                if filters.is_verified is not None:
                    base_query = base_query.where(User.is_verified == filters.is_verified)
                if filters.created_after:
                    base_query = base_query.where(User.created_at >= filters.created_after)
                if filters.created_before:
                    base_query = base_query.where(User.created_at <= filters.created_before)
            
            # Apply sorting
            if sort_by:
                if sort_by.field == "username":
                    base_query = base_query.order_by(desc(User.username) if sort_by.desc else User.username)
                elif sort_by.field == "email":
                    base_query = base_query.order_by(desc(User.email) if sort_by.desc else User.email)
                elif sort_by.field == "created_at":
                    base_query = base_query.order_by(desc(User.created_at) if sort_by.desc else User.created_at)
                elif sort_by.field == "last_login_at":
                    base_query = base_query.order_by(desc(User.last_login_at) if sort_by.desc else User.last_login_at)
                else:
                    base_query = base_query.order_by(User.id)
            else:
                base_query = base_query.order_by(User.id)
            
            # Get total count
            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await self.db_session.execute(count_query)
            total_count = count_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * page_size
            base_query = base_query.offset(offset).limit(page_size)
            
            # Execute query
            result = await self.db_session.execute(base_query)
            users = result.scalars().all()
            
            return users, total_count
            
        except Exception as e:
            logger.error(f"Failed to get users: {str(e)}")
            raise
    
    async def update_user(
        self, 
        user_id: int, 
        user_data: UserUpdate, 
        current_user: User
    ) -> User:
        """Update user information"""
        try:
            # Get user to update
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")
            
            # Check permissions
            if not self._can_modify_user(current_user, user):
                raise InsufficientPermissionsError("Insufficient permissions to modify this user")
            
            # Check username uniqueness if changing
            if user_data.username and user_data.username != user.username:
                existing_user = await self.get_user_by_username(user_data.username)
                if existing_user:
                    raise UserAlreadyExistsError(f"Username '{user_data.username}' already exists")
            
            # Check email uniqueness if changing
            if user_data.email and user_data.email != user.email:
                existing_email = await self.get_user_by_email(user_data.email)
                if existing_email:
                    raise UserAlreadyExistsError(f"Email '{user_data.email}' already exists")
            
            # Update user fields
            update_data = user_data.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(user, field, value)
                
                user.updated_at = datetime.utcnow()
                user.updated_by = current_user.id
                
                await self.db_session.commit()
                await self.db_session.refresh(user)
                
                logger.info(f"Updated user {user.username} (ID: {user.id})")
            
            return user
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update user {user_id}: {str(e)}")
            raise
    
    async def delete_user(self, user_id: int, current_user: User) -> bool:
        """Delete user (soft delete)"""
        try:
            # Get user to delete
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")
            
            # Check permissions
            if not self._can_modify_user(current_user, user):
                raise InsufficientPermissionsError("Insufficient permissions to delete this user")
            
            # Soft delete
            user.is_active = False
            user.deleted_at = datetime.utcnow()
            user.deleted_by = current_user.id
            
            await self.db_session.commit()
            
            logger.info(f"Deleted user {user.username} (ID: {user.id})")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            raise
    
    async def activate_user(self, user_id: int, current_user: User) -> User:
        """Activate a user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")
            
            if not self._can_modify_user(current_user, user):
                raise InsufficientPermissionsError("Insufficient permissions to activate this user")
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            user.updated_by = current_user.id
            
            await self.db_session.commit()
            await self.db_session.refresh(user)
            
            logger.info(f"Activated user {user.username} (ID: {user.id})")
            return user
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to activate user {user_id}: {str(e)}")
            raise
    
    async def deactivate_user(self, user_id: int, current_user: User) -> User:
        """Deactivate a user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")
            
            if not self._can_modify_user(current_user, user):
                raise InsufficientPermissionsError("Insufficient permissions to deactivate this user")
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            user.updated_by = current_user.id
            
            await self.db_session.commit()
            await self.db_session.refresh(user)
            
            logger.info(f"Deactivated user {user.username} (ID: {user.id})")
            return user
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to deactivate user {user_id}: {str(e)}")
            raise
    
    async def change_user_role(self, user_id: int, new_role: UserRole, current_user: User) -> User:
        """Change user role"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")
            
            if not self._can_modify_user(current_user, user):
                raise InsufficientPermissionsError("Insufficient permissions to change user role")
            
            # Prevent changing own role
            if user.id == current_user.id:
                raise InvalidUserOperationError("Cannot change your own role")
            
            user.role = new_role.value
            user.updated_at = datetime.utcnow()
            user.updated_by = current_user.id
            
            await self.db_session.commit()
            await self.db_session.refresh(user)
            
            logger.info(f"Changed role of user {user.username} to {new_role.value}")
            return user
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to change role for user {user_id}: {str(e)}")
            raise
    
    def _can_modify_user(self, current_user: User, target_user: User) -> bool:
        """Check if current user can modify target user"""
        # Admin can modify anyone
        if current_user.role == "admin":
            return True
        
        # Moderator can modify regular users but not admins or other moderators
        if current_user.role == "moderator":
            return target_user.role in ["user"]
        
        # Regular users can only modify themselves
        return current_user.id == target_user.id
    
    async def get_user_statistics(self, current_user: User) -> Dict[str, Any]:
        """Get user statistics (admin/moderator only)"""
        try:
            if current_user.role not in ["admin", "moderator"]:
                raise InsufficientPermissionsError("Insufficient permissions to view statistics")
            
            # Total users
            total_query = select(func.count(User.id))
            total_result = await self.db_session.execute(total_query)
            total_users = total_result.scalar()
            
            # Active users
            active_query = select(func.count(User.id)).where(User.is_active == True)
            active_result = await self.db_session.execute(active_query)
            active_users = active_result.scalar()
            
            # Users by role
            role_query = select(User.role, func.count(User.id)).group_by(User.role)
            role_result = await self.db_session.execute(role_query)
            users_by_role = dict(role_result.all())
            
            # Recent registrations
            recent_query = select(User).order_by(desc(User.created_at)).limit(5)
            recent_result = await self.db_session.execute(recent_query)
            recent_users = recent_result.scalars().all()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "users_by_role": users_by_role,
                "recent_users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "created_at": user.created_at
                    }
                    for user in recent_users
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            raise

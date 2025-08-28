"""
Authentication service for JWT-based authentication
Following security best practices with proper password hashing and token management
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.auth.schemas import (
    UserLogin, UserRegister, TokenData, PasswordChange, 
    PasswordReset, PasswordResetConfirm
)
from src.auth.exceptions import (
    AuthenticationError, InvalidCredentialsError, UserAlreadyExistsError,
    UserNotFoundError, InvalidTokenError, PasswordMismatchError
)
from src.models import User, UserSession
from src.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service class"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        # Refresh token expires in 7 days
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            user_id: Optional[int] = payload.get("sub")
            username: Optional[str] = payload.get("username")
            email: Optional[str] = payload.get("email")
            role: Optional[str] = payload.get("role")
            exp: Optional[datetime] = payload.get("exp")
            
            if user_id is None:
                raise InvalidTokenError("Invalid token payload")
            
            token_data = TokenData(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                exp=exp
            )
            
            return token_data
            
        except JWTError as e:
            logger.error(f"JWT token verification failed: {str(e)}")
            raise InvalidTokenError("Invalid token")
    
    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        try:
            # Find user by email
            query = select(User).where(User.email == email)
            result = await self.db_session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise InvalidCredentialsError("Invalid email or password")
            
            if not user.is_active:
                raise AuthenticationError("User account is deactivated")
            
            if not self.verify_password(password, user.password_hash):
                raise InvalidCredentialsError("Invalid email or password")
            
            # Update last login time
            user.last_login_at = datetime.utcnow()
            await self.db_session.commit()
            
            logger.info(f"User {user.username} authenticated successfully")
            return user
            
        except (InvalidCredentialsError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError("Authentication failed")
    
    async def register_user(self, user_data: UserRegister) -> User:
        """Register new user"""
        try:
            # Check if username already exists
            username_query = select(User).where(User.username == user_data.username)
            username_result = await self.db_session.execute(username_query)
            if username_result.scalar_one_or_none():
                raise UserAlreadyExistsError("Username already exists")
            
            # Check if email already exists
            email_query = select(User).where(User.email == user_data.email)
            email_result = await self.db_session.execute(email_query)
            if email_result.scalar_one_or_none():
                raise UserAlreadyExistsError("Email already exists")
            
            # Create new user
            hashed_password = self.get_password_hash(user_data.password)
            
            user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password,
                full_name=user_data.full_name,
                phone=user_data.phone,
                is_active=True,
                is_verified=False,
                role=user_data.role
            )
            
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
            
            logger.info(f"User {user.username} registered successfully")
            return user
            
        except UserAlreadyExistsError:
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"User registration failed: {str(e)}")
            raise AuthenticationError("User registration failed")
    
    async def create_user_session(self, user: User, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
        """Create user session"""
        try:
            # Generate refresh token
            refresh_token = self.create_refresh_token({
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            })
            
            # Create session record
            session = UserSession(
                user_id=user.id,
                session_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=7),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True
            )
            
            self.db_session.add(session)
            await self.db_session.commit()
            await self.db_session.refresh(session)
            
            return session
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create user session: {str(e)}")
            raise AuthenticationError("Failed to create session")
    
    async def login_user(self, login_data: UserLogin, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Login user and return tokens"""
        try:
            # Authenticate user
            user = await self.authenticate_user(login_data.email, login_data.password)
            
            # Create access token
            access_token = self.create_access_token({
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            })
            
            # Create user session
            session = await self.create_user_session(user, ip_address, user_agent)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "refresh_token": session.session_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_verified": user.is_verified
                }
            }
            
        except (InvalidCredentialsError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise AuthenticationError("Login failed")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            token_data = self.verify_token(refresh_token)
            
            # Check if session exists and is active
            session_query = select(UserSession).where(
                and_(
                    UserSession.session_token == refresh_token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
            session_result = await self.db_session.execute(session_query)
            session = session_result.scalar_one_or_none()
            
            if not session:
                raise InvalidTokenError("Invalid or expired refresh token")
            
            # Get user
            user_query = select(User).where(User.id == token_data.user_id)
            user_result = await self.db_session.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            # Create new access token
            access_token = self.create_access_token({
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            })
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_verified": user.is_verified
                }
            }
            
        except (InvalidTokenError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise AuthenticationError("Token refresh failed")
    
    async def change_password(self, user_id: int, password_data: PasswordChange) -> bool:
        """Change user password"""
        try:
            # Get user
            user_query = select(User).where(User.id == user_id)
            user_result = await self.db_session.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise UserNotFoundError("User not found")
            
            # Verify current password
            if not self.verify_password(password_data.current_password, user.password_hash):
                raise PasswordMismatchError("Current password is incorrect")
            
            # Hash new password
            new_hashed_password = self.get_password_hash(password_data.new_password)
            user.password_hash = new_hashed_password
            user.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            logger.info(f"Password changed successfully for user {user.username}")
            return True
            
        except (UserNotFoundError, PasswordMismatchError):
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Password change failed: {str(e)}")
            raise AuthenticationError("Password change failed")
    
    async def request_password_reset(self, email: str) -> bool:
        """Request password reset"""
        try:
            # Find user by email
            user_query = select(User).where(User.email == email)
            user_result = await self.db_session.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Don't reveal if user exists or not
                logger.info(f"Password reset requested for email: {email}")
                return True
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store reset token (you might want to create a separate table for this)
            # For now, we'll just log it
            logger.info(f"Password reset token for {email}: {reset_token}")
            
            # TODO: Send email with reset token
            # await self.send_password_reset_email(user.email, reset_token)
            
            return True
            
        except Exception as e:
            logger.error(f"Password reset request failed: {str(e)}")
            raise AuthenticationError("Password reset request failed")
    
    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset with token"""
        try:
            # TODO: Verify reset token from storage
            # For now, we'll just log it
            logger.info(f"Password reset confirmed with token: {token}")
            
            # TODO: Update user password
            # user.password_hash = self.get_password_hash(new_password)
            # await self.db_session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Password reset confirmation failed: {str(e)}")
            raise AuthenticationError("Password reset confirmation failed")
    
    async def logout_user(self, user_id: int, refresh_token: Optional[str] = None) -> bool:
        """Logout user and invalidate session"""
        try:
            if refresh_token:
                # Invalidate specific session
                session_query = select(UserSession).where(
                    and_(
                        UserSession.session_token == refresh_token,
                        UserSession.user_id == user_id
                    )
                )
                session_result = await self.db_session.execute(session_query)
                session = session_result.scalar_one_or_none()
                
                if session:
                    session.is_active = False
                    await self.db_session.commit()
            else:
                # Invalidate all user sessions
                sessions_query = select(UserSession).where(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True
                    )
                )
                sessions_result = await self.db_session.execute(sessions_query)
                sessions = sessions_result.scalars().all()
                
                for session in sessions:
                    session.is_active = False
                
                await self.db_session.commit()
            
            logger.info(f"User {user_id} logged out successfully")
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Logout failed: {str(e)}")
            raise AuthenticationError("Logout failed")
    
    async def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        try:
            # TODO: Verify email verification token
            # For now, we'll just log it
            logger.info(f"Email verification with token: {token}")
            
            # TODO: Update user verification status
            # user.is_verified = True
            # await self.db_session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            raise AuthenticationError("Email verification failed")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            query = select(User).where(User.id == user_id)
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            query = select(User).where(User.email == email)
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            query = select(User).where(User.username == username)
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get user by username: {str(e)}")
            return None

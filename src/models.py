"""
Global database models for Liên Quân Mobile Automation System
Following SQLAlchemy best practices and 3NF normalization
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, 
    Integer, String, Text, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model - normalized to 3NF"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum('user', 'admin', 'moderator', name='user_role'), default='user', index=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    workflows = relationship("AutomationWorkflow", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        Index('idx_role', 'role'),
        Index('idx_created_at', 'created_at'),
    )


class EmulatorConfig(Base):
    """Emulator configuration model"""
    __tablename__ = "emulator_configs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    avd_name = Column(String(100), nullable=False, index=True)
    android_version = Column(String(20), nullable=False, index=True)
    api_level = Column(Integer, nullable=False)
    screen_resolution = Column(String(20), nullable=False)
    ram_size_mb = Column(Integer, nullable=False)
    storage_size_gb = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    workflows = relationship("AutomationWorkflow", back_populates="emulator_config")
    
    # Indexes
    __table_args__ = (
        Index('idx_avd_name', 'avd_name'),
        Index('idx_android_version', 'android_version'),
        Index('idx_is_active', 'is_active'),
    )


class AutomationWorkflow(Base):
    """Automation workflow model"""
    __tablename__ = "automation_workflows"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    workflow_type = Column(Enum('install', 'screenshot', 'both', name='workflow_type'), nullable=False, index=True)
    status = Column(Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='workflow_status'), 
                   default='pending', index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    emulator_config_id = Column(BigInteger, ForeignKey('emulator_configs.id', ondelete='CASCADE'), nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    user = relationship("User", back_populates="workflows")
    emulator_config = relationship("EmulatorConfig", back_populates="workflows")
    screenshots = relationship("Screenshot", back_populates="workflow", cascade="all, delete-orphan")
    logs = relationship("WorkflowLog", back_populates="workflow", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_status', 'status'),
        Index('idx_workflow_type', 'workflow_type'),
        Index('idx_started_at', 'started_at'),
    )


class Screenshot(Base):
    """Screenshot model"""
    __tablename__ = "screenshots"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = Column(BigInteger, ForeignKey('automation_workflows.id', ondelete='CASCADE'), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    screenshot_type = Column(Enum('login', 'game_loading', 'game_play', 'error', name='screenshot_type'), 
                           nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    workflow = relationship("AutomationWorkflow", back_populates="screenshots")
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_id', 'workflow_id'),
        Index('idx_screenshot_type', 'screenshot_type'),
        Index('idx_created_at', 'created_at'),
    )


class WorkflowLog(Base):
    """Workflow log model"""
    __tablename__ = "workflow_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    workflow_id = Column(BigInteger, ForeignKey('automation_workflows.id', ondelete='CASCADE'), nullable=False, index=True)
    log_level = Column(Enum('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', name='log_level'), nullable=False, index=True)
    message = Column(Text, nullable=False)
    step_name = Column(String(100), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    workflow = relationship("AutomationWorkflow", back_populates="logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_id', 'workflow_id'),
        Index('idx_log_level', 'log_level'),
        Index('idx_created_at', 'created_at'),
    )


class UserSession(Base):
    """User session model"""
    __tablename__ = "user_sessions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_session_token', 'session_token'),
        Index('idx_expires_at', 'expires_at'),
    )

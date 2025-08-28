"""
Automation service layer - Business logic for automation workflows
Following SOLID principles and DRY methodology
"""
import asyncio
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from src.models import AutomationWorkflow, Screenshot, WorkflowLog
from src.automation.schemas import (
    AutomationWorkflowCreate, AutomationWorkflowUpdate, WorkflowStatus,
    ScreenshotCreate, WorkflowLogCreate, LogLevel, ScreenshotType
)
from src.automation.exceptions import (
    WorkflowNotFoundError, WorkflowAlreadyRunningError, 
    EmulatorNotAvailableError, ScreenshotCaptureError
)
from src.automation.constants import (
    WORKFLOW_STEPS, SCREENSHOT_DIR, EMULATOR_TIMEOUT,
    INSTALLATION_TIMEOUT, SCREENSHOT_TIMEOUT
)

logger = logging.getLogger(__name__)


class AutomationService:
    """Service class for automation workflows"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.screenshot_dir = Path(SCREENSHOT_DIR)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_workflow(
        self, 
        workflow_data: AutomationWorkflowCreate, 
        user_id: int
    ) -> AutomationWorkflow:
        """Create a new automation workflow"""
        try:
            workflow = AutomationWorkflow(
                **workflow_data.dict(),
                user_id=user_id,
                status=WorkflowStatus.PENDING
            )
            
            self.db_session.add(workflow)
            await self.db_session.commit()
            await self.db_session.refresh(workflow)
            
            # Log workflow creation
            await self._log_workflow_event(
                workflow.id, 
                LogLevel.INFO, 
                f"Workflow '{workflow.name}' created successfully",
                "workflow_creation"
            )
            
            logger.info(f"Created workflow {workflow.id} for user {user_id}")
            return workflow
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create workflow: {str(e)}")
            raise
    
    async def get_workflow(self, workflow_id: int, user_id: int) -> AutomationWorkflow:
        """Get workflow by ID with user authorization"""
        query = select(AutomationWorkflow).where(
            and_(
                AutomationWorkflow.id == workflow_id,
                AutomationWorkflow.user_id == user_id
            )
        )
        
        result = await self.db_session.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")
        
        return workflow
    
    async def get_user_workflows(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10,
        status: Optional[WorkflowStatus] = None,
        workflow_type: Optional[str] = None
    ) -> Tuple[List[AutomationWorkflow], int]:
        """Get paginated workflows for a user with optional filters"""
        # Build base query
        base_query = select(AutomationWorkflow).where(
            AutomationWorkflow.user_id == user_id
        )
        
        # Apply filters
        if status:
            base_query = base_query.where(AutomationWorkflow.status == status)
        if workflow_type:
            base_query = base_query.where(AutomationWorkflow.workflow_type == workflow_type)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db_session.execute(count_query)
        total_count = total_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * page_size
        workflows_query = base_query.order_by(desc(AutomationWorkflow.created_at)).offset(offset).limit(page_size)
        
        result = await self.db_session.execute(workflows_query)
        workflows = result.scalars().all()
        
        return workflows, total_count
    
    async def update_workflow(
        self, 
        workflow_id: int, 
        user_id: int, 
        update_data: AutomationWorkflowUpdate
    ) -> AutomationWorkflow:
        """Update workflow with user authorization"""
        workflow = await self.get_workflow(workflow_id, user_id)
        
        # Only allow updates for non-running workflows
        if workflow.status == WorkflowStatus.RUNNING:
            raise WorkflowAlreadyRunningError("Cannot update running workflow")
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(workflow, field, value)
        
        workflow.updated_at = datetime.utcnow()
        
        await self.db_session.commit()
        await self.db_session.refresh(workflow)
        
        # Log update
        await self._log_workflow_event(
            workflow.id,
            LogLevel.INFO,
            f"Workflow updated: {list(update_data.dict(exclude_unset=True).keys())}",
            "workflow_update"
        )
        
        return workflow
    
    async def execute_workflow(
        self, 
        workflow_id: int, 
        user_id: int, 
        force_restart: bool = False
    ) -> Dict[str, Any]:
        """Execute automation workflow"""
        workflow = await self.get_workflow(workflow_id, user_id)
        
        # Check if workflow is already running
        if workflow.status == WorkflowStatus.RUNNING and not force_restart:
            raise WorkflowAlreadyRunningError("Workflow is already running")
        
        # Update workflow status
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        workflow.error_message = None
        
        await self.db_session.commit()
        
        # Log execution start
        await self._log_workflow_event(
            workflow.id,
            LogLevel.INFO,
            f"Workflow execution started: {workflow.workflow_type}",
            "execution_start"
        )
        
        try:
            # Execute workflow based on type
            if workflow.workflow_type == "install":
                result = await self._execute_install_workflow(workflow)
            elif workflow.workflow_type == "screenshot":
                result = await self._execute_screenshot_workflow(workflow)
            elif workflow.workflow_type == "both":
                result = await self._execute_both_workflow(workflow)
            else:
                raise ValueError(f"Unknown workflow type: {workflow.workflow_type}")
            
            # Update workflow status
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            # Log completion
            await self._log_workflow_event(
                workflow.id,
                LogLevel.INFO,
                f"Workflow completed successfully: {result}",
                "execution_complete"
            )
            
            return {
                "workflow_id": workflow.id,
                "status": "completed",
                "message": "Workflow executed successfully",
                "result": result,
                "started_at": workflow.started_at,
                "completed_at": workflow.completed_at
            }
            
        except Exception as e:
            # Update workflow status on failure
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            workflow.completed_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            # Log error
            await self._log_workflow_event(
                workflow.id,
                LogLevel.ERROR,
                f"Workflow execution failed: {str(e)}",
                "execution_error"
            )
            
            logger.error(f"Workflow {workflow_id} execution failed: {str(e)}")
            raise
    
    async def _execute_install_workflow(self, workflow: AutomationWorkflow) -> Dict[str, Any]:
        """Execute installation workflow (Flow 1)"""
        start_time = time.time()
        
        # Step 1: Check emulator availability
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Checking emulator availability", "check_emulator"
        )
        
        emulator_status = await self._check_emulator_status()
        if not emulator_status["available"]:
            raise EmulatorNotAvailableError(f"Emulator not available: {emulator_status['error']}")
        
        # Step 2: Reset to home screen
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Resetting to home screen", "reset_home"
        )
        
        await self._reset_to_home_screen()
        
        # Step 3: Open Google Play Store
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Opening Google Play Store", "open_play_store"
        )
        
        await self._open_google_play_store()
        
        # Step 4: Search and open Liên Quân Mobile
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Searching Liên Quân Mobile", "search_game"
        )
        
        await self._search_lienquan_mobile()
        
        # Step 5: Click install button
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Clicking install button", "click_install"
        )
        
        await self._click_install_button()
        
        # Step 6: Wait for installation
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Waiting for installation", "wait_installation"
        )
        
        installation_result = await self._wait_for_installation()
        
        execution_time = time.time() - start_time
        
        await self._log_workflow_event(
            workflow.id,
            LogLevel.INFO,
            f"Installation workflow completed in {execution_time:.2f}s",
            "workflow_complete",
            int(execution_time * 1000)
        )
        
        return {
            "type": "install",
            "status": "success",
            "installation_result": installation_result,
            "execution_time_seconds": execution_time
        }
    
    async def _execute_screenshot_workflow(self, workflow: AutomationWorkflow) -> Dict[str, Any]:
        """Execute screenshot workflow (Flow 2)"""
        start_time = time.time()
        
        # Step 1: Check if Liên Quân is installed
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Checking Liên Quân installation", "check_installation"
        )
        
        is_installed = await self._check_lienquan_installed()
        if not is_installed:
            raise ValueError("Liên Quân Mobile is not installed")
        
        # Step 2: Reset to home screen
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Resetting to home screen", "reset_home"
        )
        
        await self._reset_to_home_screen()
        
        # Step 3: Find and launch Liên Quân
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Finding and launching Liên Quân", "launch_game"
        )
        
        await self._find_and_launch_lienquan()
        
        # Step 4: Wait for app to load
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Waiting for app to load", "wait_load"
        )
        
        await asyncio.sleep(10)  # Wait for app to load
        
        # Step 5: Take screenshot
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Taking screenshot", "take_screenshot"
        )
        
        screenshot_path = await self._take_screenshot(workflow.id)
        
        # Step 6: Save screenshot to database
        await self._log_workflow_event(
            workflow.id, LogLevel.INFO, "Saving screenshot to database", "save_screenshot"
        )
        
        screenshot = await self._save_screenshot_to_db(workflow.id, screenshot_path)
        
        execution_time = time.time() - start_time
        
        await self._log_workflow_event(
            workflow.id,
            LogLevel.INFO,
            f"Screenshot workflow completed in {execution_time:.2f}s",
            "workflow_complete",
            int(execution_time * 1000)
        )
        
        return {
            "type": "screenshot",
            "status": "success",
            "screenshot_id": screenshot.id,
            "screenshot_path": screenshot.file_path,
            "execution_time_seconds": execution_time
        }
    
    async def _execute_both_workflow(self, workflow: AutomationWorkflow) -> Dict[str, Any]:
        """Execute both installation and screenshot workflows"""
        # Execute installation first
        install_result = await self._execute_install_workflow(workflow)
        
        # Then execute screenshot
        screenshot_result = await self._execute_screenshot_workflow(workflow)
        
        return {
            "type": "both",
            "status": "success",
            "installation": install_result,
            "screenshot": screenshot_result
        }
    
    async def _check_emulator_status(self) -> Dict[str, Any]:
        """Check if emulator is available and running"""
        try:
            # Check if emulator is running
            result = subprocess.run(
                ["adb", "devices"], 
                capture_output=True, 
                text=True, 
                timeout=EMULATOR_TIMEOUT
            )
            
            if result.returncode != 0:
                return {"available": False, "error": "ADB command failed"}
            
            # Parse device list
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line.split('\t')[0] for line in lines if line.strip()]
            
            if not devices:
                return {"available": False, "error": "No emulator devices found"}
            
            return {"available": True, "devices": devices}
            
        except subprocess.TimeoutExpired:
            return {"available": False, "error": "ADB command timeout"}
        except Exception as e:
            return {"available": False, "error": f"Unexpected error: {str(e)}"}
    
    async def _reset_to_home_screen(self):
        """Reset emulator to home screen"""
        try:
            # Press home button
            subprocess.run(
                ["adb", "shell", "input", "keyevent", "3"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(2)  # Wait for animation
            
        except Exception as e:
            logger.error(f"Failed to reset to home screen: {str(e)}")
            raise
    
    async def _open_google_play_store(self):
        """Open Google Play Store"""
        try:
            # Launch Google Play Store
            subprocess.run(
                ["adb", "shell", "am", "start", "-n", "com.android.vending/.AssetBrowserActivity"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(5)  # Wait for Play Store to load
            
        except Exception as e:
            logger.error(f"Failed to open Google Play Store: {str(e)}")
            raise
    
    async def _search_lienquan_mobile(self):
        """Search for Liên Quân Mobile in Play Store"""
        try:
            # Click search button (assuming it's at a specific position)
            subprocess.run(
                ["adb", "shell", "input", "tap", "1200", "200"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(2)
            
            # Type search query
            subprocess.run(
                ["adb", "shell", "input", "text", "lienquan"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(2)
            
            # Press enter
            subprocess.run(
                ["adb", "shell", "input", "keyevent", "66"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(3)  # Wait for search results
            
        except Exception as e:
            logger.error(f"Failed to search Liên Quân Mobile: {str(e)}")
            raise
    
    async def _click_install_button(self):
        """Click install button for Liên Quân Mobile"""
        try:
            # Click install button (coordinates from previous testing)
            subprocess.run(
                ["adb", "shell", "input", "tap", "2117", "350"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to click install button: {str(e)}")
            raise
    
    async def _wait_for_installation(self) -> str:
        """Wait for installation to complete"""
        try:
            max_wait_time = INSTALLATION_TIMEOUT
            check_interval = 5
            total_checks = max_wait_time // check_interval
            
            for i in range(total_checks):
                # Check if app is installed by looking for Play/Uninstall button
                if await self._check_app_installed():
                    return "INSTALL_SUCCESS"
                
                await asyncio.sleep(check_interval)
                
                # Log progress
                if i % 10 == 0:  # Log every 50 seconds
                    await self._log_workflow_event(
                        workflow.id,
                        LogLevel.INFO,
                        f"Installation in progress... ({i * check_interval}s elapsed)",
                        "installation_progress"
                    )
            
            return "INSTALL_TIMEOUT"
            
        except Exception as e:
            logger.error(f"Failed to wait for installation: {str(e)}")
            return "INSTALL_ERROR"
    
    async def _check_app_installed(self) -> bool:
        """Check if Liên Quân Mobile is installed by looking for UI elements"""
        try:
            # Get UI dump
            subprocess.run(
                ["adb", "shell", "rm", "/sdcard/ui_dump.xml"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            subprocess.run(
                ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            # Pull UI dump to local machine
            temp_file = f"ui_dump_check_{int(time.time())}.xml"
            subprocess.run(
                ["adb", "pull", "/sdcard/ui_dump.xml", temp_file],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            # Check for Play/Uninstall buttons
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # Clean up temp file
            os.remove(temp_file)
            
            # Check for specific button attributes
            has_play = 'text="play"' in content or 'content-desc="play"' in content
            has_uninstall = 'text="uninstall"' in content or 'content-desc="uninstall"' in content
            
            return has_play or has_uninstall
            
        except Exception as e:
            logger.error(f"Failed to check app installation: {str(e)}")
            return False
    
    async def _check_lienquan_installed(self) -> bool:
        """Check if Liên Quân Mobile is installed using package manager"""
        try:
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages"],
                capture_output=True,
                text=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            return 'kgvn' in result.stdout
            
        except Exception as e:
            logger.error(f"Failed to check Liên Quân installation: {str(e)}")
            return False
    
    async def _find_and_launch_lienquan(self):
        """Find and launch Liên Quân Mobile app"""
        try:
            # Launch app directly using package and activity
            subprocess.run(
                ["adb", "shell", "am", "start", "-n", "com.garena.game.kgvn/com.garena.game.kgtw.SGameActivity"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            await asyncio.sleep(5)  # Wait for app to launch
            
        except Exception as e:
            logger.error(f"Failed to launch Liên Quân: {str(e)}")
            raise
    
    async def _take_screenshot(self, workflow_id: int) -> str:
        """Take screenshot and save to local storage"""
        try:
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"lienquan_workflow_{workflow_id}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            # Take screenshot
            subprocess.run(
                ["adb", "shell", "screencap", "/sdcard/screenshot.png"],
                capture_output=True,
                timeout=SCREENSHOT_TIMEOUT
            )
            
            # Pull screenshot to local machine
            subprocess.run(
                ["adb", "pull", "/sdcard/screenshot.png", str(filepath)],
                capture_output=True,
                timeout=SCREENSHOT_TIMEOUT
            )
            
            # Clean up remote file
            subprocess.run(
                ["adb", "shell", "rm", "/sdcard/screenshot.png"],
                capture_output=True,
                timeout=EMULATOR_TIMEOUT
            )
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            raise ScreenshotCaptureError(f"Screenshot capture failed: {str(e)}")
    
    async def _save_screenshot_to_db(self, workflow_id: int, file_path: str) -> Screenshot:
        """Save screenshot information to database"""
        try:
            # Get file information
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size
            
            # Create screenshot record
            screenshot = Screenshot(
                workflow_id=workflow_id,
                file_path=file_path,
                file_name=file_path_obj.name,
                file_size_bytes=file_size,
                mime_type="image/png",
                width=2400,  # Default emulator resolution
                height=1080,
                screenshot_type=ScreenshotType.GAME_LOADING,
                metadata={"source": "automation_workflow"}
            )
            
            self.db_session.add(screenshot)
            await self.db_session.commit()
            await self.db_session.refresh(screenshot)
            
            return screenshot
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to save screenshot to DB: {str(e)}")
            raise
    
    async def _log_workflow_event(
        self, 
        workflow_id: int, 
        level: LogLevel, 
        message: str, 
        step_name: str,
        execution_time_ms: Optional[int] = None
    ):
        """Log workflow event to database"""
        try:
            log = WorkflowLog(
                workflow_id=workflow_id,
                log_level=level,
                message=message,
                step_name=step_name,
                execution_time_ms=execution_time_ms
            )
            
            self.db_session.add(log)
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log workflow event: {str(e)}")
            # Don't raise here to avoid breaking workflow execution
    
    async def get_workflow_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get workflow statistics for a user"""
        try:
            # Get total workflows
            total_query = select(func.count()).where(AutomationWorkflow.user_id == user_id)
            total_result = await self.db_session.execute(total_query)
            total_workflows = total_result.scalar()
            
            # Get completed workflows
            completed_query = select(func.count()).where(
                and_(
                    AutomationWorkflow.user_id == user_id,
                    AutomationWorkflow.status == WorkflowStatus.COMPLETED
                )
            )
            completed_result = await self.db_session.execute(completed_query)
            completed_workflows = completed_result.scalar()
            
            # Get failed workflows
            failed_query = select(func.count()).where(
                and_(
                    AutomationWorkflow.user_id == user_id,
                    AutomationWorkflow.status == WorkflowStatus.FAILED
                )
            )
            failed_result = await self.db_session.execute(failed_query)
            failed_workflows = failed_result.scalar()
            
            # Get running workflows
            running_query = select(func.count()).where(
                and_(
                    AutomationWorkflow.user_id == user_id,
                    AutomationWorkflow.status == WorkflowStatus.RUNNING
                )
            )
            running_result = await self.db_session.execute(running_query)
            running_workflows = running_result.scalar()
            
            # Calculate success rate
            success_rate = 0.0
            if total_workflows > 0:
                success_rate = (completed_workflows / total_workflows) * 100
            
            # Calculate average execution time
            avg_time_query = select(func.avg(
                func.extract('epoch', AutomationWorkflow.completed_at - AutomationWorkflow.started_at)
            )).where(
                and_(
                    AutomationWorkflow.user_id == user_id,
                    AutomationWorkflow.status == WorkflowStatus.COMPLETED,
                    AutomationWorkflow.started_at.isnot(None),
                    AutomationWorkflow.completed_at.isnot(None)
                )
            )
            
            avg_time_result = await self.db_session.execute(avg_time_query)
            average_execution_time = avg_time_result.scalar()
            
            return {
                "total_workflows": total_workflows,
                "completed_workflows": completed_workflows,
                "failed_workflows": failed_workflows,
                "running_workflows": running_workflows,
                "success_rate": round(success_rate, 2),
                "average_execution_time": round(average_execution_time, 2) if average_execution_time else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {str(e)}")
            raise

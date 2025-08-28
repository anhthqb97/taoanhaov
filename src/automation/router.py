"""
API router for Automation module
Following FastAPI best practices with proper documentation and error handling
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse

from src.automation.schemas import (
    AutomationWorkflowCreate, AutomationWorkflowUpdate, AutomationWorkflowResponse,
    WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowStatusResponse,
    AutomationWorkflowListResponse, WorkflowStatistics, ScreenshotListResponse,
    WorkflowLogListResponse, WorkflowQueryParams, ScreenshotQueryParams
)
from src.automation.service import AutomationService
from src.automation.exceptions import (
    handle_automation_exception, WorkflowNotFoundError, WorkflowAlreadyRunningError
)
from src.database import get_db_session_dependency
from src.auth.dependencies import get_current_user
from src.auth.schemas import UserResponse

# Create router
router = APIRouter(prefix="/automation", tags=["Automation"])

# Dependency for automation service
async def get_automation_service(
    db_session = Depends(get_db_session_dependency)
) -> AutomationService:
    """Get automation service instance"""
    return AutomationService(db_session)


@router.post(
    "/workflows",
    response_model=AutomationWorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Automation Workflow",
    description="Create a new automation workflow for Liên Quân Mobile",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Workflow created successfully",
            "model": AutomationWorkflowResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error"
        }
    }
)
async def create_workflow(
    workflow_data: AutomationWorkflowCreate,
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Create a new automation workflow"""
    try:
        workflow = await automation_service.create_workflow(
            workflow_data, 
            current_user.id
        )
        return workflow
        
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/workflows",
    response_model=AutomationWorkflowListResponse,
    summary="Get User Workflows",
    description="Get paginated list of user's automation workflows",
    responses={
        status.HTTP_200_OK: {
            "description": "List of workflows retrieved successfully",
            "model": AutomationWorkflowListResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        }
    }
)
async def get_workflows(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    workflow_type: Optional[str] = Query(None, description="Filter by workflow type"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get user's automation workflows with pagination and filtering"""
    try:
        workflows, total_count = await automation_service.get_user_workflows(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            status=status,
            workflow_type=workflow_type
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return AutomationWorkflowListResponse(
            workflows=workflows,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/workflows/{workflow_id}",
    response_model=AutomationWorkflowResponse,
    summary="Get Workflow by ID",
    description="Get specific automation workflow by ID",
    responses={
        status.HTTP_200_OK: {
            "description": "Workflow retrieved successfully",
            "model": AutomationWorkflowResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def get_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get specific workflow by ID"""
    try:
        workflow = await automation_service.get_workflow(
            workflow_id, 
            current_user.id
        )
        return workflow
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.put(
    "/workflows/{workflow_id}",
    response_model=AutomationWorkflowResponse,
    summary="Update Workflow",
    description="Update existing automation workflow",
    responses={
        status.HTTP_200_OK: {
            "description": "Workflow updated successfully",
            "model": AutomationWorkflowResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input or workflow cannot be updated"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def update_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    update_data: AutomationWorkflowUpdate = ...,
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Update existing workflow"""
    try:
        workflow = await automation_service.update_workflow(
            workflow_id, 
            current_user.id, 
            update_data
        )
        return workflow
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except WorkflowAlreadyRunningError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update running workflow"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.delete(
    "/workflows/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Workflow",
    description="Delete automation workflow",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Workflow deleted successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def delete_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Delete workflow"""
    try:
        # TODO: Implement delete functionality in service
        # await automation_service.delete_workflow(workflow_id, current_user.id)
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/workflows/{workflow_id}/execute",
    response_model=WorkflowExecutionResponse,
    summary="Execute Workflow",
    description="Execute automation workflow",
    responses={
        status.HTTP_200_OK: {
            "description": "Workflow execution started successfully",
            "model": WorkflowExecutionResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Workflow cannot be executed"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def execute_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    execution_request: WorkflowExecutionRequest = ...,
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Execute automation workflow"""
    try:
        result = await automation_service.execute_workflow(
            workflow_id, 
            current_user.id, 
            execution_request.force_restart
        )
        return WorkflowExecutionResponse(**result)
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except WorkflowAlreadyRunningError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is already running"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/workflows/{workflow_id}/status",
    response_model=WorkflowStatusResponse,
    summary="Get Workflow Status",
    description="Get current status of automation workflow",
    responses={
        status.HTTP_200_OK: {
            "description": "Workflow status retrieved successfully",
            "model": WorkflowStatusResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def get_workflow_status(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get workflow status"""
    try:
        workflow = await automation_service.get_workflow(
            workflow_id, 
            current_user.id
        )
        
        # Calculate progress percentage based on workflow type and current step
        progress_percentage = None
        current_step = None
        
        if workflow.status == "running":
            # TODO: Implement progress calculation based on workflow logs
            progress_percentage = 50
            current_step = "executing"
        
        return WorkflowStatusResponse(
            workflow_id=workflow.id,
            status=workflow.status,
            progress_percentage=progress_percentage,
            current_step=current_step,
            started_at=workflow.started_at,
            estimated_completion=None  # TODO: Implement estimation
        )
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/workflows/{workflow_id}/screenshots",
    response_model=ScreenshotListResponse,
    summary="Get Workflow Screenshots",
    description="Get screenshots captured during workflow execution",
    responses={
        status.HTTP_200_OK: {
            "description": "Screenshots retrieved successfully",
            "model": ScreenshotListResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def get_workflow_screenshots(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get screenshots for specific workflow"""
    try:
        # Verify workflow exists and user has access
        await automation_service.get_workflow(workflow_id, current_user.id)
        
        # TODO: Implement screenshot retrieval from service
        # screenshots, total_count = await automation_service.get_workflow_screenshots(
        #     workflow_id, page, page_size
        # )
        
        # Placeholder response
        return ScreenshotListResponse(
            screenshots=[],
            total_count=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/workflows/{workflow_id}/logs",
    response_model=WorkflowLogListResponse,
    summary="Get Workflow Logs",
    description="Get execution logs for automation workflow",
    responses={
        status.HTTP_200_OK: {
            "description": "Workflow logs retrieved successfully",
            "model": WorkflowLogListResponse
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def get_workflow_logs(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get logs for specific workflow"""
    try:
        # Verify workflow exists and user has access
        await automation_service.get_workflow(workflow_id, current_user.id)
        
        # TODO: Implement log retrieval from service
        # logs, total_count = await automation_service.get_workflow_logs(
        #     workflow_id, page, page_size, log_level
        # )
        
        # Placeholder response
        return WorkflowLogListResponse(
            logs=[],
            total_count=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.get(
    "/statistics",
    response_model=WorkflowStatistics,
    summary="Get Workflow Statistics",
    description="Get automation workflow statistics for current user",
    responses={
        status.HTTP_200_OK: {
            "description": "Statistics retrieved successfully",
            "model": WorkflowStatistics
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        }
    }
)
async def get_workflow_statistics(
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Get workflow statistics for current user"""
    try:
        statistics = await automation_service.get_workflow_statistics(current_user.id)
        return WorkflowStatistics(**statistics)
        
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )


@router.post(
    "/workflows/{workflow_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel Workflow",
    description="Cancel running automation workflow",
    responses={
        status.HTTP_200_OK: {
            "description": "Workflow cancelled successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Workflow cannot be cancelled"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found"
        }
    }
)
async def cancel_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    current_user: UserResponse = Depends(get_current_user),
    automation_service: AutomationService = Depends(get_automation_service)
):
    """Cancel running workflow"""
    try:
        # TODO: Implement cancel functionality in service
        # await automation_service.cancel_workflow(workflow_id, current_user.id)
        
        return {
            "message": "Workflow cancelled successfully",
            "workflow_id": workflow_id
        }
        
    except WorkflowNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    except Exception as e:
        error_response = handle_automation_exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )

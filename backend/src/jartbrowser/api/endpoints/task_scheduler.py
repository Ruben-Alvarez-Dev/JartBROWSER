"""Task Scheduler API endpoints"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from jartbrowser.services.task_scheduler import (
    TaskSchedulerService,
    ScheduleType,
    TaskStatus,
    TaskPriority,
    get_task_scheduler,
)


router = APIRouter()

task_scheduler: TaskSchedulerService = get_task_scheduler()


class TaskCreate(BaseModel):
    name: str
    description: str = ""
    task_type: str
    task_config: dict = {}
    schedule_type: ScheduleType = ScheduleType.ONE_TIME
    schedule_config: dict = {}
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    timeout: int = 300


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    task_config: Optional[dict] = None
    schedule_config: Optional[dict] = None
    enabled: Optional[bool] = None
    max_retries: Optional[int] = None
    timeout: Optional[int] = None


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate):
    """Create a scheduled task"""
    task = task_scheduler.create_task(
        name=payload.name,
        task_type=payload.task_type,
        schedule_type=payload.schedule_type,
        schedule_config=payload.schedule_config,
        task_config=payload.task_config,
        description=payload.description,
        priority=payload.priority,
        max_retries=payload.max_retries,
        timeout=payload.timeout,
    )
    return task.to_dict()


@router.get("/tasks")
async def list_tasks(
    status: Optional[TaskStatus] = None,
    task_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    limit: int = 50,
):
    """List scheduled tasks"""
    tasks = task_scheduler.get_tasks(
        status=status,
        task_type=task_type,
        enabled=enabled,
        limit=limit,
    )
    return [t.to_dict() for t in tasks]


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a task"""
    task = task_scheduler.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.put("/tasks/{task_id}")
async def update_task(task_id: str, payload: TaskUpdate):
    """Update a task"""
    task = task_scheduler.update_task(
        task_id,
        name=payload.name,
        description=payload.description,
        task_config=payload.task_config,
        schedule_config=payload.schedule_config,
        enabled=payload.enabled,
        max_retries=payload.max_retries,
        timeout=payload.timeout,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    if not task_scheduler.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}


@router.post("/tasks/{task_id}/enable")
async def enable_task(task_id: str):
    """Enable a task"""
    if not task_scheduler.enable_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "enabled"}


@router.post("/tasks/{task_id}/disable")
async def disable_task(task_id: str):
    """Disable a task"""
    if not task_scheduler.disable_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "disabled"}


@router.post("/tasks/{task_id}/run")
async def run_task(task_id: str):
    """Run a task immediately"""
    execution = await task_scheduler.run_task_now(task_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": execution.id,
        "task_id": execution.task_id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
    }


@router.get("/tasks/{task_id}/executions")
async def list_task_executions(task_id: str, status: Optional[str] = None, limit: int = 20):
    """List task executions"""
    executions = task_scheduler.get_executions(task_id=task_id, status=status, limit=limit)
    return [
        {
            "id": e.id,
            "task_id": e.task_id,
            "status": e.status,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            "result": e.result,
            "error": e.error,
        }
        for e in executions
    ]


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution"""
    execution = task_scheduler.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {
        "id": execution.id,
        "task_id": execution.task_id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "result": execution.result,
        "error": execution.error,
    }


@router.get("/tasks/upcoming")
async def get_upcoming_tasks(hours: int = 24):
    """Get upcoming tasks"""
    tasks = task_scheduler.get_upcoming_tasks(hours=hours)
    return [t.to_dict() for t in tasks]


@router.get("/tasks/{task_id}/export")
async def export_task(task_id: str):
    """Export task as JSON"""
    data = task_scheduler.export_task(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return data


@router.post("/tasks/import")
async def import_task(data: dict):
    """Import task from JSON"""
    task = task_scheduler.import_task(data)
    return task.to_dict()

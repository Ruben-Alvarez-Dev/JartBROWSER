"""Agent API endpoints"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from jartbrowser.models.schemas import AgentTask, AgentTaskResponse, AgentStatusResponse

router = APIRouter()


# In-memory task storage (would be database in production)
_agent_tasks: Dict[str, Dict[str, Any]] = {}


@router.post("/agent/task", response_model=AgentTaskResponse)
async def create_agent_task(task: AgentTask):
    """Create a new agent task"""
    task_id = str(uuid.uuid4())

    _agent_tasks[task_id] = {
        "task_id": task_id,
        "task": task.task,
        "context": task.context or {},
        "max_steps": task.max_steps,
        "status": "pending",
        "result": None,
        "error": None,
        "steps_completed": 0,
        "created_at": asyncio.get_event_loop().time(),
    }

    # Start task in background
    asyncio.create_task(run_agent_task(task_id))

    return AgentTaskResponse(task_id=task_id, status="pending", steps_completed=0)


async def run_agent_task(task_id: str):
    """Run agent task in background"""
    if task_id not in _agent_tasks:
        return

    task_data = _agent_tasks[task_id]
    task_data["status"] = "running"

    try:
        # Simulate agent execution
        # In production, this would:
        # 1. Get page context from Chrome extension
        # 2. Use LLM to reason about actions
        # 3. Execute browser actions
        # 4. Continue until task complete or max_steps

        for step in range(task_data["max_steps"]):
            task_data["steps_completed"] = step + 1

            # Simulate work
            await asyncio.sleep(0.5)

            # Check if should continue
            if step >= task_data["max_steps"] - 1:
                break

        # Mark as completed
        task_data["status"] = "completed"
        task_data["result"] = {
            "success": True,
            "message": "Task completed",
            "steps": task_data["steps_completed"],
        }

    except Exception as e:
        task_data["status"] = "failed"
        task_data["error"] = str(e)


@router.get("/agent/task/{task_id}", response_model=AgentTaskResponse)
async def get_agent_task(task_id: str):
    """Get status of an agent task"""
    if task_id not in _agent_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = _agent_tasks[task_id]

    return AgentTaskResponse(
        task_id=task_data["task_id"],
        status=task_data["status"],
        result=task_data.get("result"),
        error=task_data.get("error"),
        steps_completed=task_data["steps_completed"],
    )


@router.get("/agent/tasks", response_model=List[AgentTaskResponse])
async def list_agent_tasks(status: Optional[str] = None):
    """List all agent tasks"""
    tasks = list(_agent_tasks.values())

    if status:
        tasks = [t for t in tasks if t["status"] == status]

    return [
        AgentTaskResponse(
            task_id=t["task_id"],
            status=t["status"],
            result=t.get("result"),
            error=t.get("error"),
            steps_completed=t["steps_completed"],
        )
        for t in tasks
    ]


@router.delete("/agent/task/{task_id}")
async def cancel_agent_task(task_id: str):
    """Cancel an agent task"""
    if task_id not in _agent_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    _agent_tasks[task_id]["status"] = "cancelled"

    return {"success": True, "message": "Task cancelled"}


@router.get("/agent/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """Get overall agent status"""
    tasks = list(_agent_tasks.values())

    active = len([t for t in tasks if t["status"] == "running"])
    completed = len([t for t in tasks if t["status"] == "completed"])
    failed = len([t for t in tasks if t["status"] == "failed"])

    return AgentStatusResponse(
        active_tasks=active, completed_tasks=completed, failed_tasks=failed, total_tokens_used=0
    )


@router.post("/agent/chat")
async def agent_chat(message: str, context: Optional[Dict[str, Any]] = None):
    """Simple chat with agent (uses LLM)"""
    # Placeholder - would integrate with LLM provider
    return {
        "response": f"Echo: {message}",
        "context_used": bool(context),
        "model_used": "placeholder",
    }

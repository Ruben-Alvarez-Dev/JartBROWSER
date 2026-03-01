"""
Task Scheduling Service

Provides task scheduling with cron support, one-time and recurring tasks.
"""

import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
import json
import croniter


class ScheduleType(Enum):
    """Schedule types"""

    ONE_TIME = "one_time"
    RECURRING = "recurring"
    CRON = "cron"
    INTERVAL = "interval"


class TaskStatus(Enum):
    """Task status"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ScheduledTask:
    """Scheduled task definition"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: str = ""  # workflow, action, script
    task_config: Dict[str, Any] = field(default_factory=dict)
    schedule_type: ScheduleType = ScheduleType.ONE_TIME
    schedule_config: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    max_retries: int = 3
    retry_count: int = 0
    timeout: int = 300  # seconds
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "task_config": self.task_config,
            "schedule_type": self.schedule_type.value,
            "schedule_config": self.schedule_config,
            "priority": self.priority.value,
            "status": self.status.value,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "metadata": self.metadata,
        }


@dataclass
class TaskExecution:
    """Task execution record"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class TaskSchedulerService:
    """
    Service for scheduling and executing tasks.

    Provides:
    - One-time, recurring, cron, and interval scheduling
    - Task execution with timeout and retries
    - Task history and logging
    - Task enable/disable
    """

    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._executions: Dict[str, TaskExecution] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._scheduler_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._handlers: Dict[str, Callable[[ScheduledTask], Awaitable[Dict[str, Any]]]] = {}
        self._check_interval = 10  # seconds

    def register_handler(
        self, task_type: str, handler: Callable[[ScheduledTask], Awaitable[Dict[str, Any]]]
    ) -> None:
        """Register a task handler"""
        self._handlers[task_type] = handler

    async def start(self) -> None:
        """Start the scheduler"""
        if self._is_running:
            return
        self._is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        # Calculate next run times for all enabled tasks
        for task in self._tasks.values():
            if task.enabled and task.status == TaskStatus.SCHEDULED:
                self._calculate_next_run(task)

    async def stop(self) -> None:
        """Stop the scheduler"""
        self._is_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        # Cancel running tasks
        for task in self._running_tasks.values():
            task.cancel()

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self._is_running:
            try:
                await self._check_and_run_tasks()
            except Exception as e:
                pass
            await asyncio.sleep(self._check_interval)

    async def _check_and_run_tasks(self) -> None:
        """Check for tasks to run"""
        now = datetime.utcnow()
        for task in self._tasks.values():
            if not task.enabled:
                continue
            if task.status not in (TaskStatus.SCHEDULED, TaskStatus.PENDING):
                continue
            if task.next_run and task.next_run <= now:
                await self._execute_task(task)

    def _calculate_next_run(self, task: ScheduledTask) -> None:
        """Calculate next run time for a task"""
        if task.schedule_type == ScheduleType.ONE_TIME:
            # Already set
            pass
        elif task.schedule_type == ScheduleType.INTERVAL:
            interval = task.schedule_config.get("interval_seconds", 3600)
            if task.last_run:
                task.next_run = task.last_run + timedelta(seconds=interval)
            else:
                task.next_run = datetime.utcnow() + timedelta(seconds=interval)
        elif task.schedule_type == ScheduleType.CRON:
            cron_expr = task.schedule_config.get("cron", "")
            if cron_expr:
                try:
                    cron = croniter.croniter(cron_expr, datetime.utcnow())
                    task.next_run = cron.get_next(datetime)
                except Exception:
                    pass
        elif task.schedule_type == ScheduleType.RECURRING:
            # Similar to interval
            interval = task.schedule_config.get("interval_seconds", 3600)
            if task.last_run:
                task.next_run = task.last_run + timedelta(seconds=interval)
            else:
                task.next_run = datetime.utcnow() + timedelta(seconds=interval)

    # ============== Task CRUD ==============

    def create_task(
        self,
        name: str,
        task_type: str,
        schedule_type: ScheduleType = ScheduleType.ONE_TIME,
        schedule_config: Optional[Dict[str, Any]] = None,
        task_config: Optional[Dict[str, Any]] = None,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        timeout: int = 300,
    ) -> ScheduledTask:
        """Create a new scheduled task"""
        task = ScheduledTask(
            name=name,
            description=description,
            task_type=task_type,
            task_config=task_config or {},
            schedule_type=schedule_type,
            schedule_config=schedule_config or {},
            priority=priority,
            max_retries=max_retries,
            timeout=timeout,
        )

        # Calculate initial next run
        if schedule_type == ScheduleType.ONE_TIME:
            run_at = schedule_config.get("run_at") if schedule_config else None
            if run_at:
                if isinstance(run_at, str):
                    task.next_run = datetime.fromisoformat(run_at)
                else:
                    task.next_run = run_at
            task.status = TaskStatus.SCHEDULED if task.next_run else TaskStatus.PENDING
        else:
            self._calculate_next_run(task)
            task.status = TaskStatus.SCHEDULED

        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task"""
        return self._tasks.get(task_id)

    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        limit: int = 50,
    ) -> List[ScheduledTask]:
        """Get tasks"""
        results = list(self._tasks.values())

        if status:
            results = [t for t in results if t.status == status]
        if task_type:
            results = [t for t in results if t.task_type == task_type]
        if enabled is not None:
            results = [t for t in results if t.enabled == enabled]

        # Sort by priority (desc) then by next_run
        results.sort(key=lambda t: (-t.priority.value, t.next_run or datetime.max))
        return results[:limit]

    def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        task_config: Optional[Dict[str, Any]] = None,
        schedule_config: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
        max_retries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> Optional[ScheduledTask]:
        """Update a task"""
        task = self._tasks.get(task_id)
        if not task:
            return None

        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if task_config is not None:
            task.task_config = task_config
        if schedule_config is not None:
            task.schedule_config = schedule_config
            self._calculate_next_run(task)
        if enabled is not None:
            task.enabled = enabled
            if enabled and task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.SCHEDULED
        if max_retries is not None:
            task.max_retries = max_retries
        if timeout is not None:
            task.timeout = timeout

        task.updated_at = datetime.utcnow()
        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def enable_task(self, task_id: str) -> bool:
        """Enable a task"""
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.enabled = True
        if task.status == TaskStatus.PAUSED:
            task.status = TaskStatus.SCHEDULED
            self._calculate_next_run(task)
        task.updated_at = datetime.utcnow()
        return True

    def disable_task(self, task_id: str) -> bool:
        """Disable a task"""
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.enabled = False
        task.updated_at = datetime.utcnow()
        return True

    # ============== Execution ==============

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a task"""
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.utcnow()

        execution = TaskExecution(
            task_id=task.id,
            status="running",
            started_at=datetime.utcnow(),
        )
        self._executions[execution.id] = execution

        try:
            handler = self._handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")

            # Run with timeout
            result = await asyncio.wait_for(handler(task), timeout=task.timeout)

            execution.status = "completed"
            execution.result = result
            task.status = TaskStatus.COMPLETED
            task.last_run = datetime.utcnow()

        except asyncio.TimeoutError:
            execution.status = "failed"
            execution.error = f"Task timed out after {task.timeout} seconds"
            task.retry_count += 1
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.SCHEDULED
            else:
                task.status = TaskStatus.FAILED

        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            task.retry_count += 1
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.SCHEDULED
            else:
                task.status = TaskStatus.FAILED

        execution.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        # Calculate next run for recurring tasks
        if task.schedule_type != ScheduleType.ONE_TIME and task.status == TaskStatus.COMPLETED:
            self._calculate_next_run(task)
            task.status = TaskStatus.SCHEDULED

    async def run_task_now(self, task_id: str) -> Optional[TaskExecution]:
        """Run a task immediately"""
        task = self._tasks.get(task_id)
        if not task:
            return None

        await self._execute_task(task)
        return self._executions.get(task.id)

    def get_execution(self, execution_id: str) -> Optional[TaskExecution]:
        """Get an execution"""
        return self._executions.get(execution_id)

    def get_executions(
        self,
        task_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[TaskExecution]:
        """Get executions"""
        results = list(self._executions.values())

        if task_id:
            results = [e for e in results if e.task_id == task_id]
        if status:
            results = [e for e in results if e.status == status]

        results.sort(key=lambda e: e.created_at, reverse=True)
        return results[:limit]

    # ============== Import/Export ==============

    def export_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Export task as JSON"""
        task = self._tasks.get(task_id)
        if not task:
            return None
        return task.to_dict()

    def import_task(self, data: Dict[str, Any]) -> ScheduledTask:
        """Import task from JSON"""
        task = ScheduledTask(
            name=data.get("name", "Imported Task"),
            description=data.get("description", ""),
            task_type=data.get("task_type", ""),
            task_config=data.get("task_config", {}),
            schedule_type=ScheduleType(data.get("schedule_type", "one_time")),
            schedule_config=data.get("schedule_config", {}),
            priority=TaskPriority(data.get("priority", 2)),
            max_retries=data.get("max_retries", 3),
            timeout=data.get("timeout", 300),
            enabled=data.get("enabled", True),
        )
        self._tasks[task.id] = task
        return task

    def get_upcoming_tasks(self, hours: int = 24) -> List[ScheduledTask]:
        """Get upcoming tasks within specified hours"""
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)

        results = [
            t for t in self._tasks.values() if t.enabled and t.next_run and t.next_run <= end_time
        ]
        results.sort(key=lambda t: t.next_run or datetime.max)
        return results


# Singleton
_task_scheduler: Optional[TaskSchedulerService] = None


def get_task_scheduler() -> TaskSchedulerService:
    """Get the task scheduler service instance"""
    global _task_scheduler
    if _task_scheduler is None:
        _task_scheduler = TaskSchedulerService()
    return _task_scheduler

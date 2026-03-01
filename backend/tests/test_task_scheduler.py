import pytest
from datetime import datetime, timedelta

from jartbrowser.services.task_scheduler import TaskSchedulerService, ScheduleType, TaskPriority


def build_service():
    # Fresh in-memory store per test
    return TaskSchedulerService()


def get_id(task):
    if hasattr(task, "id"):
        return task.id
    if isinstance(task, dict):
        return task.get("id")
    return None


def get_priority(task):
    if hasattr(task, "priority"):
        return task.priority
    if isinstance(task, dict):
        return task.get("priority")
    return None


def test_create_and_get_one_time_task():
    service = build_service()
    run_at = datetime.utcnow() + timedelta(days=1)
    task_id = service.create_task(
        name="OneTimeTask",
        schedule_type=ScheduleType.ONE_TIME,
        run_at=run_at.isoformat(),
        priority=TaskPriority.MEDIUM,
    )
    task = service.get_task(task_id)
    assert get_id(task) == task_id
    assert (
        getattr(task, "schedule_type", None) == ScheduleType.ONE_TIME
        or task.get("schedule_type") == ScheduleType.ONE_TIME
    )
    assert getattr(task, "enabled", True) is True


def test_create_and_get_recurring_task():
    service = build_service()
    task_id = service.create_task(
        name="RecurringTask",
        schedule_type=ScheduleType.RECURRING,
        cron="*/5 * * * *",
        priority=TaskPriority.LOW,
    )
    task = service.get_task(task_id)
    assert get_id(task) == task_id
    assert (
        getattr(task, "schedule_type", None) == ScheduleType.RECURRING
        or task.get("schedule_type") == ScheduleType.RECURRING
    )
    cron = getattr(task, "cron", None) if hasattr(task, "__dict__") else task.get("cron")
    assert cron == "*/5 * * * *"
    assert getattr(task, "enabled", True) is True


def test_get_tasks_with_filters():
    service = build_service()
    t1 = service.create_task(
        name="TaskA",
        schedule_type=ScheduleType.ONE_TIME,
        run_at=(datetime.utcnow() + timedelta(days=1)).isoformat(),
        priority=TaskPriority.HIGH,
    )
    t2 = service.create_task(
        name="TaskB",
        schedule_type=ScheduleType.RECURRING,
        cron="0 1 * * *",
        priority=TaskPriority.MEDIUM,
    )
    # No filters
    tasks = service.get_tasks()
    assert isinstance(tasks, list)
    assert any(get_id(t) == t1 for t in tasks)
    assert any(get_id(t) == t2 for t in tasks)
    # Filter by priority HIGH
    high_tasks = service.get_tasks(priority=TaskPriority.HIGH)
    assert isinstance(high_tasks, list)
    assert any(get_id(t) == t1 for t in high_tasks)
    # Filter by enabled state
    enabled_tasks = service.get_tasks(enabled=True)
    assert isinstance(enabled_tasks, list)
    assert all(getattr(t, "enabled", True) for t in enabled_tasks)


def test_enable_disable_and_delete_task():
    service = build_service()
    task_id = service.create_task(
        name="ToggleTask",
        schedule_type=ScheduleType.ONE_TIME,
        run_at=(datetime.utcnow() + timedelta(days=2)).isoformat(),
        priority=TaskPriority.MEDIUM,
    )
    # Disable
    service.disable_task(task_id)
    t = service.get_task(task_id)
    assert getattr(t, "enabled", True) is False
    # Enable
    service.enable_task(task_id)
    t = service.get_task(task_id)
    assert getattr(t, "enabled", True) is True
    # Delete
    service.delete_task(task_id)
    with pytest.raises(Exception):
        service.get_task(task_id)


def test_get_executions_for_task():
    service = build_service()
    task_id = service.create_task(
        name="ExecTask",
        schedule_type=ScheduleType.ONE_TIME,
        run_at=(datetime.utcnow() + timedelta(days=1)).isoformat(),
        priority=TaskPriority.LOW,
    )
    exes = service.get_executions(task_id)
    assert isinstance(exes, list)

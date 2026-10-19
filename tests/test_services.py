"""
Unit tests for TaskService and UserService business logic.
"""

import pytest
from src.services import TaskService, UserService
from src.models import TaskPriority, TaskStatus


def test_task_creation_and_retrieval():
    service = TaskService()
    task = service.create_task(
        title="Setup CI/CD Pipeline",
        description="Configure GitHub Actions with DevSecOps quality gates",
        priority="high",
        assigned_to="dhiopatty"
    )

    assert task.task_id.startswith("TSK-")
    assert task.title == "Setup CI/CD Pipeline"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.PENDING

    fetched = service.get_task(task.task_id)
    assert fetched is not None
    assert fetched.title == task.title


def test_task_status_update():
    service = TaskService()
    task = service.create_task(
        title="Implement SAST Analysis",
        description="Integrate Bandit into the workflow"
    )
    updated = service.update_task_status(task.task_id, "in_progress")
    assert updated.status == TaskStatus.IN_PROGRESS


def test_task_deletion():
    service = TaskService()
    task = service.create_task(
        title="Temporary Task",
        description="Will be deleted"
    )
    deleted = service.delete_task(task.task_id)
    assert deleted is True
    assert service.get_task(task.task_id) is None


def test_user_registration_and_authentication():
    service = UserService()
    user = service.register_user(
        username="dhiopatty",
        email="dhio@example.com",
        password="SuperSecretPassword123!"
    )
    assert user.username == "dhiopatty"

    # Authenticate with valid password
    auth_user = service.authenticate("dhiopatty", "SuperSecretPassword123!")
    assert auth_user is not None
    assert auth_user.user_id == user.user_id

    # Authenticate with invalid password
    invalid_auth = service.authenticate("dhiopatty", "WrongPassword123")
    assert invalid_auth is None


def test_user_duplicate_registration_fails():
    service = UserService()
    service.register_user("alexander", "alex@example.com", "Password123!")
    with pytest.raises(ValueError):
        service.register_user("alexander", "other@example.com", "Password123!")

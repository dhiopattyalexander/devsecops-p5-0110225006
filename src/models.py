"""
Data models and schema definitions for the Task Management System.
Implements validation and data integrity checks.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class User:
    """User entity representing authenticated members."""

    def __init__(self, user_id: str, username: str, email: str, role: str = "developer"):
        self.user_id = user_id
        self.username = self._validate_username(username)
        self.email = self._validate_email(email)
        self.role = role
        self.created_at = datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _validate_username(username: str) -> str:
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        return username.strip()

    @staticmethod
    def _validate_email(email: str) -> str:
        if not email or "@" not in email or "." not in email:
            raise ValueError("Invalid email format provided.")
        return email.strip().lower()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at
        }


class Task:
    """Task entity representing a trackable unit of work."""

    def __init__(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_to: Optional[str] = None
    ):
        self.task_id = task_id
        self.title = self._validate_title(title)
        self.description = description
        self.priority = priority if isinstance(priority, TaskPriority) else TaskPriority(priority)
        self.status = TaskStatus.PENDING
        self.assigned_to = assigned_to
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at

    @staticmethod
    def _validate_title(title: str) -> str:
        if not title or len(title.strip()) < 4:
            raise ValueError("Task title must be at least 4 characters long.")
        return title.strip()

    def update_status(self, new_status: TaskStatus) -> None:
        self.status = new_status if isinstance(new_status, TaskStatus) else TaskStatus(new_status)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

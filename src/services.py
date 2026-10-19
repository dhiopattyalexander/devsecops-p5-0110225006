"""
Business logic services managing tasks and user lifecycles.
"""

from typing import List, Optional, Dict, Any
import uuid
from .models import Task, User, TaskPriority, TaskStatus
from .security import SecurityManager
from .utils import setup_logger

logger = setup_logger("services")


class UserService:
    """Service handling user registration and credential validation."""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._credentials: Dict[str, Dict[str, str]] = {}

    def register_user(self, username: str, email: str, password: str, role: str = "developer") -> User:
        for u in self._users.values():
            if u.username == username:
                raise ValueError("Username already exists.")
            if u.email == email:
                raise ValueError("Email already registered.")

        user_id = str(uuid.uuid4())[:8]
        user = User(user_id=user_id, username=username, email=email, role=role)
        pw_hash, salt = SecurityManager.hash_password(password)

        self._users[user_id] = user
        self._credentials[user_id] = {"hash": pw_hash, "salt": salt}
        logger.info(f"User registered successfully: {username} (ID: {user_id})")
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        for uid, u in self._users.items():
            if u.username == username:
                creds = self._credentials.get(uid)
                if creds and SecurityManager.verify_password(password, creds["hash"], creds["salt"]):
                    logger.info(f"User authenticated: {username}")
                    return u
        logger.warning(f"Failed authentication attempt for: {username}")
        return None

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def list_users(self) -> List[Dict[str, Any]]:
        return [u.to_dict() for u in self._users.values()]


class TaskService:
    """Service handling task creation, status updates, and assignment."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def create_task(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        assigned_to: Optional[str] = None
    ) -> Task:
        task_id = f"TSK-{uuid.uuid4().hex[:6].upper()}"
        clean_title = SecurityManager.sanitize_input(title)
        clean_desc = SecurityManager.sanitize_input(description)

        task = Task(
            task_id=task_id,
            title=clean_title,
            description=clean_desc,
            priority=TaskPriority(priority.lower()),
            assigned_to=assigned_to
        )
        self._tasks[task_id] = task
        logger.info(f"Task created: {task_id} - '{clean_title}'")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_task_status(self, task_id: str, new_status: str) -> Task:
        task = self.get_task(task_id)
        if not task:
            raise KeyError(f"Task with ID {task_id} does not exist.")

        task.update_status(TaskStatus(new_status.lower()))
        logger.info(f"Task {task_id} status updated to {new_status}")
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [
                t.to_dict() for t in self._tasks.values()
                if t.status.value == status.lower()
            ]
        return [t.to_dict() for t in self._tasks.values()]

    def delete_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.info(f"Task deleted: {task_id}")
            return True
        return False

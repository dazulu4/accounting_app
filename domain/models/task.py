from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone


class TaskStatus(str, Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task:
    def __init__(self, task_id: UUID, title: str, description: str, user_id: UUID):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.user_id = user_id
        self.status = TaskStatus.NEW
        self.created_at = datetime.now(timezone.utc)
        self.completed_at = None

    def complete(self):
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc)

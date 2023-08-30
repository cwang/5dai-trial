"""Task models."""

from dataclasses import dataclass
from datetime import datetime

from fastapi import UploadFile

from .common import (
    ConversationInfo,
    FileInfo,
    IdentityAware,
    TaskStatus,
)


class TaskConversation(IdentityAware, ConversationInfo):
    """Task conversation."""

    pass


class TaskFile(IdentityAware, FileInfo):
    """Task file."""

    pass


@dataclass
class TaskUserInput:
    """Task user input."""

    question: str
    files: list[UploadFile]


class CreateTaskRequest(TaskUserInput):
    """Create task request."""

    pass


class UpdateTaskRequest(TaskUserInput):
    """Update task request."""

    pass


class TaskActionResponse(IdentityAware):
    """Task action response."""

    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class ReadTaskResponse(TaskActionResponse):
    """Read task response."""

    conversations: list[TaskConversation] = []
    files: list[TaskFile] = []

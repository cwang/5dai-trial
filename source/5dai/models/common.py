"""Common models."""

from abc import abstractmethod
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""

    created = "created"
    started = "started"
    completed = "completed"
    cancelled = "cancelled"
    stopped = "stopped"


@abstractmethod
class IdentityAware(BaseModel):
    """Identity aware, i.e. with a `id_` field."""

    id_: int = Field(..., alias="id")


@abstractmethod
class ConversationInfo(BaseModel):
    """Conversation info."""

    question: str
    answer: str | None
    generated_at: datetime


@abstractmethod
class FileInfo(BaseModel):
    """File info."""

    name: str
    size: int
    content_type: str
    uploaded_at: datetime

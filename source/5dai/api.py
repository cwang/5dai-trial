"""API layer for the module."""

import logging as log
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from .models import tasks as models
from .services import tasks as services
from .support.store import init_database

load_dotenv()

log.basicConfig()
log.getLogger().setLevel(os.getenv("APP_LOG_LEVEL", "INFO"))

init_database()

app = FastAPI()


@app.post("/tasks")
async def create_task(
    background_tasks: BackgroundTasks,
    question: Annotated[str, Form()],
    files: Annotated[list[UploadFile], File()] = [],
) -> models.TaskActionResponse:
    """Create a task."""
    log.debug("create_task(): question=%s, files=%s", question, files)
    response = services.create_task(models.CreateTaskRequest(question, files))
    background_tasks.add_task(services.run_task, response.id_)
    return response


@app.post("/tasks/{id_}")
async def update_task(
    background_tasks: BackgroundTasks,
    id_: int,
    question: Annotated[str, Form()],
    files: Annotated[list[UploadFile], File()] = [],
) -> models.TaskActionResponse:
    """Update a task."""
    try:
        response = services.update_task(
            id_, models.UpdateTaskRequest(question, files)
        )
        background_tasks.add_task(services.run_task, response.id_)
        return response
    except Exception as e:
        log.exception("Error updating task %s: %s", id_, e)
        raise HTTPException(400, "Error updating task") from e


@app.delete("/tasks/{id_}")
async def cancel_task():
    """Cancel a task."""
    pass


@app.get("/tasks/{id_}")
async def read_task(id_: int) -> models.ReadTaskResponse:
    """Read a task."""
    response = services.get_task(id_)
    if response is None:
        raise HTTPException(404, "Task not found")
    return response


@app.get("/tasks/{task_id}/files/{file_id}")
async def download_file() -> FileResponse:
    return FileResponse()

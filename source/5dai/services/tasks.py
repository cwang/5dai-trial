"""Task service."""

import logging
import sqlite3
from contextlib import closing
from datetime import datetime

from ..models.common import TaskStatus
from ..models.tasks import (
    CreateTaskRequest,
    ReadTaskResponse,
    TaskActionResponse,
    TaskConversation,
    TaskFile,
    TaskUserInput,
    UpdateTaskRequest,
)
from ..support.llm import reindex, run_ask, run_chat
from ..support.paths import (
    get_sqlite_file_path,
    get_upload_dir_path,
    get_upload_file_path,
)

log = logging.getLogger("services.tasks")


def _query_task(
    id_: int, extras: bool = False
) -> TaskActionResponse | ReadTaskResponse | None:
    log.debug("_query_task(): Getting task with id=%d", id_)
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        row = cursor.execute(
            "SELECT id, status, created_at, updated_at FROM tasks WHERE id = ?",
            (id_,),
        ).fetchone()
        log.debug("_query_task(): Got row: %s", row)

        if extras:
            conversation_rows = cursor.execute(
                "SELECT id, question, answer, generated_at FROM task_conversations WHERE task_id = ? ORDER BY generated_at ASC",
                (id_,),
            ).fetchall()
            log.debug(
                "_query_task(): Got conversations: %s", conversation_rows
            )

            file_rows = cursor.execute(
                "SELECT id, name, size, content_type, uploaded_at FROM task_files WHERE task_id = ? ORDER BY uploaded_at ASC",
                (id_,),
            ).fetchall()
            log.debug("_query_task(): Got files: %s", file_rows)

            return (
                ReadTaskResponse(
                    id=row[0],
                    status=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    conversations=[
                        TaskConversation(
                            id=r[0],
                            question=r[1],
                            answer=r[2],
                            generated_at=r[3],
                        )
                        for r in conversation_rows
                    ],
                    files=[
                        TaskFile(
                            id=f[0],
                            name=f[1],
                            size=f[2],
                            content_type=f[3],
                            uploaded_at=f[4],
                        )
                        for f in file_rows
                    ],
                )
                if row
                else None
            )
        else:
            return (
                TaskActionResponse(
                    id=row[0],
                    status=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                )
                if row
                else None
            )


def _add_task() -> int:
    log.debug("_add_task(): Adding task")
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO tasks (status, created_at, updated_at) VALUES (?, ?, ?)",
            (
                TaskStatus.created,
                datetime.now(),
                datetime.now(),
            ),
        )
        id_ = cursor.lastrowid
        log.debug("_add_task(): Added task with id=%d", id_)
        connection.commit()
        return id_


def _add_task_conversation(task_id: int, data: TaskUserInput) -> None:
    log.debug(
        "_add_task_conversation(): Adding conversation for task with id=%d",
        task_id,
    )
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO task_conversations (task_id, question, generated_at) VALUES (?, ?, ?)",
            (
                task_id,
                data.question,
                datetime.now(),
            ),
        )
        log.debug(
            "_add_task_conversation(): Added conversation for task with id=%d",
            task_id,
        )
        connection.commit()


def _update_task_answer(id_: int, answer: str) -> None:
    log.debug(
        "_update_task_answer(): Updating task's latest answer with id=%d", id_
    )
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "UPDATE task_conversations SET answer = ? WHERE id = (SELECT MAX(id) FROM task_conversations WHERE task_id = ?) AND answer IS NULL",
            (answer, id_),
        )
        log.debug(
            "_update_task_answer(): Updated task's latest answer with id=%d",
            id_,
        )
        connection.commit()


def _get_task_status(id_: int) -> TaskStatus | None:
    log.debug("_get_task_status(): Getting status for task with id=%d", id_)
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        row = cursor.execute(
            "SELECT status FROM tasks WHERE id = ?",
            (id_,),
        ).fetchone()
        log.debug("_get_task_status(): Got row: %s", row)
        return TaskStatus(row[0]) if row else None


def _update_task_status(id_: int, status: TaskStatus) -> None:
    log.debug("_update_task_status(): Updating task with id=%d", id_)
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now(), id_),
        )
        log.debug("_update_task_status(): Updated task with id=%d", id_)
        connection.commit()


def _add_task_files(id_: int, data: TaskUserInput) -> None:
    if len(data.files) > 0:
        with closing(
            sqlite3.connect(
                get_sqlite_file_path(),
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
        ) as connection, closing(connection.cursor()) as cursor:
            for file in data.files:
                name = file.filename
                log.debug("_save_task_files(): Saving file %s", name)
                cursor.execute(
                    "INSERT INTO task_files (task_id, name, size, content_type) VALUES (?, ?, ?, ?)",
                    (id_, name, file.size, file.content_type),
                )
                file_id = cursor.lastrowid
                log.debug("_save_task_files(): Added file with id=%d", file_id)

                with closing(
                    open(get_upload_file_path(id_, f"{file_id}-{name}"), "wb")
                ) as out_, closing(file.file) as in_:
                    out_.write(in_.read())
                log.debug("_save_task_files(): Saved file %s", name)

            connection.commit()

        reindex(id_)
        log.debug("_save_task_files(): Reindexed task with id=%d", id_)


def get_task(id_: int) -> ReadTaskResponse | None:
    return _query_task(id_, extras=True)


def create_task(data: CreateTaskRequest) -> TaskActionResponse:
    id_ = _add_task()
    _add_task_conversation(id_, data)
    _add_task_files(id_, data)
    return _query_task(id_)


def update_task(id_: int, data: UpdateTaskRequest) -> TaskActionResponse:
    if _get_task_status(id_) is TaskStatus.completed:
        _add_task_conversation(id_, data)
        _add_task_files(id_, data)
        return _query_task(id_)
    else:
        raise ValueError("Task is not completed")


async def run_task(id_: int) -> None:
    """Run a task."""
    task = _query_task(id_, extras=True)
    if task.status is not TaskStatus.started:
        try:
            _update_task_status(id_, TaskStatus.started)
            log.debug("Running task %d", id_)

            answer = (
                run_chat(task.conversations, id_)
                if len(task.files) == 0
                else run_ask(task.conversations, id_)
            )
            _update_task_answer(id_, answer.response)

            log.debug("Completed task %d", id_)
        except Exception as e:
            log.exception("Error running task %d: %s", id_, e)
        finally:
            _update_task_status(id_, TaskStatus.completed)
    else:
        log.warning("Task %d already started", id_)

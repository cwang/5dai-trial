"""Functions for utilising the SQLite database."""
import logging as log
import sqlite3
from contextlib import closing

from .paths import get_sqlite_file_path

SQL_CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

SQL_CREATE_TASK_CONVERSATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS task_conversations (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id)
)
"""

SQL_CREATE_TASK_FILES_TABLE = """
CREATE TABLE IF NOT EXISTS task_files (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    size INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id)
)
"""


def init_database() -> None:
    """Initialize the database."""
    with closing(
        sqlite3.connect(
            get_sqlite_file_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
    ) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(SQL_CREATE_TASKS_TABLE)
        cursor.execute(SQL_CREATE_TASK_CONVERSATIONS_TABLE)
        cursor.execute(SQL_CREATE_TASK_FILES_TABLE)
        log.info("Database initialized")

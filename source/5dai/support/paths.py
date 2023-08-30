"""Paths to files and directories used by the 5dai package."""

import logging as log
import os
from enum import Enum


class DataType(str, Enum):
    """Data type enumeration."""

    sqlite = "sqlite"
    upload = "upload"
    index = "index"


def _get_path(
    type_: DataType, dirname: str = None, filename: str = None
) -> str:
    """Get the path to a file or directory."""
    dir_ = os.path.join(os.getenv("APP_DATA_DIR"), type_.value)
    if dirname is not None:
        dir_ = os.path.join(dir_, dirname)
    os.makedirs(dir_, exist_ok=True)
    log.info("_get_path(): %s", dir_)
    return os.path.join(dir_, filename) if filename else dir_


def get_sqlite_file_path() -> str:
    """Get the path to the SQLite database file."""
    return _get_path(DataType.sqlite, filename="system.sqlite")


def get_upload_dir_path(_id: int) -> str:
    """Get the path to the file upload directory."""
    return _get_path(DataType.upload, str(_id))


def get_upload_file_path(_id: int, filename: str) -> str:
    """Get the path to the file upload directory."""
    return _get_path(DataType.upload, str(_id), filename)


def get_index_dir_path(_id: int) -> str:
    """Get the path to the file index directory."""
    return _get_path(DataType.index, str(_id))

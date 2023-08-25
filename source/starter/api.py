"""Module Docstring."""

import logging

import fastapi

from .starter import hello

log = logging.getLogger("starter")

router = fastapi.APIRouter()


@router.get("/say/{name}")
async def say(name: str) -> str:
    """Function Docstring."""
    log.info("Calling: hello() with [%s]", name)
    return hello(name)

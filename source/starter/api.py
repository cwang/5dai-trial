"""Module Docstring."""

import logging

from fastapi import FastAPI

from .starter import hello

log = logging.getLogger("starter")

app = FastAPI()


@app.get("/say/{name}")
async def say(name: str) -> str:
    """Function Docstring."""
    log.info("Calling: hello() with [%s]", name)
    return hello(name)

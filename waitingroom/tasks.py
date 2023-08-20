from __future__ import annotations

import asyncio
import logging
import time
from typing import (
    NoReturn,
)

from .base import (
    app,
    get_redis_typed,
)

LOG = logging.getLogger(__name__)


@app.before_serving
async def startup() -> None:
    app.add_background_task(task_instanceonline_flush)


@app.after_serving
async def shutdown() -> None:
    while app.background_tasks:
        task = app.background_tasks.pop()
        LOG.warning("Cancelling task %r", (task,))
        task.cancel()


async def task_instanceonline_flush() -> NoReturn:
    while True:
        flush_period = app.config["INSTANCEONLINE_FLUSH_PERIOD_SECONDS"]
        try:
            await task_instanceonline_flush_body()
        except asyncio.CancelledError:
            LOG.warning("instanceOnline task shutting down")
            raise
        except Exception:
            LOG.exception("Exception when running task_instanceonline_flush_body")
        await asyncio.sleep(flush_period)


async def task_instanceonline_flush_body() -> None:
    lifetime = app.config["INSTANCEONLINE_LIFETIME_SECONDS"]

    now_secs = time.time()
    db = get_redis_typed()
    deleted_count = await db.zremrangebyscore(
        "stats/instanceOnline", min="-inf", max=now_secs - lifetime
    )
    user_count = await db.zcard("stats/instanceOnline")
    LOG.warning(
        "instanceOnline: current user count: %(user_count)d (deleted: %(deleted_count)d)",
        {
            "user_count": user_count,
            "deleted_count": deleted_count,
        },
    )

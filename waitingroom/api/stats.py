# Copyright 2023, GreaseMonkey and the waitingroom contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from dataclasses import dataclass
import datetime
import time
from typing import Optional

from quart import (
    ResponseReturnValue,
    abort,
    make_response,
    request,
)

from ..base import (
    app,
    compute_reverse_timestamp,
    format_utc_datetime,
    get_redis_typed,
    is_valid_machine_id,
    make_typed_json_response,
)
from ..models import (
    OnlineUserStats,
)

#
# GET[U/A] /api/stats/onlineUserStats
#
# Displayed online user count on dash menu is f"{registeredUserCount-headlessUserCount}(~{instanceCount})"
#


@app.route("/api/stats/onlineUserStats", methods=["GET"])
async def api_stats_onlineUserStats() -> ResponseReturnValue:
    lifetime: float = app.config["INSTANCEONLINE_LIFETIME_SECONDS"]
    db = get_redis_typed()
    now_secs = time.time()
    instance_count = await db.zcount(
        "stats/instanceOnline", min=now_secs - lifetime, max="+inf"
    )
    user_count = 0

    now = datetime.datetime.utcnow()
    resp = await make_typed_json_response(
        OnlineUserStats(
            captureTimestamp=now,
            registeredUserCount=user_count,
            instanceCount=instance_count,
            vrUserCount=0,
            screenUserCount=0,
            headlessUserCount=0,
            mobileUserCount=0,
            publicSessionCount=0,
            activePublicSessionCount=0,
            publicWorldUserCount=0,
            PartitionKey=str(compute_reverse_timestamp(now)),
            RowKey="",
            Timestamp="0001-01-01T00:00:00+00:00",
            ETag=None,
        ),
        # QUIRK: The API server reports this as text/plain. Probably uses a different codepath from the other JSON stuff.
        mimetype="text/plain; charset=utf-8",
    )
    return resp


#
# POST[U/A] /api/stats/instanceOnline/<machineId>
#


@app.route("/api/stats/instanceOnline/<machine_id>", methods=["POST"])
async def api_stats_instanceOnline(machine_id: str) -> ResponseReturnValue:
    if not is_valid_machine_id(machine_id):
        abort(400)
    else:
        db = get_redis_typed()
        now_secs = time.time()
        await db.zadd(
            "stats/instanceOnline",
            {machine_id: now_secs},
        )
        return await make_response("", 200)

from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Optional

from quart import (
    ResponseReturnValue,
    make_response,
    request,
)

from ..base import (
    app,
    compute_reverse_timestamp,
    format_utc_datetime,
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
    # FIXME generate this properly --GM
    now = datetime.datetime.utcnow()
    resp = await make_typed_json_response(
        OnlineUserStats(
            captureTimestamp=now,
            registeredUserCount=1,
            instanceCount=2,
            vrUserCount=4,
            screenUserCount=8,
            headlessUserCount=0,
            mobileUserCount=32,
            publicSessionCount=64,
            activePublicSessionCount=128,
            publicWorldUserCount=256,
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


@app.route("/api/stats/instanceOnline/<machineId>", methods=["POST"])
async def api_stats_instanceOnline(machineId: str) -> ResponseReturnValue:
    # FIXME use this properly --GM
    return await make_response("", 200)

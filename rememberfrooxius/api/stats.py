from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Optional

from flask import (
    Response,
    make_response,
    request,
)

from ..base import (
    app,
    compute_reverse_timestamp,
    format_utc_datetime,
    make_json_response,
)

#
# GET[U/A] /api/stats/onlineUserStats
#
# Displayed online user count on dash menu is f"{registeredUserCount-headlessUserCount}(~{instanceCount})"
#


@app.route("/api/stats/onlineUserStats", methods=["GET"])
def api_stats_onlineUserStats() -> Response:
    # FIXME generate this properly --GM
    now = datetime.datetime.utcnow()
    return make_json_response(
        {
            "captureTimestamp": format_utc_datetime(now),
            "registeredUserCount": 1,
            "instanceCount": 2,
            "vrUserCount": 4,
            "screenUserCount": 8,
            "headlessUserCount": 0,
            "mobileUserCount": 32,
            "publicSessionCount": 64,
            "activePublicSessionCount": 128,
            "publicWorldUserCount": 256,
            "PartitionKey": compute_reverse_timestamp(now),
            "RowKey": "",
            "Timestamp": "0001-01-01T00:00:00+00:00",
            "ETag": None,
        }
    )


@dataclass(slots=True)
class OnlineUserStats:
    # This is the order I received this in a dump once.
    captureTimestamp: datetime.datetime
    registeredUserCount: int
    instanceCount: int
    vrUserCount: int
    screenUserCount: int
    headlessUserCount: int
    mobileUserCount: int
    publicSessionCount: int
    activePublicSessionCount: int
    publicWorldUserCount: int

    PartitionKey: str  # This is indeed a camelO - also (almost) exactly the same timestamp as captureTimestamp as a reverse timestamp
    RowKey: str  # This is indeed a camelO - seems to be empty?
    Timestamp: str = "0001-01-01T00:00:00+00:00"  # This is indeed a camelO, also that's the actual timestamp string
    ETag: Optional[str] = None  # This is indeed a camelO

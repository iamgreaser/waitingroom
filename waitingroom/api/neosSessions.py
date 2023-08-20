from __future__ import annotations

from dataclasses import dataclass
import datetime
import json
import logging
import urllib
from uuid import (
    UUID,
    uuid4,
)
from typing import (
    Any,
    Callable,
    Optional,
)

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
    unpack_typed_json,
)
from ..models import (
    NeosSessions,
)

#
# POST[U]|PATCH[A] /api/neosSessions
#


@app.route("/api/neosSessions", methods=["POST", "PATCH"])
async def api_neosSessions() -> ResponseReturnValue:
    inbody = await request.get_json()
    if not isinstance(inbody, dict):
        return await make_response("Bad request", 400)

    try:
        blob: NeosSessions = unpack_typed_json(NeosSessions, inbody)
    except TypeError:
        return await make_response("Bad request", 400)
    else:
        if request.method == "POST":
            # TODO: Process this stuff instead of returning it directly --GM
            blob.clientIp = request.remote_addr

            now = datetime.datetime.utcnow()
            nowstr = format_utc_datetime(now)
            blob.timestamp = now
            blob.eTag = f"W/\"datetime'{urllib.parse.quote(nowstr)}'\""

            # Copy this across
            if blob.sessionEnd is None:
                blob.sessionEnd = blob.sessionStart

            # TODO: Actually use this value --GM
            if blob.sessionId is None:
                sessionId = uuid4()
                blob.sessionId = sessionId
                blob.rowKey = sessionId

            blob.reverseTimestamp = str(compute_reverse_timestamp(now))
            blob.partitionKey = blob.reverseTimestamp

            # TODO: userId (eventually) --GM

            return await make_typed_json_response(blob)
        elif request.method == "PATCH":
            # TODO: Handle this properly --GM
            return await make_response("", 204)
            # return await make_response(f"TODO PATCH {blob!r}", 500)
        else:
            raise Exception("invalid method - should have been caught higher up!")

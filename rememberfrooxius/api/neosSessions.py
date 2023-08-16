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

from ..base import (
    app,
    compute_reverse_timestamp,
    format_utc_datetime,
    make_typed_json_response,
    unpack_typed_json,
)

from flask import (
    Response,
    make_response,
    request,
)

#
# POST[U]|PATCH[A] /api/neosSessions
#


#
# When first joining, a POST is sent early and a reply is made, then later on a PATCH is sent.
# These have been checked against a desktop user running the Linux version.
#
# missing in requests: clientIp, eTag, partitionKey, rowKey, timestamp
# missing in responses: countryCode, headDeviceModel, peripherals, userId
# null in all requests: countryCode, headDeviceModel, peripherals
# null in POST requests: reverseTimestamp, sessionId, userId
#
@dataclass(slots=True)
class NeosSessions:
    clientIp: Optional[str] = None  # RESPONSE ONLY
    countryCode: Optional[
        str
    ] = None  # REQUEST ONLY - TODO: Work out what the actual type is --GM
    cpu: Optional[str] = None
    createdWorlds: Optional[int] = None
    eTag: Optional[str] = None  # RESPONSE ONLY - "W/\"datetime'{urlescape(utcnow)}'\""
    gpu: Optional[str] = None
    headDevice: Optional[str] = None
    headDeviceModel: Optional[
        str
    ] = None  # REQUEST ONLY - TODO: Work out what the actual type is --GM
    machineId: Optional[str] = None
    memoryBytes: Optional[int] = None
    neosVersion: Optional[str] = None
    operatingSystem: Optional[str] = None
    partitionKey: Optional[str] = None  # RESPONSE ONLY - Equal to reverseTimestamp.
    peripherals: Optional[
        str
    ] = None  # REQUEST ONLY - TODO: Work out what the actual type is --GM
    reverseTimestamp: Optional[
        str
    ] = None  # This is a long decimal number, in units of 10^-7 seconds until 10000 AD.
    rowKey: Optional[UUID] = None  # RESPONSE ONLY - Equal to sessionId.
    sessionEnd: Optional[datetime.datetime] = None
    sessionId: Optional[UUID] = None
    sessionStart: Optional[datetime.datetime] = None
    systemLocale: Optional[str] = None
    userId: Optional[str] = None  # REQUEST ONLY?
    timestamp: Optional[
        datetime.datetime
    ] = None  # RESPONSE ONLY - same time used for eTag EXCEPT it uses "+00:00" instead of "Z" at the end.
    visitedWorlds: Optional[int] = None

    @classmethod
    def pack_field(cls, default: Callable[[Any], Any], name: str, value: Any) -> Any:
        if name == "timestamp":
            return format_utc_datetime(
                value, suffix="+00:00"
            )  # I did not create this API.
        else:
            return default(value)

    @classmethod
    def unpack_field(cls, default: Callable[[Any], Any], name: str, value: Any) -> Any:
        # TODO: Work out how to support this properly --GM
        return default(value)


@app.route("/api/neosSessions", methods=["POST", "PATCH"])
def api_neosSessions() -> Response:
    inbody = request.get_json()
    if not isinstance(inbody, dict):
        return make_response("Bad request", 400)

    try:
        blob: NeosSessions = unpack_typed_json(NeosSessions, inbody)
    except TypeError:
        return make_response("Bad request", 400)
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

            return make_typed_json_response(blob)
        elif request.method == "PATCH":
            # TODO: Handle this properly --GM
            return make_response("", 204)
            # return make_response(f"TODO PATCH {blob!r}", 500)
        else:
            raise Exception("invalid method - should have been caught higher up!")

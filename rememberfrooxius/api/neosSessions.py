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
    Dict,
    Optional,
    cast,
    get_type_hints,
)

from ..base import (
    app,
    compute_reverse_timestamp,
    format_utc_datetime,
    make_json_response,
)

from flask import (
    Response,
    make_response,
    request,
)

#
# POST[U]|PATCH[A] /api/neosSessions
#


# NOTE: Python's datetime module cannot handle the year 10000 AD, so we can use this metric instead:
# - Days from the start of 2000 AD until the start of 10000 AD: 2921940 (results in issues!)
# - Days from the start of 9999 AD until the start of 10000 AD: 365


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


@app.route("/api/neosSessions", methods=["POST", "PATCH"])
def api_neosSessions() -> Response:
    # TODO: Hoist the parsing out into base --GM
    inbody = request.get_json()
    if not isinstance(inbody, dict):
        return make_response("Bad request", 400)
    if False:
        # FIXME: We need to actually parse this information --GM
        hints = get_type_hints(NeosSessions)
        for k, v in inbody.items():
            logging.warn(f"type: {hints[k]}")

    try:
        blob = NeosSessions(**inbody)
    except TypeError:
        return make_response("Bad request", 400)
    else:
        if request.method == "POST":
            # TODO: Process this stuff instead of returning it directly --GM
            # FIXME this all needs to actually serialise instead of us just making a string --GM
            blob.clientIp = request.remote_addr

            now = datetime.datetime.utcnow()
            nowstr = format_utc_datetime(now)
            blob.timestamp = cast(
                datetime.datetime,
                format_utc_datetime(now, suffix="+00:00"),
            )  # I did not create this API.
            blob.eTag = f"W/\"datetime'{urllib.parse.quote(nowstr)}'\""

            # Copy this across
            if blob.sessionEnd is None:
                blob.sessionEnd = blob.sessionStart

            # FIXME: We need proper serialisation and then we need to get rid of these casts --GM
            # TODO: Actually use this value --GM
            if blob.sessionId is None:
                sessionId = uuid4()
                blob.sessionId = cast(UUID, str(sessionId))
                blob.rowKey = cast(UUID, str(sessionId))

            blob.reverseTimestamp = str(compute_reverse_timestamp(now))
            blob.partitionKey = blob.reverseTimestamp

            # TODO: userId (eventually) --GM
            # TODO: Hoist this out into base --GM
            body: Dict[str, Any] = {
                k: getattr(blob, k)
                for k in blob.__slots__
                if getattr(blob, k) is not None
            }
            return make_json_response(body)
        elif request.method == "PATCH":
            return make_response(f"TODO PATCH {blob!r}", 500)
        else:
            raise Exception("invalid method - should have been caught higher up!")

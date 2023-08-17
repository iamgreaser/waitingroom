from __future__ import annotations

import base64
from dataclasses import dataclass
import datetime
import logging
import os
from typing import (
    Any,
    Callable,
    Optional,
)
import urllib

from flask import (
    Response,
    make_response,
    request,
)

from ..base import (
    app,
    format_utc_datetime,
    make_typed_json_response,
    unpack_typed_json,
)

from ..models import (
    UserSessionRequest,
    UserSessionResponse,
)

#
# POST[U] /api/userSessions
#


@app.route("/api/userSessions", methods=["POST"])
def api_userSessions() -> Response:
    inbody = request.get_json()
    if not isinstance(inbody, dict):
        return make_response("Bad request", 400)

    try:
        blob: UserSessionRequest = unpack_typed_json(UserSessionRequest, inbody)
    except TypeError:
        logging.exception("Failed to parse userSessions input")
        return make_response("Bad request", 400)
    else:
        # FIXME actually authenticate, right now we're keeping the token around to be polite --GM
        now = datetime.datetime.utcnow()
        assert request.remote_addr is not None
        nowstr = format_utc_datetime(now)

        ownerId: str
        if blob.ownerId is not None:
            ownerId = blob.ownerId
        else:
            assert blob.username is not None
            ownerId = "U-" + blob.username

        token: str
        if blob.sessionCode is not None:
            # TODO: Validate this! (also process this somehow) --GM
            token = blob.sessionCode
        else:
            token = "V2-" + base64.b64encode(os.urandom(128), altchars=b"+_").decode(
                "utf-8"
            )
        assert blob.sessionCode is not None

        return make_typed_json_response(
            UserSessionResponse(
                created=now,
                eTag=f"W/\"datetime'{urllib.parse.quote(nowstr)}'\"",
                expire=now + datetime.timedelta(days=7),
                partitionKey=ownerId,
                rememberMe=blob.rememberMe,
                rowKey=token,
                secretMachineId=blob.secretMachineId,
                sourceIP=request.remote_addr,
                timestamp=now,
                token=token,
                userId=ownerId,
            )
        )

# Copyright 2023, GreaseMonkey and the waitingroom contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import (
    List,
)

from quart import (
    ResponseReturnValue,
    make_response,
    request,
)

from waitingroom.base import (
    app,
    format_utc_datetime,
    make_typed_json_response,
)
from waitingroom.models import (
    Session,
)

#
# POST[U/A]|PUT[U/A], GET[U/A] /api/sessions
#
# NOTE: outputDevice: 1 = "Headless", 2 = "Screen", 3 = "VR" - FIXME make an enum for this --GM
#


@app.route("/api/sessions", methods=["POST", "PUT", "GET"])
async def api_sessions() -> ResponseReturnValue:
    if request.method == "POST" or request.method == "PUT":
        # TODO! --GM
        return await make_response("", 200)
    elif request.method == "GET":
        # TODO! --GM
        now = datetime.datetime.utcnow()
        return await make_typed_json_response(
            [],
            obj_type=List[Session],
        )
    else:
        raise Exception("invalid method - should have been caught higher up!")

from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import (
    List,
)

from flask import (
    Response,
    make_response,
    request,
)

from ..base import (
    app,
    format_utc_datetime,
    make_typed_json_response,
)
from ..models import (
    Session,
)

#
# POST[U/A]|PUT[U/A], GET[U/A] /api/sessions
#
# NOTE: outputDevice: 1 = "Headless", 2 = "Screen", 3 = "VR" - FIXME make an enum for this --GM
#


@app.route("/api/sessions", methods=["POST", "PUT", "GET"])
def api_sessions() -> Response:
    if request.method == "POST" or request.method == "PUT":
        # TODO! --GM
        return make_response("", 200)
    elif request.method == "GET":
        # TODO! --GM
        now = datetime.datetime.utcnow()
        return make_typed_json_response(
            [],
            obj_type=List[Session],
        )
    else:
        raise Exception("invalid method - should have been caught higher up!")

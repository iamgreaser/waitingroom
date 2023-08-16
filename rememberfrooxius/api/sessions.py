from __future__ import annotations

from flask import (
    Response,
    make_response,
    request,
)

from ..base import (
    app,
    make_json_response,
)

#
# POST[U/A]|PUT[U/A], GET[U/A] /api/sessions
#


@app.route("/api/sessions", methods=["POST", "PUT", "GET"])
def api_sessions() -> Response:
    if request.method == "POST" or request.method == "PUT":
        # TODO! --GM
        return make_response("", 200)
    elif request.method == "GET":
        # TODO! --GM
        return make_json_response([])
    else:
        raise Exception("invalid method - should have been caught higher up!")

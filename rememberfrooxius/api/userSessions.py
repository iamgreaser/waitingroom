from __future__ import annotations

from flask import (
    Response,
    make_response,
    request,
)

from ..base import app

#
# POST[U] /api/userSessions
#


@app.route("/api/userSessions", methods=["POST"])
def api_userSessions() -> Response:
    if request.method == "POST":
        # TODO! --GM
        return make_response("TODO! but pretending you're rate-limited", 429)
    else:
        raise Exception("invalid method - should have been caught higher up!")

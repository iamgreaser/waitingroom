from __future__ import annotations

import logging
import subprocess

import flask
from flask import (
    Response,
    make_response,
)

from .base import (
    app,
    format_utc_datetime,
    make_json_response,
)
from . import (
    api,
    install_ServerResponse,
)


#
# TESTING: /
#


@app.route("/")
def root() -> Response:
    resp = flask.make_response(
        "<h1>It Works!</h1>",
    )
    resp.mimetype = "text/html"
    return resp


#
# AUTOSTART: Check the thing to see if it passes type checks and is also working
#

logging.warn("Running mypy to confirm that this isn't blatantly wrong")
subprocess.run(["mypy", "--strict", "-m", __name__], check=True)
logging.warn("Type-checked successfully!")

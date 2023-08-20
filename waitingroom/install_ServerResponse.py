from __future__ import annotations

import datetime

from quart import ResponseReturnValue

from .base import (
    app,
    format_utc_datetime,
    make_json_response,
)

#
# /install/ServerResponse
#


@app.route("/install/ServerResponse")
async def install_ServerResponse() -> ResponseReturnValue:
    return await make_json_response(
        {
            "lastUpdate": format_utc_datetime(datetime.datetime.utcnow()),
            "responseTimeMilliseconds": 7,  # Not sure how to calculate this but I know a certain someone would appreciate this number
        }
    )

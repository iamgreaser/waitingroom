from __future__ import annotations

import json
from typing import Dict

from ..base import app

from quart import (
    ResponseReturnValue,
    make_response,
)

#
# /api/globalvars/<varname>
#

# Things that will never change.
# Precompile them to minimise the time wasted on them.
static_globalvars_unbaked = {
    "CDFT_CONVERSION": {
        "eTag": "W/\"datetime'2021-11-29T10%3A47%3A34.2147849Z'\"",
        "ownerId": "GLOBAL",
        "partitionKey": "GLOBAL",
        "path": "CDFT_CONVERSION",
        "rowKey": "CDFT_CONVERSION",
        "timestamp": "2021-11-29T10:47:34.2147849+00:00",
        "value": "19.66930202",
    },
    "NCR_CONVERSION": {
        "eTag": "W/\"datetime'2023-07-29T06%3A50%3A51.8575104Z'\"",
        "ownerId": "GLOBAL",
        "partitionKey": "GLOBAL",
        "path": "NCR_CONVERSION",
        "rowKey": "NCR_CONVERSION",
        "timestamp": "2023-07-29T06:50:51.8575104+00:00",
        "value": "0.073194",
    },
}
static_globalvars: Dict[str, bytes] = {
    k: json.dumps(v).encode("utf-8") for k, v in static_globalvars_unbaked.items()
}


@app.route("/api/globalvars/<varname>")
async def api_globalvars(varname: str) -> ResponseReturnValue:
    assert isinstance(varname, str)
    try:
        content = static_globalvars[varname]
    except LookupError:
        return await make_response("Not Found", 404)
    else:
        resp = await make_response(content)
        resp.mimetype = "application/json; charset=utf-8"
        return resp

# This is the entry point for all the SignalR stuff.
from __future__ import annotations

import base64
from dataclasses import dataclass
import datetime
import json
import os
from typing import (
    Any,
    Dict,
    List,
)
import urllib

from flask import (
    Response,
    request,
)

from .base import (
    app,
    make_json_response,
    make_typed_json_response,
    websocket_base,
)

#
# POST /hub/negotiate?negotiateVersion={version, should be 1}
#


@dataclass(slots=True)
class HubNegotiateResponse:
    accessToken: str  # JWT auth, HS-256
    availableTransports: List[Dict[str, Any]]  # In practice, this list is empty.
    negotiateVersion: int  # In practice, this is 0.
    url: str


@app.route("/hub/negotiate", methods=["POST"])
def hub_negotiate() -> Response:
    # FIXME the URL formation is not safe here! --GM
    negotiateVersion = 1  # TODO: Get it from the URL --GM
    return make_typed_json_response(
        HubNegotiateResponse(
            accessToken="TODOINSERTJWTHERE",
            availableTransports=[],
            negotiateVersion=0,
            url=urllib.parse.urlunparse(
                (
                    "https",
                    # request.host, # Actually not adequate, needs to be cloudx.service.signalr.net ?
                    "cloudx.service.signalr.net",
                    "/client/",
                    "",
                    f"hub=apphub&asrs.op=%2Fhub&negotiateVersion={negotiateVersion}&asrs_request_id=INSERTREQUESTIDHERE",
                    "",
                )
            ),
        )
    )


#
# POST /client/negotiate?whatever
#
# This takes an Authorization: Bearer token, with the given JWT from /hub/negotiate, field "accessToken".
#


@app.route("/client/negotiate", methods=["POST"])
def client_negotiate() -> Response:
    # Pilfered from mitmproxy.
    # Generate a maybe-nearly-websafe (_ is used, but is - used or is this still + like the 2048-bit tokens?) unpadded-base64 31-char connectionId --GM
    connectionId = (
        base64.b64encode(os.urandom(23), altchars=b"-_").decode("utf-8").rstrip("=")
    )
    return make_json_response(
        {
            "availableTransports": [
                {"transferFormats": ["Text", "Binary"], "transport": "WebSockets"},
                {"transferFormats": ["Text"], "transport": "ServerSentEvents"},
                {"transferFormats": ["Text", "Binary"], "transport": "LongPolling"},
            ],
            "connectionId": connectionId,
            "negotiateVersion": 0,
        }
    )


#
# WSS GET /client/?whatever
#
# This takes an Authorization: Bearer token, with the given JWT from /hub/negotiate, field "accessToken".
#
@websocket_base.route("/client/")  # type: ignore
def client_websocket(ws: Any) -> None:
    # WARNING: This is a lazy approach --GM
    data = ws.receive()
    ws.send(json.dumps({}).encode("utf-8") + b"\x1e")
    while True:
        data = ws.receive()
        ws.send(json.dumps({"type": 6}).encode("utf-8") + b"\x1e")


# Normal URL: https://cloudx.service.signalr.net/client/?hub=apphub&asrs.op=%2Fhub&negotiateVersion=1&asrs_request_id={someRequestId}
# This gets changed into: https://cloudx.service.signalr.net/client/negotiate?hub=apphub&asrs.op=%2Fhub&negotiateVersion=1&asrs_request_id={someRequestId}
# And then we connect a websocket to: https://cloudx.service.signalr.net/client/?hub=apphub&asrs.op=%2Fhub&negotiateVersion=1&asrs_request_id={someRequestId}&id={connectionIdInNegotiateURLResponse}

# JWT Header:
# {
#    "alg": "HS256",
#    "kid": "-1895682698",
#    "typ": "JWT",
# }

# JWT Body:
# {
#    "asrs.s.uid": "U-GreaseMonkey",
#    "asrs.s.aut": "neos",
#    "asrs.s.derror": "True",
#    "UserID": "U-GreaseMonkey",
#    "SessionToken": "V2-{auth}",  # No, I'm not leaking that.
#    "nbf": 1690858681,
#    "exp": 1690862281,
#    "iat": 1690858681,
#    "aud": "https://cloudx.service.signalr.net/client/?hub=apphub",
# }
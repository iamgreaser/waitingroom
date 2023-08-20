# Copyright 2023, GreaseMonkey and the waitingroom contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
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

from quart import (
    ResponseReturnValue,
    request,
    websocket,
)

from .base import (
    app,
    make_json_response,
    make_typed_json_response,
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
async def hub_negotiate() -> ResponseReturnValue:
    # FIXME the URL formation is not safe here! --GM
    negotiateVersion = 1  # TODO: Get it from the URL --GM
    return await make_typed_json_response(
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
async def client_negotiate() -> ResponseReturnValue:
    # Pilfered from mitmproxy.
    # Generate a maybe-nearly-websafe (_ is used, but is - used or is this still + like the 2048-bit tokens?) unpadded-base64 31-char connectionId --GM
    connectionId = (
        base64.b64encode(os.urandom(23), altchars=b"-_").decode("utf-8").rstrip("=")
    )
    return await make_json_response(
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
@app.websocket("/client/")
async def client_websocket() -> None:
    # WARNING: This is a lazy approach --GM
    data = await websocket.receive()
    await websocket.send(json.dumps({}).encode("utf-8") + b"\x1e")
    while True:
        data = await websocket.receive()
        await websocket.send(json.dumps({"type": 6}).encode("utf-8") + b"\x1e")


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

#
# Spec for SignalR hub protocol: https://github.com/dotnet/aspnetcore/blob/main/src/SignalR/docs/specs/HubProtocol.md
# Messages observed:
#
# Type 6: Ping - purely used as a keepalive
#
# {"type":6}\x1e
#
# Type 1: Invocation
#
# {"type":1,"target":"SendMessage","arguments":[{"id":"MSG-aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa","ownerId":"U-From","recipientId":"U-To","senderId":"U-From","messageType":"Text","content":"Hey, can you send a message back to me? I just need to test something.","sendTime":"2023-08-16T21:05:51.570726Z","lastUpdateTime":"0001-01-01T00:00:00","readTime":null}]}\x1e
# {"type":1,"target":"MessageSent","arguments":[{"id":"MSG-aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa","ownerId":"U-To","recipientId":"U-To","senderId":"U-From","messageType":"Text","content":"Hey, can you send a message back to me? I just need to test something.","sendTime":"2023-08-16T21:05:51.570726Z","lastUpdateTime":"2023-08-16T21:05:51.0999508Z","readTime":null}]}\x1e
# {"type":1,"target":"MessagesRead","arguments":[{"recipientId":"U-To","readTime":"2023-08-16T21:05:53.0255815Z","ids":["MSG-aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"]}]}\x1e
# {"type":1,"target":"ReceiveMessage","arguments":[{"id":"MSG-bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb","ownerId":"U-From","recipientId":"U-From","senderId":"U-To","messageType":"Text","content":"Hello :)","sendTime":"2023-08-16T21:06:08.2111369Z","lastUpdateTime":"2023-08-16T21:06:13.3875945Z","readTime":null}]}\x1e
# {"type":1,"target":"MarkMessagesRead","arguments":[{"senderId":"U-To","ids":["MSG-bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb"],"readTime":"2023-08-16T21:06:14.120171Z"}]}\x1e
#

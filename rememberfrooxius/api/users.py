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
    make_json_response,
    make_typed_json_response,
    unpack_typed_json,
)

#
# GET[A] /api/users/{myUserId}/friends
#


@app.route("/api/users/<userId>/friends", methods=["GET"])
def api_users_id_friends(userId: str) -> Response:
    # FIXME do this properly instead of using a stub --GM
    return make_json_response(
        [
            {
                "friendStatus": "Accepted",
                "friendUsername": name,
                "id": f"U-Nose{i:05d}",
                "isAccepted": True,
                "latestMessageTime": format_utc_datetime(
                    datetime.datetime(
                        year=2023, month=8, day=16, hour=0, minute=0, second=0
                    )
                    - datetime.timedelta(seconds=5 * i)
                ),
                "ownerId": userId,
                "profile": {
                    "iconUrl": "neosdb:///27095aed82033a1b36f4051f3bda0e654ff21c0f816f14bf3bb9d574f1f97a34.webp"
                },
                "userStatus": {
                    # "compatibilityHash": "jnnkdwkBqGv5+jlf1u/k7A==",  # Not used in bot accounts
                    "currentHosting": True,
                    "currentSessionAccessLevel": 0,
                    "currentSessionHidden": True,
                    "isMobile": True,
                    "lastStatusChange": "2018-01-01T00:00:00",
                    # "neosVersion": "2022.1.28.1335",  # Not used in bot accounts
                    "neosVersion": desc,  # Not used in bot accounts
                    "onlineStatus": "Online",  # Bot accounts seem to always be "Offline", but they show up as online
                    "outputDevice": "Unknown",
                },
            }
            for (i, (name, desc)) in enumerate(
                [
                    ("We're no strangers", "to love"),
                    ("You know the rules", "and so do I"),
                    ("A full commitment's", "what I'm thinking of"),
                    ("You wouldn't get", "this from any other guy"),
                    ("I just wanna tell", "you how I'm feeling"),
                    ("Gotta make you", ""),
                    ("Understand", "Understand"),
                    ("Understand", "Understand"),
                    ("Understand", "Understand"),
                    ("The concept", "The concept of"),
                    ("LOVE", "(insert bass here)"),
                ]
            )
        ]
    )


#
# GET[A] /api/users/{myUserId}/messages?maxItems={an_integer_or_minus1_is_unlimited}&unread={true_or_false}
#


@app.route("/api/users/<userId>/messages", methods=["GET"])
def api_users_id_messages(userId: str) -> Response:
    # FIXME do this properly instead of using a stub --GM
    # FIXME actually log this API being used so I have some clue what the objects inside it even look like --GM
    return make_json_response([])

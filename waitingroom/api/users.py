from __future__ import annotations

import base64
from dataclasses import dataclass
import datetime
import logging
import os
from typing import (
    Any,
    Callable,
    List,
    Optional,
    cast,
)
import urllib

from quart import (
    ResponseReturnValue,
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
from ..models import (
    Friend,
    FriendProfile,
    UserStatus,
    Message,
)

#
# GET[A] /api/users/{myUserId}/friends
#


@app.route("/api/users/<userId>/friends", methods=["GET"])
async def api_users_id_friends(userId: str) -> ResponseReturnValue:
    # GET args:
    # - optional lastStatusUpdate: datetime.datetime

    # FIXME do this properly instead of using a stub --GM
    return await make_typed_json_response(
        [
            Friend(
                friendStatus="Accepted",
                friendUsername="Essential Bot",
                id="U-Neos",
                isAccepted=True,
                latestMessageTime=datetime.datetime(year=1, month=1, day=1),
                ownerId=userId,
                profile=FriendProfile(
                    iconUrl="neosdb:///27095aed82033a1b36f4051f3bda0e654ff21c0f816f14bf3bb9d574f1f97a34.webp",  # Logo used by the Neos bot
                    # tokenOptOut=["NCR"],
                ),
                userStatus=UserStatus(
                    # compatibilityHash="jnnkdwkBqGv5+jlf1u/k7A==",  # Not used in bot accounts
                    currentHosting=False,
                    currentSessionAccessLevel=0,
                    currentSessionHidden=False,
                    isMobile=False,
                    lastStatusChange=datetime.datetime(year=2018, month=1, day=1),
                    # ^ For when your definition of "null" isn't enough, and your definition to replace *that* also isn't enough... here's the third definition of a "null" timestamp. Enjoy!
                    # neosVersion="2022.1.28.1335",  # Not used in bot accounts
                    onlineStatus="Offline",
                    outputDevice="Unknown",
                ),
            )
        ],
        obj_type=List[Friend],
    )


#
# GET[A] /api/users/{myUserId}/messages?maxItems={an_integer_or_minus1_is_unlimited}&unread={true_or_false}
#


INTRO_MESSAGE_LINES = [
    [
        "Howdy! Welcome to the completely unofficial Resonite waiting room.",
        "NeosVR would not have been possible without those who worked on it, officially and unofficially. So, here's some credits. Note that the list here is woefully incomplete.",
        "Official contributions:",
        "- Frooxius: Made the bulk of the engine.",
        "- Geenz: Did a bunch of graphics programming work.",
        "- ProbablePrime: Wrote a bunch of tutorials, documentation, and code.",
    ],
    [
        "- Shifty: Solved a lot of peoples' problems with NeosVR.",
        "- Raith: Worked on the moderation ticket system. Also often involved with the NeosVR Twitch streams.",
        "- Aegis_Wolf: Creative director for a lot of content.",
        "- Chroma: Involved with a lot of NeosVR's graphical and video design. Made the last official trailer for NeosVR.",
        "- Lacy Bean: Involved with a lot of NeosVR's sound design.",
        "- Nexulan: *Still* runs the NeosVR streams on Twitch.",
        "- Rue Shejn: Made a lot of 3D assets for official NeosVR worlds.",
    ],
    [
        "- Ryuvi: Made a lot of LogiX stuff, as well as the default head-and-hands avatar + ViewModel that you're probably using right now if you haven't gotten an avatar set up yet.",
        "- Theofilus the Folf: Chroma's right-hand folf.",
        "- Canadian Git: Runs the moderation team.",
        "- Dante: Also runs the moderation team.",
        "- Veer: Handles a bunch of the moderation-related meta stuff like policies and guidelines.",
    ],
    [
        "Anyway, we hope you enjoy this place as much as we did. Look forward to seeing you all on Resonite!",
    ],
]
INTRO_MESSAGE = ["\n".join(grp) for grp in INTRO_MESSAGE_LINES]


@app.route("/api/users/<userId>/messages", methods=["GET"])
async def api_users_id_messages(userId: str) -> ResponseReturnValue:
    # FIXME we really need to authenticate in order to actually get a coherent answer instead of pretending that the use is always U-GreaseMonkey --GM

    # GET args:
    # - maxItems: int (seen: "-1", "100")
    # - optional unread: bool (seen: "true" (w/ maxItems=-1))
    # - optional user: str ("U-{name}" format - seen w/ maxItems=100)

    messages: List[Message] = []
    q_maxItems: int = int(str(request.args["maxItems"]))
    # FIXME: "unread=false" does not have known semantics, we could check this or we could assume "true" is the only valid thing and anything else doesn't do this check --GM
    q_unread: bool = {"true": True, "false": False}[request.args.get("unread", "false")]
    qopt_user: Optional[str] = request.args.get("user", None)
    if qopt_user is not None and not q_unread:
        q_user = str(qopt_user)
        if q_user == "U-Neos":
            for i, line in enumerate(INTRO_MESSAGE):
                td = datetime.timedelta(seconds=1) * i
                messages.insert(
                    0,
                    Message(
                        content=line,
                        messageType="Text",
                        id="MSG-bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb",
                        sendTime=datetime.datetime(
                            year=2023,
                            month=8,
                            day=16,
                            hour=12,
                            minute=34,
                            second=48,
                            microsecond=344278,
                        )
                        + td,
                        readTime=datetime.datetime(
                            year=2023,
                            month=8,
                            day=16,
                            hour=12,
                            minute=34,
                            second=56,
                            microsecond=789012,
                        )
                        + td,
                        # Not necessarily equal to either of the above times.
                        lastUpdateTime=datetime.datetime(
                            year=2023,
                            month=8,
                            day=16,
                            hour=12,
                            minute=34,
                            second=56,
                            microsecond=789012,
                        )
                        + td,
                        otherId=q_user,
                        ownerId=userId,
                        recipientId=userId,
                        senderId=q_user,
                    ),
                )

    if q_maxItems >= 0:
        messages = messages[:q_maxItems]

    return await make_typed_json_response(messages, obj_type=List[Message])


@app.route("/api/users/<userId>/status", methods=["PUT"])
async def api_users_id_status(userId: str) -> ResponseReturnValue:
    inbody = await request.get_json()
    if not isinstance(inbody, dict):
        return await make_response("Bad request", 400)

    # API BUG: "CurrentSession" is used instead of "currentSession". Remap accordingly.
    if "CurrentSession" in inbody:
        if "currentSession" in inbody:
            return await make_response("Bad request", 400)
        inbody["currentSession"] = inbody["CurrentSession"]
        del inbody["CurrentSession"]

    try:
        blob: UserStatus = unpack_typed_json(UserStatus, inbody)
    except TypeError:
        return await make_response("Bad request", 400)
    else:
        # TODO! --GM
        logging.warning(f"Got user status: {blob!r}")
        return await make_response("", 200)

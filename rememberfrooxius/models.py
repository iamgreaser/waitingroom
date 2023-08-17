from __future__ import annotations

from dataclasses import dataclass
import datetime
import logging
from typing import (
    List,
    Optional,
    cast,
)
from uuid import UUID

from . import base

#
# Friend definitions
#


@dataclass(slots=True)
class Friend:
    friendStatus: str  # "Accepted", ...?
    friendUsername: str  # Visible name
    id: str  # "U-{name}" format
    isAccepted: bool
    latestMessageTime: datetime.datetime  #
    ownerId: str  # The provided userId when querying one's friends list.
    profile: Optional[FriendProfile]  # If the profile is empty, we don't send it.
    userStatus: UserStatus


@dataclass(slots=True)
class FriendProfile:
    iconUrl: str  # Typically a neosdb URL
    tokenOptOut: Optional[
        List[str]
    ] = None  # By the way, this is visible to other users! SHOW YOUR SUPPORT


@dataclass(slots=True)
class UserStatus:
    # compatibilityHash: Optional[str] = None  # base64 +/, 22 wide then "==" padding (128-bit value?), normally "jnnkdwkBqGv5+jlf1u/k7A==" for version 2022.1.28.1335
    currentHosting: bool
    currentSessionAccessLevel: int  # 0 = private(enum name unknown), 2 = ?, 3 = "FriendsOfFriends", 4 = "RegisteredUsers"...?, 5 = "Anyone"
    currentSessionHidden: bool
    isMobile: bool
    lastStatusChange: datetime.datetime  # Defaults to "2018-01-01T00:00:00" which we'll also report but we'll format it consistently as per everything else
    # neosVersion: Optional[str] = None  # Normally "2022.1.28.1335"
    onlineStatus: str  # "Offline", "Busy", "Away", "Online", ...?
    outputDevice: str  # outputDevice: ? = "Unknown", 1 = "Headless", 2 = "Screen", 3 = "VR" - FIXME make an enum for this --GM

    # Optionals
    compatibilityHash: Optional[
        str
    ] = None  # base64 +/, 22 wide then "==" padding (128-bit value?), normally "jnnkdwkBqGv5+jlf1u/k7A==" for version 2022.1.28.1335
    neosVersion: Optional[str] = None  # Normally "2022.1.28.1335"


#
# Message definitions
#


@dataclass(slots=True)
class Message:
    content: str  # WARNING: For "Text" messages, these appear to be limited to no more than 510 characters, maybe 509 is the practical limit. The client will truncate a longer message and append a "..." if whatever the limit is is violated.
    id: str  # MSG-{someuuid}
    lastUpdateTime: datetime.datetime
    messageType: str  # "Text", "SessionInvite" (contains a Session blob), ?
    otherId: str  # "U-{name}" for provided userId
    ownerId: str  # "U-{name}" for userId of the given mailbox
    readTime: Optional[datetime.datetime]
    recipientId: str  # "U-{name}" for provided userId
    sendTime: Optional[datetime.datetime]
    senderId: str  # "U-{name}" for userId of the given mailbox


#
# Session definitions
#


@dataclass(slots=True)
class Session:
    # This is the order they appear to be sent in a direct message invite.
    name: str
    # description: Optional[str] = None
    # correspondingWorldId: Optional[str] = None
    tags: List[str]
    sessionId: str  # "S-{someuuid}"
    normalizedSessionId: str  # "S-{someuuid}".lower()
    hostUserId: str  # "U-{somename}"
    hostMachineId: str  # 22-char public machine ID
    hostUsername: str  # User display name
    compatibilityHash: str  # Usually "jnnkdwkBqGv5+jlf1u/k7A=="
    # universeId: Optional[str] = None
    neosVersion: str  # Usually "2022.1.28.1335"
    headlessHost: bool
    sessionURLs: List[
        str
    ]  # "lnl-nat:///S-{someuuid}", "neos-steam://{steamid}/{usually_1}/S-{someuuid}"
    # parentSessionIds: Optional[List[str]] = None  # TODO: Find this type! --GM
    # nestedSessionIds: Optional[List[str]] = None  # TODO: Find this type! --GM
    sessionUsers: List[SessionUser]
    thumbnail: str  # Typically a neosdb URL like "neosdb:///{sha512_of_contents}.webp" but it could also be "https://operationaldata.neos.com/thumbnails/{someuuid}-v2.webp"
    joinedUsers: int
    activeUsers: int
    totalJoinedUsers: int  # Seems to be 0 maybe?
    totalActiveUsers: int
    maxUsers: int
    mobileFriendly: bool  # Usually false
    sessionBeginTime: datetime.datetime
    lastUpdate: datetime.datetime
    # awaySince: Optional[str] = None  # TODO: Find this type! --GM
    accessLevel: str  # String part of this enum: 0 = private(enum name unknown), 2 = ?, 3 = "FriendsOfFriends", 4 = "RegisteredUsers"...?, 5 = "Anyone"

    # Optionals
    description: Optional[str] = None
    correspondingWorldId: Optional[str] = None
    universeId: Optional[str] = None  # TODO: Find this type! --GM
    parentSessionIds: Optional[List[str]] = None  # TODO: Find this type! --GM
    nestedSessionIds: Optional[List[str]] = None  # TODO: Find this type! --GM
    awaySince: Optional[str] = None  # TODO: Find this type! --GM


@dataclass(slots=True)
class SessionUser:
    username: str  # Visible user name
    userID: str  # camelO - U-{id} format
    isPresent: bool
    outputDevice: int  # outputDevice: 1 = "Headless", 2 = "Screen", 3 = "VR" - FIXME make an enum for this --GM


#
# UserSession definitions
#


@dataclass(slots=True)
class UserSessionRequest:
    #
    # Observed formats:
    #
    # - ownerId, sessionCode
    # - username, password
    #

    rememberMe: bool
    secretMachineId: str
    uniqueDeviceID: str  # 32 hex digit string
    # Optionals follow.

    email: Optional[str] = None
    ownerId: Optional[str] = None
    password: Optional[str] = None
    recoverCode: Optional[str] = None  # TODO: Work out what the actual type is --GM
    # rememberMe: bool
    # secretMachineId: str
    sessionCode: Optional[str] = None
    totp: Optional[str] = None
    # uniqueDeviceID: str  # 32 hex digit string
    username: Optional[str] = None


@dataclass(slots=True)
class UserSessionResponse:
    created: datetime.datetime
    eTag: str  # "W/\"datetime'{urlescape(utcnow)}'\""
    expire: datetime.datetime
    partitionKey: str  # Equal to userId
    rememberMe: bool
    rowKey: str  # Equal to token
    secretMachineId: str  # Echoed
    sourceIP: str  # Same as client IP
    timestamp: datetime.datetime  # Same time used for eTag EXCEPT it uses "+00:00" instead of "Z" at the end
    token: str
    userId: str


#
# Online user stats
#


@dataclass(slots=True)
class OnlineUserStats:
    # This is the order I received this in a dump once.
    captureTimestamp: datetime.datetime
    registeredUserCount: int
    instanceCount: int
    vrUserCount: int
    screenUserCount: int
    headlessUserCount: int
    mobileUserCount: int
    publicSessionCount: int
    activePublicSessionCount: int
    publicWorldUserCount: int

    PartitionKey: str  # This is indeed a camelO - also (almost) exactly the same timestamp as captureTimestamp as a reverse timestamp
    RowKey: str  # This is indeed a camelO - seems to be empty?
    Timestamp: str = "0001-01-01T00:00:00+00:00"  # This is indeed a camelO, also that's the actual timestamp string
    ETag: Optional[str] = None  # This is indeed a camelO


#
# neosSessions
#


#
# When first joining, a POST is sent early and a reply is made, then later on a PATCH is sent.
# These have been checked against a desktop user running the Linux version.
#
# missing in requests: clientIp, eTag, partitionKey, rowKey, timestamp
# missing in responses: countryCode, headDeviceModel, peripherals, userId
# null in all requests: countryCode, headDeviceModel, peripherals
# null in POST requests: reverseTimestamp, sessionId, userId
#
@dataclass(slots=True)
class NeosSessions:
    clientIp: Optional[str] = None  # RESPONSE ONLY
    countryCode: Optional[
        str
    ] = None  # REQUEST ONLY - TODO: Work out what the actual type is --GM
    cpu: Optional[str] = None
    createdWorlds: Optional[int] = None
    eTag: Optional[str] = None  # RESPONSE ONLY - "W/\"datetime'{urlescape(utcnow)}'\""
    gpu: Optional[str] = None
    headDevice: Optional[str] = None
    headDeviceModel: Optional[
        str
    ] = None  # REQUEST ONLY - TODO: Work out what the actual type is --GM
    machineId: Optional[str] = None
    memoryBytes: Optional[int] = None
    neosVersion: Optional[str] = None
    operatingSystem: Optional[str] = None
    partitionKey: Optional[str] = None  # RESPONSE ONLY - Equal to reverseTimestamp.
    peripherals: Optional[
        str
    ] = None  # REQUEST ONLY - TODO: Work out what the actual type is --GM
    reverseTimestamp: Optional[
        str
    ] = None  # This is a long decimal number, in units of 10^-7 seconds until 10000 AD.
    rowKey: Optional[UUID] = None  # RESPONSE ONLY - Equal to sessionId.
    sessionEnd: Optional[datetime.datetime] = None
    sessionId: Optional[UUID] = None
    sessionStart: Optional[datetime.datetime] = None
    systemLocale: Optional[str] = None
    userId: Optional[str] = None  # REQUEST ONLY?
    timestamp: Optional[
        datetime.datetime
    ] = None  # RESPONSE ONLY - same time used for eTag EXCEPT it uses "+00:00" instead of "Z" at the end.
    visitedWorlds: Optional[int] = None


# Smoke tests
neos_sessions_smoke = base.unpack_typed_json(
    NeosSessions,
    {
        "countryCode": None,
        "cpu": "Toaster",
        "createdWorlds": 0,
        "gpu": "llvmpipe",
        "headDevice": "Screen",
        "headDeviceModel": None,
        "machineId": "wwwwwwwwwwwwwwwwwwwwww",
        "memoryBytes": 33698349056,
        "neosVersion": "Beta 2022.1.28.1335",
        "operatingSystem": "Linux 6.4 Artix Linux  64bit",
        "peripherals": None,
        "reverseTimestamp": None,
        "sessionEnd": "0001-01-01T00:00:00",
        "sessionId": "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
        "sessionStart": "2023-08-17T03:29:55.24465Z",
        "systemLocale": "ja-JP",
        "userId": None,
        "visitedWorlds": 0,
    },
)
# logging.warning(f"{neos_sessions_smoke}")
assert neos_sessions_smoke == NeosSessions(
    clientIp=None,
    countryCode=None,
    cpu="Toaster",
    createdWorlds=0,
    eTag=None,
    gpu="llvmpipe",
    headDevice="Screen",
    headDeviceModel=None,
    machineId="wwwwwwwwwwwwwwwwwwwwww",
    memoryBytes=33698349056,
    neosVersion="Beta 2022.1.28.1335",
    operatingSystem="Linux 6.4 Artix Linux  64bit",
    partitionKey=None,
    peripherals=None,
    reverseTimestamp=None,
    rowKey=None,
    sessionEnd=datetime.datetime(1, 1, 1, 0, 0, 0),
    sessionId=UUID("aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"),
    sessionStart=datetime.datetime(2023, 8, 17, 3, 29, 55, microsecond=244650),
    systemLocale="ja-JP",
    userId=None,
    timestamp=None,
    visitedWorlds=0,
)

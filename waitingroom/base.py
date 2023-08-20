# Copyright 2023, GreaseMonkey and the waitingroom contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import datetime
import json
import logging
import math
import typing
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_type_hints,
)
from uuid import UUID

from quart import (
    Quart,
    ResponseReturnValue,
    make_response,
)
from quart_redis import (  # type: ignore
    RedisHandler,
    get_redis,
)
import redis.asyncio

LOG_TYPECHECKS = False


app = Quart(__name__)

# TODO: Get a better config setup working --GM
app.config["REDIS_URI"] = "redis://localhost:6379"

# /api/stats/instanceOnline/{machineid} is polled every 60 seconds by the Neos client.
#
app.config["INSTANCEONLINE_LIFETIME_SECONDS"] = (60.0 * 2) + 20.0
app.config["INSTANCEONLINE_FLUSH_PERIOD_SECONDS"] = 20.0

redis_handler = RedisHandler(app)


def get_redis_typed() -> redis.asyncio.Redis[Any]:
    r: Any
    r = get_redis()
    assert isinstance(r, redis.asyncio.Redis)
    return r


machine_id_values = set(
    "abcdefghijklmnopqrstuvwxyz" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "0123456789" + "-_",
)

machine_id_values_final = set("agqw")


def is_valid_machine_id(machine_id: str) -> bool:
    return (
        len(machine_id) == 22
        and all(map(lambda x: x in machine_id_values, machine_id[:-1]))
        and machine_id[-1] in machine_id_values_final
    )


async def make_json_response(body: Any) -> ResponseReturnValue:
    resp = await make_response(
        json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    )
    resp.mimetype = "application/json; charset=utf-8"
    return resp


async def make_typed_json_response(
    blob: Any,
    *,
    obj_type: Optional[Type[Any]] = None,
    mimetype: Optional[str] = None,
) -> ResponseReturnValue:
    if obj_type is None:
        rt = type(blob)
    else:
        rt = obj_type
    return await make_json_response(default_json_packer(rt, blob))


def check_type(t: Type[Any], value: Any) -> Type[Any]:
    if LOG_TYPECHECKS:
        logging.warning(f"pack type {t!r} {value!r}")
    torig = typing.get_origin(t)
    if LOG_TYPECHECKS:
        logging.warning(f"pack type {t!r} origin {torig!r}")
    if torig is None:
        if not isinstance(value, t):
            raise TypeError(
                f"type mismatch when typechecking JSON: {type(value)!r} is not a closed subset of {t!r}"
            )
        return t
    else:
        targs = typing.get_args(t)
        if LOG_TYPECHECKS:
            logging.warning(f"pack type {t!r} origin {torig!r} args {targs!r}")
        if torig == Union:  # Optional uses this
            for child in targs[:-1]:
                try:
                    return check_type(child, value)
                except TypeError:
                    continue
            else:
                return check_type(targs[-1], value)
        elif torig == List or torig == list:
            (child,) = targs
            return child  # type: ignore
        else:
            raise Exception(f"TODO: type origin {torig!r} args {targs!r}")


def default_json_packer(t: Type[Any], value: Any) -> Any:
    ctype = check_type(t, value)
    if LOG_TYPECHECKS:
        logging.warning(f"pack type {t!r} -> {ctype!r}")

    if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
        return value
    elif value is None:
        return value
    elif isinstance(value, list):
        return [default_json_packer(ctype, v) for v in value]
    elif isinstance(value, datetime.datetime):
        return format_utc_datetime(value)
    elif isinstance(value, UUID):
        return str(value)
    else:
        hints = get_type_hints(type(value))
        return {
            k: default_json_packer(hints[k], getattr(value, k))
            for k in value.__slots__
            if getattr(value, k) is not None
        }


def unpack_typed_json(Base: Type[Any], body: Dict[str, Any]) -> Any:
    # FIXME: Typecheck this thing --GM
    hints = get_type_hints(Base)
    return Base(**{k: default_json_unpacker(hints[k], v) for k, v in body.items()})


def default_json_unpacker(t: Type[Any], v: Any) -> Any:
    if LOG_TYPECHECKS:
        logging.warning(f"unpack type {t!r}")

    torig = typing.get_origin(t)
    if torig is not None:
        targs = typing.get_args(t)
        if torig == Union:
            if len(targs) == 2 and targs[1] == type(None):
                if v is None:
                    return v
                else:
                    t = targs[0]
            else:
                raise Exception(f"TODO origin {torig!r} args {targs!r}")
        else:
            raise Exception(f"TODO origin {torig!r} args {targs!r}")

    if LOG_TYPECHECKS:
        logging.warning(f"unpack type real {t!r}")

    if t == datetime.datetime:
        assert isinstance(v, str)
        return parse_utc_datetime(v)
    elif t == UUID:
        assert isinstance(v, str)
        return UUID(v)
    elif isinstance(v, dict):
        return unpack_typed_json(t, v)
    else:
        return v


def format_utc_datetime(ts: datetime.datetime) -> str:
    # Ignoring suffix here, we don't generate garbage
    return ts.isoformat("T", "microseconds") + "Z"


# Smoke tests
assert (
    format_utc_datetime(datetime.datetime(year=2018, month=1, day=1))
    == "2018-01-01T00:00:00.000000Z"
)


def parse_utc_datetime(s: str) -> datetime.datetime:
    # Strip the timezone component
    if s.endswith("+00:00"):
        s = s.rpartition("+")[0]
    elif s.endswith("Z"):
        s = s[:-1]

    return datetime.datetime.fromisoformat(s)


assert parse_utc_datetime("2018-01-01T00:00:00.000000Z") == datetime.datetime(
    year=2018, month=1, day=1
)
assert parse_utc_datetime("2018-01-01T00:00:00.0000001Z") == datetime.datetime(
    year=2018, month=1, day=1
)
assert parse_utc_datetime("2018-01-01T00:00:00.0000012Z") == datetime.datetime(
    year=2018, month=1, day=1, microsecond=1
)
assert parse_utc_datetime("2018-01-01T00:00:00") == datetime.datetime(
    year=2018, month=1, day=1
)
assert parse_utc_datetime("2018-01-01T00:00:00.000000+00:00") == datetime.datetime(
    year=2018, month=1, day=1
)
assert parse_utc_datetime("2018-01-01T00:00:00.0000001+00:00") == datetime.datetime(
    year=2018, month=1, day=1
)
assert parse_utc_datetime("2018-01-01T00:00:00.0000012+00:00") == datetime.datetime(
    year=2018, month=1, day=1, microsecond=1
)


# UNIX timestamp for one hour into the start of 10000 AD.
_EPOCHALYPSE = (
    int(
        round(
            datetime.datetime(
                year=9999,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
            ).timestamp()
        )
    )
    + (365 * 24 * 60 * 60)
    + (60 * 60)
) * 10_000_000


def compute_reverse_timestamp(ts: datetime.datetime) -> int:
    tsunix = (int(round(ts.replace(microsecond=0).timestamp())) * 10_000_000) + (
        ts.microsecond * 10
    )
    result = _EPOCHALYPSE - tsunix
    logging.warning(f"smoke test: compute_reverse_timestamp: {ts!r} -> {result}")
    return result


# BASIC SMOKE TEST
# We don't have 1/10 usec accuracy so go for usec accuracy.
# Actual value received from my data was 2517116271230034043, so not sure what took ~2355 usecs.
assert (
    compute_reverse_timestamp(
        datetime.datetime(
            year=2023,
            month=7,
            day=29,
            hour=23,
            minute=34,
            second=36,
            microsecond=998951,
        )
    )
    == 2517116271230010490
)

assert (
    compute_reverse_timestamp(
        datetime.datetime(
            year=2023,
            month=7,
            day=29,
            hour=23,
            minute=34,
            second=57,
            microsecond=320033,  # +0.4
        )
    )
    == 2517116271026799670
    # >2517116271026799665
)

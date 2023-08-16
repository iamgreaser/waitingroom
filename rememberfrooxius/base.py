from __future__ import annotations

import datetime
import json
import logging
import math
from typing import (
    Any,
    Dict,
    Type,
)
from uuid import UUID

from flask import (
    Flask,
    Response,
    make_response,
)


app = Flask(__name__)


def make_json_response(body: Any) -> Response:
    resp = make_response(json.dumps(body))
    resp.mimetype = "application/json; charset=utf-8"
    return resp


def make_typed_json_response(blob: Any) -> Response:
    # FIXME: Typecheck this thing --GM
    if hasattr(type(blob), "pack_field"):
        return make_json_response(
            {
                k: type(blob).pack_field(default_json_packer, k, getattr(blob, k))
                for k in blob.__slots__
                if getattr(blob, k) is not None
            }
        )
    else:
        return make_json_response(
            {
                k: default_json_packer(getattr(blob, k))
                for k in blob.__slots__
                if getattr(blob, k) is not None
            }
        )


def unpack_typed_json(Base: Type[Any], body: Dict[str, Any]) -> Any:
    # FIXME: Typecheck this thing --GM
    if hasattr(Base, "unpack_field"):
        return Base(
            **{k: Base.unpack_field(lambda x: x, k, v) for k, v in body.items()}
        )
    else:
        return Base(**body)


def format_utc_datetime(ts: datetime.datetime, suffix: str = "Z") -> str:
    return ts.isoformat("T") + suffix


def default_json_packer(value: Any) -> Any:
    if isinstance(value, datetime.datetime):
        return format_utc_datetime(value)
    elif isinstance(value, UUID):
        return str(value)
    else:
        return value


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

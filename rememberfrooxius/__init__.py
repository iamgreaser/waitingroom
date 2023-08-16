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
# ASSETS:
#

# These are under "/api".
ASSET_PATHS = {
    "/api/groups": [
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/ShapeTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/MaterialTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/GlueTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/GrabbableSetterTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/Microphone",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/CharacterColliderSetterTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/DevToolTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/LightTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ShortcutTooltips/LogixTip",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/ViewVisual",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/VR_Glove_Left",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/VR_Headset",  # FIXME: NONFREE ASSET --GM
        "G-Neos/records/root/Inventory/SpawnObjects/VR_Glove_Right",  # FIXME: NONFREE ASSET --GM
    ]
}
for asset_root, asset_list in ASSET_PATHS.items():
    for asset_name in asset_list:

        def _f0(urlpath: str, localpath: str) -> None:
            def _f1() -> Response:
                with app.open_resource(localpath, "rb") as f:
                    return make_response(f.read(), 200)

            _f1.__name__ = "path$" + urlpath
            app.route(urlpath)(_f1)

        _f0(asset_root + "/" + asset_name, "cloudbase/" + asset_name)

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

# Copyright 2023, GreaseMonkey and the waitingroom contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import logging
import subprocess

from quart import (
    ResponseReturnValue,
    make_response,
)

from .base import (
    app,
    format_utc_datetime,
    make_json_response,
)

# Endpoints
from . import (
    api,
    hub,
    install_ServerResponse,
)

# Background tasks
from . import (
    tasks,
)


#
# ASSETS:
#

# These are under "/api".
ASSET_PATHS = {
    "/api/groups/G-Neos/records/root/Inventory/SpawnObjects": {
        # FIXME THESE ARE NONFREE ASSETS FOR BOOTSTRAPPING PURPOSES --GM
        "ShortcutTooltips/CharacterColliderSetterTip": "28/196c6a8c41f9e4514e32d8e218e2324b92cd9270a4e3b4000508732ada46cd",
        "ShortcutTooltips/DevToolTip": "1e/dfac0d0f4ca3cbe7a151b1bf90a1de537c7c72b87844ebda4d1fcfcc9a82b1",
        "ShortcutTooltips/GlueTip": "25/7d2f2ed87e9858243722b4f136987af3231c401a83972aee6db8ff8a76ca3f",
        "ShortcutTooltips/GrabbableSetterTip": "84/c6224e179c61b52f1cb7c82366c055975efe90c3b38a9ed0ce8038640e6d79",
        "ShortcutTooltips/LightTip": "74/35ac782f5e6d1321e9fee39ef5b87ed7e22f34cf9aa841b29bc61d346f3b9e",
        "ShortcutTooltips/LogixTip": "dd/2aceb4a9438a0dea9c68dbf7b08db8a7a3a8fa8f139df121bb28f9646357f0",
        "ShortcutTooltips/MaterialTip": "fb/fa5d8efc85236afaf579e455175235af6e49c1053a9477abea7378e1d70d4a",
        "ShortcutTooltips/Microphone": "0c/ac2446567e462b865796155ffa30a2b9483e09b4bd94cc9c665899d2893452",
        "ShortcutTooltips/ShapeTip": "3f/35fc95dcefae5915b866372b5733abb55082d044e1baa6da847af250bad78c",
        "VR_Glove_Left": "f8/b65ce4442ac97fd1f0958747b209fc2d3f2bd867f4b3a378e3a7476c8f75e7",
        "VR_Glove_Right": "20/073f60d896d45b7281bca15eb2e1df026cc83bca3bc4b7a0ccea2a75434bd6",
        "VR_Headset": "6a/6023e7bff6af447d6a5779285e10063a68542bb97fdc64620c3e5b3ba17183",
        "ViewVisual": "97/ede1ce17cf9e09399bb873dc73d093933c816730c725232db32e9edff59fe8",
    }
}
for asset_root, asset_map in ASSET_PATHS.items():
    for asset_name, asset_hash in asset_map.items():

        def _f0(urlpath: str, localpath: str) -> None:
            async def _f1() -> ResponseReturnValue:
                async with await app.open_resource(localpath, "rb") as f:
                    return await make_response(await f.read(), 200)

            _f1.__name__ = "path$" + urlpath
            app.route(urlpath)(_f1)

        _f0(asset_root + "/" + asset_name, "cloudseed/" + asset_hash)

#
# TESTING: /
#


@app.route("/")
async def root() -> ResponseReturnValue:
    resp = await make_response(
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

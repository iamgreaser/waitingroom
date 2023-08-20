WARNING THIS THING IS INCOMPLETE. but help would be much appreciated, i can be found on the fediverse here: `@GreaseMonkey@misskey.neos.love`

tested on Python 3.11. older versions might not work - if you have 3.8 or later and you want to support your version then you're responsible for maintaining it.

there are no plans to support running the server on Windows. if you still insist on using that garbage, consider using WSL.

running this thing boils down to:

- running a Redis server with the given redis.conf file or something similar: `mkdir -p ./db && redis-server ./redis.conf`
- setting up and activating a Python venv: `python3 -m venv venv` then `. venv/bin/activate`
- install all the pip requirements: `pip install -r requirements.txt`
- running: `python3 -m waitingroom`
- pointing all Neos HTTPS connections to this server - for this i'm using mitmproxy where there are some incomplete instructions in `./docs/mitmproxy_setup.md`, although i should probably add in the `LD_PRELOAD` library i'm using to force Neos to pipe all port 80 + port 443 stuff this way

licensing:

- code is AGPLv3.0-or-later
- THERE ARE NONFREE ASSETS REQUIRED FOR BOOTSTRAPPING. these will probably be replaced with either free assets (likely CC-0-licensed) or a script to fetch them or something. currently what we have is:
    - replaceable parts:
        - JSON records for default avatar components: VR headset, left + right hands, third-person camera
        - JSON records for desktop shortcut tooltips


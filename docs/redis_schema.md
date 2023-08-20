Redis schema

Using the `unix/path/like` convention for stuff.

## Online users

- sorted set `stats/instanceOnline`:
    - member = machine ID
    - score = unix timestamp of last POST sent as a float (that is, Python `time.time()`)


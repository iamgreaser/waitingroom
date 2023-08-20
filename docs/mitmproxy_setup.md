Setting up mitmproxy for testing:

Firstly, set up mitmproxy properly so that you have all the certificates you need in your trusted root store. (TODO: Document this --GM)

Then, in your settings, set `map_remote` to:

    |https?://[^/]*/|http://127.0.0.1:5000/

and then you should be good. Hopefully.

I also use an `LD_PRELOAD` shim to route all requests to connect to ports 80 and 443 to either `127.0.0.1` (IPv4) or `::1` (IPv6, although I'm not sure if Neos actually does this lol).


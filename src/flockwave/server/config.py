"""Default configuration for the Flockwave server.

This script will be evaluated first when the server attempts to load its
configuration. Configuration files may import variables from this module
with `from flockwave.server.config import SOMETHING`, and may also modify
them if the variables are mutable. For instance, to disable an extension
locally, create a configuration file containing this:

    from flockwave.server.config import EXTENSIONS
    del EXTENSIONS["extension_to_disable"]
"""

import platform

ON_MAC = platform.system().lower() == "darwin"

# Secret key to encode cookies and session data
SECRET_KEY = (
    b"\xa6\xd6\xd3a\xfd\xd9\x08R\xd2U\x05\x10\xbf\x8c2\t\t\x94\xb5R\x06z\xe5\xef"
)

# Configure the command execution manager
COMMAND_EXECUTION_MANAGER = {"timeout": 30}

# Declare the list of extensions to load
EXTENSIONS = {
    "auth": {},
    "auth_basic": {},
    "debug": {"route": "/debug"},
    "fake_uavs": {
        "count": 3,
        "delay": 1.9,
        "enabled": True,
        "id_format": "COLLMOT-{0:02}",
        "center": {
            # ELTE kert
            "lat": 47.473360,
            "lon": 19.062159,
            "agl": 20,
        },
        "radius": 50,
        "time_of_single_cycle": 10,
    },
    "flockctrl": {
        "id_format": "{0:02}",
        "connections": {
            # "wireless": "default"
            "wireless": "local"
        },
    },
    "gps": {
        # "connection": "/dev/cu.usbmodem1411",
        "connection": "gpsd",
        "id_format": "BEACON:{0}",
    },
    "http_server": {},
    "mavlink": {"enabled": False, "id_format": "MAV-{0:02}"},
    "radiation": {
        "sources": [{"lat": 47.473313, "lon": 19.062818, "intensity": 50000}],
        "background_intensity": 10,
    },
    "socketio": {},
    "smpte_timecode": {"connection": "midi:IAC Driver Bus 1"},
    "ssdp": {},
    "system_clock": {},
    "tcp": {},
    "udp": {},
}

# smpte_timecode seems to have some problems on a Mac - it consumes 15% CPU
# even when idle, and it starts throwing messages like this on the console
# after a while if there is no MIDI device:
#
# MidiInCore::initialize: error creating OS-X MIDI client object (-50)
if ON_MAC:
    EXTENSIONS.pop("smpte_timecode", None)
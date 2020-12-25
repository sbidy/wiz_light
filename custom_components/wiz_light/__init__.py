"""WiZ Light integration."""
import logging
import socket
import threading
import json
import time

import voluptuous as vol

from homeassistant.const import (
    CONF_PORT,
    EVENT_HOMEASSISTANT_START,
    EVENT_HOMEASSISTANT_STOP,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 38900
DOMAIN = "wiz_light"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up Wiz Light."""
    if "wiz_light" in config:
        conf = config[DOMAIN]
        port = conf.get(CONF_PORT)
        listener = WizLightBroadcastListener(hass, port)
        #hass.data[DOMAIN] = listener
        hass.bus.listen_once(EVENT_HOMEASSISTANT_START, listener.start_listen)
        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, listener.shutdown)
    return True


class WizLightBroadcastListener(threading.Thread):
    """WizLight broadcast listener."""

    def __init__(self, hass, port):
        """Initialize."""
        super().__init__(daemon=True)
        self._hass = hass
        self._port = port
        self._socket = None
        self._shutdown = False
        self._firstBeats = {}
        _LOGGER.debug("Listener initialized")

    def start_listen(self, event):
        """Start thread."""
        _LOGGER.debug("Start thread")
        self.start()

    def shutdown(self, event):
        """Shutdown thread."""
        _LOGGER.debug("Shutdown thread")
        self._shutdown = True
        self._close_socket()

    def run(self):
        """Event thread."""
        self._create_socket()
        while True:
            if self._shutdown:
                break
            try:
                datastr, address = self._socket.recvfrom(2048)
                ip, port = address
                self._parse_broadcast((datastr.decode('utf-8')).rstrip(), ip)
            except socket.timeout:
                continue
        self._close_socket()

    def _create_socket(self):
        """Create socket."""
        if self._socket is None:
            _LOGGER.debug("Create socket: %i", self._port)
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._socket.settimeout(10)
            self._socket.bind(('', self._port))

    def _close_socket(self):
        """Close socket."""
        _LOGGER.debug('Close socket')
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def _parse_broadcast(self, datastr, ip):
        """Parse incoming broadcase."""
        _LOGGER.debug("Got broadcast from %s: %s", ip, datastr)
        try:
            data = json.loads(datastr)
        except:
            _LOGGER.debug("Unparseable broadcast.")
            return
        if "method" in data and data["method"] == "firstBeat":
            now = int(time.time())
            if (not ip in self._firstBeats) or (now-self._firstBeats[ip] > 180):
                self._firstBeats[ip] = now
                _LOGGER.debug("Got firstBeat from %s", ip)
                time.sleep(1) # Waiting for bulbs to be ready, one second seems to work
                self._hass.bus.fire("wiz_light_first_beat", {"ip": ip})
            else:
                _LOGGER.debug("Got firstBeat from %s but still cooling down from previous one.", ip)
        else:
            _LOGGER.debug("Unknown broadcast.")

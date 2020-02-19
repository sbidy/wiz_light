"""Platform for light integration."""
import logging
import voluptuous as vol
from pywizlight import wizlight


import homeassistant.util.color as color_utils
import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, PLATFORM_SCHEMA, Light, ATTR_RGB_COLOR, SUPPORT_COLOR, SUPPORT_BRIGHTNESS)
from homeassistant.const import CONF_HOST

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
})

SUPPORT_FEATURES = (SUPPORT_BRIGHTNESS | SUPPORT_COLOR )

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the WiZ Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    ip = config[CONF_HOST]
    bulb = wizlight(ip)

    # Add devices
    add_entities([WizBulb(bulb)])


class WizBulb(Light):
    """Representation of WiZ Light bulb"""

    def __init__(self, light):
        """Initialize an WiZLight."""
        self._light = light
        self._state = None
        self._brightness = None
        self._name = None
        self._rgb = None

    @property
    def brightness(self):
        """Return the brightness of the light. """
        return self._brightness

    @property
    def rgb_color(self):
        """Return the color property."""
        return self._color

    @property
    def name(self):
        """Return the ip as name of the device if any."""
        return self._light.ip

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        if ATTR_RGB_COLOR in kwargs:
            self._rgb = kwargs[ATTR_RGB_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        self._light.turn_on()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.turn_off()

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_FEATURES

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._light.status
        self._brightness = self._light.brightness
        self._color = self._light.color
        self._name = self._light.ip
        self._rgb = self._light.rgb

    def hex_to_percent(self, hex):
        return (hex/255)*100

    def percent_to_hex(self, percent):
        return (percent / 100)*255

'''
    ToDO:
        - Change ATTR_BRIGHTNESS to ATTR_BRIGHTNESS_PCT ??
        - ATTR_EFFECT_LIST - List of possible effects
        - @property def white_value(self)

'''


"""Platform for light integration."""
''' Stephan Traub @sbidy '''

import logging
import voluptuous as vol
from pywizlight import wizlight
from homeassistant.exceptions import InvalidStateError
from homeassistant.core import callback

from homeassistant.const import STATE_OFF, STATE_ON

import homeassistant.util.color as color_utils
import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    Light,
    ATTR_RGB_COLOR,
    SUPPORT_COLOR,
    SUPPORT_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    SUPPORT_COLOR_TEMP,
    ATTR_HS_COLOR,
    SUPPORT_EFFECT,
    ATTR_EFFECT
    )
from homeassistant.const import CONF_HOST, CONF_NAME

_LOGGER = logging.getLogger(__name__)
_VALID_STATES = [STATE_ON, STATE_OFF, "True", "False", "true", "false"]

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
})

SUPPORT_FEATURES = (SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_COLOR_TEMP | SUPPORT_EFFECT)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """
        Set up the WiZ Light platform.
    """
    # Assign configuration variables.
    # The configuration check takes care they are present.
    ip = config[CONF_HOST]
    bulb = wizlight(ip)

    # Add devices
    add_entities([WizBulb(bulb, config[CONF_NAME])])


class WizBulb(Light):
    """
        Representation of WiZ Light bulb
    """

    def __init__(self, light, name):
        """
            Initialize an WiZLight.
        """
        self._light = light
        self._state = None
        self._brightness = None
        self._name = name
        self._rgb_color = None
        self._temperature = None
        self._hscolor = None
        self._available = None
        self._effect = None
        self._scenes = []

    @property
    def brightness(self):
        """
            Return the brightness of the light.
        """
        return self._brightness

    @property
    def rgb_color(self):
        """
            Return the color property.
        """
        return self._rgb_color

    @property
    def hs_color(self):
        """Return the hs color value."""
        return self._hscolor

    @property
    def name(self):
        """
            Return the ip as name of the device if any.
        """
        return self._name

    @property
    def is_on(self):
        """
            Return true if light is on.
        """
        return self._state

    async def async_turn_on(self, **kwargs):
        """
            Instruct the light to turn on.
        """
        if ATTR_RGB_COLOR in kwargs:
            self._light.rgb = kwargs[ATTR_RGB_COLOR]
        if ATTR_HS_COLOR in kwargs:
           self._light.rgb = color_utils.color_hs_to_RGB(kwargs[ATTR_HS_COLOR][0], kwargs[ATTR_HS_COLOR][1])
        if ATTR_BRIGHTNESS in kwargs:
           self._light.brightness = kwargs[ATTR_BRIGHTNESS]
        if ATTR_COLOR_TEMP in kwargs:
            kelvin = color_utils.color_temperature_mired_to_kelvin(kwargs[ATTR_COLOR_TEMP])
            self._light.colortemp = kelvin
        if ATTR_EFFECT in kwargs:
            _LOGGER.info("Effekt %s", ATTR_EFFECT)
            self._light.scene = self.scene_helper(kwargs[ATTR_EFFECT])
        self._light.turn_on()

    async def async_turn_off(self, **kwargs):
        """
            Instruct the light to turn off.
        """
        self._light.turn_off()

    @property
    def color_temp(self):
        """
            Return the CT color value in mireds.
        """
        return self._temperature

    @property
    def min_mireds(self):
        """
            Return the coldest color_temp that this light supports.
        """
        return color_utils.color_temperature_kelvin_to_mired(6500)

    @property
    def max_mireds(self):
        """
            Return the warmest color_temp that this light supports.
        """
        return color_utils.color_temperature_kelvin_to_mired(2500)

    @property
    def supported_features(self) -> int:
        """
            Flag supported features.
        """
        return SUPPORT_FEATURES
    
    @property
    def effect(self):
        """Return the current effect."""
        return self._effect

    @property
    def effect_list(self):
        """Return the list of supported effects."""
        return self._scenes

    @property
    def available(self):
        """Return if light is available."""
        return self._available

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self.update_availability()
        self.update_state()
        self.update_brightness()
        self.update_temperature()
        self.update_color()
        self.update_effect()
        self.update_scene_list()

        # deprecated - should be deleted
        # self._rgb_color = self._light.rgb

# ---- CALLBACKS -----
    @callback
    def update_brightness(self):
        """
            Update the brightness.
        """
        if self._light.brightness is None:
            return
        try:
            brightness = self._light.brightness
            if 0 <= int(brightness) <= 255:
                self._brightness = int(brightness)
            else:
                _LOGGER.error(
                    "Received invalid brightness : %s. Expected: 0-255", brightness
                )
                self._brightness = None
        except Exception as ex:
            _LOGGER.error(ex)
            self._state = None
    @callback
    def update_state(self):
        """
            Update the state
        """
        if self._light.status is None:
            return
        try:
            self._state = self._light.status
            return
        except Exception as ex:
            _LOGGER.error(ex)
            self._state = None
    @callback
    def update_temperature(self):
        """
            Update the temperature
        """
        if self._light.colortemp is None:
            return
        try:
            temperature = color_utils.color_temperature_kelvin_to_mired(self._light.colortemp)
            if self.min_mireds <= temperature <= self.max_mireds:
                self._temperature = temperature
            else:
                _LOGGER.error(
                    "Received invalid color temperature : %s. Expected: 0-%s",
                    temperature,
                    self.max_mireds,
                )
                self._temperature = None
        except Exception:
            _LOGGER.error("Cannot evaluate temperature", exc_info=True)
            self._temperature = None
    @callback
    def update_color(self):
        """
            Update the hs color
        """
        if self._light.rgb is None:
            return
        try:
            r, g, b = self._light.rgb
            if r is None:
                # this is the case if the temperature was changed - no infomation was return form the lamp.
                # do nothing until the RGB color was changed
                return
            color = color_utils.color_RGB_to_hs(r,g,b)
            if color is not None:
                self._hscolor = color
            else:
                _LOGGER.error(
                    "Received invalid HS color : %s", color
                )
                self._hscolor = None
        except Exception:
            _LOGGER.error("Cannot evaluate color", exc_info=True)
            self._hscolor = None

    @callback
    def update_availability(self):
        '''
            update the bulb availability
        '''
        self._available = self._light.getConnection
    
    @callback
    def update_effect(self):
        '''
            update the bulb availability
        '''
        self._effect = self._light.scene
    @callback

    # this should be improved :-)
    def update_scene_list(self):
        self._scenes = []
        for id in self._light.SCENES:
            self._scenes.append(self._light.SCENES[id])

    def scene_helper(self, scene):
        for id in self._light.SCENES:
            if self._light.SCENES[id] == scene:
                return id
            else:
                return 0
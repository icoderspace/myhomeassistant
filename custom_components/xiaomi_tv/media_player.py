"""
Add support for the Xiaomi TVs.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/xiaomi_tv/
"""

import logging

import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON)
from homeassistant.components.media_player import (
    SUPPORT_TURN_ON, SUPPORT_TURN_OFF, MediaPlayerDevice, PLATFORM_SCHEMA,
    SUPPORT_VOLUME_STEP)

REQUIREMENTS = ['pymitv==1.5.0']

DEFAULT_NAME = "Xiaomi TV"

_LOGGER = logging.getLogger(__name__)

SUPPORT_XIAOMI_TV = SUPPORT_VOLUME_STEP | SUPPORT_TURN_ON | SUPPORT_TURN_OFF

# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Xiaomi TV platform."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    _LOGGER.info("add Xiaomi TV.config:%s", config)
    add_devices([XiaomiTV(host, name)])


class XiaomiTV(MediaPlayerDevice):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, ip, name):
        """Receive IP address and name to construct class."""
        # Import pymitv library.
        from pymitv import TV

        # Initialize the Xiaomi TV.
        self._tv = TV(ip)
        # Default name value, only to be overridden by user.
        self._state = STATE_OFF
        self._name = name
        self._ip = ip

    @staticmethod
    def check_ip(ip_address, log=False):
        """Attempts a connection to the TV and checks if there really is a TV."""
        if log:
            print('Checking ip: {}...'.format(ip_address))

        request_timeout = 0.3

        try:
            tv_url = 'http://{}:6095/request?action=isalive'.format(ip_address)
            request = requests.get(tv_url, timeout=request_timeout)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
            return False

        return request.status_code == 200

    def update(self):
        _LOGGER.debug("updating Xiaomi TV status :%s", self._state)
        if self.check_ip(self._ip):
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
        _LOGGER.debug("update Xiaomi TV status :%s", self._state)

    @property
    def name(self):
        """Return the display name of this TV."""
        return self._name

    @property
    def state(self):
        """Return _state variable, containing the appropriate constant."""
        return self._state

    @property
    def assumed_state(self):
        """Indicate that state is assumed."""
        return True

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_XIAOMI_TV

    def turn_off(self):
        """
        Instruct the TV to turn sleep.

        This is done instead of turning off,
        because the TV won't accept any input when turned off. Thus, the user
        would be unable to turn the TV back on, unless it's done manually.
        """
        if self._state == STATE_ON:
            self._tv.turn_off()
        self._state = STATE_OFF

    def turn_on(self):
        """Wake the TV back up from sleep."""
        self._tv.wake()

        self._state = STATE_ON

    def volume_up(self):
        """Increase volume by one."""
        self._tv.volume_up()

    def volume_down(self):
        """Decrease volume by one."""
        self._tv.volume_down()

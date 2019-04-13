import logging
import time

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, WEEKDAYS
from homeassistant.components.binary_sensor import BinarySensorDevice
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = '工作日'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Workday sensor."""
    sensor_name = config.get(CONF_NAME)
    add_entities([IsWorkdaySensor(sensor_name, 10003, "b59bc3ef6191eb9f747dd4e83c99f2a4")], True)


class IsWorkdaySensor(BinarySensorDevice):
    """Implementation of a Workday sensor."""

    def __init__(self, name, app_key, sign):
        self._name = name
        self._date = None
        self._state = None
        self._app_key = app_key
        self._sign = sign

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def app_key(self):
        return self._app_key

    @property
    def sign(self):
        return self._sign

    def update(self):
        """Get date and look whether it is a holiday."""
        # Default is  workday

        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        # 一天只查询一次
        if self._date == date:
            return
        params = {
            "app": "life.workday",
            "date": date,
            "appkey": self.app_key,
            "sign": self.sign,
            "format": "json"
        }
        _LOGGER.info("update holiday.param:%s", params)
        self._state = True
        try:
            # http://api.k780.com:88/?app=life.workday&date=20150903&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4&format=json
            response = requests.get("http://api.k780.com:88/", params)
            json = response.json()
            _LOGGER.info("update holiday: %s", json)
            result = json.get("result").get("workmk")
            self._state = result == '1'
            self._date = date
        except Exception as e:
            _LOGGER.error(e)

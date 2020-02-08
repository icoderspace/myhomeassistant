import logging
import time
from threading import Thread

from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.xiaomi_aqara import PY_XIAOMI_GATEWAY, XiaomiDevice
from homeassistant.components.xiaomi_aqara.binary_sensor import XiaomiBinarySensor, ATTR_LAST_ACTION

CONF_GATEWAY_COUNT = "gateway_count"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_GATEWAY_COUNT, default=2): cv.positive_int
})
_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Xiaomi devices."""
    devices = []
    gateway_count = config.get(CONF_GATEWAY_COUNT)
    while len(hass.data[PY_XIAOMI_GATEWAY].gateways) != gateway_count:
        time.sleep(2)
    for (_, gateway) in hass.data[PY_XIAOMI_GATEWAY].gateways.items():
        for device in gateway.devices["binary_sensor"]:
            model = device["model"]
            if model in [
                "86sw1"
            ]:
                if "proto" not in device or int(device["proto"][0:1]) == 1:
                    data_key = "channel_0"
                else:
                    data_key = "button_0"
                devices.append(
                    XiaomiExtendButton(device, "Extend Wall Switch", data_key, hass, gateway)
                )
            elif model in [
                "86sw2"
            ]:
                if "proto" not in device or int(device["proto"][0:1]) == 1:
                    data_key_left = "channel_0"
                    data_key_right = "channel_1"
                else:
                    data_key_left = "button_0"
                    data_key_right = "button_1"
                devices.append(
                    XiaomiExtendButton(
                        device, "Extend Wall Switch (Left)", data_key_left, hass, gateway
                    )
                )
                devices.append(
                    XiaomiExtendButton(
                        device, "Extend Wall Switch (Right)", data_key_right, hass, gateway
                    )
                )
                devices.append(
                    XiaomiExtendButton(
                        device, "Extend Wall Switch (Both)", "dual_channel", hass, gateway
                    )
                )
    add_entities(devices)


class XiaomiExtendButton(XiaomiBinarySensor):
    """Representation of a Xiaomi Button."""

    def __init__(self, device, name, data_key, hass, xiaomi_hub):
        """Initialize the XiaomiButton."""
        self._hass = hass
        self._last_action = None
        self._clicking = False
        _LOGGER.info("XiaomiExtendButton init name: %s,data_key:%s", name, data_key)
        XiaomiBinarySensor.__init__(self, device, name, xiaomi_hub, data_key, None)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_LAST_ACTION: self._last_action}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""

        value = data.get(self._data_key)
        _LOGGER.debug("parse_data :%s,raw_data:%s", value, raw_data)
        if value is None:
            return False
        if value == "click":
            click_type = "single"
        elif value == "both_click":
            click_type = "both"
        else:
            _LOGGER.error("unsupported click type:%s,raw_data:%s", value, raw_data)
            return False
        if self._clicking:
            self._clicking = False
            self._fire_event("double")
        else:
            self._clicking = True
            thread = Thread(target=self._check_click_type, args=(click_type,))
            thread.start()
        return True

    def _check_click_type(self, click_type):
        # 延时一秒，如果一秒内没有新的动作，则认为是单击，否则就是双击
        time.sleep(0.7)
        if self._clicking:
            self._clicking = False
            self._fire_event(click_type)

    def _fire_event(self, click_type):
        _LOGGER.debug("_fire_event click_type:%s", click_type)
        self._hass.bus.fire(
            "xiaomi_aqara.click",
            {"entity_id": self.entity_id, "click_type": click_type},
        )
        self._last_action = click_type

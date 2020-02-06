import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.xiaomi_aqara import PY_XIAOMI_GATEWAY, XiaomiDevice
from homeassistant.components.xiaomi_aqara.switch import XiaomiGenericSwitch
from homeassistant.const import CONF_HOST, CONF_ID

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_ID): cv.string,
})
_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    devices = []
    host = config.get(CONF_HOST)
    sid = config.get(CONF_ID)
    gateway = hass.data[PY_XIAOMI_GATEWAY].gateways.get(host)
    _LOGGER.info("setup for xiaomi relay")
    device = {
        "model": "relay",
        "proto": gateway.proto,
        "sid": sid,
        "short_id": 0,
        "data": {},
        "raw_data": {}}
    devices.append(
        XiaomiGenericSwitch(
            device, "Relay Left", "channel_0", False, gateway
        )
    )
    devices.append(
        XiaomiGenericSwitch(
            device, "Relay Right", "channel_1", False, gateway
        )
    )
    add_entities(devices)

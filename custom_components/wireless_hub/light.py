from homeassistant.components.light import Light

from custom_components.wireless_hub import DATA_WIRELESS_HUB


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Xiaomi devices."""

    add_entities([KitchenLight("KitchenLight", hass.data[DATA_WIRELESS_HUB])])


class KitchenLight(Light):
    def __init__(self, name, hub):
        self._name = name
        self._date = None
        self._state = False
        self._hub = hub

    @property
    def is_on(self):
        """Return true if it is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._hub.send_rf("48a2a3dd")
        self._state = True

    def turn_off(self, **kwargs):
        """Turn the switch on."""
        self._hub.send_rf("48a2a3db")
        self._state = False

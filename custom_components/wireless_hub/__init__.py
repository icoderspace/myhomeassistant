import json
import logging
import socket
import voluptuous as vol
from threading import Thread

from homeassistant.const import CONF_HOST, CONF_PORT, EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'wireless_hub'
CONF_DISCOVERY_RETRY = 'discovery_retry'
CONF_DEVICE_ID = 'device_id'
CONF_SEND_PORT = 'send_port'
CONF_LISTEN_PORT = 'listen_port'
CONF_CLIENT = 'clients'

SERVICE_SEND_RF = 'send_rf_'
SERVICE_SEND_IR = 'send_ir_'
SERVICE_LEARN_IR = 'learn_ir_'
SERVICE_LEARN_RF = 'learn_rf_'

ATTR_RF_COMMAND = 'rf_command'
ATTR_IR_COMMAND = 'ir_command'

DATA_WIRELESS_HUB = 'wireless_hub'

HUB_CONFIG = vol.Schema({
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_SEND_PORT, default=7000): cv.port,
    vol.Optional(CONF_LISTEN_PORT, default=1319): cv.port,
    vol.Optional(CONF_DISCOVERY_RETRY, default=3): cv.positive_int
})

# CONFIG_SCHEMA = vol.Schema({
#     DOMAIN: vol.All(cv.ensure_list, HUB_CONFIG)
# }, extra=vol.ALLOW_EXTRA)

SERVICE_SEND_RF_SCHEMA = vol.Schema({
    vol.Required(ATTR_RF_COMMAND): cv.string
})

SERVICE_SEND_IR_SCHEMA = vol.Schema({
    vol.Required(ATTR_IR_COMMAND): cv.string
})


def send_rf_service(hub):
    def service(call):
        command = call.data.get(ATTR_RF_COMMAND)
        hub.send_rf(command)

    return service


def send_ir_service(hub):
    def service(call):
        command = call.data.get(ATTR_IR_COMMAND)
        hub.send_ir(command)

    return service


def learn_ir_service(hub):
    def service(call):
        hub.learn_ir()

    return service


def learn_rf_service(hub):
    def service(call):
        hub.learn_rf()

    return service


def setup(hass, config):
    """Set up the Wireless hub component."""
    if DOMAIN in config:
        hub_configs = config[DOMAIN]
        _LOGGER.info("wireless config:%s", hub_configs)
    hubs = []

    for hub_config in hub_configs:
        device_id = hub_config[CONF_DEVICE_ID]
        wireless_hub = WirelessHub(hub_config[CONF_HOST], hub_config[CONF_LISTEN_PORT],
                                   hub_config[CONF_SEND_PORT],
                                   device_id)
        hubs.append(wireless_hub)
        hass.data[DATA_WIRELESS_HUB] = wireless_hub
        hass.services.register(DOMAIN, SERVICE_SEND_RF + device_id, send_rf_service(wireless_hub),
                               schema=SERVICE_SEND_RF_SCHEMA)
        hass.services.register(DOMAIN, SERVICE_SEND_IR + device_id, send_ir_service(wireless_hub),
                               schema=SERVICE_SEND_IR_SCHEMA)
        hass.services.register(DOMAIN, SERVICE_LEARN_RF + device_id, learn_rf_service(wireless_hub))
        hass.services.register(DOMAIN, SERVICE_LEARN_IR + device_id, learn_ir_service(wireless_hub))

    def stop_listen(event):
        _LOGGER.info("Shutting down wireless Hub")
        for hub in hubs:
            hub.stop_listen()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_listen)
    return True


class WirelessHub(Entity):
    def __init__(self, ip, listen_port, send_port, device_id):
        self._ip = ip
        self._listen_port = listen_port
        self._send_port = send_port
        self._device_id = device_id
        self._mcastsocket = None
        self._listening = False
        self._threads = []
        self._message_id = 1

    @property
    def send_port(self):
        return self._send_port

    @property
    def ip(self):
        return self._ip

    @property
    def listen_port(self):
        return self._listen_port

    @property
    def device_id(self):
        return self._device_id

    def listen(self):
        """Start listening."""

        _LOGGER.info('Creating Multicast Socket')
        self._mcastsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._mcastsocket.bind(('0.0.0.0', self._listen_port))
        self._listening = True
        thread = Thread(target=self._listen_to_msg, args=())
        self._threads.append(thread)
        thread.daemon = True
        thread.start()

    def send_rf(self, value):
        self._message_id += 1
        command = self._build_rf_command(value)
        self._send_data(command)

    def send_ir(self, value):
        self._message_id += 1
        command = self._build_ir_command(value)
        self._send_data(command)

    def learn_ir(self):
        self._message_id += 1
        command = self._build_ir_command("", 1)
        self._send_data(command)

    def learn_rf(self):
        self._message_id += 1
        command = self._build_rf_command("", 1)
        self._send_data(command)

    def _build_ir_command(self, value, t=0):
        return json.dumps({
            "msg_type": "set",
            "msg_id": self._message_id,
            "device_id": self.device_id,
            "services": {
                "ir": {
                    "type": t,
                    "value": value
                }
            }
        })

    def _build_rf_command(self, value, t=0):
        return json.dumps({
            "msg_type": "set",
            "msg_id": self._message_id,
            "device_id": self.device_id,
            "services": {
                "rf": {
                    "type": t,
                    "value": value
                }
            }
        })

    def _send_data(self, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.sendto(data.encode(), (self.ip, self.send_port))
            _LOGGER.info("send data:%s", data)
        except socket.timeout:
            _LOGGER.error("Cannot connect to wireless hub")
        finally:
            s.close()

    def stop_listen(self):
        """Stop listening."""
        self._listening = False

        if self._mcastsocket is not None:
            _LOGGER.info('Closing multisocket')
            self._mcastsocket.close()
            self._mcastsocket = None

        for thread in self._threads:
            thread.join()

    def _listen_to_msg(self):
        while self._listening:
            if self._mcastsocket is None:
                continue
            data, (ip_add, _) = self._mcastsocket.recvfrom(1024)
            try:
                data = data.decode("utf-8")
                _LOGGER.info("receive data:%s", data)

            except Exception as e:
                _LOGGER.error('Cannot process multicast message: %s', data)
                _LOGGER.error(e)
                continue

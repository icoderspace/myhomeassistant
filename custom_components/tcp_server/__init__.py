import json
import logging
import socket
import voluptuous as vol
from threading import Thread

from homeassistant.const import CONF_PORT, EVENT_HOMEASSISTANT_STOP, CONF_HOST, CONF_IP_ADDRESS
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'tcp_server'

SERVICE_SEND = 'send'
ATTR_SEND_DATA = 'send_data'

TCP_SERVER_CONFIG = vol.Schema({
    vol.Optional(CONF_PORT, default=8001): cv.port
})

SERVICE_SEND_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(ATTR_SEND_DATA): cv.string
})


def setup(hass, config):
    """Set up the tcp server component."""
    if DOMAIN in config:
        tcp_server_config = config[DOMAIN]
        _LOGGER.info("tcp server config:%s", tcp_server_config)
    else:
        return
    port = tcp_server_config[CONF_PORT]
    tcp_server = TcpServer(port)

    def send_service(call):
        data = call.data.get(ATTR_SEND_DATA)
        ip = call.data.get(CONF_IP_ADDRESS)
        tcp_server.send(ip, data)

    hass.services.register(DOMAIN, SERVICE_SEND, send_service,
                           schema=SERVICE_SEND_SCHEMA)

    def stop_listen(event):
        _LOGGER.info("Shutting down tcp server")
        tcp_server.stop_listen()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_listen)
    tcp_server.start_listen()
    return True


class TcpServer:
    def __init__(self, port):
        self._port = port
        self._listening = False
        self._threads = []
        self._mcastsocket = None
        self._conns = {}

    def send(self, ip, data):
        if self._conns[ip] is None:
            _LOGGER.error("no ip[%s] in conns", ip)
            return
        _LOGGER.info("send to %s==>%s", ip, data)
        try:
            if not data.endswith('\n'):
                data += '\n'
            self._conns[ip].send(data.encode())
        except Exception as e:
            _LOGGER.error("send failed.%s", e)

    def start_listen(self):
        self._mcastsocket = socket.socket()  # 创建socket对象
        self._mcastsocket.bind(("0.0.0.0", self._port))  # 将地址与套接字绑定，且套接字要求是从未被绑定过的
        self._mcastsocket.listen(5)  # 代办事件中排队等待connect的最大数目
        self._listening = True
        thread = Thread(target=self._connect, args=())
        self._threads.append(thread)
        thread.daemon = True
        thread.start()

    def stop_listen(self):
        """Stop listening."""
        self._listening = False

        if self._mcastsocket is not None:
            _LOGGER.info('Closing multisocket')
            self._mcastsocket.close()
            self._mcastsocket = None
        for conn in self._conns.values():
            conn.close()
        for thread in self._threads:
            thread.join()

    def _connect(self):
        while self._listening:
            if self._mcastsocket is None:
                continue
            try:
                conn, address = self._mcastsocket.accept()
                _LOGGER.info('connected:%s', address)
                self._conns[address[0]] = conn
                thread = Thread(target=self._listen, args=(conn, address))
                self._threads.append(thread)
                thread.daemon = True
                thread.start()
            except Exception as e:
                _LOGGER.error('Cannot connect')
                _LOGGER.error(e)
                continue

    def _listen(self, conn, addr):
        _LOGGER.info('listen to :%s', addr)
        while self._listening:
            data = conn.recv(1024)
            try:
                data = data.decode("utf-8")
                _LOGGER.info("receive data=>%s:%s", addr, data)
            except Exception as e:
                _LOGGER.error('Cannot process message:addr:%s,data: %s', addr, data)
                _LOGGER.error(e)
                continue
        conn.close()

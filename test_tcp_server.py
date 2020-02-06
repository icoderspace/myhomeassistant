import logging
import time

from Tools.scripts.treesync import raw_input

from custom_components.tcp_server import TcpServer

logging.basicConfig(level=logging.DEBUG)
tcp_server = TcpServer(8001)
tcp_server.start_listen()
time.sleep(3)
tcp_server.send("192.168.31.188", "test")

name = raw_input('please enter your name: ')

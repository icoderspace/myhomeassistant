import logging

from Tools.scripts.treesync import raw_input

from custom_components.wireless_hub import WirelessHub

logging.basicConfig(level=logging.DEBUG)

#wireless_sender = WirelessHub("192.168.31.190", 1319, 7000, "iyk_008434ae")
wireless_sender = WirelessHub("192.168.31.107", 1319, 7000, "iyk_0065c772")
wireless_sender.listen()
# wireless_hub.send(
#     '{"msg_type":"set","msg_id":7,"device_id":"iyk_008434ae","services":{"rf":{"type":0,"value":"48a2a3db"}}}')
wireless_sender.learn_rf();
#wireless_sender.send_ir("g463g2284d3e4ec94d3e4ec94dc94dca4e3d4dca4ec94dc94d3e4dc94d3e4d3d4dca4d3d4dca4d3d4dca4a414dca4a4149424a414d3e4dc949424dc94d3e4dc94dc94dca4dh2d1g463g2284e3d4dca4e3d4dc94dca4dc94d3e4dc949cd4ec94d3d4acc4a414a4149cd4a4049cd494249cd49424acd49424a414a4149414acd49414acc4a414acc4acd49cd4ah2d4g463g2294d3e4ec949414acd49cd49ce4a4149ce4acd49cd4a4149cd494249414acd49414acc4a414acc4a4149ce4a4149424a414a4149cd4e3d49cd494249cd49ce4acd4")
name = raw_input('please enter your name: ')

import socket
from .. import config
from .. import logger
from .tracker import PeerTracker
from ..messages import Disconnect

def prompt_for_port():
    user_input = input('Select port for peer to run on: ')
    return int(user_input)

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as peer_socket:
        if config.USE_DEFAULT_PORT:
            port = config.DEFAULT_PORT
        else:
            port = prompt_for_port()

        peer_socket.bind(('0.0.0.0', port))
        tracker = PeerTracker(port, peer_socket)
        tracker.broadcast_message(Disconnect())
        while True:
            print(tracker.receive_message())
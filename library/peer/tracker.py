import json
import socket
from .. import config

class Peer:
    def __init__(self, ip: str, port: int, name: str):
        self.ip = ip
        self.port = port
        self.name = name
        self.socket = socket

    def encode(self):
        return {
            'ip': self.ip, 
            'port': self.port,
            'name': self.name
        }

    @staticmethod
    def decode(message):
        ip = message['data']['ip']
        port = message['data']['port']
        name = message['data']['name']

        return Peer(ip, port, name)

    def address(self):
        return (self.ip, self.port)

class PeerTracker(Peer):
    def __init__(self, port: int, peer_socket):
        super().__init__(self.get_ip(), port, None)
        self.socket = peer_socket
        self.peers = []

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send_message(self, message, peer):
        self.socket.sendto(message.encode(), peer.address())

    def broadcast_message(self, message):
        self.socket.sendto(message.encode(), ('<broadcast>', self.port))

    def receive_message(self):
        data, addr = self.socket.recvfrom(config.MAXIMUM_MESSAGE_LENGTH)

        for peer in self.peers:
            if peer.address() == addr:
                return json.loads(data), peer

        return json.loads(data), None

    @staticmethod
    def get_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
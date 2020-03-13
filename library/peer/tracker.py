import json
import socket
from .. import config
from .. import messages
from .. import logger
import select

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

    def address(self):
        return (self.ip, self.port)

    def __repr__(self):
        if self.name:
            return f'{self.name} ({self.ip}:{self.port})'
        else:
            return f'{self.ip}:{self.port}'

class PeerTracker(Peer):
    def __init__(self, port: int, peer_socket):
        super().__init__(self.get_ip(), port, None)
        self.socket = peer_socket
        self.peers = [self]
        self.old_name = ''

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send_message(self, message, peer):
        self.socket.sendto(message.encode(), peer.address())

    def broadcast_message(self, message):
        self.socket.sendto(message.encode(), ('<broadcast>', self.port))

        for peer in self.peers:
            if peer.port != self.port:
                self.socket.sendto(message.encode(), peer.address())

    def receive_message(self):
        data, addr = self.socket.recvfrom(config.MAXIMUM_MESSAGE_LENGTH)

        return json.loads(data), addr

    def discover_peer_names(self):
        logger.info(f'Starting discovery phase...')
        self.broadcast_message(messages.Discovery(self))
        logger.info(f'Discovering other peers in the subnet...')

        peer_names = []
        
        while True:
            read_list, _, __ = select.select([self.socket], [], [], config.DISCOVERY_TIME_LIMIT)

            if len(read_list):
                message, _ = self.receive_message()
                data = messages.MessageData(message)

                if data.mtp == 'DiscoveryResponse':
                    peer_names.append(data.name)
            else:
                # timeout, move to next phase
                return peer_names

    def handshake(self, name):
        self.name = name
        logger.info(f'Sending handshake messages with ip and port: {self.ip}:{self.port} using {self.name}')
        self.broadcast_message(messages.Handshake(self))
        logger.info(f'Waiting for response from other peers...')

    def get_peer(self, addr):
        for peer in self.peers:
            if peer.address() == addr:
                return peer
        return Peer(addr[0], addr[1], None)

    def get_peer_from_name(self, name):
        for peer in self.peers:
            if peer.name == name:
                return peer
        return None

    def add_peer(self, peer):
        self.peers.append(peer)

    def remove_peer(self, peer):
        if self is not peer:
            self.peers.remove(peer)
        else:
            logger.error('You cannot disconnect from yourself!')

    def disconnect_peer(self, name):
        if self.name != name:
            peer = self.get_peer_from_name(name)
            logger.info(f'Disconnected from {peer.name}')
            self.send_message(messages.Disconnect(), peer)
            self.peers.remove(peer)
        else:
            logger.error('You cannot disconnect from yourself!')

    def send_chat(self, message):
        self.broadcast_message(messages.SendChat(message))

    def online(self):
        return [peer.name for peer in self.peers]

    def whisper(self, name, message):
        peer = self.get_peer_from_name(name)
        self.send_message(messages.Whisper(message), peer)

    def quit(self):
        logger.info('Disconnecting from all peers...')
        self.broadcast_message(messages.Disconnect())

    def set_username(self, name):
        self.old_name = self.name
        self.name = name
        self.broadcast_message(messages.SetUsername(self.name))
        logger.info(f'New name: {self.name}')

    def reset_username(self):
        if self.old_name:
            self.name = self.old_name
            self.old_name = ''
            self.broadcast_message(messages.SetUsername(self.name))
        else:
            logger.error(f'Old name still produces an error. Disconnecting from all peers.')
            return True

    @staticmethod
    def get_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]

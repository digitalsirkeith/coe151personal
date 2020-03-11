import socket
import json
from .. import messages
from .. import config
from .. import logger

class Connection:
    def __init__(self, hostname, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((hostname, port))
        self.name = None

    def send_message(self, message):
        self.socket.send(message.encode())

    def receive_message(self):
        data = self.socket.recv(config.MAX_MESSAGE_LEN).decode()
        if data == '':
            return None
        else:
            return json.loads(data)

    def login(self, name):
        self.send_message(messages.Login(name))
        response = self.receive_message()

        if response['mtp'] != 'AssignUsername':
            logger.error(f'MTP Mismatch! Expected: AssignUsername. Got: {response["mtp"]}')
            return False
        else:
            self.name = response['data']['name']
            logger.info(f'Connected with name: {self.name}')
            return True
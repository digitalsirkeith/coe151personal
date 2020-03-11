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
        self.is_connected = True

    def send_message(self, message):
        self.socket.send(message.encode())

    def receive_message(self):
        data = self.socket.recv(config.MAX_MESSAGE_LEN).decode()
        if data == '':
            self.is_connected = False
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

    def send_chat(self, message):
        self.send_message(messages.SendChat(message))

    def terminate(self):
        if self.is_connected:
            self.send_message(messages.Disconnect())
            self.socket.close()
        else:
            self.socket.close()
        logger.info('Connection terminated.')

    def set_name(self, new_name):
        self.name = new_name
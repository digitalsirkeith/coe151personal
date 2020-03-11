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
            if response['status'] != 'OK':
                logger.error(f'Status: {response["status"]}. Disconnecting')
                return False
            else:
                self.name = response['data']['name']
                logger.info(f'Connected with name: {self.name}')
                return True

    def terminate(self):
        if self.is_connected:
            self.send_message(messages.Disconnect())
        logger.info('Connection terminated.')

    def set_name(self, new_name):
        self.name = new_name

    def encode_message(self, user_input):
        tokens = user_input.split()

        if not tokens:
            return None

        if tokens[0][0] != '/':
            return messages.SendChat(user_input)
        elif tokens[0] in ['/changename', '/setusername', '/su']:
            return messages.SetUsername(tokens[1])
        elif tokens[0] in ['/request_user_info', '/who', '/rui']:
            return messages.RequestUserInfo(tokens[1])
        elif tokens[0] in ['/request_local_time', '/time']:
            return messages.RequestLocalTime()
        elif tokens[0] in ['/whisper_to_user', '/msg', '/w']:
            return messages.WhisperToUser(self.name, [tokens[1]], ' '.join(tokens[2:]))
        elif tokens[0] in ['/request_online_list', '/online', '/list']:
            return messages.RequestOnlineList()
        elif tokens[0] in ['/quit', '/exit', '/disconnect']:
            return messages.Disconnect()
        elif tokens[0] in ['/kick', '/kick_user']:
            return messages.KickUser(tokens[1])
        elif tokens[0] in ['/mute', '/mute_user']:
            return messages.MuteUser(tokens[1])
        elif tokens[0] in ['/unmute', '/unmute_user']:
            return messages.UnmuteUser(tokens[1])
        elif tokens[0] in ['/op', '/setadmin']:
            return messages.UnmuteUser(tokens[1])
        else:
            logger.error('Unknown command!')
            return None
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

    def read_json_object(self):
        open_brackets = 1
        data = self.socket.recv(1).decode()

        if not data:
            return ''

        while open_brackets:
            data += self.socket.recv(1).decode()
            if data[-1] == '{':
                open_brackets += 1
            elif data[-1] == '}':
                open_brackets -= 1

        return data

    def receive_message(self):
        data = self.read_json_object()
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
            if response['status'] != 'OK':
                logger.error(f'Status: {response["status"]}. Disconnecting')
                return False
            else:
                self.name = response['data']['name']
                logger.info(f'Connected with name: {self.name}')
                return True

    def terminate(self):
        self.socket.close()
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
            if len(tokens) == 2:
                return messages.SetUsername(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')
                return None

        elif tokens[0] in ['/request_user_info', '/who', '/rui']:
            if len(tokens) == 2:
                return messages.RequestUserInfo(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')
                return None

        elif tokens[0] in ['/request_local_time', '/time']:
            return messages.RequestLocalTime()

        elif tokens[0] in ['/whisper_to_user', '/msg', '/w']:
            if len(tokens) >= 3:
                return messages.WhisperToUser(self.name, [tokens[1]], ' '.join(tokens[2:]))
            else:
                logger.error(f'Usage: {tokens[0]} <username> <message>')
                return None
            
        elif tokens[0] in ['/request_online_list', '/online', '/list']:
            return messages.RequestOnlineList()

        elif tokens[0] in ['/quit', '/exit', '/disconnect']:
            return messages.Disconnect()

        elif tokens[0] in ['/kick', '/kick_user']:
            if len(tokens) == 2:
                return messages.KickUser(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')
                return None

        elif tokens[0] in ['/mute', '/mute_user']:
            if len(tokens) == 2:
                return messages.MuteUser(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')
                return None
            

        elif tokens[0] in ['/unmute', '/unmute_user']:
            if len(tokens) == 2:
                return messages.UnmuteUser(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')
                return None
            

        elif tokens[0] in ['/op', '/setadmin']:
            if len(tokens) == 2:
                return messages.SetAsAdmin(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')
                return None
            
        else:
            logger.error('Unknown command!')
            return None
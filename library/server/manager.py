from .. import messages
from .. import logger
from .. import config
import sys
import time
import select
from .user import User

class Manager:
    def __init__(self, server_socket):
        self.users = []
        self.is_running = True
        self.admin = None
        self.muted_list = []
        self.server_socket = server_socket

    def wait(self):
        read_list, _, __ = select.select(self.users + [sys.stdin, self.server_socket], [], [])
        return read_list

    def add_user(self, user: User):
        if self.admin is None:
            self.admin = user
        self.users.append(user)
        self.announce(f'{user.name} joined the server.')

    def answer_client(self, client: User):
        # Controller function
        message = client.receive_message()

        if message is None:
            self.disconnect_client(client)

        elif message['mtp'] == 'SendChat':
            if client not in self.muted_list:
                self.send_chat_from_user(client, message['data']['message'])
            else:
                client.send_message(messages.ServerMessage('You are muted.'))

        elif message['mtp'] == 'Disconnect':
            self.disconnect_client(client)

        elif message['mtp'] == 'SetUsername':
            self.set_username(client, message['data']['name'])

        elif message['mtp'] == 'RequestUserInfo':
            found_user = False
            for user in self.users:
                if user.name == message['data']['name']:
                    client.send_message(messages.ProvideUserInfo(user))
                    found_user = True
            if not found_user:
                client.send_message(messages.ProvideUserInfo(None, status='UserDoesNotExist'))

        elif message['mtp'] == 'RequestLocalTime':
            client.send_message(messages.SendLocalTime())

        elif message['mtp'] == 'WhisperToUser':
            if client not in self.muted_list:
                for user in self.users:
                    if user.name in message['data']['to']:
                        user.send_message(messages.WhisperFromUser(client.name, message['data']['message']))
            else:
                client.send_message(messages.ServerMessage('You are muted.'))

        elif message['mtp'] == 'RequestOnlineList':
            client.send_message(messages.SendOnlineList([user.name for user in self.users]))

        elif message['mtp'] == 'KickUser':
            if client is self.admin:
                found_user = False
                for user in self.users:
                    if user.name in message['data']['name']:
                        client.send_message(messages.KickUser(status='OK'))
                        self.disconnect_client(user, 'Kicked from the server.')
                        self.announce(f'{user.name} has been kicked from the server.')
                        found_user = True
                        
                if not found_user:
                    client.send_message(messages.KickUser(status='UserDoesNotExist'))
            else:
                client.send_message(messages.KickUser(status='NotAdminError'))

        elif message['mtp'] == 'MuteUser':
            if client is self.admin:
                found_user = False
                for user in self.users:
                    if user.name in message['data']['name']:
                        if user not in self.muted_list:
                            self.muted_list.append(user)
                            self.announce(f'{user.name} has been muted.')
                            client.send_message(messages.MuteUser(status='OK'))
                        else:
                            client.send_message(messages.MuteUser(status="UserAlreadyMuted"))
                        found_user = True
                        
                if not found_user:
                    client.send_message(messages.MuteUser(status='UserDoesNotExist'))
            else:
                client.send_message(messages.MuteUser(status='NotAdminError'))

        elif message['mtp'] == 'UnmuteUser':
            if client is self.admin:
                found_user = False
                for user in self.users:
                    if user.name in message['data']['name']:
                        if user in self.muted_list:
                            self.muted_list.remove(user)
                            self.announce(f'{user.name} has been unmuted.')
                            client.send_message(messages.UnmuteUser(status='OK'))
                        else:
                            # what if hindi pala siya muted in the first place.
                            client.send_message(messages.MuteUser(status="UserNotMuted"))
                        found_user = True
                        
                if not found_user:
                    client.send_message(messages.UnmuteUser(status='UserDoesNotExist'))
            else:
                client.send_message(messages.UnmuteUser(status='NotAdminError'))

        elif message['mtp'] == 'SetAsAdmin':
            if client is self.admin:
                found_user = False
                for user in self.users:
                    if user.name in message['data']['name']:
                        if user is client:
                            client.send_message(messages.SetAsAdmin(status='AlreadyAdmin'))
                        else:
                            self.admin = user
                            self.announce(f'{user.name} is now the admin.')
                            client.send_message(messages.SetAsAdmin(status='OK'))
                        found_user = True
                        
                if not found_user:
                    client.send_message(messages.SetAsAdmin(status='UserDoesNotExist'))
            else:
                client.send_message(messages.SetAsAdmin(status='NotAdminError'))

        else:
            logger.error('Unsupported message type received!')

    def send_chat_from_user(self, from_user, message):
        for to_user in self.users:
            if from_user is not to_user:
                to_user.send_message(messages.SendChatFromUser(from_user.name, message))
        logger.chat(f'{from_user.name}: {message}')

    def disconnect_client(self, outgoing_client: User, reason=''):
        if outgoing_client is self.admin:
            found_user = False
            for user in self.users:
                if user is not outgoing_client:
                    self.admin = user
                    found_user = True
                    break
            if found_user:
                self.announce(f'{self.admin.name} is now the admin.')
            else:
                self.admin = None

        if outgoing_client in self.muted_list:
            self.muted_list.remove(outgoing_client)

        if outgoing_client.is_connected:
            outgoing_client.send_message(messages.Disconnect(reason))
            logger.debug(f'Disconnected {outgoing_client}')
        else:
            logger.warning(f'Client ({outgoing_client}) disconnected unexpectedly.')

        self.users.remove(outgoing_client)
        if not reason:
            self.announce(f'{outgoing_client.name} left the server.')

        outgoing_client.close()

    def announce(self, server_message):
        for user in self.users:
            user.send_message(messages.ServerMessage(server_message))
        logger.info(server_message)

    def handshake(self, client: User):
        request = client.receive_message()

        if request['mtp'] != 'Login':
            logger.error(f'MTP Mismatch! Expected: Login. Got: {request["mtp"]}')
            return False
        else:
            requested_name = request['data']['name']

            if self.check_name(requested_name):
                logger.error(f'Client requested name already exists! Disconnecting.')
                client.send_message(messages.AssignUsername(requested_name, status='DuplicateError'))
                return False

            else:
                client.send_message(messages.AssignUsername(requested_name))
                client.set_name(requested_name)
                return True

    def set_username(self, user, new_name):
        if self.check_name(new_name):
            logger.error(f'Requested name already exists!')
            user.send_message(messages.SetUsername(user.name, 'DuplicateError'))

        else:
            self.announce(f'{user.name} has changed username to {new_name}.')
            user.name = new_name
            user.send_message(messages.SetUsername(user.name))


    def shutdown(self):
        logger.info('Disconnecting all clients.')
        for user in self.users:
            self.disconnect_client(user, "Server is shutting down.")
        logger.info('Disconnected all clients. Server now shutting down.')
        self.is_running = False

    def check_name(self, name):
        for user in self.users:
            if name == user.name:
                return True
        return False

    def purge_clients(self):
        # Supposedly kick all clients that have not responded to a keepAlive packet
        pass
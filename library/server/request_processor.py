from .. import messages
from .. import logger
from .. import config
import sys
import time
from .connected_client import ConnectedClient

class RequestProcessor:
    def __init__(self):
        self.connected_clients = []
        self.sockets = [sys.stdin]
        self.is_running = True
        self.admin = None
        self.muted_list = []
        
    def get_connected_clients(self):
        return self.connected_clients

    def add_client(self, new_client: ConnectedClient):
        if self.admin is None:
            self.admin = new_client
        self.sockets.append(new_client.socket)
        self.connected_clients.append(new_client)

    def answer_client(self, client: ConnectedClient):
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
            for user in self.connected_clients:
                if user.name == message['data']['name']:
                    client.send_message(messages.ProvideUserInfo(user))
                    found_user = True
            if not found_user:
                client.send_message(messages.ProvideUserInfo(None, status='UserDoesNotExist'))

        elif message['mtp'] == 'RequestLocalTime':
            client.send_message(messages.SendLocalTime())

        elif message['mtp'] == 'WhisperToUser':
            if client not in self.muted_list:
                for user in self.connected_clients:
                    if user.name in message['data']['to']:
                        user.send_message(messages.WhisperFromUser(client.name, message['data']['message']))
            else:
                client.send_message(messages.ServerMessage('You are muted.'))

        elif message['mtp'] == 'RequestOnlineList':
            client.send_message(messages.SendOnlineList([user.name for user in self.connected_clients]))

        elif message['mtp'] == 'KickUser':
            if client is self.admin:
                found_user = False
                for user in self.connected_clients:
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
                for user in self.connected_clients:
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
                for user in self.connected_clients:
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
                for user in self.connected_clients:
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

    def send_chat_from_user(self, user, message):
        for client in self.connected_clients:
            if client is not user:
                client.send_message(messages.SendChatFromUser(user.name, message))
        logger.chat(f'{user.name}: {message}')

    def disconnect_client(self, outgoing_client: ConnectedClient, reason=''):
        if outgoing_client is self.admin:
            found_user = False
            for user in self.connected_clients:
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

        self.connected_clients.remove(outgoing_client)
        self.sockets.remove(outgoing_client.socket)
        if not reason:
            self.announce(f'{outgoing_client.name} left the server.')

        outgoing_client.close()

    def announce(self, server_message):
        for client in self.connected_clients:
            client.send_message(messages.ServerMessage(server_message))
        logger.info(server_message)

    def handshake(self, client: ConnectedClient):
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

    def set_username(self, client, new_name):
        if self.check_name(new_name):
            logger.error(f'Requested name already exists!')
            client.send_message(messages.SetUsername(client.name, 'DuplicateError'))

        else:
            self.announce(f'{client.name} has changed username to {new_name}.')
            client.name = new_name
            client.send_message(messages.SetUsername(client.name))


    def shutdown(self):
        logger.info('Disconnecting all clients.')
        for client in self.connected_clients:
            self.disconnect_client(client, "Server is shutting down.")
        logger.info('Disconnected all clients. Server now shutting down.')
        self.is_running = False

    def check_name(self, name):
        for client in self.connected_clients:
            if name == client.name:
                return True
        return False


    def purge_clients(self):
        # Supposedly kick all clients that have not responded to a keepAlive packet
        pass
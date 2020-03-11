from .. import messages
from .. import logger
import sys
from .connected_client import ConnectedClient

class RequestProcessor:
    def __init__(self):
        self.connected_clients = []
        self.sockets = [sys.stdin]
        
    def get_connected_clients(self):
        return self.connected_clients

    def add_client(self, new_client: ConnectedClient):
        self.sockets.append(new_client.socket)
        self.connected_clients.append(new_client)

    def answer_client(self, client: ConnectedClient):
        # for connected_client in self.connected_clients:
        #     if client is connected_client:
        message = client.receive_message()

        if message is None:
            self.disconnect_client(client)

        elif message['mtp'] == 'SendChat':
            self.send_chat_from_user(client, message['data']['message'])

        elif message['mtp'] == 'Disconnect':
            client.is_connected = True
            self.disconnect_client(client)

        elif message['mtp'] == 'SetUsername':
            pass

        else:
            logger.error('Unsupported message type received!')

    def send_chat_from_user(self, user, message):
        for client in self.connected_clients:
            if client is not user:
                client.send_message(messages.SendChatFromUser(user.name, message))
        logger.chat(f'{user.name}: {message}')

    def disconnect_client(self, outgoing_client: ConnectedClient):
        if outgoing_client.is_connected:
            logger.debug(f'Disconnected {outgoing_client}')
        else:
            logger.warning(f'Client ({outgoing_client}) disconnected unexpectedly.')

        self.connected_clients.remove(outgoing_client)
        self.sockets.remove(outgoing_client.socket)
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
                client.send_message(messages.AssignUsername(requested_name, status="DuplicateError"))
                return False

            else:
                client.send_message(messages.AssignUsername(requested_name))
                client.set_name(requested_name)
                return True

    def shutdown(self):
        logger.info('Disconnecting all clients.')
        for client in self.connected_clients:
            self.disconnect_client(client)
        logger.info('Disconnected all clients. Server now shutting down.')

    def check_name(self, name):
        for client in self.connected_clients:
            if name == client.name:
                return True
        return False


    def purge_clients(self):
        # Supposedly kick all clients that have not responded to a keepAlive packet
        pass
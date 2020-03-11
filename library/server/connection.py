from .. import messages
from .. import config
from .. import logger
import json

class ConnectedClient:
    def __init__(self, conn, addr):
        self.socket = conn
        self.addr = addr
        self.name = ''
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

    def set_name(self, name):
        self.name = name

    def __repr__(self):
        return f'{self.addr[0]}:{self.addr[1]}'

class RequestProcessor:
    def __init__(self):
        self.connected_clients = []
        
    def get_connected_clients(self):
        return self.connected_clients

    def add_client(self, connected_client: ConnectedClient):
        self.connected_clients.append(connected_client)

    def answer_client(self, client: ConnectedClient):
        for connected_client in self.connected_clients:
            if client is connected_client:
                message = client.receive_message()
                if message is None:
                    logger.warning(f'Client ({client}) disconnected unexpectedly.')
                    self.disconnect_client(client)

    def disconnect_client(self, outgoing_client: ConnectedClient):
        if outgoing_client.is_connected:
            outgoing_client.send_message()
            pass
        else:
            self.connected_clients.remove(outgoing_client)
            self.announce(f'{outgoing_client.name} left the server.')

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
            for connected_client in self.connected_clients:
                if requested_name == connected_client.name:
                    logger.error(f'Client requested name already exists! Disconnecting.')
                    client.send_message(messages.AssignUsername(requested_name, status="DuplicateError"))
                    return False

            client.send_message(messages.AssignUsername(requested_name))
            client.set_name(requested_name)
            
            return True

    def purge_clients(self):
        pass
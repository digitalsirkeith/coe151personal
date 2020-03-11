from .. import message

class ConnectedClient:
    def __init__(self, conn, addr):
        self.socket = conn
        self.addr = addr

    def handshake(self):
        # self.socket.send()
        return True

    def __repr__(self):
        return str(self.addr)

class RequestProcessor:
    def __init__(self):
        self.connected_clients = []
        
    def get_connected_clients(self):
        return self.connected_clients

    def add_client(self, connected_client: ConnectedClient):
        self.connected_clients.append(connected_client)

    def answer_client(self, client):
        for connected_client in self.connected_clients:
            if client is connected_client:
                pass

    def purge_clients(self):
        pass
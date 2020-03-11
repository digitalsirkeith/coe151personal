from .. import config
import json

class ConnectedClient:
    def __init__(self, conn, addr):
        self.socket = conn
        self.addr = addr
        self.ip_addr = addr[0]
        self.port = addr[1]
        self.name = ''
        self.is_connected = True

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
            self.is_connected = False
            return None
        else:
            return json.loads(data)

    def set_name(self, name):
        self.name = name

    def __repr__(self):
        return f'{self.addr[0]}:{self.addr[1]}'

    def close(self):
        self.socket.close()
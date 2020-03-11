import socket
import select
import sys
from .. import config
from .. import logger
from .connected_client import ConnectedClient
from .request_processor import RequestProcessor

def prompt_for_port():
    user_input = input('Select port for server to run on: ')
    return int(user_input)

def run():
    request_processor = RequestProcessor()
    sockets = [sys.stdin]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        if config.USE_DEFAULT_PORT:
            port = config.DEFAULT_PORT
        else:
            port = prompt_for_port()
            
        server_socket.bind(('', port))
        logger.info(f'Now listening as: {socket.gethostname()}:{port}')
        
        server_socket.listen(config.MAXIMUM_CONNECTIONS)
        sockets.append(server_socket)

        while True:
            read_list, _, __ = select.select(sockets, [], [])

            for fd in read_list:
                if fd == server_socket:
                    logger.debug('Incoming new connection.')
                    conn, addr = server_socket.accept()
                    logger.debug(f'New connection from: {addr[0]}:{addr[1]}.')
                    new_client = ConnectedClient(conn, addr)

                    if request_processor.handshake(new_client) is True:
                        sockets.append(new_client.socket)
                        request_processor.add_client(new_client)
                        logger.info(f'Handshake successful with {new_client}')
                        request_processor.announce(f'{new_client.name} joined the server.')

                elif fd == sys.stdin:
                    # User entered a server command.
                    user_input = input()
                    if user_input == 'exit':
                        request_processor.shutdown()
                        return
                else:
                    # Someone sent something, find who did it and process it accordingly
                    for client in request_processor.get_connected_clients():
                        if fd == client.socket:
                            request_processor.answer_client(client)


if __name__ == '__main__':
    run()
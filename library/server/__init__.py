import socket
import select
from .. import config
from .. import logger
from .connection import ConnectedClient, RequestProcessor

def prompt_for_port():
    print('Select port for server to run on: ', end='')
    user_input = input()
    return int(user_input)

def run():
    request_processor = RequestProcessor()
    sockets = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        if config.USE_DEFAULT_PORT:
            server_socket.bind(('', config.DEFAULT_PORT))
        else:
            port = prompt_for_port()
            server_socket.bind(('', port))
        
        server_socket.listen(config.MAXIMUM_CONNECTIONS)
        sockets.append(server_socket)

        while True:
            read_list, _, __ = select.select(sockets, [], [])

            for sock in read_list:
                if sock == server_socket:
                    logger.debug('Incoming new connection.')
                    conn, addr = server_socket.accept()
                    logger.debug(f'New connection from: {addr}.')
                    new_client = ConnectedClient(conn, addr)

                    if new_client.handshake() is True:
                        sockets.append(new_client.socket)
                        request_processor.add_client(new_client)
                        logger.info(f'Handshake successful with {new_client}')
                else:
                    # Someone sent something, find who did it and process it accordingly
                    for client in request_processor.get_connected_clients():
                        if sock == client.socket:
                            request_processor.answer_client(client)


if __name__ == '__main__':
    run()
import socket
import sys
from .. import config
from .. import logger
from .user import User
from .manager import Manager

def prompt_for_port():
    user_input = input('Select port for server to run on: ')
    return int(user_input)

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        if config.USE_DEFAULT_PORT:
            port = config.DEFAULT_PORT
        else:
            port = prompt_for_port()
            
        server_socket.bind(('', port))
        server_socket.listen(config.MAXIMUM_CONNECTIONS)
        logger.info(f'Now listening as: {server_socket.getsockname()[0]}:{port}')

        manager = Manager(server_socket)
        while manager.is_running:
            read_list = manager.wait()

            for readable in read_list:
                if server_socket is readable:
                    logger.debug('Incoming new connection.')
                    conn, addr = server_socket.accept()
                    logger.debug(f'New connection from: {addr[0]}:{addr[1]}.')
                    new_user = User(conn, addr)

                    if manager.handshake(new_user) is True:
                        manager.add_user(new_user)
                        logger.info(f'Handshake successful with {new_user}')

                elif sys.stdin is readable:
                    # User entered a server command.
                    user_input = input()
                    if user_input in ['exit', '/exit']:
                        manager.shutdown()
                        server_socket.close()
                else:
                    # Someone sent something, find who did it and process it accordingly
                    logger.debug(f'Reading from {readable}')
                    manager.answer_client(readable)

if __name__ == '__main__':
    run()
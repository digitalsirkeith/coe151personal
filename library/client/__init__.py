from .. import config
from .. import logger
from .connection import Connection
import socket
import select
import sys

def run():
    hostname, port = prompt_for_hostname()
    name = prompt_for_username()

    connection = Connection(hostname, port)
    connection.login(name)

    while True:
        read_list, _, __ = select.select([connection.socket, sys.stdin], [], [])

        for fd in read_list:
            if fd is sys.stdin:
                # User entered something
                user_input = input()
                connection.send_chat(user_input)
                print('KOLD')
            else:
                # server sent something
                message = connection.receive_message()

                if message is None:
                    connection.terminate()

                elif message['mtp'] == 'ServerMessage':
                    print(message['data']['message'])

                elif message['mtp'] == 'SendChatFromUser':
                    print(f'{message["data"]["name"]}: {message["data"]["message"]}')

                elif message['mtp'] == 'AssignUsername':
                    connection.set_name(message['mtp']['name'])
                    print(f'Your new name is: {connection.name}')

                else:
                    logger.error('Unsupported message type received!')

def prompt_for_hostname():
    hostname = input('Enter IP address of server: ')
    if config.USE_DEFAULT_PORT:
        port = config.DEFAULT_PORT
    else:
        port = int(input('Enter port of server: '))
    return (hostname, port)

def prompt_for_username():
    return input('Enter your name: ')

if __name__ == '__main__':
    run()

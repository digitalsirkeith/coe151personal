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
    if connection.login(name) == False:
        return

    while True:
        read_list, _, __ = select.select([connection.socket, sys.stdin], [], [])

        for fd in read_list:
            if fd is sys.stdin:
                user_input = input()
                message = connection.encode_message(user_input)
                if message:
                    connection.send_message(message)

            else:
                # server sent something
                message = connection.receive_message()

                if message is None:
                    connection.terminate()
                    return

                elif message['mtp'] == 'ServerMessage':
                    print(message['data']['message'])

                elif message['mtp'] == 'SendChatFromUser':
                    name = message['data']['name']
                    user_message = message['data']['message']
                    print(f'{name}: {user_message}')

                elif message['mtp'] == 'SetUsername' or message['mtp'] == 'AssignUsername':
                    status = message['status']
                    if status == 'OK':
                        connection.set_name(message['data']['name'])
                        print(f'Your new name is: {connection.name}')
                    else:
                        print(f'Failed to change name: {status}')

                elif message['mtp'] == 'Disconnect':
                    reason = message['data']['message']
                    print(f'Disconnected. {reason}')
                    connection.terminate()
                    return
                
                elif message['mtp'] == 'ProvideUserInfo':
                    name = message['data']['name']
                    ip = message['data']['ip']
                    port = message['data']['port']
                    print(f'{name} is {ip}:{port}')

                elif message['mtp'] == 'SendLocalTime':
                    local_time = message['data']['time']
                    print(f'Server local time: {local_time}')

                elif message['mtp'] == 'WhisperFromUser':
                    name = message['data']['name']
                    user_message = message['data']['message']
                    print(f'[{name} -> me]: {user_message}')

                elif message['mtp'] == 'SendOnlineList':
                    names = message['data']['names']
                    print(f'Online Users:', ', '.join(names))

                elif message['mtp'] == 'KickUser':
                    status = message['status']
                    if status == 'OK':
                        print('Kicked user')
                    else:
                        print(f'Failed to kick user: {status}')

                elif message['mtp'] == 'MuteUser':
                    status = message['status']
                    if status == 'OK':
                        print('Muted user')
                    else:
                        print(f'Failed to mute user: {status}')

                elif message['mtp'] == 'UnmuteUser':
                    status = message['status']
                    if status == 'OK':
                        print('Unmuted user')
                    else:
                        print(f'Failed to unmute user: {status}')

                elif message['mtp'] == 'SetAsAdmin':
                    status = message['status']
                    if status == 'OK':
                        print('Set user as admin')
                    else:
                        print(f'Failed to set user as admin: {status}')

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

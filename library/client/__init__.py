from .. import config
from .. import logger
from .connection import Connection
from .handler import Handler
from . import terminal
from . import gui
import socket
import select
import sys

def run():
    hostname, port = prompt_for_hostname()
    name = prompt_for_username()

    connection = Connection(hostname, port)
    handler = Handler()

    if config.CLIENT_MODE == 'terminal':
        handler.set_caller(terminal)
    else:
        handler.set_caller(gui)

    if connection.login(name) == False:
        return

    while True:
        read_list, _, __ = select.select([connection.socket, sys.stdin], [], [])

        for readable in read_list:
            if sys.stdin is readable:
                user_input = input()
                message = connection.encode_message(user_input)
                if message:
                    connection.send_message(message)

            elif connection.socket is readable:
                # server sent something
                message = connection.receive_message()
                if handler.handle_message(message, connection):
                    return

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

from .. import config
from .connection import Connection
import socket

def prompt_for_hostname():
    print('Enter IP address of server: ', end='')
    hostname = input()
    if config.USE_DEFAULT_PORT:
        port = config.DEFAULT_PORT
    else:
        port = int(input())
    return (hostname, port)

def prompt_for_username():
    print('Enter your name: ', end='')
    return input()

def run():
    hostname, port = prompt_for_hostname()
    name = prompt_for_username()

    connection = Connection(hostname, port)
    connection.login(name)

if __name__ == '__main__':
    run()
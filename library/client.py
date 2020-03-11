from . import config
import socket

def prompt_for_hostname():
    print('Enter IP address of server: ')
    hostname = input()
    if config.USE_DEFAULT_PORT:
        port = config.DEFAULT_PORT
    else:
        port = int(input())
    return (hostname, port)

def run():
    hostname, port = prompt_for_hostname()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((hostname, port))
        pass

if __name__ == '__main__':
    run()
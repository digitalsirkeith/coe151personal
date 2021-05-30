import socket
import select
import sys
from .. import config
from .. import logger
from . import terminal, gui
from .handler import Handler
from .tracker import PeerTracker
from ..messages import Disconnect

def prompt_for_port():
    user_input = input('Select port for peer to run on: ')
    return int(user_input)

def prompt_for_name():
    return input('Enter username: ')

def prompts_for_messages(handler, tracker):
    while True:
        user_input = input('')
        if handler.handle_input(user_input, tracker):
            return

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as peer_socket:
        if config.USE_DEFAULT_PORT:
            port = config.DEFAULT_PORT
        else:
            port = prompt_for_port()

        peer_socket.bind(('0.0.0.0', port))

        handler = Handler()
        if config.CLIENT_MODE == 'terminal':
            handler.set_caller(terminal)
        else:
            handler.set_caller(gui)

        tracker = PeerTracker(port, peer_socket)
        names = tracker.discover_peer_names()
        if names:
            print('The names currently online in the network are:', ', '.join(names))
        else:
            print('Nobody responded. Assuming nobody is online.')
        
        while True:
            user_name = prompt_for_name()
            if user_name not in names:
                break
            else:
                print(f'That username already exists!')

        tracker.handshake(user_name)
        if config.OS == 'UNIX':
            while True:
                read_list, _, __ = select.select([sys.stdin, peer_socket], [], [])

                for readable in read_list:
                    if sys.stdin is readable:
                        user_input = input('')
                        if handler.handle_input(user_input, tracker):
                            return
                    elif peer_socket is readable:
                        message, addr = tracker.receive_message()
                        if handler.handle_message(message, tracker, addr):
                            return
        else:
            from threading import Thread
            input_thread = Thread(target=prompts_for_messages, args=(handler, tracker))
            input_thread.start()
            while True:
                message, addr = tracker.receive_message()
                if handler.handle_message(message, tracker, addr):
                    input_thread.join()
                    return
                if input_thread.is_alive() is not True:
                    return

#!/usr/bin/env python

from library import server, client, peer

if __name__ == '__main__':
    while True:
        print('What mode would you like to run as?')
        print('[1] Server')
        print('[2] Client')
        print('[3] Peer')
        user_answer = input('> ')

        if user_answer == '1':
            server.run()
            break
        elif user_answer == '2':
            client.run()
            break
        elif user_answer == '3':
            peer.run()
            break
        else:
            print('Invalid input!')
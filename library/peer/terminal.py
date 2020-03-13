from .. import messages
from .. import logger
from .tracker import Peer

def onDiscovery(data, peer, tracker):
    tracker.send_message(messages.DiscoveryResponse(tracker), peer)

def onHandshake(data, peer, tracker):
    if peer.name:
        logger.warning(f'{peer} sent another Handshake message without disconnecting first.')
    else:
        logger.info(f'Handshake message received from {peer} with name {data.name}.')

    if data.name in tracker.online():
        logger.warning(f'Name already exists in the list. Sending a DuplicateError back.')
        tracker.send_message(messages.HandshakeResponse(tracker, status='DuplicateError'), peer)
    else:
        peer.name = data.name
        tracker.send_message(messages.HandshakeResponse(tracker), peer)
        tracker.add_peer(peer)

def onHandshakeResponse(data, peer, tracker):
    if data.status == 'OK':
        if peer.name:
            logger.warning(f'{peer} sent a HandshakeResponse message more than once.')
        else:
            logger.info(f'HandshakeResponse message received from {peer} with name {data.name}.')

        peer.name = data.name
        tracker.add_peer(peer)
    else:
        logger.error(f'Error from a HandshakeResponse message: {data.status}')
        if data.status == 'DuplicateError':
            logger.info(f'Please change usernames if you wish to connect.')

def onDisconnect(data, peer, tracker):
    if peer.name:
        logger.debug(f'{peer} sent a Disconnect message. Removing from list of online peers')
        print(f'{peer.name} disconnected.')
        tracker.remove_peer(peer)
    else:
        logger.warning(f'Received Disconnect message from an unkown peer.')

def onSendChat(data, peer, tracker):
    if peer in tracker.peers:
        print(f'{peer.name}: {data.message}')
    else:
        logger.warning(f'Received SendChat message from an unknown peer. Message: {data.message}')

def onWhisper(data, peer, tracker):
    if peer in tracker.peers:
        print(f'[{peer.name} -> me] {data.message}')
    else:
        logger.warning(f'Received SendChat message from an unknown peer: {data.message}')

def onSetUsername(data, peer, tracker):
    if peer in tracker.peers:
        if peer.name != data.name:
            if data.name not in tracker.online():
                tracker.send_message(messages.SetUsernameResponse(data.name), peer)
                print(f'{peer.name} changed username to {data.name}')
                peer.name = data.name
            else:
                logger.warning(f'Name already exists in the list. Sending a DuplicateError back.')
                tracker.send_message(messages.SetUsernameResponse(data.name, 'DuplicateError'), peer)
        else:
            logger.info(f'{peer} resetted username. No change involved.')
    else:
        logger.warning(f'Received SetUsername message from an unknown peer.')

def onSetUsernameResponse(data, peer, tracker):
    if peer in tracker.peers:
        if data.status != 'OK':
            if tracker.name == data.name:
                logger.error(f'SetUsernameResponse error: {data.status}. Resetting name back to old username.')
                return tracker.reset_username()
            else:
                logger.warning(f'SetUsernameResponse error: {data.status}. This is for a previously attempted name: {data.name}')
        else:
            logger.info(f'{peer} has accepted the new name.')
    else:
        logger.warning(f'Received SetUsernameResponse message from an unknown peer.')

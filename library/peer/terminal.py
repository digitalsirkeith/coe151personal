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

    if data.name in [peer.name for peer in tracker.peers]:
        tracker.send_message(messages.HandshakeResponse(tracker, status='DuplicateError'), peer)
    else:
        peer.name = data.name
        tracker.send_message(messages.HandshakeResponse(tracker), peer)
        tracker.add_peer(peer)

def onHandshakeResponse(data, peer, tracker):
    if peer.name:
        logger.warning(f'{peer} sent a HandshakeResponse message more than once.')
    else:
        logger.info(f'HandshakeResponse message received from {peer} with name {data.name}.')

    peer.name = data.name
    tracker.add_peer(peer)

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
        logger.warning(f'Received SendChat message from an unknown peer. MessageL {data.message}')

def onWhisper(data, peer, tracker):
    if peer in tracker:
        print(f'[{peer.name} -> me] {data.message}')
    else:
        logger.warning(f'Received SendChat message from an unknown peer: {data.message}')

from .. import logger
from .. import messages
from .tracker import Peer

class Handler:
    def __init__(self):
        self.func = dict()

    def on(self, event: str, event_func: callable):
        self.func[event] = event_func

    def handle_message(self, message, tracker, addr):
        data = messages.MessageData(message)
        if data.ip is not None and data.port is not None:
            peer = tracker.get_peer((data.ip, data.port))
        else:
            peer = tracker.get_peer(addr)
        
        if peer.ip == tracker.ip and peer.port == tracker.port:
            return
            
        if data.mtp not in self.func:
            logger.error(f'Unsupported message type received! {data.mtp}')
        else:
            return self.func[data.mtp](data, peer, tracker)

    def set_caller(self, caller):
        self.on('Discovery', caller.onDiscovery)
        self.on('Handshake', caller.onHandshake)
        self.on('HandshakeResponse', caller.onHandshakeResponse)
        self.on('Disconnect', caller.onDisconnect)
        self.on('SendChat', caller.onSendChat)
        self.on('Whipser', caller.onWhisper)

        # self.on('Terminate', caller.onTerminate)
        # self.on('ServerMessage', caller.onServerMessage)
        # self.on('SendChatFromUser', caller.onSendChatFromUser)
        # self.on('SetUsername', caller.onSetUsername)
        # self.on('Disconnect', caller.onDisconnect)
        # self.on('ProvideUserInfo', caller.onProvideUserInfo)
        # self.on('SendLocalTime', caller.onSendLocalTime)
        # self.on('WhisperFromUser', caller.onWhisperFromUser)
        # self.on('SendOnlineList', caller.onSendOnlineList)
        # self.on('KickUser', caller.onKickUser)
        # self.on('MuteUser', caller.onMuteUser)
        # self.on('UnmuteUser', caller.onUnmuteUser)
        # self.on('SetAsAdmin', caller.onSetAsAdmin)

    def handle_input(self, user_input, tracker):
        tokens = user_input.split()

        if not tokens:
            return

        if tokens[0][0] != '/':
            tracker.send_chat(user_input)

        elif tokens[0] in ['/request_user_info', '/who', '/rui']:
            if len(tokens) == 2:
                peer = tracker.get_peer_from_name(tokens[1])
                if peer is not None:
                    print(f'{peer.name} has ip and port: {peer.ip}:{peer.port}')
                else:
                    logger.error(f'Name not found!')
            else:
                logger.error(f'Usage: {tokens[0]} <username>')

        elif tokens[0] in ['/whisper_to_user', '/msg', '/w']:
            if len(tokens) >= 3:
                tracker.whisper(tokens[1], ' '.join(tokens[2:]))
            else:
                logger.error(f'Usage: {tokens[0]} <username> <message>')
            
        elif tokens[0] in ['/request_online_list', '/online', '/list']:
            print(f'Online Users:', ', '.join(tracker.online()))

        elif tokens[0] in ['/quit', '/exit', '/leave']:
            tracker.quit()
            return True

        elif tokens[0] in ['/connect', '/add']:
            if len(tokens) == 3:
                try:
                    ip = tokens[1]
                    port = int(tokens[2])
                except ValueError:
                    logger.error('Use a valid value for port.')
                else:
                    logger.info(f'Connecting to {ip}:{port}')
                    tracker.send_message(messages.Handshake(tracker), Peer(ip, port, None))
            else:
                logger.error(f'Usage: {tokens[0]} <ip> <port>')

        elif tokens[0] in ['/disconnect', '/dc']:
            if len(tokens) == 2:
                tracker.disconnect_peer(tokens[1])
            else:
                logger.error(f'Usage: {tokens[0]} <username>')

        # elif tokens[0] in ['/changename', '/setusername', '/su']:
        #     if len(tokens) == 2:
        #         return messages.SetUsername(tokens[1])
        #     else:
        #         logger.error(f'Usage: {tokens[0]} <username>')
        #         return None

        # elif tokens[0] in ['/request_local_time', '/time']:
        #     return messages.RequestLocalTime()
            
        else:
            logger.error('Unknown command!')
            return None
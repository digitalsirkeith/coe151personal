from .. import logger
from ..messages import MessageData

class Handler:
    def __init__(self):
        self.func = dict()

    def on(self, event: str, event_func: callable):
        self.func[event] = event_func

    def handle_message(self, message, connection):
        if message is None:
            self.func['Terminate'](None, connection)
            
        data = MessageData(message)
        if data.mtp not in self.func:
            logger.error('Unsupported message type received!')
        else:
            return self.func[data.mtp](data, connection)

    def set_caller(self, caller):
        self.on('Terminate', caller.onTerminate)
        self.on('ServerMessage', caller.onServerMessage)
        self.on('SendChatFromUser', caller.onSendChatFromUser)
        self.on('SetUsername', caller.onSetUsername)
        self.on('Disconnect', caller.onDisconnect)
        self.on('ProvideUserInfo', caller.onProvideUserInfo)
        self.on('SendLocalTime', caller.onSendLocalTime)
        self.on('WhisperFromUser', caller.onWhisperFromUser)
        self.on('SendOnlineList', caller.onSendOnlineList)
        self.on('KickUser', caller.onKickUser)
        self.on('MuteUser', caller.onMuteUser)
        self.on('UnmuteUser', caller.onUnmuteUser)
        self.on('SetAsAdmin', caller.onSetAsAdmin)
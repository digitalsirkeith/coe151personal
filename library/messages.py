import json
from datetime import datetime

"""
    Helper class for parsing message data
"""

class MessageData:
    def __init__(self, message):
        self.name = None
        self.status = None
        self.message = None
        self.time = None
        self.ip = None
        self.port = None
        self.names = None

        if 'name' in message['data']:
            self.name = message['data']['name']

        if 'names' in message['data']:
            self.names = message['data']['names']

        if 'message' in message['data']:
            self.message = message['data']['message']
            
        if 'time' in message['data']:
            self.time = message['data']['time']

        if 'ip' in message['data']:
            self.ip = message['data']['ip']
        
        if 'port' in message['data']:
            self.port = message['data']['port']

        self.mtp = message['mtp']

        if 'status' in message:
            self.status = message['status']

""" 
    Both Serverbound and Clientbound
    These are messages sent both by client and server.
"""
def SetUsername(name: str, status: str="OK"):
    return json.dumps({
        'mtp': 'SetUsername',
        'data': {
            'name': name
        },
        'status': status
    })

def Disconnect(reason: str=""):
    return json.dumps({
        'mtp': 'Disconnect',
        'data': {
            "message": reason
        }
    })

def KickUser(name: str="", status: str="OK"):
    return json.dumps({
        'mtp': 'KickUser',
        'data': {
            'name': name
        },
        'status': status
    })

def MuteUser(name: str="", status: str="OK"):
    return json.dumps({
        'mtp': 'MuteUser',
        'data': {
            'name': name
        },
        'status': status
    })

def UnmuteUser(name: str="", status: str="OK"):
    return json.dumps({
        'mtp': 'UnmuteUser',
        'data': {
            'name': name
        },
        'status': status
    })

def SetAsAdmin(name: str="", status: str="OK"):
    return json.dumps({
        'mtp': 'SetAsAdmin',
        'data': {
            'name': name
        },
        'status': status
    })

""" 
    Serverbound Messages
    Messages sent to the server.
"""

def Login(name: str):
    return json.dumps({
        'mtp': 'Login', 
        'data': {
            'name': name
        }
    })

def RequestUserInfo(name: str):
    return json.dumps({
        'mtp': 'RequestUserInfo', 
        'data': {
            'name': name
        }
    })

def RequestLocalTime():
    return json.dumps({
        'mtp': 'RequestLocalTime',
        'data': {}
    })

def WhisperToUser(from_user, to_users, message):
    return json.dumps({
        'mtp': 'WhisperToUser',
        'data': {
            'from': from_user,
            'to': to_users,
            'message': message
        }
    })

def SendChat(message):
    return json.dumps({
        'mtp': 'SendChat',
        'data': {
            'message': message
        }
    })

def RequestOnlineList():
    return json.dumps({
        'mtp': 'RequestOnlineList',
        'data': {}
    })

""" 
    Clientbound Messages
    Messages sent to the client
"""

def AssignUsername(name: str, status: str='OK'):
    return json.dumps({
        'mtp': 'AssignUsername',
        'data': {
            'name': name
        },
        'status': status
    })

def ProvideUserInfo(client, status='OK'):
    return json.dumps({
        'mtp': 'ProvideUserInfo',
        'data': {
            'name': client.name,
            'ip': client.ip_addr,
            'port': client.port
        } if client else {},
        'status': status
    })

def SendLocalTime():
    return json.dumps({
        'mtp': 'SendLocalTime',
        'data': {
            'time': datetime.now().strftime('%H:%M:%S')
        }
    })

def WhisperFromUser(name, message):
    return json.dumps({
        'mtp': 'WhisperFromUser',
        'data': {
            'name': name,
            'message': message
        }
    })

def SendChatFromUser(name, message):
    return json.dumps({
        'mtp': 'SendChatFromUser',
        'data': {
            'name': name,
            'message': message
        }
    })

def SendOnlineList(names):
    return json.dumps({
        'mtp': 'SendOnlineList',
        'data': {
            'names': names
        }
    })

def ServerMessage(message):
    return json.dumps({
        'mtp': 'ServerMessage',
        'data': {
            'message': message
        }
    })
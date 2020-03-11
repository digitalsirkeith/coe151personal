import json

def Login(name: str):
    return json.dumps({
        'mtp': 'Login', 
        'data': {
            'name': name
        }
    })

def AssignUsername(name: str, status: str="OK"):
    return json.dumps({
        'mtp': 'AssignUsername',
        'data': {
            'name': name
        },
        'status': status
    })

def ServerMessage(message):
    return json.dumps({
        'mtp': 'ServerMessage',
        'data': {
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

def SendChatFromUser(name, message):
    return json.dumps({
        'mtp': 'SendChat',
        'data': {
            'name': name,
            'message': message
        }
    })

def Disconnect():
    return json.dumps({
        'mtp': 'Disconnect',
        'data': {}
    })
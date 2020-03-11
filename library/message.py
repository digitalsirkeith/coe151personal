import json

def Login(name):
    return json.dumps(
        {
            'mtp': 'Login', 
            'data': {
                'name': name
            }
        })
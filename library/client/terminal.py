def onTerminate(data, connection):
    connection.terminate()
    return True

def onServerMessage(data, connection):
    print(data.message)

def onSendChatFromUser(data, connection):
    print(f'{data.name}: {data.message}')

def onSetUsername(data, connection):
    if data.status == 'OK':
        connection.set_name(data.name)
        print(f'Your new name is: {connection.name}')
    else:
        print(f'Failed to change name: {data.status}')

def onDisconnect(data, connection):
    print(f'Disconnected. {data.message}')
    connection.terminate()
    return True

def onProvideUserInfo(data, connection):
    print(f'{data.name} is {data.ip}:{data.port}')

def onSendLocalTime(data, connection):
    print(f'Server local time: {data.time}')

def onWhisperFromUser(data, connection):
    print(f'[{data.name} -> me]: {data.message}')

def onSendOnlineList(data, connection):
    print(f'Online Users:', ', '.join(data.names))

def onKickUser(data, connection):
    if data.status == 'OK':
        print('Kicked user')
    else:
        print(f'Failed to kick user: {data.status}')

def onMuteUser(data, connection):
    if data.status == 'OK':
        print('Muted user')
    else:
        print(f'Failed to mute user: {data.status}')

def onUnmuteUser(data, connection):
    if data.status == 'OK':
        print('Unmuted user')
    else:
        print(f'Failed to unmute user: {data.status}')

def onSetAsAdmin(data, connection):
    if data.status == 'OK':
        print('Set user as admin.')
    else:
        print(f'Failed to set user as admin: {data.status}')
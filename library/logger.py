from . import config

def info(message):
    if 'info' in config.ENABLED_LOGGERS:
        print(f'[INFO] {message}')

def debug(message):
    if 'debug' in config.ENABLED_LOGGERS:
        print(f'[DEBUG] {message}')

def warning(message):
    if 'warning' in config.ENABLED_LOGGERS:
        print(f'[WARNING] {message}')

def error(message):
    if 'error' in config.ENABLED_LOGGERS:
        print(f'[ERROR] {message}')

def chat(message):
    if 'chat' in config.ENABLED_LOGGERS:
        print(f'[CHAT] {message}')
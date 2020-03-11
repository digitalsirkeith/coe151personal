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
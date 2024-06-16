import logging
import os


def get_env_variable(var_name: str, default_value=None):
    """Get the environment variable or return the default value."""
    return os.getenv(var_name, default_value)


class SingletonMeta(type):
    """A Singleton metaclass to ensure only one instance of the logger."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    def __init__(self):
        log_level = get_env_variable('LOG_LEVEL', 'INFO').upper()
        self.logger = logging.getLogger("FileProcessorLogger")
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger

class FileReadError(Exception):
    """Custom exception for file reading errors."""
    pass

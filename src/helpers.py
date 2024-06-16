import logging
import os
from typing import Any, Optional


def get_env_variable(var_name: str, default_value: Optional[Any] = None) -> Any:
    """
    Get the environment variable or return the default value.

    Args:
        var_name (str): The name of the environment variable.
        default_value (Optional[Any]): The default value to return if the environment variable is not set.

    Returns:
        Any: The value of the environment variable or the default value.
    """
    return os.getenv(var_name, default_value)


class SingletonMeta(type):
    """A Singleton metaclass to ensure only one instance of the logger."""
    _instances: dict[type, Any] = {}

    def __call__(cls: type, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    """Logger class utilizing the Singleton pattern."""

    def __init__(self) -> None:
        """Initialize the Logger with a specific log level."""
        log_level = get_env_variable('LOG_LEVEL', 'INFO').upper()
        self.logger = logging.getLogger("FileProcessorLogger")
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
            '%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        """
        Get the logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger


class FileReadError(Exception):
    """Custom exception for file reading errors."""
    pass

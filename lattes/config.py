from logging.config import fileConfig
from pathlib import Path
import logging
import os


class BaseLogger:

    file_name = 'logging_config.ini'
    file_path = Path(__file__).parent.absolute()
    CONFIG_FILE = os.path.join(file_path, file_name)

    def __init__(self):
        self.logger_name = self.__class__.__name__
        self.logger = self.set_logger()

    def set_logger(self):
        """Create and returns a logger object configured based on an external
        file: CONFIG_FILE.
        """
        fileConfig(self.CONFIG_FILE)
        logger = logging.getLogger(self.logger_name)
        return logger

    @classmethod
    def from_name(cls, name):
        """Alternative log constructor in order to get a logger not by inheritance."""
        fileConfig(cls.CONFIG_FILE)
        logger = logging.getLogger(name)
        return logger

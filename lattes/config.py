from logging.config import fileConfig
from pathlib import Path
import logging
import os


class BaseLogger:

    file_name = 'logging_config.ini'
    file_path = Path(__file__).parent.absolute()
    CONFIG_FILE = os.path.join(file_path, file_name)

    def __init__(self):
        logger_name = self.__class__.__name__
        self.logger = self.get_logger(logger_name)

    def get_logger(self, name):
        """Create and returns a logger object configured based on an external
        file: CONFIG_FILE.
        """
        fileConfig(self.CONFIG_FILE)
        logger = logging.getLogger(name)
        return logger

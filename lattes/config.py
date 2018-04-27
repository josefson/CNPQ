#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler
import logging


class BaseLogger:

    base_name = 'CNPQ.'
    formatter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(processName)s|%(name)s|%(filename)s|'
        '%(funcName)s - %(message)s', '%Y-%m-%d %H:%M:%S'
        )

    def __init__(self, rotating_file=''):
        self.name = self.base_name + self.__class__.__name__
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.file_handler(rotating_file)

    def file_handler(self, file_name):
        file_handler = RotatingFileHandler(
            file_name, mode='a', maxBytes=500000, backupCount=5
            )
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    @classmethod
    def from_file(cls, logger_name='client', file_name=None):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        if file_name:
            file_handler = RotatingFileHandler(
                file_name, mode='a', maxBytes=500000, backupCount=5
                )
            file_handler.setFormatter(cls.formatter)
            logger.addHandler(file_handler)
            return logger
        else:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(cls.formatter)
            logger.addHandler(stream_handler)
            return logger

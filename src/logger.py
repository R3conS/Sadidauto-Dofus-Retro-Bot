import logging
from datetime import datetime
import os


class Logger:

    LOGS_DIR_PATH = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(LOGS_DIR_PATH):
        os.mkdir(LOGS_DIR_PATH)

    LOGGER_NAME = datetime.now().strftime("[%Y-%m-%d] %H-%M-%S")
    LOGGER_DIR_PATH = os.path.join(LOGS_DIR_PATH, LOGGER_NAME)
    if not os.path.exists(LOGGER_DIR_PATH):
        os.mkdir(LOGGER_DIR_PATH)

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def get_logger(
        cls,
        log_level: int,
        log_to_console: bool,
        log_to_file: bool
    ):
        """
        Get logger object. 
        
        Make sure to call this method at the top of the module before 
        any other imports:

        from src.logger import Logger
        log = Logger.get_logger(Logger.DEBUG, True, True)
        """
        if cls.LOGGER_NAME in logging.Logger.manager.loggerDict:
            return logging.getLogger(cls.LOGGER_NAME)
        else:
            return cls._create_logger(
                cls.LOGGER_NAME,
                log_level,
                log_to_console,
                log_to_file
            )

    @classmethod
    def get_logger_dir_path(cls):
        return cls.LOGGER_DIR_PATH

    @classmethod
    def _create_logger(
        cls,
        logger_name: str,
        log_level: int,
        log_to_console: bool,
        log_to_file: bool
    ):
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = False
        if log_to_file:
            logger.addHandler(cls._create_file_handler())
        if log_to_console:
            logger.addHandler(cls._create_stream_handler())
        return logger

    @classmethod
    def _create_file_handler(cls):
        log_filename = cls.LOGGER_NAME + ".log"
        file_handler = logging.FileHandler(
            filename=os.path.join(cls.LOGGER_DIR_PATH, log_filename)
        )
        file_formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        return file_handler

    @staticmethod
    def _create_stream_handler():
        stream_formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        return stream_handler


if __name__ == "__main__":
    log = Logger.get_logger(Logger.DEBUG, True, True)
    log.info("Hello World!")

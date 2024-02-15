import glob
import logging
import multiprocessing as mp
import os
from datetime import datetime
import logging
import logging.handlers
import multiprocessing


class Logger:

    MASTER_LOGS_DIR_PATH = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(MASTER_LOGS_DIR_PATH):
        os.mkdir(MASTER_LOGS_DIR_PATH)

    # LOGGER_NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    # LOGGER_DIR_PATH = os.path.join(MASTER_LOGS_DIR_PATH, LOGGER_NAME)
    # if not os.path.exists(LOGGER_DIR_PATH):
    #     os.mkdir(LOGGER_DIR_PATH)

    @classmethod
    def configure_main_process_logger(cls, log_listener_queue: mp.Queue):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        queue_handler = logging.handlers.QueueHandler(log_listener_queue)
        logger.addHandler(queue_handler)
        log_dir = cls.get_session_log_folder_path()
        log_file_path = os.path.join(log_dir, "log_main_process.txt")
        file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    @classmethod
    def configure_bot_process_logger(cls, log_listener_queue: mp.Queue):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        queue_handler = logging.handlers.QueueHandler(log_listener_queue)
        logger.addHandler(queue_handler)
        log_dir = cls.get_session_log_folder_path()
        log_file_path = os.path.join(log_dir, "log_bot_process.txt")
        file_handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    @staticmethod
    def get_session_file_name():
        cwd = os.getcwd()
        session_files = glob.glob(os.path.join(cwd, '*.session'))
        if not session_files:
            raise FileNotFoundError(f"No session file in: {cwd}")

        session_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_session_file_name = os.path.basename(session_files[0])
        for session_file in session_files[1:]:
            os.remove(session_file)

        return latest_session_file_name

    @classmethod
    def get_session_log_folder_path(cls):
        return os.path.join(cls.MASTER_LOGS_DIR_PATH, cls.get_session_file_name())

    @classmethod
    def create_session_log_folder(cls):
        folder_path = cls.get_session_log_folder_path()
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    @classmethod
    def get_logger(cls):
        """
        Get logger object. 
        
        Make sure to call this method at the top of the module before 
        any other imports:

        from src.logger import Logger\n
        log = Logger.get_logger()
        """
        if cls.LOGGER_NAME in logging.Logger.manager.loggerDict:
            return logging.getLogger(cls.LOGGER_NAME)
        else:
            return cls._create_logger(
                logger_name=cls.LOGGER_NAME,
                log_level=logging.DEBUG,
                log_to_console=True,
                log_to_file=True
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
    log = Logger.get_logger()
    log.info("Hello World!")

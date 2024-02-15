import glob
import logging
import os
from datetime import datetime


class Logger:

    MASTER_LOGS_DIR_PATH = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(MASTER_LOGS_DIR_PATH):
        os.mkdir(MASTER_LOGS_DIR_PATH)

    @staticmethod
    def create_session_file():
        with open(os.path.join(os.getcwd(), datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3] + ".session"), "w") as f:
            print("Session file created!")
            pass

    @classmethod
    def create_session_log_folder(cls):
        folder_path = cls.get_session_log_folder_path()
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    @classmethod
    def configure_process_logger(cls, log_file_name: str, logging_level: int = logging.DEBUG):
        logger = logging.getLogger()
        logger.setLevel(logging_level)
        if log_file_name != "debug.log":
            file_handler = logging.FileHandler(os.path.join(cls.get_session_log_folder_path(), log_file_name))
        else:
            file_handler = logging.FileHandler(os.path.join(cls.MASTER_LOGS_DIR_PATH, log_file_name))
        file_handler.setFormatter(cls._get_formatter())
        logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(cls._get_formatter())
        logger.addHandler(stream_handler)

    @classmethod
    def get_logger(cls):
        logger = logging.getLogger()
        # Happens when program isn't started from __main__.py. Mostly when
        # developing and running other modules as __main__.
        if len(logger.handlers) == 0:
            cls.configure_process_logger("debug.log")
        return logging.getLogger()

    @classmethod
    def get_session_log_folder_path(cls):
        return os.path.join(cls.MASTER_LOGS_DIR_PATH, cls._get_session_file_name())

    @staticmethod
    def _get_formatter():
        return logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def _get_session_file_name():
        cwd = os.getcwd()
        session_files = glob.glob(os.path.join(cwd, '*.session'))
        if not session_files:
            raise FileNotFoundError(f"No session file in: {cwd}")

        session_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_session_file_name = os.path.basename(session_files[0])
        for session_file in session_files[1:]:
            os.remove(session_file)

        return latest_session_file_name


if __name__ == "__main__":
    log = Logger.get_logger()
    log.info("Hello World!")

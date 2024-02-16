import glob
import logging
import multiprocessing as mp
import os
from datetime import datetime


class Logger:

    MASTER_LOGS_DIR_PATH = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(MASTER_LOGS_DIR_PATH):
        os.mkdir(MASTER_LOGS_DIR_PATH)

    @classmethod
    def create_session_file(cls):
        with open(os.path.join(os.getcwd(), cls._get_timestamp() + ".session"), "w") as f:
            print("Session file created!")
            pass

    @classmethod
    def create_session_log_folder(cls):
        folder_path = cls.get_session_log_folder_path()
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    @classmethod
    def get_logger(cls):
        current_process_name = mp.current_process().name
        logger = logging.getLogger(current_process_name)

        if len(logger.handlers) == 0:
            logger.setLevel(logging.DEBUG)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(cls._get_formatter())
            logger.addHandler(stream_handler)

            if current_process_name == "MainProcess":
                file_handler = logging.FileHandler(
                   os.path.join(cls.get_session_log_folder_path(), "main_process.log") 
                )
            elif current_process_name == "BotProcess":
                file_handler = logging.FileHandler(
                   os.path.join(cls.get_session_log_folder_path(), f"bot_process_{cls._get_timestamp()}.log") 
                )
            file_handler.setFormatter(cls._get_formatter())
            logger.addHandler(file_handler)
                
        return logger

    @classmethod
    def get_session_log_folder_path(cls):
        return os.path.join(cls.MASTER_LOGS_DIR_PATH, cls._get_session_file_name())

    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

    @staticmethod
    def _get_formatter():
        return logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    @staticmethod
    def _get_session_file_name():
        """Get the name of the newest session file and delete the rest.""" 
        session_files = glob.glob(os.path.join(os.getcwd(), '*.session'))
        if not session_files:
            raise FileNotFoundError(f"No session file in: {os.getcwd()}")
        session_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for session_file in session_files[1:]:
            os.remove(session_file)
        return os.path.basename(session_files[0])


if __name__ == "__main__":
    log = Logger.get_logger()
    log.info("Hello World!")

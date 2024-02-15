import logging
import multiprocessing as mp
import os

from src.logger import Logger


class LogListener(mp.Process):

    def __init__(self, log_record_queue: mp.Queue):
        super().__init__()
        self.log_record_queue = log_record_queue

    def run(self):
        print("Log listener started!")
        self.configure()
        while True:
            try:
                record = self.log_record_queue.get()
                if record is None:
                    break
                logger = logging.getLogger()
                logger.handle(record)
            except Exception:
                import traceback
                print("An exception occured in main_log_listener_process!")
                print(traceback.format_exc())    

    def configure(self):
        root_logger = logging.getLogger()
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler) 

        log_dir = Logger.get_session_log_folder_path()
        log_file_path = os.path.join(log_dir, "log_all.txt")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
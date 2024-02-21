import os
from threading import Thread
from time import perf_counter, sleep

from PySide6.QtCore import QObject, Signal

from src.logger import get_logger, get_session_log_folder_path

log = get_logger()


# Not inheriting from QThread because, even after the run() method completes
# and the finished signal is emitted, a DummyThread object persists in the
# threading.enumerate() list. With each invocation of this thread, a new
# DummyThread object is added to the list, leading to an accumulation of
# these objects. According to this Stack Overflow answer --
# https://stackoverflow.com/a/55778564/14787568 -- DummyThread objects are
# utilized to represent threads not managed by the threading module, and
# they are not considered memory leaks. Nonetheless, I prefer to avoid
# cluttering the threading.enumerate() list.
class BotProcessLogReader(QObject, Thread):

    log_file_line_read = Signal(str)

    def __init__(self, bot_process, bot_process_start_time: float):
        super().__init__()
        self._bot_process = bot_process
        self._bot_process_start_time = bot_process_start_time

    def run(self):
        log.info("Bot process log reader started!")
        log.info("Looking for log file ...")

        timeout = 10 
        start_time = perf_counter() 
        while perf_counter() - start_time <= timeout:
            file = self._get_most_recently_modified_file() 
            if (
                file is not None
                and self._is_file_modified_after_bot_process_start_time(file)
            ):
                break
            sleep(0.25)
            continue
        else:
            log.info(f"Failed to find log file in '{timeout}' seconds.")
            return

        log.info(f"Log file found! Reading ... ")
        for line in self._read_file_lines(file):
            self.log_file_line_read.emit(line)

    def _is_file_modified_after_bot_process_start_time(self, file_path: str):
        return os.path.getmtime(file_path) >= self._bot_process_start_time 

    def _read_file_lines(self, file_path: str):
        with open(file_path, "r") as f:
            file_pointer_position = 0
            while True:
                f.seek(file_pointer_position)
                line = f.readline()
                if not line:
                    if not self._bot_process.is_alive() and file_pointer_position == f.tell():
                        break
                    sleep(0.25)
                    continue
                file_pointer_position = f.tell()
                yield line.strip()

    @staticmethod
    def _get_all_bot_process_files():
        log_dir_path = get_session_log_folder_path()
        return [
            os.path.join(log_dir_path, f) for f 
            in os.listdir(get_session_log_folder_path()) if "BotProcess" in f
        ]

    @classmethod
    def _get_most_recently_modified_file(cls):
        all_bot_process_files = cls._get_all_bot_process_files()
        if len(all_bot_process_files) == 0:
            return None
        return max(all_bot_process_files, key=os.path.getctime)

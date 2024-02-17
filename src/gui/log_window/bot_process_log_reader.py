import os
from time import perf_counter, sleep

from PySide6.QtCore import QThread, Signal

from src.logger import get_logger, get_session_log_folder_path
log = get_logger()


class BotProcessLogReader(QThread):

    line_read_signal = Signal(str)

    def __init__(self, bot_process, bot_process_start_time: float, parent=None):
        super().__init__(parent)
        self._bot_process = bot_process
        self._bot_process_start_time = bot_process_start_time

    def run(self):
        log.info("Bot process log reader started!")
        while self._bot_process.is_alive():
            log.info("Looking for log file ...")
            file = self._get_most_recently_modified_file() 
            if not self._is_file_modified_after_time(file, self._bot_process_start_time):
                sleep(1)
                continue

            log.info(f"Found log file: '{file}'!")
            for line in self._read_file_lines(file):
                print(f"Read line: {line}")
                self.line_read_signal.emit(line)
        else:
            log.info("Bot process has exited before the log file was found. Stopping the log reader.")

    @staticmethod
    def _get_all_bot_process_files():
        # return [f for f in os.listdir(get_session_log_folder_path()) if f.startswith("bot_process")]
        return [f for f in os.listdir(os.getcwd()) if f.startswith("bot_process")]

    @classmethod
    def _get_most_recently_modified_file(cls):
        all_bot_process_files = cls._get_all_bot_process_files()
        if not all_bot_process_files:
            return None
        return max(all_bot_process_files, key=os.path.getctime)

    @staticmethod
    def _get_file_modification_time(file_path: str):
        return os.path.getmtime(file_path)

    @staticmethod
    def _is_file_modified_after_time(file_path: str, time: float):
        return os.path.getmtime(file_path) > time

    def _read_file_lines(self, file_path: str):
        log.info(f"Reading lines from file: '{file_path}'.")
        with open(file_path, "r") as f:
            file_pointer_position = 0
            while True:
                f.seek(file_pointer_position)
                line = f.readline()
                if not line:
                    if not self._bot_process.is_alive() and file_pointer_position == f.tell():
                        print("Bot process has exited and file has not been modified.")
                        break
                    sleep(1)
                    continue
                file_pointer_position = f.tell()
                yield line.strip()


   
def dummy_bot_process(time):
    print("started")
    sleep(time)

if __name__ == "__main__":
    import multiprocessing as mp
    from time import time
    dummy_time = 2900000000.0
    
    process = mp.Process(target=dummy_bot_process, args=(3,))
    process.start()

    reader = BotProcessLogReader(process, dummy_time)
    reader.start()

    reader.wait()

    print(f"Is process alie: {process.is_alive()}")
    print(f"Is reader alive: {reader.isRunning()}")


    # reader = BotProcessLogReader()
    # for line in reader._read_file_lines(file):
    #     print(line)


# Receive signal that bot is started.
# Save the received signal time.
# Start bot process log reader.
# Get the latest bot process file and check if its last modificatio time
# is greater than the received signal time. If it is then start reading
# the file. If it's not keep checking each second.
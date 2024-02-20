from src.logger import get_logger

log = get_logger()

from time import perf_counter, sleep, time

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMainWindow, QPushButton

from src.bot.bot import Bot


class StartButton(QPushButton):

    bot_started_signal = Signal(Bot, float) # Bot, start_time
    bot_exited_due_to_exception_signal = Signal()
    initialization_options_invalid_signal = Signal(str)
    bot_stopped_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self._on_button_clicked)

    def on_bot_stopped(self):
        self._label_updater.stopped = True
        self.setEnabled(True)

    def on_bot_exited_due_to_exception(self):
        self.bot_exited_due_to_exception_signal.emit()
        self.setEnabled(True)
        self.window().setFocus() # Without this the focus for some reason shifts to character name line edit

    def _on_button_clicked(self):
        main_window = self.window()
        if not self._are_initialization_options_valid(main_window):
            return
        self._start_bot_process(main_window)

    def _are_initialization_options_valid(self, main_window: QMainWindow):
        if main_window.character_name_line_edit.text() == "":
            self.initialization_options_invalid_signal.emit("Character name is not set!")
            return False
        if main_window.server_combo_box.currentIndex() == -1:
            self.initialization_options_invalid_signal.emit("Server is not selected!")
            return False
        if main_window.script_combo_box.currentIndex() == -1:
            self.initialization_options_invalid_signal.emit("Script is not selected!")
            return False
        return True

    def _start_bot_process(self, main_window: QMainWindow):
        bot = Bot(
            script=main_window.script_combo_box.currentText(),
            character_name=main_window.character_name_line_edit.text(),
            server_name=main_window.server_combo_box.currentText(),
            go_bank_when_pods_percentage=main_window.bank_percentage_spin_box.value(),
            disable_spectator_mode=main_window.spectator_mode_check_box.isChecked()
        )
        log.info("Starting the bot process ...")
        bot.start()
        log.info("Bot process has started!")
        self.setEnabled(False)
        self.bot_started_signal.emit(bot, time())
        self._label_updater = _RunTimeDurationLabelUpdater(main_window.run_time_duration_label, bot.is_alive, self)
        self._label_updater.bot_exited_due_to_exception.connect(self.on_bot_exited_due_to_exception)
        self._label_updater.start()
        self._bot_process_alive_checker = _BotProcessAliveChecker(bot.is_alive, self)
        self._bot_process_alive_checker.bot_stopped_signal.connect(self.bot_stopped_signal)
        self._bot_process_alive_checker.start()


class _RunTimeDurationLabelUpdater(QThread):

    bot_exited_due_to_exception = Signal()

    def __init__(self, time_label, is_bot_process_alive: callable, parent=None):
        super().__init__(parent)
        self.stopped = False
        self._is_bot_process_alive = is_bot_process_alive
        self._time_label = time_label

    def run(self):
        start_time = perf_counter()
        while not self.stopped:
            if not self._is_bot_process_alive(): # Prevents the label from updating if Bot exited due to an exception.
                self.bot_exited_due_to_exception.emit()
                break
            current_time = perf_counter()
            elapsed_time = int(current_time - start_time)
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            self._time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")


class _BotProcessAliveChecker(QThread):

    bot_stopped_signal = Signal()

    def __init__(self, is_bot_process_alive: callable, parent=None):
        super().__init__(parent)
        self._is_bot_process_alive = is_bot_process_alive

    def run(self):
        while self._is_bot_process_alive():
            sleep(1)
        self.bot_stopped_signal.emit()
 
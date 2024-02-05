from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton

from src.bot.bot import Bot


class StartButton(QPushButton):

    bot_object_initialized_signal = Signal(Bot)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self._on_button_clicked)

    # Slot
    def _on_button_clicked(self):
        main_window = self.window()
        bot = Bot(
            script=main_window.script_combo_box.currentText(),
            character_name=main_window.character_name_line_edit.text(),
            server_name=main_window.server_combo_box.currentText(),
            go_bank_when_pods_percentage=main_window.bank_percentage_spin_box.value(),
            disable_spec_mode=main_window.spectator_mode_check_box.isChecked()
        )
        self.bot_object_initialized_signal.emit(bot)
        bot.start()
        self.setEnabled(False)

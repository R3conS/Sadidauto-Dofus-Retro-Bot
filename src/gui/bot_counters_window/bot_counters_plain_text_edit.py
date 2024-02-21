import re

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit


class BotCountersPlainTextEdit(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._read_only = True
        # This call is necessary so that the text edit is not editable 
        # when this module is ran as __main__.
        self.setReadOnly(self._read_only) 
        self.setFont(QFont("Segoe UI", 14))
        self.current_counters = {}

    """Override"""
    def setReadOnly(self, _):
        # For some reason using self.setReadOnly() in __init__() doesn't
        # seem to work when app is started from __main__.py. Works either
        # through QT Designer or like this.
        return super().setReadOnly(self._read_only)

    def on_bot_started(self):
        self.clear()
        self.current_counters = {}

    def on_log_file_line_read(self, log_line: str):
        if self._is_started_fight_number_line(log_line):
            fight_number = self._parse_started_fight_number_line(log_line)
            self.current_counters["Total Fights"] = fight_number
        elif self._is_monster_count_line(log_line):
            monster_counts = self._parse_monster_count_line(log_line)
            for monster, count in monster_counts.items():
                if monster not in self.current_counters:
                    self.current_counters[monster] = 0
                self.current_counters[monster] += count

        self._display_current_counters()

    def _display_current_counters(self):
        self.clear()
        sorted_counters = {
            key: self.current_counters[key] 
            for key in sorted(self.current_counters)
        }

        # Display total fights first.
        if "Total Fights" in sorted_counters:
            self.appendHtml(f"Total Fights: {sorted_counters['Total Fights']}")

        for counter, value in sorted_counters.items():
            if counter != "Total Fights":
                self.appendHtml(f"{counter}: {value}")

    def _is_monster_count_line(self, log_line: str):
        return "Successfully attacked:" in log_line

    def _parse_monster_count_line(self, log_line: str):
        split_line = log_line.split("Successfully attacked:")[1].strip()
        counts_list = [w.strip().replace(".", "") for w in split_line.split(",")]
        counts_dict = {
            parts[1]: int(parts[0])
            for parts in (item.split(" ", 1) for item in counts_list)
        }
        return counts_dict 

    def _is_started_fight_number_line(self, log_line: str):
        return "Started fight number:" in log_line

    def _parse_started_fight_number_line(self, log_line: str):
        split_line = log_line.split("Started fight number:")[1].strip()
        match = re.search(r"(\d+)", split_line)
        if match:
            return int(match.group(1))
        return None 


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = BotCountersPlainTextEdit()
    log_message_1 = "Started fight number: '33'."
    window.on_log_file_line_read(log_message_1)
    log_message_2 = "Successfully attacked: 3 Prespic, 2 Gobball"
    window.on_log_file_line_read(log_message_2)
    log_message_2 = "Successfully attacked: 1 Boar, 3 Prespic, 2 Gobball"
    window.on_log_file_line_read(log_message_2)
    window.show()
    sys.exit(app.exec())
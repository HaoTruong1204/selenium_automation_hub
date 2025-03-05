# modules/logs.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDateTime

class LogsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Logs")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        layout.addWidget(self.log_console)

        self.setLayout(layout)

    def append_log(self, msg):
        ts = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.log_console.append(f"[{ts}] {msg}")

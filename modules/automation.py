# modules/automation.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QProgressBar, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .automation_worker import AutomationWorker

class AutomationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Automation")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Nhập URL cần tự động hóa...")
        layout.addWidget(self.url_edit)

        self.proxy_edit = QLineEdit()
        self.proxy_edit.setPlaceholderText("Nhập Proxy (nếu có)...")
        layout.addWidget(self.proxy_edit)

        self.headless_cb = QCheckBox("Chạy ở chế độ headless?")
        layout.addWidget(self.headless_cb)

        # Delay
        self.delay_edit = QLineEdit()
        self.delay_edit.setPlaceholderText("Độ trễ giữa các bước (giây), ví dụ 1.0")
        layout.addWidget(self.delay_edit)

        # Nút
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Bắt đầu")
        self.start_btn.clicked.connect(self.start_automation)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Dừng")
        self.stop_btn.clicked.connect(self.stop_automation)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Log
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        layout.addWidget(self.log_console)

        self.setLayout(layout)

    def start_automation(self):
        if self.worker and self.worker.isRunning():
            self.log_console.append("Một tiến trình đang chạy. Vui lòng dừng trước khi bắt đầu mới.")
            return

        url = self.url_edit.text().strip()
        proxy = self.proxy_edit.text().strip()
        headless = self.headless_cb.isChecked()
        delay_str = self.delay_edit.text().strip()
        if not delay_str:
            delay_str = "1"
        try:
            delay = float(delay_str)
        except:
            delay = 1.0

        if not url:
            self.log_console.append("❌ Vui lòng nhập URL!")
            return

        # Tạo worker
        self.worker = AutomationWorker(url=url, proxy=proxy, headless=headless, delay=delay)
        self.worker.log_signal.connect(self.log_console.append)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_finished)

        self.progress_bar.setValue(0)
        self.log_console.append(">>> Bắt đầu tự động hóa...")
        self.worker.start()

    def stop_automation(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_console.append(">>> Gửi tín hiệu dừng tiến trình...")

    def on_finished(self, status):
        self.log_console.append(f"Trạng thái: {status}")
        self.worker = None

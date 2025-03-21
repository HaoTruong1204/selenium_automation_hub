import os
import sys
import logging
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QComboBox, 
    QTextEdit, QProgressBar, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QIcon

from .automation_worker_fixed import EnhancedAutomationWorker

class MainWindow(QMainWindow):
    """
    Giao diện chính của ứng dụng Selenium Automation Hub
    """
    def __init__(self, worker_config=None, worker_class=None, parent=None):
        super().__init__(parent)
        
        self.worker = None
        self.worker_config = worker_config or {}
        self.worker_class = worker_class or EnhancedAutomationWorker
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        self.setWindowTitle("Selenium Automation Hub")
        self.setMinimumSize(800, 600)
        
        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout chính
        main_layout = QVBoxLayout(central_widget)
        
        # Controls area (top)
        controls_layout = QHBoxLayout()
        
        # Task selection
        self.task_combo = QComboBox()
        self.task_combo.addItems(["facebook", "google", "shopee"])
        controls_layout.addWidget(QLabel("Task:"))
        controls_layout.addWidget(self.task_combo)
        
        # Keyword input
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keyword...")
        controls_layout.addWidget(QLabel("Keyword:"))
        controls_layout.addWidget(self.keyword_input)
        
        # Headless mode
        self.headless_combo = QComboBox()
        self.headless_combo.addItems(["Visible", "Headless"])
        controls_layout.addWidget(QLabel("Mode:"))
        controls_layout.addWidget(self.headless_combo)
        
        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.setMinimumWidth(100)
        controls_layout.addWidget(self.start_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumWidth(100)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(controls_layout)
        
        # Results area (middle)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(QLabel("Logs:"))
        main_layout.addWidget(self.log_output)
        
        # Progress bar (bottom)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(QLabel("Progress:"))
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def setup_connections(self):
        """Thiết lập các kết nối tín hiệu-khe"""
        self.start_button.clicked.connect(self.start_task)
        self.stop_button.clicked.connect(self.stop_task)
        
    def start_task(self):
        """Bắt đầu tác vụ được chọn"""
        # Lấy cấu hình từ UI
        task = self.task_combo.currentText()
        keyword = self.keyword_input.text()
        headless = self.headless_combo.currentText() == "Headless"
        
        # Cập nhật cấu hình worker
        config = {
            "task": task,
            "keyword": keyword,
            "headless": headless,
            "use_stealth": True,
            "keep_browser_open": True,
            "chrome_config": {
                "profile_path": r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default",
                "binary_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                "use_brave": True
            }
        }
        
        # Tạo worker
        self.worker = self.worker_class(**config)
        
        # Kết nối signals
        self.worker.log_signal.connect(self.append_log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.finished_signal.connect(self.task_finished)
        
        # Bắt đầu worker
        self.worker.start()
        
        # Cập nhật UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage(f"Running {task} task...")
        
    def stop_task(self):
        """Dừng tác vụ đang chạy"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.append_log("Task stop requested...")
            
    @pyqtSlot(str)
    def append_log(self, message):
        """Thêm thông báo vào vùng log"""
        self.log_output.append(message)
        
    @pyqtSlot(int)
    def update_progress(self, value):
        """Cập nhật thanh tiến trình"""
        self.progress_bar.setValue(value)
        
    @pyqtSlot(str)
    def handle_error(self, error_message):
        """Xử lý thông báo lỗi"""
        self.append_log(f"ERROR: {error_message}")
        QMessageBox.critical(self, "Error", error_message)
        
    @pyqtSlot()
    def task_finished(self):
        """Xử lý khi task hoàn thành"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage("Task completed")
        self.append_log("Task completed") 
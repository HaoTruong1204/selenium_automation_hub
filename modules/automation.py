import os
import sys
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton,
    QHBoxLayout, QProgressBar, QTextEdit, QGroupBox, QFormLayout,
    QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# Import Worker thật (AutomationWorker) 
from .automation_worker import AutomationWorker

class AutomationWidget(QWidget):
    """
    Widget chạy Selenium thật với Brave:
      - URL, keyword
      - Proxy, headless, delay
      - Brave path, profile path
      - Chạy => AutomationWorker
    """
    log_signal = pyqtSignal(str)
    task_completed = pyqtSignal(str, str)

    def __init__(self, parent=None, proxies=None):
        super().__init__(parent)
        self.worker = None
        self.proxies = proxies or []

        # Mặc định Brave path & profile
        self.chrome_config = {
            "chrome_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "profile_path": r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default"
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Selenium Automation Hub (Brave)")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Nhóm task
        task_group = QGroupBox("Task Selection")
        task_layout = QFormLayout()
        
        self.task_combo = QComboBox()
        self.task_combo.addItems(["google", "facebook", "shopee", "custom"])
        self.task_combo.currentTextChanged.connect(self.on_task_changed)
        task_layout.addRow("Task:", self.task_combo)
        
        task_group.setLayout(task_layout)
        layout.addWidget(task_group)

        # Nhóm input
        target_group = QGroupBox("Target Configuration")
        target_layout = QFormLayout()

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Nhập URL cần tự động hoá...")
        target_layout.addRow("URL:", self.url_edit)

        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("Nhập từ khoá tìm kiếm")
        target_layout.addRow("Keyword:", self.keyword_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email/Phone (cho Facebook)")
        target_layout.addRow("Email:", self.email_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password (cho Facebook)")
        target_layout.addRow("Password:", self.password_edit)

        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # Nhóm options
        options_group = QGroupBox("Tùy chọn Browser")
        options_layout = QFormLayout()

        self.proxy_edit = QLineEdit()
        self.proxy_edit.setPlaceholderText("Proxy ip:port (nếu có)")
        options_layout.addRow("Proxy:", self.proxy_edit)
        
        self.use_proxies_cb = QCheckBox("Sử dụng proxy từ danh sách")
        self.use_proxies_cb.setChecked(True if self.proxies else False)
        options_layout.addRow("Auto Proxy:", self.use_proxies_cb)

        self.headless_cb = QCheckBox("Chạy headless?")
        options_layout.addRow("Headless:", self.headless_cb)

        self.delay_edit = QLineEdit()
        self.delay_edit.setText("1.0")
        self.delay_edit.setPlaceholderText("Độ trễ mỗi bước (giây)")
        options_layout.addRow("Delay:", self.delay_edit)
        
        self.max_results_edit = QLineEdit()
        self.max_results_edit.setText("10")
        self.max_results_edit.setPlaceholderText("Số kết quả tối đa")
        options_layout.addRow("Max Results:", self.max_results_edit)

        self.brave_path_edit = QLineEdit(self.chrome_config["chrome_path"])
        self.brave_path_edit.setPlaceholderText("Đường dẫn Brave.exe")
        options_layout.addRow("Brave exe:", self.brave_path_edit)

        self.brave_profile_edit = QLineEdit(self.chrome_config["profile_path"])
        self.brave_profile_edit.setPlaceholderText("Profile Brave")
        options_layout.addRow("Profile path:", self.brave_profile_edit)
        
        self.stealth_cb = QCheckBox("Sử dụng chế độ ẩn danh (tránh phát hiện)")
        self.stealth_cb.setChecked(True)
        options_layout.addRow("Stealth Mode:", self.stealth_cb)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Nút Bắt đầu, Dừng
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Bắt đầu")
        self.start_btn.clicked.connect(self.start_automation)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Dừng")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_automation)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

        # Thanh progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Log
        log_label = QLabel("Log:")
        layout.addWidget(log_label)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        layout.addWidget(self.log_console)

        self.setLayout(layout)
        
        # Set initial visibility based on task
        self.on_task_changed(self.task_combo.currentText())

        self.log_message("✅ Ready for Brave automation. Chọn task và bấm 'Bắt đầu'.")
        
    def on_task_changed(self, task):
        """Update UI based on selected task"""
        # Hide/show fields based on task
        is_facebook = task == "facebook"
        is_search = task in ["google", "shopee"]
        
        self.url_edit.setVisible(task == "custom")
        self.keyword_edit.setVisible(is_search)
        self.email_edit.setVisible(is_facebook)
        self.password_edit.setVisible(is_facebook)

    def start_automation(self):
        """Tạo AutomationWorker, chạy Brave."""
        if self.worker and self.worker.isRunning():
            self.log_message("Một tiến trình đang chạy. Dừng trước khi bắt đầu mới.")
            return

        task = self.task_combo.currentText()
        url = self.url_edit.text().strip()
        keyword = self.keyword_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        proxy = self.proxy_edit.text().strip() if not self.use_proxies_cb.isChecked() else None
        headless = self.headless_cb.isChecked()
        use_stealth = self.stealth_cb.isChecked()

        try:
            delay = float(self.delay_edit.text().strip())
        except:
            delay = 1.0
            
        try:
            max_results = int(self.max_results_edit.text().strip())
        except:
            max_results = 10

        # Cập nhật config
        self.chrome_config["chrome_path"] = self.brave_path_edit.text().strip()
        self.chrome_config["profile_path"] = self.brave_profile_edit.text().strip()

        # Validate inputs
        if task == "google" and not keyword:
            self.log_message("❌ Thiếu từ khóa cho tìm kiếm Google.")
            return
            
        if task == "shopee" and not keyword:
            self.log_message("❌ Thiếu từ khóa cho tìm kiếm Shopee.")
            return
            
        if task == "facebook" and (not email or not password):
            self.log_message("❌ Thiếu thông tin đăng nhập Facebook.")
            return
            
        if task == "custom" and not url:
            self.log_message("❌ Thiếu URL cho task tùy chỉnh.")
            return

        # Create worker with enhanced parameters
        self.worker = AutomationWorker()
        self.worker.task = task
        self.worker.keyword = keyword
        self.worker.email = email
        self.worker.password = password
        self.worker.url = url
        self.worker.headless = headless
        self.worker.delay = delay
        self.worker.max_results = max_results
        self.worker.chrome_config = self.chrome_config
        
        # Set proxy
        if self.use_proxies_cb.isChecked() and self.proxies:
            self.worker.all_proxies = self.proxies
            self.worker.should_rotate_proxies = True
            self.log_message(f"🔄 Using {len(self.proxies)} proxies from list")
        else:
            self.worker.proxy = proxy
            self.worker.should_rotate_proxies = False

        self.worker.log_signal.connect(self.log_message)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.result_signal.connect(self.on_results)
        self.worker.finished.connect(self.on_finished)

        self.progress_bar.setValue(0)
        self.log_message(f"🚀 Bắt đầu task {task}...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker.start()

    def stop_automation(self):
        """Dừng Worker."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_message("⚠️ Yêu cầu dừng...")
        else:
            self.log_message("Không có tiến trình nào.")

    def on_finished(self):
        """Khi worker xong."""
        self.log_message(f"✅ Task đã hoàn thành")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.worker = None
        
    def on_results(self, results):
        """Nhận kết quả từ worker"""
        if isinstance(results, list):
            self.log_message(f"📊 Nhận được {len(results)} kết quả")
            # Emit results for other components
            self.task_completed.emit(self.task_combo.currentText(), str(results))
        elif isinstance(results, bool):
            status = "thành công" if results else "thất bại"
            self.log_message(f"📊 Task {status}")
        else:
            self.log_message(f"📊 Kết quả: {results}")

    def log_message(self, msg):
        self.log_console.append(msg)
        self.log_signal.emit(msg)
        self.log_console.verticalScrollBar().setValue(
            self.log_console.verticalScrollBar().maximum()
        )
        
    def update_proxies(self, proxies):
        """Update proxy list from external components"""
        self.proxies = proxies
        self.use_proxies_cb.setChecked(True if proxies else False)
        self.log_message(f"📋 Danh sách proxy đã được cập nhật: {len(proxies)} proxies")
        
        # Update worker if running
        if self.worker and self.worker.isRunning() and self.use_proxies_cb.isChecked():
            self.worker.all_proxies = proxies
            self.log_message(f"🔄 Đã cập nhật proxy cho worker đang chạy")

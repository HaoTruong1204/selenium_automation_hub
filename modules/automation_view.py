"""
Module automation_view.py
This module implements the automation view for the Selenium Automation Hub.
"""

import sys
import time
from datetime import datetime
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QLineEdit, 
                             QCheckBox, QHBoxLayout, QPushButton, QProgressBar,
                             QTextEdit, QTableWidget, QTableWidgetItem, QFormLayout,
    QApplication, QHeaderView, QFileDialog
)
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCursor, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSettings, QDateTime

from modules.config import DEFAULT_THEME
from modules.automation_worker import EnhancedAutomationWorker

class AutomationView(QWidget):
    log_signal = pyqtSignal(str)
    task_completed = pyqtSignal(dict)  # Emits task result as a dictionary
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.settings = QSettings("MyApp", "AutomationWidget")
        self.active_proxies = []  # Danh sách proxy hoạt động
        self.start_time = 0  # Track when task begins
        self.init_ui()
        self.setup_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)

        header = QLabel("🚀 Điều Khiển Automation (Brave)")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 10))
        
        self.create_google_tab()
        self.create_facebook_tab()
        self.create_shopee_tab()
        
        main_layout.addWidget(self.tabs)
        self.setup_control_buttons(main_layout)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        main_layout.addWidget(self.progress)

        self.setup_output_sections(main_layout)

    def setup_styles(self):
        current_theme = self.settings.value("theme", DEFAULT_THEME)
        if current_theme == "Dark":
            self.setStyleSheet("""
                QWidget { background-color: #272727; color: #f5f5f5; }
                QTabWidget::pane { border: 1px solid #495057; border-radius: 8px; background-color: #323232; }
                QTabBar::tab { background-color: #272727; color: #f5f5f5; border: 1px solid #495057; padding: 8px 16px; margin-right: 5px; border-top-left-radius: 5px; border-top-right-radius: 5px; min-height: 30px; }
                QTabBar::tab:selected { background-color: #0d6efd; color: white; border-bottom-color: #0d6efd; }
                QLineEdit { padding: 8px; border: 1px solid #495057; border-radius: 5px; background-color: #323232; color: #f5f5f5; }
                QLineEdit:focus { border-color: #0d6efd; }
                QCheckBox { color: #f5f5f5; }
                QPushButton { background-color: #0d6efd; color: white; border: none; border-radius: 5px; padding: 8px 16px; min-height: 40px; font-weight: bold; }
                QPushButton:hover { background-color: #0b5ed7; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background-color: #f8f9fa; color: #212529; }
                QTabWidget::pane { border: 1px solid #ced4da; border-radius: 8px; background-color: white; }
                QTabBar::tab { background-color: #f0f2f5; color: #212529; border: 1px solid #ced4da; padding: 8px 16px; margin-right: 5px; border-top-left-radius: 5px; border-top-right-radius: 5px; min-height: 30px; }
                QTabBar::tab:selected { background-color: #0d6efd; color: white; border-bottom-color: #0d6efd; }
                QLineEdit { padding: 8px; border: 1px solid #ced4da; border-radius: 5px; background-color: white; color: #212529; }
                QLineEdit:focus { border-color: #0d6efd; }
                QCheckBox { color: #212529; }
                QPushButton { background-color: #0d6efd; color: white; border: none; border-radius: 5px; padding: 8px 16px; min-height: 40px; font-weight: bold; }
                QPushButton:hover { background-color: #0b5ed7; }
            """)

    # ------------------ TABS ------------------
    def create_google_tab(self):
        google_tab = QWidget()
        google_layout = QVBoxLayout(google_tab)
        google_layout.setContentsMargins(20, 20, 20, 20)
        google_layout.setSpacing(20)

        tab_header = QHBoxLayout()
        google_icon = QLabel()
        google_icon.setPixmap(QIcon("resources/icons/google.png").pixmap(32, 32))
        tab_header.addWidget(google_icon)

        google_title = QLabel("Google Search")
        google_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        tab_header.addWidget(google_title)
        tab_header.addStretch()

        google_layout.addLayout(tab_header)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.google_keyword = QLineEdit(self.settings.value("google_keyword", "selenium python automation"))
        self.google_keyword.setPlaceholderText("Nhập từ khoá (vd: học tiếng anh)")
        self.google_keyword.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("Từ khoá:", self.google_keyword)

        # Ensure google_max_results is a string
        max_results_value = self.settings.value("google_max_results", "10")
        if not isinstance(max_results_value, str):
            max_results_value = str(max_results_value)
            
        self.google_max_results = QLineEdit(max_results_value)
        self.google_max_results.setPlaceholderText("Số lượng kết quả tối đa")
        self.google_max_results.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("Số kết quả:", self.google_max_results)

        self.google_headless = QCheckBox("Chạy ẩn danh (headless)?")
        self.google_headless.setChecked(self.settings.value("google_headless", True, type=bool))
        form_layout.addRow("Tùy chọn:", self.google_headless)
        
        # Add proxy checkbox
        proxy_layout = QHBoxLayout()
        self.use_proxies_cb = QCheckBox("Sử dụng proxy từ Proxy Manager?")
        self.use_proxies_cb.setChecked(False)
        self.use_proxies_cb.setEnabled(False)  # Will be enabled if proxies are available
        proxy_layout.addWidget(self.use_proxies_cb)
        proxy_layout.addStretch()
        form_layout.addRow("Proxy:", proxy_layout)

        google_layout.addLayout(form_layout)

        desc = QLabel("Tab này sẽ thực hiện Google Search trên Brave.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6c757d; font-style: italic;")
        google_layout.addWidget(desc)

        google_layout.addStretch()
        self.tabs.addTab(google_tab, "Google Search")

    def create_facebook_tab(self):
        facebook_tab = QWidget()
        fb_layout = QVBoxLayout(facebook_tab)
        fb_layout.setContentsMargins(20, 20, 20, 20)
        fb_layout.setSpacing(20)

        tab_header = QHBoxLayout()
        fb_icon = QLabel()
        fb_icon.setPixmap(QIcon("resources/icons/facebook.png").pixmap(32, 32))
        tab_header.addWidget(fb_icon)

        fb_title = QLabel("Facebook Login")
        fb_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        tab_header.addWidget(fb_title)
        tab_header.addStretch()

        fb_layout.addLayout(tab_header)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.fb_email = QLineEdit(self.settings.value("fb_email", ""))
        self.fb_email.setPlaceholderText("Nhập email hoặc số điện thoại")
        self.fb_email.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("Email:", self.fb_email)

        self.fb_password = QLineEdit(self.settings.value("fb_password", ""))
        self.fb_password.setPlaceholderText("Nhập mật khẩu")
        self.fb_password.setEchoMode(QLineEdit.Password)
        self.fb_password.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("Mật khẩu:", self.fb_password)

        self.fb_save_login = QCheckBox("Lưu thông tin đăng nhập?")
        self.fb_save_login.setChecked(self.settings.value("fb_save_login", False, type=bool))
        form_layout.addRow("Tùy chọn:", self.fb_save_login)

        fb_layout.addLayout(form_layout)

        desc = QLabel("Tab này sẽ đăng nhập Facebook trên Brave.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6c757d; font-style: italic;")
        fb_layout.addWidget(desc)

        fb_layout.addStretch()
        self.tabs.addTab(facebook_tab, "Facebook")

    def create_shopee_tab(self):
        shopee_tab = QWidget()
        sp_layout = QVBoxLayout(shopee_tab)
        sp_layout.setContentsMargins(20, 20, 20, 20)
        sp_layout.setSpacing(20)

        tab_header = QHBoxLayout()
        sp_icon = QLabel()
        sp_icon.setPixmap(QIcon("resources/icons/shopee.png").pixmap(32, 32))
        tab_header.addWidget(sp_icon)

        sp_title = QLabel("Shopee Scraping")
        sp_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        tab_header.addWidget(sp_title)
        tab_header.addStretch()

        sp_layout.addLayout(tab_header)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.sp_keyword = QLineEdit(self.settings.value("sp_keyword", "điện thoại"))
        self.sp_keyword.setPlaceholderText("Nhập từ khóa sản phẩm")
        self.sp_keyword.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("Từ khóa:", self.sp_keyword)

        # Ensure sp_pages is a string
        sp_pages_value = self.settings.value("sp_pages", "2")
        if not isinstance(sp_pages_value, str):
            sp_pages_value = str(sp_pages_value)
            
        self.sp_pages = QLineEdit(sp_pages_value)
        self.sp_pages.setPlaceholderText("Số trang cần scrape")
        self.sp_pages.setFont(QFont("Segoe UI", 11))
        form_layout.addRow("Số trang:", self.sp_pages)

        self.sp_headless = QCheckBox("Chạy ẩn danh (headless)?")
        self.sp_headless.setChecked(self.settings.value("sp_headless", True, type=bool))
        form_layout.addRow("Tùy chọn:", self.sp_headless)

        sp_layout.addLayout(form_layout)

        desc = QLabel("Tab này sẽ scrape sản phẩm từ Shopee trên Brave.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6c757d; font-style: italic;")
        sp_layout.addWidget(desc)

        sp_layout.addStretch()
        self.tabs.addTab(shopee_tab, "Shopee")

    # ---------------- CONTROL BUTTONS ----------------
    def setup_control_buttons(self, layout):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.start_btn = QPushButton("Bắt đầu")
        self.start_btn.setIcon(QIcon("resources/icons/play.png"))
        
        self.stop_btn = QPushButton("Dừng")
        self.stop_btn.setIcon(QIcon("resources/icons/stop.png"))
        self.stop_btn.setEnabled(False)
        
        self.reset_btn = QPushButton("Làm mới")
        self.reset_btn.setIcon(QIcon("resources/icons/reset.png"))

        self.export_btn = QPushButton("Xuất CSV")
        self.export_btn.setIcon(QIcon("resources/icons/export.png"))
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        
        self.start_btn.clicked.connect(self.start_automation)
        self.stop_btn.clicked.connect(self.stop_automation)
        self.reset_btn.clicked.connect(self.reset_automation)
        self.export_btn.clicked.connect(self.export_results)
        
        layout.addLayout(btn_layout)

    def setup_output_sections(self, main_layout):
        output_tabs = QTabWidget()

        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 11))
        log_layout.addWidget(self.log_console)
        output_tabs.addTab(log_tab, "Logs")

        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        results_layout.addWidget(self.results_table)
        output_tabs.addTab(results_tab, "Kết quả")

        main_layout.addWidget(output_tabs)

    # ---------------- LOG ----------------
    def log_message(self, message, level="info"):
        """Add a message to the log widget with proper formatting"""
        # Get current date time for log
        now = datetime.now().strftime("%H:%M:%S")
        
        # Determine display format based on message level
        if level == "error":
            message = f"❌ {message}"
            color = "#e74c3c"  # Red
        elif level == "warning":
            message = f"⚠️ {message}"
            color = "#f39c12"  # Yellow/Orange
        elif level == "success":
            message = f"✅ {message}"
            color = "#2ecc71"  # Green
        else:
            # Regular info message
            color = "#3498db"  # Blue
            
        # Format the log message with timestamp
        formatted_msg = f"[{now}] {message}"
        
        # Add to log widget with appropriate color
        self.log_console.append(f'<span style="color: {color};">{formatted_msg}</span>')
        
        # Ensure the latest message is visible (scroll to bottom)
        self.log_console.verticalScrollBar().setValue(
            self.log_console.verticalScrollBar().maximum()
        )
        
        # Also print to console for debugging
        print(formatted_msg)

    # ---------------- HANDLERS ----------------
    def update_proxies(self, proxies):
        """Update proxy list"""
        self.active_proxies = proxies
        
        # Cập nhật trạng thái checkbox sử dụng proxy
        if hasattr(self, 'use_proxies_cb'):
            self.use_proxies_cb.setEnabled(len(proxies) > 0)
            self.use_proxies_cb.setChecked(len(proxies) > 0)
        
        self.log_message(f"Đã cập nhật danh sách proxy: {len(proxies)} proxy có sẵn")

    def start_automation(self):
        """
        Khởi động tiến trình automation
        """
        if self.worker and self.worker.isRunning():
            self.log_message("❌ Tiến trình đang chạy, không thể khởi động mới", "error")
            return
            
        # Clear previous results
        self.results_table.setRowCount(0)
        self.log_console.clear()
        self.progress.setValue(0)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.reset_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        current_tab = self.tabs.currentIndex()
        
        # Kiểm tra tùy chọn Chrome
        brave_path = self.settings.value("brave_path", "")
        brave_profile = self.settings.value("brave_profile", "")
        
        # Kiểm tra proxy
        proxy = None
        if hasattr(self, 'use_proxies_cb') and self.use_proxies_cb.isChecked() and self.active_proxies:
            import random
            proxy = random.choice(self.active_proxies)
            self.log_message(f"Đang sử dụng proxy: {proxy}", "info")
        
        self.log_message("Đang khởi động automation...", "info")
        self.start_time = time.time()
        
        # Thiết lập worker dựa trên tab hiện tại
        if current_tab == 0:  # Google tab
            keyword = self.google_keyword.text().strip() or "selenium python automation"
            headless = self.google_headless.isChecked()
            
            # Lưu cài đặt
            self.settings.setValue("google_keyword", keyword)
            self.settings.setValue("google_headless", headless)
            
            self.worker = EnhancedAutomationWorker(
                task="google",
                keyword=keyword,
                headless=headless,
                proxy=proxy,
                max_results=int(self.google_max_results.text() or 10),
                chrome_config={"chrome_path": brave_path, "profile_path": brave_profile}
            )
            
            # Chuẩn bị bảng kết quả
            self.results_table.setColumnCount(3)
            self.results_table.setHorizontalHeaderLabels(["STT", "Tiêu đề", "URL"])
        elif current_tab == 1:  # Facebook tab
            email = self.fb_email.text().strip()
            password = self.fb_password.text().strip()
            save_login = self.fb_save_login.isChecked()
            
            # Show informative message about manual login
            self.log_message("ℹ️ Facebook yêu cầu đăng nhập thủ công để tránh phát hiện automation", "info")
            self.log_message("⚠️ Khi trình duyệt mở ra, hãy đăng nhập vào tài khoản của bạn", "warning")
            self.log_message("📝 Hệ thống sẽ tự động phát hiện khi bạn đã đăng nhập thành công", "info")
            
            if save_login:
                self.settings.setValue("fb_email", email)
                self.settings.setValue("fb_password", password)
                self.settings.setValue("fb_save_login", save_login)
                
            self.worker = EnhancedAutomationWorker(
                task="facebook",
                email=email,
                password=password,
                proxy=proxy,
                headless=False,
                chrome_config={"chrome_path": brave_path, "profile_path": brave_profile}
            )
            self.results_table.setColumnCount(2)
            self.results_table.setHorizontalHeaderLabels(["Thông tin", "Giá trị"])
        elif current_tab == 2:
            keyword = self.sp_keyword.text().strip() or "điện thoại"
            pages = int(self.sp_pages.text().strip() or 2)
            headless = self.sp_headless.isChecked()
            self.settings.setValue("sp_keyword", keyword)
            self.settings.setValue("sp_pages", pages)
            self.settings.setValue("sp_headless", headless)
            self.worker = EnhancedAutomationWorker(
                task="shopee",
                keyword=keyword,
                proxy=proxy,
                headless=headless,
                pages=pages,
                chrome_config={"chrome_path": brave_path, "profile_path": brave_profile}
            )
            self.results_table.setColumnCount(4)
            self.results_table.setHorizontalHeaderLabels(["STT", "Tên sản phẩm", "Giá", "URL"])
        else:
            self.log_message("Tab chưa hỗ trợ.", "error")
            self.reset_automation()
            return

        self.worker.log_signal.connect(lambda m: self.log_message(m, "info"))
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(lambda status=True: self.on_worker_finished())
        self.worker.result_signal.connect(self.on_results)
        self.worker.error_signal.connect(lambda e: self.log_message(f"Lỗi: {e}", "error"))
        
        # Cập nhật danh sách proxy cho worker
        if hasattr(self, 'active_proxies') and self.active_proxies:
            self.worker.proxies = self.active_proxies
            
        self.worker.start()

    def stop_automation(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_message("Đã yêu cầu dừng automation.", "warning")
        else:
            self.log_message("Không có tiến trình nào đang chạy.")

    def on_worker_finished(self):
        """Handle worker thread finished"""
        self.log_message("✅ Task completed")
        
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        formatted_time = f"{int(elapsed_time)}s"
        
        # Determine task name and type
        task_name = "Unknown Task"
        task_type = "Unknown Type"
        
        if hasattr(self.worker, 'task'):
            task = self.worker.task
            if task == "google":
                task_name = "Google Search"
                task_type = "Search"
            elif task == "facebook":
                task_name = "Facebook Login"
                task_type = "Authentication"
            elif task == "shopee":
                task_name = "Shopee Scraping"
                task_type = "Data Collection"
            elif task == "google_trends":
                task_name = "Google Trends"
                task_type = "Data Collection"
            elif task == "facebook_trends":
                task_name = "Facebook Trends"
                task_type = "Data Collection"
            elif task == "content_creation":
                task_name = "Content Creation"
                task_type = "Content Creation"
            elif task == "post_content":
                task_name = "Facebook Posting"
                task_type = "Social Media"
            elif task == "schedule_post":
                task_name = "Post Scheduling"
                task_type = "Social Media"
            
        # Create a result object
        result = {
            "task_name": task_name,
            "task_type": task_type,
            "status": "Completed",
            "elapsed_time": formatted_time
        }
        
        # Send to any connected signals
        self.task_completed.emit(result)
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setValue(100)
        
    def on_finished(self, status=None):
        """
        Legacy method for backward compatibility
        Redirects to on_worker_finished
        """
        self.on_worker_finished()

    def reset_automation(self):
        self.log_console.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.reset_btn.setEnabled(True)
        self.export_btn.setEnabled(False)
        self.log_message("Đã làm mới giao diện.", "info")

    def on_results(self, results):
        """Handle worker results"""
        self.log_message(f"✅ Task completed with results: {results}")
        
        # Format the results for display
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, list) and len(value) > 0:
                    self.log_message(f"- {key}: Found {len(value)} items")
                else:
                    self.log_message(f"- {key}: {value}")
                    
        # Update UI for completed task
        self.reset_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
                    
        # Pass results to any connected signal
        self.task_completed.emit(results)

    def export_results(self):
        if self.results_table.rowCount() == 0:
            self.log_message("Không có dữ liệu để xuất.", "warning")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Lưu kết quả", "", "CSV Files (*.csv)")
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                headers = [self.results_table.horizontalHeaderItem(i).text() for i in range(self.results_table.columnCount())]
                f.write(','.join(headers) + '\n')
                for row in range(self.results_table.rowCount()):
                    row_data = [self.results_table.item(row, col).text() for col in range(self.results_table.columnCount())]
                    f.write(','.join(row_data) + '\n')
            self.log_message(f"Đã xuất kết quả ra {file_name}", "success")

    def run_google_trends(self, country="vietnam", category=None, timeframe="now 1-d"):
        """Run Google Trends task"""
        self.start_time = time.time()
        self.log_message("🔎 Bắt đầu lấy xu hướng từ Google Trends...", "info")
        
        # Setup worker and run
        worker = self.setup_worker(
            "google_trends", 
            country=country,
            category=category,
            timeframe=timeframe
        )
        
        # Start worker thread
        if worker:
            worker.start()
            return True
        return False
        
    def run_facebook_trends(self):
        """Run Facebook Trending Topics task"""
        self.start_time = time.time()
        self.log_message("🔎 Bắt đầu lấy xu hướng từ Facebook...", "info")
        
        # Setup worker and run
        worker = self.setup_worker("facebook_trends")
        
        # Start worker thread
        if worker:
            worker.start()
            return True
        return False

    def run_content_creation(self, trend_data, content_type="article"):
        """Run content creation task"""
        self.start_time = time.time()
        self.log_message(f"📝 Bắt đầu tạo nội dung từ xu hướng: {trend_data.get('keyword', 'Unknown')}", "info")
        
        # Setup worker
        worker = self.setup_worker(
            "content_creation"
        )
        
        # Set parameters after worker initialization
        if worker:
            worker.trend = trend_data
            worker.content_type = content_type
            worker.word_count = 500
            
            # Start worker thread
            worker.start()
            return True
        return False
        
    def run_post_content(self, content_data, post_type="personal", page_id=None, group_id=None):
        """Run post content task"""
        self.start_time = time.time()
        self.log_message(f"📤 Bắt đầu đăng nội dung lên {post_type}", "info")
        
        # Show informative message about manual login
        self.log_message("ℹ️ Facebook yêu cầu đăng nhập thủ công để tránh phát hiện automation", "info")
        self.log_message("⚠️ Khi trình duyệt mở ra, hãy đăng nhập vào tài khoản của bạn", "warning")
        self.log_message("📝 Hệ thống sẽ tự động phát hiện khi bạn đã đăng nhập thành công", "info")
        
        # Setup worker
        worker = self.setup_worker(
            "post_content"
        )
        
        # Set parameters after worker initialization
        if worker:
            worker.content = content_data
            worker.post_type = post_type
            worker.page_id = page_id
            worker.group_id = group_id
            
            # Start worker thread
            worker.start()
            return True
        return False

    def run_schedule_post(self, content_data, schedule_time, post_type="personal", page_id=None, group_id=None):
        """Run schedule post task"""
        self.start_time = time.time()
        self.log_message(f"📅 Bắt đầu lập lịch đăng bài cho: {schedule_time.strftime('%d/%m/%Y %H:%M')}", "info")
        
        # Show informative message about manual login
        self.log_message("ℹ️ Facebook yêu cầu đăng nhập thủ công để tránh phát hiện automation", "info")
        self.log_message("⚠️ Khi trình duyệt mở ra, hãy đăng nhập vào tài khoản của bạn", "warning")
        self.log_message("📝 Hệ thống sẽ tự động phát hiện khi bạn đã đăng nhập thành công", "info")
        
        # Setup worker
        worker = self.setup_worker(
            "schedule_post"
        )
        
        # Set parameters after worker initialization
        if worker:
            worker.content = content_data
            worker.schedule_time = schedule_time
            worker.post_type = post_type
            worker.page_id = page_id
            worker.group_id = group_id
            
            # Start worker thread
            worker.start()
            return True
        return False

    def setup_worker(self, task, **kwargs):
        """Setup worker thread with task and parameters"""
        self.log_message(f"Setting up worker for task: {task}")
        
        # Create new worker
        brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        brave_profile = r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default"
        
        # Determine if we should use a proxy
        proxy = None
        if hasattr(self, 'active_proxies') and self.active_proxies and hasattr(self, 'use_proxies_cb') and self.use_proxies_cb.isChecked():
            import random
            proxy = random.choice(self.active_proxies)
            self.log_message(f"Sử dụng proxy: {proxy}")
        
        # Set headless mode based on current tab or default to False
        headless = False
        if task == "google" or task == "google_trends":
            headless = self.google_headless.isChecked() if hasattr(self, 'google_headless') else False
        elif task == "shopee":
            headless = self.sp_headless.isChecked() if hasattr(self, 'sp_headless') else False
        
        # Create enhanced worker with proper configuration
        self.worker = EnhancedAutomationWorker(
            task=task,
            proxy=proxy,
            headless=headless,
            delay=1.5,  # Reasonable default
            chrome_config={"chrome_path": brave_path, "profile_path": brave_profile}
        )
        
        # Set specific properties based on task
        if task == "google":
            self.worker.keyword = kwargs.get('keyword', self.google_keyword.text() if hasattr(self, 'google_keyword') else '')
            self.worker.max_results = int(self.google_max_results.text()) if hasattr(self, 'google_max_results') and self.google_max_results.text() else 10
        elif task == "facebook":
            self.worker.email = kwargs.get('email', self.fb_email.text() if hasattr(self, 'fb_email') else '')
            self.worker.password = kwargs.get('password', self.fb_password.text() if hasattr(self, 'fb_password') else '')
        elif task == "shopee":
            self.worker.keyword = kwargs.get('keyword', self.sp_keyword.text() if hasattr(self, 'sp_keyword') else '')
            self.worker.pages = kwargs.get('pages', int(self.sp_pages.text()) if hasattr(self, 'sp_pages') and self.sp_pages.text() else 3)
        elif task == "google_trends":
            self.worker.country = kwargs.get('country', 'vietnam')
            self.worker.category = kwargs.get('category', None)
            self.worker.timeframe = kwargs.get('timeframe', 'now 1-d')
        elif task == "facebook_trends":
            # No specific parameters needed
            pass
        elif task == "content_creation":
            self.worker.trend = kwargs.get('trend', {})
            self.worker.content_type = kwargs.get('content_type', 'article')
            self.worker.word_count = kwargs.get('word_count', 500)
        elif task == "post_content":
            self.worker.content = kwargs.get('content', {})
            self.worker.post_type = kwargs.get('post_type', 'personal')
            self.worker.page_id = kwargs.get('page_id', None)
            self.worker.group_id = kwargs.get('group_id', None)
        elif task == "schedule_post":
            self.worker.content = kwargs.get('content', {})
            self.worker.schedule_time = kwargs.get('schedule_time', None)
            self.worker.post_type = kwargs.get('post_type', 'personal')
            self.worker.page_id = kwargs.get('page_id', None)
            self.worker.group_id = kwargs.get('group_id', None)
        elif task == "custom":
            self.worker.custom_script = kwargs.get('custom_script', '')
            self.worker.custom_script_args = kwargs.get('custom_script_args', {})
            
        # Set proxy list for rotation if needed
        if hasattr(self, 'active_proxies') and self.active_proxies:
            self.worker.proxies = self.active_proxies
            
        # Connect common signals
        self.worker.log_signal.connect(self.log_message)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.error_signal.connect(lambda e: self.log_message(f"❌ Error: {e}", "error"))
        
        # Connect task completion signal
        if task == "google_trends" or task == "facebook_trends":
            if hasattr(self.worker, 'trends_signal'):
                self.worker.trends_signal.connect(self.on_trends_received)
        elif task == "content_creation":
            if hasattr(self.worker, 'content_signal'):
                self.worker.content_signal.connect(self.on_content_created)
        elif task == "post_content" or task == "schedule_post":
            if hasattr(self.worker, 'post_result_signal'):
                self.worker.post_result_signal.connect(self.on_post_completed)
        
        # General result signal
        self.worker.result_signal.connect(self.on_results)
        self.worker.finished_signal.connect(lambda status="Completed": self.on_worker_finished())
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.log_message(f"🚀 Starting task: {task}")
        
        return self.worker
        
    def on_trends_received(self, trends):
        """Handle received trends data"""
        source = "google" if trends and isinstance(trends, list) and trends and trends[0].get('source') == 'Google Trends' else "facebook"
        self.log_message(f"✅ Received {len(trends)} trends from {source}")
        
        # Create a complete result object to pass up to the main window
        result = {
            "task_name": f"{source.capitalize()} Trends",
            "task_type": "Data Collection",
            "status": "Hoàn thành",
            "elapsed_time": f"{int(time.time() - self.start_time)}s",
            "result": f"{len(trends)} xu hướng",
            "trends": trends,
            "source": source
        }
        
        self.task_completed.emit(result)
        
    def on_content_created(self, content):
        """Handle created content"""
        self.log_message(f"✅ Content created with title: {content.get('title', 'Untitled')}")
        
        # Create a complete result object
        result = {
            "task_name": "Tạo nội dung",
            "task_type": "Content Creation",
            "status": "Hoàn thành",
            "elapsed_time": f"{int(time.time() - self.start_time)}s",
            "result": f"Nội dung: {content.get('title', 'Untitled')}",
            "content": content
        }
        
        self.task_completed.emit(result)
        
    def on_post_completed(self, result):
        """Handle post completion"""
        task_type = self.worker.task if hasattr(self.worker, 'task') else "post_content"
        
        if task_type == "post_content":
            status = "Hoàn thành" if result else "Thất bại"
            task_name = "Đăng nội dung"
            success_msg = "Đã đăng thành công" if result else "Đăng không thành công"
        else:  # schedule_post
            status = "Hoàn thành" if result else "Thất bại"
            task_name = "Lên lịch đăng bài"
            success_msg = "Đã lên lịch thành công" if result else "Lên lịch không thành công"
        
        # Create a complete result object
        result_obj = {
            "task_name": task_name,
            "task_type": "Social Media",
            "status": status,
            "elapsed_time": f"{int(time.time() - self.start_time)}s",
            "result": success_msg,
            "success": result
        }
        
        # Log appropriate message
        if result:
            self.log_message(f"✅ {task_name}: {success_msg}", "success")
        else:
            self.log_message(f"❌ {task_name}: {success_msg}", "error")
            self.log_message("💡 Lưu ý: Facebook yêu cầu đăng nhập thủ công để đăng bài. Hãy đảm bảo bạn đã đăng nhập khi trình duyệt mở ra.", "info")
        
        self.task_completed.emit(result_obj)
        
    def on_schedule_completed(self, result):
        """Use on_post_completed instead which now handles both post_content and schedule_post"""
        # This method is deprecated
        self.on_post_completed(result)

    def is_running(self):
        """Kiểm tra worker đang chạy"""
        return self.worker is not None and hasattr(self.worker, 'isRunning') and self.worker.isRunning()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress.setValue(value)

    def update_results(self, results):
        """Update results table with data from worker"""
        # Skip if not a list or dict
        if not isinstance(results, (list, dict)):
            return

        # Handle different result types
        if isinstance(results, list):
            items = results
            self.results_table.setRowCount(len(items))
            
            # Determine current tab
            current_tab = self.tabs.currentIndex()
            
            if current_tab == 0:  # Google
                self.results_table.setColumnCount(3)
                self.results_table.setHorizontalHeaderLabels(["STT", "Tiêu đề", "URL"])
                for i, item in enumerate(items):
                    if isinstance(item, tuple) and len(item) >= 2:
                        title, url = item[0], item[1]
                        self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                        self.results_table.setItem(i, 1, QTableWidgetItem(title))
                        self.results_table.setItem(i, 2, QTableWidgetItem(url))
            elif current_tab == 2:  # Shopee
                self.results_table.setColumnCount(4)
                self.results_table.setHorizontalHeaderLabels(["STT", "Tên sản phẩm", "Giá", "URL"])
                for i, item in enumerate(items):
                    if isinstance(item, tuple) and len(item) >= 3:
                        name, price, url = item[0], item[1], item[2]
                        self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                        self.results_table.setItem(i, 1, QTableWidgetItem(name))
                        self.results_table.setItem(i, 2, QTableWidgetItem(price))
                        self.results_table.setItem(i, 3, QTableWidgetItem(url))
        
        elif isinstance(results, dict):
            # Display dict items as key-value pairs
            items = list(results.items())
            self.results_table.setRowCount(len(items))
            self.results_table.setColumnCount(2)
            self.results_table.setHorizontalHeaderLabels(["Thông tin", "Giá trị"])
            
            for i, (key, value) in enumerate(items):
                # Convert value to string if needed
                if isinstance(value, (list, dict)):
                    value_str = f"{len(value)} items"
                else:
                    value_str = str(value)
                
                self.results_table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.results_table.setItem(i, 1, QTableWidgetItem(value_str))
        
        # Enable export button if we have results
        if (isinstance(results, list) and len(results) > 0) or (isinstance(results, dict) and len(results) > 0):
            self.export_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationView()
    window.setWindowTitle("Selenium Automation Hub (Brave)")
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())
# modules/main_window.py

import os
import sys
import json
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QMenu, QMenuBar,
    QProgressBar, QAction, QMessageBox, QHBoxLayout, QLabel, QPushButton, QFrame, QApplication,
    QStatusBar, QToolBar, QFileDialog, QDialog, QTabWidget, QDateTimeEdit
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSettings, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QPixmap
import subprocess
import importlib
import traceback
import psutil
from datetime import timedelta
import logging

# Import các module UI con (đảm bảo các module này tồn tại trong thư mục modules)
from .splash_screen import SplashScreen
from .settings_dialog import SettingsDialog
from .dashboard import DashboardWidget
from .automation_view import AutomationView

# Điều chỉnh tên các module dựa trên tên file thực tế
try:
    from .data_view import DataWidget
except ImportError:
    print("Warning: data_view module not found")
    DataWidget = QWidget  # Fallback

try:
    from .logs_view import LogsWidget
except ImportError:
    print("Warning: logs_view module not found")
    LogsWidget = QWidget  # Fallback

try:
    from .script_manager import ScriptManagerWidget
except ImportError:
    print("Warning: script_manager module not found")
    ScriptManagerWidget = QWidget  # Fallback

try:
    from .proxy_manager import ProxyManagerWidget
except ImportError:
    print("Warning: proxy_manager module not found")
    ProxyManagerWidget = QWidget  # Fallback

try:
    from .task_scheduler import TaskSchedulerWidget
except ImportError:
    print("Warning: task_scheduler module not found")
    TaskSchedulerWidget = QWidget  # Fallback

try:
    from .captcha_resolver import CaptchaResolver
except ImportError:
    print("Warning: captcha_resolver module not found")

try:
    from .script_builder import ScriptBuilder
except ImportError:
    print("Warning: script_builder module not found")

# Tạo logger thay vì import
logger = logging.getLogger(__name__)

# Import config, utils
from .config import APP_TITLE, APP_ICON, APP_WIDTH, APP_HEIGHT, THEMES, DEFAULT_THEME, APP_VERSION
from .utils import setup_logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(50, 50, APP_WIDTH, APP_HEIGHT)
        self.setWindowIcon(QIcon(APP_ICON))
        # Khởi tạo QSettings để lưu trạng thái theme
        self.settings = QSettings("MyCompany", "MyApp")
        self.current_theme = self.settings.value("theme", "Light")
        
        self.init_logging()
        self.init_ui()
        self.init_menu()
        self.apply_theme()
        self.init_splash_screen()
        self.init_statusbar()
        self.connect_signals()

        self.log("Ứng dụng khởi động.")
        # Cập nhật theme mặc định nếu cần
        self.current_theme = DEFAULT_THEME
        self.load_icons()

    def init_logging(self):
        setup_logging()

    def init_ui(self):
        # Main container widget sử dụng layout dọc
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Stacked widget chứa các trang
        self.stacked_widget = QStackedWidget()
        
        # Khởi tạo các widget cho từng tab
        self.dashboard_page = DashboardWidget()       # index 0
        self.automation_page = AutomationView()     # index 1
        self.data_page = DataWidget()                # index 2
        self.logs_page = LogsWidget()                # index 3
        self.script_manager_page = ScriptManagerWidget()   # index 4
        self.proxy_manager_page = ProxyManagerWidget()      # index 5
        self.task_scheduler_page = TaskSchedulerWidget()    # index 6
        
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.automation_page)
        self.stacked_widget.addWidget(self.data_page)
        self.stacked_widget.addWidget(self.logs_page)
        self.stacked_widget.addWidget(self.script_manager_page)
        self.stacked_widget.addWidget(self.proxy_manager_page)
        self.stacked_widget.addWidget(self.task_scheduler_page)
        
        layout.addWidget(self.stacked_widget)
        
        # Progress bar nằm dưới cùng
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def init_menu(self):
        menubar = self.menuBar()

        # Menu Tệp
        file_menu = menubar.addMenu("Tệp")
        
        # Menu Xem
        view_menu = menubar.addMenu("Xem")
        
        # Dashboard action
        dashboard_action = QAction(QIcon("resources/icons/dashboard.png"), "Dashboard", self)
        dashboard_action.setObjectName("dashboard_action")
        dashboard_action.triggered.connect(lambda: self.switch_page(0))
        view_menu.addAction(dashboard_action)
        
        # Automation action
        automation_action = QAction(QIcon("resources/icons/automation.png"), "Automation", self)
        automation_action.setObjectName("automation_action")
        automation_action.triggered.connect(lambda: self.switch_page(1))
        view_menu.addAction(automation_action)
        
        # Data action
        data_action = QAction(QIcon("resources/icons/data.png"), "Dữ liệu", self)
        data_action.setObjectName("data_action")
        data_action.triggered.connect(lambda: self.switch_page(2))
        view_menu.addAction(data_action)
        
        # Logs action
        logs_action = QAction(QIcon("resources/icons/logs.png"), "Logs", self)
        logs_action.setObjectName("logs_action")
        logs_action.triggered.connect(lambda: self.switch_page(3))
        view_menu.addAction(logs_action)
        
        # Script Manager action
        script_manager_action = QAction(QIcon("resources/icons/script.png"), "Quản lý Script", self)
        script_manager_action.setObjectName("script_manager_action")
        script_manager_action.triggered.connect(lambda: self.switch_page(4))
        view_menu.addAction(script_manager_action)
        
        # Proxy Manager action
        proxy_manager_action = QAction(QIcon("resources/icons/proxy.png"), "Quản lý Proxy", self)
        proxy_manager_action.setObjectName("proxy_manager_action")
        proxy_manager_action.triggered.connect(self.open_proxy_manager)
        view_menu.addAction(proxy_manager_action)
        
        # Task Scheduler action
        task_scheduler_action = QAction(QIcon("resources/icons/schedule.png"), "Lập lịch Task", self)
        task_scheduler_action.setObjectName("task_scheduler_action")
        task_scheduler_action.triggered.connect(self.open_scheduler)
        view_menu.addAction(task_scheduler_action)
        
        # Lưu các action vào thuộc tính của lớp
        self.nav_dashboard = dashboard_action
        self.nav_automation = automation_action
        self.nav_data = data_action
        self.nav_logs = logs_action
        self.action_script_manager = script_manager_action
        self.action_proxy_manager = proxy_manager_action
        self.action_task_scheduler = task_scheduler_action
        
        # Menu Công cụ
        tools_menu = menubar.addMenu("Công cụ")
        
        # Script Builder action
        script_builder_action = QAction(QIcon("resources/icons/builder.png"), "Script Builder", self)
        script_builder_action.triggered.connect(self.open_script_builder)
        tools_menu.addAction(script_builder_action)
        
        # Captcha Resolver action
        captcha_resolver_action = QAction(QIcon("resources/icons/captcha.png"), "Captcha Resolver", self)
        captcha_resolver_action.triggered.connect(self.open_captcha_resolver)
        tools_menu.addAction(captcha_resolver_action)
        
        # Menu Cài đặt
        settings_menu = menubar.addMenu("Cài đặt")
        
        # Preferences action
        preferences_action = QAction(QIcon("resources/icons/settings.png"), "Tùy chỉnh", self)
        preferences_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(preferences_action)
        
        # Toggle Theme action
        toggle_theme_action = QAction(QIcon("resources/icons/theme.png"), "Chuyển đổi Theme", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(toggle_theme_action)
        
        # Menu Trợ giúp
        help_menu = menubar.addMenu("Trợ giúp")
        
        # About action
        about_action = QAction(QIcon("resources/icons/about.png"), "Giới thiệu", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Exit action
        exit_action = QAction(QIcon("resources/icons/exit.png"), "Thoát", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def apply_theme(self, theme_name=None):
        """Áp dụng theme theo giá trị theme được cung cấp hoặc mặc định"""
        if theme_name:
            current_theme = theme_name
        else:
            current_theme = DEFAULT_THEME
        
        theme = THEMES.get(current_theme, THEMES["Dark"])
        
        # Áp dụng màu sắc chính
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(theme["bg_primary"]))
        palette.setColor(QPalette.WindowText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Base, QColor(theme["bg_secondary"]))
        palette.setColor(QPalette.AlternateBase, QColor(theme["bg_primary"]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme["text_primary"]))
        palette.setColor(QPalette.ToolTipText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Text, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Button, QColor(theme["accent"]))
        palette.setColor(QPalette.ButtonText, QColor("white"))
        palette.setColor(QPalette.BrightText, QColor("white"))
        palette.setColor(QPalette.Highlight, QColor(theme["accent"]))
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        palette.setColor(QPalette.Light, QColor(theme["text_primary"]).lighter(120))
        palette.setColor(QPalette.Midlight, QColor(theme["text_primary"]).lighter(110))
        palette.setColor(QPalette.Mid, QColor(theme["border"]))
        palette.setColor(QPalette.Dark, QColor(theme["bg_primary"]).darker(120))
        palette.setColor(QPalette.Shadow, QColor(theme["bg_primary"]).darker(130))
        palette.setColor(QPalette.Link, QColor(theme["accent"]))
        palette.setColor(QPalette.LinkVisited, QColor(theme["accent_hover"]))
        
        self.setPalette(palette)
        
        additional_style = f"""
            QTabWidget::pane {{ 
                border: 1px solid {theme["border"]}; 
                background-color: {theme["bg_secondary"]};
            }}
            QTableWidget, QTreeWidget {{ 
                alternate-background-color: {theme["bg_primary"]};
                gridline-color: {theme["border"]};
            }}
            QHeaderView::section {{
                background-color: {theme["bg_primary"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["border"]};
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme["accent"]};
                color: white;
                border: 1px solid {theme["accent_hover"]};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme["accent_hover"]};
            }}
            QLineEdit, QTextEdit {{
                border: 1px solid {theme["border"]};
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
                selection-background-color: {theme["accent"]};
                selection-color: white;
                padding: 5px;
            }}
            QComboBox {{
                border: 1px solid {theme["border"]};
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
                padding: 5px;
            }}
            QCheckBox, QRadioButton {{
                color: {theme["text_primary"]};
            }}
        """
        
        sidebar_style = f"""
            QPushButton[nav=true] {{
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 0;
                background-color: {theme["bg_primary"]};
                color: {theme["text_primary"]};
                font-weight: bold;
            }}
            QPushButton[nav=true]:hover {{
                background-color: {theme["bg_secondary"]};
            }}
            QPushButton[nav=true]:checked {{
                background-color: {theme["accent"]};
                color: white;
            }}
        """
        
        self.setStyleSheet(additional_style + sidebar_style)

    def init_splash_screen(self):
        splash = SplashScreen()
        splash.show()
        # Xử lý events để đảm bảo splash hiển thị
        for _ in range(5):
            QApplication.processEvents()
        QTimer.singleShot(1500, splash.close)

    def log(self, message):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        print(f"[{now}] {message}")

    def open_settings_dialog(self):
        dlg = SettingsDialog(self)
        if dlg.exec_() == dlg.Accepted:
            self.log("Đã cập nhật cài đặt.")

    def show_about(self):
        QMessageBox.information(self, "Thông tin", f"Selenium Automation Hub\nNhóm 7 - Hào TN\nPhiên bản {APP_VERSION}")

    def switch_page(self, index: int):
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            self.log(f"Chuyển sang trang {index}")

    def closeEvent(self, event):
        event.accept()

    def open_script_builder(self):
        """Mở Script Builder"""
        try:
            from .script_builder import ScriptBuilderWidget
            dialog = ScriptBuilderWidget(self)
            dialog.script_saved.connect(self.on_script_saved)
            dialog.exec_()
        except Exception as e:
            self.log(f"Error opening script builder: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not open script builder: {str(e)}")

    def open_captcha_resolver(self):
        """Mở Captcha Resolver"""
        try:
            from .captcha_resolver import CaptchaResolverWidget
            dialog = CaptchaResolverWidget(self)
            dialog.exec_()
        except Exception as e:
            self.log(f"Error opening captcha resolver: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not open captcha resolver: {str(e)}")

    def on_script_saved(self, script_name, script_content):
        self.log(f"Script saved: {script_name}")
        if hasattr(self, 'script_manager_page') and hasattr(self.script_manager_page, 'refresh_list'):
            self.script_manager_page.refresh_list()
        self.switch_page(4)

    def open_scheduler(self):
        self.switch_page(6)

    def open_proxy_manager(self):
        self.switch_page(5)

    def on_proxies_updated(self, proxy_list):
        """Handle updated proxies from proxy manager"""
        try:
            # Update proxies in automation page
            if hasattr(self.automation_page, 'update_proxies'):
                self.automation_page.update_proxies(proxy_list)
                self.log(f"✅ Updated {len(proxy_list)} proxies in automation page")
        except Exception as e:
            self.log(f"❌ Error updating proxies: {str(e)}")

    def on_scheduled_task_ready(self, task_id, script_path):
        self.log(f"Task đã đến lịch chạy: {task_id}")
        try:
            from importlib.machinery import SourceFileLoader
            module = SourceFileLoader("script", script_path).load_module()
            if hasattr(module, "run"):
                self.log(f"Bắt đầu chạy script: {script_path}")
                import threading
                thread = threading.Thread(target=module.run, args=(self,))
                thread.daemon = True
                thread.start()
            else:
                self.log(f"Lỗi: Script không có hàm run(): {script_path}")
        except Exception as e:
            self.log(f"Lỗi khi chạy script theo lịch: {str(e)}")

    def connect_signals(self):
        """Connect all UI signals and worker signals"""
        # Tạo thuộc tính để lưu các action menu nếu chưa tồn tại
        if not hasattr(self, 'nav_dashboard'):
            # Sử dụng self.findChild để tìm các action đã tạo
            self.nav_dashboard = self.findChild(QAction, "dashboard_action")
            self.nav_automation = self.findChild(QAction, "automation_action")
            self.nav_data = self.findChild(QAction, "data_action")
            self.nav_logs = self.findChild(QAction, "logs_action")
            
            # Nếu không tìm thấy, có thể là action chưa được đặt tên, bỏ qua và log lỗi
            if not self.nav_dashboard:
                self.log("Cảnh báo: Không tìm thấy action nav_dashboard, bỏ qua kết nối tín hiệu.")
                return
        
        # Nav actions - chỉ kết nối nếu action tồn tại
        if hasattr(self, 'nav_dashboard') and self.nav_dashboard:
            self.nav_dashboard.triggered.connect(lambda: self.switch_page(0))
        if hasattr(self, 'nav_automation') and self.nav_automation:
            self.nav_automation.triggered.connect(lambda: self.switch_page(1))
        if hasattr(self, 'nav_data') and self.nav_data:
            self.nav_data.triggered.connect(lambda: self.switch_page(2))
        if hasattr(self, 'nav_logs') and self.nav_logs:
            self.nav_logs.triggered.connect(lambda: self.switch_page(3))
        
        # Menu actions
        if hasattr(self, 'action_settings'):
            self.action_settings.triggered.connect(self.open_settings_dialog)
        if hasattr(self, 'action_about'):
            self.action_about.triggered.connect(self.show_about)
        if hasattr(self, 'action_exit'):
            self.action_exit.triggered.connect(self.close)
        if hasattr(self, 'action_theme'):
            self.action_theme.triggered.connect(self.toggle_theme)
        if hasattr(self, 'action_script_builder'):
            self.action_script_builder.triggered.connect(self.open_script_builder)
        if hasattr(self, 'action_captcha_resolver'):
            self.action_captcha_resolver.triggered.connect(self.open_captcha_resolver)
        if hasattr(self, 'action_task_scheduler'):
            self.action_task_scheduler.triggered.connect(self.open_scheduler)
        if hasattr(self, 'action_proxy_manager'):
            self.action_proxy_manager.triggered.connect(self.open_proxy_manager)
        
        # Task scheduler signals
        if hasattr(self, 'task_scheduler_page'):
            self.task_scheduler_page.task_ready.connect(self.on_scheduled_task_ready)
        
        # Script builder signals
        if hasattr(self, 'script_builder'):
            self.script_builder.script_completed_signal.connect(self.on_script_builder_completed)
            
        # Connect automation page signals
        if hasattr(self, 'automation_page'):
            self.automation_page.task_completed.connect(self.on_task_completed)
            
        # Connect dashboard signals to automation
        if hasattr(self, 'dashboard_page') and hasattr(self, 'automation_page'):
            # Connect dashboard get_trends signal to automation methods
            self.dashboard_page.get_trends_signal.connect(self.on_get_trends_requested)
            
            # Connect dashboard create_content signal to automation
            self.dashboard_page.create_content_signal.connect(self.on_create_content_requested)
            
            # Connect dashboard post_content signal to automation
            self.dashboard_page.post_content_signal.connect(self.on_post_content_requested)
            
            # Connect dashboard navigate_signal to switch_page
            if hasattr(self.dashboard_page, 'navigate_signal'):
                self.dashboard_page.navigate_signal.connect(self.switch_page)
        
        # Connect refresh buttons
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.clicked.connect(self.refresh_all_data)

    def init_statusbar(self):
        self.statusBar().showMessage("Sẵn sàng")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 10, 0)
        
        self.theme_toggle = QPushButton()
        self.theme_toggle.setToolTip("Chuyển đổi chế độ sáng/tối")
        self.theme_toggle.setFixedSize(24, 24)
        self.theme_toggle.setIcon(QIcon("resources/icons/theme.png"))
        self.theme_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        self.theme_toggle.clicked.connect(self.toggle_theme)
        
        version_label = QLabel(f"v{APP_VERSION}")
        status_layout.addStretch()
        status_layout.addWidget(self.theme_toggle)
        status_layout.addWidget(version_label)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        self.statusBar().addPermanentWidget(status_widget)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        # Switch theme
        if self.current_theme == "Dark":
            self.current_theme = "Light"
        else:
            self.current_theme = "Dark"
            
        # Save setting and apply
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme(self.current_theme)
        
        # Notify components about theme change
        if hasattr(self, 'automation_page'):
            settings = QSettings("MyApp", "AutomationWidget")
            settings.setValue("theme", self.current_theme)
            if hasattr(self.automation_page, 'setup_styles'):
                self.automation_page.setup_styles()
                
        if hasattr(self, 'dashboard_page'):
            # Refresh dashboard to apply new theme
            if hasattr(self.dashboard_page, 'refresh_data'):
                self.dashboard_page.refresh_data()
                
        # Reload icons for current theme
        self.load_icons()
        
        # Log theme change
        self.log(f"Đã chuyển sang chế độ {self.current_theme}")

    def load_icons(self):
        theme_suffix = "dark" if self.current_theme == "Light" else "light"
        self.icons = {
            "dashboard": QIcon(f"resources/icons/dashboard_{theme_suffix}.png"),
            "automation": QIcon(f"resources/icons/automation_{theme_suffix}.png"),
            "data": QIcon(f"resources/icons/data_{theme_suffix}.png"),
            "logs": QIcon(f"resources/icons/logs_{theme_suffix}.png"),
            "scripts": QIcon(f"resources/icons/scripts_{theme_suffix}.png"),
            "settings": QIcon(f"resources/icons/settings_{theme_suffix}.png"),
            "theme": QIcon(f"resources/icons/theme_{theme_suffix}.png")
        }
        self.update_ui_icons()

    def update_ui_icons(self):
        # Initialize nav_actions if it doesn't exist
        if not hasattr(self, 'nav_actions'):
            self.nav_actions = []
            # Find all QAction objects in the menu bar
            for menu in self.menuBar().findChildren(QMenu):
                for action in menu.actions():
                    if action.icon() and not action.icon().isNull():
                        self.nav_actions.append(action)
                        # Try to determine the action type from its text
                        for key in self.icons.keys():
                            if key in action.text().lower():
                                action.setData(key)
        
        # Update icons for all actions in nav_actions
        for action in self.nav_actions:
            data = action.data()
            if data and data in self.icons:
                action.setIcon(self.icons[data])
        
        # Update theme toggle button icon
        if hasattr(self, 'theme_toggle'):
            self.theme_toggle.setIcon(self.icons.get("theme", QIcon()))

    def on_script_selected(self, script_path):
        """Handle script selection from script manager"""
        try:
            self.log(f"✅ Script selected: {os.path.basename(script_path)}")
            # You can add additional handling here if needed
        except Exception as e:
            self.log(f"❌ Error handling script selection: {str(e)}")

    def run_script(self, script_path):
        self.log(f"Running script: {script_path}")
        self.switch_page(1)
        if hasattr(self.automation_page, 'run_custom_script'):
            self.automation_page.run_custom_script(script_path)

    def refresh_all_data(self):
        self.log("Refreshing all data...")
        if hasattr(self.dashboard_page, 'update_stats'):
            self.dashboard_page.update_stats()
        if hasattr(self.data_page, 'refresh_data'):
            self.data_page.refresh_data()
        if hasattr(self.script_manager_page, 'refresh_list'):
            self.script_manager_page.refresh_list()
        if hasattr(self.proxy_manager_page, 'refresh_proxies'):
            self.proxy_manager_page.refresh_proxies()
        if hasattr(self.task_scheduler_page, 'refresh_tasks'):
            self.task_scheduler_page.refresh_tasks()
        self.log("Data refresh complete")

    def refresh_dashboard(self):
        self.log("Refreshing dashboard data...")
        if hasattr(self.dashboard_page, 'update_stats'):
            self.dashboard_page.update_stats()
        try:
            if hasattr(self.dashboard_page, 'cpu_progress') and hasattr(self.dashboard_page, 'memory_progress'):
                self.dashboard_page.cpu_progress.setValue(int(psutil.cpu_percent()))
                self.dashboard_page.memory_progress.setValue(int(psutil.virtual_memory().percent))
        except Exception as e:
            self.log(f"Error updating system stats: {str(e)}")
        self.log("Dashboard refreshed")

    def on_task_completed(self, result):
        """Handle task completion from automation page"""
        try:
            self.log(f"✅ Task completed with result: {result}")
            
            if isinstance(result, dict):
                # Update dashboard with result
                if "task_name" in result:
                    task_name = result["task_name"]
                    task_type = result.get("task_type", "Unknown")
                    elapsed_time = result.get("elapsed_time", "0s")
                    status = result.get("status", "Completed")
                    result_text = result.get("result", "")
                    
                    # Update task history in dashboard
                    if hasattr(self, 'dashboard_page'):
                        self.dashboard_page.update_recent_task(
                            task_name, task_type, elapsed_time, status, result_text
                        )
                        
                    # If task was trend-related, update dashboard trends
                    if "trends" in result and hasattr(self, 'dashboard_page'):
                        trends = result.get("trends", [])
                        source = result.get("source", "google")
                        self.dashboard_page.add_trending_topics(trends, source)
                    
                    # If task was content creation, update dashboard content
                    if "content" in result and hasattr(self, 'dashboard_page'):
                        content = result.get("content", {})
                        self.dashboard_page.display_content(content)
                        
                # Update stats
                stats = {}
                if "total_tasks" in result:
                    stats["task_count"] = result["total_tasks"]
                if "success_rate" in result:
                    stats["success_rate"] = result["success_rate"]
                if "proxy_count" in result:
                    stats["active_proxies"] = result["proxy_count"]
                if "script_count" in result:
                    stats["script_count"] = result["script_count"]
                    
                if stats and hasattr(self, 'dashboard_page'):
                    self.dashboard_page.update_stat_cards(stats)
            
            elif isinstance(result, str):
                # Log the result as a message
                self.log(f"Task result: {result}")
                
            # Update task stats and dashboard
            self.refresh_dashboard()
            
            # Complete progress bar
            self.update_progress(100)
            
        except Exception as e:
            self.log(f"Error processing task result: {str(e)}")
            import traceback
            self.log(f"Stacktrace: {traceback.format_exc()}")
            self.update_progress(0)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_script_builder_completed(self, script_name, content):
        self.log(f"Script '{script_name}' created successfully")
        try:
            scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
            os.makedirs(scripts_dir, exist_ok=True)
            script_path = os.path.join(scripts_dir, f"{script_name}.py")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            if hasattr(self, 'script_manager_page'):
                self.script_manager_page.refresh_list()
        except Exception as e:
            self.log(f"Error saving script: {str(e)}")

    def on_task_scheduled(self, task_data):
        """Handle newly scheduled task"""
        try:
            self.log(f"✅ New task scheduled: {task_data.get('name', 'Unknown')}")
            # Update dashboard with new task count
            if hasattr(self.dashboard_page, 'update_task_count'):
                self.dashboard_page.update_task_count()
        except Exception as e:
            self.log(f"❌ Error handling scheduled task: {str(e)}")

    def on_get_trends_requested(self, source):
        """
        Handle request to get trends from dashboard
        """
        self.log(f"Đang lấy xu hướng từ {source}...")
        
        # Remember current page
        current_page = self.stacked_widget.currentIndex()
        
        if source == "google":
            if hasattr(self, 'automation_page'):
                self.automation_page.run_google_trends("vietnam")
                
                # Connect signals if not already connected
                if hasattr(self.automation_page.worker, 'trends_signal'):
                    self.automation_page.worker.trends_signal.connect(
                        lambda trends: self.dashboard_page.add_trending_topics(trends, "google")
                    )
        elif source == "facebook":
            if hasattr(self, 'automation_page'):
                self.automation_page.run_facebook_trends()
                
                # Connect signals if not already connected
                if hasattr(self.automation_page.worker, 'trends_signal'):
                    self.automation_page.worker.trends_signal.connect(
                        lambda trends: self.dashboard_page.add_trending_topics(trends, "facebook")
                    )
                    
    def on_create_content_requested(self, trend_data, content_type):
        """
        Handle request to create content from a trend
        """
        self.log(f"Đang tạo nội dung từ xu hướng: {trend_data.get('keyword', 'Unknown')}")
        
        # Use automation page to create content
        if hasattr(self, 'automation_page'):
            self.automation_page.run_content_creation(trend_data, content_type)
            
            # Connect signals if not already connected
            if hasattr(self.automation_page.worker, 'content_signal'):
                self.automation_page.worker.content_signal.connect(self.dashboard_page.display_content)
        
    def on_post_content_requested(self, content_data, post_type):
        """
        Handle request to post content
        """
        if post_type == "now":
            self.log(f"Đang đăng nội dung...")
            if hasattr(self, 'automation_page'):
                self.automation_page.run_post_content(content_data)
                
                # Connect signals if not already connected
                if hasattr(self.automation_page.worker, 'post_result_signal'):
                    self.automation_page.worker.post_result_signal.connect(
                        lambda success: self.show_post_result(success)
                    )
        elif post_type == "schedule":
            self.log(f"Đang lập lịch đăng bài...")
            # Get schedule time (24 hours from now)
            schedule_time = datetime.now() + timedelta(hours=24)
            
            if hasattr(self, 'automation_page'):
                self.automation_page.run_schedule_post(content_data, schedule_time)
                
                # Connect signals if not already connected
                if hasattr(self.automation_page.worker, 'post_result_signal'):
                    self.automation_page.worker.post_result_signal.connect(
                        lambda success: self.show_schedule_result(success)
                    )
    
    def show_post_result(self, success):
        """Show dialog with post result"""
        if success:
            QMessageBox.information(self, "Đăng bài thành công", "Bài viết đã được đăng thành công!")
        else:
            QMessageBox.warning(self, "Đăng bài thất bại", "Không thể đăng bài viết. Vui lòng thử lại sau.")
            
    def show_schedule_result(self, success):
        """Show dialog with schedule result"""
        if success:
            QMessageBox.information(self, "Lên lịch thành công", "Đã lên lịch đăng bài thành công!")
        else:
            QMessageBox.warning(self, "Lên lịch thất bại", "Không thể lên lịch đăng bài. Vui lòng thử lại sau.")

    def load_settings(self):
        """Load and apply user settings"""
        # Load theme setting
        theme = self.settings.value("theme", DEFAULT_THEME)
        retry_count = self.settings.value("retry_count", 3, type=int)
        timeout = self.settings.value("timeout", 30, type=int)
        font_size = self.settings.value("font_size", 10, type=int)
        
        # Apply theme
        self.current_theme = theme
        self.apply_theme(theme)
        
        # Apply retry and timeout settings to worker components
        if hasattr(self, 'automation_page') and self.automation_page:
            # Update automation page theme
            if hasattr(self.automation_page, 'setup_styles'):
                self.automation_page.setup_styles()
                
        # Apply font size across components if needed
        font = QFont()
        font.setPointSize(font_size)
        QApplication.setFont(font)
        
        # Log settings loaded
        self.log(f"Settings loaded: Theme={theme}, Retry={retry_count}, Timeout={timeout}, Font={font_size}pt")
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

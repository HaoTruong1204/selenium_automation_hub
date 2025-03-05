# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QWidget, QVBoxLayout, QSplitter, QListWidget, QListWidgetItem, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Import hằng số cấu hình
from modules.config import APP_TITLE, APP_WIDTH, APP_HEIGHT, APP_ICON, QSS_FILE
# Import UI widgets
from modules.dashboard import DashboardWidget
from modules.automation import AutomationWidget
from modules.data_processing import DataProcessingWidget
from modules.logs import LogsWidget
from modules.script_manager import ScriptManagerWidget
from modules.settings import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)

        if os.path.exists(APP_ICON):
            self.setWindowIcon(QIcon(APP_ICON))

        # Tạo status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Khởi tạo UI
        self.setup_ui()

        # Áp dụng QSS style
        self.apply_stylesheet()

    def setup_ui(self):
        """Tạo sidebar + stacked widget chứa các trang (Dashboard, Automation, Data, Logs, Script Manager)."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Tạo Sidebar (QListWidget)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)

        # Các mục menu (tên + icon)
        items = [
            ("Dashboard",      "resources/icons/automation.png"),
            ("Automation",     "resources/icons/automation.png"),
            ("Data",           "resources/icons/data.png"),
            ("Logs",           "resources/icons/logs.png"),
            ("Script Manager", "resources/icons/script.png"),
            ("Settings",       "resources/icons/settings.png")
        ]
        for text, icon_path in items:
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
            item = QListWidgetItem(icon, text)
            self.sidebar.addItem(item)

        # Tạo stacked widget để chứa các trang
        self.stacked_widget = QStackedWidget()

        # Khởi tạo các trang
        self.dashboard_page = DashboardWidget()
        self.automation_page = AutomationWidget()
        self.data_page = DataProcessingWidget()
        self.logs_page = LogsWidget()
        self.script_manager_page = ScriptManagerWidget()

        # Thêm trang vào stacked
        self.stacked_widget.addWidget(self.dashboard_page)       # index 0
        self.stacked_widget.addWidget(self.automation_page)      # index 1
        self.stacked_widget.addWidget(self.data_page)            # index 2
        self.stacked_widget.addWidget(self.logs_page)            # index 3
        self.stacked_widget.addWidget(self.script_manager_page)  # index 4

        # Settings là dialog, không cần add vào stacked
        self.settings_dialog = None

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.stacked_widget)

        # Bắt sự kiện chọn sidebar => đổi trang
        self.sidebar.currentRowChanged.connect(self.display_page)

    def display_page(self, index):
        if index == 5:  # Mục Settings
            self.open_settings_dialog()
        else:
            self.stacked_widget.setCurrentIndex(index)
            page_names = ["Dashboard", "Automation", "Data", "Logs", "Script Manager"]
            if index < len(page_names):
                self.statusBar().showMessage(f"Đang hiển thị: {page_names[index]}")

    def open_settings_dialog(self):
        dlg = SettingsDialog(self)
        if dlg.exec_():
            # Xử lý nếu người dùng bấm OK
            pass
        # Reset sidebar trở về trang hiện tại
        self.sidebar.setCurrentRow(self.stacked_widget.currentIndex())

    def apply_stylesheet(self):
        """Tải và áp dụng QSS style."""
        if os.path.exists(QSS_FILE):
            try:
                with open(QSS_FILE, "r", encoding="utf-8") as f:
                    style = f.read()
                    self.setStyleSheet(style)
                print("✅ Theme QSS đã được áp dụng!")
            except Exception as e:
                print(f"Không thể load QSS: {e}")
        else:
            print(f"Không tìm thấy file QSS: {QSS_FILE}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

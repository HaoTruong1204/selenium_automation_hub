from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QDateTime, QPropertyAnimation, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

class LogsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        # Set a modern dark theme via QSS
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; }
            QLabel { color: #ffffff; font-size: 16px; font-weight: bold; }
            QTextEdit { background-color: #363636; color: #e0e0e0; border: 1px solid #454545; padding: 10px; font-family: 'Segoe UI'; font-size: 13px; }
            QPushButton { background-color: #0d6efd; color: white; border: none; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header Label
        header = QLabel("Logs Viewer")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        main_layout.addWidget(header)

        # Log Console (QTextEdit)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        main_layout.addWidget(self.log_console)

        # Control Buttons (Clear Logs)
        button_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def setup_animations(self):
        # Create a fade-in animation for the widget whenever a new log is appended.
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)

    def append_log(self, message, log_type="info"):
        """Thêm log với màu sắc phân biệt dựa trên loại log"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        # Xác định màu dựa trên loại log
        color_map = {
            "error": "#ff6b6b",  # Đỏ sáng
            "warning": "#feca57",  # Vàng sáng
            "success": "#1dd1a1",  # Xanh lá sáng
            "info": "#ffffff"  # Trắng
        }
        
        # Định dạng icon dựa vào loại log
        icon_map = {
            "error": "❌",
            "warning": "⚠️",
            "success": "✅",
            "info": "ℹ️"
        }
        
        # Tạo CSS inline cho màu chữ
        color = color_map.get(log_type, "#ffffff")
        icon = icon_map.get(log_type, "")
        
        # Tạo HTML với định dạng màu
        log_entry = f'<span style="color:{color};">[{timestamp}] {icon} {message}</span>'
        
        # Thêm log vào console
        self.log_console.append(log_entry)
        self.log_console.ensureCursorVisible()  # Đảm bảo cuộn xuống dòng mới nhất

    def clear_logs(self):
        self.log_console.clear()
        self.append_log("Logs cleared.")

# Example usage for testing standalone:
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LogsWidget()
    window.resize(600, 400)
    window.show()
    
    # Append a few test log messages with delay
    def add_test_logs():
        window.append_log("Application started.")
        QTimer.singleShot(1000, lambda: window.append_log("Connecting to server..."))
        QTimer.singleShot(2000, lambda: window.append_log("Data loaded successfully."))
        QTimer.singleShot(3000, lambda: window.append_log("Automation process complete."))
        
    QTimer.singleShot(500, add_test_logs)
    
    sys.exit(app.exec())

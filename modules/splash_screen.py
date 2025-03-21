# modules/splash_screen.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import os

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        # Bỏ khung & luôn top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #1E1E2F;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tiêu đề
        self.label = QLabel("Selenium Automation Hub", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.label.setStyleSheet("color: #0d47a1; margin-top: 50px;")
        layout.addWidget(self.label)
        
        # Logo (nếu có)
        logo_label = QLabel(self)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "app.png")
        
        # Kiểm tra file có tồn tại không
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                layout.addWidget(logo_label)
        else:
            # Nếu không có logo, thêm một label thông báo
            info_label = QLabel("Automation Hub", self)
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: white; font-size: 16px;")
            layout.addWidget(info_label)

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #2c2c3c;
                border: 1px solid #0d47a1;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0d47a1;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.timer.start(50)  # 50ms/lần, giả lập loading

    def advance(self):
        self.value += 1
        self.progress.setValue(self.value)
        if self.value >= 100:
            self.timer.stop()
            self.close()

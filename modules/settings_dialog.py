# modules/settings_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QHBoxLayout, QPushButton, QWidget, 
    QVBoxLayout, QLabel, QGroupBox, QRadioButton, QSlider, QFrame
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPalette
from modules.config import DEFAULT_THEME

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt Tự động hóa")
        self.resize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])

        self.retry_spin = QComboBox()
        for i in range(1, 11):
            self.retry_spin.addItem(str(i))

        self.timeout_spin = QComboBox()
        for i in range(10, 61, 5):
            self.timeout_spin.addItem(str(i))

        layout.addRow("Giao diện:", self.theme_combo)
        layout.addRow("Số lần thử lại:", self.retry_spin)
        layout.addRow("Timeout (giây):", self.timeout_spin)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.setLayout(layout)

    def create_appearance_tab(self):
        """Tạo tab cài đặt giao diện"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme selection
        theme_group = QGroupBox("Chọn theme")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme previews
        theme_previews = QHBoxLayout()
        
        # Dark theme preview
        dark_frame = QFrame()
        dark_frame.setFrameShape(QFrame.StyledPanel)
        dark_frame.setFixedSize(200, 150)
        dark_preview = QVBoxLayout(dark_frame)
        
        dark_title = QLabel("Dark Theme")
        dark_title.setAlignment(Qt.AlignCenter)
        dark_title.setStyleSheet("color: white; font-weight: bold;")
        
        dark_content = QLabel("Giao diện tối, dễ nhìn về đêm\nvà giảm mỏi mắt")
        dark_content.setAlignment(Qt.AlignCenter)
        dark_content.setStyleSheet("color: #e0e0e0;")
        
        dark_button = QPushButton("Button")
        dark_button.setStyleSheet("""
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px;
        """)
        
        dark_frame.setStyleSheet("""
            background-color: #272727;
            border: 2px solid #495057;
            border-radius: 8px;
        """)
        
        dark_preview.addWidget(dark_title)
        dark_preview.addWidget(dark_content)
        dark_preview.addWidget(dark_button)
        
        # Light theme preview
        light_frame = QFrame()
        light_frame.setFrameShape(QFrame.StyledPanel)
        light_frame.setFixedSize(200, 150)
        light_preview = QVBoxLayout(light_frame)
        
        light_title = QLabel("Light Theme")
        light_title.setAlignment(Qt.AlignCenter)
        light_title.setStyleSheet("color: #212529; font-weight: bold;")
        
        light_content = QLabel("Giao diện sáng, thân thiện\nvà dễ sử dụng vào ban ngày")
        light_content.setAlignment(Qt.AlignCenter)
        light_content.setStyleSheet("color: #495057;")
        
        light_button = QPushButton("Button")
        light_button.setStyleSheet("""
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px;
        """)
        
        light_frame.setStyleSheet("""
            background-color: #f8f9fa;
            border: 2px solid #ced4da;
            border-radius: 8px;
        """)
        
        light_preview.addWidget(light_title)
        light_preview.addWidget(light_content)
        light_preview.addWidget(light_button)
        
        # Radio buttons for selection
        self.dark_radio = QRadioButton("Dark Mode")
        self.light_radio = QRadioButton("Light Mode")
        
        if DEFAULT_THEME == "Dark":
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)
        
        # Add to layout
        theme_previews.addWidget(dark_frame)
        theme_previews.addWidget(light_frame)
        
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.dark_radio)
        radio_layout.addWidget(self.light_radio)
        
        theme_layout.addLayout(theme_previews)
        theme_layout.addLayout(radio_layout)
        layout.addWidget(theme_group)
        
        # Các tùy chỉnh font
        font_group = QGroupBox("Cỡ chữ")
        font_layout = QVBoxLayout(font_group)
        
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setMinimum(8)
        self.font_slider.setMaximum(16)
        self.font_slider.setValue(10)
        self.font_slider.setTickPosition(QSlider.TicksBelow)
        self.font_slider.setTickInterval(1)
        
        self.font_size_label = QLabel("Cỡ chữ: 10pt")
        self.font_slider.valueChanged.connect(self.update_font_size_label)
        
        font_layout.addWidget(self.font_size_label)
        font_layout.addWidget(self.font_slider)
        
        layout.addWidget(font_group)
        layout.addStretch()
        
        return tab

    def update_font_size_label(self, value):
        """Cập nhật label hiển thị cỡ chữ"""
        self.font_size_label.setText(f"Cỡ chữ: {value}pt")

    def apply_settings(self):
        """Áp dụng các cài đặt đã chọn"""
        # Lưu theme
        if self.dark_radio.isChecked():
            QSettings().setValue("theme", "Dark")
        else:
            QSettings().setValue("theme", "Light")
        
        # Lưu cỡ chữ
        QSettings().setValue("font_size", self.font_slider.value())
        
        # Thông báo thay đổi theme và font cho MainWindow
        if self.parent():
            self.parent().load_settings()

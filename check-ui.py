#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
                            QCheckBox, QRadioButton, QTableWidget, QTableWidgetItem,
                            QTabWidget, QGroupBox, QFormLayout, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UITestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UI Dark Mode Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Tiêu đề
        title = QLabel("Test Độ Tương Phản UI")
        title.setProperty("heading", "true")
        layout.addWidget(title)
        
        # Tab Widget
        tabs = QTabWidget()
        
        # Tab 1: Form controls
        form_tab = QWidget()
        form_layout = QFormLayout(form_tab)
        
        # Input elements
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nhập tên của bạn")
        
        password_input = QLineEdit()
        password_input.setPlaceholderText("Nhập mật khẩu")
        password_input.setEchoMode(QLineEdit.Password)
        
        combo = QComboBox()
        combo.addItems(["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3"])
        
        check1 = QCheckBox("Tùy chọn 1")
        check2 = QCheckBox("Tùy chọn 2")
        check1.setChecked(True)
        
        radio1 = QRadioButton("Tùy chọn A")
        radio2 = QRadioButton("Tùy chọn B")
        radio1.setChecked(True)
        
        # Add to form
        form_layout.addRow("Tên:", name_input)
        form_layout.addRow("Mật khẩu:", password_input)
        form_layout.addRow("Lựa chọn:", combo)
        form_layout.addRow("Checkbox:", check1)
        form_layout.addRow("", check2)
        form_layout.addRow("Radio:", radio1)
        form_layout.addRow("", radio2)
        
        # Buttons
        btn_layout = QVBoxLayout()
        submit_btn = QPushButton("Xác nhận")
        cancel_btn = QPushButton("Hủy bỏ")
        special_btn = QPushButton("Nút Đặc biệt")
        special_btn.setObjectName("start_btn")  # Áp dụng style đặc biệt
        
        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(special_btn)
        
        form_layout.addRow("Các nút:", btn_layout)
        
        # Tab 2: Table and progress
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        # Table
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Cột 1", "Cột 2", "Cột 3"])
        
        for i in range(5):
            for j in range(3):
                item = QTableWidgetItem(f"Dòng {i+1}, Cột {j+1}")
                table.setItem(i, j, item)
        
        table_layout.addWidget(table)
        
        # Progress bar
        progress = QProgressBar()
        progress.setValue(75)
        table_layout.addWidget(progress)
        
        # Tab 3: Text and console
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        
        # Text area
        text_edit = QTextEdit()
        text_edit.setPlainText("Đây là một đoạn văn bản mẫu.\nKiểm tra xem bạn có thể đọc được không.")
        text_layout.addWidget(text_edit)
        
        # Console
        console = QTextEdit()
        console.setProperty("log", "true")
        console.setPlainText("[INFO] Khởi động ứng dụng\n[ERROR] Lỗi kết nối cơ sở dữ liệu\n[SUCCESS] Kết nối thành công")
        console.setReadOnly(True)
        text_layout.addWidget(console)
        
        # Add tabs
        tabs.addTab(form_tab, "Form Controls")
        tabs.addTab(table_tab, "Table & Progress")
        tabs.addTab(text_tab, "Text & Console")
        
        layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Trạng thái: Đã sẵn sàng")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Tải stylesheet
    try:
        with open("resources/qss/app_style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Lỗi khi load QSS: {e}")
    
    window = UITestWindow()
    window.show()
    
    sys.exit(app.exec_()) 
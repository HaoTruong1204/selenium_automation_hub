# modules/script_manager.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ScriptManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Script Manager")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Tên Kịch Bản", "Ngày Tạo", "Mô tả"])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm Script")
        self.btn_delete = QPushButton("Xóa Script")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Demo
        self.load_scripts()

        # Kết nối nút
        self.btn_add.clicked.connect(self.add_script)
        self.btn_delete.clicked.connect(self.delete_script)

    def load_scripts(self):
        scripts = [
            {"name": "Script Google", "date": "2023-09-01", "desc": "Tìm kiếm Google"},
            {"name": "Script FB",     "date": "2023-09-02", "desc": "Đăng nhập Facebook"},
        ]
        self.table.setRowCount(len(scripts))
        for row, sc in enumerate(scripts):
            self.table.setItem(row, 0, QTableWidgetItem(sc["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(sc["date"]))
            self.table.setItem(row, 2, QTableWidgetItem(sc["desc"]))

    def add_script(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("New Script"))
        self.table.setItem(row, 1, QTableWidgetItem("2023-09-10"))
        self.table.setItem(row, 2, QTableWidgetItem("Mô tả..."))

    def delete_script(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

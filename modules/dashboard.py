# modules/dashboard.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.stats_table = QTableWidget(3, 2)
        self.stats_table.setHorizontalHeaderLabels(["Chỉ số", "Giá trị"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.stats_table.setItem(0, 0, QTableWidgetItem("Số bước thực hiện"))
        self.stats_table.setItem(1, 0, QTableWidgetItem("Thời gian chạy"))
        self.stats_table.setItem(2, 0, QTableWidgetItem("Trạng thái"))

        self.stats_table.setItem(0, 1, QTableWidgetItem("0"))
        self.stats_table.setItem(1, 1, QTableWidgetItem("00:00:00"))
        self.stats_table.setItem(2, 1, QTableWidgetItem("Chưa chạy"))

        layout.addWidget(self.stats_table)
        layout.addStretch()

    def update_info(self, steps, elapsed_time, status):
        # Hàm này giúp cập nhật giá trị trên dashboard
        self.stats_table.setItem(0, 1, QTableWidgetItem(str(steps)))
        self.stats_table.setItem(1, 1, QTableWidgetItem(str(elapsed_time)))
        self.stats_table.setItem(2, 1, QTableWidgetItem(status))

# modules/data_view.py
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QPushButton, QFileDialog, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class DataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scraped_data = pd.DataFrame()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Dữ liệu thu thập")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Lọc dữ liệu...")
        self.filter_edit.textChanged.connect(self.filter_data)
        layout.addWidget(self.filter_edit)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels(["Thời gian", "Nguồn", "Loại", "Nội dung", "Trạng thái", "Chi tiết"])
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.data_table)
        self.export_btn = QPushButton("Xuất CSV")
        self.export_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_btn)
        self.setLayout(layout)

    def filter_data(self):
        keyword = self.filter_edit.text().strip()
        if self.scraped_data.empty or keyword == "":
            self.update_table(self.scraped_data)
            return
        filtered = self.scraped_data[self.scraped_data.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)]
        self.update_table(filtered)

    def update_table(self, df: pd.DataFrame):
        self.data_table.clearContents()
        self.data_table.setRowCount(len(df))
        for i, row in df.iterrows():
            self.data_table.setItem(i, 0, QTableWidgetItem(str(row.get("timestamp", ""))))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(row.get("source", ""))))
            self.data_table.setItem(i, 2, QTableWidgetItem(str(row.get("type", ""))))
            self.data_table.setItem(i, 3, QTableWidgetItem(str(row.get("content", ""))))
            self.data_table.setItem(i, 4, QTableWidgetItem(str(row.get("status", ""))))
            self.data_table.setItem(i, 5, QTableWidgetItem(str(row.get("details", ""))))

    def export_csv(self):
        if self.scraped_data.empty:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất!")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Chọn nơi lưu CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                self.scraped_data.to_csv(file_path, index=False, encoding="utf-8-sig")
                QMessageBox.information(self, "Thành công", f"Đã lưu dữ liệu tại: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu CSV: {str(e)}")

# modules/data_processing.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pandas as pd

class DataProcessingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.df = pd.DataFrame()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Data Processing")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Nhập từ khóa để lọc...")
        self.filter_edit.textChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_edit)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        export_btn = QPushButton("Xuất CSV")
        export_btn.clicked.connect(self.export_csv)
        layout.addWidget(export_btn)

        self.setLayout(layout)

        # Demo data
        self.load_demo_data()

    def load_demo_data(self):
        data = {
            "timestamp": ["2023-09-01 10:00", "2023-09-02 12:30", "2023-09-03 09:15"],
            "source": ["Website A", "Website B", "Website A"],
            "value": [123, 456, 789],
        }
        self.df = pd.DataFrame(data)
        self.update_table(self.df)

    def apply_filter(self):
        keyword = self.filter_edit.text().strip().lower()
        if not keyword:
            self.update_table(self.df)
            return
        filtered = self.df[self.df.apply(lambda row: keyword in str(row).lower(), axis=1)]
        self.update_table(filtered)

    def update_table(self, df: pd.DataFrame):
        self.table.clear()
        if df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                val = str(df.iloc[i][col])
                self.table.setItem(i, j, QTableWidgetItem(val))

    def export_csv(self):
        if self.df.empty:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Xuất CSV", "", "CSV Files (*.csv)")
        if path:
            self.df.to_csv(path, index=False, encoding='utf-8-sig')

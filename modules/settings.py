# modules/settings.py

from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt Ứng dụng")
        self.resize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.proxy_edit = QLineEdit()
        form_layout.addRow("Proxy:", self.proxy_edit)

        self.user_agent_edit = QLineEdit()
        form_layout.addRow("User-Agent:", self.user_agent_edit)

        self.headless_cb = QCheckBox("Chạy headless?")
        form_layout.addRow(self.headless_cb)

        self.delay_edit = QLineEdit()
        self.delay_edit.setPlaceholderText("Độ trễ (giây)...")
        form_layout.addRow("Delay:", self.delay_edit)

        layout.addLayout(form_layout)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def get_settings(self):
        """Trả về dict các cài đặt."""
        return {
            "proxy": self.proxy_edit.text().strip(),
            "user_agent": self.user_agent_edit.text().strip(),
            "headless": self.headless_cb.isChecked(),
            "delay": self.delay_edit.text().strip()
        }

# modules/script_manager.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QHeaderView, QMessageBox, QFileDialog, QInputDialog, QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import os
import datetime

class ScriptManagerWidget(QWidget):
    """
    Widget Quản lý kịch bản (script):
      - Hiển thị danh sách kịch bản dạng bảng
      - Cho phép Lưu/Tải/Xóa kịch bản
      - Double-click vào một kịch bản để phát signal script_selected
    """
    # Signal để thông báo khi một kịch bản được chọn (double-click)
    script_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tiêu đề
        title = QLabel("Quản lý kịch bản")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tạo bảng hiển thị danh sách kịch bản
        self.script_list = QTableWidget()
        self.script_list.setColumnCount(3)
        self.script_list.setHorizontalHeaderLabels(["Tên Kịch Bản", "Ngày Tạo", "Ghi chú"])
        self.script_list.horizontalHeader().setStretchLastSection(True)
        self.script_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.script_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.script_list.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.script_list)

        # Layout cho các nút thao tác
        btn_layout = QHBoxLayout()
        self.save_script_btn = QPushButton("Lưu kịch bản")
        self.load_script_btn = QPushButton("Tải kịch bản")
        self.delete_script_btn = QPushButton("Xóa kịch bản")
        btn_layout.addWidget(self.save_script_btn)
        btn_layout.addWidget(self.load_script_btn)
        btn_layout.addWidget(self.delete_script_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Load dữ liệu ban đầu
        self.refresh_list()

        # Kết nối các tín hiệu
        self.script_list.cellDoubleClicked.connect(self.on_script_double_clicked)
        self.save_script_btn.clicked.connect(self.save_script)
        self.load_script_btn.clicked.connect(self.load_script)
        self.delete_script_btn.clicked.connect(self.delete_script)

    def refresh_list(self):
        """
        Tải danh sách script từ thư mục scripts.
        """
        # Đường dẫn đến thư mục scripts
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        
        # Tạo thư mục scripts nếu chưa tồn tại
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
            
        # Danh sách script
        scripts = []
        
        # Tìm tất cả file .py trong thư mục scripts
        try:
            for filename in os.listdir(scripts_dir):
                if filename.endswith(".py"):
                    file_path = os.path.join(scripts_dir, filename)
                    
                    # Lấy thời gian tạo/sửa đổi file
                    file_time = os.path.getmtime(file_path)
                    date_str = datetime.datetime.fromtimestamp(file_time).strftime("%Y-%m-%d %H:%M")
                    
                    # Đọc nội dung file để tìm ghi chú
                    note = "Không có ghi chú"
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read(500)  # Chỉ đọc 500 ký tự đầu tiên
                            
                            # Tìm dòng comment đầu tiên
                            lines = content.split("\n")
                            for line in lines:
                                line = line.strip()
                                if line.startswith("#"):
                                    note = line[1:].strip()
                                    break
                    except:
                        pass
                        
                    scripts.append({
                        "name": filename,
                        "date": date_str,
                        "note": note,
                        "path": file_path
                    })
        except Exception as e:
            print(f"Lỗi khi đọc thư mục scripts: {str(e)}")
            
        # Cập nhật bảng
        self.script_list.setRowCount(0)
        self.script_list.setRowCount(len(scripts))
        
        for row, script in enumerate(scripts):
            self.script_list.setItem(row, 0, QTableWidgetItem(script["name"]))
            self.script_list.setItem(row, 1, QTableWidgetItem(script["date"]))
            self.script_list.setItem(row, 2, QTableWidgetItem(script["note"]))
            
            # Lưu đường dẫn đầy đủ vào dữ liệu của item
            self.script_list.item(row, 0).setData(Qt.UserRole, script["path"])

    def on_script_double_clicked(self, row, column):
        """
        Khi người dùng double-click vào một dòng trong bảng,
        phát ra signal với đường dẫn đầy đủ của script được chọn.
        """
        item = self.script_list.item(row, 0)
        if item:
            script_path = item.data(Qt.UserRole)
            if script_path:
                self.script_selected.emit(script_path)
                print(f"Đã chọn script: {script_path}")

    def save_script(self):
        """
        Xử lý lưu script mới.
        """
        # Đường dẫn đến thư mục scripts
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        
        # Tạo thư mục scripts nếu chưa tồn tại
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
            
        # Hỏi tên file
        script_name, ok = QInputDialog.getText(
            self, 
            "Tên Script", 
            "Nhập tên cho script mới:",
            QLineEdit.Normal
        )
        
        if not ok or not script_name:
            return
            
        # Đảm bảo tên file hợp lệ
        if not script_name.endswith(".py"):
            script_name += ".py"
            
        # Đường dẫn đầy đủ
        script_path = os.path.join(scripts_dir, script_name)
        
        # Kiểm tra xem file đã tồn tại chưa
        if os.path.exists(script_path):
            confirm = QMessageBox.question(
                self,
                "Xác nhận ghi đè",
                f"Script {script_name} đã tồn tại. Bạn có muốn ghi đè không?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
                
        # Tạo nội dung mẫu cho script mới
        template = """# Script tự động tạo bởi Selenium Automation Hub

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def run(driver):
    \"\"\"
    Hàm chính để chạy script. Nhận tham số là một WebDriver đã khởi tạo.
    Trả về danh sách kết quả (nếu có).
    \"\"\"
    try:
        # Mở trang web
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # Tìm ô tìm kiếm và nhập từ khóa
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys("Selenium Python automation")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Lấy kết quả
        results = []
        search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        for i, result in enumerate(search_results[:5]):
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h3")
                title = title_element.text
                
                link_element = result.find_element(By.CSS_SELECTOR, "a")
                link = link_element.get_attribute("href")
                
                results.append((title, link))
            except:
                continue
                
        return results
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return []

# Nếu chạy trực tiếp file này
if __name__ == "__main__":
    # Khởi tạo driver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Chạy script
        results = run(driver)
        
        # In kết quả
        print("\\nKết quả:")
        for i, (title, link) in enumerate(results):
            print(f"{i+1}. {title}\\n   {link}\\n")
            
    finally:
        # Đóng driver
        driver.quit()
"""
        
        # Lưu file
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(template)
                
            QMessageBox.information(
                self,
                "Thành công",
                f"Đã lưu script {script_name} thành công!"
            )
            
            # Làm mới danh sách
            self.refresh_list()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể lưu script: {str(e)}"
            )

    def load_script(self):
        """
        Mở script đã chọn trong trình soạn thảo mặc định.
        """
        # Lấy dòng đang chọn
        selected_rows = self.script_list.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "Cảnh báo",
                "Vui lòng chọn một script để mở."
            )
            return
            
        # Lấy dòng đầu tiên được chọn
        row = selected_rows[0].row()
        
        # Lấy đường dẫn script
        item = self.script_list.item(row, 0)
        if not item:
            return
            
        script_path = item.data(Qt.UserRole)
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(
                self,
                "Lỗi",
                f"Không tìm thấy script tại đường dẫn: {script_path}"
            )
            return
            
        # Mở file bằng ứng dụng mặc định
        try:
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Windows":
                os.startfile(script_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", script_path])
            else:  # Linux
                subprocess.call(["xdg-open", script_path])
                
            QMessageBox.information(
                self,
                "Thành công",
                f"Đã mở script: {os.path.basename(script_path)}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể mở script: {str(e)}"
            )

    def delete_script(self):
        """
        Xóa script đã chọn.
        """
        # Lấy dòng đang chọn
        selected_rows = self.script_list.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "Cảnh báo",
                "Vui lòng chọn một script để xóa."
            )
            return
            
        # Lấy dòng đầu tiên được chọn
        row = selected_rows[0].row()
        
        # Lấy đường dẫn script
        item = self.script_list.item(row, 0)
        if not item:
            return
            
        script_path = item.data(Qt.UserRole)
        script_name = item.text()
        
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(
                self,
                "Lỗi",
                f"Không tìm thấy script tại đường dẫn: {script_path}"
            )
            return
            
        # Xác nhận xóa
        confirm = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa script '{script_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
            
        # Xóa file
        try:
            os.remove(script_path)
            
            QMessageBox.information(
                self,
                "Thành công",
                f"Đã xóa script: {script_name}"
            )
            
            # Làm mới danh sách
            self.refresh_list()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể xóa script: {str(e)}"
            )

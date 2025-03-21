# modules/proxy_manager.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

import os
import json
import requests
import threading
import time
from queue import Queue

class ProxyManagerWidget(QWidget):
    """
    Widget quản lý và kiểm tra Proxy:
      - Thêm/sửa/xóa proxy
      - Test proxy đa luồng
      - Hỗ trợ HTTP/HTTPS/SOCKS4/SOCKS5 (cần 'requests[socks]' nếu dùng SOCKS)
      - Lưu/đọc proxy từ file JSON
      - Xuất danh sách proxy hoạt động ra file .txt
    """
    proxies_updated = pyqtSignal(list)  # Signal khi danh sách proxy được cập nhật
    log_signal = pyqtSignal(str)  # Signal để gửi thông báo log

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxies = []
        # Đường dẫn lưu file JSON proxy
        self.proxy_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "proxies.json"
        )
        self.init_ui()
        self.load_proxies()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tiêu đề
        title = QLabel("Quản lý Proxy")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Giải thích
        description = QLabel(
            "Sử dụng proxy để phân tán kết nối, tránh bị chặn khi gửi nhiều request.\n"
            "Hỗ trợ các định dạng:\n"
            "- http://ip:port\n"
            "- socks4://ip:port\n"
            "- socks5://ip:port\n"
            "- ip:port (mặc định http)\n"
            "- ip:port:username:password (có thể tuỳ biến)"
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Nhập proxy mới
        input_layout = QHBoxLayout()
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText(
            "Nhập proxy (vd: 171.224.79.180:20031 hoặc socks5://user:pass@ip:port)"
        )
        input_layout.addWidget(self.proxy_input)

        add_btn = QPushButton("Thêm")
        add_btn.clicked.connect(self.add_proxy)
        input_layout.addWidget(add_btn)

        layout.addLayout(input_layout)

        # Bảng hiển thị proxy
        self.proxy_table = QTableWidget(0, 3)
        self.proxy_table.setHorizontalHeaderLabels(["Proxy", "Tình trạng", "Tốc độ (ms)"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.proxy_table)

        # Nút điều khiển
        control_layout = QHBoxLayout()

        test_btn = QPushButton("Kiểm tra tất cả")
        test_btn.clicked.connect(self.test_all_proxies)
        control_layout.addWidget(test_btn)

        delete_btn = QPushButton("Xóa đã chọn")
        delete_btn.clicked.connect(self.delete_selected)
        control_layout.addWidget(delete_btn)

        export_btn = QPushButton("Xuất danh sách")
        export_btn.clicked.connect(self.export_proxies)
        control_layout.addWidget(export_btn)

        layout.addLayout(control_layout)

        # Tuỳ chọn
        options_layout = QHBoxLayout()
        self.auto_rotate = QCheckBox("Tự động xoay vòng proxy")
        self.auto_rotate.setChecked(True)
        options_layout.addWidget(self.auto_rotate)

        self.skip_failed = QCheckBox("Bỏ qua proxy lỗi")
        self.skip_failed.setChecked(True)
        options_layout.addWidget(self.skip_failed)

        layout.addLayout(options_layout)
        self.setLayout(layout)

    def load_proxies(self):
        """
        Đọc danh sách proxy từ file JSON (nếu có).
        """
        try:
            if os.path.exists(self.proxy_file):
                with open(self.proxy_file, 'r', encoding='utf-8') as f:
                    self.proxies = json.load(f)
                self.update_table()
                # Phát signal thông báo danh sách proxy hoạt động
                self.proxies_updated.emit(self.get_active_proxies())
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải danh sách proxy: {str(e)}")

    def save_proxies(self):
        """
        Lưu danh sách proxy vào file JSON.
        """
        try:
            os.makedirs(os.path.dirname(self.proxy_file), exist_ok=True)
            with open(self.proxy_file, 'w', encoding='utf-8') as f:
                json.dump(self.proxies, f, indent=2, ensure_ascii=False)
            # Phát signal thông báo danh sách proxy hoạt động
            self.proxies_updated.emit(self.get_active_proxies())
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu danh sách proxy: {str(e)}")

    def update_table(self):
        """
        Cập nhật nội dung bảng QTableWidget dựa vào self.proxies.
        """
        self.proxy_table.setRowCount(len(self.proxies))
        for row, proxy_data in enumerate(self.proxies):
            self.proxy_table.setItem(row, 0, QTableWidgetItem(proxy_data["proxy"]))
            self.proxy_table.setItem(row, 1, QTableWidgetItem(proxy_data.get("status", "Chưa kiểm tra")))
            self.proxy_table.setItem(row, 2, QTableWidgetItem(str(proxy_data.get("speed", "-"))))

    def add_proxy(self):
        """
        Thêm một proxy mới vào danh sách.
        Định dạng hỗ trợ:
          - ip:port
          - http://ip:port
          - socks4://ip:port
          - socks5://ip:port
          - ip:port:username:password
        """
        proxy_str = self.proxy_input.text().strip()
        if not proxy_str:
            return

        # Kiểm tra trùng lặp
        if any(p["proxy"] == proxy_str for p in self.proxies):
            QMessageBox.information(self, "Thông báo", "Proxy này đã tồn tại trong danh sách.")
            return

        # Bổ sung vào danh sách
        new_proxy = {
            "proxy": proxy_str,
            "status": "Chưa kiểm tra",
            "speed": "-"
        }
        self.proxies.append(new_proxy)
        self.update_table()
        self.proxy_input.clear()
        self.save_proxies()

    def parse_proxy(self, proxy_str):
        """
        Phân tích proxy_str để trả về dict cho requests.
        Hỗ trợ:
          - ip:port -> mặc định http://ip:port
          - http://ip:port
          - socks4://ip:port
          - socks5://ip:port
          - [user:pass@]ip:port
        => Trả về { 'http': 'xxx', 'https': 'xxx' } (nếu parse thành công).
        """
        # Kiểm tra xem user có nhập sẵn schema chưa
        # vd: socks4://..., socks5://..., http://..., https://...
        # Nếu không, mặc định là http://
        if "://" not in proxy_str:
            # user:pass@ip:port hay ip:port
            # => Mặc định gắn http://
            proxy_str = "http://" + proxy_str

        # Kết quả => 1 dict cho http & https
        # requests[socks] vẫn cho phép xài socks4, socks5
        return {"http": proxy_str, "https": proxy_str}

    def test_proxy(self, proxy):
        """Kiểm tra proxy có hoạt động không"""
        try:
            import requests
            from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout
            
            # Thiết lập timeout ngắn để kiểm tra nhanh
            timeout = 8
            
            # Thiết lập proxy
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            
            # Thử kết nối đến một trang web đơn giản
            try:
                # Sử dụng User-Agent để tránh bị chặn
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }
                
                # Thử kết nối đến Google
                response = requests.get(
                    "https://www.google.com", 
                    proxies=proxies, 
                    timeout=timeout,
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Kiểm tra tốc độ phản hồi
                    speed = response.elapsed.total_seconds()
                    if speed < 5:  # Nếu phản hồi dưới 5 giây
                        return True, f"Hoạt động tốt (phản hồi: {speed:.2f}s)"
                    else:
                        return True, f"Hoạt động chậm (phản hồi: {speed:.2f}s)"
                else:
                    return False, f"Lỗi: Mã trạng thái {response.status_code}"
                    
            except (ProxyError, ConnectTimeout, ReadTimeout) as e:
                return False, f"Lỗi kết nối: {str(e)}"
                
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def test_all_proxies(self):
        """Kiểm tra tất cả proxy trong danh sách"""
        self.log_signal.emit("🔄 Đang kiểm tra tất cả proxy...")
        
        # Tạo một hàng đợi để lưu kết quả
        result_queue = Queue()
        
        # Hàm kiểm tra proxy và đưa kết quả vào hàng đợi
        def test_proxy_worker(index, proxy_str):
            success, message = self.test_proxy(proxy_str)
            result_queue.put((index, success, message))
        
        # Tạo và khởi động các thread
        threads = []
        for i, proxy_data in enumerate(self.proxies):
            proxy_str = proxy_data["proxy"]
            t = threading.Thread(target=test_proxy_worker, args=(i, proxy_str))
            t.daemon = True
            threads.append(t)
            t.start()
            # Giới hạn số lượng thread đồng thời để tránh quá tải
            if len(threads) >= 10:
                for thread in threads:
                    thread.join()
                threads = []
        
        # Đợi các thread còn lại hoàn thành
        for thread in threads:
            thread.join()
        
        # Xử lý kết quả
        working_count = 0
        while not result_queue.empty():
            index, success, message = result_queue.get()
            if success:
                self.proxies[index]["status"] = "Hoạt động"
                self.proxies[index]["speed"] = message
                working_count += 1
            else:
                self.proxies[index]["status"] = "Không hoạt động"
                self.proxies[index]["speed"] = message
        
        # Cập nhật UI
        self.update_table()
        self.log_signal.emit(f"✅ Đã kiểm tra xong: {working_count}/{len(self.proxies)} proxy hoạt động")
        
        # Phát tín hiệu cập nhật proxy
        working_proxies = [p["proxy"] for p in self.proxies if p["status"] == "Hoạt động"]
        self.proxies_updated.emit(working_proxies)

    def delete_selected(self):
        """
        Xóa các proxy được chọn trong bảng.
        """
        selected_rows = set(item.row() for item in self.proxy_table.selectedItems())
        if not selected_rows:
            return

        confirm = QMessageBox.question(
            self,
            "Xóa Proxy",
            f"Bạn có chắc muốn xóa {len(selected_rows)} proxy đã chọn?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self.proxies):
                self.proxies.pop(row)

        self.update_table()
        self.save_proxies()

    def export_proxies(self):
        """
        Xuất danh sách proxy ra file text (tất cả & proxy hoạt động).
        """
        if not self.proxies:
            QMessageBox.warning(self, "Không có dữ liệu", "Danh sách proxy trống.")
            return

        all_proxies = "\n".join([p["proxy"] for p in self.proxies])
        working_proxies = "\n".join(
            [p["proxy"] for p in self.proxies if p["status"] == "Hoạt động"]
        )

        export_text = (
            "=== TẤT CẢ PROXY ===\n"
            f"{all_proxies}\n\n"
            "=== PROXY HOẠT ĐỘNG ===\n"
            f"{working_proxies}"
        )

        try:
            with open("proxies_export.txt", "w", encoding="utf-8") as f:
                f.write(export_text)
            QMessageBox.information(
                self,
                "Xuất thành công",
                "Đã xuất danh sách proxy vào file proxies_export.txt"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể xuất file: {str(e)}"
            )

    def get_active_proxies(self):
        """
        Trả về list các proxy đang ở trạng thái 'Hoạt động'.
        """
        return [p["proxy"] for p in self.proxies if p["status"] == "Hoạt động"]
        
    def refresh_proxies(self):
        """
        Làm mới danh sách proxy từ file và cập nhật giao diện.
        """
        self.log_signal.emit("🔄 Đang làm mới danh sách proxy...")
        self.load_proxies()
        self.log_signal.emit("✅ Đã làm mới danh sách proxy")

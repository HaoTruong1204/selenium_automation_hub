import os
import time
import base64
import requests
import logging
from PIL import Image
from io import BytesIO
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox, QGroupBox, QFileDialog, QComboBox, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
import json

class CaptchaResolver(QObject):
    status_signal = pyqtSignal(str)  # Signal để cập nhật trạng thái xử lý CAPTCHA
    
    def __init__(self, service="auto", api_key=None):
        super().__init__()
        self.service = service  # "auto", "2captcha", "anticaptcha", "manual"
        self.api_key = api_key
        
        # Tạo thư mục lưu ảnh captcha nếu chưa có
        self.captcha_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "captcha")
        os.makedirs(self.captcha_dir, exist_ok=True)
    
    def resolve_recaptcha(self, driver, sitekey=None, wait_time=30):
        """Xử lý reCAPTCHA trên trang hiện tại"""
        url = driver.current_url
        
        self.status_signal.emit("Phát hiện reCAPTCHA, đang xử lý...")
        
        # Nếu không có sitekey, tìm từ trang
        if not sitekey:
            try:
                sitekey = driver.find_element_by_xpath("//div[@class='g-recaptcha']").get_attribute("data-sitekey")
            except:
                try:
                    iframe = driver.find_element_by_xpath("//iframe[contains(@src, 'recaptcha')]")
                    recaptcha_url = iframe.get_attribute("src")
                    # Extract sitekey from URL
                    import re
                    match = re.search(r"k=([^&]+)", recaptcha_url)
                    if match:
                        sitekey = match.group(1)
                except:
                    self.status_signal.emit("Không thể xác định sitekey reCAPTCHA.")
                    return False
        
        if not sitekey:
            self.status_signal.emit("Không tìm thấy sitekey reCAPTCHA.")
            return False
        
        # Xử lý dựa trên service được chọn
        if self.service == "2captcha" and self.api_key:
            return self._solve_with_2captcha(url, sitekey, driver, wait_time)
        elif self.service == "anticaptcha" and self.api_key:
            return self._solve_with_anticaptcha(url, sitekey, wait_time)
        elif self.service == "manual":
            return self._solve_manually(driver, wait_time)
        else:
            # Auto - thử các phương pháp theo thứ tự ưu tiên
            if self.api_key:
                result = self._solve_with_2captcha(url, sitekey, driver, wait_time)
                if result:
                    return result
            
            # Nếu không có api_key hoặc giải tự động thất bại, chuyển sang giải manual
            return self._solve_manually(driver, wait_time)
    
    def resolve_image_captcha(self, driver, element_selector, wait_time=30):
        """Xử lý CAPTCHA dạng hình ảnh đơn giản"""
        self.status_signal.emit("Phát hiện Image CAPTCHA, đang xử lý...")
        
        try:
            # Tìm element chứa captcha image
            captcha_elem = driver.find_element_by_css_selector(element_selector)
            
            # Chụp screenshot của element
            captcha_img = captcha_elem.screenshot_as_base64
            img_data = base64.b64decode(captcha_img)
            image = Image.open(BytesIO(img_data))
            
            # Lưu ảnh captcha
            timestamp = int(time.time())
            image_path = os.path.join(self.captcha_dir, f"captcha_{timestamp}.png")
            image.save(image_path)
            
            if self.service == "2captcha" and self.api_key:
                return self._solve_image_with_2captcha(image_path, wait_time)
            elif self.service == "manual":
                return self._solve_image_manually(image_path, wait_time)
            else:
                # Auto - thử các phương pháp
                if self.api_key:
                    result = self._solve_image_with_2captcha(image_path, wait_time)
                    if result:
                        return result
                
                return self._solve_image_manually(image_path, wait_time)
                
        except Exception as e:
            self.status_signal.emit(f"Lỗi khi xử lý Image CAPTCHA: {str(e)}")
            return None
    
    def _solve_with_2captcha(self, url, sitekey, driver, wait_time):
        """Giải reCAPTCHA sử dụng 2Captcha API"""
        try:
            self.status_signal.emit("Đang gửi CAPTCHA đến 2Captcha...")
            
            # API endpoint
            api_url = "https://2captcha.com/in.php"
            
            # Request parameters
            params = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': sitekey,
                'pageurl': url,
                'json': 1
            }
            
            # Gửi request đến 2Captcha
            response = requests.post(api_url, data=params)
            data = response.json()
            
            if data.get('status') == 1:
                # Lấy request ID
                request_id = data.get('request')
                
                # Chờ kết quả
                self.status_signal.emit(f"Đang đợi 2Captcha xử lý (ID: {request_id})...")
                
                # API endpoint cho kết quả
                result_url = f"https://2captcha.com/res.php?key={self.api_key}&action=get&id={request_id}&json=1"
                
                # Polling cho đến khi có kết quả hoặc hết thời gian
                for _ in range(wait_time):
                    time.sleep(5)  # Wait 5 seconds between polls
                    
                    result_response = requests.get(result_url)
                    result_data = result_response.json()
                    
                    if result_data.get('status') == 1:
                        captcha_response = result_data.get('request')
                        self.status_signal.emit("2Captcha đã giải thành công!")
                        
                        # Điền kết quả vào form
                        script = f"""
                        document.getElementById("g-recaptcha-response").innerHTML="{captcha_response}";
                        if (typeof ___grecaptcha_cfg !== 'undefined') {{
                            // Sử dụng callback của reCAPTCHA nếu có
                            ___grecaptcha_cfg.clients[0].W.W.callback("{captcha_response}");
                        }}
                        """
                        driver.execute_script(script)
                        return True
                
                self.status_signal.emit("Hết thời gian chờ 2Captcha.")
                return False
            else:
                self.status_signal.emit(f"Lỗi từ 2Captcha: {data.get('error_text', 'Unknown error')}")
                return False
        except Exception as e:
            self.status_signal.emit(f"Lỗi khi gọi 2Captcha API: {str(e)}")
            return False
    
    def _solve_image_with_2captcha(self, image_path, wait_time):
        """Giải Image CAPTCHA sử dụng 2Captcha API"""
        try:
            self.status_signal.emit("Đang gửi CAPTCHA đến 2Captcha...")
            
            # API endpoint
            api_url = "https://2captcha.com/in.php"
            
            # Mở file và encode base64
            with open(image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Request parameters
            params = {
                'key': self.api_key,
                'method': 'base64',
                'body': img_data,
                'json': 1
            }
            
            # Gửi request đến 2Captcha
            response = requests.post(api_url, data=params)
            data = response.json()
            
            if data.get('status') == 1:
                # Lấy request ID
                request_id = data.get('request')
                
                # Chờ kết quả
                self.status_signal.emit(f"Đang đợi 2Captcha xử lý (ID: {request_id})...")
                
                # API endpoint cho kết quả
                result_url = f"https://2captcha.com/res.php?key={self.api_key}&action=get&id={request_id}&json=1"
                
                # Polling cho đến khi có kết quả hoặc hết thời gian
                for _ in range(wait_time):
                    time.sleep(5)  # Wait 5 seconds between polls
                    
                    result_response = requests.get(result_url)
                    result_data = result_response.json()
                    
                    if result_data.get('status') == 1:
                        captcha_text = result_data.get('request')
                        self.status_signal.emit("2Captcha đã giải thành công!")
                        return captcha_text
                
                self.status_signal.emit("Hết thời gian chờ 2Captcha.")
                return None
            else:
                self.status_signal.emit(f"Lỗi từ 2Captcha: {data.get('error_text', 'Unknown error')}")
                return None
        except Exception as e:
            self.status_signal.emit(f"Lỗi khi gọi 2Captcha API: {str(e)}")
            return None
    
    def _solve_manually(self, driver, wait_time):
        """Cho phép người dùng giải CAPTCHA thủ công"""
        self.status_signal.emit("Đang chuyển sang giải CAPTCHA thủ công...")
        
        # Hiển thị cửa sổ hướng dẫn
        dialog = ManualCaptchaDialog(wait_time)
        result = dialog.exec_()
        
        if result == 1:  # User pressed OK
            self.status_signal.emit("Người dùng đã xác nhận giải CAPTCHA thủ công.")
            return True
        else:
            self.status_signal.emit("Người dùng đã hủy giải CAPTCHA thủ công.")
            return False
    
    def _solve_image_manually(self, image_path, wait_time):
        """Cho phép người dùng giải Image CAPTCHA thủ công"""
        self.status_signal.emit("Đang chuyển sang giải Image CAPTCHA thủ công...")
        
        # Hiển thị cửa sổ nhập CAPTCHA
        dialog = ImageCaptchaDialog(image_path, wait_time)
        result = dialog.exec_()
        
        if result == 1:  # User pressed OK
            captcha_text = dialog.get_captcha_text()
            if captcha_text:
                self.status_signal.emit("Đã nhận CAPTCHA từ người dùng.")
                return captcha_text
            else:
                self.status_signal.emit("Người dùng không nhập CAPTCHA.")
                return None
        else:
            self.status_signal.emit("Người dùng đã hủy giải CAPTCHA.")
            return None

class ManualCaptchaDialog(QDialog):
    """Dialog for manual captcha solving"""
    captcha_solved = pyqtSignal(str)
    
    def __init__(self, image_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Giải CAPTCHA")
        self.resize(400, 300)
        self.init_ui()
        
        if image_path:
            self.load_image(image_path)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(100)
        layout.addWidget(self.image_label)
        
        # Solution input
        input_layout = QHBoxLayout()
        
        self.solution_input = QLineEdit()
        self.solution_input.setPlaceholderText("Nhập giải pháp CAPTCHA...")
        input_layout.addWidget(self.solution_input)
        
        self.submit_btn = QPushButton("Xác nhận")
        self.submit_btn.clicked.connect(self.submit_solution)
        input_layout.addWidget(self.submit_btn)
        
        layout.addLayout(input_layout)
        
        # Additional buttons
        btn_layout = QHBoxLayout()
        
        self.load_image_btn = QPushButton("Tải ảnh")
        self.load_image_btn.clicked.connect(self.browse_image)
        btn_layout.addWidget(self.load_image_btn)
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def load_image(self, path):
        """Load captcha image from path"""
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                # Scale if too large
                if pixmap.width() > 350:
                    pixmap = pixmap.scaledToWidth(350, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("Failed to load image")
        else:
            self.image_label.setText("Image not found")

    def browse_image(self):
        """Open file dialog to select an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CAPTCHA image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.load_image(file_path)

    def submit_solution(self):
        """Submit captcha solution"""
        solution = self.solution_input.text().strip()
        if solution:
            self.captcha_solved.emit(solution)
            self.accept()
        else:
            QMessageBox.warning(self, "Empty Solution", "Please enter the CAPTCHA solution")

class ImageCaptchaDialog(QDialog):
    def __init__(self, image_path, timeout=30, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Giải Image CAPTCHA")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Hướng dẫn
        instruction = QLabel(
            "Vui lòng nhập văn bản hiển thị trong hình CAPTCHA bên dưới:\n"
            f"Bạn có {timeout} giây để hoàn thành."
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # Hiển thị ảnh CAPTCHA
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setMaximumSize(300, 100)
        layout.addWidget(image_label)
        
        # Ô nhập CAPTCHA
        form_layout = QFormLayout()
        self.captcha_input = QLineEdit()
        form_layout.addRow("Nhập CAPTCHA:", self.captcha_input)
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QVBoxLayout()
        self.ok_button = QPushButton("Xác nhận")
        self.cancel_button = QPushButton("Hủy")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_captcha_text(self):
        return self.captcha_input.text().strip()

class CaptchaResolverWidget(QDialog):
    """
    Dialog for configuring and testing captcha resolution.
    Provides a GUI for the CaptchaResolver functionality.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Captcha Resolver")
        self.resize(600, 500)
        self.resolver = CaptchaResolver()
        self.resolver.status_signal.connect(self.update_status)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Captcha Resolver")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Service selection
        service_group = QGroupBox("Dịch vụ giải Captcha")
        service_layout = QVBoxLayout()
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Auto (Tự động)", "2Captcha", "Anti-Captcha", "Manual (Thủ công)"])
        service_layout.addWidget(self.service_combo)
        
        # API Key input
        api_layout = QFormLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Nhập API key nếu sử dụng 2Captcha hoặc Anti-Captcha")
        api_layout.addRow("API Key:", self.api_key_input)
        service_layout.addLayout(api_layout)
        
        service_group.setLayout(service_layout)
        layout.addWidget(service_group)
        
        # Test area
        test_group = QGroupBox("Kiểm tra giải Captcha")
        test_layout = QVBoxLayout()
        
        # Image display
        self.image_label = QLabel("Chưa có ảnh Captcha")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(100)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        test_layout.addWidget(self.image_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.load_image_btn = QPushButton("Tải ảnh Captcha")
        self.load_image_btn.clicked.connect(self.load_captcha_image)
        btn_layout.addWidget(self.load_image_btn)
        
        self.solve_btn = QPushButton("Giải Captcha")
        self.solve_btn.clicked.connect(self.solve_captcha)
        btn_layout.addWidget(self.solve_btn)
        
        test_layout.addLayout(btn_layout)
        
        # Result display
        result_layout = QFormLayout()
        self.result_text = QLineEdit()
        self.result_text.setReadOnly(True)
        result_layout.addRow("Kết quả:", self.result_text)
        test_layout.addLayout(result_layout)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # Status area
        status_group = QGroupBox("Trạng thái")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Lưu cài đặt")
        self.save_btn.clicked.connect(self.save_settings)
        bottom_layout.addWidget(self.save_btn)
        
        self.close_btn = QPushButton("Đóng")
        self.close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # Load saved settings
        self.load_settings()
    
    def load_settings(self):
        """Load saved captcha resolver settings"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "captcha_settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # Set service
                    service_map = {
                        "auto": 0,
                        "2captcha": 1,
                        "anticaptcha": 2,
                        "manual": 3
                    }
                    service = settings.get("service", "auto")
                    self.service_combo.setCurrentIndex(service_map.get(service, 0))
                    
                    # Set API key
                    self.api_key_input.setText(settings.get("api_key", ""))
        except Exception as e:
            self.update_status(f"Lỗi khi tải cài đặt: {str(e)}")
    
    def save_settings(self):
        """Save captcha resolver settings"""
        try:
            service_map = {
                0: "auto",
                1: "2captcha",
                2: "anticaptcha",
                3: "manual"
            }
            
            settings = {
                "service": service_map.get(self.service_combo.currentIndex(), "auto"),
                "api_key": self.api_key_input.text().strip()
            }
            
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            os.makedirs(data_dir, exist_ok=True)
            
            # Save settings
            settings_path = os.path.join(data_dir, "captcha_settings.json")
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
            self.update_status("Đã lưu cài đặt thành công")
            
            # Update resolver with new settings
            self.resolver.service = settings["service"]
            self.resolver.api_key = settings["api_key"]
            
        except Exception as e:
            self.update_status(f"Lỗi khi lưu cài đặt: {str(e)}")
    
    def load_captcha_image(self):
        """Load a captcha image for testing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh Captcha", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.captcha_image_path = file_path
            pixmap = QPixmap(file_path)
            
            if not pixmap.isNull():
                # Scale if too large
                if pixmap.width() > 350:
                    pixmap = pixmap.scaledToWidth(350, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
                self.update_status(f"Đã tải ảnh: {os.path.basename(file_path)}")
            else:
                self.image_label.setText("Không thể tải ảnh")
                self.update_status("Lỗi: Không thể tải ảnh")
    
    def solve_captcha(self):
        """Test captcha solving with the loaded image"""
        if not hasattr(self, 'captcha_image_path') or not os.path.exists(self.captcha_image_path):
            self.update_status("Vui lòng tải ảnh Captcha trước")
            return
            
        # Update resolver settings
        service_map = {
            0: "auto",
            1: "2captcha",
            2: "anticaptcha",
            3: "manual"
        }
        
        self.resolver.service = service_map.get(self.service_combo.currentIndex(), "auto")
        self.resolver.api_key = self.api_key_input.text().strip()
        
        # Solve captcha
        self.update_status("Đang giải Captcha...")
        
        try:
            # For testing, we'll use the _solve_image_manually or _solve_image_with_2captcha method
            if self.resolver.service == "2captcha" and self.resolver.api_key:
                result = self.resolver._solve_image_with_2captcha(self.captcha_image_path, 30)
            else:
                result = self.resolver._solve_image_manually(self.captcha_image_path, 30)
                
            if result:
                self.result_text.setText(result)
                self.update_status("Đã giải Captcha thành công")
            else:
                self.result_text.setText("")
                self.update_status("Không thể giải Captcha")
        except Exception as e:
            self.update_status(f"Lỗi khi giải Captcha: {str(e)}")
    
    def update_status(self, message):
        """Update status label with message"""
        self.status_label.setText(message)
        print(f"Captcha Resolver: {message}") 
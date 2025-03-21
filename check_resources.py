import os
import shutil
import sys
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_directory_structure():
    """Tạo cấu trúc thư mục cần thiết cho dự án"""
    # Thư mục gốc
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Danh sách thư mục cần tạo
    directories = [
        "data",
        "logs",
        "scripts",
        "downloads",
        "captcha",
        os.path.join("resources", "icons"),
        os.path.join("resources", "qss")
    ]
    
    # Tạo các thư mục
    for directory in directories:
        dir_path = os.path.join(root_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info(f"Đã tạo thư mục: {directory}")
    
    # Tạo file mẫu cho scripts
    create_sample_script(root_dir)
    
    # Tạo file app.png nếu chưa có
    create_default_icon(root_dir)
    
    # Tạo file QSS nếu chưa có
    create_default_qss(root_dir)
    
    logging.info("Hoàn thành kiểm tra và tạo cấu trúc thư mục!")

def create_sample_script(root_dir):
    """Tạo script mẫu trong thư mục scripts"""
    sample_script_path = os.path.join(root_dir, "scripts", "sample_google_search.py")
    
    if not os.path.exists(sample_script_path):
        sample_script = '''
# Sample Google Search Script
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def run(main_window=None):
    """
    Hàm chạy script - sẽ được gọi bởi ứng dụng chính
    """
    # Log thông báo nếu có main_window
    if main_window:
        main_window.log("Bắt đầu chạy script Google Search")
    
    # Thiết lập trình duyệt
    options = Options()
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Mở Google
        driver.get("https://www.google.com")
        
        # Tìm ô tìm kiếm và nhập từ khóa
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Python selenium automation")
        search_box.send_keys(Keys.RETURN)
        
        # Đợi kết quả load
        time.sleep(2)
        
        # Lấy danh sách kết quả
        results = []
        elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        for element in elements[:5]:  # Chỉ lấy 5 kết quả đầu
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "h3")
                link_elem = element.find_element(By.CSS_SELECTOR, "a")
                
                title = title_elem.text
                link = link_elem.get_attribute("href")
                
                results.append({
                    "Tiêu đề": title,
                    "Liên kết": link
                })
                
                if main_window:
                    main_window.log(f"Tìm thấy: {title}")
            except:
                continue
        
        if main_window:
            main_window.log(f"Tìm thấy {len(results)} kết quả")
        
        return results
        
    except Exception as e:
        if main_window:
            main_window.log(f"Lỗi: {str(e)}")
        print(f"Lỗi: {str(e)}")
    finally:
        # Đóng trình duyệt
        driver.quit()

if __name__ == "__main__":
    # Nếu chạy trực tiếp từ command line
    print("Chạy script Google Search...")
    results = run()
    print(f"Kết quả: {results}")
'''
        with open(sample_script_path, "w", encoding="utf-8") as f:
            f.write(sample_script)
        logging.info(f"Đã tạo script mẫu: {sample_script_path}")

def create_default_icon(root_dir):
    """Tạo file icon mặc định nếu chưa có"""
    icon_path = os.path.join(root_dir, "resources", "icons", "app.png")
    
    if not os.path.exists(icon_path):
        # Tạo một file PNG trống
        try:
            from PIL import Image
            img = Image.new('RGB', (256, 256), color = (0, 100, 255))
            img.save(icon_path)
            logging.info(f"Đã tạo icon mặc định: {icon_path}")
        except ImportError:
            # Nếu không có thư viện PIL, tạo file trống
            with open(icon_path, "wb") as f:
                f.write(b"")
            logging.info(f"Đã tạo file icon trống: {icon_path}")

def create_default_qss(root_dir):
    """Tạo file QSS mặc định nếu chưa có"""
    qss_path = os.path.join(root_dir, "resources", "qss", "app_style.qss")
    
    if not os.path.exists(qss_path):
        default_qss = '''
/* app_style.qss - Bảng màu tối */

* {
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

QMainWindow {
    background-color: #2b2b2b;
}

QLabel {
    color: #e0e0e0;
}

QLabel[heading="true"] {
    font-size: 24px;
    font-weight: bold;
    padding: 10px;
}

QLabel[subheading="true"] {
    font-size: 18px;
    font-weight: bold;
    padding: 5px;
}

QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #0b5ed7;
}

QPushButton:pressed {
    background-color: #0a58ca;
}

QPushButton:disabled {
    background-color: #6c757d;
    color: #e0e0e0;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #363636;
    color: #e0e0e0;
    border: 1px solid #454545;
    border-radius: 4px;
    padding: 8px;
}

QTableWidget {
    background-color: #363636;
    color: #e0e0e0;
    border: 1px solid #454545;
    gridline-color: #454545;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #0d6efd;
}

QHeaderView::section {
    background-color: #2b2b2b;
    color: #e0e0e0;
    padding: 5px;
    border: 1px solid #454545;
}

QTabWidget::pane {
    border: 1px solid #454545;
    background-color: #363636;
}

QTabBar::tab {
    background-color: #2b2b2b;
    color: #e0e0e0;
    border: 1px solid #454545;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #363636;
}

QTabBar::tab:hover {
    background-color: #404040;
}

QProgressBar {
    border: 1px solid #454545;
    border-radius: 4px;
    text-align: center;
    color: #e0e0e0;
    background-color: #363636;
}

QProgressBar::chunk {
    background-color: #0d6efd;
    width: 10px;
    margin: 0px;
}

QScrollBar:vertical {
    border: none;
    background-color: #2b2b2b;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #454545;
    min-height: 30px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #0d6efd;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #2b2b2b;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #454545;
    min-width: 30px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #0d6efd;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QCheckBox {
    color: #e0e0e0;
    spacing: 10px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid #454545;
    background-color: #363636;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 1px solid #0d6efd;
    background-color: #0d6efd;
    border-radius: 3px;
}

QRadioButton {
    color: #e0e0e0;
    spacing: 10px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    border: 1px solid #454545;
    background-color: #363636;
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    border: 1px solid #0d6efd;
    background-color: #0d6efd;
    border-radius: 9px;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 10px;
}

QMenuBar::item:selected {
    background-color: #0d6efd;
    color: white;
}

QMenu {
    background-color: #363636;
    color: #e0e0e0;
    border: 1px solid #454545;
    padding: 5px 0;
}

QMenu::item {
    padding: 8px 20px;
}

QMenu::item:selected {
    background-color: #0d6efd;
    color: white;
}

QStatusBar {
    background-color: #2b2b2b;
    color: #e0e0e0;
}
'''
        with open(qss_path, "w", encoding="utf-8") as f:
            f.write(default_qss)
        logging.info(f"Đã tạo file QSS mặc định: {qss_path}")

if __name__ == "__main__":
    create_directory_structure() 
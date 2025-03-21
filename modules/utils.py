# modules/utils.py

import logging
import importlib
import os
import sys
import subprocess
import re
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

def setup_logging():
    """Thiết lập logging cho ứng dụng"""
    # Tạo thư mục logs nếu chưa tồn tại
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Tạo tên file log với timestamp
    log_file = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Định dạng log
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Thiết lập root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Xóa các handler cũ nếu có
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Handler cho console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)
    
    # Handler cho file
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Ghi chi tiết hơn vào file
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)
    
    # Thiết lập logger cho các thư viện bên thứ ba
    for logger_name in ["selenium", "urllib3", "requests"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)  # Chỉ ghi log warning trở lên cho thư viện bên thứ ba
    
    logging.info("✅ Logging đã được thiết lập!")

def check_environment():
    """Kiểm tra môi trường và các thư viện cần thiết."""
    required_libs = ["selenium", "pandas", "PyQt5", "matplotlib"]
    missing_libs = []
    
    for lib in required_libs:
        try:
            importlib.import_module(lib)
        except ImportError:
            missing_libs.append(lib)
    
    if missing_libs:
        logging.error(f"Thiếu các thư viện: {', '.join(missing_libs)}")
        return False
    
    return True

def get_chrome_version(chrome_path=None):
    """
    Lấy phiên bản của Chrome từ đường dẫn chỉ định hoặc từ hệ thống
    """
    try:
        if chrome_path and os.path.exists(chrome_path):
            # Tìm phiên bản Chrome từ file cụ thể
            output = subprocess.check_output([chrome_path, "--version"], 
                                            stderr=subprocess.STDOUT,
                                            universal_newlines=True)
            match = re.search(r"Chrome\s+(\d+\.\d+\.\d+\.\d+)", output)
            if match:
                return match.group(1)
        
        # Nếu không tìm thấy từ đường dẫn, tìm theo cách thủ công
        if sys.platform.startswith("win"):
            # Windows
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    output = subprocess.check_output([path, "--version"], 
                                                 stderr=subprocess.STDOUT,
                                                 universal_newlines=True)
                    match = re.search(r"Chrome\s+(\d+\.\d+\.\d+\.\d+)", output)
                    if match:
                        return match.group(1)
        
        # Nếu không tìm thấy, trả về None
        return None
    except Exception as e:
        logging.error(f"⚠️ Lỗi khi xác định phiên bản Chrome: {str(e)}")
        return None

def check_install_webdriver(chrome_path=None):
    """
    Kiểm tra, tải và cài đặt WebDriver phù hợp với phiên bản Chrome.
    
    Args:
        chrome_path: Đường dẫn tới Chrome exe, nếu không dùng mặc định
        
    Returns:
        webdriver_path: Đường dẫn tới ChromeDriver đã cài đặt
    """
    try:
        # Xác định phiên bản Chrome
        chrome_version = get_chrome_version(chrome_path)
        if chrome_version:
            logging.info(f"✅ Phát hiện Chrome phiên bản: {chrome_version}")
        else:
            logging.warning("⚠️ Không thể xác định phiên bản Chrome. Sẽ sử dụng ChromeDriver mới nhất.")
        
        # Cài đặt ChromeDriver tương thích
        try:
            driver_path = ChromeDriverManager().install()
            logging.info(f"✅ ChromeDriver đã cài đặt tại: {driver_path}")
            return driver_path
        except Exception as e:
            logging.error(f"⚠️ Lỗi khi cài đặt ChromeDriver: {str(e)}")
            logging.info("⚠️ Sẽ dùng phiên bản ChromeDriver có sẵn nếu có")
            return None
            
    except Exception as e:
        logging.error(f"⚠️ Không thể kiểm tra/cài đặt ChromeDriver: {str(e)}")
        return None

def get_chrome_profile_info():
    """
    Lấy thông tin về các Chrome profile có sẵn.
    
    Returns:
        List of dict với thông tin profile
    """
    profiles = []
    
    # Đường dẫn tiêu chuẩn tới User Data
    default_paths = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
        os.path.join(os.environ.get('APPDATA', ''), 'Google', 'Chrome', 'User Data'),
        os.path.join(os.environ.get('HOMEPATH', ''), 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
    ]
    
    for base_path in default_paths:
        if not os.path.exists(base_path):
            continue
            
        # Tìm tất cả thư mục Profile
        try:
            for item in os.listdir(base_path):
                if item.startswith('Profile ') or item == 'Default':
                    profile_path = os.path.join(base_path, item)
                    profiles.append({
                        'name': item,
                        'path': profile_path,
                        'base_dir': base_path
                    })
        except:
            pass
    
    return profiles

def ensure_webdriver_installed():
    """Make sure the WebDriver is installed, with user-friendly error handling"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        return driver_path
    except Exception as e:
        # Handle common issues
        error_message = str(e).lower()
        
        if "connection" in error_message:
            return "ERROR: Internet connection issue. Please check your connection and try again."
        elif "chrome" in error_message and "version" in error_message:
            return "ERROR: Could not detect Chrome version. Please make sure Chrome is installed correctly."
        elif "permission" in error_message:
            return "ERROR: Permission denied when installing WebDriver. Try running as administrator."
        else:
            return f"ERROR: {str(e)}"

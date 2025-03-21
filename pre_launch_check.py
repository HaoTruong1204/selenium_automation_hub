#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import importlib
import subprocess
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pre_launch_check.log")
    ]
)

def check_python_version():
    """Kiểm tra phiên bản Python"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 7):
        logging.error("❌ Yêu cầu Python 3.7 trở lên. Phiên bản hiện tại: %s.%s", major, minor)
        return False
    
    logging.info("✅ Phiên bản Python hợp lệ: %s.%s", major, minor)
    return True

def check_required_packages():
    """Kiểm tra các thư viện cần thiết"""
    required_packages = [
        "PyQt5",
        "selenium",
        "pandas",
        "matplotlib",
        "webdriver_manager",
        "requests",
        "pillow",
        "sqlalchemy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            logging.info(f"✅ Đã cài đặt: {package}")
        except ImportError:
            missing_packages.append(package)
            logging.error(f"❌ Thiếu thư viện: {package}")
    
    if missing_packages:
        logging.error("Các thư viện sau cần được cài đặt: %s", ", ".join(missing_packages))
        logging.info("Bạn có thể cài đặt bằng lệnh: pip install %s", " ".join(missing_packages))
        
        # Hỏi người dùng có muốn cài đặt tự động không
        if input("Bạn có muốn cài đặt tự động các thư viện còn thiếu? (y/n): ").lower() == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                logging.info("✅ Đã cài đặt thành công các thư viện còn thiếu")
                return True
            except subprocess.CalledProcessError:
                logging.error("❌ Không thể cài đặt tự động các thư viện")
                return False
        return False
    
    return True

def check_directory_structure():
    """Kiểm tra cấu trúc thư mục"""
    required_directories = [
        "data",
        "logs",
        "scripts",
        "downloads",
        "captcha",
        os.path.join("resources", "icons"),
        os.path.join("resources", "qss")
    ]
    
    missing_directories = []
    
    for directory in required_directories:
        if not os.path.exists(directory):
            missing_directories.append(directory)
            logging.error(f"❌ Thiếu thư mục: {directory}")
    
    if missing_directories:
        logging.error("Các thư mục sau cần được tạo: %s", ", ".join(missing_directories))
        
        # Hỏi người dùng có muốn tạo tự động không
        if input("Bạn có muốn tạo tự động các thư mục còn thiếu? (y/n): ").lower() == 'y':
            for directory in missing_directories:
                os.makedirs(directory, exist_ok=True)
            logging.info("✅ Đã tạo thành công các thư mục còn thiếu")
            return True
        return False
    
    logging.info("✅ Cấu trúc thư mục hợp lệ")
    return True

def check_required_files():
    """Kiểm tra các file cần thiết"""
    required_files = [
        os.path.join("resources", "icons", "app.png"),
        os.path.join("resources", "qss", "app_style.qss")
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            logging.error(f"❌ Thiếu file: {file_path}")
    
    if missing_files:
        logging.error("Các file sau cần được tạo: %s", ", ".join(missing_files))
        
        # Gợi ý chạy check_resources.py
        logging.info("Gợi ý: Chạy 'python check_resources.py' để tạo tự động các file còn thiếu")
        return False
    
    logging.info("✅ Đã tìm thấy tất cả các file cần thiết")
    return True

def run_all_checks():
    """Chạy tất cả các kiểm tra"""
    checks = [
        check_python_version,
        check_required_packages,
        check_directory_structure,
        check_required_files
    ]
    
    all_passed = True
    
    for check_func in checks:
        if not check_func():
            all_passed = False
    
    if all_passed:
        logging.info("✅ Tất cả các kiểm tra đã vượt qua. Ứng dụng sẵn sàng chạy!")
        return True
    else:
        logging.error("❌ Có một số vấn đề cần giải quyết trước khi chạy ứng dụng.")
        return False

if __name__ == "__main__":
    print("🔍 Kiểm tra trước khi chạy ứng dụng...\n")
    
    if run_all_checks():
        print("\n✅ Ứng dụng sẵn sàng để chạy. Bạn có thể chạy 'python main.py'")
    else:
        print("\n❌ Vui lòng giải quyết các vấn đề được liệt kê ở trên trước khi chạy ứng dụng.") 
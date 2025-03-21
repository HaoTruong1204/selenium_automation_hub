#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import importlib

def check_files():
    """Kiểm tra các file cần thiết đã tồn tại và đúng định dạng"""
    required_files = [
        "main.py",
        "modules/config.py",
        "modules/main_window.py",
        "modules/automation_view.py",
        "resources/qss/app_style.qss"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"Lỗi: File {file} không tồn tại")
            return False
    
    return True

def check_imports():
    """Kiểm tra imports trong các file chính"""
    try:
        importlib.import_module("PyQt5.QtCore")
        importlib.import_module("PyQt5.QtWidgets")
        importlib.import_module("PyQt5.QtGui")
    except ImportError as e:
        print(f"Lỗi import thư viện: {e}")
        return False
    
    return True

def check_qss():
    """Kiểm tra QSS đã tồn tại và đúng định dạng"""
    qss_file = "resources/qss/app_style.qss"
    if not os.path.exists(qss_file):
        print(f"Lỗi: File QSS {qss_file} không tồn tại")
        return False
    
    with open(qss_file, "r", encoding="utf-8") as f:
        content = f.read()
        if len(content) < 100:
            print("Cảnh báo: File QSS có vẻ quá ngắn")
    
    return True

def check_icons():
    """Kiểm tra các file icon đã tồn tại"""
    icons_folder = "resources/icons"
    if not os.path.exists(icons_folder):
        print(f"Lỗi: Thư mục {icons_folder} không tồn tại")
        return False
    
    required_icons = ["app.png", "theme.png", "play.png", "stop.png", "reset.png"]
    for icon in required_icons:
        icon_path = os.path.join(icons_folder, icon)
        if not os.path.exists(icon_path):
            print(f"Cảnh báo: Icon {icon} không tồn tại")
    
    return True

def check_dependencies():
    """Kiểm tra thư viện phụ thuộc đã được cài đặt"""
    dependencies = [
        "PyQt5", "selenium", "pandas", "matplotlib", 
        "requests", "pillow", "sqlalchemy"
    ]
    
    missing = []
    for dep in dependencies:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"Thiếu các thư viện: {', '.join(missing)}")
        print("Hãy cài đặt bằng lệnh: pip install " + " ".join(missing))
        return False
    
    return True

def create_folders():
    """Tạo các thư mục cần thiết nếu chưa tồn tại"""
    folders = [
        "data", "logs", "scripts", "downloads", "captcha",
        "resources/icons", "resources/qss"
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"Đã tạo thư mục: {folder}")

def run_checks():
    """Chạy tất cả các kiểm tra"""
    print("Đang kiểm tra cấu hình...")
    
    create_folders()
    
    checks = [
        ("File cần thiết", check_files),
        ("Imports", check_imports),
        ("File QSS", check_qss),
        ("Icons", check_icons),
        ("Thư viện phụ thuộc", check_dependencies)
    ]
    
    for name, check_func in checks:
        print(f"Kiểm tra {name}... ", end="")
        if check_func():
            print("OK")
        else:
            print("KHÔNG OK")
    
if __name__ == "__main__":
    run_checks() 
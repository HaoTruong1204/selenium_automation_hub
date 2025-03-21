import os
import sys
import time
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler()]
)

# Thêm thư mục hiện tại vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.automation_worker_fixed import EnhancedAutomationWorker
except ImportError as e:
    print(f"Lỗi import: {e}")
    sys.exit(1)

def log_handler(message):
    """Xử lý log từ worker"""
    print(f"LOG: {message}")

def progress_handler(percent):
    """Xử lý thông báo tiến trình"""
    print(f"PROGRESS: {percent}%")

def error_handler(error):
    """Xử lý lỗi"""
    print(f"ERROR: {error}")

def completed_handler():
    """Xử lý sự kiện hoàn thành"""
    print("COMPLETED: Task đã hoàn thành!")

def test_google_search():
    """Thử tìm kiếm Google với Brave Browser"""
    print("=== BẮT ĐẦU KIỂM TRA TÌM KIẾM GOOGLE VỚI BRAVE ===")
    
    # Cấu hình
    config = {
        "task": "google",
        "keyword": "brave browser automation",
        "headless": False,
        "use_stealth": True,
        "keep_browser_open": True,
        "max_results": 5,
        "chrome_config": {
            "profile_path": r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default",
            "binary_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        }
    }
    
    # Khởi tạo worker
    print("Khởi tạo worker...")
    worker = EnhancedAutomationWorker(**config)
    
    # Thiết lập các callbacks
    print("Thiết lập các signal handlers...")
    worker.log_signal.connect(log_handler)
    worker.progress_signal.connect(progress_handler)
    worker.error_signal.connect(error_handler)
    worker.finished_signal.connect(completed_handler)
    
    # Bắt đầu worker
    print("Bắt đầu worker...")
    worker.start()
    
    # Đợi worker hoàn thành
    print("Đang chờ worker hoàn thành...")
    try:
        while worker.isRunning():
            time.sleep(0.5)
            sys.stdout.write(".")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nĐã nhận Ctrl+C, đang dừng worker...")
        worker.stop()
    
    print("\n=== KẾT THÚC KIỂM TRA ===")

if __name__ == "__main__":
    test_google_search() 

import sys
import os
import logging
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings
import datetime

# Tính đường dẫn gốc của ứng dụng
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Thêm thư mục gốc vào sys.path để có thể import modules
sys.path.insert(0, BASE_DIR)

# Setup logging
def setup_logging():
    """Thiết lập cấu hình logging ban đầu"""
    # Tạo thư mục logs nếu chưa tồn tại
    log_dir = os.path.join(BASE_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Tạo tên file log theo ngày-tháng-năm
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'app_{today}.log')
    
    # Cấu hình logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Giảm log level của một số module gây noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('webdriver_manager').setLevel(logging.INFO)
    
    return logging.getLogger()

# Thiết lập logging
logger = setup_logging()
logger.info("=== KHỞI ĐỘNG ỨNG DỤNG SELENIUM AUTOMATION HUB ===")

try:
    # Import module chính
    from modules.main_window import MainWindow
    from modules.automation_worker_fixed import EnhancedAutomationWorker
    logger.info("Đã import thành công các module cần thiết")
except ImportError as e:
    logger.error(f"Lỗi khi import module: {e}")
    traceback.print_exc()
    sys.exit(1)

def main():
    """Hàm chính để khởi động ứng dụng"""
    # Thiết lập môi trường
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Tạo ứng dụng Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Selenium Automation Hub")
    app.setOrganizationName("GDU")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setStyle("Fusion")  # Sử dụng style Fusion cho giao diện nhất quán
    
    # Đặt đường dẫn icon cho ứng dụng
    icon_path = os.path.join(BASE_DIR, "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        from PyQt5.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))
    
    # Tạo cửa sổ chính
    main_window = MainWindow()
    main_window.show() 
    # Log thông tin khởi động
    logger.info(f"Giao diện ứng dụng đã được khởi động thành công")
    
    # Chạy event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
        
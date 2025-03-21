import os
import logging
import datetime

def setup_logging(log_level=logging.INFO):
    """
    Thiết lập logging với định dạng và mức độ cụ thể
    """
    # Tạo thư mục logs nếu chưa tồn tại
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Tạo tên file log theo ngày-tháng-năm
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'app_{today}.log')
    
    # Cấu hình logging
    logging.basicConfig(
        level=log_level,
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
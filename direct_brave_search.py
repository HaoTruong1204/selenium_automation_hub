import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def direct_brave_search():
    """Khởi động Brave trực tiếp và tìm kiếm Google"""
    print("=== KHỞI ĐỘNG BRAVE BROWSER VÀ TÌM KIẾM GOOGLE ===")
    
    # Đường dẫn Brave Browser
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    
    # Kiểm tra đường dẫn Brave
    if not os.path.exists(brave_path):
        print(f"❌ Không tìm thấy Brave tại: {brave_path}")
        return
        
    print(f"✅ Đã tìm thấy Brave tại: {brave_path}")
    
    # Thiết lập ChromeDriver
    print("Thiết lập ChromeDriver...")
    chromedriver_path = ChromeDriverManager().install()
    
    # Thiết lập options
    print("Cấu hình options cho Brave...")
    options = Options()
    options.binary_location = brave_path
    
    # Cấu hình cơ bản
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Thiết lập profile
    profile_path = r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default"
    if os.path.exists(os.path.dirname(profile_path)):
        options.add_argument(f"--user-data-dir={os.path.dirname(profile_path)}")
        options.add_argument(f"--profile-directory={os.path.basename(profile_path)}")
        print(f"✅ Sử dụng profile: {profile_path}")
    
    # Tạo service
    service = Service(chromedriver_path)
    
    # Khởi tạo driver
    print("Khởi động Brave Browser...")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Truy cập Google
        print("Đang truy cập Google...")
        driver.get("https://www.google.com")
        
        # Chờ trang load
        time.sleep(2)
        
        # Tìm kiếm
        print("Đang tìm kiếm...")
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys("brave browser selenium")
        search_box.send_keys(Keys.RETURN)
        
        # Chờ kết quả
        time.sleep(3)
        
        # Lấy tiêu đề trang
        print(f"Tiêu đề trang: {driver.title}")
        
        # Kiểm tra xem có sử dụng Brave không
        print("Kiểm tra thông tin trình duyệt...")
        driver.get("chrome://version")
        time.sleep(3)
        
        page_source = driver.page_source.lower()
        if "brave" in page_source:
            print("✅ Xác nhận đang sử dụng Brave Browser!")
        else:
            print("⚠️ Có thể không sử dụng Brave Browser!")
        
        # Đợi người dùng xem kết quả
        print("\nĐang giữ trình duyệt mở trong 10 giây...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    finally:
        # Đóng driver
        print("Đóng trình duyệt...")
        driver.quit()
        
    print("=== KẾT THÚC ===")

if __name__ == "__main__":
    direct_brave_search() 
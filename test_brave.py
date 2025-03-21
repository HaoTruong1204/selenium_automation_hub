import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_brave_browser():
    """Test khởi chạy Brave Browser với Selenium"""
    
    print("1. Kiểm tra đường dẫn Brave...")
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    
    if not os.path.exists(brave_path):
        print(f"❌ Không tìm thấy Brave tại đường dẫn: {brave_path}")
        return
        
    print(f"✅ Đã tìm thấy Brave tại: {brave_path}")
    
    print("\n2. Kiểm tra phiên bản Brave...")
    try:
        result = subprocess.run([brave_path, "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               timeout=5)
        version_output = result.stdout.strip()
        print(f"✅ Thông tin phiên bản: {version_output}")
    except Exception as e:
        print(f"❌ Lỗi khi lấy phiên bản: {e}")
    
    print("\n3. Thiết lập ChromeDriver...")
    try:
        # Cài đặt ChromeDriver mới nhất
        chromedriver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver: {chromedriver_path}")
    except Exception as e:
        print(f"❌ Lỗi cài đặt ChromeDriver: {e}")
        return
    
    print("\n4. Cấu hình và khởi chạy Brave...")
    try:
        # Thiết lập options
        options = Options()
        options.binary_location = brave_path
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Đặt user-agent giống thật
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        
        # Thiết lập driver
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Đã khởi tạo trình duyệt!")
        
        # Mở trang web
        print("\n5. Thử truy cập Google...")
        driver.get("https://www.google.com")
        print(f"✅ Tiêu đề trang: {driver.title}")
        
        # Kiểm tra xem có đang thực sự sử dụng Brave
        print("\n6. Kiểm tra thông tin trình duyệt...")
        driver.get("chrome://version")
        time.sleep(3)
        page_source = driver.page_source.lower()
        
        if "brave" in page_source:
            print("✅ Xác nhận đang sử dụng Brave Browser!")
        else:
            print("⚠️ Có thể đang sử dụng Chrome thay vì Brave!")
            
        # Chờ 5 giây để xem kết quả
        print("\nĐang giữ trình duyệt mở trong 5 giây để kiểm tra...")
        time.sleep(5)
        
        # Đóng trình duyệt
        driver.quit()
        print("✅ Đã đóng trình duyệt")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        
if __name__ == "__main__":
    test_brave_browser() 
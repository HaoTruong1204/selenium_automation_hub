# Script tự động tạo bởi Selenium Automation Hub

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def run(driver):
    """
    Hàm chính để chạy script. Nhận tham số là một WebDriver đã khởi tạo.
    Trả về danh sách kết quả (nếu có).
    """
    try:
        # Mở trang web
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # Tìm ô tìm kiếm và nhập từ khóa
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys("Selenium Python automation")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Lấy kết quả
        results = []
        search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        for i, result in enumerate(search_results[:5]):
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h3")
                title = title_element.text
                
                link_element = result.find_element(By.CSS_SELECTOR, "a")
                link = link_element.get_attribute("href")
                
                results.append((title, link))
            except:
                continue
                
        return results
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return []

# Nếu chạy trực tiếp file này
if __name__ == "__main__":
    # Khởi tạo driver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Chạy script
        results = run(driver)
        
        # In kết quả
        print("\nKết quả:")
        for i, (title, link) in enumerate(results):
            print(f"{i+1}. {title}\n   {link}\n")
            
    finally:
        # Đóng driver
        driver.quit()

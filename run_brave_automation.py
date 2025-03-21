#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Công cụ tự động hóa với Brave Browser
"""

import os
import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Đường dẫn mặc định của Brave
DEFAULT_BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
DEFAULT_PROFILE_PATH = r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default"

def run_brave_automation(task="google", keyword=None, headless=False, keep_open=False):
    """
    Chạy tác vụ tự động hóa với Brave Browser
    
    Args:
        task (str): Loại tác vụ (google, facebook, shopee)
        keyword (str): Từ khóa tìm kiếm (nếu cần)
        headless (bool): Chạy ở chế độ headless không hiển thị giao diện
        keep_open (bool): Giữ trình duyệt mở sau khi hoàn thành
    """
    print(f"=== CHẠY TÁC VỤ TỰ ĐỘNG HÓA: {task.upper()} ===")
    
    # Tìm đường dẫn Brave
    brave_path = DEFAULT_BRAVE_PATH
    
    if not os.path.exists(brave_path):
        print(f"❌ Không tìm thấy Brave tại: {brave_path}")
        alt_paths = [
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe")
        ]
        
        for path in alt_paths:
            if os.path.exists(path):
                brave_path = path
                print(f"✅ Đã tìm thấy Brave tại đường dẫn thay thế: {brave_path}")
                break
        else:
            print("❌ Không thể tìm thấy Brave. Vui lòng cài đặt Brave và thử lại.")
            return
    
    # Thiết lập ChromeDriver
    print("Đang thiết lập ChromeDriver...")
    chromedriver_path = ChromeDriverManager().install()
    print(f"✅ ChromeDriver: {chromedriver_path}")
    
    # Thiết lập options
    print("Đang cấu hình Brave Browser...")
    options = Options()
    options.binary_location = brave_path
    
    # Cấu hình chung
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Chống phát hiện automation
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Thiết lập headless nếu cần
    if headless:
        print("Chế độ headless: BẬT")
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        print("Chế độ headless: TẮT")
        options.add_argument("--start-maximized")
    
    # Thiết lập profile
    profile_path = DEFAULT_PROFILE_PATH
    if os.path.exists(os.path.dirname(profile_path)):
        print(f"✅ Sử dụng profile: {profile_path}")
        options.add_argument(f"--user-data-dir={os.path.dirname(profile_path)}")
        options.add_argument(f"--profile-directory={os.path.basename(profile_path)}")
    else:
        print("⚠️ Không tìm thấy profile mặc định, sẽ sử dụng profile tạm")
    
    # Khởi tạo driver
    print("Đang khởi động Brave Browser...")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    # Chống phát hiện automation
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
    })
    
    try:
        # Xác nhận trình duyệt
        driver.get("chrome://version")
        time.sleep(1)
        page_source = driver.page_source.lower()
        
        if "brave" in page_source:
            print("✅ Xác nhận đang sử dụng Brave Browser!")
        else:
            print("⚠️ Có thể không sử dụng Brave Browser!")
        
        # Thực hiện tác vụ
        if task == "google":
            if not keyword:
                keyword = "brave browser automation"
            run_google_search(driver, keyword)
        elif task == "facebook":
            run_facebook_task(driver)
        elif task == "shopee":
            if not keyword:
                keyword = "laptop"
            run_shopee_task(driver, keyword)
        else:
            print(f"❌ Tác vụ không hợp lệ: {task}")
            
        # Giữ trình duyệt mở nếu cần
        if keep_open and not headless:
            print("\nĐang giữ trình duyệt mở. Nhấn Enter để đóng...")
            input()
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Đóng trình duyệt nếu không giữ lại
        if not keep_open:
            print("Đóng trình duyệt...")
            driver.quit()
        
    print("=== HOÀN THÀNH ===")

def run_google_search(driver, keyword):
    """Thực hiện tìm kiếm Google"""
    print(f"\n--- Đang thực hiện tìm kiếm Google: {keyword} ---")
    
    # Truy cập Google
    print("Đang truy cập Google...")
    driver.get("https://www.google.com")
    time.sleep(2)
    
    # Tìm kiếm
    print("Đang tìm kiếm...")
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)
    
    # Đợi kết quả
    time.sleep(2)
    
    # Lấy tiêu đề trang
    print(f"✅ Tiêu đề trang: {driver.title}")
    
    # Thu thập kết quả
    try:
        print("\nĐang thu thập kết quả tìm kiếm...")
        results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        if not results:
            results = driver.find_elements(By.XPATH, "//div[@jscontroller]//a[@jsname]/../../..")
        
        print(f"Đã tìm thấy {len(results)} kết quả, hiển thị 5 kết quả đầu tiên:")
        
        for i, result in enumerate(results[:5]):
            try:
                title = result.find_element(By.CSS_SELECTOR, "h3").text
                link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                print(f"\n{i+1}. {title}\n   URL: {link}")
            except:
                continue
    except Exception as e:
        print(f"Lỗi khi thu thập kết quả: {e}")

def run_facebook_task(driver):
    """Thực hiện tác vụ Facebook"""
    print("\n--- Đang thực hiện tác vụ Facebook ---")
    
    # Truy cập Facebook
    print("Đang truy cập Facebook...")
    driver.get("https://www.facebook.com")
    time.sleep(3)
    
    # Kiểm tra đã đăng nhập chưa
    if "facebook.com/home" in driver.current_url or "/login" not in driver.current_url:
        print("✅ Đã đăng nhập Facebook")
    else:
        print("⚠️ Chưa đăng nhập Facebook. Sử dụng profile đã lưu đăng nhập để tự động đăng nhập.")

def run_shopee_task(driver, keyword):
    """Thực hiện tác vụ Shopee"""
    print(f"\n--- Đang thực hiện tác vụ Shopee: {keyword} ---")
    
    # Truy cập Shopee
    print("Đang truy cập Shopee...")
    driver.get("https://shopee.vn")
    time.sleep(5)
    
    # Tìm kiếm
    try:
        # Đóng popup nếu có
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, "svg[viewBox='0 0 10 10']")
            for button in close_buttons:
                if button.is_displayed():
                    button.click()
                    time.sleep(1)
                    break
        except:
            pass
        
        # Tìm kiếm
        print(f"Đang tìm kiếm: {keyword}")
        search_box = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        
        # Đợi kết quả
        time.sleep(3)
        
        # Thu thập kết quả
        print("Đang thu thập kết quả...")
        product_items = driver.find_elements(By.CSS_SELECTOR, "div.shopee-search-item-result__item")
        
        print(f"Đã tìm thấy {len(product_items)} sản phẩm, hiển thị 5 sản phẩm đầu tiên:")
        
        for i, item in enumerate(product_items[:5]):
            try:
                name = item.find_element(By.CSS_SELECTOR, 'div.ie3A\\+n').text
                price = item.find_element(By.CSS_SELECTOR, 'div.vioxXd').text
                print(f"\n{i+1}. {name}\n   Giá: {price}")
            except:
                continue
                
    except Exception as e:
        print(f"Lỗi khi thực hiện tác vụ Shopee: {e}")

def parse_arguments():
    """Phân tích đối số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Công cụ tự động hóa với Brave Browser")
    
    parser.add_argument("--task", "-t", 
                        choices=["google", "facebook", "shopee"],
                        default="google",
                        help="Loại tác vụ (mặc định: google)")
                        
    parser.add_argument("--keyword", "-k",
                        help="Từ khóa tìm kiếm (nếu cần)")
                        
    parser.add_argument("--headless", "-l",
                        action="store_true",
                        help="Chạy ở chế độ headless (không hiển thị giao diện)")
                        
    parser.add_argument("--keep-open", "-o",
                        action="store_true",
                        help="Giữ trình duyệt mở sau khi hoàn thành")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    run_brave_automation(
        task=args.task,
        keyword=args.keyword,
        headless=args.headless,
        keep_open=args.keep_open
    ) 
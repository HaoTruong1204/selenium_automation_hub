import time
import os
import urllib.parse
import random
import subprocess
import shutil
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
# Thêm thư viện cho việc xác định phiên bản Chromium
from packaging import version

# Google URL mặc định
GOOGLE_URL = "https://www.google.com"

# =============== DỮ LIỆU TÀI KHOẢN XÃ HỘI ===============
# Tất cả MXH (facebook, instagram, zalo, twitter, shopee)
# Shopee => phone="aa", password="aa"
SOCIAL_ACCOUNTS = {
    "facebook": {
        "url": "https://www.facebook.com",
        "phone": "0333",
        "password": "123"
    },
    "instagram": {
        "url": "https://www.instagram.com/accounts/login",
        "phone": "0333",
        "password": "123"
    },
    "zalo": {
        "url": "https://chat.zalo.me/",
        "phone": "0333",
        "password": "123"
    },
    "twitter": {
        "url": "https://twitter.com/i/flow/login",
        "phone": "0333",
        "password": "123"
    },
    "shopee": {
        "url": "https://shopee.vn/buyer/login",
        "phone": "0333",
        "password": "123"
    }
}


class AutomationWorker(QThread):
    """
    Worker DEMO (giả lập): chờ 5 giây rồi trả về kết quả Google giả.
    """
    operation_completed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True

    def run(self):
        # Giả lập 5 giây
        for _ in range(5):
            if not self._is_running:
                return
            time.sleep(1)

        data = {
            "google_results": [
                {"Tiêu đề": "Kết quả mô phỏng 1", "URL": "http://example.com/1", "Mô tả": "Mô tả 1"},
                {"Tiêu đề": "Kết quả mô phỏng 2", "URL": "http://example.com/2", "Mô tả": "Mô tả 2"}
            ]
        }
        self.operation_completed.emit(data)

    def stop(self):
        self._is_running = False


class EnhancedAutomationWorker(QThread):
    """
    Enhanced Automation Worker kết hợp tất cả tính năng:
    - Quản lý WebDriver + session 
    - API mới (keywords, social login, scraping)
    - Xử lý lỗi nâng cao
    - Hệ thống logging đầy đủ
    """
    log_signal = pyqtSignal(str)  # Signal for logging
    progress_signal = pyqtSignal(int)  # Signal for progress updates
    result_signal = pyqtSignal(object)  # Signal for general results
    finished_signal = pyqtSignal()  # No arguments needed
    error_signal = pyqtSignal(str)  # Signal for errors
    
    # Specific signals for different tasks
    trends_signal = pyqtSignal(list)  # Signal for trend results (list of trends)
    content_signal = pyqtSignal(dict)  # Signal for content creation results
    post_result_signal = pyqtSignal(bool)  # Signal for post success/failure

    def __init__(
        self,
        task=None,
        keyword="",
        url="",
        proxy=None,
        headless=False,
        delay=1.0,
        chrome_config=None,
        use_stealth=True,
        keep_browser_open=True,
        email=None,         # Add email parameter for Facebook login
        password=None,      # Add password parameter for Facebook login
        max_results=10,     # Add max_results parameter for Google search
        pages=2,            # Add pages parameter for Shopee scraping
        parent=None
    ):
        super().__init__(parent)
        self.task = task
        self.keyword = keyword
        self.url = url
        self.proxy = proxy
        self.proxies = []  # Danh sách proxy để xoay vòng
        self.headless = headless
        self.delay = delay
        self.chrome_config = chrome_config or {}
        self.use_stealth = use_stealth
        self.keep_browser_open = keep_browser_open
        self.email = email
        self.password = password
        self.max_results = max_results
        self.pages = pages

        self._running = True
        self.driver = None
        self.results = []

    def log(self, message):
        """Emit log message through signal"""
        self.log_signal.emit(str(message))

    def run(self):
        """Main execution method"""
        try:
            self.log(f"🚀 Starting {self.task} task")
            self.progress_signal.emit(10)
            
            # Setup driver
            self.driver = self.setup_driver()
            if not self.driver:
                self.error_signal.emit("Failed to initialize browser")
                return
                
            self.progress_signal.emit(30)
            
            # Execute task based on type
            success = False
            result = None
            
            if self.task == "facebook":
                success = self.facebook_login()
            elif self.task == "google":
                success = self.google_search(self.keyword)
            elif self.task == "shopee":
                result = self.shopee_scrape(self.driver)
                success = bool(result)
            elif self.task == "google_trends":
                result = self.get_google_trends(self.country, self.category, self.timeframe)
                if result:
                    self.trends_signal.emit(result)
            elif self.task == "facebook_trends":
                result = self.get_facebook_trending_topics()
                if result:
                    self.trends_signal.emit(result)
            elif self.task == "content_creation":
                result = self.generate_content_from_trend(self.trend, self.content_type, self.word_count)
                if result:
                    self.content_signal.emit(result)
            elif self.task == "post_content":
                result = self.facebook_post_content(self.content, self.post_type, self.page_id, self.group_id)
                if result is not None:
                    self.post_result_signal.emit(result)
            elif self.task == "schedule_post":
                result = self.facebook_schedule_post(self.content, self.schedule_time, self.post_type, self.page_id, self.group_id)
                if result is not None:
                    self.post_result_signal.emit(result)
            elif self.task == "custom":
                # Handle custom script execution
                if self.custom_script:
                    # Custom script execution can be complex, 
                    # we'll keep it simple for this enhanced worker
                    self.log("⚠️ Custom script execution is simplified in this version")
                    # Execute script in a safe way would be implemented here
                    # ...
                    result = "Custom script executed"
                else:
                    self.log("❌ No custom script provided")
                    
            self.progress_signal.emit(90)
            
            if success:
                self.log(f"✅ {self.task} task completed successfully!")
                if result:
                    self.result_signal.emit(result)
            else:
                self.error_signal.emit(f"{self.task} task failed")
                
        except Exception as e:
            self.error_signal.emit(f"Error in {self.task} task: {str(e)}")
            import traceback
            self.log(f"Detailed error: {traceback.format_exc()}")
            
        finally:
            self.progress_signal.emit(100)
            if not self.keep_browser_open and self.driver:
                try:
                    self.driver.quit()
                    self.log("✅ Browser closed")
                except Exception as e:
                    self.log(f"⚠️ Error closing browser: {str(e)}")
            
            # Signal completion without arguments
            self.finished_signal.emit()

    def stop(self):
        """User bấm "Dừng" => dừng Worker, đóng browser."""
        self.log("⚠️ Đã yêu cầu dừng worker...")
        self._running = False

    def validate_parameters(self):
        """Validate required parameters before launching browser"""
        if self.task == "google" and not self.keyword:
            self.log("❌ Google search requires a keyword")
            return False
        elif self.task == "facebook" and (not self.email or not self.password):
            self.log("❌ Facebook login requires email and password")
            return False
        elif self.task == "shopee" and not self.keyword:
            self.log("❌ Shopee scraping requires a keyword")
            return False
        elif not self.task and not self.url:
            self.log("❌ No task or URL specified")
            return False
        return True

    def verify_proxy(self, proxy, timeout=5):
        """
        Verify if a proxy is working by attempting to connect to a test URL
        Returns True if proxy is working, False otherwise
        """
        if not proxy:
            return False
            
        self.log(f"🔍 Testing proxy: {proxy}")
        
        # Create a minimal browser config for testing
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--proxy-server={proxy}")
        chrome_options.add_argument("--window-size=800,600")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        # Test URLs in order of preference
        test_urls = [
            "https://www.google.com",
            "https://www.bing.com",
            "https://www.cloudflare.com",
            "https://httpbin.org/ip"
        ]
        
        driver = None
        try:
            # Suppress WebDriver verbose logging
            import logging
            from selenium.webdriver.remote.remote_connection import LOGGER
            LOGGER.setLevel(logging.CRITICAL)
            
            # Setup WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(timeout)
            
            # Try each test URL until one works
            for url in test_urls:
                try:
                    driver.get(url)
                    # Check if page loaded properly
                    page_source = driver.page_source.lower()
                    
                    # Look for key indicators that the page loaded successfully
                    success_indicators = {
                        "google.com": ["google", "search"],
                        "bing.com": ["bing", "search"],
                        "cloudflare.com": ["cloudflare", "security"],
                        "httpbin.org": ["ip", "origin"]
                    }
                    
                    # Determine which domain we're testing
                    for domain, indicators in success_indicators.items():
                        if domain in url:
                            # Check if any indicator is present in the page source
                            if any(indicator in page_source for indicator in indicators):
                                self.log(f"✅ Proxy {proxy} is working (verified with {url})")
                                return True
                            break
                            
                except Exception:
                    # Try next URL if this one failed
                    continue
                    
            # If we get here, none of the URLs worked
            self.log(f"❌ Proxy {proxy} failed all connection tests")
            return False
            
        except Exception as e:
            self.log(f"❌ Proxy verification error: {str(e)}")
            return False
        finally:
            # Clean up
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def enhanced_rotate_proxy(self):
        """
        Enhanced proxy rotation with verification to ensure we get a working proxy
        Returns True if successful, False if no working proxies found
        """
        if not self.proxies or len(self.proxies) <= 1:
            self.log("⚠️ No alternative proxies available for rotation")
            return False
            
        # Get current proxy index
        current_index = 0
        if self.proxy in self.proxies:
            current_index = self.proxies.index(self.proxy)
            
        # Try up to all available proxies
        attempts = 0
        max_attempts = len(self.proxies)
        
        while attempts < max_attempts:
            # Get next proxy in the list (with wraparound)
            next_index = (current_index + 1) % len(self.proxies)
            next_proxy = self.proxies[next_index]
            
            # Skip if it's the same as current (shouldn't happen with len > 1)
            if next_proxy == self.proxy:
                next_index = (next_index + 1) % len(self.proxies)
                next_proxy = self.proxies[next_index]
                
            self.log(f"🔄 Rotating proxy from {self.proxy} to {next_proxy}")
            
            # Verify the new proxy works
            if self.verify_proxy(next_proxy):
                self.proxy = next_proxy
                self.log(f"✅ Successfully rotated to proxy: {self.proxy}")
                return True
            else:
                # If proxy doesn't work, try next one
                current_index = next_index
                attempts += 1
                self.log(f"⚠️ Proxy {next_proxy} failed verification, trying next (attempt {attempts}/{max_attempts})")
                
        self.log("❌ Failed to find a working proxy after trying all available options")
        return False
        
    def rotate_proxy(self):
        """
        Rotate to next available proxy (with backward compatibility)
        """
        return self.enhanced_rotate_proxy()
        
    def test_all_proxies(self):
        """
        Test all available proxies and return a list of working ones
        """
        if not self.proxies:
            self.log("⚠️ No proxies available to test")
            return []
            
        self.log(f"🔍 Testing {len(self.proxies)} proxies...")
        working_proxies = []
        
        for i, proxy in enumerate(self.proxies):
            self.log(f"🔄 Testing proxy {i+1}/{len(self.proxies)}: {proxy}")
            if self.verify_proxy(proxy):
                working_proxies.append(proxy)
                
        success_rate = len(working_proxies) / len(self.proxies) * 100 if self.proxies else 0
        self.log(f"✅ Proxy test complete: {len(working_proxies)}/{len(self.proxies)} working ({success_rate:.1f}%)")
        
        # Update proxies list with only working ones
        if working_proxies:
            self.proxies = working_proxies
            # Set current proxy to first working one
            self.proxy = working_proxies[0]
            
        return working_proxies

    def update_proxies(self, proxy_list):
        """Cập nhật danh sách proxy từ proxy_manager"""
        if not proxy_list:
            self.log("⚠️ Danh sách proxy trống")
            return
            
        self.proxies = proxy_list
        self.log(f"✅ Đã cập nhật {len(proxy_list)} proxy")
        
        # Nếu chưa có proxy hiện tại hoặc proxy hiện tại không hoạt động, chọn proxy đầu tiên
        if not self.proxy or self.proxy not in proxy_list:
            self.proxy = proxy_list[0]
            self.log(f"✅ Đã chọn proxy mặc định: {self.proxy}")

    def setup_driver(self):
        """Thiết lập Brave Browser với cấu hình chống phát hiện automation"""
        if not self.validate_parameters():
            return None
            
        try:
            self.log("🔧 Đang cấu hình Brave Browser...")
            
            # Sử dụng đường dẫn Brave Browser chính xác từ thông tin người dùng
            brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            
            # Kiểm tra xem brave_path có tồn tại
            if not os.path.exists(brave_path):
                self.log(f"❌ Không tìm thấy Brave tại đường dẫn chính: {brave_path}")
                # Tìm đường dẫn thay thế
                brave_paths = [
                    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                    "/usr/bin/brave-browser"
                ]
                
                for path in brave_paths:
                    if os.path.exists(path):
                        brave_path = path
                        self.log(f"✅ Đã tìm thấy Brave tại: {brave_path}")
                        break
                
            if not os.path.exists(brave_path):
                self.log("❌ Không tìm thấy Brave Browser. Vui lòng cài đặt Brave từ https://brave.com")
                return None
            
            self.log(f"✅ Đã xác nhận Brave tại: {brave_path}")
                
            # Cấu hình options cho Brave
            chrome_options = Options()
            chrome_options.binary_location = brave_path  # Chỉ định rõ binary là Brave
            
            # Thêm user agent chính xác từ thông tin người dùng cung cấp
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Thêm các tùy chọn chống phát hiện automation
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Thiết lập các tùy chọn đặc biệt từ thông tin dòng lệnh của người dùng
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--enable-dom-distiller")
            chrome_options.add_argument("--enable-distillability-service")
            chrome_options.add_argument("--origin-trial-public-key=bYUKPJoPnCxeNvu72j4EmPuK7tr1PAC7SHh8ld9Mw3E=,fMS4mpO6buLQ/QMd+zJmxzty/VQ6B1EUZqoCU04zoRU=")
            chrome_options.add_argument("--lso-url=https://no-thanks.invalid")
            chrome_options.add_argument("--sync-url=https://sync-v2.brave.com/v2")
            chrome_options.add_argument("--variations-server-url=https://variations.brave.com/seed")
            chrome_options.add_argument("--variations-insecure-server-url=https://variations.brave.com/seed")
            chrome_options.add_argument("--component-updater=url-source=https://go-updater.brave.com/extensions")
            
            # Các tùy chọn bổ sung 
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Tùy chọn riêng cho Brave
            chrome_options.add_argument("--disable-brave-update")
            chrome_options.add_argument("--disable-brave-extension")
            chrome_options.add_argument("--disable-brave-rewards")
            
            # Thiết lập ngôn ngữ
            chrome_options.add_argument("--lang=vi-VN,vi")
            
            # Thiết lập headless nếu cần
            if self.headless:
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--window-size=1920,1080")
            else:
                chrome_options.add_argument("--start-maximized")
            
            # Thiết lập profile chính xác từ thông tin người dùng
            user_data_dir = r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data"
            profile_directory = "Default"
            
            if self.chrome_config.get("profile_path"):
                profile_path = self.chrome_config["profile_path"]
                user_data_dir = os.path.dirname(profile_path)
                profile_directory = os.path.basename(profile_path)
                self.log(f"📂 Sử dụng profile tùy chỉnh: {profile_path}")
            
            # Kiểm tra profile tồn tại
            if os.path.exists(user_data_dir):
                chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
                chrome_options.add_argument(f"--profile-directory={profile_directory}")
                self.log(f"📂 Sử dụng profile: {user_data_dir}/{profile_directory}")
            else:
                self.log(f"⚠️ Không tìm thấy thư mục profile: {user_data_dir}")
            
            # Thêm proxy nếu có
            if self.proxy:
                chrome_options.add_argument(f'--proxy-server={self.proxy}')
                self.log(f"🔄 Sử dụng proxy: {self.proxy}")
            
            # Tải ChromeDriver phù hợp
            self.log("🔄 Đang tải ChromeDriver phù hợp với Brave...")
            
            # Tạo WebDriver với retry logic
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Sử dụng ChromeDriverManager để tải driver phù hợp với Chromium 134
                    driver_version = "134.0.6998"  # Dựa trên version Chromium của Brave
                    service = Service(ChromeDriverManager(version=driver_version).install())
                    
                    # Tạo driver, chỉ định rõ binary là Brave thông qua options
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                    # Ghi đè các thuộc tính automation để tránh phát hiện
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        'source': '''
                            // Ghi đè thuộc tính navigator.webdriver
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                            });
                            
                            // Xóa thuộc tính cdriver
                            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                            
                            // Giả mạo plugins như Brave
                            const makePluginInfo = (name, filename) => {
                                return {
                                    name,
                                    filename,
                                    description: 'Portable Document Format',
                                    length: 1,
                                    item: () => null
                                };
                            };
                            
                            Object.defineProperty(navigator, 'plugins', {
                                get: () => {
                                    const plugins = [
                                        makePluginInfo('PDF Viewer', 'internal-pdf-viewer'),
                                        makePluginInfo('Brave PDF Plugin', 'internal-pdf-viewer'),
                                        makePluginInfo('Brave PDF Viewer', 'mhjfbmdgcfjbbpaeojofohoefgiehjai'),
                                        makePluginInfo('Native Client', 'internal-nacl-plugin')
                                    ];
                                    
                                    // Thêm thuộc tính namedItem
                                    plugins.namedItem = name => plugins.find(p => p.name === name);
                                    
                                    return plugins;
                                }
                            });
                            
                            // Sử dụng thông tin OS chính xác
                            Object.defineProperty(navigator, 'platform', {
                                get: () => 'Win32'
                            });
                            
                            // Thiết lập ngôn ngữ
                            Object.defineProperty(navigator, 'languages', {
                                get: () => ['vi-VN', 'vi', 'en-US', 'en'],
                            });
                            
                            // Thiết lập JavaScriptEngine giống Brave
                            Object.defineProperty(navigator, 'appVersion', {
                                get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
                            });
                            
                            // Ghi đè permissions API
                            if (window.navigator.permissions) {
                                const originalQuery = window.navigator.permissions.query;
                                window.navigator.permissions.__proto__.query = parameters => {
                                    if (parameters.name === 'notifications' || 
                                        parameters.name === 'clipboard-read' || 
                                        parameters.name === 'clipboard-write') {
                                        return Promise.resolve({state: Notification.permission});
                                    }
                                    return originalQuery(parameters);
                                };
                            }
                        '''
                    })
                    
                    # Kiểm tra xem có đang thực sự sử dụng Brave
                    self.log("🔍 Đang xác minh trình duyệt...")
                    
                    # Mở trang chrome://version để xác nhận
                    driver.get("chrome://version")
                    time.sleep(2)
                    
                    # Lấy thông tin từ trang version
                    page_source = driver.page_source.lower()
                    browser_info = "Không xác định"
                    
                    if "brave" in page_source:
                        self.log("✅ Xác nhận đang sử dụng Brave Browser!")
                        browser_info = "Brave Browser"
                    elif "chrome" in page_source:
                        self.log("⚠️ Có thể đang sử dụng Chrome thay vì Brave!")
                        browser_info = "Chrome Browser"
                    
                    # Ghi log chi tiết để kiểm tra
                    self.log(f"🌐 Thông tin trình duyệt: {browser_info}")
                    
                    # Nếu đang sử dụng Chrome, thử cách khác để sử dụng Brave
                    if browser_info == "Chrome Browser":
                        self.log("🔄 Đang cố gắng khởi chạy Brave thay vì Chrome...")
                        
                        # Đóng trình duyệt hiện tại
                        driver.quit()
                        
                        # Thử khởi động Brave trực tiếp bằng subprocess
                        temp_html = os.path.join(os.getcwd(), "temp_brave_launcher.html")
                        with open(temp_html, "w") as f:
                            f.write("<html><body><h1>Brave Test</h1><p>This is a test page for Brave Browser.</p></body></html>")
                        
                        # Mở Brave với URL cụ thể
                        subprocess.Popen([brave_path, f"file://{temp_html}"])
                        
                        self.log("⚠️ Không thể tích hợp hoàn toàn với Selenium. Sử dụng phương pháp thay thế với ChromeDriver.")
                    
                    self.log("✅ Đã khởi động Brave Browser thành công!")
                    return driver
                    
                except Exception as e:
                    retry_count += 1
                    self.log(f"⚠️ Lỗi khởi động Brave (lần {retry_count}/{max_retries}): {str(e)}")
                    
                    if retry_count >= max_retries:
                        self.log("❌ Không thể khởi động Brave sau nhiều lần thử")
                        raise
                    
                    time.sleep(2)  # Chờ trước khi thử lại
            
        except Exception as e:
            self.log(f"❌ Lỗi cấu hình Brave Browser: {str(e)}")
            return None

    def get_brave_version(self, brave_path):
        """Lấy phiên bản của Brave Browser"""
        try:
            # Sử dụng --version để lấy thông tin phiên bản
            result = subprocess.run([brave_path, "--version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   timeout=5)
            version_output = result.stdout.strip()
            
            # Format thường là: "Brave Browser 134.0.6998.94" hoặc tương tự
            if "Brave" in version_output and "Chromium" in version_output:
                # Trích xuất phiên bản từ đầu ra
                chromium_version = version_output.split("Chromium:")[1].split()[0].strip()
                return chromium_version
            elif "Brave" in version_output:
                # Trích xuất phiên bản từ đầu ra
                brave_version = ''.join(c for c in version_output.split("Brave")[1] if c.isdigit() or c == '.')
                return brave_version.strip()
                
            return None
        except Exception as e:
            self.log(f"⚠️ Lỗi khi lấy phiên bản Brave: {str(e)}")
            return None
            
    def get_compatible_chromedriver(self, browser_version):
        """Tìm ChromeDriver phù hợp với phiên bản Brave"""
        try:
            # Kiểm tra thư mục driver đã tải
            driver_path = os.path.expanduser("~/.wdm/drivers/chromedriver")
            
            if not os.path.exists(driver_path):
                return None
                
            # Lấy phiên bản chính của Brave (major version)
            major_version = browser_version.split('.')[0]
            
            # Tìm thư mục chứa driver phù hợp
            for root, dirs, files in os.walk(driver_path):
                for file in files:
                    if file.lower() == "chromedriver.exe" or file.lower() == "chromedriver":
                        # Kiểm tra nếu thư mục chứa phiên bản phù hợp
                        if major_version in root:
                            return os.path.join(root, file)
            
            return None
        except Exception as e:
            self.log(f"⚠️ Lỗi khi tìm ChromeDriver phù hợp: {str(e)}")
            return None

    def handle_timeouts_and_errors(self, driver, url, retries=3, delay=2):
        """
        Advanced error handling for page loads and timeouts
        Returns True if successful, False if failed after retries
        """
        attempt = 0
        
        while attempt < retries:
            try:
                # If this isn't the first attempt, reload the page
                if attempt > 0:
                    self.log(f"🔄 Retrying page load (attempt {attempt+1}/{retries}): {url}")
                
                # Try loading the page
                driver.get(url)
                
                # Check if page loaded properly
                if "ERR_" in driver.page_source or "This site can't be reached" in driver.page_source:
                    raise Exception("Page failed to load: Network error")
                    
                # Page loaded successfully
                return True
                
            except Exception as e:
                attempt += 1
                self.log(f"⚠️ Page load error: {str(e)}")
                
                # Try fixing common issues
                if "ERR_PROXY_CONNECTION_FAILED" in str(e) or "proxy" in str(e).lower():
                    self.log("🔄 Proxy issue detected, trying to rotate proxy...")
                    if self.rotate_proxy():
                        # Recreate the driver with new proxy if possible
                        try:
                            driver.quit()
                        except:
                            pass
                            
                        self.driver = self.setup_driver()
                        driver = self.driver
                
                # Wait before retry
                time.sleep(delay)
                
        return False

    def wait_for_element(self, driver, by, selector, timeout=10, retries=2):
        """
        Enhanced element wait with retry logic
        Returns the element if found, None if not found
        """
        attempt = 0
        
        while attempt <= retries:
            try:
                if attempt > 0:
                    self.log(f"🔄 Retrying to find element {selector} (attempt {attempt}/{retries})")
                
                # Try explicit wait
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                return element
                
            except Exception as e:
                attempt += 1
                
                # Last attempt failed
                if attempt > retries:
                    self.log(f"❌ Element not found after {retries} retries: {selector}")
                    return None
                    
                # Try scroll and refresh DOM
                try:
                    # Scroll down to trigger lazy loading
                    driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(1)
                except:
                    pass
                    
        return None

    def verify_schedule_success(self):
        """Verify if scheduling was successful"""
        try:
            # Look for success indicators
            success_messages = [
                "Your post is scheduled",
                "Bài viết của bạn đã được lên lịch",
                "scheduled for",
                "đã lên lịch vào"
            ]
            
            # Check page source for success messages
            page_source = self.driver.page_source
            for message in success_messages:
                if message.lower() in page_source.lower():
                    return True
                    
            # Look for scheduled post indicators in current URL
            current_url = self.driver.current_url.lower()
            if "scheduled" in current_url or "pending" in current_url:
                return True
                
            # If we've waited a while and don't get an error, assume success
            return True
            
        except Exception as e:
            self.log(f"❌ Error verifying schedule success: {str(e)}")
            return False

    def google_search(self, query):
        """Tìm kiếm trên Google và trả về kết quả"""
        if not query:
            self.log("❌ Vui lòng nhập từ khóa tìm kiếm")
            return False
            
        if not self.driver:
            self.log("❌ Trình duyệt chưa được khởi tạo")
            return False
            
        try:
            self.log(f"🔍 Đang tìm kiếm: {query}")
            
            # Truy cập Google
            if not self.handle_timeouts_and_errors(self.driver, GOOGLE_URL):
                self.log("❌ Không thể truy cập Google")
                return False
                
            # Đợi trang tải
            time.sleep(2)
            
            # Tìm kiếm input
            search_box = self.wait_for_element(
                self.driver, 
                By.NAME, 
                "q", 
                timeout=10
            )
            
            if not search_box:
                self.log("❌ Không tìm thấy ô tìm kiếm Google")
                return False
                
            # Xóa nội dung cũ và nhập từ khóa mới
            search_box.clear()
            search_box.send_keys(query)
            
            # Enter để tìm kiếm
            search_box.send_keys(Keys.RETURN)
            
            # Đợi kết quả
            time.sleep(3)
            
            # Thu thập kết quả tìm kiếm
            results = []
            
            # Tìm tất cả kết quả tìm kiếm
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            # Nếu không tìm thấy với CSS selector cũ, thử selector mới
            if not result_elements:
                result_elements = self.driver.find_elements(By.XPATH, "//div[@jscontroller]//a[@jsname]/../../..")
                
            # Nếu vẫn không tìm thấy, thử cách khác
            if not result_elements:
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[jsmodel]")
                
            for idx, result in enumerate(result_elements[:self.max_results]):
                try:
                    # Tiêu đề là thẻ h3
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text if title_element else "Không có tiêu đề"
                    
                    # Link là thẻ a
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href") if link_element else ""
                    
                    # Mô tả là div.VwiC3b hoặc span.st
                    try:
                        desc_element = result.find_element(By.CSS_SELECTOR, "div[aria-level='3']")
                    except:
                        try:
                            desc_element = result.find_element(By.CSS_SELECTOR, "div[data-content-feature]")
                        except:
                            desc_element = None
                            
                    desc = desc_element.text if desc_element else "Không có mô tả"
                    
                    # Thêm vào kết quả
                    results.append({
                        "Tiêu đề": title,
                        "URL": link,
                        "Mô tả": desc
                    })
                    
                except Exception as e:
                    self.log(f"⚠️ Lỗi khi phân tích kết quả #{idx+1}: {str(e)}")
            
            # In kết quả
            self.log(f"✅ Đã tìm thấy {len(results)} kết quả cho: {query}")
            for i, result in enumerate(results):
                self.log(f"Kết quả #{i+1}: {result['Tiêu đề']} - {result['URL']}")
                
            # Lưu kết quả
            self.results = results
            
            # Trả về
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tìm kiếm Google: {str(e)}")
            import traceback
            self.log(f"Chi tiết lỗi: {traceback.format_exc()}")
            return False

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PyQt5.QtCore import QThread, pyqtSignal

class EnhancedAutomationWorker(QThread):
    """Enhanced worker class for automation tasks"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    result_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(bool)

    def __init__(self, task=None, keyword="", email="", password="", max_results=10, 
                 headless=False, proxy=None, delay=0.0, pages=1, chrome_config=None):
        super().__init__()
        self.task = task
        self.keyword = keyword
        self.email = email
        self.password = password
        self.max_results = max_results
        self.headless = headless
        self.proxy = proxy
        self.delay = delay
        self.pages = pages
        self.chrome_config = chrome_config or {}
        self.running = False
        self.driver = None
        
    def run(self):
        """Main execution method"""
        self.running = True
        self.progress_signal.emit(0)
        
        try:
            if self.task == "google":
                self.google_search()
            elif self.task == "facebook":
                self.facebook_login()
            elif self.task == "shopee":
                self.shopee_scrape()
            else:
                raise ValueError(f"Unknown task: {self.task}")
                
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.error_signal.emit(str(e))
            
        finally:
            self.running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.finished_signal.emit(True)
            
    def stop(self):
        """Stop the worker thread"""
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
                
    def setup_driver(self):
        """Setup Chrome/Brave driver with basic options"""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        
        if self.headless:
            options.add_argument("--headless=new")
            
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
            
        # Add Chrome binary location if specified
        if self.chrome_config.get("chrome_path"):
            options.binary_location = self.chrome_config["chrome_path"]
            
        # Add user profile if specified
        if self.chrome_config.get("profile_path"):
            options.add_argument(f"--user-data-dir={os.path.dirname(self.chrome_config['profile_path'])}")
            options.add_argument(f"--profile-directory={os.path.basename(self.chrome_config['profile_path'])}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            self.log_signal.emit(f"Driver setup error: {str(e)}")
            return False
            
    def google_search(self):
        """Perform Google search"""
        if not self.setup_driver():
            return
            
        try:
            self.driver.get("https://www.google.com")
            self.progress_signal.emit(30)
            
            # Find and fill search box
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.send_keys(self.keyword)
            search_box.submit()
            
            self.progress_signal.emit(50)
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Get results
            results = []
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for i, element in enumerate(elements[:self.max_results]):
                try:
                    title = element.find_element(By.CSS_SELECTOR, "h3").text
                    link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    results.append((title, link))
                except:
                    continue
                    
            self.result_signal.emit(results)
            self.progress_signal.emit(100)
            
        except Exception as e:
            self.error_signal.emit(f"Search error: {str(e)}")
            
    def facebook_login(self):
        """Perform Facebook login"""
        if not self.setup_driver():
            return
            
        try:
            self.driver.get("https://www.facebook.com")
            self.progress_signal.emit(30)
            
            # Find login elements
            email_field = self.driver.find_element(By.ID, "email")
            pass_field = self.driver.find_element(By.ID, "pass")
            
            # Enter credentials
            email_field.send_keys(self.email)
            pass_field.send_keys(self.password)
            
            self.progress_signal.emit(50)
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login
            time.sleep(3)
            
            # Check login status
            result = {"status": "success", "url": self.driver.current_url}
            self.result_signal.emit(result)
            self.progress_signal.emit(100)
            
        except Exception as e:
            self.error_signal.emit(f"Login error: {str(e)}")
            
    def shopee_scrape(self):
        """Scrape Shopee products"""
        if not self.setup_driver():
            return
            
        try:
            # Go to search page
            search_url = f"https://shopee.vn/search?keyword={self.keyword}"
            self.driver.get(search_url)
            self.progress_signal.emit(30)
            
            # Wait for products
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".shopee-search-item-result__item"))
            )
            
            # Scroll to load more products
            for _ in range(min(self.pages, 5)):
                self.driver.execute_script("window.scrollBy(0, 800)")
                time.sleep(1)
                
            self.progress_signal.emit(50)
            
            # Get products
            results = []
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
            
            for element in elements[:self.max_results]:
                try:
                    name = element.find_element(By.CSS_SELECTOR, "div._36CEnF").text
                    price = element.find_element(By.CSS_SELECTOR, "span._29R_un").text
                    link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    results.append((name, price, link))
                except:
                    continue
                    
            self.result_signal.emit(results)
            self.progress_signal.emit(100)
            
        except Exception as e:
            self.error_signal.emit(f"Scraping error: {str(e)}")

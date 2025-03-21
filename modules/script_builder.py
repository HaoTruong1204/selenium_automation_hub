# modules/script_builder.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QLabel,
    QComboBox, QLineEdit, QFormLayout, QTabWidget,
    QSplitter, QDialogButtonBox, QMessageBox,
    QMenu, QAction, QGroupBox, QCheckBox, QListWidget, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor

import json
import os
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """
    Basic Python syntax highlighter to improve code readability in QTextEdit.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Blue
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "def", "class", "from", "import", "if", "else", "elif", "for", "while",
            "try", "except", "finally", "with", "as", "return", "yield", "and", "or",
            "not", "in", "is", "True", "False", "None", "self", "break", "continue"
        ]
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))

        # String literals
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Brown
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))

        # Comments (# ...)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Green
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((r"#[^\n]*", comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Light green
        self.highlighting_rules.append((r"\b\d+\b", number_format))

        # Function calls
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))  # Yellow
        self.highlighting_rules.append((r"\b[A-Za-z0-9_]+(?=\s*\()", function_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class ScriptBuilderWidget(QDialog):
    """
    Giao diện xây dựng và chỉnh sửa kịch bản Selenium.
    Cho phép:
      - Tạo/lưu kịch bản .py
      - Dùng snippet mẫu (Selenium Basic Setup, Google Search, Facebook Login, v.v.)
      - Kéo thả + insert lệnh Selenium
      - Kiểm tra syntax Python trước khi lưu
    """
    script_saved = pyqtSignal(str, str)  # name, script_content

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selenium Script Builder")
        self.resize(900, 700)

        self.init_ui()
        self.load_commands()
        self.load_snippets()
        
        # Khởi tạo dialog thêm command
        self.init_command_dialog()
        
        # Thiết lập drag & drop
        self.setup_drag_drop()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header: nhập tên script
        header_layout = QHBoxLayout()
        self.script_name = QLineEdit()
        self.script_name.setPlaceholderText("Tên script (không cần .py)")

        header_layout.addWidget(QLabel("Tên script:"))
        header_layout.addWidget(self.script_name)
        layout.addLayout(header_layout)

        # Tạo splitter chính
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left side (snippets, commands)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # GroupBox: command tree
        command_group = QGroupBox("Selenium Commands")
        command_layout = QVBoxLayout(command_group)
        self.command_tree = QTreeWidget()
        self.command_tree.setHeaderLabel("Available Commands")
        command_layout.addWidget(self.command_tree)
        left_layout.addWidget(command_group)

        # GroupBox: snippets
        snippet_group = QGroupBox("Code Snippets")
        snippet_layout = QVBoxLayout(snippet_group)

        self.snippet_combo = QComboBox()
        self.snippet_combo.addItems([])  # Sẽ được load trong load_snippets()
        snippet_layout.addWidget(self.snippet_combo)

        self.insert_snippet_btn = QPushButton("Chèn Snippet")
        snippet_layout.addWidget(self.insert_snippet_btn)

        # Preview snippet
        snippet_layout.addWidget(QLabel("Preview:"))
        self.snippet_preview = QTextEdit()
        self.snippet_preview.setReadOnly(True)
        snippet_layout.addWidget(self.snippet_preview)

        left_layout.addWidget(snippet_group)

        # GroupBox: tùy chọn
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)

        self.use_chrome_profile = QCheckBox("Sử dụng Chrome Profile")
        self.use_chrome_profile.setChecked(True)
        actions_layout.addWidget(self.use_chrome_profile)

        self.use_stealth_mode = QCheckBox("Sử dụng Stealth Mode")
        self.use_stealth_mode.setChecked(True)
        actions_layout.addWidget(self.use_stealth_mode)

        self.use_proxy = QCheckBox("Sử dụng Proxy")
        actions_layout.addWidget(self.use_proxy)

        self.generate_btn = QPushButton("Tạo Script")
        actions_layout.addWidget(self.generate_btn)

        left_layout.addWidget(actions_group)

        # Right side: code editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        editor_label = QLabel("Code Editor:")
        right_layout.addWidget(editor_label)

        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("# Viết code Python/Selenium ở đây hoặc sử dụng snippets")
        self.code_editor.setFont(QFont("Courier New", 11))

        self.highlighter = PythonSyntaxHighlighter(self.code_editor.document())

        right_layout.addWidget(self.code_editor)

        # Button khu vực dưới
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Lưu Script")
        self.clear_btn = QPushButton("Xóa")
        self.cancel_btn = QPushButton("Hủy")
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)

        right_layout.addLayout(btn_layout)

        # Add left/right to splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([300, 600])

        layout.addWidget(main_splitter)
        self.setLayout(layout)

        # Kết nối signal
        self.insert_snippet_btn.clicked.connect(self.insert_snippet)
        self.snippet_combo.currentIndexChanged.connect(self.update_snippet_preview)
        self.generate_btn.clicked.connect(self.generate_script)
        self.clear_btn.clicked.connect(self.clear_editor)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.save_script)

        # Khởi tạo snippet preview ban đầu
        self.update_snippet_preview()

    def load_commands(self):
        """
        Tạo dữ liệu Selenium command mẫu (phân cấp theo category).
        """
        categories = {
            "Browser": ["open", "maximize", "close", "back", "forward", "refresh"],
            "Navigation": ["get", "current_url", "title"],
            "Find Elements": ["find_element", "find_elements"],
            "Actions": ["click", "send_keys", "clear", "submit"],
            "Wait": ["implicit_wait", "explicit_wait", "fluent_wait"],
            "Advanced": ["execute_script", "switch_to_frame", "switch_to_window", "alert"]
        }

        for category, commands in categories.items():
            cat_item = QTreeWidgetItem([category])
            for cmd in commands:
                cmd_item = QTreeWidgetItem([cmd])
                cat_item.addChild(cmd_item)
            self.command_tree.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)

    def load_snippets(self):
        """
        Định nghĩa một bộ snippets code Python/Selenium để hỗ trợ người dùng.
        """
        self.snippets = {
            # Bạn đã cung cấp danh sách snippet đầy đủ trong code
            # (Selenium Basic Setup, Google Search, Facebook Login, Shopee Scrape, v.v.)
            "Selenium Basic Setup": r"""from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def setup_driver(headless=False, use_profile=True):
    \"\"\"Setup Selenium WebDriver with Chrome\"\"\"
    options = Options()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    if use_profile:
        chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        profile_path = r"C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

        options.binary_location = chrome_path
        options.add_argument(f"--user-data-dir={os.path.dirname(profile_path)}")
        options.add_argument(f"--profile-directory={os.path.basename(profile_path)}")

    # Add anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Further anti-detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def run():
    driver = setup_driver(headless=False)
    try:
        # Your automation code here

        print("Automation complete")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
""",
            "Google Search": """def google_search(driver, keyword):
    \"\"\"Perform a Google search\"\"\"
    print(f"Searching Google for: {keyword}")

    driver.get("https://www.google.com")

    # Find the search box
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.submit()

    # Wait for results
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search"))
    )

    # Get search results
    results = driver.find_elements(By.CSS_SELECTOR, ".g")

    # Print top 5
    for i, result in enumerate(results[:5], 1):
        try:
            title = result.find_element(By.CSS_SELECTOR, "h3").text
            print(f"{i}. {title}")
        except:
            continue

    return results
""",
            "Facebook Login": """def facebook_login(driver, email=None, password=None):
    \"\"\"Login to Facebook using Chrome profile or credentials\"\"\"
    print("Logging into Facebook...")

    driver.get("https://www.facebook.com")
    time.sleep(3)

    # Check if logged in already (using profile)
    try:
        if driver.find_elements(By.XPATH, "//*[contains(text(), 'on your mind')]"):
            print("Already logged in via Chrome profile")
            return True
    except:
        pass

    if email and password:
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)

            password_field = driver.find_element(By.ID, "pass")
            password_field.clear()
            password_field.send_keys(password)

            login_button = driver.find_element(By.NAME, "login")
            login_button.click()
            time.sleep(5)

            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    print("Not logged in and no credentials provided")
    return False
""",
            "Shopee Scrape Product": """def scrape_shopee_products(driver, search_term, max_products=10):
    \"\"\"Scrape products from Shopee\"\"\"
    print(f"Scraping Shopee for: {search_term}")

    search_url = f"https://shopee.vn/search?keyword={search_term.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(3)

    try:
        driver.execute_script("document.querySelector('.shopee-popup__close-btn')?.click()")
    except:
        pass

    products = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".shopee-search-item-result__item"))
    )

    product_data = []
    for i, product in enumerate(products[:max_products]):
        try:
            name_element = product.find_element(By.CSS_SELECTOR, "._10Wbs-._5SSWfi")
            price_element = product.find_element(By.CSS_SELECTOR, "._3c5u7X")
            name = name_element.text
            price = price_element.text
            product_data.append({"name": name, "price": price})
            print(f"Product {i+1}: {name} - {price}")
        except Exception as e:
            print(f"Error scraping product: {e}")
            continue

    return product_data
""",
            "Save Data to CSV": """import csv
import os

def save_to_csv(data, filename="data.csv"):
    \"\"\"Save data to CSV file\"\"\"
    if not data:
        print("No data to save")
        return False
    try:
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        headers = data[0].keys()

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        print(f"Data saved to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False
""",
            "Screenshot Element": """def take_element_screenshot(driver, element_selector, filename="element.png"):
    \"\"\"Take screenshot of a specific element\"\"\"
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(element_selector)
        )
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)
        element.screenshot(filepath)
        print(f"Screenshot saved to {filepath}")
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False
""",
            "Wait for Element": """def wait_for_element(driver, selector, timeout=10, selector_type=By.CSS_SELECTOR):
    \"\"\"Wait for an element to be present in the DOM\"\"\"
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((selector_type, selector))
        )
        return element
    except Exception as e:
        print(f"Element not found: {selector} - {e}")
        return None
""",
            "Click Element": """def click_element(driver, selector, timeout=10, selector_type=By.CSS_SELECTOR):
    \"\"\"Wait for an element and click it\"\"\"
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((selector_type, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(0.5)
        element.click()
        return True
    except Exception as e:
        print(f"Error clicking element {selector}: {e}")
        return False
""",
            "Fill Form": """def fill_form(driver, form_data):
    \"\"\"Fill a form with the provided data\"\"\"
    try:
        for selector, value in form_data.items():
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            input_field.clear()
            input_field.send_keys(value)
            time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Error filling form: {e}")
        return False
"""
        }

        # Đưa keys của self.snippets vào combobox
        self.snippet_combo.clear()
        self.snippet_combo.addItems(list(self.snippets.keys()))

    def update_snippet_preview(self):
        """Hiển thị nội dung snippet khi thay đổi selection"""
        selected = self.snippet_combo.currentText()
        if selected in self.snippets:
            self.snippet_preview.setText(self.snippets[selected])
        else:
            self.snippet_preview.clear()

    def insert_snippet(self):
        """Chèn snippet vào code editor tại vị trí con trỏ"""
        selected = self.snippet_combo.currentText()
        if selected in self.snippets:
            cursor = self.code_editor.textCursor()
            cursor.insertText(self.snippets[selected])
            self.code_editor.setTextCursor(cursor)

    def generate_script(self):
        """
        Sinh code script cơ bản dựa trên các lựa chọn (profile, stealth, proxy...).
        Sau đó chèn vào code editor để người dùng tiếp tục chỉnh sửa.
        """
        script_name = self.script_name.text().strip()
        if not script_name:
            QMessageBox.warning(self, "Thiếu tên script", "Vui lòng nhập tên script trước khi tạo.")
            return
        
        # Tạo template cơ bản
        template = []
        
        # Import cơ bản
        template.append("from selenium import webdriver")
        template.append("from selenium.webdriver.chrome.options import Options")
        template.append("from selenium.webdriver.chrome.service import Service")
        template.append("from selenium.webdriver.common.by import By")
        template.append("from selenium.webdriver.support.ui import WebDriverWait")
        template.append("from selenium.webdriver.support import expected_conditions as EC")
        template.append("from webdriver_manager.chrome import ChromeDriverManager")
        template.append("import time")
        template.append("import os")
        template.append("")
        
        # Thêm setup_driver function
        template.append("def setup_driver(headless=False):")
        template.append("    \"\"\"Setup Selenium WebDriver with Chrome/Brave\"\"\"")
        template.append("    options = Options()")
        template.append("")
        
        # Thêm các tùy chọn dựa trên lựa chọn của người dùng
        template.append("    # Thiết lập các tùy chọn cơ bản")
        template.append("    options.add_argument(\"--no-sandbox\")")
        template.append("    options.add_argument(\"--disable-dev-shm-usage\")")
        template.append("    options.add_argument(\"--disable-infobars\")")
        template.append("    options.add_argument(\"--disable-notifications\")")
        template.append("    options.add_argument(\"--disable-popup-blocking\")")
        template.append("")
        
        template.append("    if headless:")
        template.append("        options.add_argument(\"--headless=new\")")
        template.append("        options.add_argument(\"--window-size=1920,1080\")")
        template.append("        options.add_argument(\"--disable-gpu\")")
        template.append("    else:")
        template.append("        options.add_argument(\"--window-size=1366,768\")")
        template.append("")
        
        # Thêm Chrome profile nếu được chọn
        if self.use_chrome_profile.isChecked():
            template.append("    # Sử dụng Chrome profile")
            template.append("    chrome_path = r\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\"")
            template.append("    profile_path = r\"C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data\\Default\"")
            template.append("")
            template.append("    if os.path.exists(chrome_path):")
            template.append("        options.binary_location = chrome_path")
            template.append("    if os.path.exists(os.path.dirname(profile_path)):")
            template.append("        options.add_argument(f\"--user-data-dir={os.path.dirname(profile_path)}\")")
            template.append("        options.add_argument(f\"--profile-directory={os.path.basename(profile_path)}\")")
            template.append("")
        
        # Thêm stealth mode nếu được chọn
        if self.use_stealth_mode.isChecked():
            template.append("    # Sử dụng Stealth Mode để tránh phát hiện automation")
            template.append("    options.add_argument(\"--disable-blink-features=AutomationControlled\")")
            template.append("    options.add_experimental_option(\"excludeSwitches\", [\"enable-automation\"])")
            template.append("    options.add_experimental_option(\"useAutomationExtension\", False)")
            template.append("")
        
        # Thêm proxy nếu được chọn
        if self.use_proxy.isChecked():
            template.append("    # Sử dụng proxy")
            template.append("    proxy = \"your_proxy_here:port\"  # Thay thế bằng proxy của bạn")
            template.append("    options.add_argument(f'--proxy-server={proxy}')")
            template.append("")
        
        # Hoàn thành setup_driver function
        template.append("    service = Service(ChromeDriverManager().install())")
        template.append("    driver = webdriver.Chrome(service=service, options=options)")
        template.append("")
        
        # Thêm anti-detection nếu sử dụng stealth mode
        if self.use_stealth_mode.isChecked():
            template.append("    # Thêm anti-detection")
            template.append("    driver.execute_script(\"Object.defineProperty(navigator, 'webdriver', {get: () => undefined})\")")
            template.append("")
        
        template.append("    return driver")
        template.append("")
        
        # Thêm hàm main
        template.append("def main():")
        template.append("    \"\"\"Main function to run the script\"\"\"")
        template.append("    driver = setup_driver(headless=False)")
        template.append("    try:")
        template.append("        # Your automation code here")
        template.append("        driver.get(\"https://www.google.com\")")
        template.append("        print(\"Opened Google\")")
        template.append("        time.sleep(5)")
        template.append("")
        template.append("        # Add more automation steps here")
        template.append("")
        template.append("        print(\"Automation completed successfully\")")
        template.append("    except Exception as e:")
        template.append("        print(f\"Error: {e}\")")
        template.append("    finally:")
        template.append("        driver.quit()")
        template.append("")
        
        # Thêm entry point
        template.append("if __name__ == \"__main__\":")
        template.append("    main()")
        
        # Chèn template vào code editor
        self.code_editor.setPlainText("\n".join(template))
        
        # Thông báo
        QMessageBox.information(self, "Tạo script thành công", 
                               f"Đã tạo script cơ bản cho {script_name}.\nBạn có thể chỉnh sửa và lưu.")

    def clear_editor(self):
        """Xóa nội dung code editor (có xác nhận)"""
        if self.code_editor.toPlainText():
            reply = QMessageBox.question(
                self, "Confirm Clear",
                "Bạn có chắc muốn xóa nội dung editor?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.code_editor.clear()
        else:
            self.code_editor.clear()

    def save_script(self):
        """Lưu script vào file"""
        script_name = self.script_name.text().strip()
        if not script_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên script")
            return
        
        # Thêm .py nếu chưa có
        if not script_name.endswith(".py"):
            script_name += ".py"
        
        # Lấy nội dung script
        script_content = self.code_editor.toPlainText()
        
        # Kiểm tra syntax
        if not self.validate_python_syntax(script_content):
            reply = QMessageBox.question(
                self, 
                "Lỗi Syntax", 
                "Script có lỗi cú pháp Python. Bạn vẫn muốn lưu?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Đường dẫn thư mục scripts
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        
        # Đường dẫn đầy đủ của file
        script_path = os.path.join(scripts_dir, script_name)
        
        # Kiểm tra xem file đã tồn tại chưa
        if os.path.exists(script_path):
            reply = QMessageBox.question(
                self, 
                "Xác nhận ghi đè", 
                f"Script {script_name} đã tồn tại. Bạn có muốn ghi đè không?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Lưu file
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            
            QMessageBox.information(
                self, 
                "Thành công", 
                f"Đã lưu script {script_name} thành công!"
            )
            
            # Emit signal để thông báo script đã được lưu
            self.script_saved.emit(script_name, script_content)
            
            # Đóng dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Lỗi", 
                f"Không thể lưu script: {str(e)}"
            )

    def validate_python_syntax(self, code):
        """Kiểm tra syntax Python trước khi lưu"""
        if not code.strip():
            return True
        
        try:
            # Sử dụng compile để kiểm tra syntax
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError as e:
            line_num = e.lineno
            error_msg = str(e)
            
            # Hiển thị thông báo lỗi chi tiết
            QMessageBox.warning(
                self,
                "Lỗi Syntax Python",
                f"Lỗi tại dòng {line_num}: {error_msg}"
            )
            
            # Di chuyển con trỏ đến dòng lỗi
            cursor = self.code_editor.textCursor()
            block = self.code_editor.document().findBlockByLineNumber(line_num - 1)
            cursor.setPosition(block.position())
            self.code_editor.setTextCursor(cursor)
            self.code_editor.setFocus()
            
            return False
        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi kiểm tra code",
                f"Không thể kiểm tra syntax: {str(e)}"
            )
            return False

    def init_command_dialog(self):
        """Cho phép click chuột phải -> Add Command và double-click trên tree để chèn"""
        self.code_editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.code_editor.customContextMenuRequested.connect(self.show_editor_context_menu)
        self.command_tree.itemDoubleClicked.connect(self.on_command_double_clicked)

    def show_editor_context_menu(self, position):
        """Menu chuột phải trong code editor"""
        menu = self.code_editor.createStandardContextMenu()
        menu.addSeparator()
        add_command_action = QAction("Add Selenium Command", self)
        add_command_action.triggered.connect(self.open_command_dialog)
        menu.addAction(add_command_action)
        menu.exec_(self.code_editor.mapToGlobal(position))

    def open_command_dialog(self):
        """Click phải -> Add Command"""
        dialog = CommandDialog(parent=self)
        if dialog.exec_():
            command = dialog.command_combo.currentText()
            target = dialog.target_edit.text()
            value = dialog.value_edit.text()
            code = self.generate_command_code(command, target, value)

            cursor = self.code_editor.textCursor()
            cursor.insertText(code)

    def on_command_double_clicked(self, item, column):
        """Double-click vào command trong tree -> chèn code vào editor"""
        if item.parent():  # Chỉ xử lý nếu là node con
            command = item.text(0)
            dialog = CommandDialog(command=command, parent=self)
            if dialog.exec_():
                target = dialog.target_edit.text()
                value = dialog.value_edit.text()
                code = self.generate_command_code(command, target, value)

                cursor = self.code_editor.textCursor()
                cursor.insertText(code)

    def generate_command_code(self, command, target, value):
        """Sinh code Python tùy theo lệnh Selenium"""
        code_templates = {
            "open": f'driver.get("{value}")',
            "click": f'driver.find_element(By.{target}, "{value}").click()',
            "send_keys": f'driver.find_element(By.{target}, "{value}").send_keys("text_to_type")',
            "wait": f'WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.{target}, "{value}")))',
            "get": f'driver.get("{value}")',
            "clear": f'driver.find_element(By.{target}, "{value}").clear()',
            "maximize": 'driver.maximize_window()',
            "close": 'driver.close()',
            "back": 'driver.back()',
            "forward": 'driver.forward()',
            "refresh": 'driver.refresh()',
            "submit": f'driver.find_element(By.{target}, "{value}").submit()',
            "implicit_wait": f'driver.implicitly_wait({value or 10})',
            "execute_script": f'driver.execute_script("{value}")',
            "switch_to_frame": f'driver.switch_to.frame("{value}")',
            "switch_to_window": f'driver.switch_to.window(driver.window_handles[{value or 0}])',
            "alert": 'alert = driver.switch_to.alert\nalert.accept()'
        }
        if command in code_templates:
            return code_templates[command] + "\n"
        else:
            return f"# {command} command with {target}={value}\n"

    def setup_drag_drop(self):
        """
        Bật drag & drop từ QTreeWidget -> QTextEdit
        """
        self.command_tree.setDragEnabled(True)
        self.code_editor.setAcceptDrops(True)

        class CodeEditorWithDrop(QTextEdit):
            def __init__(self, parent_widget=None):
                super().__init__(parent_widget)
                self.setAcceptDrops(True)
                self.parent_widget = parent_widget

            def dragEnterEvent(self, event):
                if event.mimeData().hasText():
                    event.acceptProposedAction()

            def dropEvent(self, event):
                text = event.mimeData().text()
                if text and self.parent_widget:
                    if text in self.parent_widget.command_map:
                        command = text
                        dialog = CommandDialog(command=command, parent=self.parent_widget)
                        if dialog.exec_():
                            target = dialog.target_edit.text()
                            value = dialog.value_edit.text()
                            code = self.parent_widget.generate_command_code(command, target, value)
                            cursor = self.textCursor()
                            cursor.insertText(code)
                event.acceptProposedAction()

        # Thay thế self.code_editor bằng CodeEditorWithDrop
        self.code_editor_with_drop = CodeEditorWithDrop(self)
        self.code_editor_with_drop.setPlaceholderText(self.code_editor.placeholderText())
        self.code_editor_with_drop.setFont(self.code_editor.font())

        # Copy nội dung cũ
        self.code_editor_with_drop.setText(self.code_editor.toPlainText())

        # Thay thế trong layout
        right_layout = self.code_editor.parent().layout()
        right_layout.replaceWidget(self.code_editor, self.code_editor_with_drop)
        self.code_editor.deleteLater()
        self.code_editor = self.code_editor_with_drop

        # Áp dụng lại highlight
        self.highlighter = PythonSyntaxHighlighter(self.code_editor.document())

        # command_map: map tên command -> category (giúp filter if needed)
        self.command_map = {}
        for i in range(self.command_tree.topLevelItemCount()):  # ✅ Đã sửa lỗi đóng ngoặc
            category_item = self.command_tree.topLevelItem(i)  # Lấy mục cha (category)
    
        # Duyệt qua các lệnh con trong từng danh mục
        for j in range(category_item.childCount()):
            cmd = category_item.child(j).text(0)  # Lấy tên lệnh con
            self.command_map[cmd] = category_item.text(0)  # Ánh xạ cmd -> danh mục

class CommandDialog(QDialog):
    """
    Hộp thoại điền thông tin command: command, target, value
    """
    def __init__(self, command="", parent=None, target="", value=""):
        super().__init__(parent)
        self.setWindowTitle("Thêm Command")
        self.resize(400, 200)
        self.init_ui(command, target, value)

    def init_ui(self, command, target, value):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.command_combo = QComboBox()
        commands = ["open", "click", "send_keys", "wait", "get", "clear",
                    "maximize", "close", "back", "forward", "refresh",
                    "submit", "implicit_wait", "execute_script",
                    "switch_to_frame", "switch_to_window", "alert"]
        self.command_combo.addItems(commands)

        if command in commands:
            self.command_combo.setCurrentText(command)

        self.target_edit = QLineEdit()
        self.target_edit.setText(target)
        self.target_edit.setPlaceholderText("XPATH, ID, CSS_SELECTOR, NAME...")

        self.value_edit = QLineEdit()
        self.value_edit.setText(value)
        self.value_edit.setPlaceholderText("Giá trị cho command, e.g. URL, selector...")

        form.addRow("Command:", self.command_combo)
        form.addRow("Target Type:", self.target_edit)
        form.addRow("Value:", self.value_edit)
        layout.addLayout(form)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Cập nhật placeholder theo loại command
        self.command_combo.currentTextChanged.connect(self.update_placeholders)
        self.update_placeholders()

    def update_placeholders(self):
        cmd = self.command_combo.currentText()
        if cmd in ["click", "send_keys", "clear", "wait", "submit"]:
            self.target_edit.setPlaceholderText("By.ID, By.NAME, By.CSS_SELECTOR...")
            self.value_edit.setPlaceholderText("selector string")
        elif cmd in ["open", "get"]:
            self.target_edit.setPlaceholderText("Not used for this command")
            self.value_edit.setPlaceholderText("https://example.com")
        elif cmd == "maximize":
            self.target_edit.setPlaceholderText("No target needed")
            self.value_edit.setPlaceholderText("No value needed")
        else:
            self.target_edit.setPlaceholderText("By.ID, By.NAME, By.CSS_SELECTOR...")
            self.value_edit.setPlaceholderText("Custom value, e.g. frame name, window index, script...")


# config.py

APP_TITLE = "Selenium Automation Hub"
APP_ICON = "resources/icons/app.png"
APP_WIDTH = 1200
APP_HEIGHT = 800
APP_VERSION = "2.0.0"

DEFAULT_THEME = "Dark"
DEFAULT_RETRY = 3
DEFAULT_TIMEOUT = 30

# Định nghĩa màu sắc chung cho giao diện
COLORS = {
    "primary": "#0d6efd",
    "primary_hover": "#0b5ed7",
    "primary_active": "#0a58ca",
    "dark_bg": "#2b2b2b",
    "dark_bg_secondary": "#363636",
    "light_bg": "#f8f9fa",
    "light_bg_secondary": "#e9ecef",
    "dark_text": "#212529",
    "light_text": "#ffffff",
    "border_dark": "#555555",
    "border_light": "#ced4da",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
}

THEMES = {
    "Dark": {
        "bg_primary": COLORS["dark_bg"],
        "bg_secondary": COLORS["dark_bg_secondary"],
        "text_primary": COLORS["light_text"],
        "text_secondary": "#e0e0e0",
        "accent": COLORS["primary"],
        "accent_hover": COLORS["primary_hover"],
        "border": COLORS["border_dark"]
    },
    "Light": {
        "bg_primary": COLORS["light_bg"],
        "bg_secondary": COLORS["light_bg_secondary"],
        "text_primary": COLORS["dark_text"],
        "text_secondary": "#495057",
        "accent": COLORS["primary"],
        "accent_hover": COLORS["primary_hover"],
        "border": COLORS["border_light"]
    }
}

# URL của các trang web
GOOGLE_URL = "https://www.google.com"
FACEBOOK_URL = "https://www.facebook.com"
SHOPEE_SEARCH_URL = "https://shopee.vn/search?keyword=your_search_keyword"

# Thông tin đăng nhập (nên sử dụng biến môi trường cho bảo mật thực tế)
FACEBOOK_EMAIL = "your_email@example.com"
FACEBOOK_PASSWORD = "your_password"

# Cài đặt nâng cao
ENABLE_HEADLESS = True
ENABLE_STEALTH_MODE = True
ENABLE_PROXY_ROTATION = False
CAPTCHA_SERVICE = "manual"  # 'manual', '2captcha', 'anticaptcha', 'auto'
CAPTCHA_API_KEY = ""

# Thư mục lưu trữ
DATA_DIR = "data"
SCRIPTS_DIR = "scripts"
LOGS_DIR = "logs"
DOWNLOADS_DIR = "downloads"

# Danh sách User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

# --- Cấu hình đặc biệt dành cho Brave ---
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_PROFILE_PATH = r"C:\Users\admin\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default"

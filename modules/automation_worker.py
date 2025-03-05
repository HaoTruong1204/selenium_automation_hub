# modules/automation_worker.py

import time
import traceback
from PyQt5.QtCore import QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class AutomationWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, url="", proxy="", headless=False, delay=1.0, parent=None):
        super().__init__(parent)
        self.url = url
        self.proxy = proxy
        self.headless = headless
        self.delay = delay
        self._running = True  # Flag để dừng thread an toàn

    def stop(self):
        self._running = False

    def run(self):
        try:
            self.log_signal.emit(f"Khởi động Selenium với URL={self.url}, headless={self.headless}, proxy={self.proxy}")

            # Cấu hình Selenium
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            if self.proxy:
                chrome_options.add_argument(f"--proxy-server={self.proxy}")

            driver = webdriver.Chrome(options=chrome_options)

            # Mở trang
            driver.get(self.url)
            self.log_signal.emit(f"Đã mở trang: {self.url}")

            # Giả lập quá trình automation
            for i in range(1, 21):
                if not self._running:
                    self.log_signal.emit("Đã dừng theo yêu cầu người dùng.")
                    break
                time.sleep(self.delay)
                progress_value = int(i * 100 / 20)
                self.progress_signal.emit(progress_value)
                self.log_signal.emit(f"Đang xử lý bước {i}/20 ...")

            driver.quit()

            if self._running:
                self.log_signal.emit("Hoàn thành quá trình automation!")
                self.finished_signal.emit("Hoàn thành")
            else:
                self.finished_signal.emit("Đã dừng")

        except Exception as e:
            err_msg = f"Lỗi trong AutomationWorker:\n{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(err_msg)
            self.finished_signal.emit("Lỗi")

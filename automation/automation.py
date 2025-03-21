# automation/automation.py
from PyQt5.QtCore import QThread, pyqtSignal
import time

class AutomationWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    data_ready = pyqtSignal(dict)
    task_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, task_type, config):
        super().__init__()
        self.task_type = task_type
        self.config = config

    def run(self):
        try:
            self.log_message.emit(f"Worker started: {self.task_type}")
            # Giả lập tiến trình (sleep)
            for i in range(5):
                time.sleep(1)
                self.progress_updated.emit(int((i+1)/5*100))

            # Giả lập kết quả
            if self.task_type == "google_search":
                data = [{
                    "time": "12:00",
                    "source": "Google",
                    "type": "Result",
                    "content": "Demo",
                    "status": "OK",
                    "details": "demo"
                }]
                self.data_ready.emit({"google_results": data})
            elif self.task_type == "facebook_login":
                self.data_ready.emit({"facebook_login": "Success"})
            else:
                data = [{
                    "name": "Item 1",
                    "price": "10000",
                    "rating": "4.5",
                    "sold": "100",
                    "seller": "Seller A"
                }]
                self.data_ready.emit({"shopee_products": data})

            self.task_completed.emit(f"{self.task_type} completed")
        except Exception as e:
            self.error_occurred.emit(str(e))

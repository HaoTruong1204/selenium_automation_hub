# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from .dashboard import DashboardWidget  # Import DashboardWidget từ file dashboard.py

# def main():
#     app = QApplication(sys.argv)

#     # Load file QSS cho toàn bộ ứng dụng
#     qss_file = "D:/ProjectGDU/Python/CuoiKi/selenium_automation_hub/resources/qss/app_style.qss"
#     try:
#         with open(qss_file, "r", encoding="utf-8") as f:
#             qss = f.read()
#             app.setStyleSheet(qss)
#     except Exception as e:
#         print("Không thể load QSS:", e)

#     # Tạo MainWindow và gán DashboardWidget làm central widget
#     main_window = QMainWindow()
#     main_window.setWindowTitle("Selenium Automation Hub")
#     dashboard = DashboardWidget()
#     main_window.setCentralWidget(dashboard)
#     main_window.resize(1200, 800)  # Kích thước cửa sổ chính
#     main_window.show()

#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()

import sys
import os
import json
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QListWidget, QLabel, QDateTimeEdit, QComboBox,
                           QFormLayout, QGroupBox, QCheckBox, QSpinBox, QDialog,
                           QDialogButtonBox, QMessageBox, QListWidgetItem, QTableWidget, QTableWidgetItem, 
                           QHeaderView)
from PyQt5.QtCore import Qt, QDateTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush, QIcon
from PyQt5.QtWidgets import QLineEdit

import time

class TaskSchedulerWidget(QWidget):
    task_scheduled = pyqtSignal(dict)  # Signal khi task được lên lịch
    task_ready = pyqtSignal(str, str)  # task_id, script_path - khi đến thời gian chạy task
    task_log = pyqtSignal(str)  # Signal để gửi thông báo log
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.running_tasks = {}  # Dictionary of task_id: timer
        self.task_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scheduled_tasks.json")
        self.init_ui()
        self.load_tasks()
        
        # Timer để kiểm tra tasks cần chạy
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_scheduled_tasks)
        self.check_timer.start(60000)  # Check mỗi phút
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Lên lịch tự động")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        layout.addWidget(self.task_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("Thêm lịch mới")
        self.add_task_btn.clicked.connect(self.add_task)
        self.edit_task_btn = QPushButton("Chỉnh sửa")
        self.edit_task_btn.clicked.connect(self.edit_task)
        self.remove_task_btn = QPushButton("Xóa lịch")
        self.remove_task_btn.clicked.connect(self.remove_task)
        
        btn_layout.addWidget(self.add_task_btn)
        btn_layout.addWidget(self.edit_task_btn)
        btn_layout.addWidget(self.remove_task_btn)
        layout.addLayout(btn_layout)
        
        # Scheduled vs One-time
        options_layout = QHBoxLayout()
        self.run_now_btn = QPushButton("Chạy ngay")
        self.run_now_btn.clicked.connect(self.run_selected_task)
        options_layout.addWidget(self.run_now_btn)
        
        self.enable_all_cb = QCheckBox("Bật tất cả")
        self.enable_all_cb.setChecked(True)
        self.enable_all_cb.stateChanged.connect(self.toggle_all_tasks)
        options_layout.addWidget(self.enable_all_cb)
        
        layout.addLayout(options_layout)
        
        # Task creation form
        form_group = QGroupBox("Tạo Task Mới")
        form_layout = QFormLayout()
        
        self.task_name = QLineEdit()
        form_layout.addRow("Tên task:", self.task_name)
        
        self.script_combo = QComboBox()
        self.update_script_list()
        form_layout.addRow("Script:", self.script_combo)
        
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # Default to 1 hour from now
        self.datetime_edit.setCalendarPopup(True)
        form_layout.addRow("Thời gian chạy:", self.datetime_edit)
        
        self.repeat_check = QCheckBox("Lặp lại")
        form_layout.addRow("Lặp lại:", self.repeat_check)
        
        self.repeat_interval = QComboBox()
        self.repeat_interval.addItems(["Hàng ngày", "Hàng tuần", "Hàng tháng"])
        form_layout.addRow("Chu kỳ lặp:", self.repeat_interval)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Task list
        self.task_table = QTableWidget(0, 5)
        self.task_table.setHorizontalHeaderLabels(["Tên", "Script", "Thời gian", "Lặp lại", "Trạng thái"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.task_table)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Xóa Task")
        delete_btn.clicked.connect(self.delete_task)
        btn_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.clicked.connect(self.refresh_tasks)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_tasks(self):
        """Tải danh sách task từ file JSON"""
        try:
            if os.path.exists(self.task_file):
                with open(self.task_file, 'r', encoding='utf-8') as f:
                    loaded_tasks = json.load(f)
                    
                    # Kiểm tra và chuẩn hóa dữ liệu
                    valid_tasks = []
                    for task in loaded_tasks:
                        # Đảm bảo task có các trường cần thiết
                        if not isinstance(task, dict):
                            continue
                            
                        if 'id' not in task or 'name' not in task or 'script' not in task:
                            continue
                            
                        # Đảm bảo task có trường run_time
                        if 'run_time' not in task:
                            task['run_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                        # Đảm bảo task có trường status
                        if 'status' not in task:
                            task['status'] = 'Chưa chạy'
                            
                        # Đảm bảo task có trường enabled
                        if 'enabled' not in task:
                            task['enabled'] = True
                            
                        valid_tasks.append(task)
                        
                    self.tasks = valid_tasks
                    
                    # Phát signal thông báo
                    if hasattr(self, 'task_log'):
                        self.task_log.emit(f"Đã tải {len(self.tasks)} task từ file")
                        
                    self.update_table()
            else:
                # Tạo file mới nếu chưa tồn tại
                self.tasks = []
                self.save_tasks()
                
                # Phát signal thông báo
                if hasattr(self, 'task_log'):
                    self.task_log.emit("Đã tạo file task mới")
        except Exception as e:
            error_msg = f"Không thể tải danh sách task: {str(e)}"
            QMessageBox.warning(self, "Lỗi", error_msg)
            
            # Phát signal thông báo lỗi
            if hasattr(self, 'task_log'):
                self.task_log.emit(f"Lỗi: {error_msg}")
                
            # Tạo danh sách task trống
            self.tasks = []
    
    def save_tasks(self):
        """Lưu danh sách task vào file JSON"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.task_file), exist_ok=True)
            
            # Lưu danh sách task vào file
            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
                
            # Phát signal thông báo
            if hasattr(self, 'task_log'):
                self.task_log.emit(f"Đã lưu {len(self.tasks)} task vào file")
                
        except Exception as e:
            error_msg = f"Không thể lưu danh sách task: {str(e)}"
            QMessageBox.warning(self, "Lỗi", error_msg)
            
            # Phát signal thông báo lỗi
            if hasattr(self, 'task_log'):
                self.task_log.emit(f"Lỗi: {error_msg}")
                
            # Ghi log lỗi
            import traceback
            print(f"Lỗi khi lưu task: {str(e)}")
            print(traceback.format_exc())
    
    def update_table(self):
        """Cập nhật danh sách task trên giao diện"""
        self.task_list.clear()
        
        if not self.tasks:
            # Hiển thị thông báo nếu không có task nào
            empty_item = QListWidgetItem("Chưa có task nào được lên lịch. Nhấn 'Thêm Task' để tạo mới.")
            empty_item.setForeground(QBrush(QColor("#888888")))
            self.task_list.addItem(empty_item)
            return
            
        for task in self.tasks:
            try:
                # Tạo item hiển thị thông tin task
                name = task.get('name', 'Không tên')
                run_time = task.get('run_time', 'Không có thời gian')
                status = task.get('status', 'Chưa chạy')
                
                # Định dạng thời gian hiển thị
                try:
                    # Thử chuyển đổi thời gian sang định dạng đẹp hơn
                    dt = None
                    try:
                        dt = datetime.datetime.strptime(run_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            dt = datetime.datetime.strptime(run_time, "yyyy-MM-dd hh:mm:ss")
                        except ValueError:
                            pass
                            
                    if dt:
                        run_time = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass
                
                item_text = f"{name} - {run_time}"
                
                # Thêm thông tin trạng thái
                item_text += f" [{status}]"
                
                # Thêm thông tin lặp lại
                if task.get('repeat'):
                    item_text += f" (Lặp lại: {task.get('repeat_interval', 'Không xác định')})"
                    
                # Thêm thông tin script
                script = task.get('script', 'Không có script')
                item_text += f" - Script: {script}"
                
                # Thêm thông tin bật/tắt
                if not task.get('enabled', True):
                    item_text += " [Đã tắt]"
                    
                item = QListWidgetItem(item_text)
                
                # Set màu dựa trên trạng thái
                if not task.get('enabled', True):
                    item.setForeground(QBrush(QColor("#888888")))  # Màu xám cho task bị tắt
                elif status == "Running":
                    item.setForeground(QBrush(QColor("#2ecc71")))  # Màu xanh lá cho task đang chạy
                elif status == "Failed":
                    item.setForeground(QBrush(QColor("#e74c3c")))  # Màu đỏ cho task lỗi
                elif status == "Completed":
                    item.setForeground(QBrush(QColor("#3498db")))  # Màu xanh dương cho task đã hoàn thành
                elif self.is_task_due_soon(task):
                    item.setForeground(QBrush(QColor("#f39c12")))  # Màu cam cho task sắp chạy
                
                self.task_list.addItem(item)
            except Exception as e:
                # Nếu có lỗi khi hiển thị task, vẫn hiển thị nhưng với thông báo lỗi
                error_item = QListWidgetItem(f"Lỗi hiển thị task: {str(e)}")
                error_item.setForeground(QBrush(QColor("#e74c3c")))
                self.task_list.addItem(error_item)
    
    def is_task_due_soon(self, task):
        """Kiểm tra xem task có sắp chạy trong 15 phút tới không"""
        try:
            run_time = task.get('run_time', '')
            if not run_time:
                return False
                
            # Thử nhiều định dạng thời gian khác nhau
            schedule_time = None
            try:
                schedule_time = datetime.datetime.strptime(run_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    schedule_time = datetime.datetime.strptime(run_time, "%Y-%m-%d %H:%M")
                except ValueError:
                    try:
                        schedule_time = datetime.datetime.strptime(run_time, "yyyy-MM-dd hh:mm:ss")
                    except ValueError:
                        # Thử chuyển đổi từ QDateTime string
                        date_parts = run_time.split(" ")
                        if len(date_parts) >= 2:
                            date_str = date_parts[0]
                            time_str = date_parts[1]
                            
                            # Xử lý date
                            date_parts = date_str.split("-")
                            if len(date_parts) == 3:
                                year = int(date_parts[0])
                                month = int(date_parts[1])
                                day = int(date_parts[2])
                                
                                # Xử lý time
                                time_parts = time_str.split(":")
                                if len(time_parts) >= 2:
                                    hour = int(time_parts[0])
                                    minute = int(time_parts[1])
                                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                                    
                                    schedule_time = datetime.datetime(year, month, day, hour, minute, second)
            
            if not schedule_time:
                return False
                
            now = datetime.datetime.now()
            diff = (schedule_time - now).total_seconds() / 60  # Chênh lệch phút
            
            # Trả về True nếu task sẽ chạy trong 15 phút tới và chưa quá hạn
            return 0 <= diff <= 15
        except Exception as e:
            print(f"Lỗi khi kiểm tra thời gian task: {str(e)}")
            return False
    
    def add_task(self):
        """Add a new scheduled task"""
        name = self.task_name.text().strip()
        script = self.script_combo.currentText()
        run_time = self.datetime_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        repeat = self.repeat_check.isChecked()
        repeat_interval = self.repeat_interval.currentText() if repeat else "None"
        
        if not name or not script:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên task và chọn script")
            return
            
        # Create task
        task = {
            "id": f"task_{int(time.time())}",
            "name": name,
            "script": script,
            "run_time": run_time,
            "repeat": repeat,
            "repeat_interval": repeat_interval,
            "status": "Scheduled"
        }
        
        # Add to list and update UI
        self.tasks.append(task)
        self.update_table()
        
        # Save tasks
        self.save_tasks()
        
        # Clear form
        self.task_name.clear()
        
        QMessageBox.information(self, "Task đã tạo", f"Task '{name}' đã được lập lịch chạy vào {run_time}")
    
    def edit_task(self):
        selected = self.task_list.currentRow()
        if selected >= 0:
            task = self.tasks[selected]
            dlg = TaskDialog(self, task, is_new=False)
            if dlg.exec_() == QDialog.Accepted:
                self.tasks[selected] = dlg.get_task_data()
                # Giữ lại ID gốc
                if 'id' in task:
                    self.tasks[selected]['id'] = task['id']
                self.update_table()
                self.save_tasks()
    
    def remove_task(self):
        selected = self.task_list.currentRow()
        if selected >= 0:
            reply = QMessageBox.question(self, "Xác nhận", 
                                      f"Xóa task '{self.tasks[selected]['name']}'?",
                                      QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.tasks[selected]
                self.update_table()
                self.save_tasks()
    
    def run_selected_task(self):
        selected = self.task_list.currentRow()
        if selected >= 0:
            task = self.tasks[selected]
            script_name = task.get('script', '')
            
            # Xây dựng đường dẫn script đầy đủ
            scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
            script_path = os.path.join(scripts_dir, script_name)
            
            if not os.path.exists(script_path):
                QMessageBox.warning(self, "Lỗi", f"Không tìm thấy script: {script_path}")
                return
                
            # Log hành động
            print(f"Đang chạy task: {task.get('name', 'unknown')} với script: {script_path}")
            self.task_log.emit(f"Đang chạy task: {task.get('name', 'unknown')}")
                
            # Phát tín hiệu để main_window xử lý
            task_id = task.get('id', f"manual_{int(datetime.datetime.now().timestamp())}")
            self.task_ready.emit(task_id, script_path)
    
    def toggle_all_tasks(self, state):
        enabled = state == Qt.Checked
        for task in self.tasks:
            task['enabled'] = enabled
        self.update_table()
        self.save_tasks()
    
    def check_scheduled_tasks(self):
        """Kiểm tra xem có task nào cần chạy không"""
        current_time = datetime.datetime.now()
        
        for task in self.tasks:
            # Bỏ qua nếu task đã đang chạy
            if task["id"] in self.running_tasks:
                continue
                
            # Bỏ qua nếu task đã hoàn thành và không lặp lại
            if task["status"] == "Completed" and not task.get("repeat", False):
                continue
                
            # Bỏ qua nếu task bị vô hiệu hóa
            if not task.get("enabled", True):
                continue
                
            # Kiểm tra xem đã đến thời gian chạy chưa
            try:
                # Xử lý định dạng thời gian
                try:
                    run_time = datetime.datetime.strptime(task["run_time"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        run_time = datetime.datetime.strptime(task["run_time"], "yyyy-MM-dd hh:mm:ss")
                    except ValueError:
                        # Thử chuyển đổi từ QDateTime string
                        date_parts = task["run_time"].split(" ")
                        if len(date_parts) >= 2:
                            date_str = date_parts[0]
                            time_str = date_parts[1]
                            
                            # Xử lý date
                            date_parts = date_str.split("-")
                            if len(date_parts) == 3:
                                year = int(date_parts[0])
                                month = int(date_parts[1])
                                day = int(date_parts[2])
                                
                                # Xử lý time
                                time_parts = time_str.split(":")
                                if len(time_parts) >= 2:
                                    hour = int(time_parts[0])
                                    minute = int(time_parts[1])
                                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                                    
                                    run_time = datetime.datetime(year, month, day, hour, minute, second)
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                
                if current_time >= run_time:
                    # Chạy task
                    self.run_task(task)
                    
                    # Cập nhật trạng thái - kiểm tra xem 'repeat' có tồn tại không
                    if "repeat" in task and task["repeat"]:
                        task["status"] = "Running"
                    else:
                        task["status"] = "Completed"
                    task["last_run"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Tính thời gian chạy tiếp theo nếu lặp lại
                    if "repeat" in task and task["repeat"]:
                        if task["repeat_interval"] == "Hàng ngày":
                            new_run_time = run_time + datetime.timedelta(days=1)
                        elif task["repeat_interval"] == "Hàng tuần":
                            new_run_time = run_time + datetime.timedelta(days=7)
                        elif task["repeat_interval"] == "Hàng tháng":
                            # Xử lý tháng
                            new_month = run_time.month + 1
                            new_year = run_time.year
                            if new_month > 12:
                                new_month = 1
                                new_year += 1
                            
                            # Xử lý ngày cuối tháng
                            last_day = 28
                            if new_month in [1, 3, 5, 7, 8, 10, 12]:
                                last_day = 31
                            elif new_month in [4, 6, 9, 11]:
                                last_day = 30
                            elif new_month == 2:
                                # Xử lý năm nhuận
                                if (new_year % 4 == 0 and new_year % 100 != 0) or (new_year % 400 == 0):
                                    last_day = 29
                                else:
                                    last_day = 28
                            
                            new_day = min(run_time.day, last_day)
                            new_run_time = datetime.datetime(new_year, new_month, new_day, 
                                                           run_time.hour, run_time.minute, run_time.second)
                        
                        task["run_time"] = new_run_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"Lỗi khi kiểm tra task {task.get('name', 'unknown')}: {str(e)}")
                import traceback
                print(traceback.format_exc())
                
        # Cập nhật bảng với trạng thái mới
        self.update_table()
        self.save_tasks()

    def run_task(self, task):
        """Chạy một task đã lên lịch"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", task["script"])
        
        # Kiểm tra xem script có tồn tại không
        if not os.path.exists(script_path):
            print(f"Lỗi: Script không tồn tại: {script_path}")
            task["status"] = "Failed"
            self.update_table()
            self.save_tasks()
            return
            
        # Phát signal để chạy task
        task_id = task["id"]
        print(f"Đang chạy task: {task.get('name', task_id)} với script: {task['script']}")
        
        # Phát signal để main_window xử lý
        self.task_ready.emit(task_id, script_path)
        
        # Phát signal task_log nếu có
        if hasattr(self, 'task_log'):
            self.task_log.emit(f"Task {task.get('name', task_id)} đã được kích hoạt")
            
        # Cập nhật trạng thái
        task["status"] = "Running"
        self.update_table()
        self.save_tasks()

    def update_script_list(self):
        """Update the list of available scripts"""
        self.script_combo.clear()
        
        # Find all Python scripts in the scripts directory
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        if os.path.exists(scripts_dir):
            for file in os.listdir(scripts_dir):
                if file.endswith(".py"):
                    self.script_combo.addItem(file)

    def delete_task(self):
        """Delete selected tasks"""
        selected_rows = set()
        for item in self.task_table.selectedItems():
            selected_rows.add(item.row())
            
        if not selected_rows:
            return
            
        # Remove tasks (in reverse order to avoid index issues)
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self.tasks):
                task_id = self.tasks[row]["id"]
                # Stop timer if running
                if task_id in self.running_tasks:
                    self.running_tasks[task_id].stop()
                    del self.running_tasks[task_id]
                    
                self.tasks.pop(row)
                
        self.update_table()
        self.save_tasks()

    def refresh_tasks(self):
        """Làm mới danh sách task và trạng thái"""
        try:
            # Phát signal thông báo đang làm mới
            if hasattr(self, 'task_log'):
                self.task_log.emit("Đang làm mới danh sách task...")
                
            # Cập nhật danh sách script
            self.update_script_list()
            
            # Tải lại danh sách task từ file
            self.load_tasks()
            
            # Cập nhật giao diện
            self.update_table()
            
            # Kiểm tra các task đã lên lịch
            self.check_scheduled_tasks()
            
            # Phát signal thông báo đã làm mới xong
            if hasattr(self, 'task_log'):
                self.task_log.emit(f"Đã làm mới danh sách task: {len(self.tasks)} task")
                
        except Exception as e:
            # Xử lý lỗi
            error_msg = f"Lỗi khi làm mới danh sách task: {str(e)}"
            print(error_msg)
            
            # Phát signal thông báo lỗi
            if hasattr(self, 'task_log'):
                self.task_log.emit(error_msg)
                
            # Hiển thị thông báo lỗi
            QMessageBox.warning(self, "Lỗi", error_msg)


class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None, is_new=False):
        super().__init__(parent)
        self.task = task or {}
        self.is_new = is_new
        self.scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        
        self.setWindowTitle("Lên lịch Task")
        self.resize(500, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Basic settings
        basic_group = QGroupBox("Thông tin cơ bản")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit(self.task.get('name', ''))
        basic_layout.addRow("Tên task:", self.name_edit)
        
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        
        # Nếu là task đã tồn tại, đặt thời gian lên lịch
        if 'run_time' in self.task:
            try:
                dt = datetime.datetime.strptime(self.task['run_time'], "%Y-%m-%d %H:%M")
                self.datetime_edit.setDateTime(QDateTime(
                    dt.year, dt.month, dt.day, dt.hour, dt.minute
                ))
            except:
                pass
                
        basic_layout.addRow("Thời gian chạy:", self.datetime_edit)
        
        self.script_combo = QComboBox()
        self.load_scripts()
        
        if 'script' in self.task and self.task['script'] in [self.script_combo.itemData(i) 
                                                         for i in range(self.script_combo.count())]:
            index = [self.script_combo.itemData(i) for i in range(self.script_combo.count())].index(self.task['script'])
            self.script_combo.setCurrentIndex(index)
            
        basic_layout.addRow("Script:", self.script_combo)
        
        self.enabled_cb = QCheckBox("Bật task này")
        self.enabled_cb.setChecked(self.task.get('enabled', True))
        basic_layout.addRow("", self.enabled_cb)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Recurring settings
        recurring_group = QGroupBox("Cài đặt lặp lại")
        recurring_layout = QFormLayout()
        
        self.recurring_combo = QComboBox()
        self.recurring_combo.addItem("Không lặp lại", "")
        self.recurring_combo.addItem("Hàng ngày", "daily")
        self.recurring_combo.addItem("Hàng tuần", "weekly")
        self.recurring_combo.addItem("Hàng tháng", "monthly")
        self.recurring_combo.addItem("Hàng giờ", "hourly")
        
        # Set giá trị lặp lại nếu có
        recurring = self.task.get('recurring', '')
        index = 0
        for i in range(self.recurring_combo.count()):
            if self.recurring_combo.itemData(i) == recurring:
                index = i
                break
        self.recurring_combo.setCurrentIndex(index)
        
        recurring_layout.addRow("Lặp lại:", self.recurring_combo)
        recurring_group.setLayout(recurring_layout)
        layout.addWidget(recurring_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_scripts(self):
        self.script_combo.clear()
        
        if os.path.exists(self.scripts_dir):
            for filename in os.listdir(self.scripts_dir):
                if filename.endswith(".py"):
                    script_path = os.path.join(self.scripts_dir, filename)
                    self.script_combo.addItem(filename, script_path)
    
    def validate_and_accept(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên task không được để trống")
            return
            
        if self.script_combo.currentData() is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn script")
            return
            
        self.accept()
    
    def get_task_data(self):
        """Trả về dữ liệu task từ dialog"""
        return {
            'name': self.name_edit.text().strip(),
            'run_time': self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm"),
            'script': self.script_combo.currentData(),
            'enabled': self.enabled_cb.isChecked(),
            'recurring': self.recurring_combo.currentData(),
            'parameters': self.task.get('parameters', {})
        } 
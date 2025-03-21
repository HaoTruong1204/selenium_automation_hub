# modules/dashboard.py

from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QSizePolicy,
    QTabWidget, QListWidget, QListWidgetItem, QTextEdit, QTextBrowser, QSplitter, QMessageBox,
    QScrollArea, QCheckBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QBrush, QColor, QDesktopServices
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QUrl
import os
import time
import psutil
from datetime import datetime

class StatCard(QFrame):
    """
    Card hiển thị thông số thống kê (StatCard).
    Màu sắc, font, v.v... có thể được điều khiển qua QSS để đồng nhất giao diện.
    """
    def __init__(self, title, value, icon_path=None, color="#0d6efd", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("statCard")
        # Đặt property để QSS có thể điều khiển màu nền/gradient
        self.setProperty("cardColor", color)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Header layout chứa icon và tiêu đề
        header_layout = QHBoxLayout()
        if icon_path:
            self.icon_label = QLabel()
            # Kiểm tra xem file icon có tồn tại không
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(pixmap)
            self.icon_label.setObjectName("statIcon")
            header_layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statTitle")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Giá trị thống kê
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("statValue")
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(self.value_label, alignment=Qt.AlignLeft)
        layout.addStretch()
    
    def update_value(self, new_value):
        """Cập nhật giá trị hiển thị trên card."""
        self.value_label.setText(str(new_value))

class TrendingTopicItem(QWidget):
    """
    Widget hiển thị thông tin về một chủ đề trending
    """
    def __init__(self, trend_data, parent=None):
        super().__init__(parent)
        self.trend_data = trend_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(8)
        
        # Title with rank indicator
        title_layout = QHBoxLayout()
        
        rank = QLabel(f"#{self.trend_data['id']}")
        rank.setStyleSheet("font-weight: bold; color: #0d6efd; min-width: 30px;")
        title_layout.addWidget(rank)
        
        title = QLabel(self.trend_data['title'])
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setWordWrap(True)
        title_layout.addWidget(title)
        
        layout.addLayout(title_layout)
        
        # Traffic info
        traffic_layout = QHBoxLayout()
        traffic_icon = QLabel("🔥")
        traffic_layout.addWidget(traffic_icon)
        
        traffic = QLabel(self.trend_data.get('traffic', 'Unknown'))
        traffic.setStyleSheet("color: #dc3545;")
        traffic_layout.addWidget(traffic)
        
        traffic_layout.addStretch()
        
        source = QLabel(self.trend_data.get('source', 'Unknown source'))
        source.setFont(QFont("Segoe UI", 9, weight=QFont.Normal, italic=True))
        source.setStyleSheet("color: #6c757d;")
        traffic_layout.addWidget(source)
        
        layout.addLayout(traffic_layout)
        
        # Description if available
        if 'description' in self.trend_data and self.trend_data['description']:
            desc = QLabel(self.trend_data['description'])
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #6c757d; margin-top: 5px;")
            layout.addWidget(desc)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Details")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        view_btn.clicked.connect(self.view_details)
        actions_layout.addWidget(view_btn)
        
        create_content_btn = QPushButton("Create Content")
        create_content_btn.setObjectName("create_content_btn")
        create_content_btn.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #157347;
            }
        """)
        create_content_btn.clicked.connect(self.create_content)
        actions_layout.addWidget(create_content_btn)
        
        layout.addLayout(actions_layout)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dee2e6; margin-top: 10px;")
        layout.addWidget(line)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #e9ecef;
            }
        """)
        
    def view_details(self):
        if 'link' in self.trend_data and self.trend_data['link']:
            QDesktopServices.openUrl(QUrl(self.trend_data['link']))
            
    def create_content(self):
        # Signal that we want to create content from this trend
        # This will be connected to a handler in the parent widget
        parent = self.parent()
        while parent and not isinstance(parent, DashboardWidget):
            parent = parent.parent()
            
        if parent and isinstance(parent, DashboardWidget):
            parent.request_content_creation(self.trend_data)

class TrendingWidget(QWidget):
    """Widget to display trending topics"""
    create_content_signal = pyqtSignal(dict)  # Signal when a content creation is requested

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with refresh button
        header_layout = QHBoxLayout()
        
        title = QLabel("Trending Topics")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        refresh_btn.clicked.connect(self.on_refresh_clicked)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)

        # Source selection
        source_layout = QHBoxLayout()
        
        source_label = QLabel("Source:")
        source_layout.addWidget(source_label)
        
        self.google_trends_checkbox = QCheckBox("Google Trends")
        self.google_trends_checkbox.setChecked(True)
        source_layout.addWidget(self.google_trends_checkbox)
        
        self.facebook_trends_checkbox = QCheckBox("Facebook")
        self.facebook_trends_checkbox.setChecked(True)
        source_layout.addWidget(self.facebook_trends_checkbox)
        
        source_layout.addStretch()
        
        layout.addLayout(source_layout)
        
        # Scroll area for trending items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.trends_container = QWidget()
        self.trends_layout = QVBoxLayout(self.trends_container)
        self.trends_layout.setContentsMargins(0, 0, 0, 0)
        self.trends_layout.setSpacing(10)
        self.trends_layout.addStretch()
        
        scroll_area.setWidget(self.trends_container)
        layout.addWidget(scroll_area)
        
    def on_refresh_clicked(self):
        # This would be connected to the dashboard's refresh_trends method
        parent = self.parent()
        while parent and not isinstance(parent, DashboardWidget):
            parent = parent.parent()
            
        if parent and isinstance(parent, DashboardWidget):
            parent.refresh_trends()
            
    def add_trending_topic(self, topic_data):
        """Add a trending topic item to the list"""
        # Create the trend item widget
        item_widget = TrendingTopicItem(topic_data)
        
        # Connect the create_content method to our signal
        # Use a lambda to pass along the topic data
        item_widget.create_content_btn = item_widget.findChild(QPushButton, "create_content_btn")
        if item_widget.create_content_btn:
            item_widget.create_content_btn.clicked.connect(
                lambda: self.create_content_signal.emit(topic_data)
            )
        
        # Insert at the top (before the stretch)
        self.trends_layout.insertWidget(self.trends_layout.count() - 1, item_widget)
        
    def clear_topics(self):
        """Clear all trending topics"""
        # Remove all widgets except the stretch at the end
        while self.trends_layout.count() > 1:
            item = self.trends_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class ContentWidget(QWidget):
    """
    Widget hiển thị nội dung đã tạo và cho phép đăng
    """
    post_content_signal = pyqtSignal(dict, str)  # Phát tín hiệu khi nút đăng bài được nhấn

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_content = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tiêu đề
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Nội dung đã tạo")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Khu vực hiển thị nội dung
        content_layout = QHBoxLayout()
        
        # Panel nội dung trái (tiêu đề, nội dung)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Tiêu đề nội dung
        self.content_title_label = QLabel("Tiêu đề:")
        self.content_title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_title = QTextEdit()
        self.content_title.setMaximumHeight(60)
        self.content_title.setPlaceholderText("Tiêu đề nội dung sẽ hiển thị ở đây...")
        
        # Nội dung chính
        self.content_body_label = QLabel("Nội dung:")
        self.content_body_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_body = QTextEdit()
        self.content_body.setPlaceholderText("Nội dung chính sẽ hiển thị ở đây...")
        
        left_layout.addWidget(self.content_title_label)
        left_layout.addWidget(self.content_title)
        left_layout.addWidget(self.content_body_label)
        left_layout.addWidget(self.content_body)
        
        # Panel nội dung phải (hashtags, nguồn)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Hashtags
        self.hashtags_label = QLabel("Hashtags:")
        self.hashtags_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.hashtags_list = QListWidget()
        self.hashtags_list.setMaximumHeight(150)
        
        # Thông tin nguồn
        self.source_label = QLabel("Thông tin nguồn:")
        self.source_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.source_info = QTextBrowser()
        self.source_info.setMaximumHeight(100)
        
        right_layout.addWidget(self.hashtags_label)
        right_layout.addWidget(self.hashtags_list)
        right_layout.addWidget(self.source_label)
        right_layout.addWidget(self.source_info)
        right_layout.addStretch()
        
        # Thêm panels vào layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])  # Tỷ lệ kích thước ban đầu
        
        content_layout.addWidget(splitter)
        layout.addLayout(content_layout)
        
        # Nút đăng bài
        action_layout = QHBoxLayout()
        
        self.post_now_btn = QPushButton("Đăng ngay")
        self.post_now_btn.setIcon(QIcon("resources/icons/upload.png"))
        self.post_now_btn.clicked.connect(self.post_now)
        
        self.schedule_post_btn = QPushButton("Lập lịch đăng")
        self.schedule_post_btn.setIcon(QIcon("resources/icons/calendar.png"))
        self.schedule_post_btn.clicked.connect(self.schedule_post)
        
        self.clear_btn = QPushButton("Xóa nội dung")
        self.clear_btn.setIcon(QIcon("resources/icons/delete.png"))
        self.clear_btn.clicked.connect(self.clear_content)
        
        action_layout.addWidget(self.post_now_btn)
        action_layout.addWidget(self.schedule_post_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.clear_btn)
        
        layout.addLayout(action_layout)
        
    def display_content(self, content):
        """
        Hiển thị nội dung đã tạo
        """
        if not content:
            return
            
        self.current_content = content
        
        # Hiển thị tiêu đề
        self.content_title.setText(content.get("title", ""))
        
        # Hiển thị nội dung
        self.content_body.setText(content.get("content", ""))
        
        # Hiển thị hashtags
        self.hashtags_list.clear()
        for hashtag in content.get("hashtags", []):
            self.hashtags_list.addItem(hashtag)
            
        # Hiển thị thông tin nguồn
        source_text = f"Nguồn: {content.get('source_trend', 'Không rõ')}\n"
        source_text += f"Thời gian tạo: {content.get('created_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}"
        self.source_info.setText(source_text)
        
    def clear_content(self):
        """
        Xóa nội dung hiện tại
        """
        self.current_content = None
        self.content_title.clear()
        self.content_body.clear()
        self.hashtags_list.clear()
        self.source_info.clear()

    def post_now(self):
        """Kiểm tra content trước khi phát tín hiệu post_content_signal"""
        if self.current_content:
            self.post_content_signal.emit(self.current_content, "now")
        else:
            # Hiển thị thông báo nếu không có nội dung
            QMessageBox.warning(self, "Không có nội dung", "Vui lòng tạo nội dung trước khi đăng.")
            
    def schedule_post(self):
        """Kiểm tra content trước khi phát tín hiệu post_content_signal"""
        if self.current_content:
            self.post_content_signal.emit(self.current_content, "schedule")
        else:
            # Hiển thị thông báo nếu không có nội dung
            QMessageBox.warning(self, "Không có nội dung", "Vui lòng tạo nội dung trước khi lập lịch đăng.")

class DashboardWidget(QWidget):
    """
    Widget Dashboard hiển thị:
      - 4 thẻ thống kê (StatCard) bố trí dạng 2x2
      - Khu vực "Các Task gần đây" với bảng Task và 2 nút "Làm mới", "Chạy Task mới"
      - Tiến trình CPU/Memory
      - *MỚI* Thêm các tab để hiển thị trends và nội dung đã tạo
    """
    # Signal để yêu cầu lấy trends
    get_trends_signal = pyqtSignal(str)  # Loại trend: "google" hoặc "facebook"
    
    # Signal để yêu cầu tạo nội dung từ trend
    create_content_signal = pyqtSignal(dict, str)  # Trend data và content_type
    
    # Signal để yêu cầu đăng bài
    post_content_signal = pyqtSignal(dict, str)  # Content data và post_type
    
    # Signal để cập nhật khi có stats mới
    update_stats_signal = pyqtSignal(dict)
    
    # Signal để chuyển trang
    navigate_signal = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Dữ liệu thống kê
        self.stats = {
            "task_count": 0,
            "success_rate": 0,
            "active_proxies": 0,
            "script_count": 0
        }
        
        # Timer cập nhật thống kê và CPU/Memory (mỗi 5 giây)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_stats)
        self.update_timer.start(5000)

    def init_ui(self):
        # Áp dụng một stylesheet đơn giản để QGroupBox có viền và tiêu đề nhẹ nhàng
        self.setStyleSheet("""
        QGroupBox#tasksBox {
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-top: 10px;
            font: 15px "Segoe UI";
            color: #2c3e50;
        }
        QGroupBox#tasksBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            background-color: transparent;
            margin-left: 10px;
            margin-top: 2px;
            padding: 0 5px;
            font: bold 14px "Segoe UI";
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
            border-radius: 6px;
                background-color: white;
            padding: 5px;
        }
        QTabBar::tab {
            background: #f1f1f1; 
            border: 1px solid #ccc;
            border-bottom-color: white;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 100px;
            padding: 5px;
            font: 12px "Segoe UI";
        }
        QTabBar::tab:selected {
            background: white;
            border-bottom-color: white;
                font-weight: bold;
            }
        """)

        # Layout tổng thể
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # Tiêu đề Dashboard
        title_panel = QFrame()
        title_panel.setObjectName("titlePanel")
        title_layout = QVBoxLayout(title_panel)
        
        self.dashboard_title = QLabel("Dashboard")
        self.dashboard_title.setObjectName("dashboardTitle")
        self.dashboard_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.dashboard_title.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(self.dashboard_title)
        main_layout.addWidget(title_panel)
        
        # Lưới các StatCard (2 x 2)
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.task_card = StatCard("Tổng số Task", "0", "resources/icons/tasks.png", "#0d6efd")
        stats_layout.addWidget(self.task_card, 0, 0)
        
        self.success_card = StatCard("Tỷ lệ thành công", "0%", "resources/icons/success.png", "#28a745")
        stats_layout.addWidget(self.success_card, 0, 1)
        
        self.proxy_card = StatCard("Proxy đang hoạt động", "0", "resources/icons/proxy.png", "#6f42c1")
        stats_layout.addWidget(self.proxy_card, 1, 0)
        
        self.script_card = StatCard("Tổng số Script", "0", "resources/icons/script.png", "#fd7e14")
        stats_layout.addWidget(self.script_card, 1, 1)
        
        main_layout.addLayout(stats_layout)
        
        # Create main tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setObjectName("mainTabs")
        
        # Tasks tab
        self.tasks_tab = QWidget()
        tasks_layout = QVBoxLayout(self.tasks_tab)
        
        # Tasks table
        self.stats_table = QTableWidget(0, 5)
        self.stats_table.setObjectName("statsTable")
        self.stats_table.setHorizontalHeaderLabels(["Task", "Loại", "Thời gian", "Trạng thái", "Kết quả"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stats_table.setMinimumHeight(250)
        
        tasks_layout.addWidget(self.stats_table)
        
        # Buttons
        tool_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        self.run_btn = QPushButton("Chạy Task mới")
        self.run_btn.setObjectName("run_btn")
        self.run_btn.setIcon(QIcon("resources/icons/play.png"))
        self.run_btn.clicked.connect(self.run_new_task)
        
        tool_layout.addWidget(self.refresh_btn)
        tool_layout.addWidget(self.run_btn)
        tool_layout.addStretch()
        tasks_layout.addLayout(tool_layout)
        
        # Add trending widget to tabs
        self.trending_widget = TrendingWidget()
        
        # Add content widget to tabs
        self.content_widget = ContentWidget()
        
        # Add tabs
        self.main_tabs.addTab(self.tasks_tab, "Các Task gần đây")
        self.main_tabs.addTab(self.trending_widget, "Xu hướng & Trending")
        self.main_tabs.addTab(self.content_widget, "Nội dung")
        
        main_layout.addWidget(self.main_tabs)
        
        # System status section
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Tình trạng hệ thống:")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFont(QFont("Segoe UI", 12))
        
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setObjectName("cpuProgress")
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(30)
        self.cpu_progress.setFormat("CPU: %p%")
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setObjectName("memoryProgress")
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(45)
        self.memory_progress.setFormat("Memory: %p%")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.cpu_progress)
        status_layout.addWidget(self.memory_progress)
        main_layout.addLayout(status_layout)
        
        # Add sample data
        self.add_sample_tasks()
        self.add_sample_trends()
        self.add_sample_content()

        # Connect signals
        self.trending_widget.create_content_signal.connect(self.request_content_creation)
        self.content_widget.post_content_signal.connect(self.request_post_content)

    def add_sample_tasks(self):
        """
        Thêm dữ liệu mẫu vào bảng "Các Task gần đây".
        Bạn có thể thay thế bằng dữ liệu thực tế từ hệ thống.
        """
        sample_data = [
            {"task": "Google Search", "type": "Web Search", "time": "02:30", "status": "Hoàn thành", "result": "10 kết quả"},
            {"task": "Facebook Login", "type": "Authentication", "time": "01:15", "status": "Hoàn thành", "result": "Thành công"},
            {"task": "Shopee Scrape", "type": "Data Collection", "time": "05:45", "status": "Tạm dừng", "result": "42 sản phẩm"}
        ]
        
        self.stats_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            self.stats_table.setItem(row, 0, QTableWidgetItem(data["task"]))
            self.stats_table.setItem(row, 1, QTableWidgetItem(data["type"]))
            self.stats_table.setItem(row, 2, QTableWidgetItem(data["time"]))
            
            status_item = QTableWidgetItem(data["status"])
            # Tô màu dựa trên trạng thái
            if data["status"] == "Hoàn thành":
                status_item.setForeground(QBrush(QColor("#4cd137")))
                status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            elif data["status"] == "Tạm dừng":
                status_item.setForeground(QBrush(QColor("#fbc531")))
                status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            else:
                status_item.setForeground(QBrush(QColor("#e84118")))
                status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.stats_table.setItem(row, 3, status_item)
            
            result_item = QTableWidgetItem(data["result"])
            result_item.setForeground(QBrush(QColor("#2c3e50")))
            self.stats_table.setItem(row, 4, result_item)

    def update_system_stats(self):
        """
        Cập nhật thống kê hệ thống (CPU, Memory) từ thông tin thực tế
        """
        try:
            # Cập nhật CPU
            cpu_percent = psutil.cpu_percent()
            self.cpu_progress.setValue(int(cpu_percent))
            
            # Cập nhật Memory
            memory = psutil.virtual_memory()
            self.memory_progress.setValue(int(memory.percent))
        except:
            # Fallback nếu không thể lấy thông tin hệ thống thực
            import random
            self.cpu_progress.setValue(random.randint(20, 80))
            self.memory_progress.setValue(random.randint(30, 70))

    def refresh_data(self):
        """Cập nhật số liệu và làm mới danh sách task."""
        self.update_system_stats()
        # Nếu có logic lấy dữ liệu thực, thêm vào đây

    def run_new_task(self):
        """
        Khi nhấn "Chạy Task mới", chuyển sang trang Automation.
        """
        # Phát tín hiệu để MainWindow xử lý
        self.navigate_signal.emit(1)  # Chuyển đến trang Automation (index 1)
        print("Đã gửi tín hiệu navigate_signal để chuyển đến trang Automation")
        
        # Cách truyền thống - dự phòng trong trường hợp tín hiệu không được kết nối
        try:
            # Tìm MainWindow từ parent hierarchy
            parent = self.parent()
            while parent and not hasattr(parent, 'switch_page'):
                parent = parent.parent()
                
            if parent and hasattr(parent, 'switch_page'):
                parent.switch_page(1)  # Chuyển đến trang Automation
        except Exception as e:
            print(f"Lỗi khi chuyển trang: {str(e)}")

    def update_recent_task(self, task_name, task_type, elapsed_time, status, result=""):
        """
        Cập nhật một Task mới vào đầu bảng.
        """
        self.stats_table.insertRow(0)
        self.stats_table.setItem(0, 0, QTableWidgetItem(task_name))
        self.stats_table.setItem(0, 1, QTableWidgetItem(task_type))
        self.stats_table.setItem(0, 2, QTableWidgetItem(elapsed_time))
        
        status_item = QTableWidgetItem(status)
        if status == "Hoàn thành":
            status_item.setForeground(QBrush(QColor("#28a745")))
        elif status == "Đang chạy":
            status_item.setForeground(QBrush(QColor("#0d6efd")))
        elif status == "Tạm dừng":
            status_item.setForeground(QBrush(QColor("#ffc107")))
        else:
            status_item.setForeground(QBrush(QColor("#dc3545")))
        self.stats_table.setItem(0, 3, status_item)
        self.stats_table.setItem(0, 4, QTableWidgetItem(result))
        
        # Giữ tối đa 10 dòng mới nhất
        if self.stats_table.rowCount() > 10:
            self.stats_table.removeRow(10)
        
        # Tăng đếm task
        self.stats["task_count"] += 1
        self.task_card.update_value(self.stats["task_count"])
        
    def update_stat_cards(self, stats):
        """
        Cập nhật các thẻ thống kê từ dữ liệu thực tế
        """
        if "task_count" in stats:
            self.task_card.update_value(stats["task_count"])
            self.stats["task_count"] = stats["task_count"]
            
        if "success_rate" in stats:
            self.success_card.update_value(f"{stats['success_rate']}%")
            self.stats["success_rate"] = stats["success_rate"]
            
        if "active_proxies" in stats:
            self.proxy_card.update_value(stats["active_proxies"])
            self.stats["active_proxies"] = stats["active_proxies"]
            
        if "script_count" in stats:
            self.script_card.update_value(stats["script_count"])
            self.stats["script_count"] = stats["script_count"]
            
    def add_trending_topics(self, topics, source="google"):
        """
        Thêm danh sách chủ đề đang trending vào widget
        """
        if not topics:
            return
            
        try:
            self.log(f"Đang cập nhật {len(topics)} xu hướng từ {source}...")
            
            # Xóa dữ liệu cũ nếu có
            if source == "google":
                self.trending_widget.clear_topics()
            elif source == "facebook":
                self.trending_widget.clear_topics()
            else:
                # Nếu source không rõ ràng, xóa tất cả
                self.trending_widget.clear_topics()
                
            # Kiểm tra định dạng dữ liệu
            for topic in topics:
                if not isinstance(topic, dict):
                    self.log(f"⚠️ Bỏ qua dữ liệu không hợp lệ: {topic}")
                    continue
                    
                # Chuẩn hóa dữ liệu topic
                if source == "google" and "source" not in topic:
                    topic["source"] = "Google Trends"
                elif source == "facebook" and "source" not in topic:
                    topic["source"] = "Facebook"
                
                # Đảm bảo có keyword
                if "keyword" not in topic and "title" in topic:
                    topic["keyword"] = topic["title"]
                elif "keyword" not in topic and "text" in topic:
                    topic["keyword"] = topic["text"]
                elif "keyword" not in topic:
                    topic["keyword"] = "Unknown trend"
                
                # Thêm vào widget
                self.trending_widget.add_trending_topic(topic)
            
            self.log(f"✅ Đã cập nhật {len(topics)} xu hướng.")
        except Exception as e:
            self.log(f"❌ Lỗi khi cập nhật xu hướng: {str(e)}")
            # Ghi log lỗi chi tiết
            import traceback
            print(f"Error in add_trending_topics: {traceback.format_exc()}")
            
    def refresh_trends(self):
        """
        Làm mới danh sách trends từ Google và Facebook
        """
        self.trending_widget.clear_topics()
        self.log("🔄 Đang làm mới xu hướng...")
        
        # Hiển thị thông báo đang tải
        loading_label = QLabel("Đang tải xu hướng...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("color: #6c757d; font-style: italic;")
        self.trending_widget.trends_layout.insertWidget(0, loading_label)
        
        # Gửi yêu cầu lấy xu hướng
        self.get_trends_signal.emit("google")
        self.get_trends_signal.emit("facebook")
            
    def display_content(self, content):
        """
        Hiển thị nội dung đã tạo trong tab nội dung
        """
        self.content_widget.display_content(content)
        # Chuyển đến tab nội dung
        self.main_tabs.setCurrentIndex(2)
        
    def request_content_creation(self, trend_data):
        """
        Yêu cầu tạo nội dung từ một trend
        """
        if not trend_data or not isinstance(trend_data, dict):
            self.log("⚠️ Không có dữ liệu xu hướng để tạo nội dung")
            return
            
        self.log(f"📝 Yêu cầu tạo nội dung cho: {trend_data.get('keyword', 'Không xác định')}")
        
        # Hiển thị thông báo đang tạo nội dung
        self.content_widget.content_title.setPlaceholderText("Đang tạo nội dung...")
        self.content_widget.content_body.setPlaceholderText("Vui lòng đợi trong giây lát...")
        
        # Phát signal yêu cầu tạo nội dung (với loại nội dung mặc định là "article")
        self.create_content_signal.emit(trend_data, "article")
        
        # Chuyển đến tab nội dung
        self.main_tabs.setCurrentIndex(2)
        
    def request_post_content(self, content_data, post_type):
        """
        Yêu cầu đăng nội dung lên mạng xã hội
        """
        if not content_data or not isinstance(content_data, dict):
            self.log("⚠️ Không có nội dung để đăng")
            return
            
        self.log(f"📤 Yêu cầu đăng nội dung: {post_type}")
        
        # Phát signal yêu cầu đăng bài
        self.post_content_signal.emit(content_data, post_type)
        
    def log(self, message):
        """
        Hiển thị message trong console và có thể gửi đến module logs
        """
        print(f"[Dashboard] {message}")
        # Nếu có kết nối với LogsWidget, có thể gửi log đến đó

    def add_sample_trends(self):
        """Add sample trending topics for demonstration"""
        sample_trends = [
            {
                "id": 1,
                "title": "World Cup 2026",
                "traffic": "1M+ searches",
                "description": "2026 FIFA World Cup news and updates",
                "source": "Google Trends",
                "link": "https://www.google.com/search?q=World+Cup+2026"
            },
            {
                "id": 2,
                "title": "#Technology",
                "traffic": "500K+ posts",
                "description": "Latest technology news and innovations",
                "source": "Facebook",
                "link": "https://www.facebook.com/hashtag/technology"
            },
            {
                "id": 3,
                "title": "Climate Change",
                "traffic": "800K+ searches",
                "description": "Global climate initiatives and environmental news",
                "source": "Google Trends",
                "link": "https://www.google.com/search?q=Climate+Change"
            },
            {
                "id": 4,
                "title": "#Entertainment",
                "traffic": "600K+ posts",
                "description": "Entertainment news, movies, and celebrity updates",
                "source": "Facebook",
                "link": "https://www.facebook.com/hashtag/entertainment"
            },
            {
                "id": 5,
                "title": "Crypto Market",
                "traffic": "750K+ searches",
                "description": "Cryptocurrency market trends and analysis",
                "source": "Google Trends",
                "link": "https://www.google.com/search?q=Crypto+Market"
            }
        ]
        
        for trend in sample_trends:
            self.trending_widget.add_trending_topic(trend)

    def add_sample_content(self):
        """
        Thêm nội dung mẫu vào tab nội dung
        """
        sample_content = {
            "title": "Trí tuệ nhân tạo thay đổi ngành công nghệ như thế nào?",
            "content": "Trí tuệ nhân tạo (AI) đang thay đổi ngành công nghệ một cách sâu sắc. Từ trợ lý ảo đến xe tự lái, AI đang thay đổi cách chúng ta tương tác với công nghệ.\n\n" +
                       "## Tác động của AI trong lĩnh vực phát triển phần mềm\n\n" +
                       "Các công cụ AI như GitHub Copilot đang giúp lập trình viên tạo ra code nhanh hơn và hiệu quả hơn. AI cũng đang được sử dụng để tối ưu hóa các quy trình CI/CD.\n\n" +
                       "## AI và tương lai của tự động hóa\n\n" +
                       "Tự động hóa là một trong những lĩnh vực mà AI đang có tác động lớn nhất. Từ việc tự động hóa các quy trình sản xuất đến việc tự động hóa các tác vụ văn phòng.",
            "hashtags": ["#AI", "#TríTuệNhânTạo", "#CôngNghệ", "#TựĐộngHóa"],
            "source_trend": "Trí tuệ nhân tạo",
            "created_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.content_widget.display_content(sample_content)

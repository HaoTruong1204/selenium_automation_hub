"""
Package chứa các module và tiện ích cho ứng dụng.
"""

# Khai báo các module quan trọng để có thể import trực tiếp
from .automation_worker_fixed import EnhancedAutomationWorker
from .app_ui import MainWindow

__all__ = [
    'automation_worker_fixed',
    'automation_worker',
    'app_ui',
    'utils'
] 
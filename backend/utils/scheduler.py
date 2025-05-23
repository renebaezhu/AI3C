import threading
import time
import datetime
import logging
from flask import current_app
from ..services.monitoring_service import SystemMonitor

class MetricsScheduler:
    """
    指标收集调度器，负责定期收集系统指标
    """
    
    def __init__(self, app=None, interval=3600):
        """
        初始化调度器
        
        参数:
        - app: Flask应用实例
        - interval: 收集指标的时间间隔（秒），默认为1小时
        """
        self.app = app
        self.interval = interval
        self.thread = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """
        配置应用
        
        参数:
        - app: Flask应用实例
        """
        self.app = app
        
        # 应用启动时启动调度任务
        @app.before_first_request
        def start_scheduler():
            self.start()
            
        # 应用关闭时停止任务
        @app.teardown_appcontext
        def stop_scheduler(exception=None):
            self.stop()
            
    def collect_metrics(self):
        """
        收集系统指标的任务
        """
        with self.app.app_context():
            try:
                self.logger.info(f"开始收集系统指标: {datetime.datetime.now()}")
                SystemMonitor.log_system_metrics()
            except Exception as e:
                self.logger.error(f"收集系统指标失败: {str(e)}")
    
    def scheduled_task(self):
        """
        定时运行的任务
        """
        while self.running:
            try:
                self.collect_metrics()
            except Exception as e:
                if self.app:
                    with self.app.app_context():
                        current_app.logger.error(f"执行调度任务失败: {str(e)}")
                else:
                    self.logger.error(f"执行调度任务失败: {str(e)}")
            
            # 等待下一次执行
            time.sleep(self.interval)
    
    def start(self):
        """
        启动定时任务
        """
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self.scheduled_task)
            self.thread.daemon = True  # 设置为守护线程，这样应用退出时线程会自动终止
            self.thread.start()
            
            if self.app:
                with self.app.app_context():
                    current_app.logger.info("系统指标调度器已启动")
            else:
                self.logger.info("系统指标调度器已启动")
    
    def stop(self):
        """
        停止定时任务
        """
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            
            if self.app:
                with self.app.app_context():
                    current_app.logger.info("系统指标调度器已停止")
            else:
                self.logger.info("系统指标调度器已停止")
                
# 创建调度器实例
metrics_scheduler = MetricsScheduler() 
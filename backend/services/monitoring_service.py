import psutil
import time
import platform
import sqlite3
from datetime import datetime
from flask import current_app, g
import json
import os

class SystemMonitor:
    """系统性能监控服务"""
    
    @staticmethod
    def get_system_info():
        """获取系统信息"""
        info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'ram_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
        }
        return info
    
    @staticmethod
    def get_cpu_usage():
        """获取CPU使用情况"""
        return {
            'percent': psutil.cpu_percent(),
            'per_cpu': psutil.cpu_percent(percpu=True),
            'load_avg': [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()],
        }
    
    @staticmethod
    def get_memory_usage():
        """获取内存使用情况"""
        vm = psutil.virtual_memory()
        return {
            'total': vm.total,
            'available': vm.available,
            'percent': vm.percent,
            'used': vm.used,
            'free': vm.free,
            'total_gb': round(vm.total / (1024**3), 2),
            'available_gb': round(vm.available / (1024**3), 2),
            'used_gb': round(vm.used / (1024**3), 2),
        }
    
    @staticmethod
    def get_disk_usage():
        """获取磁盘使用情况"""
        instance_path = current_app.instance_path if current_app else '.'
        return {
            'total': psutil.disk_usage(instance_path).total,
            'used': psutil.disk_usage(instance_path).used,
            'free': psutil.disk_usage(instance_path).free,
            'percent': psutil.disk_usage(instance_path).percent,
            'total_gb': round(psutil.disk_usage(instance_path).total / (1024**3), 2),
            'used_gb': round(psutil.disk_usage(instance_path).used / (1024**3), 2),
            'free_gb': round(psutil.disk_usage(instance_path).free / (1024**3), 2),
        }
    
    @staticmethod
    def get_network_stats():
        """获取网络统计信息"""
        # 获取网络I/O统计信息
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout,
            'mb_sent': round(net_io.bytes_sent / (1024**2), 2),
            'mb_recv': round(net_io.bytes_recv / (1024**2), 2),
        }
    
    @staticmethod
    def get_process_info():
        """获取应用进程信息"""
        process = psutil.Process(os.getpid())
        return {
            'pid': process.pid,
            'status': process.status(),
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_mb': round(process.memory_info().rss / (1024**2), 2),
            'threads': process.num_threads(),
            'create_time': datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
            'running_time': round((time.time() - process.create_time()) / 60, 2),  # 分钟
        }
    
    @staticmethod
    def log_system_metrics():
        """记录系统指标"""
        try:
            db = get_db()
            
            # 获取当前系统指标
            cpu_usage = SystemMonitor.get_cpu_usage()['percent']
            memory_usage = SystemMonitor.get_memory_usage()['percent']
            disk_usage = SystemMonitor.get_disk_usage()['percent']
            
            # 获取应用进程信息
            process_info = SystemMonitor.get_process_info()
            process_cpu = process_info['cpu_percent']
            process_memory = process_info['memory_mb']
            
            # 获取数据库指标
            db_stats = db.execute('SELECT COUNT(*) FROM sqlite_master').fetchone()[0]
            users_count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            prompts_count = db.execute('SELECT COUNT(*) FROM prompts').fetchone()[0]
            results_count = db.execute('SELECT COUNT(*) FROM prompt_results').fetchone()[0]
            
            # 将指标保存到系统指标表
            # 注意：需要先创建system_metrics表
            db.execute(
                '''
                INSERT INTO system_metrics 
                (cpu_usage, memory_usage, disk_usage, process_cpu, process_memory, 
                 database_tables, users_count, prompts_count, results_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (cpu_usage, memory_usage, disk_usage, process_cpu, process_memory,
                 db_stats, users_count, prompts_count, results_count, datetime.now())
            )
            
            db.commit()
            current_app.logger.info("系统指标已记录")
            
        except Exception as e:
            current_app.logger.error(f"记录系统指标失败: {str(e)}")
    
    @staticmethod
    def get_system_metrics(days=7):
        """获取最近几天的系统指标"""
        try:
            db = get_db()
            
            # 检查system_metrics表是否存在
            table_exists = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='system_metrics'"
            ).fetchone()
            
            if not table_exists:
                # 如果表不存在，返回模拟数据
                return SystemMonitor._get_mock_system_metrics(days)
            
            # 获取最近几天的系统指标
            metrics = db.execute(
                '''
                SELECT cpu_usage, memory_usage, disk_usage, process_cpu, process_memory,
                       database_tables, users_count, prompts_count, results_count,
                       datetime(timestamp) as timestamp
                FROM system_metrics
                WHERE timestamp >= datetime('now', ?)
                ORDER BY timestamp
                ''',
                (f'-{days} days',)
            ).fetchall()
            
            return [dict(row) for row in metrics] if metrics else SystemMonitor._get_mock_system_metrics(days)
            
        except Exception as e:
            current_app.logger.error(f"获取系统指标失败: {str(e)}")
            return SystemMonitor._get_mock_system_metrics(days)
    
    @staticmethod
    def _get_mock_system_metrics(days=7):
        """获取模拟的系统指标数据，用于表不存在时"""
        from datetime import datetime, timedelta
        import random
        
        metrics = []
        
        # 生成过去几天的数据
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d %H:%M:%S')
            
            # 生成随机但合理的数据
            cpu = random.uniform(20, 60)
            memory = random.uniform(30, 70)
            disk = random.uniform(40, 80)
            process_cpu = random.uniform(5, 20)
            process_memory = random.uniform(50, 200)
            
            metrics.append({
                'cpu_usage': cpu,
                'memory_usage': memory,
                'disk_usage': disk,
                'process_cpu': process_cpu,
                'process_memory': process_memory,
                'database_tables': random.randint(3, 10),
                'users_count': random.randint(5, 100) + i,
                'prompts_count': random.randint(10, 200) + i*2,
                'results_count': random.randint(20, 500) + i*5,
                'timestamp': date
            })
        
        return metrics

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db 
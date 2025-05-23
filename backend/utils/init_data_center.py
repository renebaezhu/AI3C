import sys
import os
import random
import sqlite3
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from AI3C.backend.app import create_app
from AI3C.backend.services.monitoring_service import SystemMonitor

def init_system_metrics(db, days=30):
    """初始化系统指标数据"""
    print("正在初始化系统指标数据...")
    
    # 检查system_metrics表是否存在
    table_exists = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='system_metrics'"
    ).fetchone()
    
    if not table_exists:
        print("system_metrics表不存在，请先运行schema.sql创建表")
        return
    
    # 清空原有数据
    db.execute("DELETE FROM system_metrics")
    
    # 生成过去days天的指标数据，每天24条数据（每小时一条）
    for day in range(days):
        date = datetime.now() - timedelta(days=days-day)
        
        for hour in range(24):
            timestamp = date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
            
            # 生成随机的但有趋势的数据
            cpu_usage = random.uniform(10, 80) + day * 0.1  # 轻微增长趋势
            memory_usage = random.uniform(20, 70) + day * 0.05
            disk_usage = 30 + day * 0.02  # 磁盘使用率缓慢增长
            process_cpu = random.uniform(1, 30)
            process_memory = random.uniform(50, 200)
            
            # 数据库统计信息也有增长趋势
            db_tables = 4 + (day // 10)  # 每10天增加一个表
            users_count = 10 + day
            prompts_count = 20 + day * 3
            results_count = 50 + day * 7
            
            # 写入数据库
            db.execute(
                '''
                INSERT INTO system_metrics 
                (cpu_usage, memory_usage, disk_usage, process_cpu, process_memory, 
                database_tables, users_count, prompts_count, results_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (cpu_usage, memory_usage, disk_usage, process_cpu, process_memory,
                db_tables, users_count, prompts_count, results_count, timestamp)
            )
    
    # 提交事务
    db.commit()
    print(f"成功插入 {days * 24} 条系统指标数据")

def get_db(app):
    """获取数据库连接"""
    return sqlite3.connect(
        app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
    )

def main():
    """主函数"""
    try:
        # 创建应用
        app = create_app()
        
        # 获取数据库连接
        with app.app_context():
            db = get_db(app)
            db.row_factory = sqlite3.Row
            
            # 初始化系统指标数据
            init_system_metrics(db)
            
            # 关闭数据库连接
            db.close()
            
        print("数据中心测试数据初始化完成！")
            
    except Exception as e:
        print(f"初始化数据时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
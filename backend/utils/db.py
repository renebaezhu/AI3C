import sqlite3
import os
from sqlite3 import Error

def get_db_connection():
    """
    创建与SQLite数据库的连接
    
    Returns:
        conn: 数据库连接对象
    """
    try:
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        # 根据环境变量决定使用哪个数据库
        db_path = 'data/test.db' if os.environ.get('FLASK_ENV') == 'testing' else 'data/prompt_manager.db'
        
        # 创建连接
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        
        return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        raise

def init_db():
    """
    初始化数据库架构
    """
    conn = get_db_connection()
    
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        print("数据库初始化完成")
    except Error as e:
        print(f"数据库初始化错误: {e}")
        raise
    finally:
        conn.close() 
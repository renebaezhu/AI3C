import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..utils.db import get_db_connection

class User:
    def __init__(self, id=None, username=None, password_hash=None, email=None, created_at=None, last_login=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.created_at = created_at
        self.last_login = last_login
    
    @staticmethod
    def create(username, password, email):
        """
        创建新用户
        
        Args:
            username (str): 用户名
            password (str): 密码
            email (str): 电子邮件
            
        Returns:
            User: 创建的用户对象
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            raise ValueError("邮箱已被注册")
        
        # 生成密码哈希
        password_hash = generate_password_hash(password)
        
        # 插入用户记录
        cursor.execute(
            'INSERT INTO users (username, password_hash, email, created_at) VALUES (?, ?, ?, ?)',
            (username, password_hash, email, datetime.now())
        )
        
        # 获取新用户ID
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 返回新创建的用户对象
        return User.get_by_id(user_id)
    
    @staticmethod
    def get_by_id(user_id):
        """
        通过ID获取用户
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            User: 用户对象，如果不存在则为None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            email=row['email'],
            created_at=row['created_at'],
            last_login=row['last_login']
        )
    
    @staticmethod
    def get_by_username(username):
        """
        通过用户名获取用户
        
        Args:
            username (str): 用户名
            
        Returns:
            User: 用户对象，如果不存在则为None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            email=row['email'],
            created_at=row['created_at'],
            last_login=row['last_login']
        )
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        验证密码
        
        Args:
            password (str): 明文密码
            password_hash (str): 密码哈希
            
        Returns:
            bool: 如果密码匹配则为True，否则为False
        """
        return check_password_hash(password_hash, password)
    
    def update_last_login(self):
        """
        更新用户最后登录时间
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_time = datetime.now()
        cursor.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (current_time, self.id)
        )
        
        conn.commit()
        conn.close()
        
        self.last_login = current_time 
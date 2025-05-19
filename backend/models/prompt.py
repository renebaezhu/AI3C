import sqlite3
import json
from datetime import datetime
from ..utils.db import get_db_connection

class Prompt:
    def __init__(self, id=None, title=None, content=None, category=None, tags=None, user_id=None, created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.tags = tags if tags else []
        self.user_id = user_id
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
    
    @staticmethod
    def create(title, content, category, tags, user_id):
        """
        创建新的Prompt
        
        Args:
            title (str): Prompt标题
            content (str): Prompt内容
            category (str): 分类
            tags (list): 标签列表
            user_id (int): 用户ID
            
        Returns:
            Prompt: 新创建的Prompt对象
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'INSERT INTO prompts (title, content, category, tags, user_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, content, category, json.dumps(tags), user_id, now, now)
        )
        
        prompt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return Prompt.get_by_id(prompt_id)
    
    @staticmethod
    def get_by_id(prompt_id):
        """
        通过ID获取Prompt
        
        Args:
            prompt_id (int): Prompt ID
            
        Returns:
            Prompt: Prompt对象，如果不存在则为None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Prompt(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            category=row['category'],
            tags=json.loads(row['tags']),
            user_id=row['user_id'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    @staticmethod
    def get_all_by_user(user_id, category=None):
        """
        获取用户的所有Prompts
        
        Args:
            user_id (int): 用户ID
            category (str, optional): 按分类筛选
            
        Returns:
            list: Prompt对象列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM prompts WHERE user_id = ? AND category = ? ORDER BY updated_at DESC', (user_id, category))
        else:
            cursor.execute('SELECT * FROM prompts WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        prompts = []
        for row in rows:
            prompts.append(Prompt(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                category=row['category'],
                tags=json.loads(row['tags']),
                user_id=row['user_id'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            ))
        
        return prompts
    
    @staticmethod
    def update(prompt_id, title, content, category, tags):
        """
        更新Prompt
        
        Args:
            prompt_id (int): Prompt ID
            title (str): 新标题
            content (str): 新内容
            category (str): 新分类
            tags (list): 新标签列表
            
        Returns:
            Prompt: 更新后的Prompt对象
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            'UPDATE prompts SET title = ?, content = ?, category = ?, tags = ?, updated_at = ? WHERE id = ?',
            (title, content, category, json.dumps(tags), now, prompt_id)
        )
        
        conn.commit()
        conn.close()
        
        return Prompt.get_by_id(prompt_id)
    
    @staticmethod
    def delete(prompt_id):
        """
        删除Prompt
        
        Args:
            prompt_id (int): Prompt ID
            
        Returns:
            bool: 成功删除返回True
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除prompt相关的处理结果数据
        cursor.execute('DELETE FROM prompt_results WHERE prompt_id = ?', (prompt_id,))
        
        # 删除prompt本身
        cursor.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    @staticmethod
    def get_category_distribution(user_id=None):
        """
        获取Prompt分类分布
        
        Args:
            user_id (int, optional): 用户ID，为None时获取所有用户的分布
            
        Returns:
            dict: 分类名称到数量的映射
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT category, COUNT(*) as count FROM prompts WHERE user_id = ? GROUP BY category', (user_id,))
        else:
            cursor.execute('SELECT category, COUNT(*) as count FROM prompts GROUP BY category')
        
        rows = cursor.fetchall()
        conn.close()
        
        distribution = {}
        for row in rows:
            distribution[row['category']] = row['count']
        
        return distribution 
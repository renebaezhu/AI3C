import sqlite3
import json
from datetime import datetime
from ..utils.db import get_db_connection

class PromptResult:
    def __init__(self, id=None, prompt_id=None, input_data=None, output_data=None, 
                 execution_time=None, success=None, error_message=None, created_at=None):
        self.id = id
        self.prompt_id = prompt_id
        self.input_data = input_data
        self.output_data = output_data
        self.execution_time = execution_time
        self.success = success
        self.error_message = error_message
        self.created_at = created_at

    @staticmethod
    def create(prompt_id, input_data, output_data, execution_time, success, error_message=None):
        """
        创建新的Prompt处理结果
        
        Args:
            prompt_id (int): Prompt ID
            input_data (str): 输入数据
            output_data (str): 输出数据
            execution_time (float): 执行时间（毫秒）
            success (bool): 处理是否成功
            error_message (str, optional): 错误信息
            
        Returns:
            PromptResult: 创建的结果对象
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO prompt_results (prompt_id, input_data, output_data, execution_time, success, error_message) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (prompt_id, input_data, output_data, execution_time, success, error_message)
        )
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return PromptResult.get_by_id(result_id)
    
    @staticmethod
    def get_by_id(result_id):
        """
        通过ID获取结果
        
        Args:
            result_id (int): 结果ID
            
        Returns:
            PromptResult: 结果对象，如果不存在则为None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM prompt_results WHERE id = ?', (result_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return PromptResult(
            id=row['id'],
            prompt_id=row['prompt_id'],
            input_data=row['input_data'],
            output_data=row['output_data'],
            execution_time=row['execution_time'],
            success=row['success'],
            error_message=row['error_message'],
            created_at=row['created_at']
        )
    
    @staticmethod
    def get_by_prompt_id(prompt_id, limit=20, offset=0):
        """
        获取指定Prompt的所有处理结果
        
        Args:
            prompt_id (int): Prompt ID
            limit (int): 结果数量限制
            offset (int): 结果偏移量
            
        Returns:
            list: PromptResult对象列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM prompt_results WHERE prompt_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (prompt_id, limit, offset)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append(PromptResult(
                id=row['id'],
                prompt_id=row['prompt_id'],
                input_data=row['input_data'],
                output_data=row['output_data'],
                execution_time=row['execution_time'],
                success=row['success'],
                error_message=row['error_message'],
                created_at=row['created_at']
            ))
        
        return results
    
    @staticmethod
    def get_stats_by_user(user_id):
        """
        获取用户的Prompt使用统计
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            list: 统计数据列表，每个元素包含prompt名称和成功率
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 联表查询获取每个prompt的成功率
        cursor.execute('''
            SELECT 
                p.id, 
                p.title as name, 
                COUNT(r.id) as total_runs,
                SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) as successful_runs,
                (SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.id)) as success_rate
            FROM 
                prompts p
            LEFT JOIN 
                prompt_results r ON p.id = r.prompt_id
            WHERE 
                p.user_id = ?
            GROUP BY 
                p.id, p.title
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in rows:
            stats.append({
                'id': row['id'],
                'name': row['name'],
                'total_runs': row['total_runs'],
                'successful_runs': row['successful_runs'],
                'success_rate': round(row['success_rate'], 2) if row['success_rate'] is not None else 0
            })
        
        return stats
    
    @staticmethod
    def get_performance_data(prompt_id):
        """
        获取指定Prompt的性能数据
        
        Args:
            prompt_id (int): Prompt ID
            
        Returns:
            dict: 性能数据字典
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取执行时间统计
        cursor.execute('''
            SELECT 
                AVG(execution_time) as avg_time,
                MIN(execution_time) as min_time,
                MAX(execution_time) as max_time,
                COUNT(*) as total_runs,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_runs
            FROM 
                prompt_results
            WHERE 
                prompt_id = ?
        ''', (prompt_id,))
        
        stats_row = cursor.fetchone()
        conn.close()
        
        if not stats_row or stats_row['total_runs'] == 0:
            return {
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'total_runs': 0,
                'successful_runs': 0,
                'success_rate': 0
            }
        
        success_rate = (stats_row['successful_runs'] * 100.0 / stats_row['total_runs']) if stats_row['total_runs'] > 0 else 0
        
        return {
            'avg_time': round(stats_row['avg_time'], 2) if stats_row['avg_time'] else 0,
            'min_time': stats_row['min_time'],
            'max_time': stats_row['max_time'],
            'total_runs': stats_row['total_runs'],
            'successful_runs': stats_row['successful_runs'],
            'success_rate': round(success_rate, 2)
        }
    
    @staticmethod
    def get_time_series_data(prompt_id, start_date=None, end_date=None):
        """
        获取指定Prompt的时间序列数据
        
        Args:
            prompt_id (int): Prompt ID
            start_date (str, optional): 开始日期，格式为YYYY-MM-DD
            end_date (str, optional): 结束日期，格式为YYYY-MM-DD
            
        Returns:
            list: 时间序列数据列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                date(created_at) as date,
                COUNT(*) as runs,
                AVG(execution_time) as avg_execution_time
            FROM 
                prompt_results
            WHERE 
                prompt_id = ?
        '''
        
        params = [prompt_id]
        
        if start_date:
            query += ' AND created_at >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND created_at <= ?'
            params.append(end_date)
        
        query += ' GROUP BY date(created_at) ORDER BY date(created_at)'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        time_series = []
        for row in rows:
            time_series.append({
                'date': row['date'],
                'runs': row['runs'],
                'avg_execution_time': round(row['avg_execution_time'], 2) if row['avg_execution_time'] else 0
            })
        
        return time_series 
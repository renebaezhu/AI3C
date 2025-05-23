from flask import current_app, g
import sqlite3
import json
from datetime import datetime, timedelta
import time

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def get_system_overview():
    """获取系统总览数据"""
    db = get_db()
    
    # 获取用户总数
    user_count = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    
    # 获取提示词总数
    prompt_count = db.execute('SELECT COUNT(*) as count FROM prompts').fetchone()['count']
    
    # 获取提示词使用总次数
    usage_count = db.execute('SELECT COUNT(*) as count FROM prompt_results').fetchone()['count']
    
    # 获取成功率
    success_stats = db.execute(
        'SELECT COUNT(*) as total, SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count '
        'FROM prompt_results'
    ).fetchone()
    
    success_rate = 0
    if success_stats['total'] > 0:
        success_rate = (success_stats['success_count'] / success_stats['total']) * 100
    
    # 获取最近7天的活跃用户数
    seven_days_ago = datetime.now() - timedelta(days=7)
    active_users = db.execute(
        'SELECT COUNT(DISTINCT user_id) as count FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        'WHERE pr.created_at >= ?',
        (seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),)
    ).fetchone()['count']
    
    return {
        'user_count': user_count,
        'prompt_count': prompt_count,
        'usage_count': usage_count,
        'success_rate': round(success_rate, 2),
        'active_users': active_users,
    }

def get_prompt_usage_stats(days=30, user_id=None):
    """获取Prompt使用统计数据"""
    db = get_db()
    
    # 计算开始日期
    start_date = datetime.now() - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # 构建查询条件
    query_params = [start_date_str]
    user_condition = ''
    if user_id:
        user_condition = 'AND p.user_id = ?'
        query_params.append(user_id)
    
    # 按天统计使用量
    daily_usage = db.execute(
        'SELECT date(pr.created_at) as date, COUNT(*) as count '
        'FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        f'WHERE pr.created_at >= ? {user_condition} '
        'GROUP BY date(pr.created_at) '
        'ORDER BY date',
        query_params
    ).fetchall()
    
    # 按类别统计使用量
    category_usage = db.execute(
        'SELECT p.category, COUNT(*) as count '
        'FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        f'WHERE pr.created_at >= ? {user_condition} '
        'GROUP BY p.category '
        'ORDER BY count DESC',
        query_params
    ).fetchall()
    
    # 按成功/失败统计
    success_stats = db.execute(
        'SELECT pr.success, COUNT(*) as count '
        'FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        f'WHERE pr.created_at >= ? {user_condition} '
        'GROUP BY pr.success',
        query_params
    ).fetchall()
    
    return {
        'daily_usage': [dict(row) for row in daily_usage],
        'category_usage': [dict(row) for row in category_usage],
        'success_stats': [dict(row) for row in success_stats]
    }

def get_user_activity(days=30):
    """获取用户活动数据"""
    db = get_db()
    
    # 计算开始日期
    start_date = datetime.now() - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # 获取每日活跃用户数
    daily_active_users = db.execute(
        'SELECT date(pr.created_at) as date, COUNT(DISTINCT p.user_id) as user_count '
        'FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        'WHERE pr.created_at >= ? '
        'GROUP BY date(pr.created_at) '
        'ORDER BY date',
        (start_date_str,)
    ).fetchall()
    
    # 获取最活跃的用户（按使用量）
    top_users = db.execute(
        'SELECT u.username, COUNT(*) as usage_count '
        'FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        'JOIN users u ON p.user_id = u.id '
        'WHERE pr.created_at >= ? '
        'GROUP BY p.user_id '
        'ORDER BY usage_count DESC '
        'LIMIT 10',
        (start_date_str,)
    ).fetchall()
    
    # 获取新增用户数据
    new_users = db.execute(
        'SELECT date(created_at) as date, COUNT(*) as count '
        'FROM users '
        'WHERE created_at >= ? '
        'GROUP BY date(created_at) '
        'ORDER BY date',
        (start_date_str,)
    ).fetchall()
    
    return {
        'daily_active_users': [dict(row) for row in daily_active_users],
        'top_users': [dict(row) for row in top_users],
        'new_users': [dict(row) for row in new_users]
    }

def get_performance_metrics(days=30):
    """获取性能指标数据"""
    db = get_db()
    
    # 计算开始日期
    start_date = datetime.now() - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # 获取每日平均执行时间
    daily_avg_time = db.execute(
        'SELECT date(created_at) as date, AVG(execution_time) as avg_time '
        'FROM prompt_results '
        'WHERE created_at >= ? '
        'GROUP BY date(created_at) '
        'ORDER BY date',
        (start_date_str,)
    ).fetchall()
    
    # 获取按提示词类别的平均执行时间
    category_avg_time = db.execute(
        'SELECT p.category, AVG(pr.execution_time) as avg_time '
        'FROM prompt_results pr '
        'JOIN prompts p ON pr.prompt_id = p.id '
        'WHERE pr.created_at >= ? '
        'GROUP BY p.category '
        'ORDER BY avg_time DESC',
        (start_date_str,)
    ).fetchall()
    
    # 获取成功率随时间的变化
    daily_success_rate = db.execute(
        'SELECT date(created_at) as date, '
        'AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END) as success_rate '
        'FROM prompt_results '
        'WHERE created_at >= ? '
        'GROUP BY date(created_at) '
        'ORDER BY date',
        (start_date_str,)
    ).fetchall()
    
    return {
        'daily_avg_time': [dict(row) for row in daily_avg_time],
        'category_avg_time': [dict(row) for row in category_avg_time],
        'daily_success_rate': [dict(row) for row in daily_success_rate]
    }

def get_data_distribution(category='prompt_categories'):
    """获取数据分布统计"""
    db = get_db()
    
    result = {}
    
    if category == 'prompt_categories':
        # 提示词类别分布
        data = db.execute(
            'SELECT category, COUNT(*) as count '
            'FROM prompts '
            'GROUP BY category '
            'ORDER BY count DESC'
        ).fetchall()
        result['prompt_categories'] = [dict(row) for row in data]
        
    elif category == 'tags':
        # 标签使用分布
        prompts = db.execute('SELECT tags FROM prompts').fetchall()
        tag_counts = {}
        
        for prompt in prompts:
            tags = json.loads(prompt['tags'])
            for tag in tags:
                if tag in tag_counts:
                    tag_counts[tag] += 1
                else:
                    tag_counts[tag] = 1
                    
        # 将标签计数转换为列表，并按数量排序
        tags_list = [{'tag': tag, 'count': count} for tag, count in tag_counts.items()]
        tags_list.sort(key=lambda x: x['count'], reverse=True)
        
        result['tags'] = tags_list
        
    elif category == 'prompt_length':
        # 提示词长度分布
        ranges = [
            (0, 100),
            (101, 500),
            (501, 1000),
            (1001, 2000),
            (2001, 5000),
            (5001, float('inf'))
        ]
        
        length_distribution = []
        
        for i, (min_len, max_len) in enumerate(ranges):
            label = f"{min_len}-{max_len}" if max_len != float('inf') else f"{min_len}+"
            
            if max_len == float('inf'):
                count = db.execute(
                    'SELECT COUNT(*) as count FROM prompts WHERE LENGTH(content) >= ?',
                    (min_len,)
                ).fetchone()['count']
            else:
                count = db.execute(
                    'SELECT COUNT(*) as count FROM prompts WHERE LENGTH(content) >= ? AND LENGTH(content) <= ?',
                    (min_len, max_len)
                ).fetchone()['count']
                
            length_distribution.append({
                'range': label,
                'count': count
            })
            
        result['prompt_length'] = length_distribution
        
    return result 
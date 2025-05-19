from functools import wraps
from flask import request, jsonify
import json
import time
import os

# 简单的内存缓存实现
cache = {}

def cache_data(timeout=300):
    """
    缓存装饰器，用于缓存API响应数据
    
    Args:
        timeout (int): 缓存超时时间，单位为秒，默认300秒(5分钟)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键（基于URL和查询参数）
            cache_key = f"{request.path}_{hash(frozenset(request.args.items()))}"
            
            # 检查缓存是否存在且未过期
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data
            
            # 执行原始函数
            result = f(*args, **kwargs)
            
            # 如果结果是JSON响应，则缓存它
            if isinstance(result, tuple) and len(result) == 2:
                response, status_code = result
                if status_code == 200:
                    cache[cache_key] = (result, time.time())
            else:
                cache[cache_key] = (result, time.time())
            
            return result
        return decorated_function
    return decorator

def clear_cache():
    """清除所有缓存"""
    global cache
    cache = {}

def clear_cache_by_prefix(prefix):
    """
    清除指定前缀的缓存
    
    Args:
        prefix (str): 缓存键前缀
    """
    global cache
    keys_to_delete = [key for key in cache.keys() if key.startswith(prefix)]
    for key in keys_to_delete:
        del cache[key] 
from flask import Blueprint, jsonify, request, g
from ..services.cache_service import cache_data
from ..models.prompt import Prompt
from ..models.data import PromptResult
from ..utils.auth import login_required
import json

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/api/visualization/prompt-stats', methods=['GET'])
@login_required
@cache_data(timeout=300)  # 缓存5分钟
def get_prompt_stats():
    """获取Prompt使用统计数据"""
    # 使用当前登录用户的ID
    user_id = g.user.id
    
    stats = PromptResult.get_stats_by_user(user_id)
    
    return jsonify({
        'success': True,
        'data': stats
    })

@visualization_bp.route('/api/visualization/prompt-performance', methods=['GET'])
@login_required
@cache_data(timeout=300)  # 缓存5分钟
def get_prompt_performance():
    """获取Prompt性能数据"""
    prompt_id = request.args.get('prompt_id')
    
    if not prompt_id:
        return jsonify({
            'success': False,
            'message': 'prompt_id参数缺失'
        }), 400
    
    # 检查prompt是否属于当前用户
    prompt = Prompt.get_by_id(int(prompt_id))
    if not prompt or prompt.user_id != g.user.id:
        return jsonify({
            'success': False,
            'message': '无权访问此Prompt数据'
        }), 403
    
    performance_data = PromptResult.get_performance_data(int(prompt_id))
    
    return jsonify({
        'success': True,
        'data': performance_data
    })

@visualization_bp.route('/api/visualization/category-distribution', methods=['GET'])
@login_required
@cache_data(timeout=600)  # 缓存10分钟
def get_category_distribution():
    """获取Prompt分类分布数据"""
    # 使用当前登录用户的ID
    user_id = g.user.id
    
    distribution = Prompt.get_category_distribution(user_id)
    
    # 格式化为ECharts饼图数据格式
    pie_data = [
        {'name': category, 'value': count}
        for category, count in distribution.items()
    ]
    
    return jsonify({
        'success': True,
        'data': pie_data
    })

@visualization_bp.route('/api/visualization/time-series', methods=['GET'])
@login_required
def get_time_series_data():
    """获取时间序列数据"""
    prompt_id = request.args.get('prompt_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not prompt_id:
        return jsonify({
            'success': False,
            'message': 'prompt_id参数缺失'
        }), 400
    
    # 检查prompt是否属于当前用户
    prompt = Prompt.get_by_id(int(prompt_id))
    if not prompt or prompt.user_id != g.user.id:
        return jsonify({
            'success': False,
            'message': '无权访问此Prompt数据'
        }), 403
    
    time_series = PromptResult.get_time_series_data(int(prompt_id), start_date, end_date)
    
    return jsonify({
        'success': True,
        'data': time_series
    }) 
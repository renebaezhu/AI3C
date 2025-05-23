from flask import Blueprint, request, jsonify, g, current_app
import sqlite3
from ..utils.auth import login_required
from ..models.dashboard_model import (
    get_system_overview, 
    get_prompt_usage_stats, 
    get_user_activity, 
    get_performance_metrics,
    get_data_distribution
)

# 创建数据中心蓝图
data_center_bp = Blueprint('data_center', __name__, url_prefix='/api/data-center')

@data_center_bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    """获取系统总览数据"""
    try:
        overview_data = get_system_overview()
        return jsonify({
            'status': 'success',
            'data': overview_data
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取系统总览数据失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取系统总览数据失败: {str(e)}"
        }), 500

@data_center_bp.route('/prompt-usage', methods=['GET'])
@login_required
def get_prompt_usage():
    """获取Prompt使用统计数据"""
    try:
        days = request.args.get('days', default=30, type=int)
        user_id = g.user['id'] if not request.args.get('all_users') else None
        
        usage_data = get_prompt_usage_stats(days, user_id)
        return jsonify({
            'status': 'success',
            'data': usage_data
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取Prompt使用统计失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取Prompt使用统计失败: {str(e)}"
        }), 500

@data_center_bp.route('/user-activity', methods=['GET'])
@login_required
def get_activity():
    """获取用户活动数据"""
    try:
        days = request.args.get('days', default=30, type=int)
        activity_data = get_user_activity(days)
        return jsonify({
            'status': 'success',
            'data': activity_data
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户活动数据失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取用户活动数据失败: {str(e)}"
        }), 500

@data_center_bp.route('/performance', methods=['GET'])
@login_required
def get_performance():
    """获取系统性能指标数据"""
    try:
        days = request.args.get('days', default=30, type=int)
        metrics = get_performance_metrics(days)
        return jsonify({
            'status': 'success',
            'data': metrics
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取性能指标失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取性能指标失败: {str(e)}"
        }), 500

@data_center_bp.route('/distribution', methods=['GET'])
@login_required
def get_distribution():
    """获取数据分布统计"""
    try:
        category = request.args.get('category', default='prompt_categories', type=str)
        distribution_data = get_data_distribution(category)
        return jsonify({
            'status': 'success',
            'data': distribution_data
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取数据分布统计失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"获取数据分布统计失败: {str(e)}"
        }), 500 
from flask import Blueprint, request, jsonify, g
from ..models.prompt import Prompt
from ..services.cache_service import cache_data, clear_cache_by_prefix
from ..utils.auth import login_required

prompt_bp = Blueprint('prompt', __name__)

@prompt_bp.route('/api/prompts', methods=['GET'])
@login_required
def get_prompts():
    """获取当前用户的所有Prompts"""
    category = request.args.get('category')
    
    prompts = Prompt.get_all_by_user(g.user.id, category)
    
    # 转换为JSON响应
    prompts_json = []
    for prompt in prompts:
        prompts_json.append({
            'id': prompt.id,
            'title': prompt.title,
            'content': prompt.content,
            'category': prompt.category,
            'tags': prompt.tags,
            'created_at': prompt.created_at,
            'updated_at': prompt.updated_at
        })
    
    return jsonify({
        'success': True,
        'data': prompts_json
    })

@prompt_bp.route('/api/prompts/<int:prompt_id>', methods=['GET'])
@login_required
@cache_data(timeout=60)  # 缓存1分钟
def get_prompt(prompt_id):
    """获取指定ID的Prompt"""
    prompt = Prompt.get_by_id(prompt_id)
    
    if not prompt:
        return jsonify({
            'success': False,
            'message': '未找到指定的Prompt'
        }), 404
    
    # 检查是否为当前用户的Prompt
    if prompt.user_id != g.user.id:
        return jsonify({
            'success': False,
            'message': '无权访问此Prompt'
        }), 403
    
    return jsonify({
        'success': True,
        'data': {
            'id': prompt.id,
            'title': prompt.title,
            'content': prompt.content,
            'category': prompt.category,
            'tags': prompt.tags,
            'created_at': prompt.created_at,
            'updated_at': prompt.updated_at
        }
    })

@prompt_bp.route('/api/prompts', methods=['POST'])
@login_required
def create_prompt():
    """创建新的Prompt"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['title', 'content', 'category']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'message': f'缺少必要字段: {field}'
            }), 400
    
    # 获取字段值，确保tags是列表
    title = data['title']
    content = data['content']
    category = data['category']
    tags = data.get('tags', [])
    
    if not isinstance(tags, list):
        return jsonify({
            'success': False,
            'message': 'tags字段必须是列表'
        }), 400
    
    # 创建新的Prompt
    try:
        prompt = Prompt.create(title, content, category, tags, g.user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': prompt.id,
                'title': prompt.title,
                'content': prompt.content,
                'category': prompt.category,
                'tags': prompt.tags,
                'created_at': prompt.created_at,
                'updated_at': prompt.updated_at
            }
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建Prompt失败: {str(e)}'
        }), 500

@prompt_bp.route('/api/prompts/<int:prompt_id>', methods=['PUT'])
@login_required
def update_prompt(prompt_id):
    """更新指定ID的Prompt"""
    prompt = Prompt.get_by_id(prompt_id)
    
    if not prompt:
        return jsonify({
            'success': False,
            'message': '未找到指定的Prompt'
        }), 404
    
    # 检查是否为当前用户的Prompt
    if prompt.user_id != g.user.id:
        return jsonify({
            'success': False,
            'message': '无权修改此Prompt'
        }), 403
    
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['title', 'content', 'category']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'message': f'缺少必要字段: {field}'
            }), 400
    
    # 获取字段值，确保tags是列表
    title = data['title']
    content = data['content']
    category = data['category']
    tags = data.get('tags', [])
    
    if not isinstance(tags, list):
        return jsonify({
            'success': False,
            'message': 'tags字段必须是列表'
        }), 400
    
    # 更新Prompt
    try:
        prompt = Prompt.update(prompt_id, title, content, category, tags)
        
        # 清除相关缓存
        clear_cache_by_prefix(f'/api/prompts/{prompt_id}')
        
        return jsonify({
            'success': True,
            'data': {
                'id': prompt.id,
                'title': prompt.title,
                'content': prompt.content,
                'category': prompt.category,
                'tags': prompt.tags,
                'created_at': prompt.created_at,
                'updated_at': prompt.updated_at
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新Prompt失败: {str(e)}'
        }), 500

@prompt_bp.route('/api/prompts/<int:prompt_id>', methods=['DELETE'])
@login_required
def delete_prompt(prompt_id):
    """删除指定ID的Prompt"""
    prompt = Prompt.get_by_id(prompt_id)
    
    if not prompt:
        return jsonify({
            'success': False,
            'message': '未找到指定的Prompt'
        }), 404
    
    # 检查是否为当前用户的Prompt
    if prompt.user_id != g.user.id:
        return jsonify({
            'success': False,
            'message': '无权删除此Prompt'
        }), 403
    
    # 删除Prompt
    try:
        success = Prompt.delete(prompt_id)
        
        # 清除相关缓存
        clear_cache_by_prefix(f'/api/prompts/{prompt_id}')
        clear_cache_by_prefix('/api/prompts')
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Prompt删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '删除Prompt失败'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除Prompt失败: {str(e)}'
        }), 500 
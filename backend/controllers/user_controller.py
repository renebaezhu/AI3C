from flask import Blueprint, request, jsonify
from ..models.user import User
from ..utils.auth import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """新用户注册"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['username', 'password', 'email']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'message': f'缺少必要字段: {field}'
            }), 400
    
    username = data['username']
    password = data['password']
    email = data['email']
    
    # 验证密码长度
    if len(password) < 6:
        return jsonify({
            'success': False,
            'message': '密码必须至少6个字符'
        }), 400
    
    # 创建新用户
    try:
        user = User.create(username, password, email)
        
        # 生成JWT令牌
        token = generate_token(user.id)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'token': token
            }
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'message': f'缺少必要字段: {field}'
            }), 400
    
    username = data['username']
    password = data['password']
    
    # 获取用户
    user = User.get_by_username(username)
    if not user:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401
    
    # 验证密码
    if not User.verify_password(password, user.password_hash):
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401
    
    # 更新最后登录时间
    user.update_last_login()
    
    # 生成JWT令牌
    token = generate_token(user.id)
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token
        }
    }) 
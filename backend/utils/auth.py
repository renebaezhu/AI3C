from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from datetime import datetime, timedelta
from ..models.user import User

def generate_token(user_id):
    """
    为用户生成JWT令牌
    
    Args:
        user_id (int): 用户ID
        
    Returns:
        str: 生成的JWT令牌
    """
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=1)  # 令牌有效期1天
    }
    
    # 使用SECRET_KEY签名令牌
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return token

def decode_token(token):
    """
    解码JWT令牌
    
    Args:
        token (str): JWT令牌
        
    Returns:
        dict: 解码后的令牌有效载荷
        None: 如果令牌无效或已过期
    """
    try:
        # 解码令牌
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # 令牌已过期
        return None
    except jwt.InvalidTokenError:
        # 无效令牌
        return None

def login_required(f):
    """
    验证用户是否已登录的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': '缺少Authorization头'
            }), 401
        
        # 检查令牌格式
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({
                'success': False,
                'message': 'Authorization头格式无效'
            }), 401
        
        token = parts[1]
        
        # 解码令牌
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': '无效或过期的令牌'
            }), 401
        
        # 获取用户
        user = User.get_by_id(payload['sub'])
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 401
        
        # 将用户对象存储在g中，以便视图函数使用
        g.user = user
        
        return f(*args, **kwargs)
    return decorated_function 
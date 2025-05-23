from flask import Flask
from flask_cors import CORS
import os
from .controllers.user_controller import auth_bp
from .controllers.prompt_controller import prompt_bp
from .controllers.visualization_controller import visualization_bp
from .controllers.data_center_controller import data_center_bp
from .utils.db import init_db
from .utils.scheduler import metrics_scheduler

def create_app(test_config=None):
    # 创建Flask应用
    app = Flask(__name__, instance_relative_config=True)
    
    # 配置应用
    app.config.from_mapping(
        SECRET_KEY='dev',  # 在生产环境中应该修改为随机值
        DATABASE=os.path.join(app.instance_path, 'prompt_manager.sqlite'),
    )
    
    if test_config is None:
        # 如果不是测试环境，加载实例配置
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载测试配置
        app.config.from_mapping(test_config)
    
    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 初始化数据库
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            app.logger.error(f"数据库初始化错误: {e}")
    
    # 初始化指标收集调度器
    metrics_scheduler.init_app(app)
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(prompt_bp)
    app.register_blueprint(visualization_bp)
    app.register_blueprint(data_center_bp)
    
    # 根路由
    @app.route('/')
    def index():
        return {
            'status': 'success',
            'message': 'Prompt管理系统API服务运行正常'
        }
    
    return app

# 如果直接运行此文件
if __name__ == '__main__':
    app = create_app()
    # 在树莓派上，绑定到所有网络接口
    app.run(host='0.0.0.0', port=5000, debug=True) 
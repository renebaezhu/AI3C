# Prompt管理与可视化共享平台

基于树莓派3B+硬件开发的Prompt管理与可视化共享平台，旨在提供高效的Prompt管理与展示服务。

## 功能特点

- **Prompt管理**：创建、编辑、删除和分类管理Prompts
- **数据可视化**：直观展示Prompt使用情况和性能数据
- **多用户支持**：支持多用户使用，每个用户管理自己的Prompts
- **性能优化**：使用缓存提高API响应速度
- **安全认证**：JWT令牌实现安全的用户认证

## 系统架构

- **前端**：Vue.js + ECharts图表库
- **后端**：Flask RESTful API
- **数据库**：SQLite
- **部署环境**：树莓派3B+

## 安装与部署

### 环境要求

- Python 3.7+
- Node.js 14+
- 树莓派3B+或树莓派4

### 后端安装

1. 克隆本仓库到树莓派
   ```
   git clone https://github.com/your-username/prompt-manager.git
   cd prompt-manager
   ```

2. 创建虚拟环境并安装依赖
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. 初始化数据库
   ```
   python -c "from backend.utils.db import init_db; init_db()"
   ```

4. 启动后端服务
   ```
   python run.py
   ```

### 前端安装

1. 进入前端目录
   ```
   cd frontend
   ```

2. 安装依赖
   ```
   npm install
   ```

3. 开发模式启动
   ```
   npm run serve
   ```

4. 构建生产版本
   ```
   npm run build
   ```

## API文档

### 用户认证

- `POST /api/auth/register` - 注册新用户
- `POST /api/auth/login` - 用户登录

### Prompt管理

- `GET /api/prompts` - 获取用户的所有Prompts
- `GET /api/prompts/:id` - 获取指定ID的Prompt
- `POST /api/prompts` - 创建新Prompt
- `PUT /api/prompts/:id` - 更新指定ID的Prompt
- `DELETE /api/prompts/:id` - 删除指定ID的Prompt

### 数据可视化

- `GET /api/visualization/prompt-stats` - 获取Prompt使用统计
- `GET /api/visualization/prompt-performance` - 获取Prompt性能数据
- `GET /api/visualization/category-distribution` - 获取分类分布
- `GET /api/visualization/time-series` - 获取时间序列数据

## 项目结构

```
prompt-manager/
│
├── backend/                # 后端Flask应用
│   ├── models/             # 数据模型
│   ├── controllers/        # API控制器
│   ├── services/           # 服务层
│   ├── utils/              # 工具函数
│   └── app.py              # Flask应用入口
│
├── frontend/               # 前端Vue应用
│   ├── src/
│   │   ├── components/     # UI组件
│   │   ├── views/          # 页面组件
│   │   ├── utils/          # 工具函数
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # Vue入口
│   └── public/             # 静态资源
│
├── data/                   # 数据库文件目录
├── schema.sql              # 数据库结构
├── requirements.txt        # Python依赖
├── run.py                  # 启动脚本
└── README.md               # 项目文档
```

## 许可证

MIT
 
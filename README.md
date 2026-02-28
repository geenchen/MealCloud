# 餐饮管理系统

餐饮管理系统是一个完整的解决方案，包含后台管理和微信点餐两个子系统。

## 项目结构

```
MealCloud/
├── Backend/
│   └── MealCloud_API/           # FastAPI后端服务
├── Frontend/
│   ├── AdminPanel/             # 后台管理前端 (Vue3 + Element Plus)
│   └── WechatOrder/            # 微信点餐前端 (Vue3 + Vant)
```

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite + JWT
- **后台管理前端**: Vue3 + Element Plus + Vite
- **微信点餐前端**: Vue3 + Vant + Vite

## 快速开始

### 后端服务

1. 进入后端目录：
   ```bash
   cd MealCloud\Backend\MealCloud_API
   ```

2. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```
   
   或者直接安装：
   ```bash
   pip install fastapi uvicorn sqlalchemy databases aiosqlite python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv redis pyjwt
   ```

3. 启动后端服务：
   ```bash
   uvicorn main:app --reload
   ```
   
   服务将在 `http://127.0.0.1:8000` 上运行

### 后台管理前端

1. 进入后台管理前端目录：
   ```bash
   cd MealCloud\Frontend\AdminPanel
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run dev
   ```
   
   前端将在 `http://localhost:3000` 上运行

### 微信点餐前端

1. 进入微信点餐前端目录：
   ```bash
   cd MealCloud\Frontend\WechatOrder
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run dev
   ```
   
   前端将在 `http://localhost:3001` 上运行

## 项目特性

### 后端特性
- 基于FastAPI的现代化API设计
- JWT身份认证
- 异步数据库操作
- 自动化API文档 (Swagger UI)
- 数据库ORM支持

### 后台管理前端特性
- 响应式布局设计
- 完整的菜品、订单、用户管理功能
- 实时数据统计面板
- Element Plus UI组件库

### 微信点餐前端特性
- 移动端优化界面
- 流畅的点餐体验
- 实时购物车管理
- Vant UI组件库

## API接口

启动后端服务后，可通过 `http://127.0.0.1:8000/docs` 访问API文档。

主要API端点：
- `/` - 主页
- `/api/v1/status` - API状态检查
- `/health` - 健康检查
- `/api/v1/token` - 用户认证
- `/api/v1/users/` - 用户管理
- `/api/v1/dishes/` - 菜品管理
- `/api/v1/orders/` - 订单管理
- `/api/v1/tables/` - 桌台管理

## 开发指南

### 添加新功能

#### 后端
1. 在 `models/` 目录下创建新的数据模型
2. 在 `schemas/` 目录下定义Pydantic数据验证模型
3. 在 `routers/` 目录下创建新的路由文件
4. 在 `main.py` 中导入并注册新路由

#### 前端
1. 在 `views/` 目录下创建新的页面组件
2. 在 `router/index.js` 中添加路由配置
3. 在 `App.vue` 中更新导航菜单

## 环境配置

### 后端环境变量

在后端目录下创建 `.env` 文件：

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite+aiosqlite:///./mealcloud.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 部署

### 生产部署建议

1. **后端部署**:
   - 使用 Nginx 作为反向代理
   - 使用 Uvicorn 生产服务器
   - 配置环境变量
   - 设置正确的安全头

2. **前端部署**:
   - 构建静态文件: `npm run build`
   - 将构建结果部署到 CDN 或 Web 服务器
   - 配置 API 代理

## 注意事项

1. 此项目目前使用SQLite作为开发数据库，生产环境建议切换到PostgreSQL或MySQL
2. JWT密钥应在生产环境中妥善保管
3. 前端API代理仅用于开发环境，生产环境需正确配置

## 维护

本项目结构清晰，便于后续功能扩展和维护。如需添加新功能模块，请遵循现有架构模式。
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import database, create_tables
from auth import get_current_active_user
from models.user import User
import uvicorn

# 创建应用实例
app = FastAPI(title="餐饮管理系统API", version="1.0.0")

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库事件处理器
@app.on_event("startup")
async def startup():
    await database.connect()
    create_tables()  # 创建数据库表

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# 导入并注册路由
from routers import auth, users, dishes, orders, tables, areas, categories

app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(users.router, prefix="/api/v1", tags=["用户"])
app.include_router(dishes.router, prefix="/api/v1", tags=["菜品"])
app.include_router(orders.router, prefix="/api/v1", tags=["订单"])
app.include_router(tables.router, prefix="/api/v1", tags=["桌台"])
app.include_router(areas.router, prefix="/api/v1", tags=["区域"])
app.include_router(categories.router, prefix="/api/v1", tags=["分类"])

# 根路径
@app.get("/")
async def read_root():
    return {"message": "餐饮管理系统API运行中"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "餐饮管理系统API服务正常运行"}

# 测试认证端点
@app.get("/api/v1/status")
async def read_status(current_user: User = Depends(get_current_active_user)):
    return {"status": "authenticated", "user": current_user.username}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8008, reload=True)
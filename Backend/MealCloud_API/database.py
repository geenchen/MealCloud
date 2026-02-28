from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import os
from config import settings

# 使用SQLAlchemy进行同步操作
engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    connect_args={"check_same_thread": False}  # 只适用于SQLite
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础类
Base = declarative_base()

# 创建所有表
def create_tables():
    # 导入所有模型以确保它们被注册到Base.metadata
    from models.user import User
    from models.dish import Dish, Category
    from models.order import Order, OrderItem, Table
    from models.area import Area
    Base.metadata.create_all(bind=engine)

# 使用databases库进行异步操作
database = Database(settings.DATABASE_URL)

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
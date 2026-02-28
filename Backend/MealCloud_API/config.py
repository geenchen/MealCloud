from pydantic_settings import BaseSettings
import os
from typing import Optional


class Settings(BaseSettings):
    # 应用程序基本信息
    APP_NAME: str = "餐饮管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mealcloud.db")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost")
    
    # 上传文件配置
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    class Config:
        env_file = ".env"


settings = Settings()
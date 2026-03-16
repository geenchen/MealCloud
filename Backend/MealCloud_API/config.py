from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = 'MealCloud'
    APP_VERSION: str = '1.0.0'
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'

    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./mealcloud.db')

    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost')

    UPLOAD_FOLDER: str = 'uploads'
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

    # Security
    BACKEND_CORS_ORIGINS: str = os.getenv(
        'BACKEND_CORS_ORIGINS',
        'http://localhost:3000,http://127.0.0.1:3000,http://localhost:3005,http://127.0.0.1:3005',
    )
    DEFAULT_ADMIN_PASSWORD: str = os.getenv('DEFAULT_ADMIN_PASSWORD', '')

    class Config:
        env_file = '.env'


settings = Settings()

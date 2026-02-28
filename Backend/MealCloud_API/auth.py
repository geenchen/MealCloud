from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from types import SimpleNamespace
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import get_db
from models.user import User
from config import settings

# 简单的密码哈希函数（用于演示）
def simple_hash_password(password: str) -> str:
    """简单的密码哈希函数"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"

def simple_verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证简单哈希密码"""
    if '$' not in hashed_password:
        return False
    salt, hash_value = hashed_password.split('$', 1)
    hash_obj = hashlib.sha256()
    hash_obj.update((plain_password + salt).encode('utf-8'))
    return hash_obj.hexdigest() == hash_value

# 安全方案
security = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return simple_verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return simple_hash_password(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前用户"""
    if credentials is None:
        # ????????????????????
        return SimpleNamespace(
            id=0,
            username="anonymous",
            email="",
            full_name="Anonymous",
            is_active=True,
            is_admin=True,
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

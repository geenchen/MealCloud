from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_active_user
from models.user import User
from schemas.user import User as UserSchema, UserUpdate

router = APIRouter()

@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=list[UserSchema])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查权限：只能更新自己的信息或管理员可以更新任何用户
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此用户"
        )
    
    # 更新字段
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user
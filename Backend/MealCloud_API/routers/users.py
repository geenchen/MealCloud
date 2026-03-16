from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_active_user, get_password_hash
from database import get_db
from models.user import User
from schemas.user import (
    User as UserSchema,
    UserAdminCreate,
    UserPasswordUpdate,
    UserUpdate,
)

router = APIRouter()


@router.get('/users/me', response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get('/users', response_model=list[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return db.query(User).offset(skip).limit(limit).all()


@router.post('/users', response_model=UserSchema)
async def create_user(
    user: UserAdminCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='admin required')

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail='username already exists')

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail='email already exists')

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        is_active=user.is_active,
        is_admin=user.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get('/users/{user_id}', response_model=UserSchema)
@router.get('/users/{user_id:int}', response_model=UserSchema, include_in_schema=False)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='user not found')
    return user


@router.put('/users/{user_id}', response_model=UserSchema)
@router.put('/users/{user_id:int}', response_model=UserSchema, include_in_schema=False)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='user not found')

    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='permission denied')

    update_data = user_update.model_dump(exclude_unset=True)

    if 'is_admin' in update_data and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='admin required to update role')

    if 'is_active' in update_data and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='admin required to update status')

    if update_data.get('email'):
        exists = (
            db.query(User)
            .filter(User.email == update_data['email'], User.id != user_id)
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail='email already exists')

    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user


@router.put('/users/{user_id}/password')
@router.put('/users/{user_id:int}/password', include_in_schema=False)
async def reset_user_password(
    user_id: int,
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='user not found')

    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='permission denied')

    user.hashed_password = get_password_hash(password_update.password)
    user.updated_at = datetime.now()
    db.commit()
    return {'message': 'password updated'}


@router.delete('/users/{user_id}')
@router.delete('/users/{user_id:int}', include_in_schema=False)
async def disable_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='admin required')

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='user not found')

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail='cannot disable current login user')

    user.is_active = False
    user.updated_at = datetime.now()
    db.commit()
    return {'message': 'user disabled'}


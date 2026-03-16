from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_active_user
from database import get_db
from models.dish import Category as CategoryModel
from models.dish import Dish as DishModel
from models.user import User
from schemas.dish import Category, CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get('/categories', response_model=list[Category])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(CategoryModel)
        .filter(CategoryModel.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get('/categories/page')
async def get_categories_page(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    base_query = db.query(CategoryModel).filter(CategoryModel.is_active == True)
    total = base_query.count()
    items = base_query.offset(skip).limit(limit).all()
    return {'items': items, 'total': total, 'skip': skip, 'limit': limit}


@router.get('/categories/stats')
async def get_category_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    active_categories = db.query(CategoryModel).filter(CategoryModel.is_active == True).all()

    category_stats = []
    for category in active_categories:
        dish_count = db.query(DishModel).filter(DishModel.category_id == category.id).count()
        category_stats.append(
            {
                'category_id': category.id,
                'category_name': category.name,
                'dish_count': dish_count,
            }
        )

    return {
        'total': len(active_categories),
        'active': len(active_categories),
        'category_details': category_stats,
    }


@router.get('/categories/{category_id:int}', response_model=Category)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if category is None or not category.is_active:
        raise HTTPException(status_code=404, detail='分类不存在')
    return category


@router.post('/categories', response_model=Category)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    existing_category = db.query(CategoryModel).filter(CategoryModel.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail='分类名称已存在')

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put('/categories/{category_id:int}', response_model=Category)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail='分类不存在')

    if category_update.name is not None:
        existing_category = (
            db.query(CategoryModel)
            .filter(CategoryModel.name == category_update.name, CategoryModel.id != category_id)
            .first()
        )
        if existing_category:
            raise HTTPException(status_code=400, detail='分类名称已存在')

    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete('/categories/{category_id:int}')
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail='分类不存在')

    dishes_in_category = db.query(DishModel).filter(DishModel.category_id == category_id).count()
    if dishes_in_category > 0:
        raise HTTPException(status_code=400, detail='分类下还有菜品，无法删除')

    db_category.is_active = False
    db.commit()
    return {'message': '分类已禁用'}

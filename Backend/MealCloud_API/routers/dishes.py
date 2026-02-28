from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_active_user
from models.user import User
from models.dish import Dish as DishModel, Category as CategoryModel
from schemas.dish import DishCreate, DishUpdate, Dish, CategoryCreate, CategoryUpdate, Category
from decimal import Decimal

router = APIRouter()

# 菜品相关路由
@router.get("/dishes", response_model=list[Dish])
async def get_dishes(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    dishes = db.query(DishModel).filter(DishModel.is_available == True).offset(skip).limit(limit).all()
    return dishes

@router.get("/dishes/{dish_id}", response_model=Dish)
async def get_dish(
    dish_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if dish is None or not dish.is_available:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return dish


@router.get("/dishes/category/{category_id}", response_model=list[Dish])
async def get_dishes_by_category(
    category_id: int,
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """按分类获取菜品"""
    dishes = db.query(DishModel).filter(
        DishModel.category_id == category_id,
        DishModel.is_available == True
    ).offset(skip).limit(limit).all()
    return dishes


@router.get("/dishes/search")
async def search_dishes(
    q: str = None,
    category_id: int = None,
    is_available: bool = True,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """搜索菜品"""
    query = db.query(DishModel)
    
    if q:
        query = query.filter(DishModel.name.contains(q))
    
    if category_id:
        query = query.filter(DishModel.category_id == category_id)
    
    if is_available is not None:
        query = query.filter(DishModel.is_available == is_available)
    
    dishes = query.all()
    return dishes

@router.post("/dishes", response_model=Dish)
async def create_dish(
    dish: DishCreate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # 检查分类是否存在
    category = db.query(CategoryModel).filter(CategoryModel.id == dish.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="分类不存在")
    
    # 检查菜品名称是否已存在
    existing_dish = db.query(DishModel).filter(DishModel.name == dish.name).first()
    if existing_dish:
        raise HTTPException(status_code=400, detail="菜品名称已存在")
    
    db_dish = DishModel(**dish.model_dump())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish

@router.put("/dishes/{dish_id}", response_model=Dish)
async def update_dish(
    dish_id: int, 
    dish_update: DishUpdate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="菜品不存在")
    
    # 如果更新了分类，检查分类是否存在
    if dish_update.category_id:
        category = db.query(CategoryModel).filter(CategoryModel.id == dish_update.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="分类不存在")
    
    # 更新字段
    update_data = dish_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dish, field, value)
    
    db.commit()
    db.refresh(db_dish)
    return db_dish

@router.delete("/dishes/{dish_id}")
async def delete_dish(
    dish_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if db_dish is None:
        raise HTTPException(status_code=404, detail="菜品不存在")
    
    # 逻辑删除（将is_available设为False）
    db_dish.is_available = False
    db.commit()
    return {"message": "菜品已禁用"}

# 分类相关路由
@router.get("/categories", response_model=list[Category])
async def get_categories(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    categories = db.query(CategoryModel).filter(CategoryModel.is_active == True).offset(skip).limit(limit).all()
    return categories

@router.get("/categories/{category_id}", response_model=Category)
async def get_category(
    category_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@router.post("/categories", response_model=Category)
async def create_category(
    category: CategoryCreate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # 检查分类名称是否已存在
    existing_category = db.query(CategoryModel).filter(CategoryModel.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=Category)
async def update_category(
    category_id: int, 
    category_update: CategoryUpdate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 更新字段
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查分类下是否有菜品
    dishes_count = db.query(DishModel).filter(
        DishModel.category_id == category_id,
        DishModel.is_available == True  # 只检查可用的菜品
    ).count()
    if dishes_count > 0:
        raise HTTPException(status_code=400, detail="分类下还有菜品，无法删除")
    
    # 逻辑删除（将is_active设为False）
    db_category.is_active = False
    db.commit()
    return {"message": "分类已禁用"}
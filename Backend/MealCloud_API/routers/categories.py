from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from database import get_db
from auth import get_current_active_user
from models.user import User
from models.dish import Category as CategoryModel
from schemas.dish import CategoryCreate, CategoryUpdate, Category


router = APIRouter()


@router.get("/categories", response_model=list[Category])
async def get_categories(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取菜品分类列表"""
    categories = db.query(CategoryModel).filter(CategoryModel.is_active == True).offset(skip).limit(limit).all()
    return categories


@router.get("/categories/{category_id}", response_model=Category)
async def get_category(
    category_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取单个菜品分类信息"""
    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if category is None or not category.is_active:
        raise HTTPException(status_code=404, detail="菜品分类不存在")
    return category


@router.post("/categories", response_model=Category)
async def create_category(
    category: CategoryCreate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """创建菜品分类"""
    # 检查分类名称是否已存在
    existing_category = db.query(CategoryModel).filter(CategoryModel.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="菜品分类名称已存在")
    
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
    """更新菜品分类信息"""
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="菜品分类不存在")
    
    # 检查名称是否与其他分类冲突
    if category_update.name is not None:
        existing_category = db.query(CategoryModel).filter(
            CategoryModel.name == category_update.name,
            CategoryModel.id != category_id
        ).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="菜品分类名称已存在")
    
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
    """删除菜品分类（逻辑删除）"""
    db_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="菜品分类不存在")
    
    # 检查分类下是否有菜品
    from models.dish import Dish as DishModel
    dishes_in_category = db.query(DishModel).filter(
        DishModel.category_id == category_id,
        DishModel.is_active == True  # 假设有is_active字段
    ).count()
    
    if dishes_in_category > 0:
        raise HTTPException(status_code=400, detail="分类下还有菜品，无法删除")
    
    # 逻辑删除（将is_active设为False）
    db_category.is_active = False
    db.commit()
    return {"message": "菜品分类已禁用"}


@router.get("/categories/stats")
async def get_category_stats(
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取菜品分类统计信息"""
    total_categories = db.query(CategoryModel).filter(CategoryModel.is_active == True).count()
    active_categories = db.query(CategoryModel).filter(CategoryModel.is_active == True).count()
    
    # 获取每个分类的菜品数量
    from models.dish import Dish as DishModel
    category_stats = []
    active_categories_list = db.query(CategoryModel).filter(CategoryModel.is_active == True).all()
    
    for category in active_categories_list:
        dish_count = db.query(DishModel).filter(
            DishModel.category_id == category.id,
            DishModel.is_active == True
        ).count()
        category_stats.append({
            "category_id": category.id,
            "category_name": category.name,
            "dish_count": dish_count
        })
    
    return {
        "total": total_categories,
        "active": active_categories,
        "category_details": category_stats
    }
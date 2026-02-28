from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: int
    image_url: Optional[str] = None
    is_available: bool = True
    is_featured: bool = False
    preparation_time: int = 15
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    nutritional_info: Optional[str] = None
    stock_quantity: int = -1  # -1表示无限库存
    min_stock_alert: int = 5

class DishCreate(DishBase):
    pass

class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None
    preparation_time: Optional[int] = None
    ingredients: Optional[str] = None
    allergens: Optional[str] = None
    nutritional_info: Optional[str] = None
    stock_quantity: Optional[int] = None
    min_stock_alert: Optional[int] = None

class Dish(DishBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
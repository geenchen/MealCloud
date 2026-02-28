from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # 分类名称
    description = Column(Text, nullable=True)  # 分类描述
    sort_order = Column(Integer, default=0)  # 排序
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # 菜品名称
    description = Column(Text, nullable=True)  # 菜品描述
    price = Column(Numeric(10, 2), nullable=False)  # 价格
    category_id = Column(Integer, ForeignKey("categories.id"))  # 分类ID
    image_url = Column(String, nullable=True)  # 图片URL
    is_available = Column(Boolean, default=True)  # 是否可售
    is_featured = Column(Boolean, default=False)  # 是否推荐
    preparation_time = Column(Integer, default=15)  # 准备时间（分钟）
    ingredients = Column(Text, nullable=True)  # 配料
    allergens = Column(String, nullable=True)  # 过敏原
    nutritional_info = Column(Text, nullable=True)  # 营养信息
    stock_quantity = Column(Integer, default=-1)  # 库存数量 (-1表示无限)
    min_stock_alert = Column(Integer, default=5)  # 最低库存警报
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    category = relationship("Category", back_populates="dishes")

    def __repr__(self):
        return f"<Dish(id={self.id}, name='{self.name}', price={self.price})>"


# 在Category类中添加反向关系
Category.dishes = relationship("Dish", order_by=Dish.id, back_populates="category")
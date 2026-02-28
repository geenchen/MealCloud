from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    dish_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    special_requests: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    dish_id: int
    is_prepared: bool
    prepared_at: Optional[datetime] = None
    is_served: bool
    served_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    order_number: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    table_id: Optional[int] = None
    order_type: str = 'dine_in'  # dine_in, takeaway, pack, preorder
    payment_method: str = 'cash'  # cash, wechat, alipay, mixed, credit
    payment_status: str = 'pending'  # pending, partial, paid, credit
    order_status: str = 'pending'  # pending, confirmed, preparing, ready, served, completed, cancelled
    subtotal: Decimal = Decimal('0.00')
    tax: Decimal = Decimal('0.00')
    service_fee: Decimal = Decimal('0.00')
    packing_fee: Decimal = Decimal('0.00')
    discount: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    paid_amount: Decimal = Decimal('0.00')
    remaining_amount: Decimal = Decimal('0.00')
    special_requests: Optional[str] = None
    is_takeout: bool = False
    takeout_number: Optional[str] = None
    waiter_id: Optional[int] = None
    is_suspended: bool = False  # 是否挂起（先下单后选桌）

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    table_id: Optional[int] = None
    order_type: Optional[str] = None
    payment_method: Optional[str] = None
    order_status: Optional[str] = None
    special_requests: Optional[str] = None
    is_suspended: Optional[bool] = None

class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    order_items: List[OrderItem] = []

    class Config:
        from_attributes = True

class TableBase(BaseModel):
    table_number: str
    name: str
    area_id: Optional[int] = None  # 区域ID
    area_name: str = '大厅'  # 区域名称（兼容旧数据）
    capacity: int = 4
    status: str = 'available'  # available, occupied, reserved, cleaning, unavailable
    is_active: bool = True
    description: Optional[str] = None
    qr_code_url: Optional[str] = None

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    name: Optional[str] = None
    area_id: Optional[int] = None
    area_name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None

from .area import Area as AreaSchema  # 导入Area schema


class Table(TableBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    area_info: Optional[AreaSchema] = None  # 区域信息

    class Config:
        from_attributes = True
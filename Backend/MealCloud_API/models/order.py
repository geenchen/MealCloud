from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from models.area import Area

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)  # 订单号
    customer_name = Column(String, nullable=True)  # 客户姓名
    customer_phone = Column(String, nullable=True)  # 客户电话
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)  # 桌台ID（可选）
    order_type = Column(String, default='dine_in')  # 订单类型：dine_in(堂食), takeaway(外带), pack(打包), preorder(预约)
    payment_method = Column(String, default='cash')  # 支付方式：cash(现金), wechat(微信), alipay(支付宝), mixed(混合), credit(赊账)
    payment_status = Column(String, default='pending')  # 支付状态：pending(待支付), partial(部分支付), paid(已支付), credit(赊账)
    order_status = Column(String, default='pending')  # 订单状态：pending(待确认), confirmed(已确认), preparing(制作中), ready(准备就绪), served(已上菜), completed(已完成), cancelled(已取消)
    subtotal = Column(Numeric(10, 2), default=0.00)  # 小计
    tax = Column(Numeric(10, 2), default=0.00)  # 税费
    service_fee = Column(Numeric(10, 2), default=0.00)  # 服务费
    packing_fee = Column(Numeric(10, 2), default=0.00)  # 打包费
    discount = Column(Numeric(10, 2), default=0.00)  # 折扣
    total_amount = Column(Numeric(10, 2), default=0.00)  # 总金额
    paid_amount = Column(Numeric(10, 2), default=0.00)  # 已支付金额
    remaining_amount = Column(Numeric(10, 2), default=0.00)  # 剩余金额
    special_requests = Column(Text, nullable=True)  # 特殊要求
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # 更新时间
    confirmed_at = Column(DateTime(timezone=True), nullable=True)  # 确认时间
    completed_at = Column(DateTime(timezone=True), nullable=True)  # 完成时间
    is_takeout = Column(Boolean, default=False)  # 是否外带
    takeout_number = Column(String, nullable=True)  # 取餐号
    waiter_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 服务员ID
    is_suspended = Column(Boolean, default=False)  # 是否挂起（先下单后选桌）
    
    # 关系
    table = relationship("Table", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    waiter = relationship("User")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', total_amount={self.total_amount})>"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)  # 单价
    total_price = Column(Numeric(10, 2), nullable=False)  # 总价
    special_requests = Column(Text, nullable=True)  # 特殊要求（如"不要香菜"等）
    is_prepared = Column(Boolean, default=False)  # 是否已制作
    prepared_at = Column(DateTime(timezone=True), nullable=True)  # 制作时间
    is_served = Column(Boolean, default=False)  # 是否已上菜
    served_at = Column(DateTime(timezone=True), nullable=True)  # 上菜时间
    
    # 关系
    order = relationship("Order", back_populates="order_items")
    dish = relationship("Dish")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, dish_id={self.dish_id})>"

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True, nullable=False)  # 桌号
    name = Column(String, nullable=False)  # 桌台名称
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)  # 区域ID
    area_name = Column(String, default='大厅')  # 区域名称（兼容旧数据）
    capacity = Column(Integer, default=4)  # 容纳人数
    status = Column(String, default='available')  # 状态：available(空闲), occupied(占用), reserved(预订), cleaning(清洁), unavailable(不可用)
    is_active = Column(Boolean, default=True)  # 是否激活
    description = Column(Text, nullable=True)  # 描述
    qr_code_url = Column(String, nullable=True)  # 二维码链接
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    area = relationship("Area", back_populates="tables", lazy="select", foreign_keys=[area_id])
    orders = relationship("Order", back_populates="table")

    def __repr__(self):
        return f"<Table(id={self.id}, table_number='{self.table_number}', name='{self.name}')>"
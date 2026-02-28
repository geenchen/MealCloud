from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import get_db
from auth import get_current_active_user
from models.user import User
from models.order import Order as OrderModel, OrderItem as OrderItemModel, Table as TableModel
from models.dish import Dish as DishModel
from schemas.order import OrderCreate, OrderUpdate, Order
from datetime import datetime, timedelta
from decimal import Decimal

router = APIRouter()

@router.get("/orders", response_model=list[Order])
async def get_orders(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    orders = db.query(OrderModel).offset(skip).limit(limit).all()
    return orders

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

@router.post("/orders", response_model=Order)
async def create_order(
    order: OrderCreate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # 检查订单号是否已存在
    existing_order = db.query(OrderModel).filter(OrderModel.order_number == order.order_number).first()
    if existing_order:
        raise HTTPException(status_code=400, detail="订单号已存在")
    
    # 检查桌台是否存在（如果指定了桌台）
    if order.table_id:
        table = db.query(TableModel).filter(TableModel.id == order.table_id).first()
        if not table:
            raise HTTPException(status_code=400, detail="桌台不存在")
    
    # 计算总价
    subtotal = sum(item.unit_price * item.quantity for item in order.order_items)
    total_amount = subtotal + order.tax + order.service_fee + order.packing_fee - order.discount
    
    # 创建订单
    db_order = OrderModel(
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        table_id=order.table_id,
        order_type=order.order_type,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        order_status=order.order_status,
        subtotal=subtotal,
        tax=order.tax,
        service_fee=order.service_fee,
        packing_fee=order.packing_fee,
        discount=order.discount,
        total_amount=total_amount,
        remaining_amount=total_amount,  # 初始剩余金额等于总金额
        special_requests=order.special_requests,
        is_takeout=order.is_takeout,
        takeout_number=order.takeout_number,
        waiter_id=current_user.id,  # 记录创建订单的用户
        is_suspended=order.is_suspended
    )
    
    db.add(db_order)
    db.flush()  # 获取订单ID以便创建订单项
    
    # 创建订单项
    for item in order.order_items:
        # 检查菜品是否存在
        dish = db.query(DishModel).filter(DishModel.id == item.dish_id).first()
        if not dish:
            raise HTTPException(status_code=400, detail=f"菜品ID {item.dish_id} 不存在")
        
        order_item = OrderItemModel(
            order_id=db_order.id,
            dish_id=item.dish_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            special_requests=item.special_requests
        )
        db.add(order_item)
    
    # 如果是外带订单且没有指定取餐号，自动生成取餐号
    if db_order.is_takeout and not db_order.takeout_number:
        # 简单的取餐号生成逻辑，实际应用中可能需要更复杂的逻辑
        takeout_number = f"T{datetime.now().strftime('%H%M%S')}{db_order.id}"
        db_order.takeout_number = takeout_number
    
    # 如果订单已支付，更新支付状态
    if db_order.paid_amount > 0:
        if db_order.paid_amount >= db_order.total_amount:
            db_order.payment_status = "paid"
        else:
            db_order.payment_status = "partial"
        db_order.remaining_amount = db_order.total_amount - db_order.paid_amount
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.put("/orders/{order_id}", response_model=Order)
async def update_order(
    order_id: int, 
    order_update: OrderUpdate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 更新字段
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    # 如果更新了支付信息，重新计算剩余金额
    if hasattr(order_update, 'paid_amount') and order_update.paid_amount is not None:
        db_order.remaining_amount = db_order.total_amount - db_order.paid_amount
        if db_order.paid_amount >= db_order.total_amount:
            db_order.payment_status = "paid"
        else:
            db_order.payment_status = "partial"
    
    # 更新时间戳
    db_order.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/orders/{order_id}")
async def delete_order(
    order_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查订单状态，不允许删除已完成或已取消的订单
    if db_order.order_status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="无法删除已完成或已取消的订单")
    
    db.delete(db_order)
    db.commit()
    return {"message": "订单删除成功"}

@router.post("/orders/{order_id}/confirm")
async def confirm_order(
    order_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if db_order.order_status != "pending":
        raise HTTPException(status_code=400, detail="只有待确认订单才能确认")
    
    db_order.order_status = "confirmed"
    db_order.confirmed_at = datetime.now()
    db.commit()
    db.refresh(db_order)
    return {"message": "订单已确认", "order": db_order}

@router.post("/orders/{order_id}/complete")
async def complete_order(
    order_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if db_order.order_status not in ["confirmed", "preparing", "ready"]:
        raise HTTPException(status_code=400, detail="订单不在可完成状态")
    
    db_order.order_status = "completed"
    db_order.completed_at = datetime.now()
    db.commit()
    db.refresh(db_order)
    return {"message": "订单已完成", "order": db_order}

# 新增接口：快速创建订单
@router.post("/orders/quick", response_model=Order)
async def create_quick_order(
    order_data: dict,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """快速创建订单接口，用于快速下单面板"""
    # 生成订单号
    order_number = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}"
    
    #计订单金额
    subtotal = Decimal('0.00')
    total_amount = Decimal('0.00')
    
    # 创建订单
    db_order = OrderModel(
        order_number=order_number,
        customer_name=order_data.get('customer_name'),
        customer_phone=order_data.get('customer_phone'),
        table_id=order_data.get('table_id'),
        order_type=order_data.get('order_type', 'dine_in'),
        payment_method=order_data.get('payment_method', 'cash'),
        subtotal=subtotal,
        total_amount=total_amount,
        order_status='pending'
    )
    
    db.add(db_order)
    db.flush()  # 获取订单ID但不提交事务
    
    # 添加订单项
    order_items_data = order_data.get('order_items', [])
    for item_data in order_items_data:
        db_item = OrderItemModel(
            order_id=db_order.id,
            dish_id=item_data['dish_id'],
            quantity=item_data['quantity'],
            unit_price=Decimal(str(item_data['unit_price'])),
            total_price=Decimal(str(item_data['total_price'])),
            special_requests=item_data.get('special_requests')
        )
        db.add(db_item)
        subtotal += Decimal(str(item_data['total_price']))
    
    # 更新订单总额
    total_amount = subtotal
    db_order.subtotal = subtotal
    db_order.total_amount = total_amount
    
    # 更新桌台状态
    if db_order.table_id and db_order.order_type == 'dine_in':
        table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
        if table and table.status == 'available':
            table.status = 'occupied'
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

# 新增接口：获取客户订单历史
@router.get("/orders/customer/{customer_phone}")
async def get_customer_order_history(
    customer_phone: str,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取指定客户的历史订单（用于订单复用）"""
    orders = db.query(OrderModel).filter(
        OrderModel.customer_phone == customer_phone
    ).order_by(OrderModel.created_at.desc()).limit(limit).all()
    
    #格式化订单数据
    formatted_orders = []
    for order in orders:
        # 获取订单菜品
        order_items = db.query(OrderItemModel).filter(
            OrderItemModel.order_id == order.id
        ).all()
        
        formatted_items = []
        for item in order_items:
            dish = db.query(DishModel).filter(DishModel.id == item.dish_id).first()
            if dish:
                formatted_items.append({
                    "dish_id": item.dish_id,
                    "dish_name": dish.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.total_price)
                })
        
        formatted_orders.append({
            "order_id": order.id,
            "order_number": order.order_number,
            "order_type": order.order_type,
            "total_amount": float(order.total_amount),
            "created_at": order.created_at,
            "items": formatted_items
        })
    
    return formatted_orders

# 新增接口：订单统计
@router.get("/orders/stats")
async def get_order_stats(
    days: int = 7,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取订单统计数据"""
    #计时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    #基统计
    total_orders = db.query(OrderModel).filter(
        OrderModel.created_at >= start_date
    ).count()
    
    total_revenue = db.query(func.sum(OrderModel.total_amount)).filter(
        and_(
            OrderModel.created_at >= start_date,
            OrderModel.order_status == 'completed'
        )
    ).scalar() or 0
    
    #按订单状态统计
    status_stats = {}
    for status in ['pending', 'confirmed', 'preparing', 'ready', 'served', 'completed', 'cancelled']:
        count = db.query(OrderModel).filter(
            and_(
                OrderModel.created_at >= start_date,
                OrderModel.order_status == status
            )
        ).count()
        if count > 0:
            status_stats[status] = count
    
    #热菜品（最近订单中）
    popular_dishes = db.query(
        OrderItemModel.dish_id,
        func.count(OrderItemModel.dish_id).label('order_count'),
        func.sum(OrderItemModel.quantity).label('total_quantity')
    ).join(OrderModel).filter(
        OrderModel.created_at >= start_date
    ).group_by(OrderItemModel.dish_id).order_by(
        func.count(OrderItemModel.dish_id).desc()
    ).limit(10).all()
    
    #格式化热门菜品数据
    formatted_dishes = []
    for dish_id, order_count, total_quantity in popular_dishes:
        dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
        if dish:
            formatted_dishes.append({
                "dish_id": dish_id,
                "dish_name": dish.name,
                "order_count": order_count,
                "total_quantity": int(total_quantity) if total_quantity else 0
            })
    
    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "status_stats": status_stats,
        "popular_dishes": formatted_dishes,
        "days": days
    }
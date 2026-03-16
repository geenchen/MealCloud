from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from auth import get_current_active_user
from database import get_db
from models.dish import Dish as DishModel
from models.order import Order as OrderModel, OrderItem as OrderItemModel, Table as TableModel
from models.user import User
from schemas.order import Order, OrderCreate, OrderUpdate

router = APIRouter()

ACTIVE_ORDER_STATUSES = ['pending', 'confirmed', 'preparing', 'ready', 'served']


def has_other_active_orders(db: Session, table_id: int, exclude_order_id: int | None = None) -> bool:
    query = db.query(OrderModel).filter(
        OrderModel.table_id == table_id,
        OrderModel.order_status.in_(ACTIVE_ORDER_STATUSES),
    )
    if exclude_order_id is not None:
        query = query.filter(OrderModel.id != exclude_order_id)
    return query.count() > 0


def release_table_if_idle(db: Session, table_id: int, exclude_order_id: int | None = None) -> None:
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if not table:
        return
    if not has_other_active_orders(db, table_id, exclude_order_id):
        table.status = 'available'
        table.updated_at = datetime.now()


@router.get('/orders', response_model=list[Order])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return db.query(OrderModel).order_by(OrderModel.created_at.desc()).offset(skip).limit(limit).all()


@router.get('/orders/stats')
async def get_order_stats(
    days: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    start_date = datetime.now() - timedelta(days=days)

    total_orders = db.query(OrderModel).filter(OrderModel.created_at >= start_date).count()
    total_revenue = (
        db.query(func.sum(OrderModel.total_amount))
        .filter(and_(OrderModel.created_at >= start_date, OrderModel.order_status == 'completed'))
        .scalar()
        or 0
    )

    status_stats = {}
    for status in ['pending', 'confirmed', 'preparing', 'ready', 'served', 'completed', 'cancelled']:
        count = (
            db.query(OrderModel)
            .filter(and_(OrderModel.created_at >= start_date, OrderModel.order_status == status))
            .count()
        )
        if count > 0:
            status_stats[status] = count

    popular_dishes = (
        db.query(
            OrderItemModel.dish_id,
            func.count(OrderItemModel.dish_id).label('order_count'),
            func.sum(OrderItemModel.quantity).label('total_quantity'),
        )
        .join(OrderModel)
        .filter(OrderModel.created_at >= start_date)
        .group_by(OrderItemModel.dish_id)
        .order_by(func.count(OrderItemModel.dish_id).desc())
        .limit(10)
        .all()
    )

    formatted_dishes = []
    for dish_id, order_count, total_quantity in popular_dishes:
        dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
        if dish:
            formatted_dishes.append(
                {
                    'dish_id': dish_id,
                    'dish_name': dish.name,
                    'order_count': int(order_count or 0),
                    'total_quantity': int(total_quantity or 0),
                }
            )

    return {
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'status_stats': status_stats,
        'popular_dishes': formatted_dishes,
        'days': days,
    }


@router.get('/orders/customer/{customer_phone}')
async def get_customer_order_history(
    customer_phone: str,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(OrderModel)
        .filter(OrderModel.customer_phone == customer_phone)
        .order_by(OrderModel.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for order in orders:
        items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
        formatted_items = []
        for item in items:
            dish = db.query(DishModel).filter(DishModel.id == item.dish_id).first()
            if not dish:
                continue
            formatted_items.append(
                {
                    'dish_id': item.dish_id,
                    'dish_name': dish.name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price),
                }
            )

        result.append(
            {
                'order_id': order.id,
                'order_number': order.order_number,
                'order_type': order.order_type,
                'total_amount': float(order.total_amount),
                'created_at': order.created_at,
                'items': formatted_items,
            }
        )

    return result


@router.get('/orders/{order_id:int}', response_model=Order)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail='order not found')
    return order


@router.post('/orders', response_model=Order)
async def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if db.query(OrderModel).filter(OrderModel.order_number == order.order_number).first():
        raise HTTPException(status_code=400, detail='order_number already exists')

    table = None
    if order.table_id:
        table = db.query(TableModel).filter(TableModel.id == order.table_id).first()
        if not table:
            raise HTTPException(status_code=400, detail='table not found')
        if order.order_type == 'dine_in' and table.status not in ['available', 'reserved', 'occupied']:
            raise HTTPException(status_code=400, detail='table is not available for dine-in order')

    subtotal = sum(Decimal(item.unit_price) * item.quantity for item in order.order_items)
    total_amount = subtotal + order.tax + order.service_fee + order.packing_fee - order.discount

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
        paid_amount=order.paid_amount,
        remaining_amount=total_amount - order.paid_amount,
        special_requests=order.special_requests,
        is_takeout=order.is_takeout,
        takeout_number=order.takeout_number,
        waiter_id=current_user.id,
        is_suspended=order.is_suspended,
    )

    if db_order.paid_amount > 0:
        db_order.payment_status = 'paid' if db_order.paid_amount >= db_order.total_amount else 'partial'

    db.add(db_order)
    db.flush()

    for item in order.order_items:
        dish = db.query(DishModel).filter(DishModel.id == item.dish_id).first()
        if not dish:
            raise HTTPException(status_code=400, detail=f'dish {item.dish_id} not found')

        db.add(
            OrderItemModel(
                order_id=db_order.id,
                dish_id=item.dish_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                special_requests=item.special_requests,
            )
        )

    if db_order.is_takeout and not db_order.takeout_number:
        db_order.takeout_number = f"T{datetime.now().strftime('%H%M%S')}{db_order.id}"

    if table and db_order.order_type == 'dine_in' and db_order.order_status in ACTIVE_ORDER_STATUSES:
        table.status = 'occupied'
        table.updated_at = datetime.now()

    db.commit()
    db.refresh(db_order)
    return db_order


@router.post('/orders/quick', response_model=Order)
async def create_quick_order(
    order_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    order_number = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}"

    db_order = OrderModel(
        order_number=order_number,
        customer_name=order_data.get('customer_name'),
        customer_phone=order_data.get('customer_phone'),
        table_id=order_data.get('table_id'),
        order_type=order_data.get('order_type', 'dine_in'),
        payment_method=order_data.get('payment_method', 'cash'),
        order_status='pending',
        subtotal=Decimal('0.00'),
        total_amount=Decimal('0.00'),
        waiter_id=current_user.id,
    )

    db.add(db_order)
    db.flush()

    subtotal = Decimal('0.00')
    for item in order_data.get('order_items', []):
        total_price = Decimal(str(item['total_price']))
        db.add(
            OrderItemModel(
                order_id=db_order.id,
                dish_id=item['dish_id'],
                quantity=item['quantity'],
                unit_price=Decimal(str(item['unit_price'])),
                total_price=total_price,
                special_requests=item.get('special_requests'),
            )
        )
        subtotal += total_price

    db_order.subtotal = subtotal
    db_order.total_amount = subtotal

    if db_order.table_id and db_order.order_type == 'dine_in':
        table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
        if table and table.status in ['available', 'reserved', 'occupied']:
            table.status = 'occupied'
            table.updated_at = datetime.now()

    db.commit()
    db.refresh(db_order)
    return db_order


@router.put('/orders/{order_id:int}', response_model=Order)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail='order not found')

    old_status = db_order.order_status
    old_table_id = db_order.table_id

    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)

    if db_order.order_status != old_status:
        if db_order.order_status == 'confirmed':
            db_order.confirmed_at = datetime.now()
        if db_order.order_status == 'completed':
            db_order.completed_at = datetime.now()

    if db_order.table_id and db_order.order_status in ACTIVE_ORDER_STATUSES and db_order.order_type == 'dine_in':
        table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
        if table:
            table.status = 'occupied'
            table.updated_at = datetime.now()

    if old_table_id and old_table_id != db_order.table_id:
        release_table_if_idle(db, old_table_id, exclude_order_id=db_order.id)

    if db_order.order_status in ['completed', 'cancelled'] and db_order.table_id:
        release_table_if_idle(db, db_order.table_id, exclude_order_id=db_order.id)

    db_order.updated_at = datetime.now()
    db.commit()
    db.refresh(db_order)
    return db_order


@router.post('/orders/{order_id:int}/confirm')
async def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail='order not found')
    if db_order.order_status != 'pending':
        raise HTTPException(status_code=400, detail='only pending order can be confirmed')

    db_order.order_status = 'confirmed'
    db_order.confirmed_at = datetime.now()
    db_order.updated_at = datetime.now()

    if db_order.table_id and db_order.order_type == 'dine_in':
        table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
        if table:
            table.status = 'occupied'
            table.updated_at = datetime.now()

    db.commit()
    db.refresh(db_order)
    return {'message': 'order confirmed', 'order': db_order}


@router.post('/orders/{order_id:int}/complete')
async def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail='order not found')
    if db_order.order_status not in ['confirmed', 'preparing', 'ready', 'served']:
        raise HTTPException(status_code=400, detail='order status cannot complete')

    db_order.order_status = 'completed'
    db_order.completed_at = datetime.now()
    db_order.updated_at = datetime.now()

    if db_order.table_id:
        table = db.query(TableModel).filter(TableModel.id == db_order.table_id).first()
        if table and not has_other_active_orders(db, table.id, exclude_order_id=db_order.id):
            table.status = 'cleaning'
            table.updated_at = datetime.now()

    db.commit()
    db.refresh(db_order)
    return {'message': 'order completed', 'order': db_order}


@router.post('/orders/{order_id:int}/cancel')
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail='order not found')
    if db_order.order_status in ['completed', 'cancelled']:
        raise HTTPException(status_code=400, detail='order cannot be cancelled')

    db_order.order_status = 'cancelled'
    db_order.updated_at = datetime.now()

    if db_order.table_id:
        release_table_if_idle(db, db_order.table_id, exclude_order_id=db_order.id)

    db.commit()
    db.refresh(db_order)
    return {'message': 'order cancelled', 'order': db_order}


@router.delete('/orders/{order_id:int}')
async def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail='order not found')

    if db_order.order_status in ['completed', 'cancelled']:
        raise HTTPException(status_code=400, detail='cannot delete completed/cancelled order')

    table_id = db_order.table_id
    db.delete(db_order)

    if table_id:
        release_table_if_idle(db, table_id, exclude_order_id=order_id)

    db.commit()
    return {'message': 'order deleted'}

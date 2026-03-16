from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_active_user
from database import get_db
from models.area import Area as AreaModel
from models.order import Order as OrderModel
from models.order import Table as TableModel
from models.reservation import Reservation as ReservationModel
from models.user import User
from schemas.order import Table, TableCreate, TableUpdate
from schemas.reservation import Reservation as ReservationSchema
from schemas.reservation import ReservationCreate

router = APIRouter()


@router.get('/tables', response_model=list[Table])
async def get_tables(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(TableModel)
        .filter(TableModel.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get('/tables/{table_id:int}', response_model=Table)
async def get_table(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id, TableModel.is_active == True).first()
    if table is None:
        raise HTTPException(status_code=404, detail='table not found')
    return table


@router.post('/tables', response_model=Table)
async def create_table(
    table: TableCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    exists = db.query(TableModel).filter(TableModel.table_number == table.table_number).first()
    if exists:
        raise HTTPException(status_code=400, detail='table_number already exists')

    if table.area_id is not None:
        area = db.query(AreaModel).filter(AreaModel.id == table.area_id, AreaModel.is_active == True).first()
        if area is None:
            raise HTTPException(status_code=404, detail='area not found')

    db_table = TableModel(
        table_number=table.table_number,
        name=table.name,
        area_id=table.area_id,
        area_name=table.area_name or 'Hall',
        capacity=table.capacity,
        status=table.status,
        is_active=table.is_active,
        description=table.description,
        qr_code_url=table.qr_code_url
    )
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table


@router.put('/tables/{table_id:int}', response_model=Table)
async def update_table(
    table_id: int,
    table_update: TableUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail='table not found')

    if table_update.area_id is not None:
        area = db.query(AreaModel).filter(AreaModel.id == table_update.area_id, AreaModel.is_active == True).first()
        if area is None:
            raise HTTPException(status_code=404, detail='area not found')

    update_data = table_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_table, field, value)

    db.commit()
    db.refresh(db_table)
    return db_table


@router.delete('/tables/{table_id:int}')
async def delete_table(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail='table not found')

    active_orders = (
        db.query(OrderModel)
        .filter(OrderModel.table_id == table_id, OrderModel.order_status.notin_(['completed', 'cancelled']))
        .count()
    )
    if active_orders > 0:
        raise HTTPException(status_code=400, detail='table has active orders and cannot be deleted')

    db_table.is_active = False
    db.commit()
    return {'message': 'table disabled'}


@router.get('/tables/available')
async def get_available_tables(
    area: str = None,
    area_id: int = None,
    capacity: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(TableModel).filter(TableModel.is_active == True, TableModel.status == 'available')
    if area:
        query = query.filter(TableModel.area_name == area)
    if area_id:
        query = query.filter(TableModel.area_id == area_id)
    if capacity:
        query = query.filter(TableModel.capacity >= capacity)
    return query.all()


@router.post('/tables/{table_id:int}/occupy')
async def occupy_table(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail='table not found')
    if table.status != 'available':
        raise HTTPException(status_code=400, detail='table is not available for occupy')

    table.status = 'occupied'
    table.updated_at = datetime.now()
    db.commit()
    return {'message': 'table occupied', 'table': table}


@router.post('/tables/{table_id:int}/free')
async def free_table(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail='table not found')

    active_orders = (
        db.query(OrderModel)
        .filter(OrderModel.table_id == table_id, OrderModel.order_status.notin_(['completed', 'cancelled']))
        .count()
    )
    if active_orders > 0:
        raise HTTPException(status_code=400, detail='table has active orders and cannot be freed')

    table.status = 'available'
    table.updated_at = datetime.now()
    db.commit()
    return {'message': 'table released', 'table': table}


@router.post('/tables/{table_id:int}/clean')
async def clean_table(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail='table not found')

    table.status = 'cleaning'
    table.updated_at = datetime.now()
    db.commit()
    return {'message': 'table set to cleaning', 'table': table}


@router.post('/tables/{table_id:int}/clean-complete')
async def complete_table_cleaning(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail='table not found')
    if table.status != 'cleaning':
        raise HTTPException(status_code=400, detail='only cleaning table can complete cleaning')

    table.status = 'available'
    table.updated_at = datetime.now()
    db.commit()
    return {'message': 'table cleaning completed', 'table': table}


@router.get('/tables/stats')
async def get_table_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    base = db.query(TableModel).filter(TableModel.is_active == True)
    return {
        'total': base.count(),
        'available': base.filter(TableModel.status == 'available').count(),
        'occupied': base.filter(TableModel.status == 'occupied').count(),
        'reserved': base.filter(TableModel.status == 'reserved').count(),
        'cleaning': base.filter(TableModel.status == 'cleaning').count(),
        'unavailable': base.filter(TableModel.status == 'unavailable').count()
    }


@router.get('/tables/{table_id:int}/details')
async def get_table_details(
    table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id, TableModel.is_active == True).first()
    if table is None:
        raise HTTPException(status_code=404, detail='table not found')

    active_orders = (
        db.query(OrderModel)
        .filter(OrderModel.table_id == table_id, OrderModel.order_status.notin_(['completed', 'cancelled']))
        .all()
    )
    return {
        'table': table,
        'active_orders': active_orders,
        'active_order_count': len(active_orders)
    }


@router.post('/tables/merge')
async def merge_tables(
    table_ids: list[int],
    merged_table_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if len(table_ids) < 2:
        raise HTTPException(status_code=400, detail='at least two tables are required')

    tables = db.query(TableModel).filter(TableModel.id.in_(table_ids), TableModel.is_active == True).all()
    if len(tables) != len(table_ids):
        raise HTTPException(status_code=404, detail='some tables were not found')

    for table in tables:
        if table.status != 'available':
            raise HTTPException(status_code=400, detail=f'table {table.table_number} is not available')

    exists = db.query(TableModel).filter(TableModel.table_number == merged_table_number).first()
    if exists:
        raise HTTPException(status_code=400, detail='merged table_number already exists')

    merged_table = TableModel(
        table_number=merged_table_number,
        name='merged table',
        area_name=tables[0].area_name,
        area_id=tables[0].area_id,
        capacity=sum(t.capacity for t in tables),
        status='available',
        is_active=True,
        description='merged from multiple tables'
    )
    db.add(merged_table)

    for table in tables:
        table.is_active = False
        table.updated_at = datetime.now()

    db.commit()
    db.refresh(merged_table)
    return {'message': 'merge success', 'merged_table': merged_table}


@router.post('/tables/split/{merged_table_id}')
async def split_table(
    merged_table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    merged_table = db.query(TableModel).filter(TableModel.id == merged_table_id).first()
    if merged_table is None:
        raise HTTPException(status_code=404, detail='table not found')

    merged_table.is_active = False
    merged_table.updated_at = datetime.now()
    db.commit()
    return {'message': 'split completed, restore original tables manually'}


@router.post('/tables/switch')
async def switch_tables(
    from_table_id: int,
    to_table_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from_table = db.query(TableModel).filter(TableModel.id == from_table_id).first()
    to_table = db.query(TableModel).filter(TableModel.id == to_table_id).first()
    if not from_table or not to_table:
        raise HTTPException(status_code=404, detail='table not found')
    if from_table.status != 'occupied' or to_table.status != 'available':
        raise HTTPException(status_code=400, detail='table status does not meet switch conditions')

    from_table.status = 'available'
    to_table.status = 'occupied'
    from_table.updated_at = datetime.now()
    to_table.updated_at = datetime.now()
    db.commit()
    return {'message': 'switch success'}


@router.post('/tables/batch-update')
async def batch_update_tables(
    table_updates: list[dict],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    updated = 0
    for item in table_updates:
        table_id = item.get('id')
        if not table_id:
            continue
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table:
            continue
        for key, value in item.items():
            if key != 'id' and hasattr(table, key):
                setattr(table, key, value)
        table.updated_at = datetime.now()
        updated += 1
    db.commit()
    return {'message': 'batch update completed', 'updated_count': updated}


@router.get('/reservations', response_model=list[ReservationSchema])
async def get_reservations(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(ReservationModel)
    if status:
        query = query.filter(ReservationModel.status == status)
    return query.order_by(ReservationModel.reservation_time.asc()).offset(skip).limit(limit).all()


@router.post('/reservations', response_model=ReservationSchema)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if reservation.party_size <= 0:
        raise HTTPException(status_code=400, detail='party_size must be greater than 0')

    table = None
    if reservation.table_id is not None:
        table = db.query(TableModel).filter(TableModel.id == reservation.table_id, TableModel.is_active == True).first()
        if table is None:
            raise HTTPException(status_code=404, detail='table not found')
        if table.status not in ['available', 'reserved']:
            raise HTTPException(status_code=400, detail='table is not reservable')
    else:
        if not (reservation.area_name or '').strip():
            raise HTTPException(status_code=400, detail='area_name is required for hall reservation')

    db_reservation = ReservationModel(
        table_id=reservation.table_id,
        area_name=((reservation.area_name or '').strip() if reservation.table_id is None else (reservation.area_name or (table.area_name if table else 'Hall'))),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        party_size=reservation.party_size,
        reservation_time=reservation.reservation_time,
        status='booked',
        notes=reservation.notes
    )

    db.add(db_reservation)
    if table is not None:
        table.status = 'reserved'
        table.updated_at = datetime.now()

    db.commit()
    db.refresh(db_reservation)
    return db_reservation


@router.post('/reservations/{reservation_id}/cancel')
async def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reservation = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail='reservation not found')

    reservation.status = 'cancelled'
    reservation.updated_at = datetime.now()

    if reservation.table_id is not None:
        active_count = (
            db.query(ReservationModel)
            .filter(
                ReservationModel.table_id == reservation.table_id,
                ReservationModel.status == 'booked',
                ReservationModel.id != reservation.id
            )
            .count()
        )
        table = db.query(TableModel).filter(TableModel.id == reservation.table_id).first()
        if table and active_count == 0 and table.status == 'reserved':
            table.status = 'available'
            table.updated_at = datetime.now()

    db.commit()
    return {'message': 'reservation cancelled'}


@router.post('/reservations/{reservation_id}/arrive')
async def arrive_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reservation = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail='reservation not found')

    reservation.status = 'arrived'
    reservation.updated_at = datetime.now()

    if reservation.table_id is not None:
        table = db.query(TableModel).filter(TableModel.id == reservation.table_id).first()
        if table is not None:
            table.status = 'occupied'
            table.updated_at = datetime.now()

    db.commit()
    return {'message': 'reservation arrived'}


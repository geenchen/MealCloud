from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import get_db
from auth import get_current_active_user
from models.user import User
from models.order import Order as OrderModel, Table as TableModel, OrderItem as OrderItemModel
from models.area import Area as AreaModel
from schemas.order import TableCreate, TableUpdate, Table
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/tables", response_model=list[Table])
async def get_tables(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    tables = db.query(TableModel).filter(TableModel.is_active == True).offset(skip).limit(limit).all()
    # 为每个桌子添加区域信息
    for table in tables:
        if hasattr(table, 'area') and table.area:
            table.area_info = table.area
    return tables

@router.get("/tables/{table_id}", response_model=Table)
async def get_table(
    table_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None or not table.is_active:
        raise HTTPException(status_code=404, detail="桌台不存在")
    # 添加区域信息
    if hasattr(table, 'area') and table.area:
        table.area_info = table.area
    return table

@router.post("/tables", response_model=Table)
async def create_table(
    table: TableCreate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # 检查桌号是否已存在
    existing_table = db.query(TableModel).filter(TableModel.table_number == table.table_number).first()
    if existing_table:
        raise HTTPException(status_code=400, detail="桌号已存在")
    
    # 如果指定了area_id，验证区域是否存在
    if table.area_id is not None:
        area = db.query(AreaModel).filter(AreaModel.id == table.area_id, AreaModel.is_active == True).first()
        if not area:
            raise HTTPException(status_code=404, detail="区域不存在或已禁用")
    
    # 创建桌台时只传递模型实际拥有的字段
    table_data = {}
    # 映射schema字段到model字段
    table_data['table_number'] = table.table_number
    table_data['name'] = table.name
    table_data['area_id'] = table.area_id
    table_data['area_name'] = table.area_name if hasattr(table, 'area_name') and table.area_name else '大厅'  # 兼容旧数据
    table_data['capacity'] = table.capacity
    table_data['status'] = table.status
    table_data['is_active'] = table.is_active
    table_data['description'] = table.description or None
    table_data['qr_code_url'] = table.qr_code_url or None
    
    db_table = TableModel(**table_data)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    
    # 添加区域信息
    if hasattr(db_table, 'area') and db_table.area:
        db_table.area_info = db_table.area
    
    return db_table

@router.put("/tables/{table_id}", response_model=Table)
async def update_table(
    table_id: int, 
    table_update: TableUpdate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    # 如果更新了area_id，验证区域是否存在
    if table_update.area_id is not None:
        area = db.query(AreaModel).filter(AreaModel.id == table_update.area_id, AreaModel.is_active == True).first()
        if not area:
            raise HTTPException(status_code=404, detail="区域不存在或已禁用")
    
    # 更新字段
    update_data = table_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_table, field, value)
    
    db.commit()
    db.refresh(db_table)
    
    # 添加区域信息
    if hasattr(db_table, 'area') and db_table.area:
        db_table.area_info = db_table.area
    
    return db_table

@router.delete("/tables/{table_id}")
async def delete_table(
    table_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if db_table is None:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    # 检查桌台是否有未完成的订单
    active_orders = db.query(OrderModel).filter(
        OrderModel.table_id == table_id,
        OrderModel.order_status.notin_(["completed", "cancelled"])
    ).count()
    
    if active_orders > 0:
        raise HTTPException(status_code=400, detail="桌台有未完成的订单，无法删除")
    
    # 逻辑删除（将is_active设为False）
    db_table.is_active = False
    db.commit()
    return {"message": "桌台已禁用"}

@router.get("/tables/available")
async def get_available_tables(
    area: str = None,
    area_id: int = None,
    capacity: int = None,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取空闲桌台"""
    query = db.query(TableModel).filter(TableModel.is_active == True, TableModel.status == "available")
    
    if area:
        query = query.filter(TableModel.area == area)
    
    if area_id:
        query = query.filter(TableModel.area_id == area_id)
    
    if capacity:
        query = query.filter(TableModel.capacity >= capacity)
    
    available_tables = query.all()
    # 为每个桌子添加区域信息
    for table in available_tables:
        if hasattr(table, 'area') and table.area:
            table.area_info = table.area
    return available_tables

@router.post("/tables/{table_id}/occupy")
async def occupy_table(
    table_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """占用桌台（例如顾客就座）"""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    if table.status != "available":
        raise HTTPException(status_code=400, detail="桌台当前不可用")
    
    table.status = "occupied"
    table.updated_at = datetime.now()
    db.commit()
    return {"message": "桌台已占用", "table": table}

@router.post("/tables/{table_id}/free")
async def free_table(
    table_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """释放桌台（例如顾客离开）"""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    # 检查桌台是否有未完成的订单
    active_orders = db.query(OrderModel).filter(
        OrderModel.table_id == table_id,
        OrderModel.order_status.notin_(["completed", "cancelled"])
    ).count()
    
    if active_orders > 0:
        raise HTTPException(status_code=400, detail="桌台有未完成的订单，无法释放")
    
    table.status = "available"
    table.updated_at = datetime.now()
    db.commit()
    return {"message": "桌台已释放", "table": table}

@router.post("/tables/{table_id}/clean")
async def clean_table(
    table_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """将桌台设为清洁状态"""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    table.status = "cleaning"
    table.updated_at = datetime.now()
    db.commit()
    return {"message": "桌台已设为清洁状态", "table": table}


@router.post("/tables/merge")
async def merge_tables(
    table_ids: list[int],  # 要合并的桌台ID列表
    merged_table_number: str,  # 合并后的桌台编号
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """合并多个桌台为一个大桌台"""
    if len(table_ids) < 2:
        raise HTTPException(status_code=400, detail="至少需要选择2个桌台进行合并")
    
    # 获取所有要合并的桌台
    tables_to_merge = db.query(TableModel).filter(TableModel.id.in_(table_ids)).all()
    
    if len(tables_to_merge) != len(table_ids):
        raise HTTPException(status_code=404, detail="部分桌台不存在")
    
    # 检查桌台是否都是空闲状态
    for table in tables_to_merge:
        if table.status != "available":
            raise HTTPException(status_code=400, detail=f"桌台 {table.table_number} 不是空闲状态，无法合并")
    
    # 检查目标桌台编号是否已存在
    existing_merged_table = db.query(TableModel).filter(TableModel.table_number == merged_table_number).first()
    if existing_merged_table:
        raise HTTPException(status_code=400, detail="合并后的桌台编号已存在")
    
    # 计算合并后桌台的总容量
    total_capacity = sum(table.capacity for table in tables_to_merge)
    
    # 创建合并后的桌台
    merged_table = TableModel(
        table_number=merged_table_number,
        name=f"合并桌 ({' + '.join([t.name for t in tables_to_merge])})",
        area=tables_to_merge[0].area,  # 使用第一个桌台的区域
        capacity=total_capacity,
        status="occupied",  # 合并后立即占用
        is_active=True,
        description=f"由桌台 {', '.join([t.table_number for t in tables_to_merge])} 合并而成"
    )
    
    db.add(merged_table)
    db.flush()  # 获取新桌台的ID
    
    # 将原来的桌台标记为不可用（逻辑删除）
    for table in tables_to_merge:
        table.is_active = False
        table.updated_at = datetime.now()
    
    db.commit()
    return {
        "message": "桌台合并成功",
        "merged_table": merged_table,
        "original_tables": tables_to_merge
    }


@router.post("/tables/split/{merged_table_id}")
async def split_table(
    merged_table_id: int,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """拆分合并的桌台，恢复原始桌台"""
    merged_table = db.query(TableModel).filter(TableModel.id == merged_table_id).first()
    if not merged_table:
        raise HTTPException(status_code=404, detail="合并桌台不存在")
    
    if not merged_table.description or "合并桌" not in merged_table.description:
        raise HTTPException(status_code=400, detail="该桌台不是合并桌台")
    
    # 检查合并桌台是否有未完成的订单
    active_orders = db.query(OrderModel).filter(
        OrderModel.table_id == merged_table_id,
        OrderModel.order_status.notin_(["completed", "cancelled"])
    ).count()
    
    if active_orders > 0:
        raise HTTPException(status_code=400, detail="合并桌台有未完成的订单，无法拆分")
    
    # 解析原始桌台信息（从描述中提取）
    # 这里我们假设描述格式为："由桌台 T001, T002, T003 合并而成"
    import re
    original_numbers_match = re.search(r'由桌台 ([^合并]+) 合并而成', merged_table.description)
    if not original_numbers_match:
        raise HTTPException(status_code=400, detail="无法解析原始桌台信息")
    
    original_numbers = [num.strip() for num in original_numbers_match.group(1).split(',')]
    
    # 查找原始桌台记录（已标记为非活跃）
    original_tables = db.query(TableModel).filter(
        TableModel.table_number.in_(original_numbers),
        TableModel.is_active == False  # 之前被标记为非活跃
    ).all()
    
    if len(original_tables) != len(original_numbers):
        raise HTTPException(status_code=400, detail="无法找到所有原始桌台记录")
    
    # 恢复原始桌台为可用状态
    for table in original_tables:
        table.is_active = True
        table.status = "available"
        table.updated_at = datetime.now()
    
    # 删除合并桌台
    merged_table.is_active = False
    db.commit()
    
    return {
        "message": "桌台拆分成功",
        "restored_tables": original_tables
    }


@router.post("/tables/switch")
async def switch_tables(
    from_table_id: int,
    to_table_id: int,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """将顾客从一个桌台转移到另一个桌台"""
    from_table = db.query(TableModel).filter(TableModel.id == from_table_id).first()
    to_table = db.query(TableModel).filter(TableModel.id == to_table_id).first()
    
    if not from_table or not to_table:
        raise HTTPException(status_code=404, detail="源桌台或目标桌台不存在")
    
    if from_table.status != "occupied":
        raise HTTPException(status_code=400, detail="源桌台不是占用状态")
    
    if to_table.status != "available":
        raise HTTPException(status_code=400, detail="目标桌台不是空闲状态")
    
    if from_table_id == to_table_id:
        raise HTTPException(status_code=400, detail="源桌台和目标桌台不能相同")
    
    # 检查源桌台是否有订单
    orders_on_from_table = db.query(OrderModel).filter(
        OrderModel.table_id == from_table_id,
        OrderModel.order_status.notin_(["completed", "cancelled"])
    ).all()
    
    if not orders_on_from_table:
        raise HTTPException(status_code=400, detail="源桌台没有未完成的订单")
    
    # 检查目标桌台容量是否足够
    max_customer_count = sum(order.subtotal for order in orders_on_from_table)  # 简化判断
    if to_table.capacity < from_table.capacity:
        # 更合理的检查方式是检查订单中的人数或菜品数量
        pass  # 暂时不强制检查容量
    
    # 更新订单的桌台ID
    for order in orders_on_from_table:
        order.table_id = to_table_id
        order.updated_at = datetime.now()
    
    # 更新桌台状态
    from_table.status = "available"
    to_table.status = "occupied"
    from_table.updated_at = datetime.now()
    to_table.updated_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "桌台转移成功",
        "from_table": from_table,
        "to_table": to_table,
        "updated_orders": len(orders_on_from_table)
    }

# 新增接口：生成桌台二维码数据
@router.get("/tables/{table_id}/qrcode-data")
async def get_table_qrcode_data(
    table_id: int,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取桌台二维码数据"""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None or not table.is_active:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    # 生成二维码数据 - 包含桌台信息的JSON
    qr_data = {
        "type": "table",
        "tableId": table.id,
        "tableName": table.name,
        "tableNumber": table.table_number,
        "area": table.area,
        "timestamp": datetime.now().isoformat()
    }
    
    import json
    import base64
    qr_json = json.dumps(qr_data)
    encoded_data = base64.b64encode(qr_json.encode()).decode()
    
    return {
        "table": table,
        "qrcode_data": encoded_data,
        "raw_data": qr_data
    }

# 新增接口：获取桌台二维码URL
@router.get("/tables/{table_id}/qrcode-url")
async def get_table_qrcode_url(
    table_id: int,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取桌台二维码URL"""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None or not table.is_active:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    # 生成二维码URL - 这里应该是实际的二维码图片服务URL
    # 在实际部署时，这应该指向一个能生成二维码图片的服务
    qr_url = f"/api/v1/qrcode/generate?data=table_{table_id}_{table.table_number}"
    
    return {
        "table_id": table.id,
        "table_name": table.name,
        "qrcode_url": qr_url
    }

# 新增接口：前台二维码数据
@router.get("/tables/frontdesk/qrcode-data")
async def get_frontdesk_qrcode_data(
    current_user: User = Depends(get_current_active_user)
):
    """获取前台二维码数据（用于外带模式）"""
    qr_data = {
        "type": "frontdesk",
        "location": "frontdesk",
        "storeId": current_user.id,  # 使用当前用户ID作为店铺标识
        "timestamp": datetime.now().isoformat()
    }
    
    import json
    import base64
    qr_json = json.dumps(qr_data)
    encoded_data = base64.b64encode(qr_json.encode()).decode()
    
    return {
        "qrcode_data": encoded_data,
        "raw_data": qr_data
    }

# 新增接口：前台二维码URL
@router.get("/tables/frontdesk/qrcode-url")
async def get_frontdesk_qrcode_url(
    current_user: User = Depends(get_current_active_user)
):
    """获取前台二维码URL"""
    qr_url = f"/api/v1/qrcode/generate?data=frontdesk_{current_user.id}"
    
    return {
        "type": "frontdesk",
        "qrcode_url": qr_url
    }

# 新增接口：获取桌台统计信息
@router.get("/tables/stats")
async def get_table_stats(
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取桌台统计信息"""
    total_tables = db.query(TableModel).filter(TableModel.is_active == True).count()
    available_tables = db.query(TableModel).filter(
        and_(TableModel.is_active == True, TableModel.status == "available")
    ).count()
    occupied_tables = db.query(TableModel).filter(
        and_(TableModel.is_active == True, TableModel.status == "occupied")
    ).count()
    reserved_tables = db.query(TableModel).filter(
        and_(TableModel.is_active == True, TableModel.status == "reserved")
    ).count()
    cleaning_tables = db.query(TableModel).filter(
        and_(TableModel.is_active == True, TableModel.status == "cleaning")
    ).count()
    
    return {
        "total": total_tables,
        "available": available_tables,
        "occupied": occupied_tables,
        "reserved": reserved_tables,
        "cleaning": cleaning_tables
    }

# 新增接口：获取桌台详情和当前订单信息
@router.get("/tables/{table_id}/details")
async def get_table_details(
    table_id: int,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取桌台详情和当前订单信息"""
    table = db.query(TableModel).filter(TableModel.id == table_id).first()
    if table is None or not table.is_active:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    # 获取当前桌台的订单
    current_order = None
    if table.status == "occupied":
        current_order = db.query(OrderModel).filter(
            and_(
                OrderModel.table_id == table_id,
                OrderModel.order_status.in_(["pending", "confirmed", "preparing", "ready", "served"])
            )
        ).first()
    
    # 获取桌台历史订单（最近7天）
    seven_days_ago = datetime.now() - timedelta(days=7)
    order_history = db.query(OrderModel).filter(
        and_(
            OrderModel.table_id == table_id,
            OrderModel.created_at >= seven_days_ago
        )
    ).order_by(OrderModel.created_at.desc()).limit(10).all()
    
    #格化订单历史
    formatted_history = []
    for order in order_history:
        formatted_history.append({
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "amount": float(order.total_amount),
            "status": order.order_status,
            "created_at": order.created_at
        })
    
    return {
        "table": table,
        "current_order": current_order,
        "order_history": formatted_history
    }

# 新增接口：批量更新桌台状态
@router.post("/tables/batch-update")
async def batch_update_tables(
    table_updates: dict,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """批量更新桌台状态"""
    updated_tables = []
    
    for table_id, status in table_updates.items():
        table = db.query(TableModel).filter(TableModel.id == int(table_id)).first()
        if table and table.is_active:
            table.status = status
            table.updated_at = datetime.now()
            updated_tables.append(table)
    
    db.commit()
    
    return {
        "message": f"成功更新 {len(updated_tables)} 个桌台",
        "updated_tables": [table.id for table in updated_tables]
    }

# 新增接口：获取可用桌台（按区域和容量筛选）
@router.get("/tables/available")
async def get_available_tables_filtered(
    area: str = None,
    area_id: int = None,
    min_capacity: int = None,
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取可用桌台，支持按区域和容量筛选"""
    query = db.query(TableModel).filter(
        and_(
            TableModel.is_active == True,
            TableModel.status == "available"
        )
    )
    
    if area:
        query = query.filter(TableModel.area == area)
    
    if area_id:
        query = query.filter(TableModel.area_id == area_id)
    
    if min_capacity:
        query = query.filter(TableModel.capacity >= min_capacity)
    
    available_tables = query.all()
    
    # 为每个桌子添加区域信息
    for table in available_tables:
        if hasattr(table, 'area') and table.area:
            table.area_info = table.area
    
    return available_tables
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from database import get_db
from auth import get_current_active_user
from models.user import User
from models.order import Area as AreaModel
from schemas.area import AreaCreate, AreaUpdate, Area


router = APIRouter()


@router.get("/areas", response_model=list[Area])
async def get_areas(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取区域列表"""
    areas = db.query(AreaModel).filter(AreaModel.is_active == True).offset(skip).limit(limit).all()
    return areas


@router.get("/areas/{area_id}", response_model=Area)
async def get_area(
    area_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取单个区域信息"""
    area = db.query(AreaModel).filter(AreaModel.id == area_id).first()
    if area is None or not area.is_active:
        raise HTTPException(status_code=404, detail="区域不存在")
    return area


@router.post("/areas", response_model=Area)
async def create_area(
    area: AreaCreate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """创建区域"""
    # 检查区域名称是否已存在
    existing_area = db.query(AreaModel).filter(AreaModel.name == area.name).first()
    if existing_area:
        raise HTTPException(status_code=400, detail="区域名称已存在")
    
    db_area = AreaModel(**area.model_dump())
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area


@router.put("/areas/{area_id}", response_model=Area)
async def update_area(
    area_id: int, 
    area_update: AreaUpdate, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """更新区域信息"""
    db_area = db.query(AreaModel).filter(AreaModel.id == area_id).first()
    if db_area is None:
        raise HTTPException(status_code=404, detail="区域不存在")
    
    # 检查名称是否与其他区域冲突
    if area_update.name is not None:
        existing_area = db.query(AreaModel).filter(
            AreaModel.name == area_update.name,
            AreaModel.id != area_id
        ).first()
        if existing_area:
            raise HTTPException(status_code=400, detail="区域名称已存在")
    
    # 更新字段
    update_data = area_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_area, field, value)
    
    db.commit()
    db.refresh(db_area)
    return db_area


@router.delete("/areas/{area_id}")
async def delete_area(
    area_id: int, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """删除区域（逻辑删除）"""
    db_area = db.query(AreaModel).filter(AreaModel.id == area_id).first()
    if db_area is None:
        raise HTTPException(status_code=404, detail="区域不存在")
    
    # 检查区域下是否有桌台
    from models.order import Table as TableModel
    tables_in_area = db.query(TableModel).filter(
        TableModel.area_id == area_id,
        TableModel.is_active == True
    ).count()
    
    if tables_in_area > 0:
        raise HTTPException(status_code=400, detail="区域下还有桌台，无法删除")
    
    # 逻辑删除（将is_active设为False）
    db_area.is_active = False
    db.commit()
    return {"message": "区域已禁用"}


@router.get("/areas/stats")
async def get_area_stats(
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """获取区域统计信息"""
    total_areas = db.query(AreaModel).filter(AreaModel.is_active == True).count()
    active_areas = db.query(AreaModel).filter(AreaModel.is_active == True).count()
    
    # 获取每个区域的桌台数量
    from models.order import Table as TableModel
    area_stats = []
    active_areas_list = db.query(AreaModel).filter(AreaModel.is_active == True).all()
    
    for area in active_areas_list:
        table_count = db.query(TableModel).filter(
            TableModel.area_id == area.id,
            TableModel.is_active == True
        ).count()
        area_stats.append({
            "area_id": area.id,
            "area_name": area.name,
            "table_count": table_count
        })
    
    return {
        "total": total_areas,
        "active": active_areas,
        "area_details": area_stats
    }
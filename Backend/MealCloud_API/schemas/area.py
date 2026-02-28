from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AreaBase(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class Area(AreaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
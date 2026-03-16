from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReservationBase(BaseModel):
    table_id: Optional[int] = None
    area_name: Optional[str] = None
    customer_name: str
    customer_phone: str
    party_size: int = 2
    reservation_time: datetime
    notes: Optional[str] = None


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    table_id: Optional[int] = None
    area_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    party_size: Optional[int] = None
    reservation_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Reservation(ReservationBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
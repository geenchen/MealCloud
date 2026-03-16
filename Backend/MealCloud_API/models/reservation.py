from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=True)
    area_name = Column(String, nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    party_size = Column(Integer, default=2)
    reservation_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default='booked')  # booked, arrived, cancelled, completed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    table = relationship('Table')
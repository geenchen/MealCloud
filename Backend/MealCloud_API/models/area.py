from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # 区域名称
    description = Column(Text, nullable=True)  # 区域描述
    sort_order = Column(Integer, default=0)  # 排序
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    tables = relationship("Table", back_populates="area")

    def __repr__(self):
        return f"<Area(id={self.id}, name='{self.name}')>"
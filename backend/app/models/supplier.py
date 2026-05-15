from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100), default="")
    phone = Column(String(50), default="")
    email = Column(String(100), default="")
    wechat = Column(String(100), default="")
    address = Column(Text, default="")
    city = Column(String(100), default="")
    province = Column(String(100), default="")
    country = Column(String(50), default="China")
    website = Column(String(300), default="")
    alibaba_store = Column(String(300), default="")
    rating = Column(Float, default=0.0)  # 0-5
    notes = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

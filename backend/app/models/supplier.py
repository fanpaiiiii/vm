from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100), default="")
    phone = Column(String(50), default="")
    email = Column(String(100), default="")
    wechat = Column(String(50), default="")
    address = Column(String(500), default="")
    city = Column(String(100), default="")
    province = Column(String(100), default="")
    country = Column(String(100), default="China")
    website = Column(String(500), default="")
    alibaba_store = Column(String(500), default="")
    rating = Column(Float, default=0)
    notes = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="supplier", passive_deletes=True)

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), default="")
    description = Column(Text, default="")
    price_cny = Column(Float, default=0.0)
    price_usd = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)  # kg
    length = Column(Float, default=0.0)  # cm
    width = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    min_order_qty = Column(Integer, default=1)
    image_url = Column(String(500), default="")
    status = Column(String(20), default="active")  # active, inactive, draft
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    tags = Column(String(500), default="")
    alibaba_link = Column(String(500), default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

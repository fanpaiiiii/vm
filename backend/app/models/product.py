from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), index=True, nullable=False)
    name = Column(String(200), nullable=False, index=True)
    link_1688 = Column(String(500), default="")
    image_url = Column(String(500), default="")
    spec = Column(String(500), default="")
    box_spec = Column(String(500), default="")
    size_variants = Column(JSON, nullable=True)
    unit_price = Column(Float, default=0.0)
    sample_price = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    description = Column(Text, default="")
    status = Column(String(20), default="active")
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="products")

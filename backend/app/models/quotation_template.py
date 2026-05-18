from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class QuotationTemplate(Base):
    __tablename__ = "quotation_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, default="")
    # Store the full form data as JSON
    company = Column(JSON, nullable=True)  # {name, address, tel, logoUrl}
    buyer_name = Column(String(200), default="")
    attn = Column(String(200), default="")
    quotation_no = Column(String(100), default="")
    dates = Column(String(50), default="")
    valid_dates = Column(String(50), default="")
    currency = Column(String(10), default="USD")
    trade_terms = Column(String(20), default="DDP")
    groups = Column(JSON, nullable=True)  # [{productNo, spec, items, imageUrl}]
    shipping = Column(JSON, nullable=True)  # {method, cost}
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

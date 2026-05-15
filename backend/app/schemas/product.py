from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    sku: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    price_cny: Optional[float] = 0.0
    price_usd: Optional[float] = 0.0
    cost: Optional[float] = 0.0
    weight: Optional[float] = 0.0
    length: Optional[float] = 0.0
    width: Optional[float] = 0.0
    height: Optional[float] = 0.0
    stock: Optional[int] = 0
    min_order_qty: Optional[int] = 1
    image_url: Optional[str] = ""
    status: Optional[str] = "active"
    supplier_id: Optional[int] = None
    tags: Optional[str] = ""
    alibaba_link: Optional[str] = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price_cny: Optional[float] = None
    price_usd: Optional[float] = None
    cost: Optional[float] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    stock: Optional[int] = None
    min_order_qty: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    supplier_id: Optional[int] = None
    tags: Optional[str] = None
    alibaba_link: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    description: str
    price_cny: float
    price_usd: float
    cost: float
    weight: float
    length: float
    width: float
    height: float
    stock: int
    min_order_qty: int
    image_url: str
    status: str
    supplier_id: Optional[int] = None
    tags: str
    alibaba_link: str
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int

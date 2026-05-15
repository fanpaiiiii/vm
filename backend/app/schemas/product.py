from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime


class ProductCreate(BaseModel):
    sku: Optional[str] = None  # 可选，为空时自动生成 FT-XXXX
    name: str  # 必填
    link_1688: Optional[str] = ""
    image_url: Optional[str] = ""
    spec: Optional[str] = ""
    box_spec: Optional[str] = ""
    size_variants: Optional[List[dict]] = None
    unit_price: Optional[float] = 0.0
    sample_price: Optional[float] = 0.0
    shipping_cost: Optional[float] = 0.0
    description: Optional[str] = ""
    status: Optional[str] = "active"
    supplier_id: Optional[int] = None

    @field_validator('supplier_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v == "null" or v == "undefined":
            return None
        return v

    @field_validator('unit_price', 'sample_price', 'shipping_cost', mode='before')
    @classmethod
    def empty_str_to_zero(cls, v):
        if v == "" or v is None:
            return 0.0
        return v


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    link_1688: Optional[str] = None
    image_url: Optional[str] = None
    spec: Optional[str] = None
    box_spec: Optional[str] = None
    size_variants: Optional[List[dict]] = None
    unit_price: Optional[float] = None
    sample_price: Optional[float] = None
    shipping_cost: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None
    supplier_id: Optional[int] = None

    @field_validator('supplier_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v == "null" or v == "undefined":
            return None
        return v

    @field_validator('unit_price', 'sample_price', 'shipping_cost', mode='before')
    @classmethod
    def empty_str_to_none_float(cls, v):
        if v == "" or v == "null" or v == "undefined":
            return None
        return v


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    link_1688: str
    image_url: str
    spec: str
    box_spec: str
    size_variants: Optional[List[dict]] = None
    unit_price: float
    sample_price: float
    shipping_cost: float
    description: str
    status: str
    supplier_id: Optional[int] = None
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

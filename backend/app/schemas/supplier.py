from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    wechat: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    province: Optional[str] = ""
    country: Optional[str] = "China"
    website: Optional[str] = ""
    alibaba_store: Optional[str] = ""
    rating: Optional[float] = 0.0
    notes: Optional[str] = ""


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    wechat: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    alibaba_store: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: str
    phone: str
    email: str
    wechat: str
    address: str
    city: str
    province: str
    country: str
    website: str
    alibaba_store: str
    rating: float
    notes: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    items: List[SupplierResponse]
    total: int
    page: int
    page_size: int

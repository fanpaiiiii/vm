from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
)
from app.utils.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/suppliers", tags=["供货商"])


@router.get("", response_model=SupplierListResponse, summary="获取供货商列表")
async def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Supplier)
    # 非管理员只看自己的数据
    if current_user.role != "admin":
        query = query.filter(Supplier.created_by == current_user.id)
    if keyword:
        query = query.filter(
            Supplier.name.contains(keyword)
            | Supplier.contact_person.contains(keyword)
            | Supplier.city.contains(keyword)
        )
    if is_active is not None and is_active.strip():
        query = query.filter(Supplier.is_active == (is_active.lower() == "true"))

    total = query.count()
    items = query.order_by(Supplier.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return SupplierListResponse(
        items=[SupplierResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{supplier_id}", response_model=SupplierResponse, summary="获取供货商详情")
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供货商不存在")
    if supplier.created_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权查看此供货商')
    return SupplierResponse.model_validate(supplier)


@router.post("", response_model=SupplierResponse, summary="创建供货商")
async def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier = Supplier(**data.model_dump(), created_by=current_user.id)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    logger.info(f"供货商创建: {supplier.name}")
    return SupplierResponse.model_validate(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse, summary="更新供货商")
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供货商不存在")
    if supplier.created_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权操作此供货商')

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    logger.info(f"供货商更新: {supplier.name} (ID: {supplier_id})")
    return SupplierResponse.model_validate(supplier)


@router.delete("/{supplier_id}", summary="删除供货商")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供货商不存在")
    if supplier.created_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权操作此供货商')

    db.delete(supplier)
    db.commit()
    logger.info(f"供货商删除: {supplier.name} (ID: {supplier_id})")
    return {"message": "删除成功"}

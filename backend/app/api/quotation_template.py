"""报价单模板CRUD API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.quotation_template import QuotationTemplate
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/quotation-templates", tags=["报价单模板"])


class TemplateCreate(BaseModel):
    name: str
    description: str = ""
    company: dict = {}
    buyer_name: str = ""
    attn: str = ""
    quotation_no: str = ""
    dates: str = ""
    valid_dates: str = ""
    currency: str = "USD"
    trade_terms: str = "DDP"
    groups: list = []
    shipping: dict = {}


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company: Optional[dict] = None
    buyer_name: Optional[str] = None
    attn: Optional[str] = None
    quotation_no: Optional[str] = None
    dates: Optional[str] = None
    valid_dates: Optional[str] = None
    currency: Optional[str] = None
    trade_terms: Optional[str] = None
    groups: Optional[list] = None
    shipping: Optional[dict] = None


@router.get("/", summary="获取模板列表")
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(QuotationTemplate)
    # 非管理员只看自己的数据
    if current_user.role != "admin":
        query = query.filter(QuotationTemplate.created_by == current_user.id)
    total = query.count()
    templates = (
        query.order_by(QuotationTemplate.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "items": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in templates
        ]
    }


@router.get("/{template_id}", summary="获取模板详情")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = db.query(QuotationTemplate).filter(QuotationTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    if t.created_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权查看此模板')
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "company": t.company or {},
        "buyer_name": t.buyer_name or "",
        "attn": t.attn or "",
        "quotation_no": t.quotation_no or "",
        "dates": t.dates or "",
        "valid_dates": t.valid_dates or "",
        "currency": t.currency or "USD",
        "trade_terms": t.trade_terms or "DDP",
        "groups": t.groups or [],
        "shipping": t.shipping or {},
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.post("/", summary="保存新模板")
async def create_template(
    data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = QuotationTemplate(
        name=data.name,
        description=data.description,
        company=data.company,
        buyer_name=data.buyer_name,
        attn=data.attn,
        quotation_no=data.quotation_no,
        dates=data.dates,
        valid_dates=data.valid_dates,
        currency=data.currency,
        trade_terms=data.trade_terms,
        groups=data.groups,
        shipping=data.shipping,
        created_by=current_user.id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "name": t.name, "message": "Template saved"}


@router.put("/{template_id}", summary="更新模板")
async def update_template(
    template_id: int,
    data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = db.query(QuotationTemplate).filter(QuotationTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    if t.created_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权操作此模板')

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(t, key, value)

    db.commit()
    return {"id": t.id, "name": t.name, "message": "Template updated"}


@router.delete("/{template_id}", summary="删除模板")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = db.query(QuotationTemplate).filter(QuotationTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    if t.created_by != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='无权操作此模板')
    db.delete(t)
    db.commit()
    return {"message": "Template deleted"}

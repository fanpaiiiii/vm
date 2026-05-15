import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.utils.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/products", tags=["产品"])


@router.get("", response_model=ProductListResponse, summary="获取产品列表")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)

    if keyword:
        query = query.filter(
            or_(
                Product.name.contains(keyword),
                Product.sku.contains(keyword),
                Product.description.contains(keyword),
            )
        )
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)
    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)

    total = query.count()

    # Sorting
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/categories", summary="获取所有产品分类")
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = (
        db.query(Product.category)
        .filter(Product.category != "")
        .distinct()
        .all()
    )
    return [c[0] for c in categories]


@router.get("/{product_id}", response_model=ProductResponse, summary="获取产品详情")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, summary="创建产品")
async def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=400, detail=f"SKU '{data.sku}' 已存在")

    product = Product(**data.model_dump(), created_by=current_user.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"产品创建: {product.name} (SKU: {product.sku})")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse, summary="更新产品")
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    logger.info(f"产品更新: {product.name} (ID: {product_id})")
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", summary="删除产品")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    db.delete(product)
    db.commit()
    logger.info(f"产品删除: {product.name} (ID: {product_id})")
    return {"message": "删除成功"}


@router.post("/import", summary="批量导入产品 (CSV)")
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")

    content = await file.read()
    # Try UTF-8 BOM, then GBK
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("gbk")

    reader = csv.DictReader(io.StringIO(text))
    created = 0
    errors = []

    for i, row in enumerate(reader, 1):
        try:
            sku = row.get("sku", "").strip()
            if not sku:
                errors.append(f"第{i}行: SKU为空")
                continue
            if db.query(Product).filter(Product.sku == sku).first():
                errors.append(f"第{i}行: SKU '{sku}' 已存在")
                continue

            product = Product(
                name=row.get("name", ""),
                sku=sku,
                category=row.get("category", ""),
                description=row.get("description", ""),
                price_cny=float(row.get("price_cny", 0)),
                price_usd=float(row.get("price_usd", 0)),
                cost=float(row.get("cost", 0)),
                weight=float(row.get("weight", 0)),
                stock=int(row.get("stock", 0)),
                min_order_qty=int(row.get("min_order_qty", 1)),
                status=row.get("status", "active"),
                created_by=current_user.id,
            )
            db.add(product)
            created += 1
        except Exception as e:
            errors.append(f"第{i}行: {str(e)}")

    db.commit()
    logger.info(f"批量导入: 成功 {created} 条, 失败 {len(errors)} 条")
    return {"created": created, "errors": errors}


@router.get("/export/csv", summary="导出产品为CSV")
async def export_products(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)

    products = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "sku", "name", "category", "price_cny", "price_usd", "cost",
        "weight", "stock", "min_order_qty", "status", "supplier_id",
    ])
    for p in products:
        writer.writerow([
            p.sku, p.name, p.category, p.price_cny, p.price_usd, p.cost,
            p.weight, p.stock, p.min_order_qty, p.status, p.supplier_id or "",
        ])

    output.seek(0)
    logger.info(f"产品导出: {len(products)} 条")
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )

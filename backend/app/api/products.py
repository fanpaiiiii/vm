import io
import csv
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func as sql_func
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


import threading
_sku_lock = threading.Lock()
from sqlalchemy import text
def generate_next_sku(db: Session) -> str:
    """自动生成下一个 FT-XXXX 格式的 SKU"""
    # 使用线程锁防止并发重复（SQLite不支持FOR UPDATE）
    with _sku_lock:
        result = db.execute(
            text("SELECT sku FROM products WHERE sku LIKE 'FT-%' ORDER BY CAST(SUBSTR(sku, 4) AS INTEGER) DESC LIMIT 1")
        ).fetchone()
        if result:
            match = re.match(r"FT-(\d+)", result[0])
            max_num = int(match.group(1)) if match else 0
        else:
            max_num = 0
    return f"FT-{max_num + 1:04d}"


@router.get("", response_model=ProductListResponse, summary="获取产品列表")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    supplier_id: Optional[str] = Query(None),
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
    if status:
        query = query.filter(Product.status == status)
    if supplier_id and supplier_id.strip():
        try:
            query = query.filter(Product.supplier_id == int(supplier_id))
        except ValueError:
            pass

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
    # 自动生成 SKU
    sku = data.sku if data.sku and data.sku.strip() else generate_next_sku(db)

    product_data = data.model_dump(exclude={"sku"})
    product = Product(**product_data, sku=sku, created_by=current_user.id)
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
                sku = generate_next_sku(db)

            product = Product(
                sku=sku,
                name=row.get("name", ""),
                link_1688=row.get("link_1688", ""),
                image_url=row.get("image_url", ""),
                spec=row.get("spec", ""),
                box_spec=row.get("box_spec", ""),
                size_variants=json.loads(row.get("size_variants", "null")) if row.get("size_variants") else None,
                unit_price=float(row.get("unit_price", 0)),
                sample_price=float(row.get("sample_price", 0)),
                shipping_cost=float(row.get("shipping_cost", 0)),
                description=row.get("description", ""),
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
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)
    if status:
        query = query.filter(Product.status == status)

    def generate_csv():
        header = [
            "sku", "name", "link_1688", "image_url", "spec", "box_spec",
            "size_variants", "unit_price", "sample_price", "shipping_cost",
            "description", "status", "supplier_id",
        ]
        yield "\ufeff" + ",".join(header) + "\n"
        count = 0
        for p in query.yield_per(100):
            row = [
                p.sku, p.name, p.link_1688, p.image_url, p.spec, p.box_spec,
                json.dumps(p.size_variants, ensure_ascii=False) if p.size_variants else "",
                str(p.unit_price), str(p.sample_price), str(p.shipping_cost),
                p.description, p.status, str(p.supplier_id or ""),
            ]
            yield ",".join(f'"{v}"' for v in row) + "\n"
            count += 1
        logger.info(f"产品导出: {count} 条")

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )

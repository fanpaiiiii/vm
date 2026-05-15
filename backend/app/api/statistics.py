from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/statistics", tags=["统计"])


@router.get("/dashboard", summary="获取仪表盘统计数据")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Combined query for total_products, active_products, and total_value
    stats = db.query(
        func.count(Product.id).label('total'),
        func.count(case((Product.status == 'active', 1))).label('active'),
        func.coalesce(func.sum(Product.unit_price), 0).label('total_value'),
    ).first()
    total_products = stats.total
    active_products = stats.active
    total_value_cny = round(float(stats.total_value or 0), 2)
    total_suppliers = db.query(Supplier).filter(Supplier.is_active == True).count()

    # 按状态统计
    statuses = (
        db.query(Product.status, func.count(Product.id))
        .group_by(Product.status)
        .all()
    )

    # 按供货商统计产品数量（top 10）
    supplier_dist = (
        db.query(Supplier.name, func.count(Product.id))
        .outerjoin(Product, Product.supplier_id == Supplier.id)
        .group_by(Supplier.id)
        .order_by(func.count(Product.id).desc())
        .limit(10)
        .all()
    )

    return {
        "overview": {
            "total_products": total_products,
            "active_products": active_products,
            "total_suppliers": total_suppliers,
            "total_stock": 0,
            "total_value_cny": total_value_cny,
            "total_value_usd": 0,
        },
        "stock_alerts": {
            "low_stock": 0,
            "out_of_stock": 0,
        },
        "category_distribution": [
            {"category": s[0] or "未分配", "count": s[1]} for s in supplier_dist
        ],
        "status_distribution": [
            {"status": s[0], "count": s[1]} for s in statuses
        ],
    }

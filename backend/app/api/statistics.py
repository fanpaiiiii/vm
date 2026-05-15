from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.status == "active").count()
    total_suppliers = db.query(Supplier).filter(Supplier.is_active == True).count()
    total_stock = db.query(func.coalesce(func.sum(Product.stock), 0)).scalar()
    total_value_cny = db.query(
        func.coalesce(func.sum(Product.price_cny * Product.stock), 0)
    ).scalar()
    total_value_usd = db.query(
        func.coalesce(func.sum(Product.price_usd * Product.stock), 0)
    ).scalar()

    # Category distribution
    categories = (
        db.query(Product.category, func.count(Product.id))
        .filter(Product.category != "")
        .group_by(Product.category)
        .all()
    )

    # Low stock products (stock < 10)
    low_stock_count = db.query(Product).filter(Product.stock < 10, Product.stock > 0).count()
    out_of_stock = db.query(Product).filter(Product.stock == 0).count()

    # Status distribution
    statuses = (
        db.query(Product.status, func.count(Product.id))
        .group_by(Product.status)
        .all()
    )

    return {
        "overview": {
            "total_products": total_products,
            "active_products": active_products,
            "total_suppliers": total_suppliers,
            "total_stock": total_stock,
            "total_value_cny": round(total_value_cny, 2),
            "total_value_usd": round(total_value_usd, 2),
        },
        "stock_alerts": {
            "low_stock": low_stock_count,
            "out_of_stock": out_of_stock,
        },
        "category_distribution": [
            {"category": c[0], "count": c[1]} for c in categories
        ],
        "status_distribution": [
            {"status": s[0], "count": s[1]} for s in statuses
        ],
    }

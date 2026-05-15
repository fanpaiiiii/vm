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

    # 按状态统计
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
            "total_stock": 0,
            "total_value_cny": 0,
            "total_value_usd": 0,
        },
        "stock_alerts": {
            "low_stock": 0,
            "out_of_stock": 0,
        },
        "category_distribution": [],
        "status_distribution": [
            {"status": s[0], "count": s[1]} for s in statuses
        ],
    }

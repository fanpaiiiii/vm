import httpx
from fastapi import APIRouter, Depends, Query
from app.config import settings
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/exchange-rate", tags=["汇率"])

# Cache for exchange rates
_cache = {"data": None, "timestamp": 0}


@router.get("", summary="获取实时汇率")
async def get_exchange_rate(
    base: str = Query("CNY", description="基础货币"),
    target: str = Query("USD", description="目标货币"),
    current_user: User = Depends(get_current_user),
):
    """通过 Frankfurter API 获取实时汇率 (基于ECB数据，完全免费)"""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                f"{settings.FRANKFURTER_API_URL}/latest",
                params={"from": base.upper(), "to": target.upper()},
            )
            resp.raise_for_status()
            data = resp.json()

        logger.info(f"汇率查询: {base} -> {target}")
        return {
            "base": data.get("base"),
            "target": target.upper(),
            "rate": data.get("rates", {}).get(target.upper()),
            "date": data.get("date"),
            "source": "Frankfurter (ECB)",
        }
    except httpx.HTTPError as e:
        logger.error(f"汇率API请求失败: {e}")
        # Fallback rates (approximate)
        fallback = {
            ("CNY", "USD"): 0.147,
            ("USD", "CNY"): 6.79,
            ("CNY", "EUR"): 0.126,
            ("EUR", "CNY"): 7.94,
            ("USD", "EUR"): 0.85,
            ("EUR", "USD"): 1.17,
        }
        rate = fallback.get((base.upper(), target.upper()), 1.0)
        return {
            "base": base.upper(),
            "target": target.upper(),
            "rate": rate,
            "date": "fallback",
            "source": "Fallback (离线数据)",
        }


@router.get("/multi", summary="获取多币种汇率")
async def get_multi_rates(
    base: str = Query("CNY", description="基础货币"),
    targets: str = Query("USD,EUR,GBP,JPY", description="目标货币，逗号分隔"),
    current_user: User = Depends(get_current_user),
):
    """一次获取多个币种的汇率"""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                f"{settings.FRANKFURTER_API_URL}/latest",
                params={"from": base.upper(), "to": targets.upper()},
            )
            resp.raise_for_status()
            data = resp.json()

        return {
            "base": data.get("base"),
            "date": data.get("date"),
            "rates": data.get("rates", {}),
            "source": "Frankfurter (ECB)",
        }
    except httpx.HTTPError as e:
        logger.error(f"汇率API请求失败: {e}")
        return {"base": base.upper(), "date": "error", "rates": {}, "source": "Error"}

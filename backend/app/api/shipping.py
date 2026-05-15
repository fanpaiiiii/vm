from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/shipping", tags=["运费计算"])


class ShippingRequest(BaseModel):
    weight_kg: float  # 包裹重量(kg)
    length_cm: Optional[float] = 0  # 长(cm)
    width_cm: Optional[float] = 0   # 宽(cm)
    height_cm: Optional[float] = 0  # 高(cm)
    origin: str = "CN"  # 发货国
    destination: str = "US"  # 目的国
    quantity: int = 1


class ShippingOption(BaseModel):
    carrier: str
    service: str
    estimated_days: str
    cost_usd: float
    cost_cny: float
    notes: str


class ShippingResponse(BaseModel):
    options: list[ShippingOption]
    weight_kg: float
    volume_weight_kg: float
    chargeable_weight_kg: float


# Shipping rate tables (simplified for demo)
SHIPPING_RATES = {
    # (origin, destination): {carrier: rate_per_kg_usd}
    ("CN", "US"): {
        "DHL": {"rate": 8.5, "days": "5-7", "service": "DHL Express"},
        "FedEx": {"rate": 9.0, "days": "4-6", "service": "FedEx International Priority"},
        "UPS": {"rate": 8.8, "days": "5-8", "service": "UPS Worldwide Express"},
        "EMS": {"rate": 5.5, "days": "10-15", "service": "EMS国际特快"},
        "ePacket": {"rate": 3.5, "days": "15-30", "service": "ePacket经济小包"},
        "海运": {"rate": 1.2, "days": "25-40", "service": "海运拼箱"},
    },
    ("CN", "EU"): {
        "DHL": {"rate": 9.0, "days": "5-8", "service": "DHL Express"},
        "FedEx": {"rate": 9.5, "days": "5-7", "service": "FedEx International Priority"},
        "EMS": {"rate": 6.0, "days": "10-20", "service": "EMS国际特快"},
        "铁路": {"rate": 2.5, "days": "18-25", "service": "中欧班列"},
        "海运": {"rate": 1.0, "days": "30-45", "service": "海运拼箱"},
    },
    ("CN", "UK"): {
        "DHL": {"rate": 9.2, "days": "5-8", "service": "DHL Express"},
        "Royal Mail": {"rate": 5.0, "days": "10-18", "service": "Royal Mail International"},
        "EMS": {"rate": 6.0, "days": "10-15", "service": "EMS国际特快"},
    },
}

# Default rate for unknown routes
DEFAULT_RATE = {"DHL": {"rate": 10.0, "days": "7-10", "service": "DHL Express"}}


@router.post("/calculate", response_model=ShippingResponse, summary="计算运费")
async def calculate_shipping(
    req: ShippingRequest,
    current_user: User = Depends(get_current_user),
):
    """基于重量和体积计算各物流渠道的运费"""

    # Volume weight: L*W*H / 5000 (国际标准)
    vol_weight = 0
    if req.length_cm > 0 and req.width_cm > 0 and req.height_cm > 0:
        vol_weight = (req.length_cm * req.width_cm * req.height_cm) / 5000

    # Chargeable weight = max(actual weight, volume weight)
    chargeable = max(req.weight_kg, vol_weight)

    # Find route
    route_key = (req.origin.upper(), req.destination.upper())
    # Try direct match, then region mapping
    if route_key not in SHIPPING_RATES:
        # Map country codes to regions
        eu_countries = {"DE", "FR", "IT", "ES", "NL", "BE", "AT", "PL", "SE", "DK", "FI", "PT", "IE", "GR", "CZ", "RO", "HU"}
        if req.destination.upper() in eu_countries:
            route_key = (req.origin.upper(), "EU")

    rates = SHIPPING_RATES.get(route_key, DEFAULT_RATE)

    options = []
    for carrier, info in rates.items():
        # Minimum charge: 0.5kg
        billable_weight = max(chargeable, 0.5) * req.quantity
        cost_usd = round(billable_weight * info["rate"], 2)
        cost_cny = round(cost_usd * 7.25, 2)  # Approximate USD->CNY

        options.append(ShippingOption(
            carrier=carrier,
            service=info["service"],
            estimated_days=info["days"],
            cost_usd=cost_usd,
            cost_cny=cost_cny,
            notes=f"计费重量: {billable_weight:.1f}kg",
        ))

    # Sort by cost
    options.sort(key=lambda x: x.cost_usd)

    return ShippingResponse(
        options=options,
        weight_kg=req.weight_kg,
        volume_weight_kg=round(vol_weight, 2),
        chargeable_weight_kg=round(chargeable, 2),
    )


@router.get("/routes", summary="获取支持的物流线路")
async def get_routes(current_user: User = Depends(get_current_user)):
    """返回所有支持的物流线路"""
    routes = []
    for (origin, dest), carriers in SHIPPING_RATES.items():
        routes.append({
            "origin": origin,
            "destination": dest,
            "carriers": list(carriers.keys()),
        })
    return routes

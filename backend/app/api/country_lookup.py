"""
Country lookup API endpoints.

Provides search, detail, cities, postal code lookup, and region summary.
All endpoints require JWT authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.country_service import country_service

router = APIRouter(prefix="/api/country", tags=["国家查询"])


# ------------------------------------------------------------------
# Response models
# ------------------------------------------------------------------
class CountrySummary(BaseModel):
    iso2: str
    iso3: str
    name_cn: str
    name_en: str
    region: str
    capital: str
    currency: Optional[str] = None
    phone_code: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: list[CountrySummary]
    total: int


class RegionItem(BaseModel):
    name: str
    count: int


class RegionsResponse(BaseModel):
    regions: list[RegionItem]


class CitiesResponse(BaseModel):
    iso2: str
    cities: list[str]
    total: int


class PostalCodeResponse(BaseModel):
    iso2: str
    postal_code: str
    data: Optional[dict] = None


class ShippingMethodItem(BaseModel):
    carrier: str
    method: Optional[str] = None
    transit_days_min: Optional[int] = None
    transit_days_max: Optional[int] = None
    cost_reference: Optional[str] = None
    source: Optional[str] = None


class ShippingUpdateRequest(BaseModel):
    methods: Optional[list[ShippingMethodItem]] = None
    available: Optional[bool] = None
    customs_clearance_days: Optional[int] = None
    remote_area_surcharge: Optional[str] = None


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.get("/search", response_model=SearchResponse, summary="搜索国家")
async def search_countries(
    q: str = Query(..., min_length=1, description="搜索关键词（国家名/ISO代码/城市/邮编）"),
    current_user: User = Depends(get_current_user),
):
    """
    Search countries by name (Chinese/English), ISO code, city, or postal code.
    """
    results = await country_service.search_country(q)
    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
    )


@router.get("/regions", response_model=RegionsResponse, summary="获取地区列表")
async def get_regions(
    current_user: User = Depends(get_current_user),
):
    """Get all regions with country counts."""
    data = await country_service.get_regions()
    return RegionsResponse(**data)


@router.get("/all", summary="获取所有国家摘要")
async def get_all_countries(
    current_user: User = Depends(get_current_user),
):
    """Lightweight summary list of all countries (name/code/region)."""
    results = await country_service.get_all_summary()
    return {"countries": results, "total": len(results)}


@router.get("/{iso2}", summary="获取国家详情")
async def get_country_detail(
    iso2: str,
    current_user: User = Depends(get_current_user),
):
    """Get full country detail with live API enrichment."""
    detail = await country_service.get_country_detail(iso2)
    if not detail:
        raise HTTPException(status_code=404, detail=f"未找到国家: {iso2}")
    return detail


@router.get("/{iso2}/cities", response_model=CitiesResponse, summary="获取城市列表")
async def get_cities(
    iso2: str,
    current_user: User = Depends(get_current_user),
):
    """Get cities for a country (from CountriesNow API)."""
    cities = await country_service.get_cities(iso2)
    if not cities:
        # Could be invalid iso2 or API failure — return empty rather than 404
        detail = await country_service.get_country_detail(iso2)
        if not detail:
            raise HTTPException(status_code=404, detail=f"未找到国家: {iso2}")
    return CitiesResponse(iso2=iso2.upper(), cities=cities, total=len(cities))


@router.get("/{iso2}/postal/{postal_code}", response_model=PostalCodeResponse, summary="邮编查询")
async def lookup_postal_code(
    iso2: str,
    postal_code: str,
    current_user: User = Depends(get_current_user),
):
    """Lookup postal code (from Zippopotam.us)."""
    data = await country_service.lookup_postal_code(iso2, postal_code)
    return PostalCodeResponse(iso2=iso2.upper(), postal_code=postal_code, data=data)


@router.put("/{iso2}/shipping", summary="更新国家物流方式")
async def update_shipping_methods(
    iso2: str,
    shipping_data: ShippingUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update shipping methods for a country. Requires admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    result = await country_service.update_shipping(iso2, shipping_data.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail=f"国家 {iso2} 不存在")
    return {"message": "更新成功", "iso2": iso2.upper()}

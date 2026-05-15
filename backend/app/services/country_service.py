"""
Country lookup service with external API integration and caching.

Integrates:
- Local trade_db.json (country master data)
- REST Countries API (enrichment)
- CountriesNow API (cities)
- Zippopotam.us (postal code lookup)
"""
import json
import os
import time
import asyncio
from typing import Optional
import httpx
from app.utils.logger import logger


# Cache TTLs (seconds)
CACHE_TTL = 86400  # 24 hours

# Country name to ISO2 mapping for CountriesNow API
_NAME_TO_ISO2 = {}


class _CacheEntry:
    """Simple cache entry with TTL."""
    __slots__ = ("data", "expires_at")

    def __init__(self, data, ttl: int = CACHE_TTL):
        self.data = data
        self.expires_at = time.time() + ttl

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at


class CountryService:
    """Country lookup service with lazy-loaded local data and cached API calls."""

    def __init__(self):
        self._trade_db: Optional[dict] = None
        self._restcountries_cache: dict[str, _CacheEntry] = {}
        self._cities_cache: dict[str, _CacheEntry] = {}
        self._postal_cache: dict[str, _CacheEntry] = {}  # key: "{iso2}:{postal}"
        self._city_index: Optional[dict[str, list[str]]] = None  # city_lower -> [iso2, ...]

    # ------------------------------------------------------------------
    # Lazy data loading
    # ------------------------------------------------------------------
    def _load_trade_db(self) -> dict:
        if self._trade_db is not None:
            return self._trade_db
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "trade_db.json")
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                self._trade_db = json.load(f)
            logger.info(f"Loaded trade_db.json: {len(self._trade_db)} countries")
        except Exception as e:
            logger.error(f"Failed to load trade_db.json: {e}")
            self._trade_db = {}
        return self._trade_db

    def _build_city_index(self) -> dict[str, list[str]]:
        """Build reverse index: city_name_lower -> [iso2, ...] from local DB major_cities."""
        if self._city_index is not None:
            return self._city_index
        db = self._load_trade_db()
        idx: dict[str, list[str]] = {}
        for iso2, country in db.items():
            for city in country.get("business", {}).get("major_cities", []):
                key = city.lower()
                if key not in idx:
                    idx[key] = []
                idx[key].append(iso2)
            # Also index capital
            cap = country.get("capital", "")
            if cap:
                key = cap.lower()
                if key not in idx:
                    idx[key] = []
                if iso2 not in idx[key]:
                    idx[key].append(iso2)
        self._city_index = idx
        return idx

    # ------------------------------------------------------------------
    # Search (local first, then API fallback)
    # ------------------------------------------------------------------
    async def search_country(self, query: str) -> list[dict]:
        """Search countries by name (Chinese/English), ISO code, city, or postal code."""
        db = self._load_trade_db()
        q = query.strip().lower()
        if not q:
            return []

        # 1. Match by ISO code or country name (fast, local)
        exact = []
        partial = []
        for iso2, country in db.items():
            iso2l = iso2.lower()
            iso3l = country.get("iso3", "").lower()
            name_cn = country.get("name_cn", "").lower()
            name_en = country.get("name_en", "").lower()
            cap = country.get("capital", "").lower()
            cap_en = country.get("capital_en", "").lower()

            # Exact matches (highest priority)
            if q == iso2l or q == iso3l or q == name_cn or q == name_en or q == cap or q == cap_en:
                exact.append(self._summary(country))
            elif q in name_cn or q in name_en or q in iso2l or q in iso3l or q in cap or q in cap_en:
                partial.append(self._summary(country))

        results = exact + partial

        if results:
            return results

        # 2. Search by city (local index first, no API calls)
        city_idx = self._build_city_index()
        matched_iso2s = set()
        for city_name, iso2s in city_idx.items():
            if q in city_name:
                matched_iso2s.update(iso2s)
        if matched_iso2s:
            return [self._summary(db[iso2]) for iso2 in matched_iso2s if iso2 in db]

        # 3. Search by postal code (try common countries only, not all 250)
        # Postal code patterns: US(5digit), CN(6digit), GB(alphanumeric), DE(5digit), JP(7digit), etc.
        if q.replace(" ", "").replace("-", "").isalnum() and len(q) >= 3:
            postal_results = await self._smart_postal_search(q)
            if postal_results:
                return postal_results

        return []

    async def _smart_postal_search(self, code: str) -> list[dict]:
        """Smart postal code search - try likely countries based on code format."""
        db = self._load_trade_db()
        clean = code.replace(" ", "").replace("-", "")

        # Determine likely countries by postal code format
        candidates = []
        if clean.isdigit():
            if len(clean) == 5:
                candidates = ["US", "DE", "FR", "IT", "ES", "NL", "BR", "MX", "AR"]
            elif len(clean) == 6:
                candidates = ["CN", "IN", "RU", "KR"]
            elif len(clean) == 7:
                candidates = ["JP"]
            elif len(clean) == 4:
                candidates = ["AU", "AT", "BE", "CH", "SE", "NO", "DK"]
        else:
            # Alphanumeric - likely UK, Canada, etc.
            candidates = ["GB", "CA"]

        results = []
        for iso2 in candidates:
            if iso2 not in db:
                continue
            data = await self.lookup_postal_code(iso2, code)
            if data and data.get("places"):
                results.append(self._summary(db[iso2]))

        return results

    # ------------------------------------------------------------------
    # Country detail
    # ------------------------------------------------------------------
    async def get_country_detail(self, iso2: str) -> Optional[dict]:
        """Get full country detail from trade_db + live API enrichment."""
        db = self._load_trade_db()
        iso2_upper = iso2.upper()
        local = db.get(iso2_upper)
        if not local:
            return None

        result = dict(local)

        # Inject unavailable shipping methods
        ALL_CARRIERS = ["DHL", "FedEx", "UPS", "EMS", "ePacket", "海运", "铁路"]
        shipping = result.get("shipping", {})
        available_carriers = {m.get("carrier") for m in shipping.get("methods", [])}
        shipping["unavailable_methods"] = [
            c for c in ALL_CARRIERS if c not in available_carriers
        ]

        # Enrich with REST Countries API (non-blocking, best effort)
        enrichment = await self._fetch_restcountries(iso2_upper)
        if enrichment:
            result["flag_emoji"] = enrichment.get("flag", "")
            result["flag_url"] = enrichment.get("flags", {}).get("png", "")
            result["maps_url"] = enrichment.get("maps", {}).get("googleMaps", "")
            result["timezones"] = enrichment.get("timezones", [])
            result["borders"] = enrichment.get("borders", [])
            result["un_member"] = enrichment.get("unMember", None)

        return result

    # ------------------------------------------------------------------
    # Cities (cached API call)
    # ------------------------------------------------------------------
    async def get_cities(self, iso2: str) -> list[str]:
        """Get cities for a country from local DB major_cities + CountriesNow API."""
        iso2_upper = iso2.upper()
        db = self._load_trade_db()
        country_info = db.get(iso2_upper)
        if not country_info:
            return []

        # Check cache first
        cached = self._cities_cache.get(iso2_upper)
        if cached and not cached.expired:
            return cached.data

        # Try API
        country_name = country_info.get("name_en", "")
        cities = await self._fetch_cities_from_api(country_name)
        if cities:
            self._cities_cache[iso2_upper] = _CacheEntry(cities)
            return cities

        # Fallback to local major_cities
        local_cities = country_info.get("business", {}).get("major_cities", [])
        return local_cities

    # ------------------------------------------------------------------
    # Postal code lookup
    # ------------------------------------------------------------------
    async def lookup_postal_code(self, iso2: str, postal_code: str) -> Optional[dict]:
        """Lookup postal code from Zippopotam.us."""
        iso2_lower = iso2.lower()
        cache_key = f"{iso2_lower}:{postal_code}"

        cached = self._postal_cache.get(cache_key)
        if cached and not cached.expired:
            return cached.data

        result = await self._fetch_postal_code(iso2_lower, postal_code)
        if result is not None:
            self._postal_cache[cache_key] = _CacheEntry(result)
            return result

        return None

    # ------------------------------------------------------------------
    # Update shipping methods
    # ------------------------------------------------------------------
    async def update_shipping(self, iso2: str, shipping_data: dict) -> bool:
        """Update shipping methods for a country in trade_db.json."""
        iso2_upper = iso2.upper()
        db = self._load_trade_db()
        
        if iso2_upper not in db:
            return False
        
        # Update shipping data
        if 'shipping' not in db[iso2_upper]:
            db[iso2_upper]['shipping'] = {}
        
        # Update methods
        if 'methods' in shipping_data:
            for method in shipping_data['methods']:
                method['source'] = 'manual'  # Mark as manually updated
            db[iso2_upper]['shipping']['methods'] = shipping_data['methods']
        
        # Update other fields
        for key in ['available', 'customs_clearance_days', 'remote_area_surcharge']:
            if key in shipping_data:
                db[iso2_upper]['shipping'][key] = shipping_data[key]
        
        # Update timestamp
        from datetime import datetime
        db[iso2_upper]['shipping']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Recalculate unavailable methods
        ALL_CARRIERS = ["DHL", "FedEx", "UPS", "EMS", "ePacket", "海运", "铁路"]
        available_carriers = {m.get('carrier') for m in db[iso2_upper]['shipping'].get('methods', [])}
        db[iso2_upper]['shipping']['unavailable_methods'] = [
            c for c in ALL_CARRIERS if c not in available_carriers
        ]
        
        # Save to file
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "trade_db.json")
        try:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            # Update in-memory cache
            self._trade_db = db
            return True
        except Exception as e:
            logger.error(f"Failed to save trade_db.json: {e}")
            return False

    # ------------------------------------------------------------------
    # Regions summary
    # ------------------------------------------------------------------
    async def get_regions(self) -> dict:
        """Get all regions with country counts."""
        db = self._load_trade_db()
        regions: dict[str, int] = {}
        for country in db.values():
            region = country.get("region", "未知")
            regions[region] = regions.get(region, 0) + 1
        return {"regions": [{"name": k, "count": v} for k, v in sorted(regions.items())]}

    # ------------------------------------------------------------------
    # All countries summary
    # ------------------------------------------------------------------
    async def get_all_summary(self) -> list[dict]:
        """Lightweight summary of all countries."""
        db = self._load_trade_db()
        return [self._summary(c) for c in db.values()]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _summary(self, country: dict) -> dict:
        """Create a lightweight summary from a country record."""
        return {
            "iso2": country.get("iso2"),
            "iso3": country.get("iso3"),
            "name_cn": country.get("name_cn"),
            "name_en": country.get("name_en"),
            "region": country.get("region"),
            "capital": country.get("capital"),
            "currency": country.get("currency"),
            "phone_code": country.get("phone_code"),
        }

    async def _fetch_restcountries(self, iso2: str) -> Optional[dict]:
        """Fetch country data from REST Countries API."""
        cached = self._restcountries_cache.get(iso2)
        if cached and not cached.expired:
            return cached.data

        # Must include fields param or API returns 400
        url = f"https://restcountries.com/v3.1/alpha/{iso2}?fields=flag,flags,maps,timezones,borders,unMember"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    result = data[0] if isinstance(data, list) and data else data
                    self._restcountries_cache[iso2] = _CacheEntry(result)
                    return result
                else:
                    logger.warning(f"REST Countries API returned {resp.status_code} for {iso2}")
        except Exception as e:
            logger.warning(f"REST Countries API failed for {iso2}: {e}")
        return None

    async def _fetch_cities_from_api(self, country_name: str) -> Optional[list[str]]:
        """Fetch cities from CountriesNow API."""
        url = "https://countriesnow.space/api/v0.1/countries/cities"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, json={"country": country_name})
                if resp.status_code == 200:
                    data = resp.json()
                    cities = data.get("data", [])
                    if isinstance(cities, list):
                        return cities
                else:
                    logger.warning(f"CountriesNow API returned {resp.status_code} for {country_name}")
        except Exception as e:
            logger.warning(f"CountriesNow API failed for {country_name}: {e}")
        return None

    async def _fetch_postal_code(self, iso2_lower: str, postal_code: str) -> Optional[dict]:
        """Fetch postal code data from Zippopotam.us."""
        url = f"https://api.zippopotam.us/{iso2_lower}/{postal_code}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 404:
                    return None
                else:
                    logger.warning(f"Zippopotam API returned {resp.status_code} for {iso2_lower}/{postal_code}")
        except Exception as e:
            logger.warning(f"Zippopotam API failed for {iso2_lower}/{postal_code}: {e}")
        return None


# Singleton instance
country_service = CountryService()

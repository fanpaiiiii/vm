import collections
import threading
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/exchange-rate", tags=["汇率"])

# 汇率缓存（10分钟，LRU限制最多20个key）
class LRUCache:
    def __init__(self, maxsize: int = 20, ttl: int = 600):
        self._cache: collections.OrderedDict = collections.OrderedDict()
        self._maxsize = maxsize
        self._ttl = ttl
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            if key in self._cache:
                value, ts = self._cache[key]
                if time.time() - ts < self._ttl:
                    self._cache.move_to_end(key)
                    return value
                else:
                    del self._cache[key]
            return None

    def set(self, key: str, value):
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self._maxsize:
                self._cache.popitem(last=False)
            self._cache[key] = (value, time.time())

_cache = LRUCache(maxsize=20, ttl=600)
CACHE_TTL = 600

# open.er-api.com 免费API，支持 166 种货币，无限制
RATE_API_URL = "https://open.er-api.com/v6/latest"

# 货币中文名称（覆盖外贸常用）
CURRENCY_NAMES = {
    # 主要货币
    "USD": "美元", "EUR": "欧元", "GBP": "英镑", "JPY": "日元", "CNY": "人民币",
    "HKD": "港币", "KRW": "韩元", "SGD": "新加坡元", "AUD": "澳元", "CAD": "加元",
    "CHF": "瑞士法郎", "THB": "泰铢", "MYR": "马来西亚林吉特", "INR": "印度卢比",
    "TWD": "新台币", "NZD": "新西兰元",
    # 非洲货币
    "XOF": "西非法郎(CFA)", "XAF": "中非法郎(CFA)", "NGN": "尼日利亚奈拉",
    "KES": "肯尼亚先令", "GHS": "加纳塞地", "EGP": "埃及镑", "MAD": "摩洛哥迪拉姆",
    "ZAR": "南非兰特", "TZS": "坦桑尼亚先令", "UGX": "乌干达先令",
    "ETB": "埃塞俄比亚比尔", "RWF": "卢旺达法郎", "XPF": "太平洋法郎",
    # 中东货币
    "AED": "阿联酋迪拉姆", "SAR": "沙特里亚尔", "QAR": "卡塔尔里亚尔",
    "KWD": "科威特第纳尔", "BHD": "巴林第纳尔", "OMR": "阿曼里亚尔",
    "JOD": "约旦第纳尔", "LBP": "黎巴嫩镑", "IQD": "伊拉克第纳尔",
    "IRR": "伊朗里亚尔", "ILS": "以色列新谢克尔",
    # 东南亚
    "PHP": "菲律宾比索", "IDR": "印尼盾", "VND": "越南盾",
    "MMK": "缅甸元", "KHR": "柬埔寨瑞尔", "LAK": "老挝基普", "BDT": "孟加拉塔卡",
    "PKR": "巴基斯坦卢比", "NPR": "尼泊尔卢比", "LKR": "斯里兰卡卢比",
    # 南美
    "BRL": "巴西雷亚尔", "ARS": "阿根廷比索", "CLP": "智利比索",
    "COP": "哥伦比亚比索", "PEN": "秘鲁索尔", "UYU": "乌拉圭比索",
    "PYG": "巴拉圭瓜拉尼", "BOB": "玻利维亚诺", "VES": "委内瑞拉玻利瓦尔",
    # 欧洲其他
    "RUB": "俄罗斯卢布", "TRY": "土耳其里拉", "PLN": "波兰兹罗提",
    "CZK": "捷克克朗", "HUF": "匈牙利福林", "RON": "罗马尼亚列伊",
    "BGN": "保加利亚列弗", "DKK": "丹麦克朗", "SEK": "瑞典克朗",
    "NOK": "挪威克朗", "ISK": "冰岛克朗", "HRK": "克罗地亚库纳",
    "RSD": "塞尔维亚第纳尔", "UAH": "乌克兰格里夫纳", "GEL": "格鲁吉亚拉里",
    "MDL": "摩尔多瓦列伊",
    # 其他
    "MXN": "墨西哥比索", "MNT": "蒙古图格里克", "KZT": "哈萨克斯坦坚哥",
    "UZS": "乌兹别克斯坦索姆", "AFN": "阿富汗尼",
    "BND": "文莱元",
}

# 常用货币（排前面）
POPULAR_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "CNY", "HKD", "KRW", "TWD",
    "SGD", "AUD", "CAD", "CHF", "THB", "MYR", "INR", "VND",
    "PHP", "IDR", "AED", "SAR", "XOF", "XAF", "NGN", "BRL",
    "RUB", "TRY", "MXN",
]


async def _fetch_rates(base: str) -> dict:
    """从 open.er-api.com 获取汇率，带缓存"""
    cache_key = f"rates_{base.upper()}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(f"{RATE_API_URL}/{base.upper()}")
        resp.raise_for_status()
        data = resp.json()

    rates = data.get("rates", {})
    rates[base.upper()] = 1.0

    result = {
        "base": base.upper(),
        "date": data.get("time_last_update_utc", ""),
        "rates": rates,
        "currencies": CURRENCY_NAMES,
        "popular": POPULAR_CURRENCIES,
        "source": "Open Exchange Rates API",
    }

    _cache.set(cache_key, result)
    return result


@router.get("/all", summary="获取全币种汇率")
async def get_all_rates(
    base: str = Query("USD", description="基础货币"),
    current_user: User = Depends(get_current_user),
):
    """一次获取所有币种汇率（166种），返回完整汇率表"""
    try:
        return await _fetch_rates(base)
    except Exception as e:
        logger.error(f"全币种汇率请求失败: {e}")
        raise HTTPException(status_code=502, detail=f"汇率服务暂时不可用: {str(e)}")


@router.get("", summary="获取实时汇率")
async def get_exchange_rate(
    base: str = Query("CNY", description="基础货币"),
    target: str = Query("USD", description="目标货币"),
    current_user: User = Depends(get_current_user),
):
    """获取两种货币间的实时汇率"""
    try:
        data = await _fetch_rates(base)
        rates = data.get("rates", {})
        return {
            "base": base.upper(),
            "target": target.upper(),
            "rate": rates.get(target.upper()),
            "date": data.get("date"),
            "source": data.get("source"),
        }
    except Exception as e:
        logger.error(f"汇率API请求失败: {e}")
        raise HTTPException(status_code=502, detail=f"汇率服务暂时不可用: {str(e)}")


@router.get("/multi", summary="获取多币种汇率")
async def get_multi_rates(
    base: str = Query("CNY", description="基础货币"),
    targets: str = Query("USD,EUR,GBP,JPY", description="目标货币，逗号分隔"),
    current_user: User = Depends(get_current_user),
):
    """一次获取多个币种的汇率"""
    try:
        data = await _fetch_rates(base)
        all_rates = data.get("rates", {})
        target_list = [t.strip().upper() for t in targets.split(",")]
        filtered = {k: all_rates[k] for k in target_list if k in all_rates}
        return {
            "base": base.upper(),
            "date": data.get("date"),
            "rates": filtered,
            "source": data.get("source"),
        }
    except Exception as e:
        logger.error(f"汇率API请求失败: {e}")
        raise HTTPException(status_code=502, detail=f"汇率服务暂时不可用: {str(e)}")

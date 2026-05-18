import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import init_db
from app.utils.logger import logger
from app.api import auth, products, suppliers, exchange_rate, shipping, statistics, upload
from app.api.country_lookup import router as country_lookup_router
from app.api.quotation import router as quotation_router
from app.api.quotation_template import router as quotation_template_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 VM 外贸工具 API 启动中...")
    init_db()
    if not settings.SECRET_KEY:
        raise RuntimeError('SECRET_KEY environment variable is required')
    logger.info("✅ 数据库初始化完成")
    yield
    logger.info("👋 API 关闭")


# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="VM 外贸工具后端API — 产品管理、供应商、运费计算、汇率",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(f'Unhandled exception: {exc}', exc_info=True)
            return JSONResponse(status_code=500, content={'detail': '服务器内部错误'})


app.add_middleware(ExceptionHandlerMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(exchange_rate.router)
app.include_router(shipping.router)
app.include_router(statistics.router)
app.include_router(upload.router)
app.include_router(country_lookup_router)
app.include_router(quotation_router)
app.include_router(quotation_template_router)

# 静态文件服务 - 上传文件
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/", tags=["系统"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["系统"])
async def health():
    return {"status": "ok"}

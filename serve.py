"""生产级静态文件服务器（SPA支持）"""
import uvicorn
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.routing import Route, Mount
import os

DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
PORT = int(os.environ.get("PORT", 3006))


async def catch_all(request):
    """SPA fallback: 非文件请求返回 index.html"""
    return FileResponse(os.path.join(DIST_DIR, "index.html"))


app = Starlette(
    routes=[
        Mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets"),
        Route("/{path:path}", catch_all),
        Route("/", catch_all),
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

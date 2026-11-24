"""main.py —— FastAPI 应用入口（升级方案 §12）"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api import auth as auth_api
from .api import comments as comments_api
from .api import posts as posts_api

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="熊猫海上（PANDA AT SEA）· React + TS / FastAPI 升级版后端",
)

# CORS：开发放行 Vite 两个端口，生产在 CORS_ORIGINS 配置前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api.router, prefix="/api")
app.include_router(posts_api.router, prefix="/api")
app.include_router(comments_api.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"code": 0, "data": {"app": settings.APP_NAME, "version": settings.VERSION}}

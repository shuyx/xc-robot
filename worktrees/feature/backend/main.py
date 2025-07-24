#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-RECON System v2.0 - 主应用入口
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from core.config import get_settings
from core.logging import setup_logging
from api.v1 import api_router


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 获取配置
    settings = get_settings()
    
    # 设置日志
    setup_logging(settings)
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="XC-RECON机器人控制系统 v2.0",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册API路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 静态文件服务
    static_dir = project_root / "data" / "uploads"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app_version}
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "message": "XC-RECON System v2.0 API",
            "version": settings.app_version,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
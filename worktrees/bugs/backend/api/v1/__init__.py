#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 模块
"""

from fastapi import APIRouter
from .endpoints import auth, devices, tasks, models, ai

# 创建API路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备管理"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(models.router, prefix="/models", tags=["3D模型"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI服务"])
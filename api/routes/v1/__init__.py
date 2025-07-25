#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 模块
"""

from fastapi import APIRouter
from .endpoints import system, robots, simple_tasks

# 创建API路由器
api_router = APIRouter()

# 注册简化的子路由
api_router.include_router(system.router, prefix="/system", tags=["系统"])
api_router.include_router(robots.router, prefix="/robots", tags=["机器人"])
api_router.include_router(simple_tasks.router, prefix="/tasks", tags=["任务管理"])
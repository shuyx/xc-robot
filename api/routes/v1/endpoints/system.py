#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统API端点
基础系统状态和健康检查
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "api": "running",
            "robots": "ready",
            "tasks": "ready"
        }
    }

@router.get("/status")
async def system_status() -> Dict[str, Any]:
    """系统状态信息"""
    return {
        "system": "XC-ROBOT",
        "version": "2.0.0",
        "status": "operational",
        "uptime": "running",
        "components": {
            "fr3_right": "disconnected",
            "fr3_left": "disconnected", 
            "hermes": "disconnected"
        },
        "last_updated": datetime.now().isoformat()
    }
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人控制API端点
简化版本，不依赖数据库
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()

# 模拟机器人状态
robot_status = {
    "fr3_right": {
        "id": "fr3_right",
        "name": "FR3右臂",
        "ip": "192.168.58.2",
        "connected": False,
        "status": "idle",
        "position": [0, 0, 0, 0, 0, 0],
        "last_update": datetime.now().isoformat()
    },
    "fr3_left": {
        "id": "fr3_left", 
        "name": "FR3左臂",
        "ip": "192.168.58.3",
        "connected": False,
        "status": "idle",
        "position": [0, 0, 0, 0, 0, 0],
        "last_update": datetime.now().isoformat()
    },
    "hermes": {
        "id": "hermes",
        "name": "Hermes底盘",
        "ip": "192.168.0.100", 
        "connected": False,
        "status": "idle",
        "position": [0, 0, 0],
        "last_update": datetime.now().isoformat()
    }
}

@router.get("/status")
async def get_robots_status() -> Dict[str, Any]:
    """获取所有机器人状态"""
    return {
        "robots": robot_status,
        "summary": {
            "total": len(robot_status),
            "connected": sum(1 for r in robot_status.values() if r["connected"]),
            "active": sum(1 for r in robot_status.values() if r["status"] != "idle")
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/connect")
async def connect_robots() -> Dict[str, Any]:
    """连接所有机器人"""
    for robot in robot_status.values():
        robot["connected"] = True
        robot["status"] = "ready"
        robot["last_update"] = datetime.now().isoformat()
    
    return {
        "message": "正在连接机器人...",
        "status": "connecting",
        "robots": list(robot_status.keys())
    }

@router.post("/disconnect")
async def disconnect_robots() -> Dict[str, Any]:
    """断开所有机器人连接"""
    for robot in robot_status.values():
        robot["connected"] = False
        robot["status"] = "idle"
        robot["last_update"] = datetime.now().isoformat()
    
    return {
        "message": "已断开所有机器人连接",
        "status": "disconnected"
    }

@router.post("/emergency-stop")
async def emergency_stop() -> Dict[str, Any]:
    """紧急停止所有机器人"""
    for robot in robot_status.values():
        robot["status"] = "emergency_stop"
        robot["last_update"] = datetime.now().isoformat()
    
    return {
        "message": "紧急停止已执行",
        "status": "emergency_stopped",
        "timestamp": datetime.now().isoformat()
    }
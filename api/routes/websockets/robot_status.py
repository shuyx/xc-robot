#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人状态WebSocket端点
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from datetime import datetime

websocket_router = APIRouter()

# 存储活跃的WebSocket连接
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 连接已断开，移除
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

manager = ConnectionManager()

@websocket_router.websocket("/ws/robot-status")
async def websocket_robot_status(websocket: WebSocket):
    """机器人状态WebSocket连接"""
    await manager.connect(websocket)
    try:
        while True:
            # 定期发送机器人状态更新
            status_data = {
                "type": "robot_status",
                "timestamp": datetime.now().isoformat(),
                "robots": {
                    "fr3_right": {
                        "connected": False,
                        "status": "idle",
                        "position": [0, 0, 0, 0, 0, 0]
                    },
                    "fr3_left": {
                        "connected": False,
                        "status": "idle", 
                        "position": [0, 0, 0, 0, 0, 0]
                    },
                    "hermes": {
                        "connected": False,
                        "status": "idle",
                        "position": [0, 0, 0]
                    }
                }
            }
            
            await manager.send_personal_message(json.dumps(status_data), websocket)
            await asyncio.sleep(1)  # 每秒发送一次状态更新
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@websocket_router.websocket("/ws/task-logs")
async def websocket_task_logs(websocket: WebSocket):
    """任务日志WebSocket连接"""
    await manager.connect(websocket)
    try:
        while True:
            # 模拟任务日志
            log_data = {
                "type": "task_log",
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": f"系统运行正常 - {datetime.now().strftime('%H:%M:%S')}"
            }
            
            await manager.send_personal_message(json.dumps(log_data), websocket)
            await asyncio.sleep(3)  # 每3秒发送一次日志
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
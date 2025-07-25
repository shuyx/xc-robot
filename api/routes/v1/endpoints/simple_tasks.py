#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理API端点
简化版本，不依赖数据库
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# 模拟任务存储
tasks = {}

@router.get("/")
async def get_tasks() -> Dict[str, Any]:
    """获取所有任务"""
    return {
        "tasks": list(tasks.values()),
        "total": len(tasks),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/execute")
async def execute_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """执行任务"""
    task_id = str(uuid.uuid4())
    
    task = {
        "id": task_id,
        "name": task_data.get("name", "未命名任务"),
        "type": task_data.get("type", "custom"),
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "started_at": datetime.now().isoformat(),
        "progress": 0
    }
    
    tasks[task_id] = task
    
    return {
        "message": "任务已开始执行",
        "task": task
    }

@router.get("/{task_id}/status")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task": tasks[task_id],
        "timestamp": datetime.now().isoformat()
    }

@router.delete("/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """取消任务"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    tasks[task_id]["status"] = "cancelled"
    tasks[task_id]["ended_at"] = datetime.now().isoformat()
    
    return {
        "message": "任务已取消",
        "task_id": task_id
    }
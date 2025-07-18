#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理API端点
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# 临时任务数据存储
TASKS_DATA = {}


@router.get("/")
async def list_tasks():
    """获取任务列表"""
    tasks = list(TASKS_DATA.values())
    
    return {
        "status": "success",
        "data": tasks,
        "total": len(tasks)
    }


@router.post("/")
async def create_task(task_data: Dict[str, Any]):
    """创建新任务"""
    task_id = str(uuid.uuid4())
    
    task = {
        "id": task_id,
        "name": task_data.get("name", f"任务-{task_id[:8]}"),
        "description": task_data.get("description", ""),
        "type": task_data.get("type", "general"),
        "priority": task_data.get("priority", 0),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "config": task_data.get("config", {}),
        "progress": 0
    }
    
    TASKS_DATA[task_id] = task
    
    return {
        "status": "success",
        "message": "任务创建成功",
        "data": task
    }


@router.get("/{task_id}")
async def get_task(task_id: str):
    """获取指定任务详情"""
    if task_id not in TASKS_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    return {
        "status": "success",
        "data": TASKS_DATA[task_id]
    }


@router.put("/{task_id}")
async def update_task(task_id: str, task_data: Dict[str, Any]):
    """更新任务"""
    if task_id not in TASKS_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    task = TASKS_DATA[task_id]
    
    # 更新字段
    for key, value in task_data.items():
        if key in ["name", "description", "priority", "config"]:
            task[key] = value
    
    task["updated_at"] = datetime.now().isoformat()
    
    return {
        "status": "success",
        "message": "任务更新成功",
        "data": task
    }


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if task_id not in TASKS_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    del TASKS_DATA[task_id]
    
    return {
        "status": "success",
        "message": "任务删除成功"
    }


@router.post("/{task_id}/start")
async def start_task(task_id: str):
    """启动任务"""
    if task_id not in TASKS_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    task = TASKS_DATA[task_id]
    task["status"] = "running"
    task["updated_at"] = datetime.now().isoformat()
    
    return {
        "status": "success",
        "message": "任务启动成功",
        "data": task
    }


@router.post("/{task_id}/stop")
async def stop_task(task_id: str):
    """停止任务"""
    if task_id not in TASKS_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在"
        )
    
    task = TASKS_DATA[task_id]
    task["status"] = "stopped"
    task["updated_at"] = datetime.now().isoformat()
    
    return {
        "status": "success",
        "message": "任务停止成功",
        "data": task
    }
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理API端点
完全基于数据库的设备管理，集成设备管理器
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# 导入数据库和模型
from backend.core.database import get_db
from backend.models.device import Device

# 导入设备管理器
from backend.services.device_manager import device_manager

# 导入认证依赖
from backend.core.dependencies import (
    get_current_user_optional,
    check_device_permission
)
from backend.models.user import User

router = APIRouter()


async def _ensure_default_devices(db: Session):
    """确保数据库中有默认设备数据"""
    # 检查是否已有设备数据
    device_count = db.query(Device).count()
    if device_count > 0:
        return
        
    # 创建默认设备
    default_devices = [
        Device(
            name="FR3 右机械臂",
            device_type="robotic_arm",
            ip_address="192.168.58.2",
            port=20003,
            status="offline",
            config={
                "degrees_of_freedom": 6,
                "max_payload": 3.0,
                "max_reach": 855,
                "precision": 0.1,
                "device_id": "right_arm"
            }
        ),
        Device(
            name="FR3 左机械臂",
            device_type="robotic_arm",
            ip_address="192.168.58.3",
            port=20003,
            status="offline",
            config={
                "degrees_of_freedom": 6,
                "max_payload": 3.0,
                "max_reach": 855,
                "precision": 0.1,
                "device_id": "left_arm"
            }
        ),
        Device(
            name="Hermes 移动底盘",
            device_type="mobile_base",
            ip_address="192.168.31.211",
            port=1448,
            status="offline",
            config={
                "max_speed": 1.5,
                "max_acceleration": 2.0,
                "wheel_diameter": 0.2,
                "wheel_base": 0.5,
                "device_id": "chassis"
            }
        )
    ]
    
    for device in default_devices:
        db.add(device)
    db.commit()


@router.get("/")
async def list_devices(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取所有设备列表 - 完全基于数据库"""
    try:
        # 确保有默认设备数据
        await _ensure_default_devices(db)
        
        # 从数据库获取所有设备
        devices = db.query(Device).all()
        device_list = []
        
        for device in devices:
            device_dict = device.dict()
            
            # 添加设备管理器状态信息
            device_id = device_dict["config"].get("device_id", f"device_{device.id}")
            device_type = device_dict["type"]
            
            # 获取实时连接状态
            try:
                status_result = await device_manager.get_device_status(device_id, device_type)
                if status_result["status"] == "success":
                    device_dict["live_status"] = status_result["data"]
                    # 更新数据库中的在线状态
                    if status_result["data"].get("connected", False):
                        device.status = "online"
                        device.last_heartbeat = datetime.utcnow()
            except:
                pass
                
            device_list.append(device_dict)
            
        # 保存状态更新
        db.commit()
        
        return {
            "status": "success",
            "data": device_list,
            "total": len(device_list),
            "simulation_mode": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备列表失败: {str(e)}"
        )


@router.get("/{device_id}")
async def get_device(device_id: int, db: Session = Depends(get_db)):
    """获取指定设备详情"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 ID {device_id} 不存在"
        )
    
    device_dict = device.dict()
    
    # 获取实时状态
    device_config_id = device_dict["config"].get("device_id", f"device_{device.id}")
    device_type = device_dict["type"]
    
    try:
        status_result = await device_manager.get_device_status(device_config_id, device_type)
        if status_result["status"] == "success":
            device_dict["live_status"] = status_result["data"]
    except:
        pass
    
    return {
        "status": "success",
        "data": device_dict
    }


@router.post("/{device_id}/connect")
async def connect_device(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_device_permission)
):
    """连接设备 - 完全集成设备管理器"""
    try:
        # 检查数据库中是否存在该设备
        device_record = db.query(Device).filter(Device.id == device_id).first()
        if not device_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 ID {device_id} 不存在"
            )
        
        # 获取设备配置ID
        device_config_id = device_record.config.get("device_id", f"device_{device_id}")
        device_type = device_record.device_type
        
        # 使用统一设备管理器连接
        connect_result = await device_manager.connect_device(device_config_id, device_type)
        
        # 更新数据库状态
        if connect_result["status"] == "success":
            device_record.status = "online"
            device_record.last_heartbeat = datetime.utcnow()
            
            # 更新设备信息
            if "data" in connect_result and "device_info" in connect_result["data"]:
                # 合并设备信息到config
                device_record.config = {
                    **device_record.config,
                    "connection_info": connect_result["data"]["device_info"]
                }
            
            db.commit()
            
            return {
                "status": "success",
                "message": connect_result["message"],
                "data": {
                    **device_record.dict(),
                    "connection_result": connect_result.get("data", {})
                },
                "simulation_mode": True,
                "connected_by": {
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        else:
            return {
                "status": "error",
                "message": connect_result["message"]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接设备失败: {str(e)}"
        )


@router.post("/{device_id}/disconnect")
async def disconnect_device(
    device_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_device_permission)
):
    """断开设备连接"""
    try:
        # 检查数据库中是否存在该设备
        device_record = db.query(Device).filter(Device.id == device_id).first()
        if not device_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 ID {device_id} 不存在"
            )
        
        # 获取设备配置ID
        device_config_id = device_record.config.get("device_id", f"device_{device_id}")
        device_type = device_record.device_type
        
        # 使用统一设备管理器断开连接
        disconnect_result = await device_manager.disconnect_device(device_config_id, device_type)
        
        # 更新数据库状态
        device_record.status = "offline"
        device_record.last_heartbeat = None
        db.commit()
        
        return {
            "status": "success",
            "message": f"设备 {device_record.name} 断开连接成功",
            "data": device_record.dict(),
            "disconnect_result": disconnect_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"断开设备连接失败: {str(e)}"
        )


@router.get("/{device_id}/status")
async def get_device_status(device_id: int, db: Session = Depends(get_db)):
    """获取设备状态"""
    try:
        # 检查数据库中是否存在该设备
        device_record = db.query(Device).filter(Device.id == device_id).first()
        if not device_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 ID {device_id} 不存在"
            )
        
        # 获取设备配置ID
        device_config_id = device_record.config.get("device_id", f"device_{device_id}")
        device_type = device_record.device_type
        
        # 从设备管理器获取实时状态
        status_result = await device_manager.get_device_status(device_config_id, device_type)
        
        # 组合数据库状态和实时状态
        response_data = {
            "device_id": device_id,
            "database_status": device_record.status,
            "last_heartbeat": device_record.last_heartbeat.isoformat() if device_record.last_heartbeat else None,
            "config": device_record.config
        }
        
        if status_result["status"] == "success":
            response_data["live_status"] = status_result["data"]
            
            # 更新数据库状态（如果设备在线）
            if status_result["data"].get("connected", False):
                device_record.status = "online"
                device_record.last_heartbeat = datetime.utcnow()
                db.commit()
                response_data["database_status"] = "online"
        
        return {
            "status": "success",
            "data": response_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备状态失败: {str(e)}"
        )


@router.post("/{device_id}/command")
async def send_device_command(
    device_id: int, 
    command: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_device_permission)
):
    """发送设备命令"""
    try:
        # 检查数据库中是否存在该设备
        device_record = db.query(Device).filter(Device.id == device_id).first()
        if not device_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"设备 ID {device_id} 不存在"
            )
        
        # 检查设备是否在线
        if device_record.status != "online":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"设备 {device_record.name} 未连接"
            )
        
        # 获取设备配置ID
        device_config_id = device_record.config.get("device_id", f"device_{device_id}")
        device_type = device_record.device_type
        
        # 根据设备类型和命令类型路由到相应的控制方法
        result = None
        
        if device_type == "robotic_arm":
            action = command.get("action")
            if action == "enable":
                result = await device_manager.control_robot_arm(device_config_id, "enable")
            elif action == "disable":
                result = await device_manager.control_robot_arm(device_config_id, "disable")
            elif action == "drag_teach":
                enable = command.get("params", {}).get("enable", False)
                result = await device_manager.control_robot_arm(device_config_id, "drag_teach", enable=enable)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的机械臂操作: {action}"
                }
                
        elif device_type == "mobile_base":
            action = command.get("action")
            if action == "move":
                params = command.get("params", {})
                x = params.get("x", 0.0)
                y = params.get("y", 0.0)
                theta = params.get("theta", 0.0)
                result = await device_manager.control_chassis(device_config_id, "move", x=x, y=y, theta=theta)
            elif action == "stop":
                result = await device_manager.control_chassis(device_config_id, "stop")
            else:
                return {
                    "status": "error",
                    "message": f"不支持的底盘操作: {action}"
                }
        else:
            return {
                "status": "error",
                "message": f"不支持的设备类型: {device_type}"
            }
        
        if result:
            return {
                "status": result["status"],
                "message": result["message"],
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "device_name": device_record.name
            }
        else:
            return {
                "status": "error",
                "message": "命令执行失败"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送设备命令失败: {str(e)}"
        )
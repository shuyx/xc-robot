#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理器 - 统一管理所有设备类型
支持仿真模式，适用于Mac开发环境
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from backend.services.fr3_service import fr3_service
from backend.services.hermes_service import hermes_service

class DeviceManager:
    """统一设备管理器"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.device_services = {
            "robotic_arm": fr3_service,
            "mobile_base": hermes_service
        }
        self.logger.info("🔧 设备管理器初始化完成（仿真模式）")
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("DeviceManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    async def connect_device(self, device_id: str, device_type: str) -> Dict[str, Any]:
        """连接设备"""
        try:
            if device_type == "robotic_arm":
                # FR3机械臂连接
                if device_id in ["right_arm", "left_arm", "fr3_right_arm", "fr3_left_arm"]:
                    return await fr3_service.connect_fr3_arm(device_id)
                else:
                    return {
                        "status": "error",
                        "message": f"不支持的机械臂设备ID: {device_id}"
                    }
                    
            elif device_type == "mobile_base":
                # Hermes底盘连接
                if device_id in ["chassis", "hermes_chassis"]:
                    return await hermes_service.connect_hermes_chassis(device_id)
                else:
                    return {
                        "status": "error", 
                        "message": f"不支持的底盘设备ID: {device_id}"
                    }
                    
            else:
                return {
                    "status": "error",
                    "message": f"不支持的设备类型: {device_type}"
                }
                
        except Exception as e:
            self.logger.error(f"连接设备{device_id}失败: {e}")
            return {
                "status": "error",
                "message": f"连接失败: {str(e)}"
            }
            
    async def disconnect_device(self, device_id: str, device_type: str) -> Dict[str, Any]:
        """断开设备连接"""
        try:
            if device_type == "robotic_arm":
                return await fr3_service.disconnect_fr3_arm(device_id)
            elif device_type == "mobile_base":
                return await hermes_service.disconnect_hermes_chassis(device_id)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的设备类型: {device_type}"
                }
                
        except Exception as e:
            self.logger.error(f"断开设备{device_id}连接失败: {e}")
            return {
                "status": "error",
                "message": f"断开连接失败: {str(e)}"
            }
            
    async def get_device_status(self, device_id: str, device_type: str) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            if device_type == "robotic_arm":
                return await fr3_service.get_device_status(device_id)
            elif device_type == "mobile_base":
                return await hermes_service.get_chassis_status(device_id)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的设备类型: {device_type}"
                }
                
        except Exception as e:
            self.logger.error(f"获取设备{device_id}状态失败: {e}")
            return {
                "status": "error",
                "message": f"获取状态失败: {str(e)}"
            }
            
    async def get_all_devices(self) -> Dict[str, Any]:
        """获取所有设备列表和状态"""
        try:
            all_devices = []
            
            # 获取FR3设备
            fr3_result = await fr3_service.get_all_devices()
            if fr3_result["status"] == "success":
                all_devices.extend(fr3_result["data"])
                
            # 获取Hermes设备
            hermes_devices = []
            for device_id, config in hermes_service.device_configs.items():
                if config.get("type") == "hermes":
                    device_data = {
                        "id": device_id,
                        "name": config.get("description", device_id),
                        "type": "mobile_base",
                        "ip": config.get("ip"),
                        "port": config.get("port"),
                        "enabled": config.get("enabled", True),
                        "connected": device_id in hermes_service.clients,
                        "status": "online" if device_id in hermes_service.clients else "offline"
                    }
                    
                    # 添加连接状态信息
                    if device_id in hermes_service.connection_status:
                        device_data.update(hermes_service.connection_status[device_id])
                        
                    hermes_devices.append(device_data)
                    
            all_devices.extend(hermes_devices)
            
            return {
                "status": "success",
                "data": all_devices,
                "total": len(all_devices),
                "summary": {
                    "robotic_arms": len([d for d in all_devices if d["type"] == "robotic_arm"]),
                    "mobile_bases": len([d for d in all_devices if d["type"] == "mobile_base"]),
                    "connected": len([d for d in all_devices if d.get("connected", False)]),
                    "simulation_mode": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取所有设备失败: {e}")
            return {
                "status": "error",
                "message": f"获取设备列表失败: {str(e)}"
            }
            
    async def control_robot_arm(self, device_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """控制机械臂"""
        try:
            if action == "enable":
                return await fr3_service.enable_robot(device_id)
            elif action == "disable":
                return await fr3_service.disable_robot(device_id)
            elif action == "drag_teach":
                enable = kwargs.get("enable", False)
                return await fr3_service.set_drag_teach_mode(device_id, enable)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的机械臂操作: {action}"
                }
                
        except Exception as e:
            self.logger.error(f"控制机械臂{device_id}失败: {e}")
            return {
                "status": "error",
                "message": f"控制失败: {str(e)}"
            }
            
    async def control_chassis(self, device_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """控制底盘"""
        try:
            if action == "move":
                x = kwargs.get("x", 0.0)
                y = kwargs.get("y", 0.0)
                theta = kwargs.get("theta", 0.0)
                return await hermes_service.move_chassis(device_id, x, y, theta)
            elif action == "stop":
                return await hermes_service.stop_chassis(device_id)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的底盘操作: {action}"
                }
                
        except Exception as e:
            self.logger.error(f"控制底盘{device_id}失败: {e}")
            return {
                "status": "error",
                "message": f"控制失败: {str(e)}"
            }

# 全局设备管理器实例
device_manager = DeviceManager()
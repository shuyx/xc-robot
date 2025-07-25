#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hermes底盘连接服务
基于robot_config.yaml配置的仿真实现
"""

import os
import time
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

# 开发环境配置 - 在Mac上使用仿真模式
SIMULATION_MODE = True  # 设为True启用仿真模式，避免真实硬件依赖

if SIMULATION_MODE:
    print("🔧 Hermes仿真模式已启用（适用于Mac开发环境）")
else:
    try:
        import httpx
        print("✅ HTTP客户端库可用")
    except ImportError as e:
        print(f"⚠️ HTTP客户端库导入失败: {e}")

class SimulatedHermesClient:
    """Hermes底盘仿真类 - 用于Mac开发环境"""
    
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.connected = True
        
        # 仿真底盘状态
        self.power_status = {
            "battery_level": 85.5,
            "charging": False,
            "voltage": 24.2,
            "temperature": 35.0
        }
        
        self.motion_status = {
            "position": {"x": 0.0, "y": 0.0, "theta": 0.0},
            "velocity": {"linear": 0.0, "angular": 0.0},
            "status": "idle"  # idle, moving, charging
        }
        
        time.sleep(0.1)  # 模拟连接延迟
        
    async def get_status(self):
        """模拟获取底盘状态"""
        await asyncio.sleep(0.05)  # 模拟网络延迟
        return {
            "status_code": 200,
            "data": {
                "power": self.power_status,
                "motion": self.motion_status,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    async def move_to(self, x: float, y: float, theta: float = 0.0):
        """模拟移动到指定位置"""
        await asyncio.sleep(0.1)  # 模拟命令处理延迟
        
        # 模拟移动过程
        self.motion_status["status"] = "moving"
        await asyncio.sleep(0.5)  # 模拟移动时间
        
        # 更新位置（添加小幅误差模拟真实情况）
        import random
        self.motion_status["position"] = {
            "x": x + random.uniform(-0.02, 0.02),
            "y": y + random.uniform(-0.02, 0.02), 
            "theta": theta + random.uniform(-0.05, 0.05)
        }
        self.motion_status["status"] = "idle"
        
        return {
            "status_code": 200,
            "message": "移动命令执行成功",
            "target": {"x": x, "y": y, "theta": theta},
            "actual": self.motion_status["position"]
        }
        
    async def stop(self):
        """模拟停止移动"""
        await asyncio.sleep(0.05)
        self.motion_status["velocity"] = {"linear": 0.0, "angular": 0.0}
        self.motion_status["status"] = "idle"
        
        return {
            "status_code": 200,
            "message": "底盘已停止"
        }
        
    async def manual_control(self, linear: float, angular: float):
        """模拟手动控制"""
        await asyncio.sleep(0.05)
        
        # 更新速度
        self.motion_status["velocity"] = {
            "linear": linear,
            "angular": angular
        }
        
        # 根据速度更新状态
        if abs(linear) > 0.01 or abs(angular) > 0.01:
            self.motion_status["status"] = "moving"
        else:
            self.motion_status["status"] = "idle"
            
        return {
            "status_code": 200,
            "message": "手动控制命令已执行",
            "velocity": self.motion_status["velocity"]
        }

class HermesDeviceService:
    """Hermes底盘设备服务"""
    
    def __init__(self):
        self.clients: Dict[str, SimulatedHermesClient] = {}
        self.device_configs = {}
        self.connection_status = {}
        self.logger = self._setup_logging()
        
        self._load_device_configs()
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("HermesService")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def _load_device_configs(self):
        """加载设备配置 - 基于robot_config.yaml"""
        try:
            import yaml
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                'robot_config.yaml'
            )
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.device_configs = config.get('devices', {})
                    self.logger.info("✅ 从robot_config.yaml加载设备配置成功")
            else:
                # 备用配置
                self.device_configs = {
                    "chassis": {
                        "type": "hermes",
                        "ip": "192.168.31.211",
                        "port": 1448,
                        "enabled": True,
                        "description": "思岚Hermes轮式底盘"
                    }
                }
                self.logger.warning("使用备用Hermes设备配置")
                
        except Exception as e:
            self.logger.error(f"加载设备配置失败: {e}")
            
    async def connect_hermes_chassis(self, device_id: str) -> Dict[str, Any]:
        """
        连接Hermes底盘
        仿真模式实现
        """
        if device_id not in self.device_configs:
            return {
                "status": "error", 
                "message": f"设备配置不存在: {device_id}"
            }
            
        device_config = self.device_configs[device_id]
        
        if device_config.get("type") != "hermes":
            return {
                "status": "error",
                "message": f"设备类型错误: {device_config.get('type')}"
            }
            
        chassis_ip = device_config["ip"]
        chassis_port = device_config["port"]
        
        try:
            self.logger.info(f"正在连接{device_id} - {chassis_ip}:{chassis_port} (仿真模式)")
            start_time = time.time()
            
            # 步骤1: 建立连接（仿真模式）
            if SIMULATION_MODE:
                client = SimulatedHermesClient(chassis_ip, chassis_port)
                self.logger.info("🔧 使用仿真Hermes底盘")
            else:
                # 真实模式下的HTTP连接（当部署到Windows时使用）
                import httpx
                async with httpx.AsyncClient() as real_client:
                    response = await real_client.get(f"http://{chassis_ip}:{chassis_port}/api/core/system/v1/power/status", timeout=5)
                    if response.status_code != 200:
                        return {
                            "status": "error",
                            "message": f"无法连接到Hermes底盘: HTTP {response.status_code}"
                        }
                client = real_client  # 这里需要更复杂的客户端管理
                
            connection_time = time.time() - start_time
            
            # 步骤2: 获取设备状态验证连接
            status_result = await client.get_status()
            
            device_info = {
                "connection_time": connection_time,
                "base_url": f"http://{chassis_ip}:{chassis_port}",
                "power_status": status_result["data"]["power"],
                "motion_status": status_result["data"]["motion"]
            }
            
            # 步骤3: 保存连接
            self.clients[device_id] = client
            self.connection_status[device_id] = {
                "connected": True,
                "connected_at": datetime.now().isoformat(),
                "connection_time": connection_time,
                "device_info": device_info
            }
            
            self.logger.info(f"✅ {device_id}连接成功完成")
            
            return {
                "status": "success",
                "message": f"{device_config['description']} 连接成功",
                "data": {
                    "device_id": device_id,
                    "ip": chassis_ip,
                    "port": chassis_port,
                    "connection_time": connection_time,
                    "device_info": device_info
                }
            }
            
        except Exception as e:
            self.logger.error(f"连接{device_id}失败: {e}")
            return {
                "status": "error",
                "message": f"连接失败: {str(e)}"
            }
            
    async def disconnect_hermes_chassis(self, device_id: str) -> Dict[str, Any]:
        """断开Hermes底盘连接"""
        try:
            if device_id not in self.clients:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            # 先停止运动
            client = self.clients[device_id]
            await client.stop()
            
            # 清理连接记录
            del self.clients[device_id]
            self.connection_status[device_id] = {
                "connected": False,
                "disconnected_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"{device_id}断开连接成功")
            
            return {
                "status": "success",
                "message": f"{device_id}断开连接成功"
            }
            
        except Exception as e:
            self.logger.error(f"断开{device_id}连接失败: {e}")
            return {
                "status": "error",
                "message": f"断开连接失败: {str(e)}"
            }
            
    async def get_chassis_status(self, device_id: str) -> Dict[str, Any]:
        """获取底盘状态"""
        try:
            if device_id not in self.clients:
                return {
                    "status": "success",
                    "data": {
                        "device_id": device_id,
                        "connected": False,
                        "status": "offline"
                    }
                }
                
            client = self.clients[device_id]
            status_result = await client.get_status()
            
            status_data = {
                "device_id": device_id,
                "connected": True,
                "status": "online",
                "connection_info": self.connection_status.get(device_id, {}),
                "real_time_data": status_result["data"]
            }
            
            return {
                "status": "success",
                "data": status_data
            }
            
        except Exception as e:
            self.logger.error(f"获取{device_id}状态失败: {e}")
            return {
                "status": "error",
                "message": f"获取状态失败: {str(e)}"
            }
            
    async def move_chassis(self, device_id: str, x: float, y: float, theta: float = 0.0) -> Dict[str, Any]:
        """移动底盘到指定位置"""
        try:
            if device_id not in self.clients:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            client = self.clients[device_id]
            result = await client.move_to(x, y, theta)
            
            self.logger.info(f"{device_id}移动到位置: ({x}, {y}, {theta})")
            
            return {
                "status": "success",
                "message": f"{device_id}移动命令执行成功",
                "data": result
            }
            
        except Exception as e:
            self.logger.error(f"{device_id}移动失败: {e}")
            return {
                "status": "error",
                "message": f"移动失败: {str(e)}"
            }
            
    async def stop_chassis(self, device_id: str) -> Dict[str, Any]:
        """停止底盘移动"""
        try:
            if device_id not in self.clients:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            client = self.clients[device_id]
            result = await client.stop()
            
            self.logger.info(f"{device_id}已停止移动")
            
            return {
                "status": "success",
                "message": f"{device_id}停止成功",
                "data": result
            }
            
        except Exception as e:
            self.logger.error(f"{device_id}停止失败: {e}")
            return {
                "status": "error",
                "message": f"停止失败: {str(e)}"
            }

# 全局服务实例
hermes_service = HermesDeviceService()
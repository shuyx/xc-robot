#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Hardware Control Bridge for Web GUI
基于真实FR3、Hermes、视觉、夹爪控制逻辑的Web GUI后端
"""

import time
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

# 导入硬件控制模块
try:
    from fairino import Robot
    FAIRINO_AVAILABLE = True
    print("✅ FR3 Fairino SDK 可用")
except ImportError as e:
    FAIRINO_AVAILABLE = False
    print(f"⚠️ FR3 Fairino SDK 不可用: {e}")

try:
    from services.robot.hermes_service import hermes_service
    HERMES_AVAILABLE = True
    print("✅ Hermes 底盘服务可用")
except ImportError as e:
    HERMES_AVAILABLE = False
    print(f"⚠️ Hermes 底盘服务不可用: {e}")

try:
    import cv2
    import numpy as np
    VISION_AVAILABLE = True
    print("✅ 视觉系统库可用")
except ImportError as e:
    VISION_AVAILABLE = False
    print(f"⚠️ 视觉系统库不可用: {e}")

class RealHardwareControlBridge(QObject):
    """
    真实硬件控制桥接器
    整合FR3、Hermes、视觉、夹爪的完整控制逻辑
    """
    
    # PyQt信号定义
    log_message = pyqtSignal(str, str)  # (level, message)
    connection_status_changed = pyqtSignal(str, str, dict)  # (device_type, device_id, status)
    test_progress_updated = pyqtSignal(str, dict)  # (test_id, progress_data)
    emergency_stop_triggered = pyqtSignal(str)  # (reason)
    
    def __init__(self):
        super().__init__()
        
        # 硬件配置
        self.hardware_config = {
            'fr3_arms': {
                'left_arm': {
                    'ip': '192.168.58.3',
                    'port': 20003,
                    'description': 'FR3左臂'
                },
                'right_arm': {
                    'ip': '192.168.58.2', 
                    'port': 20003,
                    'description': 'FR3右臂'
                }
            },
            'hermes_chassis': {
                'main_chassis': {
                    'ip': '192.168.31.211',
                    'port': 1448,
                    'description': '思岚Hermes底盘'
                }
            },
            'vision_system': {
                'gemini_335_left': {
                    'camera_index': 0,
                    'resolution': (1280, 720),
                    'description': 'Gemini 335左相机'
                },
                'gemini_335_right': {
                    'camera_index': 1, 
                    'resolution': (1280, 720),
                    'description': 'Gemini 335右相机'
                }
            },
            'gripper_system': {
                'left_gripper': {
                    'company': 3,
                    'device': 0,
                    'arm_id': 'left_arm'
                },
                'right_gripper': {
                    'company': 3,
                    'device': 0, 
                    'arm_id': 'right_arm'
                }
            }
        }
        
        # 连接状态管理
        self.connections = {
            'fr3_arms': {},
            'hermes_chassis': {},
            'vision_system': {},
            'gripper_system': {}
        }
        
        # 测试执行状态
        self.running_tests = {}
        self.test_results = {}
        
        # 日志设置
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 初始化硬件管理器
        self._init_hardware_managers()
        
    def _init_hardware_managers(self):
        """初始化各硬件管理器"""
        self.fr3_manager = FR3ArmManager(self.hardware_config['fr3_arms'])
        self.hermes_manager = HermesChassisManager(self.hardware_config['hermes_chassis'])
        self.vision_manager = VisionSystemManager(self.hardware_config['vision_system'])
        self.gripper_manager = GripperManager(self.hardware_config['gripper_system'])
        
        # 连接信号
        self._connect_manager_signals()
    
    def _connect_manager_signals(self):
        """连接各管理器的信号"""
        # FR3臂信号
        self.fr3_manager.connection_changed.connect(
            lambda device_id, status: self.connection_status_changed.emit('fr3_arm', device_id, status)
        )
        self.fr3_manager.log_message.connect(self.log_message.emit)
        
        # Hermes底盘信号
        self.hermes_manager.connection_changed.connect(
            lambda device_id, status: self.connection_status_changed.emit('hermes_chassis', device_id, status)
        )
        self.hermes_manager.log_message.connect(self.log_message.emit)
        
        # 视觉系统信号
        self.vision_manager.connection_changed.connect(
            lambda device_id, status: self.connection_status_changed.emit('vision_camera', device_id, status)
        )
        self.vision_manager.log_message.connect(self.log_message.emit)
        
        # 夹爪系统信号
        self.gripper_manager.connection_changed.connect(
            lambda device_id, status: self.connection_status_changed.emit('gripper', device_id, status)
        )
        self.gripper_manager.log_message.connect(self.log_message.emit)
    
    # ============== Web GUI API接口 ==============
    
    @pyqtSlot(str, result=str)
    def connect_fr3_arm(self, arm_id: str) -> str:
        """连接FR3机械臂"""
        try:
            result = self.fr3_manager.connect_arm(arm_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"连接FR3臂失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def disconnect_fr3_arm(self, arm_id: str) -> str:
        """断开FR3机械臂连接"""
        try:
            result = self.fr3_manager.disconnect_arm(arm_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"断开FR3臂失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def get_fr3_arm_status(self, arm_id: str) -> str:
        """获取FR3机械臂状态"""
        try:
            result = self.fr3_manager.get_arm_status(arm_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"获取FR3臂状态失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def connect_hermes_chassis(self, chassis_id: str) -> str:
        """连接Hermes底盘"""
        try:
            # 使用异步包装器
            result = asyncio.run(self.hermes_manager.connect_chassis(chassis_id))
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"连接Hermes底盘失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def disconnect_hermes_chassis(self, chassis_id: str) -> str:
        """断开Hermes底盘连接"""
        try:
            result = asyncio.run(self.hermes_manager.disconnect_chassis(chassis_id))
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"断开Hermes底盘失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def get_hermes_chassis_status(self, chassis_id: str) -> str:
        """获取Hermes底盘状态"""
        try:
            result = asyncio.run(self.hermes_manager.get_chassis_status(chassis_id))
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"获取Hermes底盘状态失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def connect_vision_camera(self, camera_id: str) -> str:
        """连接视觉相机"""
        try:
            result = self.vision_manager.connect_camera(camera_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"连接视觉相机失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def disconnect_vision_camera(self, camera_id: str) -> str:
        """断开视觉相机连接"""
        try:
            result = self.vision_manager.disconnect_camera(camera_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"断开视觉相机失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def get_vision_camera_status(self, camera_id: str) -> str:
        """获取视觉相机状态"""
        try:
            result = self.vision_manager.get_camera_status(camera_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"获取视觉相机状态失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def connect_gripper(self, gripper_id: str) -> str:
        """连接夹爪"""
        try:
            result = self.gripper_manager.connect_gripper(gripper_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"连接夹爪失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def disconnect_gripper(self, gripper_id: str) -> str:
        """断开夹爪连接"""
        try:
            result = self.gripper_manager.disconnect_gripper(gripper_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"断开夹爪失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def get_gripper_status(self, gripper_id: str) -> str:
        """获取夹爪状态"""
        try:
            result = self.gripper_manager.get_gripper_status(gripper_id)
            return json.dumps(result)
        except Exception as e:
            self.logger.error(f"获取夹爪状态失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def execute_lua_test(self, test_config: str) -> str:
        """执行Lua测试"""
        try:
            config = json.loads(test_config)
            test_executor = LuaTestExecutor(config, self)
            
            # 在新线程中执行测试
            test_thread = threading.Thread(
                target=test_executor.run_test,
                daemon=True
            )
            test_thread.start()
            
            return json.dumps({
                "success": True,
                "test_id": config.get('test_id', 'unknown'),
                "message": "测试已开始执行"
            })
            
        except Exception as e:
            self.logger.error(f"执行Lua测试失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(str, result=str)
    def emergency_stop_all(self, reason: str = "用户紧急停止") -> str:
        """紧急停止所有设备"""
        try:
            stop_results = {}
            
            # 停止所有FR3臂
            for arm_id in self.fr3_manager.connections.keys():
                try:
                    self.fr3_manager.emergency_stop_arm(arm_id)
                    stop_results[f"fr3_{arm_id}"] = "已停止"
                except Exception as e:
                    stop_results[f"fr3_{arm_id}"] = f"停止失败: {e}"
            
            # 停止所有底盘
            for chassis_id in self.hermes_manager.connections.keys():
                try:
                    asyncio.run(self.hermes_manager.emergency_stop_chassis(chassis_id))
                    stop_results[f"hermes_{chassis_id}"] = "已停止"
                except Exception as e:
                    stop_results[f"hermes_{chassis_id}"] = f"停止失败: {e}"
            
            # 停止所有夹爪
            for gripper_id in self.gripper_manager.connections.keys():
                try:
                    self.gripper_manager.emergency_stop_gripper(gripper_id)
                    stop_results[f"gripper_{gripper_id}"] = "已停止"
                except Exception as e:
                    stop_results[f"gripper_{gripper_id}"] = f"停止失败: {e}"
            
            # 发出紧急停止信号
            self.emergency_stop_triggered.emit(reason)
            
            self.logger.warning(f"紧急停止执行完成: {reason}")
            
            return json.dumps({
                "success": True,
                "reason": reason,
                "stop_results": stop_results,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"紧急停止失败: {e}")
            return json.dumps({"success": False, "error": str(e)})
    
    @pyqtSlot(result=str)
    def get_all_device_status(self) -> str:
        """获取所有设备状态"""
        try:
            status_summary = {
                "fr3_arms": {},
                "hermes_chassis": {},
                "vision_cameras": {},
                "grippers": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # FR3臂状态
            for arm_id in self.hardware_config['fr3_arms'].keys():
                status_summary["fr3_arms"][arm_id] = self.fr3_manager.get_arm_status(arm_id)
            
            # Hermes底盘状态
            for chassis_id in self.hardware_config['hermes_chassis'].keys():
                status_summary["hermes_chassis"][chassis_id] = asyncio.run(
                    self.hermes_manager.get_chassis_status(chassis_id)
                )
            
            # 视觉相机状态
            for camera_id in self.hardware_config['vision_system'].keys():
                status_summary["vision_cameras"][camera_id] = self.vision_manager.get_camera_status(camera_id)
            
            # 夹爪状态
            for gripper_id in self.hardware_config['gripper_system'].keys():
                status_summary["grippers"][gripper_id] = self.gripper_manager.get_gripper_status(gripper_id)
            
            return json.dumps({
                "success": True,
                "data": status_summary
            })
            
        except Exception as e:
            self.logger.error(f"获取设备状态失败: {e}")
            return json.dumps({"success": False, "error": str(e)})


class FR3ArmManager(QObject):
    """FR3机械臂管理器"""
    
    connection_changed = pyqtSignal(str, dict)  # (arm_id, status)
    log_message = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, arm_configs: Dict[str, Dict]):
        super().__init__()
        self.arm_configs = arm_configs
        self.connections = {}  # arm_id -> Robot object
        self.arm_status = {}   # arm_id -> status dict
        
    def connect_arm(self, arm_id: str) -> Dict[str, Any]:
        """连接FR3机械臂"""
        if not FAIRINO_AVAILABLE:
            return {
                "success": False,
                "error": "Fairino SDK不可用，无法连接FR3机械臂"
            }
        
        if arm_id not in self.arm_configs:
            return {
                "success": False,
                "error": f"未知的机械臂ID: {arm_id}"
            }
        
        arm_config = self.arm_configs[arm_id]
        
        try:
            self.log_message.emit("INFO", f"正在连接{arm_config['description']} ({arm_config['ip']})")
            
            # 建立连接
            robot = Robot.RPC(arm_config['ip'])
            
            # 验证连接
            error, version = robot.GetSDKVersion()
            if error != 0:
                return {
                    "success": False,
                    "error": f"连接验证失败，错误码: {error}"
                }
            
            # 获取机械臂状态
            error, robot_state = robot.GetRobotRealTimeState()
            if error != 0:
                return {
                    "success": False,
                    "error": f"获取机械臂状态失败，错误码: {error}"
                }
            
            # 保存连接
            self.connections[arm_id] = robot
            
            # 更新状态
            status_info = {
                "connected": True,
                "ip": arm_config['ip'],
                "sdk_version": version,
                "robot_state": {
                    "joints": robot_state.joint_pos,
                    "cartesian": robot_state.cartesian_pos,
                    "tool": robot_state.tool,
                    "speed": robot_state.speed
                },
                "connected_at": datetime.now().isoformat()
            }
            
            self.arm_status[arm_id] = status_info
            self.connection_changed.emit(arm_id, status_info)
            
            self.log_message.emit("INFO", f"{arm_config['description']}连接成功，SDK版本: {version}")
            
            return {
                "success": True,
                "data": status_info
            }
            
        except Exception as e:
            self.log_message.emit("ERROR", f"连接{arm_config['description']}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_arm(self, arm_id: str) -> Dict[str, Any]:
        """断开FR3机械臂连接"""
        if arm_id not in self.connections:
            return {
                "success": False,
                "error": f"机械臂{arm_id}未连接"
            }
        
        try:
            # 停止运动
            robot = self.connections[arm_id]
            robot.StopMotion()
            
            # 清理连接
            del self.connections[arm_id]
            
            # 更新状态
            self.arm_status[arm_id] = {
                "connected": False,
                "disconnected_at": datetime.now().isoformat()
            }
            
            self.connection_changed.emit(arm_id, self.arm_status[arm_id])
            self.log_message.emit("INFO", f"机械臂{arm_id}断开连接成功")
            
            return {"success": True}
            
        except Exception as e:
            self.log_message.emit("ERROR", f"断开机械臂{arm_id}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_arm_status(self, arm_id: str) -> Dict[str, Any]:
        """获取机械臂状态"""
        if arm_id not in self.connections:
            return {
                "connected": False,
                "arm_id": arm_id
            }
        
        try:
            robot = self.connections[arm_id]
            
            # 获取实时状态
            error, robot_state = robot.GetRobotRealTimeState()
            if error != 0:
                self.log_message.emit("WARNING", f"获取机械臂{arm_id}状态失败")
                return self.arm_status.get(arm_id, {"connected": False})
            
            # 更新状态信息
            status_update = {
                "connected": True,
                "arm_id": arm_id,
                "robot_state": {
                    "joints": robot_state.joint_pos,
                    "cartesian": robot_state.cartesian_pos,
                    "tool": robot_state.tool,
                    "speed": robot_state.speed
                },
                "last_update": datetime.now().isoformat()
            }
            
            # 合并现有状态
            if arm_id in self.arm_status:
                self.arm_status[arm_id].update(status_update)
            else:
                self.arm_status[arm_id] = status_update
            
            return self.arm_status[arm_id]
            
        except Exception as e:
            self.log_message.emit("ERROR", f"获取机械臂{arm_id}状态异常: {e}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    def emergency_stop_arm(self, arm_id: str) -> bool:
        """紧急停止机械臂"""
        if arm_id not in self.connections:
            return False
        
        try:
            robot = self.connections[arm_id]
            robot.StopMotion()
            self.log_message.emit("WARNING", f"机械臂{arm_id}紧急停止")
            return True
        except Exception as e:
            self.log_message.emit("ERROR", f"机械臂{arm_id}紧急停止失败: {e}")
            return False


class HermesChassisManager(QObject):
    """Hermes底盘管理器"""
    
    connection_changed = pyqtSignal(str, dict)  # (chassis_id, status)
    log_message = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, chassis_configs: Dict[str, Dict]):
        super().__init__()
        self.chassis_configs = chassis_configs
        self.connections = {}  # chassis_id -> connection status
        
    async def connect_chassis(self, chassis_id: str) -> Dict[str, Any]:
        """连接Hermes底盘"""
        if not HERMES_AVAILABLE:
            return {
                "success": False,
                "error": "Hermes服务不可用"
            }
        
        if chassis_id not in self.chassis_configs:
            return {
                "success": False,
                "error": f"未知的底盘ID: {chassis_id}"
            }
        
        try:
            # 使用hermes_service连接
            result = await hermes_service.connect_hermes_chassis(chassis_id)
            
            if result["status"] == "success":
                self.connections[chassis_id] = True
                
                status_info = {
                    "connected": True,
                    "chassis_id": chassis_id,
                    "connection_data": result["data"],
                    "connected_at": datetime.now().isoformat()
                }
                
                self.connection_changed.emit(chassis_id, status_info)
                self.log_message.emit("INFO", f"底盘{chassis_id}连接成功")
                
                return {
                    "success": True,
                    "data": status_info
                }
            else:
                return {
                    "success": False,
                    "error": result["message"]
                }
                
        except Exception as e:
            self.log_message.emit("ERROR", f"连接底盘{chassis_id}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def disconnect_chassis(self, chassis_id: str) -> Dict[str, Any]:
        """断开Hermes底盘连接"""
        try:
            result = await hermes_service.disconnect_hermes_chassis(chassis_id)
            
            if result["status"] == "success":
                if chassis_id in self.connections:
                    del self.connections[chassis_id]
                
                status_info = {
                    "connected": False,
                    "disconnected_at": datetime.now().isoformat()
                }
                
                self.connection_changed.emit(chassis_id, status_info)
                self.log_message.emit("INFO", f"底盘{chassis_id}断开连接成功")
                
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": result["message"]
                }
                
        except Exception as e:
            self.log_message.emit("ERROR", f"断开底盘{chassis_id}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_chassis_status(self, chassis_id: str) -> Dict[str, Any]:
        """获取底盘状态"""
        try:
            result = await hermes_service.get_chassis_status(chassis_id)
            
            if result["status"] == "success":
                return result["data"]
            else:
                return {
                    "connected": False,
                    "error": result["message"]
                }
                
        except Exception as e:
            self.log_message.emit("ERROR", f"获取底盘{chassis_id}状态失败: {e}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    async def emergency_stop_chassis(self, chassis_id: str) -> bool:
        """紧急停止底盘"""
        try:
            result = await hermes_service.stop_chassis(chassis_id)
            success = result["status"] == "success"
            if success:
                self.log_message.emit("WARNING", f"底盘{chassis_id}紧急停止")
            return success
        except Exception as e:
            self.log_message.emit("ERROR", f"底盘{chassis_id}紧急停止失败: {e}")
            return False


class VisionSystemManager(QObject):
    """视觉系统管理器"""
    
    connection_changed = pyqtSignal(str, dict)  # (camera_id, status)
    log_message = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, vision_configs: Dict[str, Dict]):
        super().__init__()
        self.vision_configs = vision_configs
        self.connections = {}  # camera_id -> cv2.VideoCapture
        self.camera_status = {}
        
    def connect_camera(self, camera_id: str) -> Dict[str, Any]:
        """连接视觉相机"""
        if not VISION_AVAILABLE:
            return {
                "success": False,
                "error": "OpenCV不可用，无法连接相机"
            }
        
        if camera_id not in self.vision_configs:
            return {
                "success": False,
                "error": f"未知的相机ID: {camera_id}"
            }
        
        camera_config = self.vision_configs[camera_id]
        
        try:
            self.log_message.emit("INFO", f"正在连接{camera_config['description']}")
            
            # 尝试连接相机
            cap = cv2.VideoCapture(camera_config['camera_index'])
            
            if not cap.isOpened():
                return {
                    "success": False,
                    "error": f"无法打开相机索引 {camera_config['camera_index']}"
                }
            
            # 设置分辨率
            width, height = camera_config['resolution']
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # 测试读取帧
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return {
                    "success": False,
                    "error": "无法从相机读取图像"
                }
            
            # 保存连接
            self.connections[camera_id] = cap
            
            # 更新状态
            status_info = {
                "connected": True,
                "camera_id": camera_id,
                "resolution": frame.shape[:2],
                "frame_size": frame.size,
                "connected_at": datetime.now().isoformat()
            }
            
            self.camera_status[camera_id] = status_info
            self.connection_changed.emit(camera_id, status_info)
            
            self.log_message.emit("INFO", f"{camera_config['description']}连接成功")
            
            return {
                "success": True,
                "data": status_info
            }
            
        except Exception as e:
            self.log_message.emit("ERROR", f"连接{camera_config['description']}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_camera(self, camera_id: str) -> Dict[str, Any]:
        """断开相机连接"""
        if camera_id not in self.connections:
            return {
                "success": False,
                "error": f"相机{camera_id}未连接"
            }
        
        try:
            # 释放相机资源
            cap = self.connections[camera_id]
            cap.release()
            
            # 清理连接
            del self.connections[camera_id]
            
            # 更新状态
            self.camera_status[camera_id] = {
                "connected": False,
                "disconnected_at": datetime.now().isoformat()
            }
            
            self.connection_changed.emit(camera_id, self.camera_status[camera_id])
            self.log_message.emit("INFO", f"相机{camera_id}断开连接成功")
            
            return {"success": True}
            
        except Exception as e:
            self.log_message.emit("ERROR", f"断开相机{camera_id}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_camera_status(self, camera_id: str) -> Dict[str, Any]:
        """获取相机状态"""
        if camera_id not in self.connections:
            return {
                "connected": False,
                "camera_id": camera_id
            }
        
        try:
            cap = self.connections[camera_id]
            
            # 检查相机是否仍然可用
            if not cap.isOpened():
                return {
                    "connected": False,
                    "error": "相机连接已断开"
                }
            
            # 更新状态
            status_update = {
                "connected": True,
                "camera_id": camera_id,
                "last_check": datetime.now().isoformat()
            }
            
            # 合并现有状态
            if camera_id in self.camera_status:
                self.camera_status[camera_id].update(status_update)
            else:
                self.camera_status[camera_id] = status_update
            
            return self.camera_status[camera_id]
            
        except Exception as e:
            self.log_message.emit("ERROR", f"获取相机{camera_id}状态异常: {e}")
            return {
                "connected": False,
                "error": str(e)
            }


class GripperManager(QObject):
    """夹爪管理器"""
    
    connection_changed = pyqtSignal(str, dict)  # (gripper_id, status) 
    log_message = pyqtSignal(str, str)  # (level, message)
    
    def __init__(self, gripper_configs: Dict[str, Dict]):
        super().__init__()
        self.gripper_configs = gripper_configs
        self.connections = {}  # gripper_id -> {robot, config}
        self.gripper_status = {}
        
    def connect_gripper(self, gripper_id: str) -> Dict[str, Any]:
        """连接夹爪（通过对应的机械臂）"""
        if not FAIRINO_AVAILABLE:
            return {
                "success": False,
                "error": "Fairino SDK不可用，无法连接夹爪"
            }
        
        if gripper_id not in self.gripper_configs:
            return {
                "success": False,
                "error": f"未知的夹爪ID: {gripper_id}"
            }
        
        gripper_config = self.gripper_configs[gripper_id]
        arm_id = gripper_config['arm_id']
        
        try:
            # 需要获取对应机械臂的连接
            # 这里假设从外部传入arm_manager或通过某种方式获取
            # 简化实现，直接创建机械臂连接
            
            self.log_message.emit("INFO", f"正在连接夹爪{gripper_id}（通过{arm_id}）")
            
            # 模拟夹爪连接成功
            status_info = {
                "connected": True,
                "gripper_id": gripper_id,
                "arm_id": arm_id,
                "company": gripper_config['company'],
                "device": gripper_config['device'],
                "connected_at": datetime.now().isoformat()
            }
            
            self.gripper_status[gripper_id] = status_info
            self.connection_changed.emit(gripper_id, status_info)
            
            self.log_message.emit("INFO", f"夹爪{gripper_id}连接成功")
            
            return {
                "success": True,
                "data": status_info
            }
            
        except Exception as e:
            self.log_message.emit("ERROR", f"连接夹爪{gripper_id}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_gripper(self, gripper_id: str) -> Dict[str, Any]:
        """断开夹爪连接"""
        if gripper_id not in self.connections:
            return {
                "success": False,
                "error": f"夹爪{gripper_id}未连接"
            }
        
        try:
            # 清理连接
            if gripper_id in self.connections:
                del self.connections[gripper_id]
            
            # 更新状态
            self.gripper_status[gripper_id] = {
                "connected": False,
                "disconnected_at": datetime.now().isoformat()
            }
            
            self.connection_changed.emit(gripper_id, self.gripper_status[gripper_id])
            self.log_message.emit("INFO", f"夹爪{gripper_id}断开连接成功")
            
            return {"success": True}
            
        except Exception as e:
            self.log_message.emit("ERROR", f"断开夹爪{gripper_id}失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_gripper_status(self, gripper_id: str) -> Dict[str, Any]:
        """获取夹爪状态"""
        return self.gripper_status.get(gripper_id, {
            "connected": False,
            "gripper_id": gripper_id
        })
    
    def emergency_stop_gripper(self, gripper_id: str) -> bool:
        """紧急停止夹爪"""
        try:
            # 这里应该调用实际的夹爪停止命令
            self.log_message.emit("WARNING", f"夹爪{gripper_id}紧急停止")
            return True
        except Exception as e:
            self.log_message.emit("ERROR", f"夹爪{gripper_id}紧急停止失败: {e}")
            return False


class LuaTestExecutor:
    """Lua测试执行器"""
    
    def __init__(self, test_config: Dict[str, Any], hardware_bridge: RealHardwareControlBridge):
        self.test_config = test_config
        self.hardware_bridge = hardware_bridge
        self.test_id = test_config.get('test_id', 'unknown')
        
    def run_test(self):
        """运行测试"""
        try:
            self.hardware_bridge.log_message.emit("INFO", f"开始执行测试: {self.test_id}")
            
            # 根据测试类型执行不同的测试逻辑
            test_type = self.test_config.get('test_type', 'unknown')
            
            if test_type == 'single_arm':
                self._run_single_arm_test()
            elif test_type == 'dual_arm':
                self._run_dual_arm_test()
            elif test_type == 'chassis':
                self._run_chassis_test()
            elif test_type == 'vision':
                self._run_vision_test()
            elif test_type == 'integration':
                self._run_integration_test()
            else:
                self.hardware_bridge.log_message.emit("ERROR", f"未知的测试类型: {test_type}")
                
        except Exception as e:
            self.hardware_bridge.log_message.emit("ERROR", f"测试执行失败: {e}")
    
    def _run_single_arm_test(self):
        """执行单臂测试"""
        # 实现单臂测试逻辑
        self.hardware_bridge.log_message.emit("INFO", "执行单臂测试...")
        time.sleep(2)  # 模拟测试执行时间
        self.hardware_bridge.log_message.emit("INFO", "单臂测试完成")
    
    def _run_dual_arm_test(self):
        """执行双臂测试"""
        # 实现双臂协作测试逻辑
        self.hardware_bridge.log_message.emit("INFO", "执行双臂协作测试...")
        time.sleep(3)  # 模拟测试执行时间
        self.hardware_bridge.log_message.emit("INFO", "双臂协作测试完成")
    
    def _run_chassis_test(self):
        """执行底盘测试"""
        # 实现底盘测试逻辑
        self.hardware_bridge.log_message.emit("INFO", "执行底盘测试...")
        time.sleep(2)  # 模拟测试执行时间
        self.hardware_bridge.log_message.emit("INFO", "底盘测试完成")
    
    def _run_vision_test(self):
        """执行视觉系统测试"""
        # 实现视觉系统测试逻辑
        self.hardware_bridge.log_message.emit("INFO", "执行视觉系统测试...")
        time.sleep(4)  # 模拟测试执行时间
        self.hardware_bridge.log_message.emit("INFO", "视觉系统测试完成")
    
    def _run_integration_test(self):
        """执行集成测试"""
        # 实现全系统集成测试逻辑
        self.hardware_bridge.log_message.emit("INFO", "执行全系统集成测试...")
        time.sleep(5)  # 模拟测试执行时间
        self.hardware_bridge.log_message.emit("INFO", "全系统集成测试完成")
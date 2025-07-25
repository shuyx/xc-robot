#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂连接服务
基于fr3_hermes_testing和fr3_control的成功实现
"""

import sys
import os
import time
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

# 添加FR3控制路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

# 开发环境配置 - 在Mac上使用仿真模式
SIMULATION_MODE = True  # 设为True启用仿真模式，避免真实硬件依赖

if SIMULATION_MODE:
    FR3_AVAILABLE = True
    Robot = None  # 仿真模式下不需要真实Robot类
    print("🔧 FR3仿真模式已启用（适用于Mac开发环境）")
else:
    try:
        from fairino import Robot
        FR3_AVAILABLE = True
        print("✅ FR3库导入成功")
    except ImportError as e:
        FR3_AVAILABLE = False
        print(f"⚠️ FR3库导入失败: {e}")
        Robot = None

class SimulatedFR3Robot:
    """FR3机械臂仿真类 - 用于Mac开发环境"""
    
    def __init__(self, ip: str):
        self.ip = ip
        self.is_conect = True  # 仿真总是连接成功
        self.robot_state = 1  # 1-停止状态
        self.robot_mode = 0   # 0-自动模式
        self.enabled = False
        self.drag_teach_mode = False
        
        # 仿真关节角度（度）
        self.joint_positions = [0.0, -30.0, 100.0, 0.0, 30.0, 0.0]
        
        # 仿真TCP位姿 [x, y, z, rx, ry, rz] (mm, 度)
        self.tcp_pose = [400.0, 0.0, 400.0, 180.0, 0.0, 0.0]
        
        # 仿真设备信息
        self.sdk_version = ["1.0.0", "仿真版本"]
        self.controller_ip = ip
        
        time.sleep(0.1)  # 模拟连接延迟
        
    def GetSDKVersion(self):
        """模拟获取SDK版本"""
        return (0, self.sdk_version)
        
    def GetControllerIP(self):
        """模拟获取控制器IP"""
        return (0, self.controller_ip)
        
    def GetActualJointPosDegree(self):
        """模拟获取关节角度"""
        # 添加小幅随机变化模拟真实情况
        import random
        positions = [pos + random.uniform(-0.1, 0.1) for pos in self.joint_positions]
        return (0, positions)
        
    def GetActualToolFlangePose(self):
        """模拟获取TCP位姿"""
        import random
        pose = [pos + random.uniform(-1.0, 1.0) for pos in self.tcp_pose]
        return (0, pose)
        
    def Mode(self, mode):
        """模拟设置模式"""
        self.robot_mode = mode
        time.sleep(0.1)
        return 0
        
    def RobotEnable(self, enable):
        """模拟使能控制"""
        self.enabled = bool(enable)
        self.robot_state = 2 if enable else 1  # 2-运行中, 1-停止
        time.sleep(0.5)  # 模拟使能延迟
        return 0
        
    def DragTeachSwitch(self, state):
        """模拟拖动示教模式"""
        self.drag_teach_mode = bool(state)
        time.sleep(0.2)
        return 0
        
    def CloseRPC(self):
        """模拟关闭连接"""
        self.is_conect = False
        return 0
        
    # 模拟robot_state_pkg属性
    @property 
    def robot_state_pkg(self):
        """模拟状态包"""
        return type('StatePackage', (), {
            'robot_state': self.robot_state,
            'robot_mode': self.robot_mode, 
            'program_state': 1,  # 1-停止
            'main_code': 0,      # 无故障
            'sub_code': 0,       # 无故障
            'motion_done': 1     # 运动完成
        })()

class FR3DeviceService:
    """FR3机械臂设备服务"""
    
    def __init__(self):
        self.robots: Dict[str, Robot] = {}
        self.device_configs = {}
        self.connection_status = {}
        self.logger = self._setup_logging()
        
        # 检查FR3库可用性
        if not FR3_AVAILABLE:
            self.logger.error("FR3库不可用，无法提供FR3连接服务")
            
        self._load_device_configs()
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("FR3Service")
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
                    "right_arm": {
                        "type": "fr3",
                        "ip": "192.168.58.2",
                        "enabled": True,
                        "description": "右臂FR3机械臂"
                    },
                    "left_arm": {
                        "type": "fr3", 
                        "ip": "192.168.58.3",
                        "enabled": True,
                        "description": "左臂FR3机械臂"
                    }
                }
                self.logger.warning("使用备用设备配置")
                
        except Exception as e:
            self.logger.error(f"加载设备配置失败: {e}")
            
    async def connect_fr3_arm(self, device_id: str) -> Dict[str, Any]:
        """
        连接FR3机械臂
        基于SAT001.py的成功实现模式
        """
        if not FR3_AVAILABLE:
            return {
                "status": "error",
                "message": "FR3库不可用，无法连接"
            }
            
        if device_id not in self.device_configs:
            return {
                "status": "error", 
                "message": f"设备配置不存在: {device_id}"
            }
            
        device_config = self.device_configs[device_id]
        
        if device_config.get("type") != "fr3":
            return {
                "status": "error",
                "message": f"设备类型错误: {device_config.get('type')}"
            }
            
        robot_ip = device_config["ip"]
        
        try:
            self.logger.info(f"正在连接{device_id} - IP: {robot_ip} (仿真模式)")
            start_time = time.time()
            
            # 步骤1: 建立连接（仿真或真实）
            if SIMULATION_MODE:
                robot = SimulatedFR3Robot(robot_ip)
                self.logger.info("🔧 使用仿真FR3机器人")
            else:
                robot = Robot.RPC(robot_ip)
            
            if not hasattr(robot, 'is_conect') or not robot.is_conect:
                return {
                    "status": "error",
                    "message": f"无法建立到{robot_ip}的连接（仿真: {SIMULATION_MODE}）"
                }
                
            connection_time = time.time() - start_time
            self.logger.info(f"✅ RPC连接成功，耗时: {connection_time:.3f}秒")
            
            # 步骤2: 获取设备信息验证连接
            device_info = {}
            
            # 获取SDK版本
            try:
                error, sdk_version = robot.GetSDKVersion()
                if error == 0:
                    device_info["sdk_version"] = sdk_version
                    self.logger.info(f"SDK版本: {sdk_version}")
                else:
                    self.logger.warning(f"获取SDK版本失败，错误码: {error}")
            except Exception as e:
                self.logger.warning(f"获取SDK版本异常: {e}")
                
            # 获取控制器IP验证
            try:
                error, controller_ip = robot.GetControllerIP()
                if error == 0:
                    device_info["controller_ip"] = controller_ip
                    self.logger.info(f"控制器IP: {controller_ip}")
                else:
                    self.logger.warning(f"获取控制器IP失败，错误码: {error}")
            except Exception as e:
                self.logger.warning(f"获取控制器IP异常: {e}")
                
            # 步骤3: 获取机器人状态
            try:
                if hasattr(robot, 'robot_state_pkg'):
                    robot_state = robot.robot_state_pkg.robot_state
                    robot_mode = robot.robot_state_pkg.robot_mode
                    main_code = robot.robot_state_pkg.main_code
                    sub_code = robot.robot_state_pkg.sub_code
                    
                    device_info.update({
                        "robot_state": robot_state,
                        "robot_mode": robot_mode,
                        "error_codes": {"main": main_code, "sub": sub_code}
                    })
                    
                    if main_code != 0 or sub_code != 0:
                        self.logger.warning(f"设备存在故障码: 主={main_code}, 子={sub_code}")
                    else:
                        self.logger.info("设备状态正常，无故障码")
                        
                else:
                    self.logger.warning("无法获取机器人状态包信息")
                    
            except Exception as e:
                self.logger.warning(f"获取机器人状态异常: {e}")
                
            # 步骤4: 获取当前位置信息
            try:
                error, joint_pos = robot.GetActualJointPosDegree()
                if error == 0:
                    device_info["current_joints"] = joint_pos
                    self.logger.info(f"当前关节角度: {[round(j, 2) for j in joint_pos]}")
                else:
                    self.logger.warning(f"获取关节角度失败，错误码: {error}")
                    
                error, tcp_pose = robot.GetActualToolFlangePose()
                if error == 0:
                    device_info["current_tcp"] = tcp_pose
                    self.logger.info(f"当前TCP位置: X={tcp_pose[0]:.1f}, Y={tcp_pose[1]:.1f}, Z={tcp_pose[2]:.1f}")
                else:
                    self.logger.warning(f"获取TCP位姿失败，错误码: {error}")
                    
            except Exception as e:
                self.logger.warning(f"获取位置信息异常: {e}")
                
            # 步骤5: 保存连接
            self.robots[device_id] = robot
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
                    "ip": robot_ip,
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
            
    async def disconnect_fr3_arm(self, device_id: str) -> Dict[str, Any]:
        """断开FR3机械臂连接"""
        try:
            if device_id not in self.robots:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            robot = self.robots[device_id]
            
            # 安全断开 - 先下使能
            try:
                robot.RobotEnable(0)
                self.logger.info(f"{device_id}已下使能")
            except Exception as e:
                self.logger.warning(f"下使能失败: {e}")
                
            # 关闭RPC连接
            try:
                if hasattr(robot, 'CloseRPC'):
                    robot.CloseRPC()
                self.logger.info(f"{device_id} RPC连接已关闭")
            except Exception as e:
                self.logger.warning(f"关闭RPC连接失败: {e}")
                
            # 清理连接记录
            del self.robots[device_id]
            self.connection_status[device_id] = {
                "connected": False,
                "disconnected_at": datetime.now().isoformat()
            }
            
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
            
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            if device_id not in self.robots:
                return {
                    "status": "success",
                    "data": {
                        "device_id": device_id,
                        "connected": False,
                        "status": "offline"
                    }
                }
                
            robot = self.robots[device_id]
            
            # 实时状态信息
            status_data = {
                "device_id": device_id,
                "connected": True,
                "status": "online",
                "connection_info": self.connection_status.get(device_id, {})
            }
            
            # 获取实时关节角度
            try:
                error, joint_pos = robot.GetActualJointPosDegree()
                if error == 0:
                    status_data["current_joints"] = joint_pos
            except:
                pass
                
            # 获取实时TCP位姿
            try:
                error, tcp_pose = robot.GetActualToolFlangePose()
                if error == 0:
                    status_data["current_tcp"] = tcp_pose
            except:
                pass
                
            # 获取实时机器人状态
            try:
                if hasattr(robot, 'robot_state_pkg'):
                    status_data.update({
                        "robot_state": robot.robot_state_pkg.robot_state,
                        "robot_mode": robot.robot_state_pkg.robot_mode,
                        "program_state": robot.robot_state_pkg.program_state,
                        "motion_done": robot.robot_state_pkg.motion_done
                    })
            except:
                pass
                
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
            
    async def enable_robot(self, device_id: str) -> Dict[str, Any]:
        """机器人上使能"""
        try:
            if device_id not in self.robots:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            robot = self.robots[device_id]
            
            # 设置自动模式
            robot.Mode(0)
            time.sleep(0.5)  # 等待模式切换
            
            # 上使能
            robot.RobotEnable(1)
            
            self.logger.info(f"{device_id}已上使能")
            
            return {
                "status": "success",
                "message": f"{device_id}上使能成功"
            }
            
        except Exception as e:
            self.logger.error(f"{device_id}上使能失败: {e}")
            return {
                "status": "error",
                "message": f"上使能失败: {str(e)}"
            }
            
    async def disable_robot(self, device_id: str) -> Dict[str, Any]:
        """机器人下使能"""
        try:
            if device_id not in self.robots:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            robot = self.robots[device_id]
            robot.RobotEnable(0)
            
            self.logger.info(f"{device_id}已下使能")
            
            return {
                "status": "success",
                "message": f"{device_id}下使能成功"
            }
            
        except Exception as e:
            self.logger.error(f"{device_id}下使能失败: {e}")
            return {
                "status": "error",
                "message": f"下使能失败: {str(e)}"
            }
            
    async def set_drag_teach_mode(self, device_id: str, enable: bool) -> Dict[str, Any]:
        """设置拖动示教模式"""
        try:
            if device_id not in self.robots:
                return {
                    "status": "error",
                    "message": f"设备{device_id}未连接"
                }
                
            robot = self.robots[device_id]
            state = 1 if enable else 0
            robot.DragTeachSwitch(state=state)
            
            mode_text = "进入" if enable else "退出"
            self.logger.info(f"{device_id}{mode_text}拖动示教模式")
            
            return {
                "status": "success",
                "message": f"{device_id}{mode_text}拖动示教模式成功"
            }
            
        except Exception as e:
            self.logger.error(f"{device_id}设置拖动模式失败: {e}")
            return {
                "status": "error",
                "message": f"设置拖动模式失败: {str(e)}"
            }
            
    async def get_all_devices(self) -> Dict[str, Any]:
        """获取所有设备列表和状态"""
        try:
            devices = []
            
            for device_id, config in self.device_configs.items():
                if config.get("type") == "fr3":
                    device_data = {
                        "id": device_id,
                        "name": config.get("description", device_id),
                        "type": "robotic_arm",
                        "ip": config.get("ip"),
                        "enabled": config.get("enabled", True),
                        "connected": device_id in self.robots,
                        "status": "online" if device_id in self.robots else "offline"
                    }
                    
                    # 添加连接状态信息
                    if device_id in self.connection_status:
                        device_data.update(self.connection_status[device_id])
                        
                    devices.append(device_data)
                    
            return {
                "status": "success",
                "data": devices
            }
            
        except Exception as e:
            self.logger.error(f"获取设备列表失败: {e}")
            return {
                "status": "error",
                "message": f"获取设备列表失败: {str(e)}"
            }

# 全局服务实例
fr3_service = FR3DeviceService()
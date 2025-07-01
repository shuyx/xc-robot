#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 整合机器人控制程序
结合Hermes轮式底盘和FR3双臂的完整控制系统
实现你描述的完整工作流程：
1. 控制hermes移动到某个位置，并旋转到合适姿态
2. 机械臂启动，左右两个机械臂分别完成不同动作
3. 机器人移动到初始位置，等待下一次指令
"""

import sys
import os
import time
import json
import requests
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# 添加路径
project_root = os.path.dirname(os.path.abspath(__file__))
fr3_control_path = os.path.join(project_root, 'fr3_control')
main_control_path = os.path.join(project_root, 'main_control')

sys.path.insert(0, fr3_control_path)
sys.path.insert(0, main_control_path)

# 导入控制模块
try:
    from fairino import Robot
    FR3_AVAILABLE = True
    print("✅ FR3库导入成功")
except ImportError as e:
    FR3_AVAILABLE = False
    print(f"⚠️  FR3库导入失败: {e}")

class Logger:
    """简单的日志记录器"""
    
    def __init__(self, name: str = "XC-ROBOT"):
        self.name = name
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] [{self.name}] {message}")
    
    def info(self, message: str):
        self.log(message, "INFO")
    
    def warning(self, message: str):
        self.log(message, "WARNING")
    
    def error(self, message: str):
        self.log(message, "ERROR")

class HermesController:
    """Hermes底盘控制器"""
    
    def __init__(self, base_url: str = "http://192.168.1.100"):
        """
        初始化Hermes控制器
        
        Args:
            base_url (str): Hermes底盘的HTTP API地址
        """
        self.base_url = base_url.rstrip('/')
        self.logger = Logger("HERMES")
        self.connected = False
        
        # 预定义位置点（示例）
        self.positions = {
            "home": {"x": 0.0, "y": 0.0, "theta": 0.0},
            "work_station_1": {"x": 2.0, "y": 1.0, "theta": 90.0},
            "work_station_2": {"x": -1.5, "y": 2.0, "theta": -45.0},
            "charging_station": {"x": 0.5, "y": -1.0, "theta": 180.0}
        }
    
    def test_connection(self) -> bool:
        """测试与Hermes底盘的连接"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                self.connected = True
                self.logger.info("Hermes底盘连接成功")
                return True
            else:
                self.logger.error(f"Hermes底盘响应异常: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Hermes底盘连接失败: {e}")
            self.connected = False
            return False
    
    def move_to_position(self, position_name: str) -> bool:
        """
        移动到预定义位置
        
        Args:
            position_name (str): 位置名称
            
        Returns:
            bool: 移动是否成功
        """
        if not self.connected:
            self.logger.error("Hermes底盘未连接")
            return False
        
        if position_name not in self.positions:
            self.logger.error(f"未知位置: {position_name}")
            return False
        
        target = self.positions[position_name]
        return self.move_to_coordinate(target["x"], target["y"], target["theta"])
    
    def move_to_coordinate(self, x: float, y: float, theta: float) -> bool:
        """
        移动到指定坐标
        
        Args:
            x (float): X坐标 (米)
            y (float): Y坐标 (米)
            theta (float): 角度 (度)
            
        Returns:
            bool: 移动是否成功
        """
        if not self.connected:
            self.logger.error("Hermes底盘未连接")
            return False
        
        try:
            command = {
                "command": "move_to",
                "x": x,
                "y": y,
                "theta": theta,
                "velocity": 0.5  # 适中速度
            }
            
            self.logger.info(f"移动到坐标: x={x}, y={y}, theta={theta}°")
            
            response = requests.post(
                f"{self.base_url}/move",
                json=command,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("移动指令发送成功")
                return True
            else:
                self.logger.error(f"移动指令失败: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"移动指令异常: {e}")
            return False
    
    def wait_for_arrival(self, timeout: int = 60) -> bool:
        """
        等待到达目标位置
        
        Args:
            timeout (int): 超时时间（秒）
            
        Returns:
            bool: 是否成功到达
        """
        if not self.connected:
            return False
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/status", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    if status.get("motion_done", False):
                        self.logger.info("已到达目标位置")
                        return True
                
                time.sleep(1)
                
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        self.logger.warning("等待到达目标位置超时")
        return False
    
    def stop(self) -> bool:
        """停止底盘运动"""
        if not self.connected:
            return False
        
        try:
            response = requests.post(f"{self.base_url}/stop", timeout=5)
            if response.status_code == 200:
                self.logger.info("底盘已停止")
                return True
            else:
                self.logger.error("停止指令失败")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"停止指令异常: {e}")
            return False

class FR3ArmController:
    """FR3机械臂控制器"""
    
    def __init__(self, ip: str, name: str):
        """
        初始化FR3机械臂控制器
        
        Args:
            ip (str): 机械臂IP地址
            name (str): 机械臂名称
        """
        self.ip = ip
        self.name = name
        self.robot = None
        self.connected = False
        self.enabled = False
        self.logger = Logger(f"FR3-{name}")
        
        # 预定义动作序列
        self.actions = {
            "home": [0.0, -20.0, -90.0, -90.0, 90.0, 0.0],
            "pick_ready": [30.0, -30.0, -120.0, -60.0, 90.0, 0.0],
            "pick_down": [30.0, -10.0, -140.0, -30.0, 90.0, 0.0],
            "place_ready": [-30.0, -30.0, -120.0, -60.0, 90.0, 0.0],
            "place_down": [-30.0, -10.0, -140.0, -30.0, 90.0, 0.0],
            "wave": [0.0, -45.0, -90.0, -45.0, 90.0, 45.0]
        }
    
    def connect(self) -> bool:
        """连接机械臂"""
        if not FR3_AVAILABLE:
            self.logger.error("FR3库不可用")
            return False
        
        try:
            self.logger.info(f"正在连接机械臂 ({self.ip})...")
            self.robot = Robot.RPC(self.ip)
            self.connected = True
            
            # 测试连接
            try:
                sdk_version = self.robot.GetSDKVersion()
                self.logger.info(f"连接成功，SDK版本: {sdk_version}")
            except Exception as test_e:
                self.logger.warning(f"连接成功但API测试失败: {test_e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            self.connected = False
            return False
    
    def initialize(self) -> bool:
        """初始化机械臂（设置模式和使能）"""
        if not self.connected:
            self.logger.error("机械臂未连接")
            return False
        
        try:
            # 设置自动模式
            ret = self.robot.Mode(0)
            if ret != 0:
                self.logger.error(f"设置自动模式失败，错误码: {ret}")
                return False
            
            time.sleep(1)
            
            # 上使能
            ret = self.robot.RobotEnable(1)
            if ret != 0:
                self.logger.error(f"使能失败，错误码: {ret}")
                return False
            
            self.enabled = True
            self.logger.info("机械臂初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化异常: {e}")
            return False
    
    def execute_action(self, action_name: str, velocity: int = 20) -> bool:
        """
        执行预定义动作
        
        Args:
            action_name (str): 动作名称
            velocity (int): 速度百分比
            
        Returns:
            bool: 执行是否成功
        """
        if not self.connected or not self.enabled:
            self.logger.error("机械臂未连接或未使能")
            return False
        
        if action_name not in self.actions:
            self.logger.error(f"未知动作: {action_name}")
            return False
        
        joint_pos = self.actions[action_name]
        return self.move_joint(joint_pos, velocity)
    
    def move_joint(self, joint_pos: List[float], velocity: int = 20) -> bool:
        """
        关节运动
        
        Args:
            joint_pos (List[float]): 关节位置
            velocity (int): 速度百分比
            
        Returns:
            bool: 运动是否成功
        """
        if not self.connected or not self.enabled:
            self.logger.error("机械臂未连接或未使能")
            return False
        
        try:
            self.logger.info(f"执行关节运动: {joint_pos}")
            ret = self.robot.MoveJ(
                joint_pos=joint_pos,
                tool=0,
                user=0,
                vel=velocity
            )
            
            if ret == 0:
                self.logger.info("运动指令发送成功")
                return True
            else:
                self.logger.error(f"运动失败，错误码: {ret}")
                return False
                
        except Exception as e:
            self.logger.error(f"运动异常: {e}")
            return False
    
    def wait_motion_done(self, timeout: int = 30) -> bool:
        """等待运动完成"""
        if not self.connected:
            return False
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                motion_done = self.robot.GetRobotMotionDone()
                if motion_done:
                    self.logger.info("运动完成")
                    return True
            except:
                # API不可用时使用固定等待
                time.sleep(2)
                return True
            
            time.sleep(0.1)
        
        self.logger.warning("等待运动完成超时")
        return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.robot and self.connected:
                self.robot.CloseRPC()
                self.logger.info("连接已断开")
            self.connected = False
            self.enabled = False
        except Exception as e:
            self.logger.error(f"断开连接异常: {e}")

class XCRobotController:
    """XC-ROBOT 整合控制器"""
    
    def __init__(self):
        """初始化XC-ROBOT控制器"""
        self.logger = Logger("XC-ROBOT")
        
        # 初始化子系统
        self.hermes = HermesController("http://192.168.1.100")
        self.right_arm = FR3ArmController("192.168.58.2", "右臂")
        self.left_arm = FR3ArmController("192.168.58.3", "左臂")
        
        # 系统状态
        self.initialized = False
        self.task_running = False
        
        self.logger.info("XC-ROBOT控制器初始化完成")
    
    def initialize_system(self) -> bool:
        """初始化整个系统"""
        self.logger.info("开始初始化XC-ROBOT系统...")
        
        # 1. 测试Hermes底盘连接
        hermes_ok = self.hermes.test_connection()
        
        # 2. 连接双臂
        right_arm_ok = self.right_arm.connect()
        left_arm_ok = self.left_arm.connect()
        
        # 3. 初始化机械臂
        if right_arm_ok:
            right_arm_ok = self.right_arm.initialize()
        
        if left_arm_ok:
            left_arm_ok = self.left_arm.initialize()
        
        # 评估初始化结果
        subsystems = {
            "Hermes底盘": hermes_ok,
            "右臂机械臂": right_arm_ok,
            "左臂机械臂": left_arm_ok
        }
        
        success_count = sum(subsystems.values())
        total_count = len(subsystems)
        
        self.logger.info(f"子系统初始化结果: {success_count}/{total_count}")
        for system, status in subsystems.items():
            status_text = "✅ 成功" if status else "❌ 失败"
            self.logger.info(f"  {system}: {status_text}")
        
        # 至少需要一个子系统成功
        self.initialized = success_count > 0
        
        if self.initialized:
            self.logger.info("🎉 XC-ROBOT系统初始化成功")
        else:
            self.logger.error("❌ XC-ROBOT系统初始化失败")
        
        return self.initialized
    
    def execute_work_task(self, work_station: str = "work_station_1", 
                         right_arm_action: str = "pick_ready",
                         left_arm_action: str = "wave") -> bool:
        """
        执行完整工作任务
        
        Args:
            work_station (str): 工作站位置
            right_arm_action (str): 右臂动作
            left_arm_action (str): 左臂动作
            
        Returns:
            bool: 任务执行是否成功
        """
        if not self.initialized:
            self.logger.error("系统未初始化")
            return False
        
        if self.task_running:
            self.logger.error("任务正在运行中")
            return False
        
        self.task_running = True
        self.logger.info("🚀 开始执行工作任务")
        
        try:
            # 步骤1: 控制hermes移动到某个位置，并旋转到合适姿态
            self.logger.info(f"步骤1: 移动到工作位置 ({work_station})")
            if self.hermes.connected:
                if not self.hermes.move_to_position(work_station):
                    self.logger.error("底盘移动失败")
                    return False
                
                # 等待到达
                if not self.hermes.wait_for_arrival(timeout=60):
                    self.logger.error("等待到达超时")
                    return False
                
                self.logger.info("✅ 已到达工作位置")
            else:
                self.logger.warning("Hermes底盘不可用，跳过移动")
            
            time.sleep(1)  # 稳定时间
            
            # 步骤2: 机械臂启动，左右两个机械臂分别完成不同的动作
            self.logger.info("步骤2: 执行双臂协调动作")
            
            arm_threads = []
            arm_results = {}
            
            # 右臂动作
            if self.right_arm.connected and self.right_arm.enabled:
                def right_arm_task():
                    self.logger.info(f"右臂开始执行动作: {right_arm_action}")
                    success = self.right_arm.execute_action(right_arm_action)
                    if success:
                        success = self.right_arm.wait_motion_done()
                    arm_results['right'] = success
                
                right_thread = threading.Thread(target=right_arm_task)
                arm_threads.append(right_thread)
                right_thread.start()
            
            # 左臂动作
            if self.left_arm.connected and self.left_arm.enabled:
                def left_arm_task():
                    self.logger.info(f"左臂开始执行动作: {left_arm_action}")
                    success = self.left_arm.execute_action(left_arm_action)
                    if success:
                        success = self.left_arm.wait_motion_done()
                    arm_results['left'] = success
                
                left_thread = threading.Thread(target=left_arm_task)
                arm_threads.append(left_thread)
                left_thread.start()
            
            # 等待所有机械臂动作完成
            for thread in arm_threads:
                thread.join()
            
            # 检查动作结果
            successful_arms = sum(arm_results.values())
            total_arms = len(arm_results)
            
            if successful_arms > 0:
                self.logger.info(f"✅ 机械臂动作完成 ({successful_arms}/{total_arms})")
            else:
                self.logger.error("❌ 所有机械臂动作失败")
                return False
            
            time.sleep(2)  # 动作完成后的稳定时间
            
            # 步骤3: 机器人移动到初始位置，等待下一次指令
            self.logger.info("步骤3: 返回初始位置")
            
            # 先让机械臂回到安全位置
            if self.right_arm.connected and self.right_arm.enabled:
                self.right_arm.execute_action("home")
            
            if self.left_arm.connected and self.left_arm.enabled:
                self.left_arm.execute_action("home")
            
            # 等待机械臂回到安全位置
            time.sleep(3)
            
            # 底盘返回初始位置
            if self.hermes.connected:
                if not self.hermes.move_to_position("home"):
                    self.logger.error("返回初始位置失败")
                    return False
                
                if not self.hermes.wait_for_arrival(timeout=60):
                    self.logger.error("等待返回初始位置超时")
                    return False
                
                self.logger.info("✅ 已返回初始位置")
            else:
                self.logger.warning("Hermes底盘不可用，跳过返回")
            
            self.logger.info("🎉 工作任务执行完成")
            return True
            
        except Exception as e:
            self.logger.error(f"任务执行异常: {e}")
            return False
        finally:
            self.task_running = False
    
    def emergency_stop(self) -> bool:
        """紧急停止所有运动"""
        self.logger.warning("⚠️  执行紧急停止")
        
        results = []
        
        # 停止底盘
        if self.hermes.connected:
            results.append(self.hermes.stop())
        
        # 停止机械臂
        if self.right_arm.connected:
            try:
                self.right_arm.robot.StopMotion()
                results.append(True)
            except:
                results.append(False)
        
        if self.left_arm.connected:
            try:
                self.left_arm.robot.StopMotion()
                results.append(True)
            except:
                results.append(False)
        
        success = any(results)
        if success:
            self.logger.info("✅ 紧急停止执行成功")
        else:
            self.logger.error("❌ 紧急停止执行失败")
        
        return success
    
    def shutdown_system(self):
        """关闭系统"""
        self.logger.info("正在关闭XC-ROBOT系统...")
        
        # 断开机械臂连接
        self.right_arm.disconnect()
        self.left_arm.disconnect()
        
        self.logger.info("✅ XC-ROBOT系统已关闭")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "initialized": self.initialized,
            "task_running": self.task_running,
            "hermes": {
                "connected": self.hermes.connected
            },
            "right_arm": {
                "connected": self.right_arm.connected,
                "enabled": self.right_arm.enabled
            },
            "left_arm": {
                "connected": self.left_arm.connected,
                "enabled": self.left_arm.enabled
            }
        }
    
    def run_interactive_mode(self):
        """运行交互模式"""
        self.logger.info("启动XC-ROBOT交互控制模式")
        
        if not self.initialized:
            self.logger.error("系统未初始化，请先初始化系统")
            return
        
        while True:
            print("\n" + "="*60)
            print("XC-ROBOT 交互控制菜单")
            print("="*60)
            print("1. 查看系统状态")
            print("2. 执行标准工作任务")
            print("3. 执行自定义任务")
            print("4. 测试单个子系统")
            print("5. 紧急停止")
            print("6. 退出系统")
            print("="*60)
            
            try:
                choice = input("请选择操作 (1-6): ").strip()
                
                if choice == "1":
                    self._show_system_status()
                elif choice == "2":
                    self._execute_standard_task()
                elif choice == "3":
                    self._execute_custom_task()
                elif choice == "4":
                    self._test_subsystem()
                elif choice == "5":
                    self.emergency_stop()
                elif choice == "6":
                    print("正在退出...")
                    break
                else:
                    print("无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n用户中断操作")
                break
            except Exception as e:
                self.logger.error(f"交互模式异常: {e}")
    
    def _show_system_status(self):
        """显示系统状态"""
        status = self.get_system_status()
        
        print("\n📊 系统状态:")
        print(f"  系统初始化: {'✅ 是' if status['initialized'] else '❌ 否'}")
        print(f"  任务运行中: {'✅ 是' if status['task_running'] else '❌ 否'}")
        print(f"  Hermes底盘: {'✅ 连接' if status['hermes']['connected'] else '❌ 断开'}")
        print(f"  右臂机械臂: {'✅ 连接' if status['right_arm']['connected'] else '❌ 断开'} / {'✅ 使能' if status['right_arm']['enabled'] else '❌ 未使能'}")
        print(f"  左臂机械臂: {'✅ 连接' if status['left_arm']['connected'] else '❌ 断开'} / {'✅ 使能' if status['left_arm']['enabled'] else '❌ 未使能'}")
    
    def _execute_standard_task(self):
        """执行标准任务"""
        print("\n🚀 执行标准工作任务")
        print("任务流程:")
        print("1. 移动到work_station_1")
        print("2. 右臂执行pick_ready动作，左臂执行wave动作")
        print("3. 返回初始位置")
        
        confirm = input("确认执行？(y/N): ").strip().lower()
        if confirm == 'y':
            success = self.execute_work_task()
            if success:
                print("✅ 标准任务执行成功")
            else:
                print("❌ 标准任务执行失败")
        else:
            print("任务已取消")
    
    def _execute_custom_task(self):
        """执行自定义任务"""
        print("\n⚙️  自定义任务配置")
        
        # 选择工作站
        stations = list(self.hermes.positions.keys())
        print(f"可用工作站: {', '.join(stations)}")
        work_station = input(f"选择工作站 (默认: work_station_1): ").strip()
        if not work_station:
            work_station = "work_station_1"
        
        # 选择右臂动作
        actions = list(self.right_arm.actions.keys())
        print(f"可用动作: {', '.join(actions)}")
        right_action = input(f"右臂动作 (默认: pick_ready): ").strip()
        if not right_action:
            right_action = "pick_ready"
        
        # 选择左臂动作
        left_action = input(f"左臂动作 (默认: wave): ").strip()
        if not left_action:
            left_action = "wave"
        
        print(f"\n任务配置:")
        print(f"  工作站: {work_station}")
        print(f"  右臂动作: {right_action}")
        print(f"  左臂动作: {left_action}")
        
        confirm = input("确认执行？(y/N): ").strip().lower()
        if confirm == 'y':
            success = self.execute_work_task(work_station, right_action, left_action)
            if success:
                print("✅ 自定义任务执行成功")
            else:
                print("❌ 自定义任务执行失败")
        else:
            print("任务已取消")
    
    def _test_subsystem(self):
        """测试子系统"""
        print("\n🔧 子系统测试")
        print("1. 测试Hermes底盘")
        print("2. 测试右臂机械臂")
        print("3. 测试左臂机械臂")
        
        choice = input("选择测试子系统 (1-3): ").strip()
        
        if choice == "1":
            self._test_hermes()
        elif choice == "2":
            self._test_arm(self.right_arm)
        elif choice == "3":
            self._test_arm(self.left_arm)
        else:
            print("无效选择")
    
    def _test_hermes(self):
        """测试Hermes底盘"""
        if not self.hermes.connected:
            print("❌ Hermes底盘未连接")
            return
        
        print("测试Hermes底盘移动...")
        stations = ["work_station_1", "work_station_2", "home"]
        
        for station in stations:
            print(f"移动到 {station}...")
            if self.hermes.move_to_position(station):
                if self.hermes.wait_for_arrival(30):
                    print(f"✅ 成功到达 {station}")
                else:
                    print(f"⚠️  到达 {station} 超时")
            else:
                print(f"❌ 移动到 {station} 失败")
            time.sleep(2)
    
    def _test_arm(self, arm: FR3ArmController):
        """测试机械臂"""
        if not arm.connected or not arm.enabled:
            print(f"❌ {arm.name}未连接或未使能")
            return
        
        print(f"测试{arm.name}动作...")
        test_actions = ["home", "wave", "home"]
        
        for action in test_actions:
            print(f"{arm.name}执行动作: {action}")
            if arm.execute_action(action):
                if arm.wait_motion_done():
                    print(f"✅ {arm.name}动作 {action} 完成")
                else:
                    print(f"⚠️  {arm.name}动作 {action} 超时")
            else:
                print(f"❌ {arm.name}动作 {action} 失败")
            time.sleep(1)

def main():
    """主函数"""
    print("=" * 70)
    print("    XC-ROBOT 轮式双臂类人形机器人控制系统")
    print("    整合Hermes底盘 + FR3双臂控制")
    print("=" * 70)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 创建控制器实例
    robot_controller = XCRobotController()
    
    try:
        # 初始化系统
        print("\n🔧 正在初始化XC-ROBOT系统...")
        if not robot_controller.initialize_system():
            print("❌ 系统初始化失败，请检查硬件连接和配置")
            return 1
        
        # 询问运行模式
        print("\n" + "="*50)
        print("选择运行模式:")
        print("1. 交互控制模式")
        print("2. 执行一次标准任务后退出")
        print("3. 仅测试系统状态后退出")
        
        mode = input("请选择 (1-3): ").strip()
        
        if mode == "1":
            # 交互模式
            robot_controller.run_interactive_mode()
        elif mode == "2":
            # 执行标准任务
            print("\n🚀 执行标准工作任务...")
            success = robot_controller.execute_work_task()
            if success:
                print("✅ 任务执行成功")
                return 0
            else:
                print("❌ 任务执行失败")
                return 1
        elif mode == "3":
            # 仅测试状态
            robot_controller._show_system_status()
            return 0
        else:
            print("无效选择")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断程序")
        robot_controller.emergency_stop()
        return 1
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        robot_controller.emergency_stop()
        return 1
    finally:
        # 确保系统正确关闭
        robot_controller.shutdown_system()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

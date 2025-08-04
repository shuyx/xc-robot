#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂+底盘联合控制脚本
结合FR3机械臂SDK和Hermes底盘API控制
支持自定义机械臂点位、底盘POI点位和运动序列
"""
import asyncio
import httpx
import json
import math
from datetime import datetime
import sys
import os
import time

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

sys.path.insert(0, project_root)

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
except ImportError as e:
    print(f"❌ fairino库导入失败: {e}")
    sys.exit(1)

# ==================== USER_CONFIG 用户配置区域 ====================
# 👇 在这里自定义你的目标点位和运动序列 👇

# 定义目标点位配置
USER_ARM_POINTS = {
    # 示例点位1: 使用关节运动 (MoveJ)
    "point11": {
        "type": "joint",  # cartesian: 笛卡尔运动, joint: 关节运动, linear: 直线运动
        "position": [-44.6, -30.88, 66.55, -16.23, 156.8, 27.2],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "MoveJ",
        "speed": 50.0,  # 自定义速度
        "wait_time": 0,  # 到达后停留时间(秒)
        "description": "工作台上方位置"
    },
    
    # 示例点位2: 使用关节运动 (MoveJ) - 快速移动
    "point55": {
        "type": "joint",      # joint: 关节运动
        "position": [-65.17, -13.97, 23.61, -6.89, 112.04, 21.42],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "MoveJ",
        "speed": 50.0,  # 快速移动
        "wait_time": 0,  # 停留1秒
        "description": "边缘位置(关节运动)"
    },
     # 你可以添加更多点位...
     "point66": {
         #当前TCP位置: X=-319.4, Y=-61.1, Z=-308.8
         #当前TCP姿态: RX=97.9, RY=69.6, RZ=-85.1
         "type": "joint",
         "position": [-51.63, -45.04, 90.41, -42.24, 125.56, 22.21],
         "method": "MoveJ",
         "speed": 100.0,  # 快速移动 - 修正到合理范围
         "wait_time": 0,  # 短停留
         "description": "边缘位置(关节运动)"
    },
    # 示例点位: 使用关节运动 (MoveJ) - 中速
    "point77": {
        "type": "joint",      # joint: 关节运动
        "position": [-51.63, -45.04, 90.41, -42.24, 99.61, 22.21],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "MoveJ",
        "speed": 100.0,  # 中速移动 - 修正到合理范围
        "wait_time": 0,  # 很短停留
        "description": "边缘位置(关节运动)"
    },
 # 示例点位: 使用关节运动 (MoveJ) - 不设置停留时间(使用默认)
    "point33": {
        #TCP位置: X=-517.5, Y=-292.2, Z=-11.2
        #TCP姿态: RX=94.3, RY=-9.5, RZ=-93.8
        #关节角度[23.98, -3.98, 18.84, -10.07, 116.95, 11.67]
        "type": "linear",      # joint: 关节运动
        "position": [-517.5, -292.2, -11.2, 94.3, -9.5, -93.8],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "ServoCart",
        "speed": 5.0,  # 中等速度
        "wait_time": 0.3,  # 不设置wait_time则使用默认停留时间
        "description": "边缘位置(关节运动)"
    },
    # 示例点位: 使用关节运动 (MoveJ) - 快速
    "point44": {
        #TCP位置: X=-530.0, Y=286.4, Z=-13.4
        #TCP姿态: RX=94.7, RY=-9.4, RZ=-93.8
        #关节角度[-44.58, -1.03, 12.79, -5.56, 48.64, 5.32]
        "type": "linear",      # joint: 关节运动
        "position":  [-530.0, 286.4, -13.4, 94.7, -9.4, -93.8],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "ServoCart",
        "speed": 5.0,  # 中等速度
        "wait_time": 0.3,  # 停留1.5秒
        "description": "边缘位置(关节运动)"
    },
}

# 联合运动序列配置
# 格式说明：
# - 字符串格式 "arm:point_name" : 机械臂动作
# - 字符串格式 "chassis:poi_name" : 底盘导航  
# - 字典格式 {"wait": 毫秒数} : 等待时间
USER_MOTION_SEQUENCE = [
     "chassis:2",           # 底盘导航到POI "2"
    "arm:point11",           # 机械臂到point1
    "arm:point55",          # 机械臂到point11
    "arm:point66",         
    "arm:point77",          # 机械臂到point22,
    "arm:point66",
    "arm:point77",
    "arm:point66",          # 机械臂到point44
    "arm:point33",
    "arm:point44",
    "arm:point33",
    "arm:point44",
    "arm:point11"
]
# ==================== END USER_CONFIG 配置区域结束 ====================

# 从机械臂程序移植的伺服运动参数
SERVO_CYCLE_TIME = 0.008
SERVO_VELOCITY = 15.0
INTERPOLATION_STEPS = 200

class CombinedRobotController:
    """机械臂+底盘联合控制器"""
    
    def __init__(self, chassis_ip="192.168.31.211", chassis_port=1448):
        # 机械臂相关
        self.robot = None
        self.is_arm_connected = False
        self.is_arm_enabled = False
        self.arm_points = USER_ARM_POINTS
        
        # 底盘相关
        self.chassis_ip = chassis_ip
        self.chassis_port = chassis_port
        self.chassis_base_url = f"http://{chassis_ip}:{chassis_port}"
        self.chassis_client = None
        self.is_chassis_connected = False
        self.chassis_pois = {}
        
        # 运动序列
        self.motion_sequence = USER_MOTION_SEQUENCE
        
        print(f"🤖 联合控制器初始化")
        print(f"🦾 机械臂IP: 192.168.58.2")
        print(f"🚗 底盘地址: {self.chassis_base_url}")
    
    # ==================== 机械臂控制部分 (从fr3_custom_motion.py移植) ====================
    
    def connect_arm(self):
        """连接机械臂"""
        try:
            print(f"🔗 正在连接机械臂...")
            self.robot = Robot.RPC('192.168.58.2')
            
            if not hasattr(self.robot, 'is_conect') or not self.robot.is_conect:
                print("❌ 机械臂连接失败")
                return False
            
            print("✅ 机械臂连接成功")
            self.is_arm_connected = True
            return True
            
        except Exception as e:
            print(f"❌ 机械臂连接异常: {e}")
            return False
    
    def enable_arm(self):
        """使能机械臂"""
        if not self.is_arm_connected:
            print("❌ 机械臂未连接")
            return False
        
        try:
            print(f"⚡ 准备机械臂运动...")
            
            ret = self.robot.Mode(0)
            if ret != 0:
                print(f"❌ 设置自动模式失败，错误码: {ret}")
                return False
            print("✅ 已切换到自动模式")
            
            time.sleep(0.5)
            
            ret = self.robot.RobotEnable(1)
            if ret != 0:
                print(f"❌ 使能失败，错误码: {ret}")
                return False
            print("✅ 机械臂已使能")
            
            time.sleep(1.5)
            self.is_arm_enabled = True
            return True
            
        except Exception as e:
            print(f"❌ 机械臂使能异常: {e}")
            return False
    
    def get_current_arm_position(self):
        """获取当前TCP位置和关节角度"""
        positions = {}
        
        if not self.is_arm_connected:
            return positions
        
        try:
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                positions["tcp"] = current_tcp
            
            error, current_joints = self.robot.GetActualJointPosDegree()
            if error == 0:
                positions["joints"] = current_joints
                
        except Exception as e:
            print(f"⚠️ 获取当前位置异常: {e}")
        
        return positions
    
    def get_current_tcp_pose(self):
        """获取当前TCP位姿"""
        if not self.is_arm_connected:
            return None
        
        try:
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                return current_tcp
            else:
                print(f"⚠️ 获取当前TCP位姿失败，错误码: {error}")
                return None
        except Exception as e:
            print(f"⚠️ 获取当前TCP位姿异常: {e}")
            return None
    
    def generate_linear_trajectory(self, start_pos, end_pos, steps):
        """生成平滑直线轨迹插值点"""
        trajectory = []
        
        for i in range(steps + 1):
            t_linear = i / steps
            
            if t_linear <= 0.0:
                t = 0.0
            elif t_linear >= 1.0:
                t = 1.0
            else:
                t = 3 * t_linear * t_linear - 2 * t_linear * t_linear * t_linear
            
            interpolated_pos = []
            for j in range(len(start_pos)):
                interpolated_value = start_pos[j] + t * (end_pos[j] - start_pos[j])
                interpolated_pos.append(interpolated_value)
            
            trajectory.append(interpolated_pos)
        
        return trajectory
    
    def check_motion_done(self):
        """检查运动是否完成"""
        try:
            if hasattr(self.robot, 'GetRobotMotionDone'):
                error, done = self.robot.GetRobotMotionDone()
                if error == 0:
                    return done == 1
            elif hasattr(self.robot, 'robot_state_pkg'):
                return self.robot.robot_state_pkg.motion_done == 1
        except Exception as e:
            print(f"⚠️ 检查运动状态异常: {e}")
        
        return False
    
    def wait_for_motion_complete(self, timeout=10):
        """等待运动完成"""
        print("⏳ 等待运动完成...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_motion_done():
                print("✅ 运动完成")
                return True
            time.sleep(0.2)
        
        print("⚠️ 运动超时，但继续执行")
        return False
    
    def move_arm_to_point_joint(self, point_name, target_joints, velocity=30.0):
        """使用关节运动移动机械臂到点位"""
        print(f"🦾 目标关节角度: {[round(j, 2) for j in target_joints]}")
        print(f"⚡ 使用MoveJ (关节空间运动) - 速度: {velocity}")
        
        try:
            ret = self.robot.MoveJ(
                joint_pos=target_joints,
                tool=0,
                user=0,
                desc_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                vel=velocity,
                acc=0.0,
                ovl=100.0
            )
            
            if ret != 0:
                print(f"🔄 带速度参数调用失败(错误码{ret})，尝试简化调用...")
                ret = self.robot.MoveJ(target_joints, 0, 0)
            
            if ret == 0:
                print(f"✅ MoveJ指令发送成功！")
                self.wait_for_motion_complete()
                
                current_pos = self.get_current_arm_position()
                if "joints" in current_pos:
                    final_joints = current_pos["joints"]
                    print(f"🦾 实际到达关节角度: {[round(j, 2) for j in final_joints]}")
                    
                    joint_errors = [(final_joints[i] - target_joints[i]) for i in range(6)]
                    max_joint_error = max(abs(err) for err in joint_errors)
                    print(f"📊 到位精度: 关节误差={max_joint_error:.2f}°")
                
                if "tcp" in current_pos:
                    final_tcp = current_pos["tcp"]
                    print(f"📍 对应TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
                
                return True
            else:
                print(f"❌ MoveJ失败，错误码: {ret}")
                return False
                
        except Exception as e:
            print(f"❌ MoveJ调用异常: {e}")
            return False
    
    def move_arm_to_point_linear(self, point_name, target_position, velocity=30.0, wait_time=0.3):
        """使用伺服直线运动移动机械臂到点位"""
        if not self.is_arm_enabled:
            print("❌ 机械臂未使能")
            return False
        
        print(f"📍 目标TCP位置: X={target_position[0]}, Y={target_position[1]}, Z={target_position[2]}")
        print(f"🔄 目标TCP姿态: RX={target_position[3]}, RY={target_position[4]}, RZ={target_position[5]}")
        
        safe_velocity = max(5.0, min(velocity, 15.0))
        print(f"🚀 伺服速度: 用户设置={velocity}, 实际使用={safe_velocity}")
        
        start_pos = self.get_current_tcp_pose()
        if not start_pos:
            print("❌ 无法获取当前TCP位姿")
            return False
        
        distance = ((start_pos[0] - target_position[0])**2 + 
                   (start_pos[1] - target_position[1])**2 + 
                   (start_pos[2] - target_position[2])**2)**0.5
        
        print(f"📏 直线距离: {distance:.1f} mm")
        
        trajectory = self.generate_linear_trajectory(start_pos, target_position, INTERPOLATION_STEPS)
        print(f"✅ 生成了 {len(trajectory)} 个轨迹点")
        
        try:
            print(f"🚀 开始执行伺服直线运动...")
            
            ret = self.robot.ServoMoveStart()
            if ret != 0:
                print(f"❌ 伺服运动开始失败，错误码: {ret}")
                return False
            print("✅ 伺服模式已启动")
            
            error_count = 0
            success_count = 0
            
            for i, pos in enumerate(trajectory):
                try:
                    safe_velocity = max(5.0, min(velocity, 15.0))
                    ret = self.robot.ServoCart(mode=0, desc_pos=pos, vel=safe_velocity)
                    
                    if ret == 0:
                        success_count += 1
                    else:
                        error_count += 1
                        if error_count < 5:
                            print(f"⚠️ 轨迹点 {i} 执行失败，错误码: {ret}")
                    
                    time.sleep(SERVO_CYCLE_TIME)
                    
                except Exception as e:
                    error_count += 1
                    if error_count < 5:
                        print(f"⚠️ 轨迹点 {i} 执行异常: {e}")
                    time.sleep(SERVO_CYCLE_TIME)
            
            print(f"✅ 轨迹跟随完成！")
            print(f"📊 执行统计: 成功 {success_count}/{len(trajectory)}, 错误 {error_count}")
            
            print("🛑 平滑停止伺服运动...")
            time.sleep(0.05)
            
            ret = self.robot.ServoMoveEnd()
            if ret != 0:
                print(f"⚠️ 伺服运动结束警告，错误码: {ret}")
            else:
                print("✅ 伺服模式已结束")
            
            time.sleep(wait_time)
            final_pos = self.get_current_tcp_pose()
            if final_pos:
                print(f"📍 伺服直线运动完成！最终TCP位姿:")
                print(f"   位置: X={final_pos[0]:.1f}, Y={final_pos[1]:.1f}, Z={final_pos[2]:.1f}")
                print(f"   姿态: RX={final_pos[3]:.1f}, RY={final_pos[4]:.1f}, RZ={final_pos[5]:.1f}")
                
                pos_errors = [abs(final_pos[i] - target_position[i]) for i in range(3)]
                max_pos_error = max(pos_errors)
                
                print(f"📊 伺服直线运动精度:")
                print(f"   位置误差: X={pos_errors[0]:.1f}, Y={pos_errors[1]:.1f}, Z={pos_errors[2]:.1f} mm")
                print(f"   最大位置误差: {max_pos_error:.1f} mm")
            
            return success_count > len(trajectory) * 0.7
            
        except Exception as e:
            print(f"❌ 伺服运动异常: {e}")
            try:
                self.robot.ServoMoveEnd()
                print("🔧 已强制结束伺服模式")
            except:
                pass
            return False
    
    def move_arm_to_point(self, point_name):
        """根据点位类型选择运动方式移动机械臂"""
        if not self.is_arm_enabled:
            print("❌ 机械臂未使能")
            return False
        
        if point_name not in self.arm_points:
            print(f"❌ 未知机械臂点位: {point_name}")
            return False
        
        point_config = self.arm_points[point_name]
        target_position = point_config["position"]
        motion_type = point_config["type"]
        method = point_config["method"]
        description = point_config.get("description", "无描述")
        
        if motion_type == "cartesian":
            default_speed = 40.0
        elif motion_type == "linear":
            default_speed = 50.0
        else:
            default_speed = 30.0
            
        custom_speed = point_config.get("speed", default_speed)
        custom_wait_time = point_config.get("wait_time", 0.3)
        
        print(f"🎯 机械臂移动到点位'{point_name}' - {description}")
        print(f"🔧 运动方式: {method} ({motion_type})")
        print(f"🚀 速度: {custom_speed}")
        print(f"⏱️ 停留时间: {custom_wait_time}秒")
        
        if motion_type == "linear":
            success = self.move_arm_to_point_linear(point_name, target_position, custom_speed, custom_wait_time)
        elif motion_type == "joint":
            success = self.move_arm_to_point_joint(point_name, target_position, custom_speed)
        else:
            print(f"❌ 未知运动类型: {motion_type}")
            success = False
            
        if success:
            print(f"✅ 机械臂成功到达点位'{point_name}'")
            if motion_type != "linear":  # linear模式已经包含了等待时间
                time.sleep(custom_wait_time)
        
        return success
    
    def disconnect_arm(self):
        """断开机械臂连接"""
        try:
            if self.robot and self.is_arm_connected:
                if self.is_arm_enabled:
                    self.robot.RobotEnable(0)
                    print("⬇️ 机械臂已下使能")
                    self.is_arm_enabled = False
                
                time.sleep(0.5)
                self.robot.CloseRPC()
                print("🔌 机械臂连接已关闭")
                
            self.is_arm_connected = False
            
        except Exception as e:
            print(f"⚠️ 机械臂断开连接异常: {e}")
    
    # ==================== 底盘控制部分 (从simple_sequence_navigation.py移植) ====================
    
    async def connect_chassis(self):
        """连接底盘"""
        try:
            self.chassis_client = httpx.AsyncClient(timeout=10.0)
            
            print("🔗 正在连接底盘...")
            response = await self.chassis_client.get(f"{self.chassis_base_url}/api/core/system/v1/capabilities")
            
            if response.status_code == 200:
                print(f"✅ 底盘连接成功!")
                self.is_chassis_connected = True
                return True
            else:
                print(f"❌ 底盘连接失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 底盘连接异常: {e}")
            return False
    
    async def disconnect_chassis(self):
        """断开底盘连接"""
        if self.chassis_client:
            await self.chassis_client.aclose()
            self.is_chassis_connected = False
            print("✅ 底盘连接已断开")
    
    async def get_current_chassis_pose(self):
        """获取当前底盘位姿"""
        if not self.is_chassis_connected:
            return None
        
        try:
            response = await self.chassis_client.get(f"{self.chassis_base_url}/api/core/slam/v1/localization/pose")
            if response.status_code == 200:
                pose = response.json()
                return {
                    'x': pose['x'],
                    'y': pose['y'],
                    'yaw': pose['yaw'],
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"❌ 获取底盘位姿失败: {e}")
        return None
    
    async def load_chassis_pois(self):
        """加载所有底盘POI点位"""
        if not self.is_chassis_connected:
            return {}
        
        try:
            response = await self.chassis_client.get(f"{self.chassis_base_url}/api/core/artifact/v1/pois")
            if response.status_code == 200:
                poi_data = response.json()
                pois = {}
                
                print(f"📍 发现 {len(poi_data)} 个POI点位:")
                for i, poi in enumerate(poi_data, 1):
                    display_name = poi['metadata']['display_name']
                    poi_id = poi['id']
                    pose = poi['pose']
                    pois[display_name] = {
                        'id': poi_id,
                        'x': pose['x'],
                        'y': pose['y'],
                        'yaw': pose['yaw'],
                        'name': display_name
                    }
                    print(f"  {i}. {display_name}: ({pose['x']:.3f}, {pose['y']:.3f}, {math.degrees(pose['yaw']):.1f}°)")
                
                self.chassis_pois = pois
                return pois
            else:
                print(f"❌ 加载POI失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ POI加载异常: {e}")
            return {}
    
    async def navigate_chassis_to_poi(self, poi_name):
        """使用MultiFloorMoveAction导航底盘到POI"""
        if not self.is_chassis_connected:
            return False
        
        try:
            print(f"🎯 底盘导航到POI '{poi_name}'")
            
            if poi_name not in self.chassis_pois:
                print(f"❌ POI '{poi_name}' 不存在")
                return False
            
            target_poi = self.chassis_pois[poi_name]
            target_x = target_poi['x']
            target_y = target_poi['y']
            target_yaw = target_poi['yaw']
            
            print(f"  目标位置: ({target_x:.3f}, {target_y:.3f}, {math.degrees(target_yaw):.1f}°)")
            
            identifiers_to_try = [poi_name]
            poi_id = target_poi['id']
            identifiers_to_try.append(poi_id)
            
            for i, identifier in enumerate(identifiers_to_try):
                identifier_type = "POI名称" if i == 0 else "POI ID" 
                print(f"  尝试使用{identifier_type}: '{identifier}'")
                
                payload = {
                    "action_name": "slamtec.agent.actions.MultiFloorMoveAction",
                    "options": {
                        "target": {
                            "poi_name": identifier
                        },
                        "move_options": {
                            "mode": 0,
                            "flags": ["with_yaw"],
                            "acceptable_precision": 0.05,
                            "fail_retry_count": 2
                        }
                    }
                }
                
                response = await self.chassis_client.post(
                    f"{self.chassis_base_url}/api/core/motion/v1/actions",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    action_id = result.get('action_id')
                    print(f"  ✅ 任务创建成功 - ID: {action_id}")
                    
                    if action_id:
                        success = await self._monitor_chassis_navigation(action_id)
                        if success:
                            print(f"  🎯 成功到达POI '{poi_name}'")
                            await self._show_chassis_navigation_accuracy(target_x, target_y, target_yaw, poi_name)
                            return True
                        else:
                            print(f"  ❌ 导航执行失败")
                    else:
                        print("  ❌ 未获取到Action ID")
                else:
                    print(f"  ❌ 任务创建失败: {response.status_code}")
                    if response.text:
                        print(f"  错误详情: {response.text}")
            
            print(f"❌ 所有尝试都失败")
            return False
                
        except Exception as e:
            print(f"❌ 底盘导航异常: {e}")
            return False
    
    async def _monitor_chassis_navigation(self, action_id, timeout=60):
        """监控底盘导航任务执行状态"""
        print(f"  🔍 监控导航任务...")
        
        for i in range(timeout):
            try:
                response = await self.chassis_client.get(
                    f"{self.chassis_base_url}/api/core/motion/v1/actions/{action_id}"
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    state = status_data.get('state', {})
                    status_code = state.get('status', 0)
                    reason = state.get('reason', '')
                    
                    status_names = {
                        0: "初始化",
                        1: "执行中", 
                        2: "暂停",
                        3: "取消",
                        4: "完成"
                    }
                    
                    current_status = status_names.get(status_code, f"未知状态({status_code})")
                    
                    if i % 5 == 0 or status_code in [3, 4]:
                        print(f"    [{i+1}s] {current_status}")
                        if reason:
                            print(f"    原因: {reason}")
                    
                    if status_code == 4:
                        result_info = state.get('result', 0)
                        if result_info == 0:
                            print(f"    ✅ 导航完成")
                            return True
                        else:
                            print(f"    ❌ 导航失败，结果码: {result_info}")
                            return False
                    elif status_code == 3:
                        print(f"    ❌ 导航被取消")
                        return False
                        
            except Exception as e:
                print(f"    ❌ 监控异常: {e}")
            
            await asyncio.sleep(1)
        
        print(f"    ⏰ 监控超时")
        return False
    
    async def _show_chassis_navigation_accuracy(self, target_x, target_y, target_yaw, poi_name):
        """显示底盘导航精度和误差"""
        try:
            await asyncio.sleep(0.5)
            
            current_pose = await self.get_current_chassis_pose()
            if not current_pose:
                print(f"  ❌ 无法获取当前位置，跳过精度计算")
                return
            
            actual_x = current_pose['x']
            actual_y = current_pose['y'] 
            actual_yaw = current_pose['yaw']
            
            dx = target_x - actual_x
            dy = target_y - actual_y
            position_error = math.sqrt(dx*dx + dy*dy)
            
            angle_diff = target_yaw - actual_yaw
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            angle_error = abs(angle_diff)
            
            print(f"  📍 精度报告:")
            print(f"    目标位置: ({target_x:.6f}, {target_y:.6f}, {math.degrees(target_yaw):.3f}°)")
            print(f"    实际位置: ({actual_x:.6f}, {actual_y:.6f}, {math.degrees(actual_yaw):.3f}°)")
            print(f"    位置误差: {position_error*100:.1f}cm")
            print(f"    角度误差: {math.degrees(angle_error):.1f}°")
            
            if position_error <= 0.05:
                position_grade = "🟢 优秀"
            elif position_error <= 0.10:
                position_grade = "🟡 良好"
            else:
                position_grade = "🔴 一般"
            
            if math.degrees(angle_error) <= 3:
                angle_grade = "🟢 优秀"
            elif math.degrees(angle_error) <= 10:
                angle_grade = "🟡 良好" 
            else:
                angle_grade = "🔴 一般"
            
            print(f"    精度评级: {position_grade} (位置) | {angle_grade} (角度)")
            
        except Exception as e:
            print(f"  ❌ 精度计算异常: {e}")
    
    async def wait_with_countdown(self, wait_time_ms: int):
        """等待指定时间并显示倒计时"""
        wait_seconds = wait_time_ms / 1000.0
        print(f"⏳ 等待 {wait_seconds:.1f} 秒...")
        
        remaining = wait_seconds
        while remaining > 0:
            if remaining >= 10 or remaining <= 5 or int(remaining) % 5 == 0:
                print(f"   ⏱️  剩余: {remaining:.1f}s")
            
            sleep_time = min(1.0, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time
        
        print(f"✅ 等待完成")
    
    # ==================== 联合控制部分 ====================
    
    def show_sequence_preview(self):
        """显示序列预览"""
        if not self.motion_sequence:
            print("❌ 序列为空")
            return
        
        print(f"\n📋 联合运动序列预览:")
        print(f"-" * 60)
        arm_count = 0
        chassis_count = 0
        wait_count = 0
        
        for i, step in enumerate(self.motion_sequence, 1):
            if isinstance(step, str):
                if step.startswith("arm:"):
                    arm_count += 1
                    point_name = step[4:]  # 去掉"arm:"前缀
                    if point_name in self.arm_points:
                        arm_config = self.arm_points[point_name]
                        desc = arm_config.get("description", "无描述")
                        print(f"  {i:2d}. 🦾 机械臂到 '{point_name}': {desc}")
                    else:
                        print(f"  {i:2d}. ❌ 无效机械臂点位 '{point_name}'")
                elif step.startswith("chassis:"):
                    chassis_count += 1
                    poi_name = step[8:]  # 去掉"chassis:"前缀
                    if poi_name in self.chassis_pois:
                        poi = self.chassis_pois[poi_name]
                        print(f"  {i:2d}. 🚗 底盘到 '{poi_name}': ({poi['x']:.2f}, {poi['y']:.2f}, {math.degrees(poi['yaw']):.0f}°)")
                    else:
                        print(f"  {i:2d}. ❌ 无效底盘POI '{poi_name}'")
                else:
                    print(f"  {i:2d}. ❓ 格式错误: {step}")
            elif isinstance(step, dict) and 'wait' in step:
                wait_count += 1
                wait_time = step['wait']
                print(f"  {i:2d}. ⏳ 等待 {wait_time}ms ({wait_time/1000:.1f}s)")
            else:
                print(f"  {i:2d}. ❓ 未知命令: {step}")
        
        print(f"-" * 60)
        print(f"📊 总计: {len(self.motion_sequence)}步 ({arm_count}个机械臂动作 + {chassis_count}个底盘动作 + {wait_count}个等待)")
    
    async def execute_sequence(self):
        """执行联合运动序列"""
        if not self.motion_sequence:
            print("❌ 序列为空")
            return False
        
        # 验证序列
        print(f"🔍 验证序列...")
        invalid_items = []
        for item in self.motion_sequence:
            if isinstance(item, str):
                if item.startswith("arm:"):
                    point_name = item[4:]
                    if point_name not in self.arm_points:
                        invalid_items.append(f"机械臂点位'{point_name}'")
                elif item.startswith("chassis:"):
                    poi_name = item[8:]
                    if poi_name not in self.chassis_pois:
                        invalid_items.append(f"底盘POI'{poi_name}'")
                else:
                    invalid_items.append(f"格式错误'{item}'")
        
        if invalid_items:
            print(f"❌ 序列包含无效项: {invalid_items}")
            return False
        
        # 显示序列预览
        self.show_sequence_preview()
        
        # 执行序列
        print(f"\n" + "="*80)
        print(f"🚀 开始执行联合运动序列")
        print(f"📋 总步骤: {len(self.motion_sequence)}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"="*80)
        
        success_count = 0
        failed_steps = []
        start_time = datetime.now()
        total_distance = 0.0
        
        for i, step in enumerate(self.motion_sequence):
            step_start_time = datetime.now()
            print(f"\n📌 步骤 {i+1}/{len(self.motion_sequence)}")
            print(f"⏰ {step_start_time.strftime('%H:%M:%S')}")
            
            try:
                if isinstance(step, str):
                    if step.startswith("arm:"):
                        # 机械臂动作
                        point_name = step[4:]
                        print(f"🦾 执行: 机械臂到点位 '{point_name}'")
                        success = self.move_arm_to_point(point_name)
                        
                    elif step.startswith("chassis:"):
                        # 底盘动作
                        poi_name = step[8:]
                        print(f"🚗 执行: 底盘导航到POI '{poi_name}'")
                        current_pose = await self.get_current_chassis_pose()
                        
                        success = await self.navigate_chassis_to_poi(poi_name)
                        
                        if success and current_pose:
                            final_pose = await self.get_current_chassis_pose()
                            if final_pose:
                                dx = final_pose['x'] - current_pose['x']
                                dy = final_pose['y'] - current_pose['y']
                                distance = math.sqrt(dx*dx + dy*dy)
                                total_distance += distance
                                print(f"📏 移动距离: {distance:.3f}m")
                    
                    if success:
                        success_count += 1
                        print(f"✅ 步骤 {i+1} 完成")
                    else:
                        failed_steps.append(f"步骤{i+1}: {step}失败")
                        print(f"❌ 步骤 {i+1} 失败")
                        
                elif isinstance(step, dict) and 'wait' in step:
                    # 等待命令
                    wait_time = step['wait']
                    print(f"⏳ 执行: 等待 {wait_time}ms ({wait_time/1000:.1f}s)")
                    await self.wait_with_countdown(wait_time)
                    success_count += 1
                    print(f"✅ 步骤 {i+1} 完成")
                
            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断序列执行")
                print(f"📊 已完成 {success_count}/{i+1} 步")
                return False
            except Exception as e:
                print(f"❌ 步骤 {i+1} 异常: {e}")
                failed_steps.append(f"步骤{i+1}: 异常 - {e}")
        
        # 显示执行结果
        end_time = datetime.now()
        total_elapsed = (end_time - start_time).total_seconds()
        
        print(f"\n" + "="*80)
        print(f"🏁 联合运动序列执行完成!")
        print(f"="*80)
        print(f"📊 执行统计:")
        print(f"   ✅ 成功步骤: {success_count}/{len(self.motion_sequence)}")
        print(f"   ❌ 失败步骤: {len(failed_steps)}")
        print(f"   📏 底盘总移动距离: {total_distance:.3f}m")
        print(f"   🕐 总执行时间: {total_elapsed:.1f}s")
        print(f"   ⏰ 结束时间: {end_time.strftime('%H:%M:%S')}")
        
        if failed_steps:
            print(f"\n❌ 失败步骤详情:")
            for failure in failed_steps:
                print(f"   • {failure}")
        
        success_rate = success_count / len(self.motion_sequence) * 100
        print(f"\n🎯 成功率: {success_rate:.1f}%")
        print(f"="*80)
        
        return success_count == len(self.motion_sequence)
    
    async def run(self):
        """运行联合控制器"""
        print("=" * 80)
        print("🤖 机械臂+底盘联合控制器")  
        print("🦾 FR3机械臂 + 🚗 Hermes底盘")
        print("📋 自动执行联合运动序列")
        print("=" * 80)
        
        # 连接机械臂
        if not self.connect_arm():
            print("❌ 机械臂连接失败，程序退出")
            return
        
        # 使能机械臂
        if not self.enable_arm():
            print("❌ 机械臂使能失败，程序退出")
            return
        
        # 连接底盘
        if not await self.connect_chassis():
            print("❌ 底盘连接失败，程序退出")
            return
        
        # 加载底盘POI数据
        print("\n📍 正在加载底盘POI数据...")
        pois = await self.load_chassis_pois()
        
        if not pois:
            print("❌ 无可用POI点位，程序退出")
            return
        
        try:
            # 直接执行序列
            await self.execute_sequence()
            
        except KeyboardInterrupt:
            print("\n⚠️  程序被用户中断")
        except Exception as e:
            print(f"❌ 程序运行错误: {e}")
        finally:
            print("\n🔧 正在清理资源...")
            self.disconnect_arm()
            await self.disconnect_chassis()
            print("👋 程序已退出")

async def main():
    """主函数"""
    import sys
    chassis_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.31.211"
    
    controller = CombinedRobotController(chassis_ip)
    await controller.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()
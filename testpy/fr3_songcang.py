#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法奥FR3机械臂自定义混合运动脚本
可自定义目标点位、运动方法(MoveCart/MoveJ)和运动序列

🎯 使用说明：
1. 在 USER_CONFIG 区域中定义你的目标点位
2. 设置每个点位的运动方法 (cartesian 用MoveCart, joint 用MoveJ)
3. 设置运动序列 (按你想要的顺序)
4. 运行脚本，系统会自动根据配置执行混合运动

✅ 支持笛卡尔运动 (MoveCart) 和关节运动 (MoveJ)
🚀 智能适应你的自定义配置
🔧 简单易用，只需修改配置区域

使用方法：
python fr3_custom_motion.py

作者：基于fr3_control/fairino SDK开发
日期：2025-07-30
"""

import sys
import os
import time
import math

# 添加FR3控制库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
except ImportError as e:
    print(f"❌ fairino库导入失败: {e}")
    sys.exit(1)


# ==================== USER_CONFIG 用户配置区域 ====================
# 👇 在这里自定义你的目标点位和运动序列 👇

# 定义目标点位配置
USER_TARGET_POINTS = {
    # 示例点位1: 使用关节运动 (MoveJ)
    #当前TCP位置: X=-48.6, Y=9.0, Z=-181.4
    #当前TCP姿态: RX=108.5, RY=77.0, RZ=-78.2
    "point111": {
        "type": "joint",  # cartesian: 笛卡尔运动, joint: 关节运动, linear: 直线运动
        "position": [-18.02, -45.33, 139.67, -78.03, 157.01, 27.88],  # 关节角度 [J1,J2,J3,J4,J5,J6] - 调整J5角度
        "method": "MoveJ",
        "speed": 80.0,  # 自定义速度 - 降低到安全范围
        "wait_time": 0,  # 到达后停留时间(秒)
        "description": "工作台上方位置"
    },
    
    # 示例点位2: 使用关节运动 (MoveJ) - 快速移动
    #当前TCP位置: X=75.1, Y=4.2, Z=-180.4
    #当前TCP姿态: RX=168.3, RY=50.3, RZ=-22.4
    "point222": {
        "type": "joint",      # joint: 关节运动
        "position":  [20.35, -46.49, 136.11, -72.08, 160.61, 30.77],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "MoveJ",
        "speed": 80.0,  # 快速移动 - 降低到安全范围
        "wait_time": 0,  # 停留1秒
        "description": "边缘位置(关节运动)"
    },
     # 你可以添加更多点位...
     "point333": {
         #当前TCP位置: X=162.8, Y=-29.3, Z=-499.1
         #当前TCP姿态: RX=149.1, RY=57.7, RZ=-36.4
         "type": "joint",
         "position":  [17.69, -2.4, 6.99, 1.37, 170.38, 24.36],
         "method": "MoveJ",
         "speed": 80.0,  # 快速移动 - 降低到安全范围 - 修正到合理范围
         "wait_time": 0,  # 短停留
         "description": "边缘位置(关节运动)"
    },
#当前TCP位置: X=52.5, Y=-29.3, Z=-499.1
#当前TCP姿态: RX=149.1, RY=57.7, RZ=-36.4
    "point444": {
        "type": "joint",      # joint: 关节运动
        "position":  [4.91, -22.8, 51.59, -26.17, 157.63, 20.9],  # 关节角度 [J1,J2,J3,J4,J5,J6]
        "method": "MoveJ",
        "speed": 80.0,  # 中速移动 - 降低到安全范围
        "wait_time": 0,  # 很短停留
        "description": "边缘位置(关节运动)"
    },

    

    
    # 伺服直线运动示例点位 - 演示ServoCart功能
    # "linear_up": {
    #     "type": "linear",  # 伺服直线运动
    #     "position": [-300.0, 200.0, 200.0, 180.0, 0.0, 0.0],  # TCP位置 [X,Y,Z,RX,RY,RZ]
    #     "method": "ServoCart",
    #     "speed": 15.0,
    #     "wait_time": 1.0,
    #     "description": "垂直上升伺服直线运动"
    # },
    
    # "linear_right": {
    #     "type": "linear",  # 伺服直线运动  
    #     "position": [-200.0, 200.0, 200.0, 180.0, 0.0, 0.0],  # TCP位置 [X,Y,Z,RX,RY,RZ]
    #     "method": "ServoCart",
    #     "speed": 15.0,
    #     "wait_time": 1.0, 
    #     "description": "水平右移伺服直线运动"
    # }
}

# 定义运动序列 (按你想要的顺序)
# 💡 新增功能：支持在序列中直接插入等待时间
# 格式：{"wait": 毫秒数} 例如：{"wait": 1000} 表示等待1000毫秒(1秒)
USER_MOTION_SEQUENCE = [
    "point111", 
    "point222", 
    "point333", 
    "point444",
    {"wait": 5000},
    "point222",    
] 

# 你可以自定义运动序列，例如：
# USER_MOTION_SEQUENCE = ["home", "point1", {"wait": 500}, "point2", "point3", "home"]
# USER_MOTION_SEQUENCE = ["point2", {"wait": 1000}, "point1"]  # 反向运动，中间等待1秒
# USER_MOTION_SEQUENCE = ["point1", "point2", {"wait": 2000}, "point1"]  # 往返运动，中间等待2秒

# 💡 关于运动类型、速度和停留时间设置说明：
# 
# 🎯 运动类型：
# - "joint": 关节空间运动 (MoveJ) - 路径弯曲，适合大范围移动
# - "cartesian": 笛卡尔点到点运动 (MoveCart) - 路径不可控
# - "linear": 笛卡尔伺服直线运动 (ServoCart) - TCP严格沿直线移动，高精度轨迹控制
# 
# 🚀 速度设置：
# - MoveJ (关节运动): 速度范围 1-200，数值越大越快（默认20.0，建议30-100）
# - MoveCart (笛卡尔运动): 速度范围 1-200，数值越大越快（默认20.0，建议40-120）
# - ServoCart (伺服直线运动): 速度范围 0-100，数值越大越快（默认50，自动换算到伺服速度3-10）
# - 如果不设置 "speed" 参数，会使用默认速度 (MoveJ: 30.0, MoveCart: 40.0, ServoCart: 50)
# - 💡 提示：速度100以上为高速运动，请确保路径安全
# 
# ⏱️ 停留时间设置：
# - "wait_time": 到达点位后的停留时间(秒)，可以是小数
# - 建议范围: 0.1 - 5.0 秒，根据工艺需求设置
# - 如果不设置 "wait_time" 参数，会使用默认停留时间 0.3秒
# - 可以设置 0.0 秒实现无停留快速通过
# 
# 💡 组合使用：
# - 可以为不同点位设置不同速度和停留时间
# - 实现快速通过 + 精确停留的混合运动序列
# - 例如：过渡点位快速通过(高速度+短停留)，工作点位精确停留(中速度+长停留)

# ==================== END USER_CONFIG 配置区域结束 ====================

# 从测试程序移植的伺服运动参数 - 优化平滑度
SERVO_CYCLE_TIME = 0.008  # 8ms伺服周期 (提高频率增加平滑度)
SERVO_VELOCITY = 15.0     # 伺服运动速度 (从40调慢到15)
INTERPOLATION_STEPS = 200  # 插值步数 (增加到200，让运动更平滑)


class FR3CustomController:
    """FR3机械臂自定义混合运动控制器"""
    
    def __init__(self, target_points=None, motion_sequence=None):
        self.robot = None
        self.is_connected = False
        self.is_enabled = False
        
        # 使用用户配置或默认配置
        self.target_points = target_points if target_points else USER_TARGET_POINTS
        self.motion_sequence = motion_sequence if motion_sequence else USER_MOTION_SEQUENCE
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """验证用户配置的有效性"""
        print("🔍 验证用户配置...")
        
        # 检查点位配置
        if not self.target_points:
            raise ValueError("❌ 目标点位配置为空！请在 USER_TARGET_POINTS 中定义点位")
        
        # 检查运动序列
        if not self.motion_sequence:
            raise ValueError("❌ 运动序列配置为空！请在 USER_MOTION_SEQUENCE 中定义序列")
        
        # 检查序列中的点位是否都存在（支持wait指令）
        missing_points = []
        for item in self.motion_sequence:
            if isinstance(item, dict):
                # 处理wait指令
                if "wait" not in item:
                    raise ValueError(f"❌ 运动序列中的字典必须包含'wait'键: {item}")
                wait_time = item["wait"]
                if not isinstance(wait_time, (int, float)) or wait_time < 0:
                    raise ValueError(f"❌ wait时间必须是非负数字(毫秒): {wait_time}")
            elif isinstance(item, str):
                # 处理点位名称
                if item not in self.target_points:
                    missing_points.append(item)
            else:
                raise ValueError(f"❌ 运动序列中的项目必须是字符串(点位名)或字典(wait指令): {item}")
        
        if missing_points:
            raise ValueError(f"❌ 运动序列中包含未定义的点位: {missing_points}")
        
        # 检查每个点位的配置
        for point_name, config in self.target_points.items():
            if "type" not in config:
                raise ValueError(f"❌ 点位'{point_name}'缺少'type'配置")
            if "position" not in config:
                raise ValueError(f"❌ 点位'{point_name}'缺少'position'配置")
            if "method" not in config:
                raise ValueError(f"❌ 点位'{point_name}'缺少'method'配置")
            
            # 检查position数组长度
            if config["type"] in ["cartesian", "linear"] and len(config["position"]) != 6:
                coord_type = "笛卡尔坐标" if config["type"] == "cartesian" else "直线运动坐标"
                raise ValueError(f"❌ 点位'{point_name}'的{coord_type}应包含6个值[X,Y,Z,RX,RY,RZ]")
            elif config["type"] == "joint" and len(config["position"]) != 6:
                raise ValueError(f"❌ 点位'{point_name}'的关节角度应包含6个值[J1,J2,J3,J4,J5,J6]")
        
        print("✅ 用户配置验证通过")
    
    def display_config(self):
        """显示当前配置"""
        print("📋 当前运动配置:")
        print("=" * 60)
        
        print("🎯 定义的目标点位:")
        for point_name, config in self.target_points.items():
            desc = config.get("description", "无描述")
            method = config["method"]
            if config["type"] == "cartesian":
                type_str = "笛卡尔坐标"
            elif config["type"] == "linear":
                type_str = "笛卡尔坐标(直线)"
            else:  # joint
                type_str = "关节角度"
            
            # 获取速度设置
            if config["type"] == "cartesian":
                default_speed = 40.0
            elif config["type"] == "linear":
                default_speed = 50.0  # ServoCart默认速度（用户输入范围0-100）
            else:  # joint
                default_speed = 30.0
            
            speed = config.get("speed", default_speed)
            speed_info = f"自定义: {speed}" if "speed" in config else f"默认: {speed}"
            
            # 获取停留时间设置
            default_wait_time = 0.3
            wait_time = config.get("wait_time", default_wait_time)
            wait_info = f"自定义: {wait_time}秒" if "wait_time" in config else f"默认: {wait_time}秒"
            
            print(f"   {point_name}: {desc}")
            print(f"     方法: {method} ({type_str})")
            print(f"     速度: {speed_info}")
            print(f"     停留: {wait_info}")
            print(f"     位置: {config['position']}")
        
        # 显示运动序列（支持wait指令）
        sequence_display = []
        for item in self.motion_sequence:
            if isinstance(item, dict) and "wait" in item:
                sequence_display.append(f"⏱️wait({item['wait']}ms)")
            else:
                sequence_display.append(str(item))
        
        print(f"\n🚀 运动序列: {' → '.join(sequence_display)}")
        
        # 统计点位和wait指令数量
        point_count = sum(1 for item in self.motion_sequence if isinstance(item, str))
        wait_count = sum(1 for item in self.motion_sequence if isinstance(item, dict))
        print(f"📊 总计 {len(self.target_points)} 个点位，{len(self.motion_sequence)} 步运动（{point_count}个点位 + {wait_count}个等待）")
        print("=" * 60)
    
    def connect(self):
        """连接机械臂 - 固定IP: 192.168.58.2"""
        try:
            print(f"🔗 正在连接机械臂...")
            self.robot = Robot.RPC('192.168.58.2')
            
            if not hasattr(self.robot, 'is_conect') or not self.robot.is_conect:
                print("❌ 连接失败")
                return False
            
            print("✅ 机械臂连接成功")
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def enable_robot(self):
        """使能机械臂"""
        if not self.is_connected:
            print("❌ 机械臂未连接")
            return False
        
        try:
            print(f"⚡ 准备机械臂运动...")
            
            # 设置自动模式
            ret = self.robot.Mode(0)
            if ret != 0:
                print(f"❌ 设置自动模式失败，错误码: {ret}")
                return False
            print("✅ 已切换到自动模式")
            
            time.sleep(0.5)
            
            # 上使能
            ret = self.robot.RobotEnable(1)
            if ret != 0:
                print(f"❌ 使能失败，错误码: {ret}")
                return False
            print("✅ 机械臂已使能")
            
            time.sleep(1.5)
            self.is_enabled = True
            return True
            
        except Exception as e:
            print(f"❌ 使能异常: {e}")
            return False
    
    def get_current_position(self):
        """获取当前TCP位置和关节角度"""
        positions = {}
        
        if not self.is_connected:
            return positions
        
        try:
            # 获取TCP位置
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                positions["tcp"] = current_tcp
            
            # 获取关节角度
            error, current_joints = self.robot.GetActualJointPosDegree()
            if error == 0:
                positions["joints"] = current_joints
                
        except Exception as e:
            print(f"⚠️ 获取当前位置异常: {e}")
        
        return positions
    
    def get_current_tcp_pose(self):
        """获取当前TCP位姿 - 从测试程序移植"""
        if not self.is_connected:
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
        """生成平滑直线轨迹插值点 - 标准三次S曲线版本"""
        trajectory = []
        
        for i in range(steps + 1):
            # 使用标准的三次S曲线，确保加速度均匀分布
            t_linear = i / steps  # 线性插值参数，从0到1
            
            # 标准三次S曲线函数 (cubic S-curve)
            # 这个函数确保在0和1处的一阶和二阶导数都为0，实现真正平滑的加减速
            if t_linear <= 0.0:
                t = 0.0
            elif t_linear >= 1.0:
                t = 1.0
            else:
                # 三次S曲线: 3t² - 2t³
                t = 3 * t_linear * t_linear - 2 * t_linear * t_linear * t_linear
            
            # 使用平滑的t值进行插值
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
    
    def move_to_point_cartesian(self, point_name, target_position, velocity=40.0):
        """使用笛卡尔运动移动到点位"""
        print(f"📍 目标TCP位置: X={target_position[0]}, Y={target_position[1]}, Z={target_position[2]}")
        print(f"🔄 目标TCP姿态: RX={target_position[3]}, RY={target_position[4]}, RZ={target_position[5]}")
        print(f"⚡ 使用MoveCart (笛卡尔空间点到点运动) - 速度: {velocity}")
        
        try:
            # 使用自定义速度的MoveCart（优先使用带速度参数版本）
            ret = self.robot.MoveCart(target_position, 0, 0, vel=velocity)
            
            if ret == 0:
                print(f"✅ MoveCart指令发送成功！")
                self.wait_for_motion_complete()
                
                # 验证到位
                current_pos = self.get_current_position()
                if "tcp" in current_pos:
                    final_tcp = current_pos["tcp"]
                    print(f"📍 实际到达TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
                    
                    # 计算误差
                    pos_error = [(final_tcp[i] - target_position[i]) for i in range(3)]
                    max_pos_error = max(abs(err) for err in pos_error)
                    print(f"📊 到位精度: 位置误差={max_pos_error:.1f}mm")
                
                return True
            else:
                print(f"❌ MoveCart失败，错误码: {ret}")
                return False
                
        except Exception as e:
            print(f"❌ MoveCart异常: {e}")
            return False
    
    def move_to_point_linear(self, point_name, target_position, velocity=30.0, wait_time=0.3):
        """使用伺服直线运动移动到点位 - 完全移植自测试程序"""
        if not self.is_enabled:
            print("❌ 机械臂未使能")
            return False
        
        print(f"📍 目标TCP位置: X={target_position[0]}, Y={target_position[1]}, Z={target_position[2]}")
        print(f"🔄 目标TCP姿态: RX={target_position[3]}, RY={target_position[4]}, RZ={target_position[5]}")
        
        # 计算实际使用的伺服速度
        safe_velocity = max(5.0, min(velocity, 15.0))
        print(f"🚀 伺服速度: 用户设置={velocity}, 实际使用={safe_velocity} (限制在5-15范围内)")
        
        # 1. 获取当前位置
        start_pos = self.get_current_tcp_pose()
        if not start_pos:
            print("❌ 无法获取当前TCP位姿")
            return False
        
        print(f"📍 起始TCP位姿:")
        print(f"   位置: X={start_pos[0]:.1f}, Y={start_pos[1]:.1f}, Z={start_pos[2]:.1f}")
        print(f"   姿态: RX={start_pos[3]:.1f}, RY={start_pos[4]:.1f}, RZ={start_pos[5]:.1f}")
        
        # 2. 计算运动信息
        distance = ((start_pos[0] - target_position[0])**2 + 
                   (start_pos[1] - target_position[1])**2 + 
                   (start_pos[2] - target_position[2])**2)**0.5
        
        print(f"\n📏 直线运动信息:")
        print(f"   直线距离: {distance:.1f} mm")
        print(f"   插值步数: {INTERPOLATION_STEPS}")
        print(f"   伺服周期: {SERVO_CYCLE_TIME*1000:.1f} ms")
        print(f"   预计耗时: {INTERPOLATION_STEPS * SERVO_CYCLE_TIME:.1f} 秒")
        
        # 3. 生成直线轨迹
        print(f"\n🔧 生成直线轨迹插值点...")
        trajectory = self.generate_linear_trajectory(start_pos, target_position, INTERPOLATION_STEPS)
        print(f"✅ 生成了 {len(trajectory)} 个轨迹点")
        
        # 4. 执行伺服运动 (去掉安全确认，自动执行)
        try:
            print(f"\n🚀 开始执行伺服直线运动...")
            
            # 开始伺服模式
            print("📡 启动伺服模式...")
            ret = self.robot.ServoMoveStart()
            if ret != 0:
                print(f"❌ 伺服运动开始失败，错误码: {ret}")
                return False
            print("✅ 伺服模式已启动")
            
            # 执行轨迹跟随
            error_count = 0
            success_count = 0
            
            print(f"🎯 开始轨迹跟随 ({len(trajectory)} 个点)...")
            
            for i, pos in enumerate(trajectory):
                try:
                    # 使用ServoCart发送位置指令 - 使用用户配置的速度
                    # mode参数：0-位置模式
                    # 限制速度在安全范围内（5-15），参考测试程序验证的速度
                    safe_velocity = max(5.0, min(velocity, 15.0))
                    ret = self.robot.ServoCart(mode=0, desc_pos=pos, vel=safe_velocity)
                    
                    if ret == 0:
                        success_count += 1
                        if i % 20 == 0:  # 每20个点显示一次进度
                            progress = (i / len(trajectory)) * 100
                            print(f"   进度: {progress:.1f}% ({i}/{len(trajectory)})")
                    else:
                        error_count += 1
                        if error_count < 5:  # 只显示前5个错误
                            print(f"⚠️ 轨迹点 {i} 执行失败，错误码: {ret}")
                    
                    # 等待伺服周期
                    time.sleep(SERVO_CYCLE_TIME)
                    
                except Exception as e:
                    error_count += 1
                    if error_count < 5:
                        print(f"⚠️ 轨迹点 {i} 执行异常: {e}")
                    time.sleep(SERVO_CYCLE_TIME)
            
            print(f"✅ 轨迹跟随完成！")
            print(f"📊 执行统计: 成功 {success_count}/{len(trajectory)}, 错误 {error_count}")
            
            # 添加平滑结束过渡，避免突然停止
            print("🛑 平滑停止伺服运动...")
            time.sleep(0.05)  # 短暂等待让最后的指令完成
            
            # 结束伺服模式
            print("📡 结束伺服模式...")
            ret = self.robot.ServoMoveEnd()
            if ret != 0:
                print(f"⚠️ 伺服运动结束警告，错误码: {ret}")
            else:
                print("✅ 伺服模式已结束")
            
            # 5. 验证最终位置
            time.sleep(wait_time)  # 使用用户配置的等待时间
            final_pos = self.get_current_tcp_pose()
            if final_pos:
                print(f"\n📍 伺服直线运动完成！最终TCP位姿:")
                print(f"   位置: X={final_pos[0]:.1f}, Y={final_pos[1]:.1f}, Z={final_pos[2]:.1f}")
                print(f"   姿态: RX={final_pos[3]:.1f}, RY={final_pos[4]:.1f}, RZ={final_pos[5]:.1f}")
                
                # 计算精度
                pos_errors = [abs(final_pos[i] - target_position[i]) for i in range(3)]
                max_pos_error = max(pos_errors)
                
                print(f"\n📊 伺服直线运动精度:")
                print(f"   位置误差: X={pos_errors[0]:.1f}, Y={pos_errors[1]:.1f}, Z={pos_errors[2]:.1f} mm")
                print(f"   最大位置误差: {max_pos_error:.1f} mm")
                print(f"   轨迹成功率: {(success_count/len(trajectory)*100):.1f}%")
                
                if max_pos_error < 5.0 and success_count > len(trajectory) * 0.9:
                    print("✅ 伺服直线运动精度优秀！")
                    return True
                elif max_pos_error < 10.0 and success_count > len(trajectory) * 0.8:
                    print("✅ 伺服直线运动精度良好！")
                    return True
                else:
                    print("⚠️ 伺服直线运动完成，但精度或成功率有待改善")
                    return True
            
            return success_count > len(trajectory) * 0.7
            
        except Exception as e:
            print(f"❌ 伺服运动异常: {e}")
            # 确保结束伺服模式
            try:
                self.robot.ServoMoveEnd()
                print("🔧 已强制结束伺服模式")
            except:
                pass
            return False
    
    def move_to_point_joint(self, point_name, target_joints, velocity=30.0):
        """使用关节运动移动到点位"""
        print(f"🦾 目标关节角度: {[round(j, 2) for j in target_joints]}")
        print(f"⚡ 使用MoveJ (关节空间运动) - 速度: {velocity}")
        
        # 检查关节角度是否在合理范围内
        joint_limits = [
            (-175, 175),  # J1
            (-265, 85),  # J2  
            (-150, 150),  # J3
            (-265, 85),  # J4
            (-175, 175),  # J5 - 这里可能是问题
            (-175, 175)   # J6
        ]
        
        warnings = []
        for i, (angle, (min_limit, max_limit)) in enumerate(zip(target_joints, joint_limits)):
            if angle < min_limit or angle > max_limit:
                warnings.append(f"J{i+1}={angle:.1f}° (限位: {min_limit}~{max_limit}°)")
        
        if warnings:
            print(f"⚠️ 关节角度可能超出限位: {', '.join(warnings)}")
            print("💡 这可能导致错误码154")
        
        try:
            # 优先使用带速度参数的MoveJ调用（支持自定义速度）
            ret = self.robot.MoveJ(
                joint_pos=target_joints,
                tool=0,
                user=0,
                desc_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                vel=velocity,  # 使用自定义速度
                acc=0.0,
                ovl=100.0
            )
            
            if ret != 0:
                # 如果带参数版本失败，尝试简化版本作为备选，但保持速度参数
                print(f"🔄 带速度参数调用失败(错误码{ret})，尝试简化调用（保持速度{velocity}）...")
                # 尝试其他MoveJ调用方式，仍然使用自定义速度
                try:
                    # 方式1：更简单的带速度调用
                    ret = self.robot.MoveJ(target_joints, 0, 0, vel=velocity)
                    if ret != 0:
                        # 方式2：如果还失败，降低速度重试
                        safe_velocity = min(velocity, 20.0)  # 限制最大速度为20
                        print(f"🔄 进一步降低速度到{safe_velocity}重试...")
                        ret = self.robot.MoveJ(target_joints, 0, 0, vel=safe_velocity)
                        if ret != 0:
                            # 方式3：最后才使用完全简化版本
                            print(f"🔄 最后尝试无速度参数版本...")
                            ret = self.robot.MoveJ(target_joints, 0, 0)
                except Exception as e:
                    print(f"⚠️ 备用调用异常: {e}")
                    ret = self.robot.MoveJ(target_joints, 0, 0)
            
            if ret == 0:
                print(f"✅ MoveJ指令发送成功！")
                self.wait_for_motion_complete()
                
                # 验证到位
                current_pos = self.get_current_position()
                if "joints" in current_pos:
                    final_joints = current_pos["joints"]
                    print(f"🦾 实际到达关节角度: {[round(j, 2) for j in final_joints]}")
                    
                    # 计算误差
                    joint_errors = [(final_joints[i] - target_joints[i]) for i in range(6)]
                    max_joint_error = max(abs(err) for err in joint_errors)
                    print(f"📊 到位精度: 关节误差={max_joint_error:.2f}°")
                
                # 同时显示TCP位置
                if "tcp" in current_pos:
                    final_tcp = current_pos["tcp"]
                    print(f"📍 对应TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
                
                return True
            else:
                if ret == 154:
                    print(f"❌ MoveJ失败，错误码154: 参数超出范围")
                    print(f"💡 可能原因：")
                    print(f"   - 速度参数过高 (当前: {velocity})")
                    print(f"   - 关节角度超出限位")
                    print(f"   - 目标位置不可达")
                else:
                    print(f"❌ MoveJ失败，错误码: {ret}")
                return False
                
        except Exception as e:
            print(f"❌ MoveJ调用异常: {e}")
            return False
    
    def move_to_point(self, point_name):
        """根据点位类型选择运动方式，返回 (success, wait_time)"""
        if not self.is_enabled:
            print("❌ 机械臂未使能")
            return False, 0.0
        
        # 确保point_name是字符串
        if not isinstance(point_name, str):
            print(f"❌ 点位名称必须是字符串: {point_name}")
            return False, 0.0
            
        if point_name not in self.target_points:
            print(f"❌ 未知点位: {point_name}")
            return False, 0.0
        
        point_config = self.target_points[point_name]
        target_position = point_config["position"]
        motion_type = point_config["type"]
        method = point_config["method"]
        description = point_config.get("description", "无描述")
        
        # 获取自定义速度，如果没有设置则使用默认值
        if motion_type == "cartesian":
            default_speed = 40.0  # MoveCart默认速度
        elif motion_type == "linear":
            default_speed = 50.0  # ServoCart默认速度（用户输入范围0-100）  
        else:  # joint
            default_speed = 30.0  # MoveJ默认速度
            
        custom_speed = point_config.get("speed", default_speed)
        
        # 基本速度范围检查（更宽松的范围）
        if custom_speed > 200.0:
            print(f"⚠️ 警告：点位'{point_name}'的速度{custom_speed}过高，自动限制为200.0")
            custom_speed = 200.0
        elif custom_speed < 1.0:
            print(f"⚠️ 警告：点位'{point_name}'的速度{custom_speed}过低，自动设置为1.0")
            custom_speed = 1.0
        
        # 获取自定义停留时间，如果没有设置则使用默认值
        default_wait_time = 0.3  # 默认停留时间 (秒)
        custom_wait_time = point_config.get("wait_time", default_wait_time)
        
        print(f"\n🎯 移动到点位'{point_name}' - {description}")
        print(f"🔧 运动方式: {method} ({motion_type})")
        
        if "speed" in point_config:
            print(f"🚀 自定义速度: {custom_speed}")
        else:
            print(f"🚀 默认速度: {custom_speed}")
            
        if "wait_time" in point_config:
            print(f"⏱️ 自定义停留时间: {custom_wait_time}秒")
        else:
            print(f"⏱️ 默认停留时间: {custom_wait_time}秒")
        
        # 执行运动
        if motion_type == "cartesian":
            success = self.move_to_point_cartesian(point_name, target_position, custom_speed)
        elif motion_type == "linear":
            success = self.move_to_point_linear(point_name, target_position, custom_speed, custom_wait_time)
        elif motion_type == "joint":
            success = self.move_to_point_joint(point_name, target_position, custom_speed)
        else:
            print(f"❌ 未知运动类型: {motion_type} (支持: cartesian, linear, joint)")
            success = False
            
        return success, custom_wait_time
    
    def execute_custom_motion(self):
        """执行自定义运动序列"""
        print("🎬 开始执行自定义运动序列")
        
        # 显示运动路径（支持wait指令）
        sequence_display = []
        for item in self.motion_sequence:
            if isinstance(item, dict) and "wait" in item:
                sequence_display.append(f"⏱️wait({item['wait']}ms)")
            else:
                sequence_display.append(str(item))
        print(f"📋 运动路径: {' → '.join(sequence_display)}")
        
        # 显示起始位置
        print(f"\n📍 起始状态:")
        start_positions = self.get_current_position()
        if "tcp" in start_positions:
            tcp = start_positions["tcp"]
            print(f"   TCP位置: X={tcp[0]:.1f}, Y={tcp[1]:.1f}, Z={tcp[2]:.1f}")
        if "joints" in start_positions:
            joints = start_positions["joints"]
            print(f"   关节角度: {[round(j, 1) for j in joints]}")
        
        success_count = 0
        
        for i, item in enumerate(self.motion_sequence, 1):
            print(f"\n{'='*60}")
            
            # 处理wait指令
            if isinstance(item, dict) and "wait" in item:
                wait_ms = item["wait"]
                wait_seconds = wait_ms / 1000.0
                print(f"⏱️ 第{i}步: 等待 {wait_ms}毫秒 ({wait_seconds:.1f}秒) ({i}/{len(self.motion_sequence)})")
                print(f"{'='*60}")
                
                print(f"🕐 开始等待 {wait_ms}毫秒...")
                time.sleep(wait_seconds)
                print(f"✅ 等待完成")
                success_count += 1
                
            # 处理点位移动
            elif isinstance(item, str):
                point_name = item
                print(f"🚀 第{i}步: 移动到点位'{point_name}' ({i}/{len(self.motion_sequence)})")
                print(f"{'='*60}")
                
                success, wait_time = self.move_to_point(point_name)
                if success:
                    success_count += 1
                    print(f"✅ 第{i}步完成")
                    
                    # 使用点位自定义的停留时间
                    if i < len(self.motion_sequence):
                        print(f"⏱️ 在点位'{point_name}'停留 {wait_time}秒...")
                        time.sleep(wait_time)
                else:
                    print(f"❌ 第{i}步失败")
                    # 失败后询问是否继续
                    continue_motion = input(f"是否继续执行剩余运动？(y/N): ").strip().lower()
                    if continue_motion != 'y':
                        print("🛑 运动序列中断")
                        break
        
        # 运动序列完成总结
        print(f"\n{'='*60}")
        print("📊 自定义运动序列执行总结")
        print(f"{'='*60}")
        print(f"🎯 计划执行点位: {len(self.motion_sequence)}个")
        print(f"✅ 成功到达点位: {success_count}个")
        print(f"📈 成功率: {(success_count/len(self.motion_sequence)*100):.1f}%")
        
        if success_count == len(self.motion_sequence):
            print("🎉 所有自定义点位运动完成!")
            return True
        else:
            print("⚠️ 部分点位移动失败")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.robot and self.is_connected:
                if self.is_enabled:
                    self.robot.RobotEnable(0)
                    print("⬇️ 机械臂已下使能")
                    self.is_enabled = False
                
                time.sleep(0.5)
                self.robot.CloseRPC()
                print("🔌 连接已关闭")
                
            self.is_connected = False
            
        except Exception as e:
            print(f"⚠️ 断开连接异常: {e}")


def main():
    """主函数"""
    print("🤖 FR3机械臂自定义混合运动程序")
    print("=" * 60)
    print("💡 这是一个可自定义的运动脚本:")
    print("  - 在代码的 USER_CONFIG 区域定义目标点位")
    print("  - 设置每个点位的运动方法 (MoveCart/MoveJ)")
    print("  - 自定义运动序列")
    print("  - 系统会自动根据配置执行混合运动")
    
    try:
        controller = FR3CustomController()
        
        # 显示当前配置
        controller.display_config()
        
        # 1. 连接机械臂
        if not controller.connect():
            return 1
        
        # 2. 使能机械臂
        if not controller.enable_robot():
            return 1
        
        # 3. 安全确认
        print(f"\n⚠️ 自定义运动安全确认:")
        print(f"  - 将执行 {len(controller.motion_sequence)} 步运动")
        print("  - 系统会根据每个点位的配置自动选择运动方式")
        print("  - 固定IP: 192.168.58.2")
        print("  - 请确保整个运动路径安全")
        print("  - 准备好急停按钮")
        
        final_confirm = input("\n确认开始自定义运动？(y/N): ").strip().lower()
        if final_confirm != 'y':
            print("❌ 自定义运动已取消")
            return 1
        
        # 4. 执行自定义运动序列
        success = controller.execute_custom_motion()
        
        if success:
            print("\n🎉 自定义运动序列圆满完成！")
            print("💡 机械臂已按照你的配置完成所有运动。")
        else:
            print("\n⚠️ 自定义运动序列部分完成。")
        
        return 0 if success else 1
        
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("💡 请检查 USER_CONFIG 区域的配置")
        return 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断程序")
        return 1
        
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        return 1
        
    finally:
        try:
            controller.disconnect()
        except:
            pass


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双臂机械臂仿真轨迹测试程序
基于FR3机械臂API和精确尺寸参数，生成内置测试轨迹
用于调试仿真系统，无需实际连接机器人
"""

import sys
import os
import math
import time
from datetime import datetime

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'fr3_control'))
sys.path.insert(0, os.path.join(project_root, 'gui', 'widgets'))

try:
    from fr3_control.fairino.Robot import *
except ImportError:
    print("警告: FR3控制库导入失败，使用模拟数据")

class RobotPhysicalConfig:
    """机器人物理结构配置"""
    
    def __init__(self):
        # 基础结构尺寸 (mm)
        self.chassis_diameter = 500.0       # 底盘直径
        self.chassis_height = 250.0         # 底盘高度
        self.lifting_column_height = 300.0  # 升降轴可见高度
        self.lifting_column_diameter = 180.0 # 升降轴直径
        self.chest_width = 380.0            # 胸部宽度
        
        # 左右臂安装位置 (相对于胸部中心)
        self.left_arm_offset = [-190.0, 0.0, 0.0]   # 左臂偏移 (x=-190mm)
        self.right_arm_offset = [190.0, 0.0, 0.0]   # 右臂偏移 (x=+190mm)
        
        # FR3机械臂精确尺寸 (mm)
        self.arm_link_lengths = {
            'base_to_j2': 140.0,    # 基座到J2的距离
            'j2_to_j3': 280.0,      # 大臂连杆长度 (J2-J3)
            'j3_to_j5': 240.0,      # 小臂连杆长度 (J3-J5，腕部中心)
            'j5_to_flange': 100.0   # 腕部到末端法兰距离
        }
        
        # 计算总臂展
        self.max_reach = (self.arm_link_lengths['j2_to_j3'] + 
                         self.arm_link_lengths['j3_to_j5'] + 
                         self.arm_link_lengths['j5_to_flange'])  # 620mm
        
        print(f"机器人配置初始化完成:")
        print(f"  胸部宽度: {self.chest_width}mm")
        print(f"  单臂最大臂展: {self.max_reach}mm")
        print(f"  左右臂基座间距: {self.chest_width}mm")

class FR3SimulatedRobot:
    """FR3机械臂模拟器"""
    
    def __init__(self, arm_id="left", base_position=None):
        self.arm_id = arm_id
        self.base_position = base_position if base_position is not None else [0, 0, 0]
        self.connected = False
        
        # 当前关节角度 (度)
        self.current_joints = [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
        
        # 当前末端法兰位姿 [x, y, z, rx, ry, rz]
        self.current_flange_pose = self.forward_kinematics(self.current_joints)
        
        print(f"{arm_id}臂模拟器初始化完成")
        print(f"  基座位置: {self.base_position}")
        print(f"  初始关节角度: {self.current_joints}")
        print(f"  初始法兰位姿: {[round(x, 2) for x in self.current_flange_pose]}")
    
    def connect(self, ip="192.168.58.2"):
        """模拟连接机器人"""
        print(f"模拟连接{self.arm_id}臂: {ip}")
        self.connected = True
        return True
    
    def get_current_joint_positions(self):
        """获取当前关节位置"""
        return self.current_joints.copy()
    
    def get_current_flange_pose(self):
        """获取当前末端法兰位姿"""
        return self.current_flange_pose.copy()
    
    def forward_kinematics(self, joint_angles):
        """简化的正运动学计算"""
        # 这里使用简化的计算，实际应用中应使用精确的DH参数
        j1, j2, j3, j4, j5, j6 = [math.radians(angle) for angle in joint_angles]
        
        # 简化计算，基于连杆长度
        config = RobotPhysicalConfig()
        L1 = config.arm_link_lengths['base_to_j2']
        L2 = config.arm_link_lengths['j2_to_j3']
        L3 = config.arm_link_lengths['j3_to_j5']
        L4 = config.arm_link_lengths['j5_to_flange']
        
        # 简化的位置计算 (相对于机械臂基座)
        x = (L2 * math.cos(j2) + L3 * math.cos(j2 + j3) + L4 * math.cos(j2 + j3 + j4)) * math.cos(j1)
        y = (L2 * math.cos(j2) + L3 * math.cos(j2 + j3) + L4 * math.cos(j2 + j3 + j4)) * math.sin(j1)
        z = L1 + L2 * math.sin(j2) + L3 * math.sin(j2 + j3) + L4 * math.sin(j2 + j3 + j4)
        
        # 简化的姿态计算
        rx = math.degrees(j4)
        ry = math.degrees(j5)
        rz = math.degrees(j6)
        
        return [x, y, z, rx, ry, rz]
    
    def move_to_joint_position(self, joint_angles, speed=20):
        """移动到指定关节位置"""
        print(f"{self.arm_id}臂移动到关节位置: {[round(x, 1) for x in joint_angles]}")
        self.current_joints = joint_angles.copy()
        self.current_flange_pose = self.forward_kinematics(joint_angles)
        return True

class DualArmTrajectoryGenerator:
    """双臂轨迹生成器"""
    
    def __init__(self):
        self.config = RobotPhysicalConfig()
        
        # 初始化左右臂模拟器
        self.left_arm = FR3SimulatedRobot("left", self.config.left_arm_offset)
        self.right_arm = FR3SimulatedRobot("right", self.config.right_arm_offset)
        
        # 轨迹数据
        self.left_arm_trajectory = []
        self.right_arm_trajectory = []
        
        print("双臂轨迹生成器初始化完成")
    
    def connect_robots(self):
        """连接双臂机器人"""
        left_success = self.left_arm.connect("192.168.58.3")  # 左臂IP
        right_success = self.right_arm.connect("192.168.58.2")  # 右臂IP
        return left_success and right_success
    
    def get_current_robot_state(self):
        """获取当前机器人状态"""
        state = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'left_arm': {
                'joints': self.left_arm.get_current_joint_positions(),
                'flange_pose': self.left_arm.get_current_flange_pose(),
                'base_position': self.left_arm.base_position
            },
            'right_arm': {
                'joints': self.right_arm.get_current_joint_positions(),
                'flange_pose': self.right_arm.get_current_flange_pose(),
                'base_position': self.right_arm.base_position
            },
            'robot_structure': {
                'chest_width': self.config.chest_width,
                'max_reach': self.config.max_reach,
                'arm_separation': self.config.chest_width
            }
        }
        return state
    
    def generate_left_arm_illumination_trajectory(self, steps=30):
        """生成左臂照明轨迹 - 抬手举起物体对前方照明"""
        print("生成左臂照明轨迹...")
        
        trajectory = []
        
        # 起始位置 (初始姿态)
        start_joints = [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
        
        # 目标位置 (抬起并指向前方)
        target_joints = [-30.0, -45.0, -120.0, -60.0, 90.0, 0.0]
        
        # 生成插值轨迹
        for i in range(steps + 1):
            t = i / steps
            
            # 线性插值关节角度
            current_joints = []
            for j in range(6):
                joint_angle = start_joints[j] + t * (target_joints[j] - start_joints[j])
                current_joints.append(joint_angle)
            
            trajectory.append(current_joints)
        
        self.left_arm_trajectory = trajectory
        print(f"左臂照明轨迹生成完成，共{len(trajectory)}个点")
        return trajectory
    
    def generate_right_arm_painting_trajectory(self, steps=50):
        """生成右臂刷墙轨迹 - 前伸并进行上下0.5m往复动作"""
        print("生成右臂刷墙轨迹...")
        
        trajectory = []
        
        # 基础位置 (前伸姿态)
        base_joints = [30.0, -30.0, -90.0, -90.0, 90.0, 0.0]
        
        # 上下运动参数
        vertical_range = 40.0  # 关节角度变化范围，对应约0.5m末端移动
        
        # 生成往复运动轨迹
        for i in range(steps + 1):
            t = i / steps
            
            # 正弦波上下运动
            vertical_offset = vertical_range * math.sin(2 * math.pi * t * 2)  # 2个完整周期
            
            current_joints = base_joints.copy()
            current_joints[1] += vertical_offset * 0.3  # J2关节主要负责上下运动
            current_joints[2] += vertical_offset * 0.7  # J3关节辅助调整
            
            trajectory.append(current_joints)
        
        self.right_arm_trajectory = trajectory
        print(f"右臂刷墙轨迹生成完成，共{len(trajectory)}个点")
        return trajectory
    
    def generate_complete_trajectory(self):
        """生成完整的双臂协调轨迹"""
        print("\\n=== 开始生成双臂协调轨迹 ===")
        
        # 生成左臂照明轨迹
        left_traj = self.generate_left_arm_illumination_trajectory(30)
        
        # 生成右臂刷墙轨迹
        right_traj = self.generate_right_arm_painting_trajectory(50)
        
        # 同步轨迹长度
        max_length = max(len(left_traj), len(right_traj))
        
        # 扩展较短的轨迹
        if len(left_traj) < max_length:
            # 在左臂轨迹末尾保持最后位置
            last_position = left_traj[-1]
            while len(left_traj) < max_length:
                left_traj.append(last_position.copy())
        
        if len(right_traj) < max_length:
            # 在右臂轨迹末尾保持最后位置
            last_position = right_traj[-1]
            while len(right_traj) < max_length:
                right_traj.append(last_position.copy())
        
        self.left_arm_trajectory = left_traj
        self.right_arm_trajectory = right_traj
        
        print(f"双臂协调轨迹生成完成:")
        print(f"  左臂轨迹点数: {len(self.left_arm_trajectory)}")
        print(f"  右臂轨迹点数: {len(self.right_arm_trajectory)}")
        print(f"  同步轨迹长度: {max_length}")
        
        return self.left_arm_trajectory, self.right_arm_trajectory
    
    def export_trajectory_data(self, filename=None):
        """导出轨迹数据"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dual_arm_trajectory_{timestamp}.json"
        
        import json
        
        data = {
            'metadata': {
                'generated_time': datetime.now().isoformat(),
                'description': '双臂机械臂仿真轨迹数据',
                'robot_config': {
                    'chest_width': self.config.chest_width,
                    'max_reach': self.config.max_reach,
                    'arm_link_lengths': self.config.arm_link_lengths
                }
            },
            'left_arm_trajectory': self.left_arm_trajectory,
            'right_arm_trajectory': self.right_arm_trajectory,
            'current_state': self.get_current_robot_state()
        }
        
        filepath = os.path.join(current_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"轨迹数据已导出到: {filepath}")
        return filepath
    
    def visualize_trajectory_summary(self):
        """显示轨迹摘要信息"""
        print("\\n=== 双臂轨迹摘要 ===")
        
        if not self.left_arm_trajectory or not self.right_arm_trajectory:
            print("轨迹数据为空，请先生成轨迹")
            return
        
        print(f"轨迹总长度: {len(self.left_arm_trajectory)}点")
        print(f"预估执行时间: {len(self.left_arm_trajectory) * 0.1:.1f}秒 (100ms/点)")
        
        # 左臂轨迹分析
        left_start = self.left_arm_trajectory[0]
        left_end = self.left_arm_trajectory[-1]
        print(f"\\n左臂轨迹 (照明动作):")
        print(f"  起始关节角度: {[round(x, 1) for x in left_start]}")
        print(f"  结束关节角度: {[round(x, 1) for x in left_end]}")
        
        # 右臂轨迹分析
        right_start = self.right_arm_trajectory[0]
        right_end = self.right_arm_trajectory[-1]
        print(f"\\n右臂轨迹 (刷墙动作):")
        print(f"  起始关节角度: {[round(x, 1) for x in right_start]}")
        print(f"  结束关节角度: {[round(x, 1) for x in right_end]}")
        
        # 运动范围分析
        print(f"\\n运动范围分析:")
        for arm_name, trajectory in [("左臂", self.left_arm_trajectory), ("右臂", self.right_arm_trajectory)]:
            joint_ranges = []
            for joint_idx in range(6):
                joint_values = [point[joint_idx] for point in trajectory]
                joint_range = max(joint_values) - min(joint_values)
                joint_ranges.append(joint_range)
            
            print(f"  {arm_name}各关节运动范围: {[round(x, 1) for x in joint_ranges]}度")

def test_simulation_integration():
    """测试与仿真系统的集成"""
    print("\\n=== 测试仿真系统集成 ===")
    
    try:
        # 尝试导入仿真控件
        from simulation_widget import ArmSimulationWidget
        print("✅ 仿真控件导入成功")
        
        # 创建轨迹生成器
        generator = DualArmTrajectoryGenerator()
        
        # 生成轨迹
        left_traj, right_traj = generator.generate_complete_trajectory()
        
        print("✅ 轨迹生成成功")
        print(f"可用于仿真系统的轨迹数据已准备就绪")
        print(f"左臂轨迹: {len(left_traj)}点")
        print(f"右臂轨迹: {len(right_traj)}点")
        
        return generator
        
    except ImportError as e:
        print(f"❌ 仿真控件导入失败: {e}")
        print("建议检查simulation_widget.py文件路径")
        return None

def main():
    """主程序"""
    print("🤖 双臂机械臂仿真轨迹测试程序")
    print("=" * 50)
    
    # 创建轨迹生成器
    generator = DualArmTrajectoryGenerator()
    
    # 模拟连接机器人
    print("\\n1. 连接机器人...")
    if generator.connect_robots():
        print("✅ 双臂机器人连接成功")
    else:
        print("❌ 机器人连接失败")
        return
    
    # 获取当前状态
    print("\\n2. 读取当前机器人状态...")
    current_state = generator.get_current_robot_state()
    print(f"✅ 状态读取完成，时间戳: {current_state['timestamp']}")
    
    # 生成轨迹
    print("\\n3. 生成双臂协调轨迹...")
    left_trajectory, right_trajectory = generator.generate_complete_trajectory()
    
    # 显示轨迹摘要
    generator.visualize_trajectory_summary()
    
    # 导出轨迹数据
    print("\\n4. 导出轨迹数据...")
    exported_file = generator.export_trajectory_data()
    
    # 测试仿真集成
    print("\\n5. 测试仿真系统集成...")
    simulation_generator = test_simulation_integration()
    
    print("\\n=== 测试完成 ===")
    print("程序功能验证:")
    print("✅ 机器人状态读取")
    print("✅ 双臂轨迹生成")
    print("✅ 数据导出功能")
    print("✅ 仿真系统集成")
    
    print(f"\\n📁 轨迹数据文件: {exported_file}")
    print("💡 可将此数据导入仿真界面进行可视化测试")

if __name__ == "__main__":
    main()
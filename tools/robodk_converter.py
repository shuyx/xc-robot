#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RoboDK参数转换工具
用于在RoboDK参数和实际FR3机械臂参数之间进行转换
"""

import numpy as np
import json
from typing import List, Dict, Tuple

class RoboDKConverter:
    """RoboDK参数转换器"""
    
    def __init__(self):
        # RoboDK中的FR3 DH参数 (基于RoboDK分析)
        self.robodk_dh = {
            'alpha': [0, -90, 0, 90, -90, 90],      # 连杆扭转角 (度)
            'a': [0, 0, 316, 0, 0, 0],              # 连杆长度 (mm)
            'd': [333, 0, 0, 384, 0, 107],          # 连杆偏移 (mm)
            'theta_offset': [0, 0, 0, 0, 0, 0]      # RoboDK中无偏移
        }
        
        # 实际FR3机械臂DH参数
        self.robot_dh = {
            'alpha': [0, -90, 0, 90, -90, 90],      # 连杆扭转角 (度)
            'a': [0, 0, 316, 0, 0, 0],              # 连杆长度 (mm) 
            'd': [333, 0, 0, 384, 0, 107],          # 连杆偏移 (mm)
            'theta_offset': [0, -90, 90, 0, 0, 0]   # 关节角偏移 (度)
        }
        
        # 坐标系变换矩阵 (如果需要)
        self.coordinate_transform = np.eye(4)
    
    def robodk_to_robot_angles(self, robodk_angles: List[float]) -> List[float]:
        """
        将RoboDK中的关节角度转换为实际机器人角度
        
        Args:
            robodk_angles: RoboDK中的6个关节角度 (度)
        
        Returns:
            实际机器人的6个关节角度 (度)
        """
        robot_angles = robodk_angles.copy()
        
        # 应用角度偏移补偿
        robot_angles[1] += 90   # J2: 补偿肩部机械偏移
        robot_angles[2] -= 90   # J3: 补偿肘部机械偏移
        
        return robot_angles
    
    def robot_to_robodk_angles(self, robot_angles: List[float]) -> List[float]:
        """
        将实际机器人角度转换为RoboDK中的关节角度
        
        Args:
            robot_angles: 实际机器人的6个关节角度 (度)
        
        Returns:
            RoboDK中的6个关节角度 (度)
        """
        robodk_angles = robot_angles.copy()
        
        # 逆向角度偏移补偿
        robodk_angles[1] -= 90  # J2: 逆向补偿肩部机械偏移
        robodk_angles[2] += 90  # J3: 逆向补偿肘部机械偏移
        
        return robodk_angles
    
    def build_transform_matrix(self, alpha: float, a: float, d: float, theta: float) -> np.ndarray:
        """构建DH变换矩阵"""
        ca, sa = np.cos(np.radians(alpha)), np.sin(np.radians(alpha))
        ct, st = np.cos(np.radians(theta)), np.sin(np.radians(theta))
        
        T = np.array([
            [ct,    -st,    0,      a],
            [st*ca, ct*ca,  -sa,    -d*sa],
            [st*sa, ct*sa,  ca,     d*ca],
            [0,     0,      0,      1]
        ])
        
        return T
    
    def forward_kinematics_robodk(self, joint_angles: List[float]) -> np.ndarray:
        """使用RoboDK参数计算正向运动学"""
        T_cumulative = np.eye(4)
        
        for i in range(6):
            alpha = self.robodk_dh['alpha'][i]
            a = self.robodk_dh['a'][i]
            d = self.robodk_dh['d'][i]
            theta = joint_angles[i] + self.robodk_dh['theta_offset'][i]
            
            T_i = self.build_transform_matrix(alpha, a, d, theta)
            T_cumulative = T_cumulative @ T_i
        
        return T_cumulative
    
    def forward_kinematics_robot(self, joint_angles: List[float]) -> np.ndarray:
        """使用实际机器人参数计算正向运动学"""
        T_cumulative = np.eye(4)
        
        for i in range(6):
            alpha = self.robot_dh['alpha'][i]
            a = self.robot_dh['a'][i]
            d = self.robot_dh['d'][i]
            theta = joint_angles[i] + self.robot_dh['theta_offset'][i]
            
            T_i = self.build_transform_matrix(alpha, a, d, theta)
            T_cumulative = T_cumulative @ T_i
        
        return T_cumulative
    
    def compare_forward_kinematics(self, test_angles: List[List[float]]) -> Dict:
        """比较RoboDK和实际机器人的正向运动学"""
        results = {}
        
        print("🔄 比较RoboDK与实际机器人的正向运动学...")
        
        for i, angles in enumerate(test_angles):
            print(f"  测试角度 {i+1}: {[f'{a:.1f}' for a in angles]}")
            
            # RoboDK计算
            T_robodk = self.forward_kinematics_robodk(angles)
            pos_robodk = T_robodk[:3, 3]
            
            # 转换角度后用实际机器人参数计算
            robot_angles = self.robodk_to_robot_angles(angles)
            T_robot = self.forward_kinematics_robot(robot_angles)
            pos_robot = T_robot[:3, 3]
            
            # 计算误差
            position_error = np.linalg.norm(pos_robodk - pos_robot)
            
            results[f"test_{i+1}"] = {
                'robodk_angles': angles,
                'robot_angles': robot_angles,
                'robodk_position': pos_robodk.tolist(),
                'robot_position': pos_robot.tolist(),
                'position_error': position_error,
                'robodk_transform': T_robodk.tolist(),
                'robot_transform': T_robot.tolist()
            }
            
            print(f"    RoboDK位置: [{pos_robodk[0]:.1f}, {pos_robodk[1]:.1f}, {pos_robodk[2]:.1f}] mm")
            print(f"    机器人位置: [{pos_robot[0]:.1f}, {pos_robot[1]:.1f}, {pos_robot[2]:.1f}] mm")
            print(f"    位置误差: {position_error:.3f} mm")
            print()
        
        return results
    
    def extract_euler_angles(self, rotation_matrix: np.ndarray) -> List[float]:
        """从旋转矩阵提取欧拉角 (ZYX顺序)"""
        R = rotation_matrix
        
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        
        if sy > 1e-6:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
        
        return [np.degrees(x), np.degrees(y), np.degrees(z)]
    
    def validate_conversion(self, test_cases: Dict[str, List[float]]) -> Dict:
        """验证角度转换的正确性"""
        print("✅ 验证角度转换...")
        
        results = {}
        
        for case_name, robot_angles in test_cases.items():
            print(f"  测试用例: {case_name}")
            
            # 机器人角度 → RoboDK角度 → 机器人角度
            robodk_angles = self.robot_to_robodk_angles(robot_angles)
            converted_back = self.robodk_to_robot_angles(robodk_angles)
            
            # 计算转换误差
            conversion_error = np.linalg.norm(np.array(robot_angles) - np.array(converted_back))
            
            # 计算末端位姿
            T_original = self.forward_kinematics_robot(robot_angles)
            T_converted = self.forward_kinematics_robot(converted_back)
            
            pose_error = np.linalg.norm(T_original[:3, 3] - T_converted[:3, 3])
            
            results[case_name] = {
                'original_robot_angles': robot_angles,
                'robodk_angles': robodk_angles,
                'converted_back_angles': converted_back,
                'angle_conversion_error': conversion_error,
                'pose_error': pose_error,
                'is_valid': conversion_error < 1e-10 and pose_error < 1e-6
            }
            
            print(f"    原始角度: {[f'{a:.1f}' for a in robot_angles]}")
            print(f"    RoboDK角度: {[f'{a:.1f}' for a in robodk_angles]}")
            print(f"    转换回角度: {[f'{a:.1f}' for a in converted_back]}")
            print(f"    角度误差: {conversion_error:.6f} °")
            print(f"    位姿误差: {pose_error:.6f} mm")
            print(f"    转换有效: {'✅' if results[case_name]['is_valid'] else '❌'}")
            print()
        
        return results
    
    def generate_robodk_program(self, waypoints: List[List[float]], filename: str = "fr3_program.py"):
        """生成RoboDK程序代码"""
        
        program_template = '''# RoboDK程序 - FR3机械臂
# 自动生成的程序文件

from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox

# 连接到RoboDK
RDK = robolink.Robolink()

# 获取机器人
robot = RDK.Item('FR3')

# 设置运动参数
robot.setSpeed(50)  # 设置速度为50%
robot.setAcceleration(50)  # 设置加速度为50%

print("开始执行FR3机械臂程序...")

# 路径点 (关节角度，单位：度)
waypoints = {waypoints_data}

# 执行路径
for i, angles in enumerate(waypoints):
    print(f"移动到路径点 {{i+1}}: {{angles}}")
    
    # 关节运动
    robot.MoveJ(angles)
    
    # 短暂停留
    RDK.Pause(0.5)

print("程序执行完成")
'''
        
        # 转换为RoboDK角度
        robodk_waypoints = []
        for waypoint in waypoints:
            robodk_angles = self.robot_to_robodk_angles(waypoint)
            robodk_waypoints.append(robodk_angles)
        
        # 生成程序代码
        program_code = program_template.format(waypoints_data=robodk_waypoints)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(program_code)
        
        print(f"📄 RoboDK程序已生成: {filename}")
        print(f"    包含 {len(waypoints)} 个路径点")
        
        return {
            'filename': filename,
            'waypoint_count': len(waypoints),
            'original_waypoints': waypoints,
            'robodk_waypoints': robodk_waypoints
        }
    
    def analyze_parameter_differences(self) -> Dict:
        """分析RoboDK与实际机器人参数的差异"""
        print("📊 分析参数差异...")
        
        differences = {
            'dh_parameters': {},
            'key_differences': [],
            'impact_analysis': {}
        }
        
        # 比较DH参数
        for param in ['alpha', 'a', 'd', 'theta_offset']:
            robodk_values = self.robodk_dh[param]
            robot_values = self.robot_dh[param]
            
            param_diff = np.array(robot_values) - np.array(robodk_values)
            differences['dh_parameters'][param] = {
                'robodk': robodk_values,
                'robot': robot_values,
                'difference': param_diff.tolist(),
                'max_diff': float(np.max(np.abs(param_diff)))
            }
        
        # 识别关键差异
        theta_offset_diff = differences['dh_parameters']['theta_offset']['difference']
        for i, diff in enumerate(theta_offset_diff):
            if abs(diff) > 1:  # 大于1度的差异
                differences['key_differences'].append(f"Joint {i+1}: θ offset = {diff}°")
        
        # 影响分析
        test_angles = [0, -30, 90, 0, 60, 0]  # 典型测试角度
        
        T_robodk = self.forward_kinematics_robodk(test_angles)
        robot_angles = self.robodk_to_robot_angles(test_angles)
        T_robot = self.forward_kinematics_robot(robot_angles)
        
        position_impact = np.linalg.norm(T_robodk[:3, 3] - T_robot[:3, 3])
        
        differences['impact_analysis'] = {
            'test_case': test_angles,
            'position_difference': position_impact,
            'requires_conversion': position_impact > 1.0  # 1mm阈值
        }
        
        print("  关键差异:")
        for diff in differences['key_differences']:
            print(f"    - {diff}")
        
        print(f"\n  影响分析:")
        print(f"    位置差异: {position_impact:.3f} mm")
        print(f"    需要转换: {'是' if differences['impact_analysis']['requires_conversion'] else '否'}")
        
        return differences

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RoboDK参数转换工具")
    parser.add_argument("--test", choices=['conversion', 'comparison', 'analysis', 'all'], 
                       default='all', help="指定测试类型")
    parser.add_argument("--generate-program", help="生成RoboDK程序文件名")
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = RoboDKConverter()
    
    # 测试用例
    test_cases = {
        'zero_position': [0, 0, 0, 0, 0, 0],
        'initial_pose': [0, -30, 90, 0, 60, 0],
        'typical_work': [90, -90, 90, 0, 90, 0],
        'boundary_test': [-90, -45, 120, -45, 45, 90]
    }
    
    # 执行指定测试
    if args.test in ['conversion', 'all']:
        converter.validate_conversion(test_cases)
    
    if args.test in ['comparison', 'all']:
        converter.compare_forward_kinematics(list(test_cases.values()))
    
    if args.test in ['analysis', 'all']:
        converter.analyze_parameter_differences()
    
    # 生成RoboDK程序
    if args.generate_program:
        waypoints = list(test_cases.values())
        converter.generate_robodk_program(waypoints, args.generate_program)

if __name__ == "__main__":
    main()
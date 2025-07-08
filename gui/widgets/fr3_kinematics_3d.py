#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂运动学与3D可视化集成
"""

import numpy as np
import sys
import os

# 添加FR3控制库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from fr3_control.fairino import Robot

class FR3Kinematics:
    """FR3运动学计算类"""
    
    def __init__(self):
        # FR3 DH参数（基于文档）
        self.dh_params = {
            'a': [0, 0, 0, 0, 0, 0],          # 连杆长度
            'd': [0.147, 0, 0.281, 0, 0.209, 0.113],  # 连杆偏移
            'alpha': [np.pi/2, -np.pi/2, np.pi/2, -np.pi/2, np.pi/2, 0],  # 连杆扭转
            'offset': [0, 0, 0, 0, 0, 0]     # 关节偏移
        }
        
    def dh_matrix(self, theta, d, a, alpha):
        """计算DH变换矩阵"""
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)
        
        return np.array([
            [ct, -st*ca, st*sa, a*ct],
            [st, ct*ca, -ct*sa, a*st],
            [0, sa, ca, d],
            [0, 0, 0, 1]
        ])
        
    def forward_kinematics(self, joint_angles):
        """正向运动学计算
        
        Args:
            joint_angles: 6个关节角度（弧度）
            
        Returns:
            positions: 每个关节的位置列表
            transforms: 每个关节的变换矩阵列表
        """
        positions = [[0, 0, 0]]  # 基座位置
        transforms = [np.eye(4)]  # 基座变换
        
        T = np.eye(4)
        for i in range(6):
            theta = joint_angles[i] + self.dh_params['offset'][i]
            d = self.dh_params['d'][i]
            a = self.dh_params['a'][i]
            alpha = self.dh_params['alpha'][i]
            
            # 计算当前关节的变换矩阵
            T_i = self.dh_matrix(theta, d, a, alpha)
            T = T @ T_i
            
            # 提取位置
            position = T[:3, 3] * 1000  # 转换为毫米
            positions.append(position.tolist())
            transforms.append(T.copy())
            
        return positions, transforms
        
    def inverse_kinematics(self, target_pos, target_rot=None):
        """逆向运动学计算（使用FR3 SDK）
        
        Args:
            target_pos: 目标位置 [x, y, z] (mm)
            target_rot: 目标姿态 [rx, ry, rz] (度)
            
        Returns:
            joint_angles: 6个关节角度（度）
        """
        # 这里需要实际的FR3机器人连接
        # 示例代码：
        # robot = Robot.RPC('192.168.58.2')
        # ret = robot.GetInverseKin(0, target_pos + target_rot)
        # if ret[0] == 0:
        #     return ret[1]
        
        # 临时返回示例值
        return [0, -30, -60, -90, 0, 0]


class FR3RobotModel:
    """FR3机器人3D模型"""
    
    def __init__(self):
        self.kinematics = FR3Kinematics()
        self.joint_angles = [0, 0, 0, 0, 0, 0]  # 当前关节角度（弧度）
        
    def update_joints(self, joint_angles_deg):
        """更新关节角度（度）"""
        self.joint_angles = [np.radians(angle) for angle in joint_angles_deg]
        
    def get_joint_positions(self):
        """获取所有关节位置"""
        positions, _ = self.kinematics.forward_kinematics(self.joint_angles)
        return positions
        
    def get_end_effector_pose(self):
        """获取末端执行器位姿"""
        positions, transforms = self.kinematics.forward_kinematics(self.joint_angles)
        
        # 最后一个变换矩阵就是末端执行器的位姿
        T_end = transforms[-1]
        
        # 提取位置（毫米）
        position = T_end[:3, 3] * 1000
        
        # 提取旋转矩阵并转换为欧拉角
        R = T_end[:3, :3]
        # 简化的欧拉角提取（ZYX顺序）
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        singular = sy < 1e-6
        
        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
            
        rotation = np.degrees([x, y, z])
        
        return position, rotation
        
    def move_to_pose(self, target_pos, target_rot=None):
        """移动到目标位姿"""
        joint_angles_deg = self.kinematics.inverse_kinematics(target_pos, target_rot)
        self.update_joints(joint_angles_deg)
        return joint_angles_deg


# 集成到3D显示控件
def integrate_fr3_kinematics(robot_3d_widget):
    """将FR3运动学集成到3D显示控件"""
    
    # 创建FR3模型
    fr3_model = FR3RobotModel()
    
    # 更新关节显示的函数
    def update_robot_display(joint_angles_deg):
        # 更新运动学模型
        fr3_model.update_joints(joint_angles_deg)
        
        # 获取关节位置
        positions = fr3_model.get_joint_positions()
        
        # 更新3D显示
        if hasattr(robot_3d_widget, 'update_joint_positions'):
            robot_3d_widget.update_joint_positions(positions)
        
        # 更新关节角度
        robot_3d_widget.update_joint_angles(joint_angles_deg)
        
    return update_robot_display, fr3_model


# 使用示例
if __name__ == "__main__":
    # 创建FR3运动学模型
    fr3 = FR3RobotModel()
    
    # 设置关节角度
    joint_angles = [0, -30, -60, -90, 0, 0]  # 度
    fr3.update_joints(joint_angles)
    
    # 获取正向运动学结果
    positions = fr3.get_joint_positions()
    print("关节位置:")
    for i, pos in enumerate(positions):
        print(f"  关节{i}: {pos}")
    
    # 获取末端执行器位姿
    pos, rot = fr3.get_end_effector_pose()
    print(f"\n末端执行器位置: {pos}")
    print(f"末端执行器姿态: {rot}")
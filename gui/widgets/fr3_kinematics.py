#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂运动学模型
实现正向运动学和逆运动学计算
"""

import numpy as np
import math

class FR3Kinematics:
    """FR3机械臂运动学类"""
    
    def __init__(self):
        """初始化FR3运动学参数"""
        # FR3机械臂的DH参数 (根据实际机械臂调整)
        # [a, alpha, d, theta_offset]
        self.dh_params = [
            [0,     0,          0.333,    0],      # 关节1
            [0,     -np.pi/2,   0,        0],      # 关节2
            [0,     np.pi/2,    0.316,    0],      # 关节3
            [0.0825, np.pi/2,   0,        0],      # 关节4
            [-0.0825, -np.pi/2,  0.384,    0],      # 关节5
            [0,     0,          0,        0]       # 关节6
        ]
        
        # 关节角度限制 (度)
        self.joint_limits = [
            [-165, 165],  # 关节1
            [-110, 110],  # 关节2  
            [-165, 165],  # 关节3
            [-110, 110],  # 关节4
            [-165, 165],  # 关节5
            [-180, 180]   # 关节6
        ]
        
        # 当前关节角度
        self.joint_angles = [0.0] * 6
        
    def deg_to_rad(self, angles):
        """角度转弧度"""
        return [math.radians(angle) for angle in angles]
        
    def rad_to_deg(self, angles):
        """弧度转角度"""
        return [math.degrees(angle) for angle in angles]
        
    def dh_transform(self, a, alpha, d, theta):
        """DH变换矩阵"""
        ct = math.cos(theta)
        st = math.sin(theta)
        ca = math.cos(alpha)
        sa = math.sin(alpha)
        
        return np.array([
            [ct,    -st*ca,     st*sa,      a*ct],
            [st,    ct*ca,      -ct*sa,     a*st],
            [0,     sa,         ca,         d],
            [0,     0,          0,          1]
        ])
    
    def forward_kinematics(self, joint_angles_deg):
        """正向运动学：从关节角度计算末端位姿"""
        joint_angles_rad = self.deg_to_rad(joint_angles_deg)
        
        # 初始变换矩阵
        T = np.eye(4)
        
        # 累积变换矩阵
        transforms = []
        for i in range(6):
            a, alpha, d, theta_offset = self.dh_params[i]
            theta = joint_angles_rad[i] + theta_offset
            
            Ti = self.dh_transform(a, alpha, d, theta)
            transforms.append(Ti)
            T = np.dot(T, Ti)
        
        # 提取位置和姿态
        position = T[:3, 3]
        rotation_matrix = T[:3, :3]
        
        # 将旋转矩阵转换为欧拉角 (ZYX顺序)
        euler_angles = self.rotation_matrix_to_euler(rotation_matrix)
        
        return {
            'position': position * 1000,  # 转换为mm
            'orientation': euler_angles,   # 度
            'transform_matrix': T,
            'joint_transforms': transforms
        }
    
    def rotation_matrix_to_euler(self, R):
        """旋转矩阵转欧拉角 (ZYX顺序)"""
        # 提取欧拉角
        sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        
        singular = sy < 1e-6
        
        if not singular:
            x = math.atan2(R[2, 1], R[2, 2])
            y = math.atan2(-R[2, 0], sy)
            z = math.atan2(R[1, 0], R[0, 0])
        else:
            x = math.atan2(-R[1, 2], R[1, 1])
            y = math.atan2(-R[2, 0], sy)
            z = 0
        
        return [math.degrees(x), math.degrees(y), math.degrees(z)]
    
    def euler_to_rotation_matrix(self, roll, pitch, yaw):
        """欧拉角转旋转矩阵"""
        r = math.radians(roll)
        p = math.radians(pitch)
        y = math.radians(yaw)
        
        # 旋转矩阵
        R_x = np.array([
            [1, 0, 0],
            [0, math.cos(r), -math.sin(r)],
            [0, math.sin(r), math.cos(r)]
        ])
        
        R_y = np.array([
            [math.cos(p), 0, math.sin(p)],
            [0, 1, 0],
            [-math.sin(p), 0, math.cos(p)]
        ])
        
        R_z = np.array([
            [math.cos(y), -math.sin(y), 0],
            [math.sin(y), math.cos(y), 0],
            [0, 0, 1]
        ])
        
        return np.dot(R_z, np.dot(R_y, R_x))
    
    def inverse_kinematics(self, target_pos, target_orient):
        """逆运动学：从末端位姿计算关节角度"""
        # 这里实现一个简化的逆运动学求解器
        # 实际应用中可以使用更复杂的算法或调用FR3 SDK
        
        # 目标位置 (mm转m)
        target_position = np.array(target_pos) / 1000.0
        
        # 目标姿态 (度转弧度)
        target_rotation = self.euler_to_rotation_matrix(
            target_orient[0], target_orient[1], target_orient[2]
        )
        
        # 构造目标变换矩阵
        target_transform = np.eye(4)
        target_transform[:3, :3] = target_rotation
        target_transform[:3, 3] = target_position
        
        # 使用数值求解方法 (简化版本)
        # 实际应用中应该使用更精确的算法
        best_joints = self.joint_angles.copy()
        best_error = float('inf')
        
        # 简单的迭代求解
        for _ in range(10):
            # 计算当前位姿
            current_fk = self.forward_kinematics(best_joints)
            current_pos = current_fk['position'] / 1000.0
            
            # 计算位置误差
            pos_error = np.linalg.norm(current_pos - target_position)
            
            if pos_error < best_error:
                best_error = pos_error
            
            # 简单的梯度下降调整
            if pos_error > 0.001:  # 1mm精度
                # 对每个关节进行微调
                for i in range(6):
                    delta = 1.0  # 度
                    test_joints = best_joints.copy()
                    test_joints[i] += delta
                    
                    # 检查关节限制
                    if (test_joints[i] >= self.joint_limits[i][0] and 
                        test_joints[i] <= self.joint_limits[i][1]):
                        
                        test_fk = self.forward_kinematics(test_joints)
                        test_pos = test_fk['position'] / 1000.0
                        test_error = np.linalg.norm(test_pos - target_position)
                        
                        if test_error < pos_error:
                            best_joints[i] = test_joints[i]
            else:
                break
        
        return best_joints
    
    def check_joint_limits(self, joint_angles):
        """检查关节限制"""
        for i, angle in enumerate(joint_angles):
            if angle < self.joint_limits[i][0] or angle > self.joint_limits[i][1]:
                return False
        return True
    
    def clamp_joint_angles(self, joint_angles):
        """限制关节角度在有效范围内"""
        clamped = []
        for i, angle in enumerate(joint_angles):
            min_limit, max_limit = self.joint_limits[i]
            clamped.append(max(min_limit, min(max_limit, angle)))
        return clamped
    
    def set_joint_angles(self, joint_angles):
        """设置关节角度"""
        self.joint_angles = self.clamp_joint_angles(joint_angles)
        return self.joint_angles
    
    def get_joint_angles(self):
        """获取当前关节角度"""
        return self.joint_angles.copy()
    
    def get_end_effector_pose(self):
        """获取末端执行器位姿"""
        return self.forward_kinematics(self.joint_angles)

# 测试代码
if __name__ == "__main__":
    # 创建运动学对象
    fr3 = FR3Kinematics()
    
    # 测试正向运动学
    print("=== 正向运动学测试 ===")
    test_joints = [0, -30, 90, 0, 60, 0]
    fk_result = fr3.forward_kinematics(test_joints)
    print(f"关节角度: {test_joints}")
    print(f"末端位置: {fk_result['position']}")
    print(f"末端姿态: {fk_result['orientation']}")
    
    # 测试逆运动学
    print("\n=== 逆运动学测试 ===")
    target_pos = [200, 100, 400]  # mm
    target_orient = [0, 0, 0]     # 度
    ik_result = fr3.inverse_kinematics(target_pos, target_orient)
    print(f"目标位置: {target_pos}")
    print(f"目标姿态: {target_orient}")
    print(f"计算关节角度: {ik_result}")
    
    # 验证逆运动学结果
    fk_verify = fr3.forward_kinematics(ik_result)
    print(f"验证位置: {fk_verify['position']}")
    print(f"验证姿态: {fk_verify['orientation']}")
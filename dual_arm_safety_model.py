"""
双臂机器人安全避障模型
用于FR3双臂机器人的碰撞检测和安全规划
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import warnings


class DualArmSafetyModel:
    """双臂机器人安全避障模型"""
    
    def __init__(self):
        # FR3机械臂DH参数 (Modified DH Convention)
        # [alpha(rad), a(mm), d(mm), theta_offset(rad)]
        self.dh_params = [
            [0,         0,    333,  0],           # Joint 1
            [-np.pi/2,  0,    0,    -np.pi/2],   # Joint 2
            [0,         316,  0,    np.pi/2],     # Joint 3
            [np.pi/2,   0,    384,  0],           # Joint 4
            [-np.pi/2,  0,    0,    0],           # Joint 5
            [np.pi/2,   0,    107,  0]            # Joint 6
        ]
        
        # 关节限制 (弧度)
        self.joint_limits = [
            [-170*np.pi/180, 170*np.pi/180],  # Joint 1
            [-120*np.pi/180, 120*np.pi/180],  # Joint 2
            [-170*np.pi/180, 170*np.pi/180],  # Joint 3
            [-170*np.pi/180, 170*np.pi/180],  # Joint 4
            [-120*np.pi/180, 120*np.pi/180],  # Joint 5
            [-175*np.pi/180, 175*np.pi/180]   # Joint 6
        ]
        
        # 双臂配置参数
        self.base_distance = 400  # 两臂基座间距 (mm)
        self.base_height = 1250   # 基座高度 (mm)
        
        # 安全参数
        self.safety_margin = 50   # 安全裕度 (mm)
        self.link_radius = 40     # 连杆简化半径 (mm)
        
        # 工作空间参数
        self.max_reach = 630      # 最大工作半径 (mm)
        self.min_reach = 100      # 最小工作半径 (mm)
        
    def dh_transform(self, alpha: float, a: float, d: float, theta: float) -> np.ndarray:
        """计算DH变换矩阵"""
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)
        
        T = np.array([
            [ct, -st*ca,  st*sa,  a*ct],
            [st,  ct*ca, -ct*sa,  a*st],
            [0,   sa,     ca,     d],
            [0,   0,      0,      1]
        ])
        
        return T
    
    def forward_kinematics(self, joint_angles: List[float], arm: str = 'left') -> np.ndarray:
        """
        正向运动学计算
        
        Args:
            joint_angles: 6个关节角度 (弧度)
            arm: 'left' 或 'right'
            
        Returns:
            4x4变换矩阵，表示末端位姿
        """
        if len(joint_angles) != 6:
            raise ValueError("需要6个关节角度")
            
        # 基座变换（左臂在原点，右臂在x轴正方向）
        if arm == 'left':
            T_base = np.eye(4)
        else:
            T_base = np.eye(4)
            T_base[0, 3] = self.base_distance
            
        T = T_base.copy()
        
        # 计算各关节变换
        for i in range(6):
            alpha, a, d, theta_offset = self.dh_params[i]
            theta = joint_angles[i] + theta_offset
            
            Ti = self.dh_transform(alpha, a, d, theta)
            T = T @ Ti
            
        return T
    
    def get_joint_positions(self, joint_angles: List[float], arm: str = 'left') -> List[np.ndarray]:
        """
        获取所有关节的位置
        
        Args:
            joint_angles: 6个关节角度
            arm: 'left' 或 'right'
            
        Returns:
            7个3D位置点（基座+6个关节）
        """
        positions = []
        
        # 基座变换
        if arm == 'left':
            T = np.eye(4)
        else:
            T = np.eye(4)
            T[0, 3] = self.base_distance
            
        positions.append(T[:3, 3])
        
        # 计算各关节位置
        for i in range(6):
            alpha, a, d, theta_offset = self.dh_params[i]
            theta = joint_angles[i] + theta_offset
            
            Ti = self.dh_transform(alpha, a, d, theta)
            T = T @ Ti
            positions.append(T[:3, 3])
            
        return positions
    
    def inverse_kinematics(self, target_pose: np.ndarray, arm: str = 'left', 
                          current_angles: Optional[List[float]] = None) -> Optional[List[float]]:
        """
        逆运动学求解（简化的数值方法）
        
        Args:
            target_pose: 目标末端位姿 (4x4矩阵)
            arm: 'left' 或 'right'
            current_angles: 当前关节角度（用于初值）
            
        Returns:
            关节角度列表，如果无解返回None
        """
        # 简化实现：使用迭代法求解
        if current_angles is None:
            # 使用零位作为初值
            angles = [0, 0, 0, 0, 0, 0]
        else:
            angles = list(current_angles)
            
        # 迭代求解参数
        max_iterations = 100
        tolerance = 1e-3
        alpha = 0.1  # 学习率
        
        for iteration in range(max_iterations):
            # 计算当前位姿
            current_pose = self.forward_kinematics(angles, arm)
            
            # 计算位置误差
            pos_error = target_pose[:3, 3] - current_pose[:3, 3]
            
            # 计算姿态误差（简化：只考虑z轴方向）
            rot_error = np.cross(current_pose[:3, 2], target_pose[:3, 2])
            
            # 组合误差
            error = np.concatenate([pos_error, rot_error * 0.1])
            
            # 检查收敛
            if np.linalg.norm(error) < tolerance:
                # 检查关节限制
                valid = True
                for i, angle in enumerate(angles):
                    if angle < self.joint_limits[i][0] or angle > self.joint_limits[i][1]:
                        valid = False
                        break
                
                if valid:
                    return angles
                else:
                    return None
            
            # 计算雅可比矩阵（数值方法）
            J = self.compute_jacobian(angles, arm)
            
            # 更新关节角度
            try:
                delta_q = alpha * np.linalg.pinv(J) @ error
                angles = [angles[i] + delta_q[i] for i in range(6)]
            except:
                return None
                
        return None  # 未收敛
    
    def compute_jacobian(self, joint_angles: List[float], arm: str = 'left') -> np.ndarray:
        """计算雅可比矩阵（数值方法）"""
        J = np.zeros((6, 6))
        epsilon = 1e-6
        
        # 当前位姿
        T0 = self.forward_kinematics(joint_angles, arm)
        p0 = T0[:3, 3]
        z0 = T0[:3, 2]
        
        # 数值微分
        for i in range(6):
            angles_plus = joint_angles.copy()
            angles_plus[i] += epsilon
            
            T_plus = self.forward_kinematics(angles_plus, arm)
            p_plus = T_plus[:3, 3]
            z_plus = T_plus[:3, 2]
            
            # 位置导数
            J[:3, i] = (p_plus - p0) / epsilon
            
            # 姿态导数
            J[3:, i] = (z_plus - z0) / epsilon
            
        return J
    
    def check_self_collision(self, joint_angles: List[float], arm: str) -> bool:
        """
        检查单臂自碰撞
        
        Args:
            joint_angles: 关节角度
            arm: 'left' 或 'right'
            
        Returns:
            True表示有碰撞，False表示安全
        """
        positions = self.get_joint_positions(joint_angles, arm)
        
        # 简化模型：将机械臂视为由连杆连接的圆柱体
        # 检查非相邻连杆之间的距离
        for i in range(len(positions) - 2):
            for j in range(i + 2, len(positions) - 1):
                # 计算线段之间的最短距离
                dist = self.segment_distance(positions[i], positions[i+1], 
                                           positions[j], positions[j+1])
                
                if dist < 2 * self.link_radius + self.safety_margin:
                    return True
                    
        return False
    
    def check_dual_arm_collision(self, left_angles: List[float], 
                                right_angles: List[float]) -> bool:
        """
        检查双臂之间的碰撞
        
        Args:
            left_angles: 左臂关节角度
            right_angles: 右臂关节角度
            
        Returns:
            True表示有碰撞，False表示安全
        """
        left_positions = self.get_joint_positions(left_angles, 'left')
        right_positions = self.get_joint_positions(right_angles, 'right')
        
        # 检查左右臂所有连杆之间的距离
        for i in range(len(left_positions) - 1):
            for j in range(len(right_positions) - 1):
                dist = self.segment_distance(
                    left_positions[i], left_positions[i+1],
                    right_positions[j], right_positions[j+1]
                )
                
                if dist < 2 * self.link_radius + self.safety_margin:
                    return True
                    
        return False
    
    def segment_distance(self, p1: np.ndarray, p2: np.ndarray, 
                        p3: np.ndarray, p4: np.ndarray) -> float:
        """计算两线段之间的最短距离"""
        # 向量表示
        u = p2 - p1
        v = p4 - p3
        w = p1 - p3
        
        a = np.dot(u, u)
        b = np.dot(u, v)
        c = np.dot(v, v)
        d = np.dot(u, w)
        e = np.dot(v, w)
        
        D = a * c - b * b
        
        # 平行情况
        if D < 1e-6:
            s = 0
            t = (b if b > c else c - b) / c if c > 1e-6 else 0
        else:
            s = (b * e - c * d) / D
            t = (a * e - b * d) / D
            
        # 限制参数范围
        s = np.clip(s, 0, 1)
        t = np.clip(t, 0, 1)
        
        # 计算最近点
        closest_p1 = p1 + s * u
        closest_p2 = p3 + t * v
        
        return np.linalg.norm(closest_p2 - closest_p1)
    
    def get_workspace_boundary(self, arm: str, height: float = 0) -> List[Tuple[float, float]]:
        """获取指定高度的工作空间边界"""
        boundary = []
        
        # 基座位置
        if arm == 'left':
            base_x = 0
        else:
            base_x = self.base_distance
            
        # 在圆周上采样点
        for angle in np.linspace(0, 2*np.pi, 36):
            x = base_x + self.max_reach * np.cos(angle)
            y = self.max_reach * np.sin(angle)
            boundary.append((x, y))
            
        return boundary
    
    def check_safety_zone(self, pose: np.ndarray, arm: str) -> bool:
        """
        检查末端是否在安全区域内
        
        Args:
            pose: 末端位姿
            arm: 'left' 或 'right'
            
        Returns:
            True表示在安全区域内
        """
        pos = pose[:3, 3]
        
        # 基座位置
        if arm == 'left':
            base_pos = np.array([0, 0, 0])
        else:
            base_pos = np.array([self.base_distance, 0, 0])
            
        # 计算到基座的距离
        dist = np.linalg.norm(pos - base_pos)
        
        # 检查是否在工作范围内
        if dist < self.min_reach or dist > self.max_reach:
            return False
            
        # 检查是否会与对侧机械臂工作空间重叠
        if arm == 'left':
            # 左臂不应进入右侧空间
            if pos[0] > self.base_distance / 2 - self.safety_margin:
                return False
        else:
            # 右臂不应进入左侧空间
            if pos[0] < self.base_distance / 2 + self.safety_margin:
                return False
                
        return True
    
    def plan_collision_free_motion(self, start_angles: List[float], 
                                  target_pose: np.ndarray, 
                                  arm: str,
                                  other_arm_angles: Optional[List[float]] = None) -> Optional[List[List[float]]]:
        """
        规划无碰撞运动路径
        
        Args:
            start_angles: 起始关节角度
            target_pose: 目标末端位姿
            arm: 'left' 或 'right'
            other_arm_angles: 另一臂的关节角度
            
        Returns:
            关节角度序列，如果无法规划返回None
        """
        # 先求解目标关节角度
        target_angles = self.inverse_kinematics(target_pose, arm, start_angles)
        
        if target_angles is None:
            return None
            
        # 线性插值路径点
        num_points = 20
        path = []
        
        for i in range(num_points + 1):
            t = i / num_points
            angles = []
            
            for j in range(6):
                angle = (1 - t) * start_angles[j] + t * target_angles[j]
                angles.append(angle)
                
            # 检查碰撞
            if self.check_self_collision(angles, arm):
                return None
                
            if other_arm_angles is not None:
                if arm == 'left':
                    if self.check_dual_arm_collision(angles, other_arm_angles):
                        return None
                else:
                    if self.check_dual_arm_collision(other_arm_angles, angles):
                        return None
                        
            path.append(angles)
            
        return path


def test_dual_arm_safety():
    """测试双臂安全模型"""
    
    print("=== 双臂机器人安全避障模型测试 ===\n")
    
    # 创建模型实例
    model = DualArmSafetyModel()
    
    # 测试1：正向运动学
    print("1. 正向运动学测试")
    test_angles = [0, -np.pi/4, np.pi/4, 0, np.pi/6, 0]
    left_pose = model.forward_kinematics(test_angles, 'left')
    right_pose = model.forward_kinematics(test_angles, 'right')
    
    print(f"左臂末端位置: {left_pose[:3, 3]}")
    print(f"右臂末端位置: {right_pose[:3, 3]}")
    print()
    
    # 测试2：逆运动学
    print("2. 逆运动学测试")
    target_pos = np.array([300, 200, 400])
    target_pose = np.eye(4)
    target_pose[:3, 3] = target_pos
    
    left_ik = model.inverse_kinematics(target_pose, 'left')
    if left_ik:
        print(f"左臂逆解成功: {[f'{angle*180/np.pi:.1f}°' for angle in left_ik]}")
        # 验证
        verify_pose = model.forward_kinematics(left_ik, 'left')
        print(f"验证位置: {verify_pose[:3, 3]}")
        print(f"位置误差: {np.linalg.norm(verify_pose[:3, 3] - target_pos):.2f}mm")
    else:
        print("左臂逆解失败")
    print()
    
    # 测试3：碰撞检测
    print("3. 碰撞检测测试")
    
    # 安全姿态
    safe_left = [0, -np.pi/4, np.pi/4, 0, 0, 0]
    safe_right = [0, -np.pi/4, np.pi/4, 0, 0, 0]
    
    collision = model.check_dual_arm_collision(safe_left, safe_right)
    print(f"安全姿态碰撞检测: {'碰撞' if collision else '安全'}")
    
    # 危险姿态（两臂向内）
    danger_left = [np.pi/4, -np.pi/4, np.pi/4, 0, 0, 0]
    danger_right = [-np.pi/4, -np.pi/4, np.pi/4, 0, 0, 0]
    
    collision = model.check_dual_arm_collision(danger_left, danger_right)
    print(f"危险姿态碰撞检测: {'碰撞' if collision else '安全'}")
    print()
    
    # 测试4：安全区域检查
    print("4. 安全区域检查")
    
    # 左臂安全位置
    safe_pose = np.eye(4)
    safe_pose[:3, 3] = [-200, 0, 300]
    print(f"左臂位置 {safe_pose[:3, 3]}: {'安全' if model.check_safety_zone(safe_pose, 'left') else '危险'}")
    
    # 左臂危险位置（太靠近右臂）
    danger_pose = np.eye(4)
    danger_pose[:3, 3] = [300, 0, 300]
    print(f"左臂位置 {danger_pose[:3, 3]}: {'安全' if model.check_safety_zone(danger_pose, 'left') else '危险'}")
    print()
    
    # 测试5：路径规划
    print("5. 路径规划测试")
    
    start = [0, 0, 0, 0, 0, 0]
    target = np.eye(4)
    target[:3, 3] = [200, 100, 400]
    
    path = model.plan_collision_free_motion(start, target, 'left')
    if path:
        print(f"规划成功，路径包含 {len(path)} 个点")
        print(f"起点: {[f'{a*180/np.pi:.0f}°' for a in path[0]]}")
        print(f"终点: {[f'{a*180/np.pi:.0f}°' for a in path[-1]]}")
    else:
        print("路径规划失败")


def create_safety_checker(base_distance: float = 400) -> 'DualArmSafetyModel':
    """
    创建安全检查器实例
    
    Args:
        base_distance: 两臂基座间距(mm)
        
    Returns:
        配置好的安全模型实例
    """
    model = DualArmSafetyModel()
    model.base_distance = base_distance
    return model


def check_dual_arm_safety(left_pose: np.ndarray, 
                         right_pose: np.ndarray,
                         left_angles: Optional[List[float]] = None,
                         right_angles: Optional[List[float]] = None,
                         model: Optional[DualArmSafetyModel] = None) -> Dict[str, any]:
    """
    快速安全检查函数
    
    Args:
        left_pose: 左臂目标末端位姿
        right_pose: 右臂目标末端位姿
        left_angles: 左臂当前关节角度
        right_angles: 右臂当前关节角度
        model: 安全模型实例
        
    Returns:
        包含安全状态的字典
    """
    if model is None:
        model = DualArmSafetyModel()
        
    result = {
        'safe': True,
        'left_in_workspace': True,
        'right_in_workspace': True,
        'collision_detected': False,
        'messages': []
    }
    
    # 检查工作空间
    if not model.check_safety_zone(left_pose, 'left'):
        result['safe'] = False
        result['left_in_workspace'] = False
        result['messages'].append("左臂超出安全工作空间")
        
    if not model.check_safety_zone(right_pose, 'right'):
        result['safe'] = False
        result['right_in_workspace'] = False
        result['messages'].append("右臂超出安全工作空间")
        
    # 如果提供了关节角度，检查碰撞
    if left_angles is not None and right_angles is not None:
        if model.check_dual_arm_collision(left_angles, right_angles):
            result['safe'] = False
            result['collision_detected'] = True
            result['messages'].append("检测到双臂碰撞风险")
            
    return result


if __name__ == "__main__":
    test_dual_arm_safety()
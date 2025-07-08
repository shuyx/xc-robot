#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DH参数分析和验证工具
用于测试FR3机械臂运动学参数的精度和一致性
"""

import numpy as np
import json
from typing import List, Dict, Tuple
from datetime import datetime

class DHParameterAnalyzer:
    """DH参数分析器"""
    
    def __init__(self):
        # FR3精确DH参数 (Modified DH Convention)
        self.dh_params = {
            'alpha': [0, -90, 0, 90, -90, 90],      # 连杆扭转角 (度)
            'a': [0, 0, 316, 0, 0, 0],              # 连杆长度 (mm)
            'd': [333, 0, 0, 384, 0, 107],          # 连杆偏移 (mm)
            'theta_offset': [0, -90, 90, 0, 0, 0]    # 关节角偏移 (度)
        }
        
        # 关节限位 (度)
        self.joint_limits = [
            (-170, 170),   # J1
            (-120, 120),   # J2  
            (-170, 170),   # J3
            (-170, 170),   # J4
            (-120, 120),   # J5
            (-175, 175)    # J6
        ]
        
        # 测试用例
        self.test_cases = {
            'zero_position': [0, 0, 0, 0, 0, 0],
            'initial_pose': [0, -30, 90, 0, 60, 0],
            'typical_work': [90, -90, 90, 0, 90, 0],
            'boundary_test': [-90, -45, 120, -45, 45, 90],
            'extended_reach': [0, -90, 180, 0, 90, 0],
            'compact_pose': [0, -30, 30, 0, 30, 0]
        }
    
    def build_transform_matrix(self, alpha: float, a: float, d: float, theta: float) -> np.ndarray:
        """
        构建Modified DH变换矩阵
        
        Args:
            alpha: 连杆扭转角 (弧度)
            a: 连杆长度 (mm)
            d: 连杆偏移 (mm)  
            theta: 关节角 (弧度)
        
        Returns:
            4x4变换矩阵
        """
        ca, sa = np.cos(alpha), np.sin(alpha)
        ct, st = np.cos(theta), np.sin(theta)
        
        T = np.array([
            [ct,    -st,    0,      a],
            [st*ca, ct*ca,  -sa,    -d*sa],
            [st*sa, ct*sa,  ca,     d*ca],
            [0,     0,      0,      1]
        ])
        
        return T
    
    def forward_kinematics(self, joint_angles: List[float]) -> np.ndarray:
        """
        正向运动学计算
        
        Args:
            joint_angles: 6个关节角度 (度)
        
        Returns:
            4x4末端变换矩阵
        """
        T_cumulative = np.eye(4)
        
        for i in range(6):
            alpha = np.radians(self.dh_params['alpha'][i])
            a = self.dh_params['a'][i]
            d = self.dh_params['d'][i]
            theta = np.radians(joint_angles[i] + self.dh_params['theta_offset'][i])
            
            T_i = self.build_transform_matrix(alpha, a, d, theta)
            T_cumulative = T_cumulative @ T_i
        
        return T_cumulative
    
    def extract_pose(self, T: np.ndarray) -> Dict:
        """
        从变换矩阵提取位置和姿态
        
        Args:
            T: 4x4变换矩阵
        
        Returns:
            位置和姿态信息字典
        """
        # 提取位置
        position = T[:3, 3].tolist()
        
        # 提取旋转矩阵
        R = T[:3, :3]
        
        # 转换为欧拉角 (ZYX顺序)
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        
        if sy > 1e-6:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
        
        orientation = [np.degrees(x), np.degrees(y), np.degrees(z)]
        
        return {
            'position': position,
            'orientation': orientation,
            'rotation_matrix': R.tolist()
        }
    
    def inverse_kinematics_geometric(self, target_pose: np.ndarray) -> List[float]:
        """
        几何法逆运动学求解 (简化版本)
        
        Args:
            target_pose: 4x4目标变换矩阵
        
        Returns:
            6个关节角度 (度)
        """
        # 这是一个简化的逆运动学实现
        # 实际应用中需要更复杂的几何解法
        
        R_06 = target_pose[:3, :3]
        p_06 = target_pose[:3, 3]
        
        # 计算腕部中心位置
        d6 = self.dh_params['d'][5]  # 107mm
        p_wrist = p_06 - d6 * R_06[:, 2]
        
        # 求解前三个关节 (位置)
        q1 = np.arctan2(p_wrist[1], p_wrist[0])
        
        # 简化求解 (需要更完整的几何分析)
        r = np.sqrt(p_wrist[0]**2 + p_wrist[1]**2)
        s = p_wrist[2] - self.dh_params['d'][0]  # 减去基座高度
        
        # 使用余弦定理求解J2, J3
        a2 = self.dh_params['a'][2]  # 316mm
        d4 = self.dh_params['d'][3]  # 384mm
        
        D = (r**2 + s**2 - a2**2 - d4**2) / (2 * a2 * d4)
        D = np.clip(D, -1, 1)  # 限制在有效范围
        
        q3 = np.arccos(D)
        q2 = np.arctan2(s, r) - np.arctan2(d4 * np.sin(q3), a2 + d4 * np.cos(q3))
        
        # 应用偏移
        q2 = q2 + np.radians(90)
        q3 = q3 - np.radians(90)
        
        # 求解后三个关节 (姿态) - 简化处理
        q4 = 0
        q5 = np.radians(90)
        q6 = 0
        
        return [np.degrees(q) for q in [q1, q2, q3, q4, q5, q6]]
    
    def test_forward_kinematics(self) -> Dict:
        """测试正向运动学"""
        print("🔧 测试正向运动学...")
        
        results = {}
        
        for case_name, angles in self.test_cases.items():
            print(f"  测试用例: {case_name}")
            
            try:
                # 计算正向运动学
                T = self.forward_kinematics(angles)
                pose = self.extract_pose(T)
                
                # 计算工作空间信息
                position = pose['position']
                reach = np.linalg.norm(position[:2])  # XY平面距离
                height = position[2]
                
                results[case_name] = {
                    'input_angles': angles,
                    'end_effector_pose': pose,
                    'reach': reach,
                    'height': height,
                    'transform_matrix': T.tolist(),
                    'status': 'success'
                }
                
                print(f"    ✅ 位置: [{position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f}] mm")
                print(f"    📏 臂展: {reach:.1f} mm, 高度: {height:.1f} mm")
                
            except Exception as e:
                results[case_name] = {
                    'input_angles': angles,
                    'error': str(e),
                    'status': 'failed'
                }
                print(f"    ❌ 失败: {e}")
        
        return results
    
    def test_inverse_kinematics(self) -> Dict:
        """测试逆向运动学"""
        print("\n🔄 测试逆向运动学...")
        
        results = {}
        
        for case_name, original_angles in self.test_cases.items():
            print(f"  测试用例: {case_name}")
            
            try:
                # 正向运动学得到目标位姿
                T_target = self.forward_kinematics(original_angles)
                
                # 逆向运动学求解
                solved_angles = self.inverse_kinematics_geometric(T_target)
                
                # 验证精度 - 再次正向运动学
                T_verify = self.forward_kinematics(solved_angles)
                
                # 计算误差
                position_error = np.linalg.norm(T_target[:3, 3] - T_verify[:3, 3])
                angle_error = np.linalg.norm(np.array(original_angles) - np.array(solved_angles))
                
                results[case_name] = {
                    'original_angles': original_angles,
                    'solved_angles': solved_angles,
                    'position_error': position_error,
                    'angle_error': angle_error,
                    'status': 'success' if position_error < 1.0 and angle_error < 5.0 else 'warning'
                }
                
                print(f"    📐 原始角度: {[f'{a:.1f}' for a in original_angles]}")
                print(f"    🎯 求解角度: {[f'{a:.1f}' for a in solved_angles]}")
                print(f"    📊 位置误差: {position_error:.3f} mm")
                print(f"    📊 角度误差: {angle_error:.3f} °")
                
            except Exception as e:
                results[case_name] = {
                    'original_angles': original_angles,
                    'error': str(e),
                    'status': 'failed'
                }
                print(f"    ❌ 失败: {e}")
        
        return results
    
    def test_workspace_analysis(self) -> Dict:
        """工作空间分析"""
        print("\n📐 工作空间分析...")
        
        # 生成测试点
        test_points = []
        
        # 边界测试
        for j1 in [-170, 0, 170]:
            for j2 in [-120, -60, 0, 60, 120]:
                for j3 in [-170, -90, 0, 90, 170]:
                    angles = [j1, j2, j3, 0, 90, 0]
                    test_points.append(angles)
        
        reachable_points = []
        max_reach = 0
        min_reach = float('inf')
        max_height = -float('inf')
        min_height = float('inf')
        
        print(f"  测试 {len(test_points)} 个工作空间点...")
        
        for angles in test_points:
            try:
                T = self.forward_kinematics(angles)
                position = T[:3, 3]
                
                reach = np.linalg.norm(position[:2])
                height = position[2]
                
                reachable_points.append({
                    'angles': angles,
                    'position': position.tolist(),
                    'reach': reach,
                    'height': height
                })
                
                max_reach = max(max_reach, reach)
                min_reach = min(min_reach, reach)
                max_height = max(max_height, height)
                min_height = min(min_height, height)
                
            except:
                continue
        
        workspace_analysis = {
            'total_test_points': len(test_points),
            'reachable_points': len(reachable_points),
            'reachability_ratio': len(reachable_points) / len(test_points),
            'max_reach': max_reach,
            'min_reach': min_reach,
            'max_height': max_height,
            'min_height': min_height,
            'workspace_volume_estimate': np.pi * max_reach**2 * (max_height - min_height) / 1e9  # 立方米
        }
        
        print(f"    ✅ 可达点: {len(reachable_points)}/{len(test_points)} ({workspace_analysis['reachability_ratio']*100:.1f}%)")
        print(f"    📏 最大臂展: {max_reach:.1f} mm")
        print(f"    📏 最小臂展: {min_reach:.1f} mm")
        print(f"    📏 最大高度: {max_height:.1f} mm")
        print(f"    📏 最小高度: {min_height:.1f} mm")
        print(f"    📦 工作空间体积估计: {workspace_analysis['workspace_volume_estimate']:.3f} 立方米")
        
        return workspace_analysis
    
    def check_singularities(self, joint_angles: List[float]) -> List[str]:
        """检查奇异性配置"""
        singularities = []
        threshold = 1.0  # 度
        
        # 肩部奇异性 (J1轴与末端重合)
        if abs(joint_angles[0]) < threshold:
            singularities.append("shoulder")
        
        # 肘部奇异性 (J3 = 0°或±180°)
        if abs(joint_angles[2]) < threshold:
            singularities.append("elbow_extended")
        elif abs(abs(joint_angles[2]) - 180) < threshold:
            singularities.append("elbow_folded")
        
        # 腕部奇异性 (J5 = 0°)
        if abs(joint_angles[4]) < threshold:
            singularities.append("wrist")
        
        return singularities
    
    def test_singularity_detection(self) -> Dict:
        """测试奇异性检测"""
        print("\n⚠️  奇异性检测测试...")
        
        # 已知奇异配置
        singular_configs = {
            'shoulder_singular': [0, -90, 90, 0, 90, 0],
            'elbow_extended': [90, -90, 0, 0, 90, 0],
            'elbow_folded': [90, -90, 180, 0, 90, 0],
            'wrist_singular': [90, -90, 90, 0, 0, 0]
        }
        
        results = {}
        
        for config_name, angles in singular_configs.items():
            singularities = self.check_singularities(angles)
            
            results[config_name] = {
                'angles': angles,
                'detected_singularities': singularities,
                'is_singular': len(singularities) > 0
            }
            
            status = "🔴" if singularities else "🟢"
            print(f"    {status} {config_name}: {singularities if singularities else '无奇异性'}")
        
        return results
    
    def generate_comprehensive_report(self) -> Dict:
        """生成综合分析报告"""
        print("📊 生成FR3机械臂DH参数综合分析报告...")
        print("=" * 60)
        
        # 执行所有测试
        forward_results = self.test_forward_kinematics()
        inverse_results = self.test_inverse_kinematics()
        workspace_results = self.test_workspace_analysis()
        singularity_results = self.test_singularity_detection()
        
        # 汇总结果
        report = {
            'timestamp': datetime.now().isoformat(),
            'dh_parameters': self.dh_params,
            'joint_limits': self.joint_limits,
            'test_results': {
                'forward_kinematics': forward_results,
                'inverse_kinematics': inverse_results,
                'workspace_analysis': workspace_results,
                'singularity_detection': singularity_results
            },
            'summary': {
                'forward_kinematics_success_rate': sum(1 for r in forward_results.values() if r['status'] == 'success') / len(forward_results),
                'inverse_kinematics_success_rate': sum(1 for r in inverse_results.values() if r['status'] == 'success') / len(inverse_results),
                'average_position_error': np.mean([r.get('position_error', 0) for r in inverse_results.values() if 'position_error' in r]),
                'average_angle_error': np.mean([r.get('angle_error', 0) for r in inverse_results.values() if 'angle_error' in r])
            }
        }
        
        return report
    
    def save_report(self, report: Dict, filename: str = None):
        """保存分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fr3_dh_analysis_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 分析报告已保存到: {filename}")
        
        # 打印摘要
        summary = report['summary']
        print("\n📋 分析摘要:")
        print("-" * 30)
        print(f"正向运动学成功率: {summary['forward_kinematics_success_rate']*100:.1f}%")
        print(f"逆向运动学成功率: {summary['inverse_kinematics_success_rate']*100:.1f}%")
        print(f"平均位置误差: {summary['average_position_error']:.3f} mm")
        print(f"平均角度误差: {summary['average_angle_error']:.3f} °")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FR3机械臂DH参数分析工具")
    parser.add_argument("--output", help="输出报告文件名")
    parser.add_argument("--test", choices=['forward', 'inverse', 'workspace', 'singularity', 'all'], 
                       default='all', help="指定测试类型")
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = DHParameterAnalyzer()
    
    # 执行指定测试
    if args.test == 'forward':
        results = analyzer.test_forward_kinematics()
    elif args.test == 'inverse':
        results = analyzer.test_inverse_kinematics()
    elif args.test == 'workspace':
        results = analyzer.test_workspace_analysis()
    elif args.test == 'singularity':
        results = analyzer.test_singularity_detection()
    else:  # all
        results = analyzer.generate_comprehensive_report()
        analyzer.save_report(results, args.output)

if __name__ == "__main__":
    main()
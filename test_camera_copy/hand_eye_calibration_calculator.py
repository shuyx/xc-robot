#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手眼标定计算工具
分析相机坐标系到机械臂坐标系的转换关系
"""

import numpy as np
import json
from datetime import datetime

class HandEyeCalibrator:
    def __init__(self):
        self.calibration_points = []
        self.transformation_matrix = None
        self.translation_vector = None
        self.rotation_matrix = None
        
    def add_calibration_point(self, camera_point, robot_point, description=""):
        """
        添加标定点
        camera_point: (x, y, z) 相机3D坐标 (毫米)
        robot_point: (X, Y, Z) 机械臂TCP坐标 (毫米)
        """
        point_data = {
            'camera_mm': list(camera_point),
            'robot_mm': list(robot_point),
            'description': description,
            'point_id': len(self.calibration_points) + 1
        }
        
        self.calibration_points.append(point_data)
        
        print(f"✅ 已添加标定点 {len(self.calibration_points)}: {description}")
        print(f"   相机坐标: ({camera_point[0]:.1f}, {camera_point[1]:.1f}, {camera_point[2]:.1f})mm")
        print(f"   机械臂坐标: ({robot_point[0]:.1f}, {robot_point[1]:.1f}, {robot_point[2]:.1f})mm")
        
        # 如果只有一个点，分析基本偏移
        if len(self.calibration_points) == 1:
            self.analyze_single_point()
        elif len(self.calibration_points) >= 3:
            print(f"\n📊 当前已有{len(self.calibration_points)}个点，可以尝试计算转换关系")
    
    def analyze_single_point(self):
        """分析单个点的特征"""
        point = self.calibration_points[0]
        camera = np.array(point['camera_mm'])
        robot = np.array(point['robot_mm'])
        
        # 计算简单的偏移向量
        offset = robot - camera
        
        print(f"\n📐 单点分析 (仅供参考):")
        print(f"   平移偏移: ({offset[0]:.1f}, {offset[1]:.1f}, {offset[2]:.1f})mm")
        print(f"   距离变化: 相机{np.linalg.norm(camera):.1f}mm → 机械臂{np.linalg.norm(robot):.1f}mm")
        
        # 分析各轴的关系
        print(f"\n🔍 各轴关系分析:")
        print(f"   X轴: 相机{camera[0]:.1f} → 机械臂{robot[0]:.1f} (差值{offset[0]:.1f})")
        print(f"   Y轴: 相机{camera[1]:.1f} → 机械臂{robot[1]:.1f} (差值{offset[1]:.1f})")
        print(f"   Z轴: 相机{camera[2]:.1f} → 机械臂{robot[2]:.1f} (差值{offset[2]:.1f})")
        
        print(f"\n⚠️ 注意:")
        print(f"   - 单点无法确定旋转关系")
        print(f"   - 需要至少3个不同位置的点")
        print(f"   - 建议收集4-6个点以提高精度")
    
    def calculate_transformation_least_squares(self):
        """使用最小二乘法计算转换关系"""
        if len(self.calibration_points) < 3:
            print("❌ 需要至少3个标定点")
            return False
        
        print(f"\n🧮 开始计算转换关系 (基于{len(self.calibration_points)}个点)...")
        
        # 提取坐标点
        camera_points = np.array([point['camera_mm'] for point in self.calibration_points])
        robot_points = np.array([point['robot_mm'] for point in self.calibration_points])
        
        # 计算中心点
        camera_center = np.mean(camera_points, axis=0)
        robot_center = np.mean(robot_points, axis=0)
        
        print(f"相机中心: ({camera_center[0]:.1f}, {camera_center[1]:.1f}, {camera_center[2]:.1f})mm")
        print(f"机械臂中心: ({robot_center[0]:.1f}, {robot_center[1]:.1f}, {robot_center[2]:.1f})mm")
        
        # 去中心化
        camera_centered = camera_points - camera_center
        robot_centered = robot_points - robot_center
        
        # 使用SVD计算旋转矩阵
        H = camera_centered.T @ robot_centered
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T
        
        # 确保是右手坐标系
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T
        
        # 计算平移向量
        t = robot_center - R @ camera_center
        
        # 构建4x4齐次变换矩阵
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        
        self.rotation_matrix = R
        self.translation_vector = t
        self.transformation_matrix = T
        
        # 显示结果
        self.display_transformation_results()
        
        # 验证精度
        self.validate_transformation()
        
        return True
    
    def calculate_simple_translation(self):
        """计算简化的平移变换（忽略旋转）"""
        if len(self.calibration_points) < 2:
            print("❌ 需要至少2个标定点")
            return False
        
        print(f"\n📐 计算简化平移变换 (基于{len(self.calibration_points)}个点)...")
        
        # 计算平均偏移
        offsets = []
        for point in self.calibration_points:
            camera = np.array(point['camera_mm'])
            robot = np.array(point['robot_mm'])
            offset = robot - camera
            offsets.append(offset)
        
        offsets = np.array(offsets)
        mean_offset = np.mean(offsets, axis=0)
        offset_std = np.std(offsets, axis=0)
        
        print(f"平均偏移: ({mean_offset[0]:.1f}, {mean_offset[1]:.1f}, {mean_offset[2]:.1f})mm")
        print(f"标准差: ({offset_std[0]:.1f}, {offset_std[1]:.1f}, {offset_std[2]:.1f})mm")
        print(f"最大误差: {np.max(offset_std):.1f}mm")
        
        # 构建简单平移矩阵
        T_simple = np.eye(4)
        T_simple[:3, 3] = mean_offset
        
        self.translation_vector = mean_offset
        self.transformation_matrix = T_simple
        
        # 验证精度
        print(f"\n🧪 验证简化变换精度:")
        errors = []
        for i, point in enumerate(self.calibration_points):
            camera = np.array(point['camera_mm'])
            robot_actual = np.array(point['robot_mm'])
            robot_predicted = camera + mean_offset
            
            error = np.linalg.norm(robot_actual - robot_predicted)
            errors.append(error)
            
            print(f"点{i+1}: 实际{robot_actual} vs 预测{robot_predicted}, 误差{error:.1f}mm")
        
        mean_error = np.mean(errors)
        max_error = np.max(errors)
        
        print(f"\n📊 精度统计:")
        print(f"平均误差: {mean_error:.1f}mm")
        print(f"最大误差: {max_error:.1f}mm")
        
        if max_error < 10:
            print("✅ 简化变换精度良好")
        elif max_error < 20:
            print("⚠️ 简化变换精度一般，建议增加标定点")
        else:
            print("❌ 简化变换精度较差，可能需要考虑旋转")
        
        return True
    
    def display_transformation_results(self):
        """显示转换结果"""
        print(f"\n📊 转换矩阵计算结果:")
        print(f"旋转矩阵 R:")
        for i in range(3):
            print(f"   [{self.rotation_matrix[i,0]:7.3f} {self.rotation_matrix[i,1]:7.3f} {self.rotation_matrix[i,2]:7.3f}]")
        
        print(f"\n平移向量 t:")
        print(f"   [{self.translation_vector[0]:7.1f} {self.translation_vector[1]:7.1f} {self.translation_vector[2]:7.1f}]mm")
        
        print(f"\n完整变换矩阵 T:")
        for i in range(4):
            print(f"   [{self.transformation_matrix[i,0]:7.3f} {self.transformation_matrix[i,1]:7.3f} {self.transformation_matrix[i,2]:7.3f} {self.transformation_matrix[i,3]:7.1f}]")
        
        # 分析旋转角度
        import math
        # 计算欧拉角 (ZYX顺序)
        sy = math.sqrt(self.rotation_matrix[0,0]**2 + self.rotation_matrix[1,0]**2)
        singular = sy < 1e-6
        
        if not singular:
            x = math.atan2(self.rotation_matrix[2,1], self.rotation_matrix[2,2])
            y = math.atan2(-self.rotation_matrix[2,0], sy)
            z = math.atan2(self.rotation_matrix[1,0], self.rotation_matrix[0,0])
        else:
            x = math.atan2(-self.rotation_matrix[1,2], self.rotation_matrix[1,1])
            y = math.atan2(-self.rotation_matrix[2,0], sy)
            z = 0
        
        print(f"\n🔄 旋转角度 (欧拉角):")
        print(f"   绕X轴: {math.degrees(x):6.1f}°")
        print(f"   绕Y轴: {math.degrees(y):6.1f}°")
        print(f"   绕Z轴: {math.degrees(z):6.1f}°")
    
    def validate_transformation(self):
        """验证转换精度"""
        print(f"\n🧪 验证转换精度:")
        
        errors = []
        for i, point in enumerate(self.calibration_points):
            # 相机坐标转换为齐次坐标
            camera_homo = np.append(point['camera_mm'], 1)
            
            # 应用变换
            robot_predicted_homo = self.transformation_matrix @ camera_homo
            robot_predicted = robot_predicted_homo[:3]
            
            # 实际机械臂坐标
            robot_actual = np.array(point['robot_mm'])
            
            # 计算误差
            error = np.linalg.norm(robot_actual - robot_predicted)
            errors.append(error)
            
            print(f"点{i+1} {point['description'][:8]}:")
            print(f"   实际: ({robot_actual[0]:6.1f}, {robot_actual[1]:6.1f}, {robot_actual[2]:6.1f})mm")
            print(f"   预测: ({robot_predicted[0]:6.1f}, {robot_predicted[1]:6.1f}, {robot_predicted[2]:6.1f})mm")
            print(f"   误差: {error:.1f}mm")
        
        mean_error = np.mean(errors)
        max_error = np.max(errors)
        
        print(f"\n📊 精度统计:")
        print(f"平均误差: {mean_error:.1f}mm")
        print(f"最大误差: {max_error:.1f}mm")
        
        if max_error < 5:
            print("✅ 转换精度优秀 (<5mm)")
        elif max_error < 10:
            print("✅ 转换精度良好 (<10mm)")
        elif max_error < 20:
            print("⚠️ 转换精度一般 (<20mm)")
        else:
            print("❌ 转换精度较差 (>20mm)")
    
    def transform_camera_to_robot(self, camera_point):
        """将相机坐标转换为机械臂坐标"""
        if self.transformation_matrix is None:
            print("❌ 请先计算转换矩阵")
            return None
        
        # 转换为齐次坐标
        camera_homo = np.append(camera_point, 1)
        
        # 应用变换
        robot_homo = self.transformation_matrix @ camera_homo
        robot_point = robot_homo[:3]
        
        return robot_point
    
    def save_calibration(self, filename="hand_eye_calibration.json"):
        """保存标定结果"""
        data = {
            'calibration_points': self.calibration_points,
            'transformation_matrix': self.transformation_matrix.tolist() if self.transformation_matrix is not None else None,
            'rotation_matrix': self.rotation_matrix.tolist() if self.rotation_matrix is not None else None,
            'translation_vector': self.translation_vector.tolist() if self.translation_vector is not None else None,
            'save_time': datetime.now().isoformat(),
            'num_points': len(self.calibration_points)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 标定结果已保存到: {filename}")
    
    def show_calibration_points(self):
        """显示所有标定点"""
        if not self.calibration_points:
            print("📋 暂无标定数据")
            return
        
        print(f"\n📋 标定点汇总 ({len(self.calibration_points)}个点):")
        print("-" * 90)
        print(f"{'ID':<3} {'描述':<10} {'相机坐标(mm)':<25} {'机械臂坐标(mm)':<25} {'距离(mm)':<10}")
        print("-" * 90)
        
        for point in self.calibration_points:
            camera = point['camera_mm']
            robot = point['robot_mm']
            distance = np.linalg.norm(np.array(robot) - np.array(camera))
            
            camera_str = f"({camera[0]:5.1f},{camera[1]:5.1f},{camera[2]:5.1f})"
            robot_str = f"({robot[0]:6.1f},{robot[1]:5.1f},{robot[2]:6.1f})"
            
            print(f"{point['point_id']:<3} {point['description'][:9]:<10} {camera_str:<25} {robot_str:<25} {distance:8.1f}")

def demo_with_your_data():
    """使用您提供的数据进行演示"""
    print("🎯 手眼标定演示 - 使用您的数据")
    print("=" * 50)
    
    calibrator = HandEyeCalibrator()
    
    # 添加您的数据点
    calibrator.add_calibration_point(
        camera_point=(58.8, 48.9, 247.0),
        robot_point=(-290.9, 32.3, -393.5),
        description="测试点1"
    )
    
    print(f"\n💡 建议收集更多数据点:")
    print(f"   - 至少需要3个点计算完整转换矩阵")
    print(f"   - 建议4-6个点提高精度")
    print(f"   - 点应该分布在工作空间的不同位置")
    
    return calibrator

if __name__ == "__main__":
    demo_with_your_data()
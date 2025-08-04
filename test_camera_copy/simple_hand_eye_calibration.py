#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版手眼标定工具
假设相机和机械臂坐标系方向一致，只需标定平移偏移
"""

import numpy as np
import json
import os
from datetime import datetime

class SimpleHandEyeCalibration:
    def __init__(self):
        self.calibration_data = []
        self.translation_offset = None
        self.calibration_file = "hand_eye_calibration.json"
        
    def add_calibration_point(self, camera_point, robot_point, description=""):
        """
        添加标定点对
        camera_point: (x, y, z) 相机检测的3D坐标 (米)
        robot_point: (X, Y, Z) 机械臂实际TCP坐标 (毫米)
        """
        # 将机械臂坐标转换为米
        robot_point_m = [p/1000.0 for p in robot_point]
        
        calibration_pair = {
            'camera': list(camera_point),
            'robot': robot_point_m,
            'robot_mm': list(robot_point),
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        
        self.calibration_data.append(calibration_pair)
        print(f"✅ 添加标定点 {len(self.calibration_data)}: {description}")
        print(f"   相机: ({camera_point[0]:.3f}, {camera_point[1]:.3f}, {camera_point[2]:.3f})m")
        print(f"   机械臂: ({robot_point[0]:.1f}, {robot_point[1]:.1f}, {robot_point[2]:.1f})mm")
        
    def calculate_translation_offset(self):
        """计算简化的平移偏移"""
        if len(self.calibration_data) < 3:
            print("❌ 需要至少3个标定点")
            return False
        
        # 提取相机和机械臂坐标
        camera_points = np.array([item['camera'] for item in self.calibration_data])
        robot_points = np.array([item['robot'] for item in self.calibration_data])
        
        # 计算平均偏移 (简化方法)
        offsets = robot_points - camera_points
        self.translation_offset = np.mean(offsets, axis=0)
        
        # 计算偏移的标准差（评估精度）
        offset_std = np.std(offsets, axis=0)
        
        print(f"\n📊 标定结果 (基于{len(self.calibration_data)}个点):")
        print(f"平移偏移: ({self.translation_offset[0]:.3f}, {self.translation_offset[1]:.3f}, {self.translation_offset[2]:.3f})m")
        print(f"标准差: ({offset_std[0]:.3f}, {offset_std[1]:.3f}, {offset_std[2]:.3f})m")
        print(f"最大误差: {np.max(offset_std):.3f}m")
        
        if np.max(offset_std) > 0.02:  # 2cm
            print("⚠️ 标定精度较低，建议增加更多标定点")
        else:
            print("✅ 标定精度良好")
        
        return True
    
    def camera_to_robot(self, camera_point):
        """相机坐标转机械臂坐标"""
        if self.translation_offset is None:
            print("❌ 请先进行标定")
            return None
        
        # 简单平移变换
        robot_point = np.array(camera_point) + self.translation_offset
        return robot_point
    
    def save_calibration(self):
        """保存标定结果"""
        calibration_result = {
            'calibration_data': self.calibration_data,
            'translation_offset': self.translation_offset.tolist() if self.translation_offset is not None else None,
            'calibration_date': datetime.now().isoformat(),
            'num_points': len(self.calibration_data)
        }
        
        with open(self.calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 标定结果已保存到: {self.calibration_file}")
    
    def load_calibration(self):
        """加载已有标定结果"""
        if not os.path.exists(self.calibration_file):
            print(f"⚠️ 标定文件不存在: {self.calibration_file}")
            return False
        
        try:
            with open(self.calibration_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.calibration_data = data['calibration_data']
            if data['translation_offset']:
                self.translation_offset = np.array(data['translation_offset'])
            
            print(f"✅ 已加载标定数据: {len(self.calibration_data)}个点")
            if self.translation_offset is not None:
                print(f"平移偏移: ({self.translation_offset[0]:.3f}, {self.translation_offset[1]:.3f}, {self.translation_offset[2]:.3f})m")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载标定文件失败: {e}")
            return False
    
    def show_calibration_data(self):
        """显示所有标定数据"""
        if not self.calibration_data:
            print("📋 暂无标定数据")
            return
        
        print(f"\n📋 标定数据汇总 ({len(self.calibration_data)}个点):")
        print("-" * 80)
        print(f"{'序号':<4} {'描述':<15} {'相机坐标(m)':<25} {'机械臂坐标(mm)':<25}")
        print("-" * 80)
        
        for i, item in enumerate(self.calibration_data, 1):
            camera_str = f"({item['camera'][0]:.3f},{item['camera'][1]:.3f},{item['camera'][2]:.3f})"
            robot_str = f"({item['robot_mm'][0]:.1f},{item['robot_mm'][1]:.1f},{item['robot_mm'][2]:.1f})"
            print(f"{i:<4} {item['description'][:14]:<15} {camera_str:<25} {robot_str:<25}")

def demo_calibration():
    """标定演示"""
    print("🎯 简化版手眼标定演示")
    print("=" * 50)
    
    calibrator = SimpleHandEyeCalibration()
    
    # 演示数据 (您需要替换为实际测量数据)
    print("📝 添加标定点 (这些是示例数据，请替换为实际测量值):")
    
    # 示例标定点
    calibrator.add_calibration_point(
        camera_point=(0.0, 0.0, 0.5),      # 相机检测: 正前方50cm
        robot_point=(400, 200, 300),        # 机械臂实际位置 (mm)
        description="中心点"
    )
    
    calibrator.add_calibration_point(
        camera_point=(0.1, 0.0, 0.6),      # 相机检测: 右侧10cm, 前方60cm  
        robot_point=(500, 200, 400),        # 机械臂实际位置 (mm)
        description="右侧点"
    )
    
    calibrator.add_calibration_point(
        camera_point=(-0.1, 0.05, 0.55),   # 相机检测: 左侧10cm, 下方5cm, 前方55cm
        robot_point=(300, 250, 350),        # 机械臂实际位置 (mm)  
        description="左下点"
    )
    
    # 计算标定
    if calibrator.calculate_translation_offset():
        # 显示标定数据
        calibrator.show_calibration_data()
        
        # 保存标定结果
        calibrator.save_calibration()
        
        # 测试转换
        print(f"\n🧪 坐标转换测试:")
        test_camera_point = (0.05, -0.02, 0.58)
        robot_result = calibrator.camera_to_robot(test_camera_point)
        if robot_result is not None:
            print(f"相机坐标: ({test_camera_point[0]:.3f}, {test_camera_point[1]:.3f}, {test_camera_point[2]:.3f})m")
            print(f"机械臂坐标: ({robot_result[0]:.3f}, {robot_result[1]:.3f}, {robot_result[2]:.3f})m")
            print(f"机械臂坐标: ({robot_result[0]*1000:.1f}, {robot_result[1]*1000:.1f}, {robot_result[2]*1000:.1f})mm")

if __name__ == "__main__":
    demo_calibration()
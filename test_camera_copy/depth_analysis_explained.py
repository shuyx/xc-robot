#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度分析原理详解
用最通俗的方式解释深度检测的工作原理
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import matplotlib.pyplot as plt

class DepthAnalysisExplainer:
    """深度分析原理解释器"""
    
    def __init__(self):
        self.pipeline = None
        self.setup_camera()
    
    def setup_camera(self):
        """设置相机"""
        self.pipeline = Pipeline()
        config = Config()
        
        depth_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        config.enable_stream(depth_profile)
        
        self.pipeline.start(config)
    
    def get_depth_image(self):
        """获取深度图像"""
        frames = self.pipeline.wait_for_frames(1000)
        if not frames:
            return None
        
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            return None
        
        depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
        depth_image = depth_data.reshape((depth_frame.get_height(), depth_frame.get_width()))
        
        return depth_image, depth_frame
    
    def explain_step_by_step(self):
        """一步步解释深度分析过程"""
        
        print("=" * 60)
        print("深度分析原理 - 一步步详解")
        print("=" * 60)
        
        # 稳定几帧
        for _ in range(5):
            self.pipeline.wait_for_frames(100)
        
        # 获取深度图像
        depth_image, depth_frame = self.get_depth_image()
        if depth_image is None:
            print("❌ 无法获取深度图像")
            return
        
        print(f"📊 获取深度图像: {depth_image.shape[1]}x{depth_image.shape[0]} 像素")
        
        # 步骤1: 分析整体深度分布
        print("\n=== 步骤1: 分析场景的深度分布 ===")
        valid_depth = depth_image[depth_image > 0]  # 过滤无效深度
        
        if len(valid_depth) == 0:
            print("❌ 无有效深度数据")
            return
        
        min_depth = np.min(valid_depth)
        max_depth = np.max(valid_depth)
        mean_depth = np.mean(valid_depth)
        
        print(f"深度范围: {min_depth}mm - {max_depth}mm")
        print(f"平均深度: {mean_depth:.0f}mm")
        print(f"有效像素: {len(valid_depth)}/{depth_image.size} ({len(valid_depth)/depth_image.size*100:.1f}%)")
        
        # 步骤2: 找桌面深度
        print("\n=== 步骤2: 找桌面(背景)的深度 ===")
        
        # 方法: 找最常见的深度值(桌面占大部分像素)
        hist, bins = np.histogram(valid_depth, bins=50)
        most_common_depth_index = np.argmax(hist)
        table_depth = bins[most_common_depth_index]
        table_pixel_count = hist[most_common_depth_index]
        
        print(f"最常见深度: {table_depth:.0f}mm ({table_pixel_count}个像素)")
        print(f"推测桌面深度: {table_depth:.0f}mm")
        print(f"解释: 大部分像素都是这个深度，应该是桌面")
        
        # 步骤3: 找物体(比桌面更近的区域)
        print("\n=== 步骤3: 找桌面上的物体 ===")
        
        # 找比桌面近的像素(物体比桌面高，所以距离相机更近)
        object_threshold = table_depth - 30  # 比桌面近3cm以上的认为是物体
        object_mask = (depth_image > 100) & (depth_image < object_threshold)
        
        object_pixels = np.sum(object_mask)
        print(f"物体阈值: 小于 {object_threshold:.0f}mm 的像素")
        print(f"检测到物体像素: {object_pixels} 个")
        
        if object_pixels < 50:
            print("⚠️ 物体像素太少，可能没有物体或物体太小")
            return
        
        # 步骤4: 找物体的最高点
        print("\n=== 步骤4: 找物体的最高点(离相机最近) ===")
        
        object_depths = depth_image[object_mask]
        min_object_depth = np.min(object_depths)
        
        # 找最高点的像素位置
        highest_point_mask = depth_image == min_object_depth
        positions = np.where(highest_point_mask)
        
        if len(positions[0]) == 0:
            print("❌ 找不到最高点")
            return
        
        # 取最高点区域的中心
        center_y = int(np.mean(positions[0]))
        center_x = int(np.mean(positions[1]))
        
        print(f"物体最近深度: {min_object_depth}mm")
        print(f"最高点位置: 像素({center_x}, {center_y})")
        print(f"物体高度: {table_depth - min_object_depth:.0f}mm")
        
        # 步骤5: 转换为3D坐标
        print("\n=== 步骤5: 转换为真实3D坐标 ===")
        
        intrinsics = depth_frame.get_camera_intrinsics()
        
        z = min_object_depth / 1000.0  # 转换为米
        x = (center_x - intrinsics.ppx) * z / intrinsics.fx
        y = (center_y - intrinsics.ppy) * z / intrinsics.fy
        
        print(f"相机内参:")
        print(f"  焦距: fx={intrinsics.fx:.1f}, fy={intrinsics.fy:.1f}")
        print(f"  主点: cx={intrinsics.ppx:.1f}, cy={intrinsics.ppy:.1f}")
        
        print(f"3D坐标转换:")
        print(f"  z = {min_object_depth}mm = {z:.3f}m (深度)")
        print(f"  x = ({center_x} - {intrinsics.ppx:.0f}) * {z:.3f} / {intrinsics.fx:.0f} = {x:.3f}m")
        print(f"  y = ({center_y} - {intrinsics.ppy:.0f}) * {z:.3f} / {intrinsics.fy:.0f} = {y:.3f}m")
        
        print(f"\n🎯 最终结果:")
        print(f"物体位置: ({x:.3f}, {y:.3f}, {z:.3f}) 米")
        print(f"物理含义: 距离相机前{z:.3f}m，右侧{x:.3f}m，下方{y:.3f}m")
        
        # 步骤6: 验证结果合理性
        print("\n=== 步骤6: 验证结果合理性 ===")
        
        # 检查物体尺寸
        object_area = np.sum(object_mask)
        estimated_radius = np.sqrt(object_area / np.pi)  # 假设圆形
        real_radius = estimated_radius * z / intrinsics.fx  # 像素转实际尺寸
        
        print(f"物体像素面积: {object_area} 像素")
        print(f"估计半径: {real_radius*1000:.1f}mm")
        
        if 20 < real_radius*1000 < 60:  # 纸杯半径大约30-50mm
            print("✅ 尺寸合理，可能是纸杯")
        else:
            print("⚠️ 尺寸不太像纸杯，可能是其他物体")
        
        return (x, y, z)
    
    def visual_explanation(self):
        """可视化解释"""
        print("\n=== 可视化深度分析过程 ===")
        
        depth_image, _ = self.get_depth_image()
        if depth_image is None:
            return
        
        # 创建深度可视化图
        valid_depth = depth_image[depth_image > 0]
        if len(valid_depth) == 0:
            return
        
        # 找桌面深度
        hist, bins = np.histogram(valid_depth, bins=50)
        table_depth = bins[np.argmax(hist)]
        
        # 创建不同深度的掩膜
        background_mask = np.abs(depth_image - table_depth) < 50  # 桌面±5cm
        object_mask = (depth_image > 0) & (depth_image < table_depth - 30)  # 物体
        
        print("深度图像分析:")
        print(f"🟫 褐色区域: 桌面 (深度 ≈ {table_depth:.0f}mm)")
        print(f"🔴 红色区域: 物体 (深度 < {table_depth-30:.0f}mm)")
        print(f"⚫ 黑色区域: 无效深度或更远的背景")
        
        # 统计各区域
        background_pixels = np.sum(background_mask)
        object_pixels = np.sum(object_mask)
        total_pixels = depth_image.size
        
        print(f"\n像素统计:")
        print(f"桌面像素: {background_pixels} ({background_pixels/total_pixels*100:.1f}%)")
        print(f"物体像素: {object_pixels} ({object_pixels/total_pixels*100:.1f}%)")
        
        if object_pixels > 100:
            print("✅ 检测到足够大的物体区域")
        else:
            print("⚠️ 物体区域太小，检测可能不准确")
    
    def run_explanation(self):
        """运行完整解释"""
        try:
            print("深度分析是怎么工作的？")
            print("让我们一步步看看相机是如何'理解'3D场景的...")
            
            input("按回车开始...")
            
            result = self.explain_step_by_step()
            self.visual_explanation()
            
            if result:
                print(f"\n🎉 成功检测到物体!")
                print("这就是深度分析的完整过程!")
            
        except Exception as e:
            print(f"解释过程出错: {e}")
        
        finally:
            if self.pipeline:
                self.pipeline.stop()

def simple_concept_explanation():
    """用最简单的话解释概念"""
    print("=" * 50)
    print("深度分析 - 最简单的解释")
    print("=" * 50)
    
    print("🤔 你的理解完全正确！深度分析就是:")
    print()
    print("1. 📏 相机告诉我们每个像素的距离")
    print("   比如: 这个像素距离80cm，那个像素距离75cm")
    print()
    print("2. 🍽️ 找到桌面的距离(大部分像素都是这个距离)")
    print("   比如: 大部分像素都是80cm，所以桌面在80cm")
    print()
    print("3. 📦 找桌面上的物体(比桌面更近的像素)")
    print("   比如: 有些像素是75cm，比桌面近5cm，这是物体！")
    print()
    print("4. 🎯 找物体的最高点(最近的像素)")
    print("   比如: 物体中最近的是74cm，这是纸杯的顶端")
    print()
    print("5. 🌍 转换为真实坐标")
    print("   像素位置(320,240) + 深度74cm = 3D坐标(x,y,z)")
    print()
    print("就这么简单！不需要AI，不需要训练，就是数学计算！")

def main():
    """主函数"""
    print("选择解释方式:")
    print("1. 概念解释 (最简单)")
    print("2. 实际演示 (需要相机)")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == "1":
        simple_concept_explanation()
    elif choice == "2":
        explainer = DepthAnalysisExplainer()
        explainer.run_explanation()
    else:
        print("请选择 1 或 2")

if __name__ == "__main__":
    main()
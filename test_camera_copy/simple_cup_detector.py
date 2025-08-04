#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版水杯检测脚本
专为快速测试设计，代码简洁易理解
"""

import numpy as np
from pyorbbecsdk import *
import time

def setup_camera():
    """设置相机"""
    pipeline = Pipeline()
    config = Config()
    
    # 配置深度流
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    config.enable_stream(depth_profile)
    
    # 启动相机
    pipeline.start(config)
    
    # 获取内参
    try:
        depth_video_profile = depth_profile.as_video_stream_profile()
        intrinsics = depth_video_profile.get_intrinsics()
        print(f"相机内参: fx={intrinsics.fx:.1f}, fy={intrinsics.fy:.1f}")
    except:
        # 使用估算值
        intrinsics = type('obj', (object,), {
            'fx': 500.0, 'fy': 500.0, 
            'ppx': 320.0, 'ppy': 240.0
        })()
        print("使用估算内参")
    
    return pipeline, intrinsics

def get_depth_image(pipeline):
    """获取深度图像"""
    frames = pipeline.wait_for_frames(1000)
    depth_frame = frames.get_depth_frame()
    
    if not depth_frame:
        return None
    
    # 转换为numpy数组
    depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
    height = depth_frame.get_height()
    width = depth_frame.get_width()
    depth_image = depth_data.reshape((height, width))
    
    return depth_image

def find_cup(depth_image, intrinsics):
    """找水杯的3D坐标，添加区域限制避免检测到桌子"""
    height, width = depth_image.shape
    
    # 1. 创建Y坐标限制掩码 - 排除画面下方25%的区域（避免桌子）
    y_detection_ratio = 0.75  # 只检测上75%的区域
    y_limit_pixel = int(height * y_detection_ratio)
    
    # 创建区域掩码
    detection_mask = np.zeros_like(depth_image, dtype=bool)
    detection_mask[:y_limit_pixel, :] = True  # 只在上75%区域检测
    
    print(f"检测区域限制: 上方{y_detection_ratio*100:.0f}%区域 (像素Y < {y_limit_pixel})")
    
    # 2. 在限制区域内过滤有效深度 (20cm-3m)
    valid_mask = (depth_image > 200) & (depth_image < 3000) & detection_mask
    valid_depth = depth_image[valid_mask]
    
    if len(valid_depth) < 100:
        print("限制区域内深度数据太少")
        return None
    
    # 3. 在限制区域内找最近物体
    closest_depth = np.min(valid_depth)
    print(f"区域限制后最近深度: {closest_depth}mm")
    
    # 4. 找到最近点的位置
    closest_positions = np.where((depth_image == closest_depth) & detection_mask)
    
    if len(closest_positions[0]) == 0:
        print("未找到最近点位置")
        return None
    
    # 5. 取第一个最近点作为检测点
    center_y = closest_positions[0][0]
    center_x = closest_positions[1][0]
    center_depth = closest_depth
    
    print(f"最近点位置: ({center_x}, {center_y})")
    
    # 6. 转换3D坐标
    z = center_depth / 1000.0  # 转米
    x = (center_x - intrinsics.ppx) * z / intrinsics.fx
    y = (center_y - intrinsics.ppy) * z / intrinsics.fy
    
    print(f"3D坐标计算: x={x:.3f}, y={y:.3f}, z={z:.3f}")
    
    # 7. 距离合理性检查
    if z < 0.1 or z > 2.0:
        print(f"Z距离不合理: {z:.3f}m")
        return None
    
    return {
        'pixel': (center_x, center_y),
        'depth_mm': center_depth,
        'position_3d': (x, y, z)
    }

def main():
    """主函数"""
    print("=== 简化版水杯检测 ===")
    
    try:
        # 设置相机
        print("初始化相机...")
        pipeline, intrinsics = setup_camera()
        
        # 预热
        print("相机预热...")
        for _ in range(5):
            pipeline.wait_for_frames(100)
        
        print("开始检测最近点距离...")
        print("✨ 功能: 只检测画面上75%区域，直接读取最近点距离")
        print("无需水杯大小判断，直接获取最近距离")
        print()
        
        for i in range(10):  # 检测10次
            print(f"--- 第{i+1}次检测 ---")
            
            # 获取深度图像
            depth_image = get_depth_image(pipeline)
            if depth_image is None:
                print("❌ 未获取到深度图像")
                continue
            
            # 检测最近点
            result = find_cup(depth_image, intrinsics)
            
            if result:
                x, y, z = result['position_3d']
                print(f"✅ 检测成功!")
                print(f"   像素位置: {result['pixel']}")
                print(f"   深度: {result['depth_mm']}mm")
                print(f"   3D坐标: ({x:.3f}, {y:.3f}, {z:.3f})m")
                print(f"   距离: 前方{z:.3f}m ({z*1000:.0f}mm)")
            else:
                print("❌ 未检测到最近点")
            
            time.sleep(1)
            print()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'pipeline' in locals():
            pipeline.stop()
        print("程序结束")

if __name__ == "__main__":
    main()
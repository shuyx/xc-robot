#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纸杯检测简化测试脚本
用于验证基础的3D坐标获取功能
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time

def simple_cup_detection():
    """简化的纸杯检测和3D定位"""
    
    print("=== 初始化相机 ===")
    
    # 初始化
    pipeline = Pipeline()
    config = Config()
    
    # 配置深度流
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    config.enable_stream(depth_profile)
    
    # 尝试启用彩色流
    try:
        color_profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if color_profile_list:
            color_profile = color_profile_list.get_default_video_stream_profile()
            config.enable_stream(color_profile)
            has_color = True
        else:
            has_color = False
    except:
        has_color = False
    
    print(f"彩色传感器: {'✅ 可用' if has_color else '❌ 不可用'}")
    
    # 启动Pipeline
    pipeline.start(config)
    
    try:
        print("\n=== 开始检测 ===")
        
        # 稳定几帧
        for _ in range(5):
            pipeline.wait_for_frames(100)
        
        # 获取相机内参
        frames = pipeline.wait_for_frames(1000)
        depth_frame = frames.get_depth_frame()
        depth_intrinsics = depth_frame.get_camera_intrinsics()
        
        print(f"相机内参:")
        print(f"  焦距: fx={depth_intrinsics.fx:.1f}, fy={depth_intrinsics.fy:.1f}")
        print(f"  主点: cx={depth_intrinsics.ppx:.1f}, cy={depth_intrinsics.ppy:.1f}")
        
        # 开始检测循环
        for i in range(5):
            print(f"\n--- 检测 {i+1}/5 ---")
            
            frames = pipeline.wait_for_frames(1000)
            if not frames:
                print("⚠️ 未获取到帧")
                continue
            
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                print("⚠️ 未获取到深度帧")
                continue
            
            # 获取深度图像
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_image = depth_data.reshape((depth_frame.get_height(), depth_frame.get_width()))
            
            # 简单的物体检测：找到距离相机最近的点
            valid_depth = depth_image[depth_image > 0]
            if len(valid_depth) == 0:
                print("⚠️ 无有效深度数据")
                continue
            
            # 过滤太近和太远的点
            valid_depth = valid_depth[(valid_depth > 200) & (valid_depth < 2000)]  # 20cm到2m
            
            if len(valid_depth) == 0:
                print("⚠️ 无合理范围内的深度数据")
                continue
            
            # 找最近的点
            min_depth = np.min(valid_depth)
            positions = np.where(depth_image == min_depth)
            
            if len(positions[0]) == 0:
                print("⚠️ 未找到目标点")
                continue
            
            # 取第一个匹配点
            pixel_y, pixel_x = positions[0][0], positions[1][0]
            
            # 转换为3D坐标
            z = min_depth / 1000.0  # 转换为米
            x = (pixel_x - depth_intrinsics.ppx) * z / depth_intrinsics.fx
            y = (pixel_y - depth_intrinsics.ppy) * z / depth_intrinsics.fy
            
            print(f"🎯 检测结果:")
            print(f"   像素位置: ({pixel_x}, {pixel_y})")
            print(f"   深度: {min_depth} mm")
            print(f"   3D坐标 (相机系): ({x:.3f}, {y:.3f}, {z:.3f}) m")
            
            # 解释坐标系
            print(f"   解释: 物体在相机前方 {z:.3f}m，右侧 {x:.3f}m，下方 {y:.3f}m")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n检测已停止")
    
    finally:
        pipeline.stop()
        print("✅ 相机已关闭")

def depth_analysis():
    """深度数据分析 - 了解场景"""
    
    print("=== 深度数据分析 ===")
    
    pipeline = Pipeline()
    config = Config()
    
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    config.enable_stream(depth_profile)
    
    pipeline.start(config)
    
    try:
        # 稳定几帧
        for _ in range(5):
            pipeline.wait_for_frames(100)
        
        frames = pipeline.wait_for_frames(1000)
        depth_frame = frames.get_depth_frame()
        
        if depth_frame:
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_image = depth_data.reshape((depth_frame.get_height(), depth_frame.get_width()))
            
            valid_depth = depth_image[depth_image > 0]
            
            if len(valid_depth) > 0:
                print(f"深度统计:")
                print(f"  有效像素数: {len(valid_depth)}")
                print(f"  最小深度: {np.min(valid_depth)} mm")
                print(f"  最大深度: {np.max(valid_depth)} mm")
                print(f"  平均深度: {np.mean(valid_depth):.1f} mm")
                print(f"  深度中位数: {np.median(valid_depth):.1f} mm")
                
                # 深度分布
                print(f"\n深度分布:")
                ranges = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 5000)]
                for min_d, max_d in ranges:
                    count = np.sum((valid_depth >= min_d) & (valid_depth < max_d))
                    print(f"  {min_d}-{max_d}mm: {count} 像素")
    
    finally:
        pipeline.stop()

def main():
    """主函数"""
    print("纸杯检测测试程序")
    print("1. 深度数据分析")
    print("2. 简单物体检测")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == "1":
        depth_analysis()
    elif choice == "2":
        simple_cup_detection()
    else:
        print("请选择 1 或 2")

if __name__ == "__main__":
    main()
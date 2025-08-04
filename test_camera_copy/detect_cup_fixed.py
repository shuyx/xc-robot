#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版水杯检测脚本
使用正确的API获取相机内参
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time

def detect_cup_by_depth():
    """使用深度分析检测水杯"""
    
    print("=== 实时水杯检测（修正版）===")
    print("确保:")
    print("- 水杯是画面中离相机最近的物体")
    print("- 相机已经对准水杯")
    print("- 按 Ctrl+C 停止检测")
    
    # 初始化相机
    pipeline = Pipeline()
    config = Config()
    
    # 配置深度流
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    if depth_profile_list is None:
        print("❌ 无法获取深度传感器")
        return
    
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    if depth_profile is None:
        print("❌ 无法获取默认深度配置")
        return
    
    config.enable_stream(depth_profile)
    print(f"✅ 深度流配置: {depth_profile}")
    
    # 尝试配置彩色流
    has_color = False
    try:
        color_profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if color_profile_list:
            color_profile = color_profile_list.get_default_video_stream_profile()
            if color_profile:
                config.enable_stream(color_profile)
                has_color = True
                print(f"✅ 彩色流配置: {color_profile}")
    except:
        print("⚠️ 彩色传感器不可用，仅使用深度数据")
    
    # 启动相机
    pipeline.start(config)
    
    try:
        # 稳定几帧
        print("相机预热中...")
        for _ in range(10):
            pipeline.wait_for_frames(100)
        
        # 获取相机内参 - 正确的方法
        print("获取相机内参...")
        
        # 方法1: 通过depth_profile获取内参
        try:
            # 将depth_profile转换为video_stream_profile
            depth_video_profile = depth_profile.as_video_stream_profile()
            intrinsics = depth_video_profile.get_intrinsics()
            
            print(f"✅ 相机内参获取成功:")
            print(f"   焦距: fx={intrinsics.fx:.1f}, fy={intrinsics.fy:.1f}")
            print(f"   主点: cx={intrinsics.ppx:.1f}, cy={intrinsics.ppy:.1f}")
            print(f"   分辨率: {intrinsics.width}x{intrinsics.height}")
            
        except Exception as e:
            print(f"⚠️ 无法获取内参: {e}")
            print("将使用估算的内参")
            # 使用估算值
            intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0,
                'width': 640, 'height': 480
            })()
        
        print("\n开始检测...")
        detection_count = 0
        
        while True:
            detection_count += 1
            print(f"\n--- 第 {detection_count} 次检测 ---")
            
            # 获取帧数据
            frames = pipeline.wait_for_frames(1000)
            if not frames:
                print("⚠️ 未获取到帧")
                continue
            
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                print("⚠️ 未获取到深度帧")  
                continue
            
            # 转换深度数据
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            depth_image = depth_data.reshape((height, width))
            
            print(f"深度图像尺寸: {width}x{height}")
            
            # 分析深度数据
            result = analyze_depth_for_cup(depth_image, intrinsics)
            
            if result:
                pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                
                print(f"🎯 检测到水杯!")
                print(f"   像素坐标: ({pixel_x}, {pixel_y})")
                print(f"   深度值: {depth_mm} mm")
                print(f"   3D坐标: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f}) m")
                print(f"   位置描述: 前方{z_3d:.3f}m, 右侧{x_3d:.3f}m, 下方{y_3d:.3f}m")
                
                # 如果有彩色图像，也显示颜色信息
                if has_color:
                    color_frame = frames.get_color_frame()
                    if color_frame:
                        color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
                        color_height = color_frame.get_height()
                        color_width = color_frame.get_width()
                        color_image = color_data.reshape((color_height, color_width, 3))
                        
                        # 获取该点的颜色 (需要考虑分辨率差异)
                        color_x = int(pixel_x * color_width / width)
                        color_y = int(pixel_y * color_height / height)
                        
                        if 0 <= color_y < color_height and 0 <= color_x < color_width:
                            pixel_color = color_image[color_y, color_x]
                            print(f"   像素颜色: RGB({pixel_color[0]}, {pixel_color[1]}, {pixel_color[2]})")
            else:
                print("❌ 未检测到水杯")
            
            time.sleep(1)  # 1秒检测一次
    
    except KeyboardInterrupt:
        print(f"\n检测停止，共进行了 {detection_count} 次检测")
    
    except Exception as e:
        print(f"❌ 检测过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pipeline.stop()
        print("✅ 相机已关闭")

def analyze_depth_for_cup(depth_image, intrinsics):
    """
    分析深度图像找水杯
    返回: (pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d) 或 None
    """
    
    # 1. 过滤有效深度值
    valid_depth = depth_image[depth_image > 0]
    if len(valid_depth) < 100:
        print("   深度数据太少")
        return None
    
    # 2. 基础统计
    min_depth = np.min(valid_depth)
    max_depth = np.max(valid_depth)
    mean_depth = np.mean(valid_depth)
    
    print(f"   深度范围: {min_depth}-{max_depth}mm, 平均: {mean_depth:.0f}mm")
    
    # 3. 过滤合理范围 (20cm - 3m)
    reasonable_depth = valid_depth[(valid_depth >= 200) & (valid_depth <= 3000)]
    if len(reasonable_depth) < 100:
        print("   合理范围内深度数据太少")
        return None
    
    # 4. 找最近的物体区域
    closest_depth = np.min(reasonable_depth)
    
    # 5. 找该深度附近的所有像素 (±2cm的范围)
    tolerance = 20  # 2cm容差
    cup_mask = np.abs(depth_image - closest_depth) <= tolerance
    
    cup_pixels = np.sum(cup_mask)
    print(f"   最近深度: {closest_depth}mm, 相关像素: {cup_pixels}个")
    
    # 6. 检查物体大小是否合理
    if cup_pixels < 50:
        print("   物体太小，可能不是水杯")
        return None
    
    if cup_pixels > 50000:  # 如果超过一半画面
        print("   物体太大，可能是背景")
        return None
    
    # 7. 计算物体的中心位置
    positions = np.where(cup_mask)
    if len(positions[0]) == 0:
        return None
    
    center_y = int(np.mean(positions[0]))
    center_x = int(np.mean(positions[1]))
    
    # 8. 获取中心点的实际深度值
    actual_depth = depth_image[center_y, center_x]
    if actual_depth == 0:
        # 如果中心点没有深度值，取周围的平均值
        region = depth_image[max(0, center_y-2):center_y+3, max(0, center_x-2):center_x+3]
        valid_region = region[region > 0]
        if len(valid_region) > 0:
            actual_depth = int(np.mean(valid_region))
        else:
            actual_depth = closest_depth
    
    # 9. 转换为3D坐标
    z = actual_depth / 1000.0  # 转米
    x = (center_x - intrinsics.ppx) * z / intrinsics.fx
    y = (center_y - intrinsics.ppy) * z / intrinsics.fy
    
    # 10. 合理性检查
    if z < 0.1 or z > 2.0:  # 距离应该在10cm-2m之间
        print(f"   距离不合理: {z:.3f}m")
        return None
    
    return (center_x, center_y, actual_depth, x, y, z)

def quick_test():
    """快速测试一次"""
    print("=== 快速测试（修正版）===")
    
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
        
        # 测试一次
        frames = pipeline.wait_for_frames(1000)
        depth_frame = frames.get_depth_frame()
        
        if depth_frame:
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            depth_image = depth_data.reshape((height, width))
            
            result = analyze_depth_for_cup(depth_image, intrinsics)
            
            if result:
                pixel_x, pixel_y, depth_mm, x_3d, y_3d, z_3d = result
                print(f"✅ 检测成功!")
                print(f"水杯位置: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f}) m")
                return True
            else:
                print("❌ 未检测到水杯")
                return False
    
    finally:
        pipeline.stop()

def main():
    """主函数"""
    print("水杯检测程序（修正版）")
    print("1. 快速测试一次")
    print("2. 连续检测")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        detect_cup_by_depth()
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
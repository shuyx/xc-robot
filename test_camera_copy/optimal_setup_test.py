#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最优设置验证脚本
验证俯视角度下的检测效果
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time

def test_overhead_detection():
    """测试俯视角度的检测效果"""
    
    print("=== 俯视角度检测效果测试 ===")
    print("请将相机调整为从上往下拍摄桌面")
    print("确保:")
    print("1. 相机距离桌面 60-80cm")
    print("2. 垂直向下拍摄")
    print("3. 白色纸杯放在深色桌面上")
    print("4. 光线均匀")
    
    input("设置好后按回车继续...")
    
    # 初始化相机
    pipeline = Pipeline()
    config = Config()
    
    # 深度流
    depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    depth_profile = depth_profile_list.get_default_video_stream_profile()
    config.enable_stream(depth_profile)
    
    # 彩色流
    has_color = False
    try:
        color_profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if color_profile_list:
            color_profile = color_profile_list.get_default_video_stream_profile()
            config.enable_stream(color_profile)
            has_color = True
    except:
        pass
    
    pipeline.start(config)
    
    try:
        # 稳定几帧
        for _ in range(5):
            pipeline.wait_for_frames(100)
        
        # 获取相机内参
        frames = pipeline.wait_for_frames(1000)
        depth_frame = frames.get_depth_frame()
        intrinsics = depth_frame.get_camera_intrinsics() if depth_frame else None
        
        print(f"\n相机参数:")
        if intrinsics:
            print(f"焦距: fx={intrinsics.fx:.1f}, fy={intrinsics.fy:.1f}")
            print(f"分辨率: {depth_frame.get_width()}x{depth_frame.get_height()}")
        
        print(f"彩色传感器: {'有' if has_color else '无'}")
        
        # 连续检测
        print("\n开始检测 (按Ctrl+C停止):")
        detection_count = 0
        success_count = 0
        
        while True:
            detection_count += 1
            print(f"\n--- 第 {detection_count} 次检测 ---")
            
            frames = pipeline.wait_for_frames(1000)
            if not frames:
                continue
            
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame() if has_color else None
            
            if not depth_frame:
                continue
            
            # 获取图像数据
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_image = depth_data.reshape((depth_frame.get_height(), depth_frame.get_width()))
            
            color_image = None
            if color_frame:
                color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
                color_image = color_data.reshape((color_frame.get_height(), color_frame.get_width(), 3))
                color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            
            # 方法1: 深度分析 (俯视角度的主要优势)
            result_depth = detect_by_depth(depth_image, intrinsics)
            
            # 方法2: 颜色检测 (如果有彩色相机)
            result_color = detect_by_color(color_image) if color_image is not None else None
            
            # 综合判断
            final_result = combine_results(result_depth, result_color, depth_image, intrinsics)
            
            if final_result:
                success_count += 1
                x, y, z = final_result
                print(f"🎯 检测成功!")
                print(f"   3D坐标: ({x:.3f}, {y:.3f}, {z:.3f}) m")
                print(f"   位置解释: 前方{z:.2f}m，右侧{x:.3f}m")
                print(f"   成功率: {success_count}/{detection_count} = {success_count/detection_count*100:.1f}%")
            else:
                print("❌ 未检测到纸杯")
                print(f"   成功率: {success_count}/{detection_count} = {success_count/detection_count*100:.1f}%")
            
            time.sleep(2)  # 2秒检测一次
    
    except KeyboardInterrupt:
        print(f"\n检测结束")
        if detection_count > 0:
            print(f"总成功率: {success_count}/{detection_count} = {success_count/detection_count*100:.1f}%")
    
    finally:
        pipeline.stop()

def detect_by_depth(depth_image, intrinsics):
    """基于深度的检测 - 俯视角度的核心方法"""
    
    # 过滤有效深度 (桌面检测范围)
    valid_depth = depth_image[(depth_image > 300) & (depth_image < 1200)]  # 30cm-120cm
    
    if len(valid_depth) < 1000:  # 有效点太少
        return None
    
    # 找桌面高度 (众数深度，大部分像素的深度)
    hist, bins = np.histogram(valid_depth, bins=50)
    table_depth = bins[np.argmax(hist)]
    
    # 找桌面上的物体 (比桌面近的点)
    object_mask = (depth_image > 0) & (depth_image < table_depth - 20)  # 比桌面高2cm以上
    
    if np.sum(object_mask) < 100:  # 物体像素太少
        return None
    
    # 找物体的最高点(距离相机最近)
    object_depths = depth_image[object_mask]
    min_depth = np.min(object_depths)
    
    # 找该深度对应的像素位置
    positions = np.where(depth_image == min_depth)
    if len(positions[0]) == 0:
        return None
    
    # 取中心位置
    pixel_y = int(np.mean(positions[0]))
    pixel_x = int(np.mean(positions[1]))
    
    print(f"深度检测: 像素({pixel_x}, {pixel_y}), 深度{min_depth}mm, 桌面{table_depth:.0f}mm")
    
    # 转3D坐标
    if intrinsics:
        z = min_depth / 1000.0
        x = (pixel_x - intrinsics.ppx) * z / intrinsics.fx
        y = (pixel_y - intrinsics.ppy) * z / intrinsics.fy
        return (x, y, z)
    
    return None

def detect_by_color(color_image):
    """基于颜色的检测 - 俯视角度下更可靠"""
    
    if color_image is None:
        return None
    
    # HSV颜色空间
    hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
    
    # 白色范围 (可能需要根据光照调整)
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 40, 255])
    
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 形态学处理
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return None
    
    # 找最大的圆形轮廓
    best_contour = None
    best_score = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # 太小忽略
            continue
        
        # 圆形度评分
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # 俯视角度下纸杯应该接近圆形
            if 0.6 < circularity < 1.4:
                score = area * circularity  # 面积和圆形度的综合评分
                if score > best_score:
                    best_score = score
                    best_contour = contour
    
    if best_contour is None:
        return None
    
    # 计算中心
    M = cv2.moments(best_contour)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    area = cv2.contourArea(best_contour)
    print(f"颜色检测: 像素({cx}, {cy}), 面积{area:.0f}")
    
    return (cx, cy)

def combine_results(result_depth, result_color, depth_image, intrinsics):
    """综合深度和颜色检测结果"""
    
    if result_depth is None:
        return None
    
    # 深度检测是主要方法
    depth_3d = result_depth
    
    # 如果有颜色检测结果，进行验证
    if result_color is not None:
        color_x, color_y = result_color
        depth_value = depth_image[color_y, color_x]
        
        if depth_value > 0 and intrinsics:
            # 颜色检测位置的3D坐标
            z = depth_value / 1000.0
            x = (color_x - intrinsics.ppx) * z / intrinsics.fx
            y = (color_y - intrinsics.ppy) * z / intrinsics.fy
            color_3d = (x, y, z)
            
            # 检查两种方法的结果是否一致
            distance = np.sqrt(sum((a-b)**2 for a, b in zip(depth_3d, color_3d)))
            
            if distance < 0.05:  # 5cm内认为一致
                print(f"✅ 深度和颜色检测结果一致 (误差{distance*100:.1f}cm)")
                return color_3d  # 颜色检测通常更精确
            else:
                print(f"⚠️ 深度和颜色检测结果不一致 (误差{distance*100:.1f}cm)")
    
    return depth_3d

def main():
    """主函数"""
    test_overhead_detection()

if __name__ == "__main__":
    main()
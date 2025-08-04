#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人视觉管道 - 获取物体3D坐标
功能：检测桌面纸杯并计算其相对于相机的3D坐标
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time

class VisionPipeline:
    """机器人视觉处理管道"""
    
    def __init__(self):
        self.pipeline = None
        self.config = None
        self.intrinsics = None  # 相机内参
        self.is_running = False
        
    def initialize_camera(self):
        """初始化相机"""
        try:
            print("=== 初始化相机 ===")
            
            # 创建Pipeline
            self.pipeline = Pipeline()
            self.config = Config()
            
            # 配置深度流
            depth_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
            if depth_profile_list is None:
                raise Exception("无法获取深度传感器配置")
            
            depth_profile = depth_profile_list.get_default_video_stream_profile()
            self.config.enable_stream(depth_profile)
            print(f"✅ 深度流配置: {depth_profile}")
            
            # 配置彩色流
            color_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
            if color_profile_list is not None:
                color_profile = color_profile_list.get_default_video_stream_profile()
                self.config.enable_stream(color_profile)
                print(f"✅ 彩色流配置: {color_profile}")
            else:
                print("⚠️ 无彩色传感器，仅使用深度数据")
            
            # 启动Pipeline
            self.pipeline.start(self.config)
            self.is_running = True
            
            # 获取相机内参
            self._get_camera_intrinsics()
            
            print("✅ 相机初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ 相机初始化失败: {e}")
            return False
    
    def _get_camera_intrinsics(self):
        """获取相机内参"""
        try:
            # 等待几帧让相机稳定
            for _ in range(5):
                frames = self.pipeline.wait_for_frames(1000)
                if frames:
                    depth_frame = frames.get_depth_frame()
                    if depth_frame:
                        break
            
            if depth_frame:
                # 获取深度相机内参
                depth_intrinsics = depth_frame.get_camera_intrinsics()
                
                self.intrinsics = {
                    'fx': depth_intrinsics.fx,
                    'fy': depth_intrinsics.fy,
                    'cx': depth_intrinsics.ppx,
                    'cy': depth_intrinsics.ppy,
                    'width': depth_frame.get_width(),
                    'height': depth_frame.get_height()
                }
                
                print(f"✅ 相机内参获取成功:")
                print(f"   焦距: fx={self.intrinsics['fx']:.2f}, fy={self.intrinsics['fy']:.2f}")
                print(f"   主点: cx={self.intrinsics['cx']:.2f}, cy={self.intrinsics['cy']:.2f}")
                print(f"   分辨率: {self.intrinsics['width']}x{self.intrinsics['height']}")
            
        except Exception as e:
            print(f"⚠️ 获取相机内参失败: {e}")
    
    def capture_frames(self):
        """采集一帧图像数据"""
        if not self.is_running:
            return None, None
        
        try:
            frames = self.pipeline.wait_for_frames(1000)
            if not frames:
                return None, None
            
            # 获取深度帧
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            
            depth_image = None
            color_image = None
            
            if depth_frame:
                # 转换深度数据
                depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
                depth_image = depth_data.reshape((depth_frame.get_height(), depth_frame.get_width()))
            
            if color_frame:
                # 转换彩色数据
                color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
                color_image = color_data.reshape((color_frame.get_height(), color_frame.get_width(), 3))
                # RGB转BGR (OpenCV格式)
                color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            
            return depth_image, color_image
            
        except Exception as e:
            print(f"❌ 采集图像失败: {e}")
            return None, None
    
    def detect_cup(self, color_image):
        """
        检测纸杯 - 使用传统视觉方法
        返回检测到的纸杯中心点坐标 (x, y)
        """
        if color_image is None:
            return None
        
        try:
            # 转换为HSV颜色空间
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
            
            # 白色纸杯的HSV范围 (可根据实际情况调整)
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            
            # 创建掩膜
            mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # 形态学操作，去除噪声
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                return None
            
            # 找到最大的轮廓（假设是纸杯）
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 计算轮廓面积，过滤太小的物体
            area = cv2.contourArea(largest_contour)
            if area < 1000:  # 最小面积阈值
                return None
            
            # 计算轮廓的中心点
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                return (cx, cy), largest_contour, area
            
            return None
            
        except Exception as e:
            print(f"❌ 杯子检测失败: {e}")
            return None
    
    def pixel_to_3d(self, pixel_x, pixel_y, depth_value):
        """
        将像素坐标和深度值转换为3D坐标
        
        Args:
            pixel_x, pixel_y: 像素坐标
            depth_value: 深度值 (毫米)
            
        Returns:
            (x, y, z): 相机坐标系下的3D坐标 (毫米)
        """
        if self.intrinsics is None or depth_value == 0:
            return None
        
        try:
            # 深度值转换为米
            z = depth_value / 1000.0
            
            # 像素坐标转换为3D坐标
            x = (pixel_x - self.intrinsics['cx']) * z / self.intrinsics['fx']
            y = (pixel_y - self.intrinsics['cy']) * z / self.intrinsics['fy']
            
            return (x, y, z)
            
        except Exception as e:
            print(f"❌ 坐标转换失败: {e}")
            return None
    
    def get_cup_3d_position(self):
        """
        获取纸杯的3D位置
        返回: (x, y, z) 相机坐标系下的坐标，单位：米
        """
        # 采集图像
        depth_image, color_image = self.capture_frames()
        
        if depth_image is None:
            return None
        
        # 如果有彩色图像，使用彩色检测
        if color_image is not None:
            detection_result = self.detect_cup(color_image)
            if detection_result is None:
                return None
                
            (cx, cy), contour, area = detection_result
            
        else:
            # 仅使用深度图像的简单检测
            # 找到桌面上最近的物体
            valid_depth = depth_image[depth_image > 0]
            if len(valid_depth) == 0:
                return None
            
            min_depth = np.min(valid_depth)
            # 找到最近物体的位置
            positions = np.where(depth_image == min_depth)
            cy, cx = positions[0][0], positions[1][0]
        
        # 获取该点的深度值
        depth_value = depth_image[cy, cx]
        
        if depth_value == 0:
            return None
        
        # 转换为3D坐标
        position_3d = self.pixel_to_3d(cx, cy, depth_value)
        
        if position_3d:
            print(f"✅ 检测到纸杯:")
            print(f"   像素坐标: ({cx}, {cy})")
            print(f"   深度值: {depth_value} mm")
            print(f"   3D坐标: ({position_3d[0]:.3f}, {position_3d[1]:.3f}, {position_3d[2]:.3f}) m")
        
        return position_3d
    
    def stop(self):
        """停止相机"""
        if self.is_running and self.pipeline:
            self.pipeline.stop()
            self.is_running = False
            print("✅ 相机已停止")

def main():
    """主函数 - 测试视觉管道"""
    vision = VisionPipeline()
    
    # 初始化相机
    if not vision.initialize_camera():
        return
    
    try:
        print("\n=== 开始检测纸杯 ===")
        print("按 Ctrl+C 停止检测")
        
        for i in range(10):  # 检测10次
            print(f"\n--- 第 {i+1} 次检测 ---")
            
            position = vision.get_cup_3d_position()
            
            if position:
                x, y, z = position
                print(f"🎯 纸杯相对相机位置: X={x:.3f}m, Y={y:.3f}m, Z={z:.3f}m")
            else:
                print("⚠️ 未检测到纸杯")
            
            time.sleep(1)  # 等待1秒
            
    except KeyboardInterrupt:
        print("\n检测已停止")
    
    finally:
        vision.stop()

if __name__ == "__main__":
    main()
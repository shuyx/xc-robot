#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版水杯检测脚本
基于深度图像检测最近物体，使用多帧平均提高稳定性
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time
from collections import deque
import threading
import math

class CupDetector:
    def __init__(self):
        self.pipeline = None
        self.config = None
        self.intrinsics = None
        self.has_color = False
        
        # 多帧平均缓冲区
        self.position_buffer = deque(maxlen=5)  # 保存最近5次检测结果
        self.depth_buffer = deque(maxlen=3)    # 保存最近3帧深度图
        
        # 检测参数
        self.min_distance = 200    # 最小检测距离 20cm
        self.max_distance = 3000   # 最大检测距离 3m
        self.depth_tolerance = 20  # 深度容差 ±2cm
        self.min_pixels = 50       # 最小像素数
        self.max_pixels = 50000    # 最大像素数
        
        # 统计信息
        self.detection_count = 0
        self.success_count = 0
        
    def initialize_camera(self):
        """初始化相机"""
        print("=== 增强版水杯检测系统 ===")
        print("特性:")
        print("- 多帧平均降噪")
        print("- 自适应阈值调整")
        print("- 实时可视化")
        print("- 3D坐标计算")
        print()
        
        self.pipeline = Pipeline()
        self.config = Config()
        
        # 配置深度流
        depth_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        if depth_profile_list is None:
            raise Exception("无法获取深度传感器")
        
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        if depth_profile is None:
            raise Exception("无法获取默认深度配置")
        
        self.config.enable_stream(depth_profile)
        print(f"✅ 深度流配置: {depth_profile}")
        
        # 尝试配置彩色流
        try:
            color_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
            if color_profile_list:
                color_profile = color_profile_list.get_default_video_stream_profile()
                if color_profile:
                    self.config.enable_stream(color_profile)
                    self.has_color = True
                    print(f"✅ 彩色流配置: {color_profile}")
        except:
            print("⚠️ 彩色传感器不可用，仅使用深度数据")
        
        # 启动相机
        self.pipeline.start(self.config)
        
        # 获取相机内参
        self._get_camera_intrinsics(depth_profile)
        
        # 预热相机
        print("相机预热中...")
        for _ in range(10):
            self.pipeline.wait_for_frames(100)
        
        print("✅ 相机初始化完成")
        return True
    
    def _get_camera_intrinsics(self, depth_profile):
        """获取相机内参"""
        try:
            depth_video_profile = depth_profile.as_video_stream_profile()
            self.intrinsics = depth_video_profile.get_intrinsics()
            
            print(f"✅ 相机内参:")
            print(f"   焦距: fx={self.intrinsics.fx:.1f}, fy={self.intrinsics.fy:.1f}")
            print(f"   主点: cx={self.intrinsics.ppx:.1f}, cy={self.intrinsics.ppy:.1f}")
            print(f"   分辨率: {self.intrinsics.width}x{self.intrinsics.height}")
            
        except Exception as e:
            print(f"⚠️ 无法获取内参: {e}")
            print("使用估算的内参")
            self.intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0,
                'width': 640, 'height': 480
            })()
    
    def get_depth_frame(self):
        """获取深度帧数据"""
        frames = self.pipeline.wait_for_frames(1000)
        if not frames:
            return None, None
        
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            return None, None
        
        # 转换深度数据
        depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
        height = depth_frame.get_height()
        width = depth_frame.get_width()
        depth_image = depth_data.reshape((height, width))
        
        # 获取彩色帧（如果可用）
        color_image = None
        if self.has_color:
            color_frame = frames.get_color_frame()
            if color_frame:
                color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
                color_height = color_frame.get_height()
                color_width = color_frame.get_width()
                color_image = color_data.reshape((color_height, color_width, 3))
        
        return depth_image, color_image
    
    def filter_depth_noise(self, depth_image):
        """多帧深度降噪"""
        # 添加到缓冲区
        self.depth_buffer.append(depth_image.copy())
        
        if len(self.depth_buffer) < 2:
            return depth_image
        
        # 计算多帧中位数，减少噪声
        depth_stack = np.stack(list(self.depth_buffer), axis=2)
        filtered_depth = np.median(depth_stack, axis=2).astype(np.uint16)
        
        return filtered_depth
    
    def find_closest_object(self, depth_image):
        """找到最近的物体区域"""
        # 过滤有效深度值
        valid_mask = (depth_image > self.min_distance) & (depth_image < self.max_distance)
        valid_depth = depth_image[valid_mask]
        
        if len(valid_depth) < 100:
            return None
        
        # 找最近深度
        closest_depth = np.min(valid_depth)
        
        # 自适应调整容差：距离越近，容差越小
        adaptive_tolerance = max(10, min(30, closest_depth * 0.015))  # 1.5%的深度作为容差
        
        # 找该深度附近的所有像素
        object_mask = np.abs(depth_image - closest_depth) <= adaptive_tolerance
        
        object_pixels = np.sum(object_mask)
        
        # 检查物体大小是否合理
        if object_pixels < self.min_pixels or object_pixels > self.max_pixels:
            return None
        
        return object_mask, closest_depth, object_pixels, adaptive_tolerance
    
    def calculate_object_center(self, object_mask, depth_image):
        """计算物体中心位置和深度"""
        positions = np.where(object_mask)
        if len(positions[0]) == 0:
            return None
        
        # 计算加权中心（按深度值加权）
        depths = depth_image[positions]
        valid_indices = depths > 0
        
        if np.sum(valid_indices) == 0:
            return None
        
        valid_positions_y = positions[0][valid_indices]
        valid_positions_x = positions[1][valid_indices]
        valid_depths = depths[valid_indices]
        
        # 使用反向深度作为权重（近的物体权重更大）
        weights = 1.0 / (valid_depths + 1)
        
        center_y = int(np.average(valid_positions_y, weights=weights))
        center_x = int(np.average(valid_positions_x, weights=weights))
        
        # 获取中心点的深度值
        center_depth = depth_image[center_y, center_x]
        
        if center_depth == 0:
            # 如果中心点没有深度值，取周围区域的中位数
            region = depth_image[max(0, center_y-2):center_y+3, max(0, center_x-2):center_x+3]
            valid_region = region[region > 0]
            if len(valid_region) > 0:
                center_depth = int(np.median(valid_region))
            else:
                center_depth = int(np.median(valid_depths))
        
        return center_x, center_y, center_depth
    
    def pixel_to_3d(self, pixel_x, pixel_y, depth_mm):
        """像素坐标转3D坐标"""
        z = depth_mm / 1000.0  # 转米
        x = (pixel_x - self.intrinsics.ppx) * z / self.intrinsics.fx
        y = (pixel_y - self.intrinsics.ppy) * z / self.intrinsics.fy
        
        return x, y, z
    
    def smooth_position(self, position_3d):
        """位置平滑滤波"""
        self.position_buffer.append(position_3d)
        
        if len(self.position_buffer) < 2:
            return position_3d
        
        # 计算加权平均（最新的检测结果权重更大）
        positions = np.array(list(self.position_buffer))
        weights = np.linspace(0.5, 2.0, len(positions))  # 权重从0.5到2.0
        weights = weights / np.sum(weights)
        
        smoothed = np.average(positions, axis=0, weights=weights)
        return tuple(smoothed)
    
    def detect_cup_once(self):
        """单次检测"""
        self.detection_count += 1
        
        # 获取深度帧
        depth_image, color_image = self.get_depth_frame()
        if depth_image is None:
            return None
        
        # 深度降噪
        filtered_depth = self.filter_depth_noise(depth_image)
        
        # 找最近物体
        object_result = self.find_closest_object(filtered_depth)
        if object_result is None:
            return None
        
        object_mask, closest_depth, object_pixels, tolerance = object_result
        
        # 计算物体中心
        center_result = self.calculate_object_center(object_mask, filtered_depth)
        if center_result is None:
            return None
        
        center_x, center_y, center_depth = center_result
        
        # 转换3D坐标
        x_3d, y_3d, z_3d = self.pixel_to_3d(center_x, center_y, center_depth)
        
        # 合理性检查
        if z_3d < 0.1 or z_3d > 2.0:
            return None
        
        # 位置平滑
        smoothed_3d = self.smooth_position((x_3d, y_3d, z_3d))
        
        self.success_count += 1
        
        result = {
            'pixel_pos': (center_x, center_y),
            'depth_mm': center_depth,
            'position_3d': smoothed_3d,
            'raw_position_3d': (x_3d, y_3d, z_3d),
            'object_pixels': object_pixels,
            'tolerance': tolerance,
            'closest_depth': closest_depth,
            'depth_image': filtered_depth,
            'color_image': color_image,
            'object_mask': object_mask,
            'success_rate': self.success_count / self.detection_count * 100
        }
        
        return result
    
    def print_detection_result(self, result):
        """打印检测结果"""
        if result is None:
            print(f"❌ 第{self.detection_count}次检测失败")
            return
        
        pixel_x, pixel_y = result['pixel_pos']
        x_3d, y_3d, z_3d = result['position_3d']
        raw_x, raw_y, raw_z = result['raw_position_3d']
        
        print(f"🎯 第{self.detection_count}次检测成功! (成功率: {result['success_rate']:.1f}%)")
        print(f"   像素坐标: ({pixel_x}, {pixel_y})")
        print(f"   深度值: {result['depth_mm']}mm")
        print(f"   平滑后3D: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f})m")
        print(f"   原始3D:   ({raw_x:.3f}, {raw_y:.3f}, {raw_z:.3f})m")
        print(f"   物体像素: {result['object_pixels']}个")
        print(f"   容差: ±{result['tolerance']:.0f}mm")
        
        # 位置描述
        distance = math.sqrt(x_3d**2 + y_3d**2 + z_3d**2)
        direction_x = "右侧" if x_3d > 0 else "左侧"
        direction_y = "下方" if y_3d > 0 else "上方"
        
        print(f"   位置: 前方{z_3d:.3f}m, {direction_x}{abs(x_3d):.3f}m, {direction_y}{abs(y_3d):.3f}m")
        print(f"   距离: {distance:.3f}m")
    
    def create_visualization(self, result):
        """创建可视化图像"""
        if result is None:
            return None
        
        depth_image = result['depth_image']
        object_mask = result['object_mask']
        pixel_x, pixel_y = result['pixel_pos']
        
        # 创建彩色深度图
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=255.0/3000.0), 
            cv2.COLORMAP_JET
        )
        
        # 标记检测到的物体
        depth_colormap[object_mask] = [0, 255, 0]  # 绿色标记
        
        # 画十字标记中心点
        cv2.drawMarker(depth_colormap, (pixel_x, pixel_y), (255, 255, 255), 
                      cv2.MARKER_CROSS, 20, 2)
        
        # 添加信息文本
        x_3d, y_3d, z_3d = result['position_3d']
        info_text = [
            f"Distance: {z_3d:.3f}m",
            f"Position: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f})",
            f"Pixels: {result['object_pixels']}",
            f"Success: {result['success_rate']:.1f}%"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(depth_colormap, text, (10, 30 + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return depth_colormap
    
    def continuous_detection(self, show_visualization=True):
        """连续检测"""
        print("\n开始连续检测...")
        print("按 'q' 退出，按 's' 保存当前帧")
        
        try:
            while True:
                start_time = time.time()
                
                # 检测
                result = self.detect_cup_once()
                
                # 打印结果
                self.print_detection_result(result)
                
                # 可视化
                if show_visualization:
                    vis_image = self.create_visualization(result)
                    if vis_image is not None:
                        cv2.imshow('Cup Detection', vis_image)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
                        elif key == ord('s') and result is not None:
                            # 保存图像
                            timestamp = int(time.time())
                            filename = f"cup_detection_{timestamp}.jpg"
                            cv2.imwrite(filename, vis_image)
                            print(f"   💾 图像已保存: {filename}")
                
                # 控制帧率
                processing_time = time.time() - start_time
                sleep_time = max(0, 0.5 - processing_time)  # 目标2fps
                time.sleep(sleep_time)
                
                print()  # 空行分隔
                
        except KeyboardInterrupt:
            print(f"\n检测停止")
        
        if show_visualization:
            cv2.destroyAllWindows()
    
    def quick_test(self):
        """快速测试"""
        print("快速测试...")
        result = self.detect_cup_once()
        self.print_detection_result(result)
        return result is not None
    
    def cleanup(self):
        """清理资源"""
        if self.pipeline:
            self.pipeline.stop()
        cv2.destroyAllWindows()
        print("✅ 资源已清理")

def main():
    """主函数"""
    detector = CupDetector()
    
    try:
        # 初始化相机
        if not detector.initialize_camera():
            print("❌ 相机初始化失败")
            return
        
        print("\n请选择模式:")
        print("1. 快速测试一次")
        print("2. 连续检测（有可视化）")
        print("3. 连续检测（无可视化）")
        
        choice = input("请选择 (1/2/3): ").strip()
        
        if choice == "1":
            detector.quick_test()
        elif choice == "2":
            detector.continuous_detection(show_visualization=True)
        elif choice == "3":
            detector.continuous_detection(show_visualization=False)
        else:
            print("无效选择")
    
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        detector.cleanup()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不同检测方法的演示和对比
帮助理解各种方法的原理和适用场景
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time

class DetectionMethodsDemo:
    """不同检测方法的演示类"""
    
    def __init__(self):
        self.pipeline = None
        self.setup_camera()
    
    def setup_camera(self):
        """设置相机"""
        self.pipeline = Pipeline()
        config = Config()
        
        # 深度流
        depth_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        config.enable_stream(depth_profile)
        
        # 彩色流
        try:
            color_profile_list = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
            if color_profile_list:
                color_profile = color_profile_list.get_default_video_stream_profile()
                config.enable_stream(color_profile)
                self.has_color = True
            else:
                self.has_color = False
        except:
            self.has_color = False
        
        self.pipeline.start(config)
        print(f"相机设置完成，彩色传感器: {'有' if self.has_color else '无'}")
    
    def get_frames(self):
        """获取图像帧"""
        frames = self.pipeline.wait_for_frames(1000)
        if not frames:
            return None, None
        
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame() if self.has_color else None
        
        depth_image = None
        color_image = None
        
        if depth_frame:
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_image = depth_data.reshape((depth_frame.get_height(), depth_frame.get_width()))
        
        if color_frame:
            color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
            color_image = color_data.reshape((color_frame.get_height(), color_frame.get_width(), 3))
            color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        
        return depth_image, color_image

    def method1_color_detection(self, color_image):
        """
        方法1: 颜色检测 (最简单)
        原理: 根据颜色找物体
        难度: ⭐
        适用: 颜色鲜明的物体 (白纸杯、红苹果等)
        """
        print("\n=== 方法1: 颜色检测 ===")
        print("原理: 在HSV颜色空间中找特定颜色范围")
        
        if color_image is None:
            print("❌ 需要彩色图像")
            return None
        
        # 转HSV颜色空间
        hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        
        # 定义白色范围 (可调整)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        
        # 创建掩膜
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # 去噪声
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            print("❌ 未检测到目标颜色")
            return None
        
        # 找最大轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        if area < 500:  # 面积太小
            print("❌ 检测到的物体太小")
            return None
        
        # 计算中心点
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            print(f"✅ 检测成功:")
            print(f"   位置: ({cx}, {cy})")
            print(f"   面积: {area:.0f} 像素")
            
            return (cx, cy), area
        
        return None

    def method2_depth_analysis(self, depth_image):
        """
        方法2: 深度分析 (简单)
        原理: 找距离最近的物体
        难度: ⭐⭐
        适用: 桌面抓取，目标物体是最前景的
        """
        print("\n=== 方法2: 深度分析 ===")
        print("原理: 找到距离相机最近的物体")
        
        if depth_image is None:
            print("❌ 需要深度图像")
            return None
        
        # 过滤有效深度
        valid_depth = depth_image[(depth_image > 200) & (depth_image < 2000)]  # 20cm-2m
        
        if len(valid_depth) == 0:
            print("❌ 无有效深度数据")
            return None
        
        # 找最近点
        min_depth = np.min(valid_depth)
        positions = np.where(depth_image == min_depth)
        
        if len(positions[0]) == 0:
            print("❌ 未找到最近点")
            return None
        
        # 取中心位置
        pixel_y = int(np.mean(positions[0]))
        pixel_x = int(np.mean(positions[1]))
        
        print(f"✅ 检测成功:")
        print(f"   位置: ({pixel_x}, {pixel_y})")
        print(f"   深度: {min_depth} mm")
        
        return (pixel_x, pixel_y), min_depth

    def method3_template_matching(self, color_image):
        """
        方法3: 模板匹配 (中等)
        原理: 用已知的纸杯图像作为模板去匹配
        难度: ⭐⭐⭐
        适用: 形状固定的物体
        """
        print("\n=== 方法3: 模板匹配 ===")
        print("原理: 用预先准备的纸杯模板图像进行匹配")
        print("注意: 需要预先拍摄纸杯模板图像")
        
        if color_image is None:
            print("❌ 需要彩色图像")
            return None
        
        # 这里只是演示原理，实际需要真实的模板图像
        print("演示: 如果有模板图像cup_template.jpg:")
        print("1. template = cv2.imread('cup_template.jpg', 0)")
        print("2. result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)")
        print("3. 找到匹配度最高的位置")
        
        return None

    def method4_contour_analysis(self, color_image):
        """
        方法4: 轮廓分析 (中等)
        原理: 根据物体的形状特征(圆形、矩形等)检测
        难度: ⭐⭐⭐
        适用: 形状特征明显的物体
        """
        print("\n=== 方法4: 轮廓分析 ===")
        print("原理: 分析物体轮廓的形状特征")
        
        if color_image is None:
            print("❌ 需要彩色图像")
            return None
        
        # 转灰度
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cup_candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:  # 太小的忽略
                continue
            
            # 计算轮廓特征
            perimeter = cv2.arcLength(contour, True)
            
            # 圆形度 (4π×面积/周长²)，圆形接近1
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # 纸杯从上往下看接近圆形
                if 0.7 < circularity < 1.3:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        cup_candidates.append({
                            'center': (cx, cy),
                            'area': area,
                            'circularity': circularity
                        })
        
        if len(cup_candidates) == 0:
            print("❌ 未找到圆形物体")
            return None
        
        # 选择面积最大的圆形物体
        best_candidate = max(cup_candidates, key=lambda x: x['area'])
        
        print(f"✅ 检测成功:")
        print(f"   位置: {best_candidate['center']}")
        print(f"   面积: {best_candidate['area']:.0f}")
        print(f"   圆形度: {best_candidate['circularity']:.2f}")
        
        return best_candidate['center'], best_candidate['area']

    def method5_point_cloud_analysis(self, depth_image):
        """
        方法5: 点云分析 (复杂)
        原理: 将深度图转为3D点云，分析3D几何特征
        难度: ⭐⭐⭐⭐
        适用: 复杂3D形状分析
        """
        print("\n=== 方法5: 点云分析 ===")
        print("原理: 将深度数据转换为3D点云，分析3D形状")
        
        if depth_image is None:
            print("❌ 需要深度图像")
            return None
        
        # 获取相机内参
        frames = self.pipeline.wait_for_frames(100)
        if frames:
            depth_frame = frames.get_depth_frame()
            if depth_frame:
                intrinsics = depth_frame.get_camera_intrinsics()
                
                print("点云生成过程:")
                print("1. 遍历每个深度像素")
                print("2. 将(x,y,depth)转换为3D坐标(X,Y,Z)")
                print("3. 生成点云数据")
                
                # 简化的点云生成示例
                height, width = depth_image.shape
                point_count = 0
                
                for y in range(0, height, 10):  # 跳采样，避免太多点
                    for x in range(0, width, 10):
                        depth = depth_image[y, x]
                        if 200 < depth < 2000:  # 有效深度范围
                            # 转3D坐标
                            z = depth / 1000.0
                            X = (x - intrinsics.ppx) * z / intrinsics.fx
                            Y = (y - intrinsics.ppy) * z / intrinsics.fy
                            
                            point_count += 1
                
                print(f"✅ 生成了 {point_count} 个3D点")
                print("可以进一步分析:")
                print("- 平面检测 (找桌面)")
                print("- 聚类分析 (分离物体)")
                print("- 几何形状拟合 (识别圆柱体)")
                
                return point_count
        
        return None

    def run_demo(self):
        """运行演示"""
        print("=" * 50)
        print("物体检测方法演示")
        print("=" * 50)
        
        try:
            # 稳定几帧
            for _ in range(5):
                self.pipeline.wait_for_frames(100)
            
            # 获取图像
            depth_image, color_image = self.get_frames()
            
            if depth_image is None:
                print("❌ 无法获取图像")
                return
            
            print(f"图像尺寸: {depth_image.shape}")
            print(f"彩色图像: {'有' if color_image is not None else '无'}")
            
            # 演示不同方法
            methods = [
                ("颜色检测", lambda: self.method1_color_detection(color_image)),
                ("深度分析", lambda: self.method2_depth_analysis(depth_image)),
                ("模板匹配", lambda: self.method3_template_matching(color_image)),
                ("轮廓分析", lambda: self.method4_contour_analysis(color_image)),
                ("点云分析", lambda: self.method5_point_cloud_analysis(depth_image))
            ]
            
            for name, method in methods:
                try:
                    result = method()
                    time.sleep(1)  # 暂停1秒
                except Exception as e:
                    print(f"❌ {name}执行失败: {e}")
        
        except KeyboardInterrupt:
            print("\n演示被中断")
        
        finally:
            if self.pipeline:
                self.pipeline.stop()
                print("✅ 相机已关闭")

def main():
    """主函数"""
    print("物体检测方法对比演示")
    print("\n这个程序会演示5种不同的检测方法:")
    print("1. 颜色检测 - 最简单，适合初学者")
    print("2. 深度分析 - 利用深度相机优势")
    print("3. 模板匹配 - 需要预先准备模板")
    print("4. 轮廓分析 - 基于形状特征")
    print("5. 点云分析 - 最复杂，3D分析")
    
    input("\n按回车开始演示...")
    
    demo = DetectionMethodsDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
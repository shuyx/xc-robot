#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景影响分析工具
帮助理解不同背景对检测效果的影响
"""

import cv2
import numpy as np
from pyorbbecsdk import *
import time

class BackgroundAnalyzer:
    """背景影响分析器"""
    
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
    
    def analyze_color_interference(self, color_image):
        """分析颜色干扰"""
        print("\n=== 颜色检测背景干扰分析 ===")
        
        if color_image is None:
            print("❌ 需要彩色图像")
            return
        
        # 白色检测
        hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 50, 255])
        
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # 统计白色区域
        white_pixels = np.sum(white_mask > 0)
        total_pixels = white_mask.shape[0] * white_mask.shape[1]
        white_ratio = white_pixels / total_pixels
        
        print(f"白色像素占比: {white_ratio*100:.1f}%")
        
        if white_ratio > 0.3:
            print("⚠️ 背景中白色区域过多，容易误检")
            print("建议:")
            print("- 更换背景（深色背景更好）")
            print("- 调整HSV范围，更精确地定位纸杯白色")
            print("- 结合深度信息过滤背景")
        elif white_ratio > 0.1:
            print("⚠️ 背景中有一些白色，需要结合其他方法")
            print("建议: 颜色检测 + 深度过滤")
        else:
            print("✅ 背景干净，颜色检测效果应该不错")
        
        # 找轮廓分析
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            print(f"检测到 {len(contours)} 个白色区域")
            
            # 分析最大的几个区域
            areas = [cv2.contourArea(c) for c in contours]
            areas.sort(reverse=True)
            
            print("最大的5个白色区域面积:")
            for i, area in enumerate(areas[:5]):
                print(f"  区域{i+1}: {area:.0f} 像素")
                
            if len(areas) > 5:
                print("背景可能比较复杂，建议简化背景")
    
    def analyze_depth_advantage(self, depth_image):
        """分析深度检测的优势"""
        print("\n=== 深度检测背景分析 ===")
        
        if depth_image is None:
            print("❌ 需要深度图像")
            return
        
        # 深度统计
        valid_depth = depth_image[depth_image > 0]
        if len(valid_depth) == 0:
            print("❌ 无有效深度数据")
            return
        
        min_depth = np.min(valid_depth)
        max_depth = np.max(valid_depth)
        mean_depth = np.mean(valid_depth)
        
        print(f"深度范围: {min_depth}mm - {max_depth}mm")
        print(f"平均深度: {mean_depth:.0f}mm")
        
        # 分析深度层次
        depth_ranges = [
            (0, 500, "很近 (<50cm)"),
            (500, 1000, "近 (50-100cm)"),
            (1000, 1500, "中等 (1-1.5m)"),
            (1500, 2000, "远 (1.5-2m)"),
            (2000, 5000, "很远 (>2m)")
        ]
        
        print("\n深度分布:")
        for min_d, max_d, desc in depth_ranges:
            count = np.sum((valid_depth >= min_d) & (valid_depth < max_d))
            ratio = count / len(valid_depth) * 100
            print(f"  {desc}: {ratio:.1f}% ({count} 像素)")
        
        # 判断背景复杂度
        depth_std = np.std(valid_depth)
        print(f"\n深度标准差: {depth_std:.0f}mm")
        
        if depth_std > 500:
            print("✅ 场景深度层次丰富，深度检测优势明显")
            print("推荐: 使用深度分析法，背景影响很小")
        elif depth_std > 200:
            print("✅ 有一定深度层次，深度检测有效")
        else:
            print("⚠️ 场景比较平坦，深度优势不明显")
    
    def compare_viewing_angles(self):
        """比较不同视角的优缺点"""
        print("\n=== 拍摄角度对比分析 ===")
        
        print("📐 前往后照射 (水平视角):")
        print("✅ 优点:")
        print("   - 符合人类视觉习惯")
        print("   - 纸杯侧面轮廓清晰")
        print("   - 高度信息明显")
        print("❌ 缺点:")
        print("   - 背景复杂（墙面、物品等）")
        print("   - 容易被其他物体遮挡")
        print("   - 白色检测受背景干扰大")
        
        print("\n📐 上往下照射 (俯视角):")
        print("✅ 优点:")
        print("   - 背景简单（主要是桌面）")
        print("   - 不易被遮挡")
        print("   - 深度层次清晰（桌面vs物体）")
        print("   - 适合机械臂抓取路径")
        print("❌ 缺点:")
        print("   - 纸杯看起来是圆形，缺少侧面信息")
        print("   - 高度信息不够直观")
        
        print("\n🎯 推荐方案:")
        print("对于桌面抓取任务，建议 **上往下照射**")
        print("原因:")
        print("1. 背景最简洁，检测精度高")
        print("2. 深度相机优势突出（桌面是明显的背景平面）")
        print("3. 符合机械臂工作方式")
        print("4. 可以同时看到多个物体的相对位置")
    
    def recommend_setup(self):
        """推荐设置方案"""
        print("\n=== 推荐设置方案 ===")
        
        print("🎯 **推荐配置: 上往下俯视**")
        
        print("\n📏 距离设置:")
        print("- 相机高度: 60-100cm (距离桌面)")
        print("- 检测范围: 30x30cm 到 50x50cm 的桌面区域")
        print("- 为什么: 既能看清细节，又有足够视野")
        
        print("\n💡 背景优化:")
        print("- 桌面颜色: 深色更好（黑色、深蓝、深绿）")
        print("- 避免: 白色桌面、反光表面")
        print("- 光照: 均匀柔和，避免强烈阴影")
        
        print("\n🔧 检测策略:")
        print("1. 主要用深度分析（找桌面上最高的物体）")
        print("2. 辅助用颜色检测（区分不同物体）")
        print("3. 形状验证（确认是圆形物体）")
        
        print("\n📊 预期效果:")
        print("- 检测准确率: >90%")
        print("- 定位精度: ±5mm")
        print("- 处理速度: <100ms")
    
    def run_analysis(self):
        """运行完整分析"""
        print("=" * 60)
        print("背景影响和拍摄角度分析")
        print("=" * 60)
        
        try:
            # 稳定几帧
            for _ in range(5):
                self.pipeline.wait_for_frames(100)
            
            # 获取当前场景
            depth_image, color_image = self.get_frames()
            
            if depth_image is None:
                print("❌ 无法获取图像")
                return
            
            print(f"当前场景尺寸: {depth_image.shape}")
            
            # 分析当前场景
            if color_image is not None:
                self.analyze_color_interference(color_image)
            
            self.analyze_depth_advantage(depth_image)
            self.compare_viewing_angles()
            self.recommend_setup()
            
        except Exception as e:
            print(f"分析过程出错: {e}")
        
        finally:
            if self.pipeline:
                self.pipeline.stop()

def main():
    """主函数"""
    analyzer = BackgroundAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
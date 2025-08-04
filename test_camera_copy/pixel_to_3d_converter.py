#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
像素坐标转3D坐标工具
用于手眼标定数据收集
"""

import numpy as np
from pyorbbecsdk import *
import time
import json
from datetime import datetime

class PixelTo3DConverter:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        self.current_depth_image = None
        self.calibration_data = []
        
    def initialize_camera(self):
        """初始化相机"""
        print("🔍 初始化相机...")
        
        self.camera_pipeline = Pipeline()
        config = Config()
        
        # 配置深度流
        depth_profile_list = self.camera_pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        config.enable_stream(depth_profile)
        
        # 启动相机
        self.camera_pipeline.start(config)
        
        # 获取内参
        try:
            depth_video_profile = depth_profile.as_video_stream_profile()
            self.camera_intrinsics = depth_video_profile.get_intrinsics()
            print(f"✅ 相机内参: fx={self.camera_intrinsics.fx:.1f}, fy={self.camera_intrinsics.fy:.1f}")
            print(f"   主点: cx={self.camera_intrinsics.ppx:.1f}, cy={self.camera_intrinsics.ppy:.1f}")
            print(f"   分辨率: {self.camera_intrinsics.width}x{self.camera_intrinsics.height}")
        except:
            # 使用估算值
            self.camera_intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0,
                'width': 640, 'height': 480
            })()
            print("✅ 使用估算相机内参")
        
        # 预热相机
        print("相机预热中...")
        for _ in range(5):
            self.camera_pipeline.wait_for_frames(100)
        
        print("✅ 相机初始化完成")
        return True
    
    def capture_current_depth(self):
        """实时捕获当前深度图像"""
        try:
            # 连续获取几帧，确保是最新的
            for _ in range(3):
                frames = self.camera_pipeline.wait_for_frames(1000)
                depth_frame = frames.get_depth_frame()
            
            if not depth_frame:
                print("❌ 未获取到深度帧")
                return False
            
            # 转换为numpy数组
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            self.current_depth_image = depth_data.reshape((height, width))
            
            print(f"✅ 已捕获最新深度图像: {width}x{height}")
            
            # 显示深度图像统计信息
            valid_depths = self.current_depth_image[self.current_depth_image > 0]
            if len(valid_depths) > 0:
                print(f"   深度范围: {np.min(valid_depths)}-{np.max(valid_depths)}mm")
                print(f"   平均深度: {np.mean(valid_depths):.0f}mm")
                print(f"   有效像素: {len(valid_depths)}个")
            
            return True
            
        except Exception as e:
            print(f"❌ 捕获深度图像失败: {e}")
            return False
    
    def pixel_to_3d(self, pixel_x, pixel_y):
        """将像素坐标转换为3D坐标"""
        if self.current_depth_image is None:
            print("❌ 请先捕获深度图像")
            return None
        
        height, width = self.current_depth_image.shape
        
        # 检查像素坐标是否在范围内
        if pixel_x < 0 or pixel_x >= width or pixel_y < 0 or pixel_y >= height:
            print(f"❌ 像素坐标超出范围: ({pixel_x}, {pixel_y})")
            print(f"   图像尺寸: {width}x{height}")
            return None
        
        # 获取该点的深度值
        depth_mm = self.current_depth_image[pixel_y, pixel_x]
        
        if depth_mm == 0:
            print(f"❌ 像素点({pixel_x}, {pixel_y})没有有效深度数据")
            
            # 尝试在周围3x3区域寻找有效深度
            print("🔍 搜索周围区域...")
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    ny, nx = pixel_y + dy, pixel_x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        nearby_depth = self.current_depth_image[ny, nx]
                        if nearby_depth > 0:
                            print(f"   找到邻近点({nx}, {ny}): {nearby_depth}mm")
            return None
        
        # 转换为3D坐标
        z = depth_mm / 1000.0  # 转米
        x = (pixel_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
        y = (pixel_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
        
        print(f"✅ 像素({pixel_x}, {pixel_y}) → 3D坐标:")
        print(f"   深度值: {depth_mm}mm")
        print(f"   3D坐标: ({x:.3f}, {y:.3f}, {z:.3f})m")
        print(f"   3D坐标: ({x*1000:.1f}, {y*1000:.1f}, {z*1000:.1f})mm")
        
        return {
            'pixel': (pixel_x, pixel_y),
            'depth_mm': depth_mm,
            'position_3d_m': (x, y, z),
            'position_3d_mm': (x*1000, y*1000, z*1000)
        }
    
    def add_calibration_point(self, pixel_x, pixel_y, robot_x, robot_y, robot_z, description=""):
        """添加标定点对"""
        # 先转换像素到3D
        camera_result = self.pixel_to_3d(pixel_x, pixel_y)
        if camera_result is None:
            print("❌ 无法获取该像素点的3D坐标")
            return False
        
        # 添加到标定数据
        calibration_point = {
            'pixel': camera_result['pixel'],
            'camera_3d_m': camera_result['position_3d_m'],
            'camera_3d_mm': camera_result['position_3d_mm'],
            'robot_tcp_mm': (robot_x, robot_y, robot_z),
            'depth_mm': camera_result['depth_mm'],
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        
        self.calibration_data.append(calibration_point)
        
        print(f"\n📋 已添加标定点 {len(self.calibration_data)}: {description}")
        print(f"   像素坐标: ({pixel_x}, {pixel_y})")
        print(f"   相机3D: ({camera_result['position_3d_mm'][0]:.1f}, {camera_result['position_3d_mm'][1]:.1f}, {camera_result['position_3d_mm'][2]:.1f})mm")
        print(f"   机械臂TCP: ({robot_x:.1f}, {robot_y:.1f}, {robot_z:.1f})mm")
        
        return True
    
    def show_calibration_data(self):
        """显示所有标定数据"""
        if not self.calibration_data:
            print("📋 暂无标定数据")
            return
        
        print(f"\n📋 标定数据汇总 ({len(self.calibration_data)}个点):")
        print("-" * 100)
        print(f"{'序号':<4} {'描述':<12} {'像素坐标':<12} {'相机3D(mm)':<30} {'机械臂TCP(mm)':<30}")
        print("-" * 100)
        
        for i, item in enumerate(self.calibration_data, 1):
            pixel_str = f"({item['pixel'][0]},{item['pixel'][1]})"
            camera_str = f"({item['camera_3d_mm'][0]:.1f},{item['camera_3d_mm'][1]:.1f},{item['camera_3d_mm'][2]:.1f})"
            robot_str = f"({item['robot_tcp_mm'][0]:.1f},{item['robot_tcp_mm'][1]:.1f},{item['robot_tcp_mm'][2]:.1f})"
            print(f"{i:<4} {item['description'][:11]:<12} {pixel_str:<12} {camera_str:<30} {robot_str:<30}")
    
    def save_calibration_data(self, filename="calibration_data.json"):
        """保存标定数据到文件"""
        data = {
            'calibration_points': self.calibration_data,
            'camera_intrinsics': {
                'fx': self.camera_intrinsics.fx,
                'fy': self.camera_intrinsics.fy,
                'cx': self.camera_intrinsics.ppx,
                'cy': self.camera_intrinsics.ppy,
                'width': self.camera_intrinsics.width,
                'height': self.camera_intrinsics.height
            },
            'save_time': datetime.now().isoformat(),
            'num_points': len(self.calibration_data)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 标定数据已保存到: {filename}")
    
    def interactive_mode(self):
        """交互模式"""
        print("\n🎮 交互模式启动")
        print("工作流程:")
        print("  1. 在相机显示软件上找到合适的标定点")
        print("  2. 使用 capture 命令获取当前深度图像")
        print("  3. 使用 convert <x> <y> 查看该像素点的3D坐标")
        print("  4. 控制机械臂移动到该点，记录TCP坐标")
        print("  5. 使用 add 命令添加标定点对")
        print()
        print("命令:")
        print("  capture - 实时捕获当前深度图像")
        print("  convert <x> <y> - 转换像素坐标到3D")
        print("  add <x> <y> <X> <Y> <Z> [描述] - 添加标定点")
        print("  show - 显示所有标定数据")
        print("  save [文件名] - 保存标定数据")
        print("  quit - 退出")
        print()
        print("💡 建议：每次在相机软件上选定点后，立即运行 capture + convert")
        
        while True:
            try:
                cmd = input("👉 请输入命令: ").strip().split()
                if not cmd:
                    continue
                
                if cmd[0] == "quit":
                    break
                elif cmd[0] == "capture":
                    self.capture_current_depth()
                elif cmd[0] == "convert" and len(cmd) >= 3:
                    pixel_x, pixel_y = int(cmd[1]), int(cmd[2])
                    self.pixel_to_3d(pixel_x, pixel_y)
                elif cmd[0] == "add" and len(cmd) >= 6:
                    pixel_x, pixel_y = int(cmd[1]), int(cmd[2])
                    robot_x, robot_y, robot_z = float(cmd[3]), float(cmd[4]), float(cmd[5])
                    description = " ".join(cmd[6:]) if len(cmd) > 6 else f"点{len(self.calibration_data)+1}"
                    self.add_calibration_point(pixel_x, pixel_y, robot_x, robot_y, robot_z, description)
                elif cmd[0] == "show":
                    self.show_calibration_data()
                elif cmd[0] == "save":
                    filename = cmd[1] if len(cmd) > 1 else "calibration_data.json"
                    self.save_calibration_data(filename)
                else:
                    print("❌ 无效命令")
                    
            except (ValueError, IndexError) as e:
                print(f"❌ 命令格式错误: {e}")
            except KeyboardInterrupt:
                break
        
        print("👋 交互模式结束")
    
    def cleanup(self):
        """清理资源"""
        if self.camera_pipeline:
            self.camera_pipeline.stop()
        print("✅ 相机资源已清理")

def main():
    """主函数"""
    print("🎯 像素坐标转3D坐标工具")
    print("=" * 50)
    
    converter = PixelTo3DConverter()
    
    try:
        # 初始化相机
        if not converter.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        # 捕获初始深度图像
        print("\n📸 捕获初始深度图像...")
        if not converter.capture_current_depth():
            print("❌ 初始深度图像捕获失败")
            return 1
        
        # 进入交互模式
        converter.interactive_mode()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断程序")
        return 1
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        converter.cleanup()

if __name__ == "__main__":
    import sys
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速像素查询工具
专门用于查询指定像素点的3D坐标
"""
#num:1
#(58.8, 48.9, 247.0)
#X=-290.9, Y=32.3, Z=-393.5
#RX=177.1, RY=3.0, RZ=-94.4
#[-349.7,-16.6,-640.5]

#num:2
#(81.9, 43.1, 353.0)
#X=-282.9, Y=34.2, Z=-486.1
#RX=177.2, RY=3.0, RZ=-94.5

#num:3
#
import numpy as np
from pyorbbecsdk import *
import time

class QuickPixelQuery:
    def __init__(self):
        self.camera_pipeline = None
        self.camera_intrinsics = None
        
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
        except:
            self.camera_intrinsics = type('obj', (object,), {
                'fx': 500.0, 'fy': 500.0, 
                'ppx': 320.0, 'ppy': 240.0
            })()
            print("✅ 使用估算相机内参")
        
        # 预热相机
        for _ in range(3):
            self.camera_pipeline.wait_for_frames(100)
        
        print("✅ 相机就绪")
        return True
    
    def query_pixel_3d(self, pixel_x, pixel_y):
        """查询指定像素的3D坐标"""
        print(f"\n🔍 查询像素点 ({pixel_x}, {pixel_y}) 的3D坐标...")
        
        try:
            # 获取最新深度图像
            print("📸 捕获最新深度图像...")
            for _ in range(3):  # 获取最新帧
                frames = self.camera_pipeline.wait_for_frames(1000)
                depth_frame = frames.get_depth_frame()
            
            if not depth_frame:
                print("❌ 未获取到深度帧")
                return None
            
            # 转换深度数据
            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            depth_image = depth_data.reshape((height, width))
            
            print(f"✅ 深度图像: {width}x{height}")
            
            # 检查像素坐标
            if pixel_x < 0 or pixel_x >= width or pixel_y < 0 or pixel_y >= height:
                print(f"❌ 像素坐标超出范围: ({pixel_x}, {pixel_y})")
                print(f"   图像尺寸: {width}x{height}")
                return None
            
            # 获取深度值
            depth_mm = depth_image[pixel_y, pixel_x]
            
            if depth_mm == 0:
                print(f"❌ 像素点({pixel_x}, {pixel_y})没有有效深度数据")
                
                # 搜索周围5x5区域
                print("🔍 搜索周围5x5区域的有效深度...")
                found_nearby = False
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        ny, nx = pixel_y + dy, pixel_x + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            nearby_depth = depth_image[ny, nx]
                            if nearby_depth > 0:
                                print(f"   邻近点({nx}, {ny}): {nearby_depth}mm")
                                found_nearby = True
                
                if not found_nearby:
                    print("   周围区域也没有有效深度数据")
                
                return None
            
            # 转换为3D坐标
            z = depth_mm / 1000.0  # 转米
            x = (pixel_x - self.camera_intrinsics.ppx) * z / self.camera_intrinsics.fx
            y = (pixel_y - self.camera_intrinsics.ppy) * z / self.camera_intrinsics.fy
            
            print(f"\n🎯 查询结果:")
            print(f"   像素坐标: ({pixel_x}, {pixel_y})")
            print(f"   深度值: {depth_mm}mm")
            print(f"   3D坐标(米): ({x:.3f}, {y:.3f}, {z:.3f})")
            print(f"   3D坐标(毫米): ({x*1000:.1f}, {y*1000:.1f}, {z*1000:.1f})")
            
            # 显示周围深度信息
            print(f"\n📊 周围区域深度信息:")
            for dy in range(-1, 2):
                row_str = "   "
                for dx in range(-1, 2):
                    ny, nx = pixel_y + dy, pixel_x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        nearby_depth = depth_image[ny, nx]
                        if dx == 0 and dy == 0:
                            row_str += f"[{nearby_depth:4d}]"
                        else:
                            row_str += f" {nearby_depth:4d} "
                    else:
                        row_str += "  --- "
                print(row_str)
            
            return {
                'pixel': (pixel_x, pixel_y),
                'depth_mm': depth_mm,
                'position_3d_m': (x, y, z),
                'position_3d_mm': (x*1000, y*1000, z*1000)
            }
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return None
    
    def cleanup(self):
        """清理资源"""
        if self.camera_pipeline:
            self.camera_pipeline.stop()
        print("✅ 相机资源已清理")

def main():
    """主函数"""
    print("🎯 快速像素查询工具")
    print("=" * 40)
    
    query_tool = QuickPixelQuery()
    
    try:
        # 初始化相机
        if not query_tool.initialize_camera():
            print("❌ 相机初始化失败")
            return 1
        
        print("\n💡 使用方法:")
        print("   输入像素坐标 (格式: x y)")
        print("   例如: 320 240")
        print("   输入 quit 退出")
        print()
        
        while True:
            try:
                user_input = input("👉 请输入像素坐标 (x y): ").strip()
                
                if user_input.lower() == 'quit':
                    break
                
                if not user_input:
                    continue
                
                # 解析坐标
                parts = user_input.split()
                if len(parts) != 2:
                    print("❌ 请输入两个数字 (x y)")
                    continue
                
                pixel_x, pixel_y = int(parts[0]), int(parts[1])
                
                # 查询3D坐标
                result = query_tool.query_pixel_3d(pixel_x, pixel_y)
                
                if result:
                    print("✅ 查询完成")
                else:
                    print("❌ 查询失败")
                
                print("-" * 50)
                
            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                break
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        return 1
    finally:
        query_tool.cleanup()

if __name__ == "__main__":
    import sys
    sys.exit(main())
#!/usr/bin/env python3
"""
在官方examples目录下的相机测试
"""

from pyorbbecsdk import *
import cv2
import numpy as np

def main():
    print("=== 相机功能测试 ===")
    
    try:
        # 创建Context
        ctx = Context()
        print("✅ Context创建成功")
        
        # 查询设备
        device_list = ctx.query_devices()
        device_count = device_list.get_count()
        print(f"发现 {device_count} 个设备")
        
        if device_count == 0:
            print("❌ 未检测到设备")
            return
        
        # 获取第一个设备
        device = device_list.get_device_by_index(0)
        device_info = device.get_device_info()
        
        print("设备信息:")
        print(f"  名称: {device_info.get_name()}")
        print(f"  PID: 0x{device_info.get_pid():04x}")
        print(f"  序列号: {device_info.get_serial_number()}")
        print(f"  固件版本: {device_info.get_firmware_version()}")
        print(f"  硬件版本: {device_info.get_hardware_version()}")
        
        # 创建Pipeline
        pipeline = Pipeline()
        print("✅ Pipeline创建成功")
        
        # 启动Pipeline
        pipeline.start()
        print("✅ Pipeline启动成功")
        
        print("\n开始获取图像数据...")
        print("按 'q' 键退出")
        
        frame_count = 0
        while frame_count < 100:  # 最多100帧
            frames = pipeline.wait_for_frames(1000)
            if frames:
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()
                
                frame_count += 1
                
                if color_frame:
                    print(f"帧 {frame_count}: 彩色图像 {color_frame.get_width()}x{color_frame.get_height()}")
                
                if depth_frame:
                    print(f"帧 {frame_count}: 深度图像 {depth_frame.get_width()}x{depth_frame.get_height()}")
                    print(f"  深度缩放因子: {depth_frame.get_depth_scale()}")
                
                # 每10帧打印一次统计
                if frame_count % 10 == 0:
                    print(f"已成功获取 {frame_count} 帧数据")
                
                if frame_count >= 30:  # 获取30帧后自动退出
                    break
            else:
                print("等待帧数据...")
        
        # 停止Pipeline
        pipeline.stop()
        print(f"✅ Pipeline停止成功，共获取 {frame_count} 帧")
        
        print("🎉 相机测试完成！相机工作正常")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")
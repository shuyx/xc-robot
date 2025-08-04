#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我们自己的相机测试脚本
在test_camera_copy目录中，继承了完整的环境配置
就像examples目录一样简单直接！
"""

# 直接导入，就像examples目录下的脚本一样
from pyorbbecsdk import Context, Pipeline, Config, OB_STREAM_DEPTH, OB_STREAM_COLOR
import time

def test_basic_connection():
    """测试基础连接"""
    print("=== 测试相机连接 ===")
    
    try:
        # 创建Context
        ctx = Context()
        print("✅ Context创建成功")
        
        # 查询设备
        device_list = ctx.query_devices()
        device_count = device_list.get_count()
        print(f"发现 {device_count} 个设备")
        
        if device_count == 0:
            print("⚠️ 未发现设备，请检查相机连接")
            return False
        
        # 获取设备信息
        device = device_list.get_device_by_index(0)
        device_info = device.get_device_info()
        
        print("设备信息:")
        print(f"  名称: {device_info.get_name()}")
        print(f"  序列号: {device_info.get_serial_number()}")
        print(f"  固件版本: {device_info.get_firmware_version()}")
        print(f"  硬件版本: {device_info.get_hardware_version()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def test_image_capture():
    """测试图像采集"""
    print("\n=== 测试图像采集 ===")
    
    try:
        # 创建Pipeline
        pipeline = Pipeline()
        print("✅ Pipeline创建成功")
        
        # 配置流
        config = Config()
        config.enable_stream(OB_STREAM_DEPTH)
        # 可选：启用彩色流
        # config.enable_stream(OB_STREAM_COLOR)
        
        # 启动Pipeline
        pipeline.start(config)
        print("✅ Pipeline启动成功")
        
        # 采集几帧数据
        for i in range(5):
            frames = pipeline.wait_for_frames(1000)
            if frames:
                depth_frame = frames.get_depth_frame()
                if depth_frame:
                    width = depth_frame.get_width()
                    height = depth_frame.get_height()
                    print(f"帧 {i+1}: 深度图像 {width}x{height}")
                else:
                    print(f"帧 {i+1}: 未获取到深度数据")
            else:
                print(f"帧 {i+1}: 未获取到帧数据")
            
            time.sleep(0.2)  # 等待200ms
        
        # 停止Pipeline
        pipeline.stop()
        print("✅ Pipeline停止成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 图像采集失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 我们自己的相机测试 ===")
    print("在test_camera_copy目录中运行")
    print("继承了完整的SDK环境配置！")
    
    # 测试1: 基础连接
    if not test_basic_connection():
        print("❌ 基础连接失败，退出测试")
        return
    
    # 测试2: 图像采集
    if not test_image_capture():
        print("❌ 图像采集失败")
        return
    
    print("\n🎉 所有测试通过！")
    print("✅ test_camera_copy环境配置完美工作！")
    print("现在你可以在这个目录中开发任何相机相关的功能了！")

if __name__ == "__main__":
    main()
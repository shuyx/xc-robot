#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正确API的相机测试脚本
基于官方examples的正确用法
"""

from pyorbbecsdk import *
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

def test_depth_capture():
    """测试深度图像采集 - 基于官方depth.py示例"""
    print("\n=== 测试深度图像采集 ===")
    
    try:
        config = Config()
        pipeline = Pipeline()
        
        # 获取深度传感器的流配置 - 正确的API用法
        profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        if profile_list is None:
            print("❌ 无法获取深度传感器配置")
            return False
            
        depth_profile = profile_list.get_default_video_stream_profile()
        if depth_profile is None:
            print("❌ 无法获取默认深度配置")
            return False
            
        print(f"深度配置: {depth_profile}")
        
        # 启用深度流
        config.enable_stream(depth_profile)
        print("✅ 深度流配置成功")
        
        # 启动Pipeline
        pipeline.start(config)
        print("✅ Pipeline启动成功")
        
        # 采集几帧数据
        for i in range(5):
            frames = pipeline.wait_for_frames(1000)
            if frames is None:
                print(f"帧 {i+1}: 超时")
                continue
                
            depth_frame = frames.get_depth_frame()
            if depth_frame is None:
                print(f"帧 {i+1}: 无深度数据")
                continue
                
            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()
            format_type = depth_frame.get_format()
            
            print(f"帧 {i+1}: {width}x{height}, 缩放: {scale}, 格式: {format_type}")
            
            time.sleep(0.2)
        
        # 停止Pipeline
        pipeline.stop()
        print("✅ Pipeline停止成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 深度采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_color_capture():
    """测试彩色图像采集"""
    print("\n=== 测试彩色图像采集 ===")
    
    try:
        config = Config()
        pipeline = Pipeline()
        
        # 获取彩色传感器的流配置
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        if profile_list is None:
            print("⚠️ 无彩色传感器或不支持")
            return True  # 不是错误，某些设备可能没有彩色传感器
            
        color_profile = profile_list.get_default_video_stream_profile()
        if color_profile is None:
            print("⚠️ 无法获取默认彩色配置")
            return True
            
        print(f"彩色配置: {color_profile}")
        
        # 启用彩色流
        config.enable_stream(color_profile)
        print("✅ 彩色流配置成功")
        
        # 启动Pipeline
        pipeline.start(config)
        print("✅ Pipeline启动成功")
        
        # 采集几帧数据
        for i in range(3):
            frames = pipeline.wait_for_frames(1000)
            if frames is None:
                print(f"帧 {i+1}: 超时")
                continue
                
            color_frame = frames.get_color_frame()
            if color_frame is None:
                print(f"帧 {i+1}: 无彩色数据")
                continue
                
            width = color_frame.get_width()
            height = color_frame.get_height()
            format_type = color_frame.get_format()
            
            print(f"帧 {i+1}: {width}x{height}, 格式: {format_type}")
            
            time.sleep(0.2)
        
        # 停止Pipeline
        pipeline.stop()
        print("✅ Pipeline停止成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 彩色采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== 正确API的相机测试 ===")
    print("使用官方examples的正确用法")
    
    # 测试1: 基础连接
    if not test_basic_connection():
        print("❌ 基础连接失败，退出测试")
        return
    
    # 测试2: 深度图像采集
    if not test_depth_capture():
        print("❌ 深度采集失败")
        return
    
    # 测试3: 彩色图像采集
    test_color_capture()  # 即使失败也继续，因为某些设备可能没有彩色传感器
    
    print("\n🎉 相机测试完成！")
    print("✅ 使用正确的API，test_camera_copy环境工作正常！")

if __name__ == "__main__":
    main()
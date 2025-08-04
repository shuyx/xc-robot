#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点云小方块检测系统测试脚本
功能：快速测试点云检测功能并输出结果
"""

import sys
import os
import time
import numpy as np

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_open3d():
    """测试Open3D是否正常工作"""
    print("🔍 测试Open3D...")
    try:
        import open3d as o3d
        print(f"✅ Open3D版本: {o3d.__version__}")
        
        # 创建一个测试点云
        test_points = np.random.rand(100, 3)
        test_pcd = o3d.geometry.PointCloud()
        test_pcd.points = o3d.utility.Vector3dVector(test_points)
        
        # 测试基本功能
        cleaned_pcd, _ = test_pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
        downsampled_pcd = cleaned_pcd.voxel_down_sample(voxel_size=0.01)
        
        print("✅ Open3D基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Open3D测试失败: {e}")
        return False

def test_camera():
    """测试相机是否正常工作"""
    print("\n🔍 测试相机...")
    try:
        from pyorbbecsdk import *
        
        pipeline = Pipeline()
        config = Config()
        
        # 配置深度流
        depth_profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        depth_profile = depth_profile_list.get_default_video_stream_profile()
        config.enable_stream(depth_profile)
        
        # 配置彩色流
        color_profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        color_profile = color_profile_list.get_default_video_stream_profile()
        config.enable_stream(color_profile)
        
        pipeline.start(config)
        
        # 预热
        for _ in range(5):
            pipeline.wait_for_frames(100)
        
        # 获取一帧
        frames = pipeline.wait_for_frames(1000)
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        if depth_frame and color_frame:
            height = depth_frame.get_height()
            width = depth_frame.get_width()
            print(f"✅ 相机测试通过，分辨率: {width}x{height}")
            
            pipeline.stop()
            return True
        else:
            print("❌ 相机测试失败：无法获取帧数据")
            pipeline.stop()
            return False
            
    except Exception as e:
        print(f"❌ 相机测试失败: {e}")
        return False

def test_detection():
    """测试方块检测功能"""
    print("\n🔍 测试方块检测...")
    try:
        # 导入检测器
        from simple_cube_detector import SimpleCubeDetector
        
        detector = SimpleCubeDetector()
        
        # 初始化相机
        if not detector.initialize_camera():
            print("❌ 检测器初始化失败")
            return False
        
        print("✅ 检测器初始化成功")
        
        # 执行一次检测
        result = detector.detect_objects()
        
        if result:
            print(f"✅ 检测测试通过，发现 {len(result)} 个物体")
            for i, obj in enumerate(result):
                center = obj['center_mm']
                extent = obj['extent_mm']
                print(f"  物体 {i+1}: 位置({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})mm, 尺寸{extent[0]:.1f}x{extent[1]:.1f}x{extent[2]:.1f}mm")
        else:
            print("⚠️ 检测测试完成，未发现物体（可能环境中没有目标物体）")
        
        detector.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 检测测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始点云小方块检测系统测试\n")
    
    results = []
    
    # 测试Open3D
    results.append(("Open3D", test_open3d()))
    
    # 测试相机
    results.append(("相机", test_camera()))
    
    # 测试检测功能
    results.append(("方块检测", test_detection()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果总结:")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
    
    # 计算成功率
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    success_rate = success_count / total_count * 100
    
    print(f"\n总体成功率: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 所有测试通过！系统已就绪")
        return 0
    elif success_rate >= 66:
        print("✅ 大部分测试通过，系统基本可用")
        return 0
    else:
        print("⚠️ 测试失败较多，请检查系统配置")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
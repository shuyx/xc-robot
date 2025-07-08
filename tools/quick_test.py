#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本
用于验证FR3机械臂分析工具的基本功能
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_stl_validation():
    """测试STL文件验证"""
    print("🔧 测试STL文件验证工具...")
    
    try:
        from tools.stl_validation import STLValidator
        
        validator = STLValidator("models")
        results = validator.validate_all_files()
        
        print("✅ STL验证工具测试成功")
        return True
        
    except Exception as e:
        print(f"❌ STL验证工具测试失败: {e}")
        return False

def test_dh_analyzer():
    """测试DH参数分析器"""
    print("\n🔧 测试DH参数分析工具...")
    
    try:
        from tools.dh_parameter_analyzer import DHParameterAnalyzer
        
        analyzer = DHParameterAnalyzer()
        
        # 测试正向运动学
        test_angles = [0, -30, 90, 0, 60, 0]
        T = analyzer.forward_kinematics(test_angles)
        pose = analyzer.extract_pose(T)
        
        print(f"  测试角度: {test_angles}")
        print(f"  末端位置: {[f'{p:.1f}' for p in pose['position']]} mm")
        
        print("✅ DH参数分析工具测试成功")
        return True
        
    except Exception as e:
        print(f"❌ DH参数分析工具测试失败: {e}")
        return False

def test_robodk_converter():
    """测试RoboDK转换器"""
    print("\n🔧 测试RoboDK转换工具...")
    
    try:
        from tools.robodk_converter import RoboDKConverter
        
        converter = RoboDKConverter()
        
        # 测试角度转换
        robot_angles = [0, -30, 90, 0, 60, 0]
        robodk_angles = converter.robot_to_robodk_angles(robot_angles)
        converted_back = converter.robodk_to_robot_angles(robodk_angles)
        
        print(f"  机器人角度: {robot_angles}")
        print(f"  RoboDK角度: {robodk_angles}")
        print(f"  转换回来: {converted_back}")
        
        # 验证转换精度
        import numpy as np
        error = np.linalg.norm(np.array(robot_angles) - np.array(converted_back))
        print(f"  转换误差: {error:.6f} °")
        
        if error < 1e-10:
            print("✅ RoboDK转换工具测试成功")
            return True
        else:
            print("❌ RoboDK转换精度不足")
            return False
        
    except Exception as e:
        print(f"❌ RoboDK转换工具测试失败: {e}")
        return False

def test_integration():
    """集成测试"""
    print("\n🔧 集成测试...")
    
    try:
        # 测试工具包导入
        from tools import STLValidator, DHParameterAnalyzer, RoboDKConverter
        
        print("  工具包导入: ✅")
        
        # 创建所有工具实例
        stl_validator = STLValidator()
        dh_analyzer = DHParameterAnalyzer()
        robodk_converter = RoboDKConverter()
        
        print("  工具实例化: ✅")
        
        # 测试DH参数一致性
        test_angles = [45, -60, 120, -30, 90, 45]
        
        # 使用分析器计算
        T1 = dh_analyzer.forward_kinematics(test_angles)
        
        # 使用转换器计算
        T2 = robodk_converter.forward_kinematics_robot(test_angles)
        
        # 比较结果
        import numpy as np
        position_diff = np.linalg.norm(T1[:3, 3] - T2[:3, 3])
        
        print(f"  运动学一致性: {position_diff:.6f} mm")
        
        if position_diff < 1e-6:
            print("✅ 集成测试成功")
            return True
        else:
            print("❌ 运动学计算不一致")
            return False
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 FR3机械臂分析工具快速测试")
    print("=" * 50)
    
    tests = [
        ("STL验证工具", test_stl_validation),
        ("DH参数分析", test_dh_analyzer), 
        ("RoboDK转换", test_robodk_converter),
        ("集成测试", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！工具包运行正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关模块")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
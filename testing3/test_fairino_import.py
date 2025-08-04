#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试fairino库导入和FR3连接
"""

import sys
import os

def test_fairino_import():
    """测试fairino模块导入"""
    
    print("=" * 50)
    print("FR3 fairino模块导入测试")
    print("=" * 50)
    
    # 显示当前路径信息
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fr3_control_path = os.path.join(project_root, 'fr3_control')
    fairino_path = os.path.join(fr3_control_path, 'fairino')
    robot_py_path = os.path.join(fairino_path, 'Robot.py')
    
    print(f"当前目录: {current_dir}")
    print(f"项目根目录: {project_root}")
    print(f"FR3控制路径: {fr3_control_path}")
    print(f"fairino路径: {fairino_path}")
    print(f"Robot.py路径: {robot_py_path}")
    
    # 检查路径是否存在
    print("\n路径检查:")
    print(f"fr3_control目录存在: {os.path.exists(fr3_control_path)}")
    print(f"fairino目录存在: {os.path.exists(fairino_path)}")
    print(f"Robot.py文件存在: {os.path.exists(robot_py_path)}")
    
    # 检查__init__.py文件
    init_py_path = os.path.join(fairino_path, '__init__.py')
    print(f"__init__.py文件存在: {os.path.exists(init_py_path)}")
    
    # 添加路径到sys.path
    print("\n添加路径到sys.path...")
    sys.path.insert(0, fr3_control_path)
    
    print("当前sys.path前5项:")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i}: {path}")
    
    # 尝试导入
    print("\n尝试导入fairino模块...")
    try:
        from fairino import Robot
        print("✅ fairino.Robot导入成功!")
        
        # 尝试创建Robot实例（不连接）
        print("✅ fairino模块可用，Robot类已导入")
        return True
        
    except ImportError as e:
        print(f"❌ fairino导入失败: {e}")
        
        # 尝试直接导入Robot.py
        print("\n尝试直接导入Robot.py...")
        try:
            sys.path.insert(0, fairino_path)
            import Robot as RobotModule
            print("✅ 直接导入Robot.py成功!")
            print("可以使用: import Robot; robot = Robot.RPC('192.168.58.2')")
            return True
        except Exception as e2:
            print(f"❌ 直接导入也失败: {e2}")
        
        return False

def test_connection():
    """测试FR3连接"""
    print("\n" + "=" * 50)
    print("FR3连接测试")
    print("=" * 50)
    
    try:
        from fairino import Robot
        
        print("正在尝试连接FR3机械臂 (192.168.58.2)...")
        robot = Robot.RPC('192.168.58.2')
        
        if robot:
            print("✅ 连接成功!")
            
            # 初始化日志
            robot.LoggerInit(output_model=0)
            robot.SetLoggerLevel(4)
            
            # 获取基本信息
            try:
                sn = robot.GetRobotSN()
                print(f"机器人SN: {sn}")
                
                state = robot.GetRobotRealTimeState()
                print(f"机器人状态: {state}")
                
            except Exception as info_e:
                print(f"获取机器人信息失败: {info_e}")
            
            print("✅ FR3机械臂连接和通讯正常!")
            return True
        else:
            print("❌ 连接失败，robot对象为None")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试...")
    
    # 测试导入
    import_success = test_fairino_import()
    
    if import_success:
        print("\n🎉 模块导入测试成功!")
        
        # 测试连接
        connection_success = test_connection()
        
        if connection_success:
            print("\n🎉 所有测试通过！可以开始使用乐白夹爪控制脚本了")
        else:
            print("\n⚠️  导入成功但连接失败，请检查:")
            print("1. FR3机械臂是否开机")
            print("2. 网络连接是否正常 (ping 192.168.58.2)")
            print("3. 机器人WebApp是否正常运行")
    else:
        print("\n❌ 模块导入失败，无法继续测试")
        print("请检查项目结构和文件路径")
    
    print("\n测试完成")
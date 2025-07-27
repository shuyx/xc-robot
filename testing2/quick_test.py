#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试FR3连接和导入
"""

import os
import sys

# 添加FR3控制模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

print("=" * 50)
print("FR3快速连接测试")
print("=" * 50)

try:
    print("正在导入fairino模块...")
    from fairino import Robot
    print("✅ fairino.Robot导入成功!")
    
    print("\n正在尝试连接FR3机械臂 (192.168.58.2)...")
    robot = Robot.RPC('192.168.58.2')
    
    if robot:
        print("✅ 连接成功!")
        
        # 简单测试
        print("\n执行简单测试...")
        try:
            robot.Mode(0)  # 设置自动模式
            print("✅ 设置自动模式成功")
            
            # 获取程序状态
            pstate = robot.GetProgramState()
            print(f"程序状态: {pstate}")
            
            robot.CloseRPC()
            print("✅ 连接已关闭")
            
        except Exception as e:
            print(f"⚠️  测试过程中出现错误: {e}")
            try:
                robot.CloseRPC()
            except:
                pass
    else:
        print("❌ 连接失败!")
        
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n请运行以下命令来解决问题:")
    print("python test_import.py")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("\n测试完成!")
input("按回车键退出...")
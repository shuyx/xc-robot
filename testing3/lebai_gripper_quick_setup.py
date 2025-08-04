#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪快速配置脚本（无需WebApp界面）

发现：乐白夹爪可以通过大寰夹爪配置代码(company=4, device=0)兼容使用！
这是基于实际测试验证的最佳配置方案。

Author: Claude
Date: 2025-07-28
"""

import sys
import os
import time

# 添加FR3控制路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr3_control_path = os.path.join(project_root, 'fr3_control')
if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

try:
    from fairino import Robot
    print("✓ 成功导入fairino.Robot")
except ImportError as e:
    print(f"✗ 导入fairino.Robot失败: {e}")
    sys.exit(1)

def quick_lebai_setup(robot_ip="192.168.58.2"):
    """
    乐白夹爪快速配置函数
    使用验证成功的配置：厂商代码4(大寰), 设备代码0
    """
    try:
        print("🤖 乐白夹爪快速配置（无需WebApp）")
        print("=" * 50)
        
        # 1. 连接机械臂
        print("1. 连接机械臂...")
        robot = Robot.RPC(robot_ip)
        print("   ✅ 连接成功")
        
        # 2. 配置夹爪（使用大寰夹爪兼容模式）
        print("2. 配置夹爪（大寰兼容模式）...")
        error = robot.SetGripperConfig(4, 0)  # 厂商=4(大寰), 设备=0
        if error == 0:
            print("   ✅ 夹爪配置成功")
        else:
            print(f"   ❌ 配置失败，错误码: {error}")
            return False
        
        time.sleep(1)
        
        # 3. 激活夹爪
        print("3. 激活夹爪...")
        
        # 3.1 复位
        error = robot.ActGripper(1, 0)
        if error == 0:
            print("   ✅ 夹爪复位成功")
        else:
            print(f"   ❌ 复位失败，错误码: {error}")
            return False
        
        time.sleep(1)
        
        # 3.2 激活
        error = robot.ActGripper(1, 1)
        if error == 0:
            print("   ✅ 夹爪激活成功")
        else:
            print(f"   ❌ 激活失败，错误码: {error}")
            return False
        
        time.sleep(2)
        
        # 4. 测试控制
        print("4. 测试夹爪控制...")
        
        test_actions = [
            ("张开", 0, 50, 30),
            ("闭合", 100, 50, 50),
            ("半开", 50, 50, 40),
            ("张开", 0, 50, 30)
        ]
        
        for action_name, pos, vel, force in test_actions:
            print(f"   {action_name}...")
            error = robot.MoveGripper(1, pos, vel, force, 5000, 0, 0, 0, 0, 0)
            if error == 0:
                print(f"      ✅ {action_name}成功")
            else:
                print(f"      ❌ {action_name}失败，错误码: {error}")
            time.sleep(2)
        
        print("\n🎉 乐白夹爪配置和测试完成！")
        print("\n📝 使用方法:")
        print("# 张开夹爪")
        print("robot.MoveGripper(1, 0, 50, 30, 5000, 0, 0, 0, 0, 0)")
        print("# 闭合夹爪") 
        print("robot.MoveGripper(1, 100, 50, 50, 5000, 0, 0, 0, 0, 0)")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False

def main():
    """主函数"""
    success = quick_lebai_setup()
    
    if success:
        print("\n✅ 配置成功！您的乐白夹爪现在可以正常使用了。")
        print("\n💡 重要发现:")
        print("乐白夹爪可以通过大寰夹爪配置代码兼容使用！")
        print("配置参数: SetGripperConfig(4, 0)")
    else:
        print("\n❌ 配置失败，请检查:")
        print("1. 机械臂网络连接是否正常")
        print("2. 24V电源是否给夹爪供电")
        print("3. 485通讯线是否正确连接")

if __name__ == "__main__":
    main()
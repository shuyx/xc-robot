#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的夹爪连接测试脚本

用于验证FR3机械臂与乐白夹爪的基本连接和配置
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

def test_robot_connection(robot_ip="192.168.58.2"):
    """测试机械臂连接"""
    try:
        print(f"🔗 尝试连接机械臂 {robot_ip}...")
        robot = Robot.RPC(robot_ip)
        print("✅ 机械臂连接成功!")
        return robot
    except Exception as e:
        print(f"❌ 机械臂连接失败: {e}")
        return None

def configure_gripper_communication(robot):
    """配置夹爪通讯"""
    try:
        print("\n⚙️ 配置夹爪通讯参数...")
        
        # 设置Modbus协议
        error = robot.SetExDevProtocol(4098)
        if error == 0:
            print("✅ Modbus协议设置成功")
        else:
            print(f"❌ Modbus协议设置失败，错误码: {error}")
            return False
        
        # 设置通讯参数 (baudRate, dataBit, stopBit, verify, timeout, timeoutTimes, period)
        # 乐白夹爪: 115200波特率, 8数据位, 1停止位, 0无校验, 3000ms超时, 3次重试, 1000ms周期
        error = robot.SetAxleCommunicationParam(115200, 8, 1, 0, 3000, 3, 1000)
        if error == 0:
            print("✅ 通讯参数配置成功 (115200, 8N1)")
        else:
            print(f"❌ 通讯参数配置失败，错误码: {error}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 配置过程出错: {e}")
        return False

def test_gripper_control(robot):
    """测试夹爪控制"""
    try:
        print("\n🧪 测试夹爪控制...")
        
        # 测试夹爪指令
        # MoveGripper(index, pos, vel, force, maxtime, block, type, rotNum, rotVel, rotTorque)
        print("发送夹爪打开指令...")
        error = robot.MoveGripper(1, 0, 50, 30, 5000, 0, 0, 0, 0, 0)  # 打开
        if error == 0:
            print("✅ 夹爪打开指令发送成功")
        else:
            print(f"❌ 夹爪打开失败，错误码: {error}")
            
        time.sleep(2)
        
        print("发送夹爪闭合指令...")
        error = robot.MoveGripper(1, 100, 50, 50, 5000, 0, 0, 0, 0, 0)  # 闭合
        if error == 0:
            print("✅ 夹爪闭合指令发送成功")
        else:
            print(f"❌ 夹爪闭合失败，错误码: {error}")
            
        time.sleep(2)
        
        print("发送夹爪中间位置指令...")
        error = robot.MoveGripper(1, 50, 50, 30, 5000, 0, 0, 0, 0, 0)  # 中间位置
        if error == 0:
            print("✅ 夹爪中间位置指令发送成功")
        else:
            print(f"❌ 夹爪中间位置失败，错误码: {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 夹爪控制测试出错: {e}")
        return False

def main():
    """主测试流程"""
    print("🤖 FR3机械臂乐白夹爪连接测试")
    print("=" * 40)
    
    # 1. 连接机械臂
    robot = test_robot_connection()
    if not robot:
        return
    
    # 2. 配置通讯
    if not configure_gripper_communication(robot):
        return
    
    # 3. 测试夹爪控制
    if not test_gripper_control(robot):
        return
    
    print("\n🎉 测试完成!")
    print("\n📝 如果看到所有 ✅ 标记，说明基本配置正确")
    print("如果夹爪没有实际动作，请检查:")
    print("1. 24V电源是否正常供电")
    print("2. 485通讯线是否正确连接")
    print("3. 是否需要在WebApp中进行额外配置")

if __name__ == "__main__":
    main()
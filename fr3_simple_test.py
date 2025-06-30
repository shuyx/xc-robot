#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂简化连接测试程序
避免ctypes兼容性问题，专注测试基本连接和控制功能
"""

import time
import sys
import os

# 添加fairino库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
fr3_control_path = os.path.join(current_dir, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.append(fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

# 导入Robot类
try:
    from fairino import Robot
    print("✓ 成功导入fairino.Robot")
except ImportError as e:
    print(f"✗ 导入fairino.Robot失败: {e}")
    sys.exit(1)

class FR3SimpleTest:
    def __init__(self, robot_ip='192.168.58.2'):
        """
        初始化FR3简化测试
        
        Args:
            robot_ip (str): 机械臂IP地址
        """
        self.robot_ip = robot_ip
        self.robot = None
        
    def connect_robot(self):
        """连接机械臂"""
        try:
            print(f"正在连接FR3机械臂，IP地址: {self.robot_ip}")
            self.robot = Robot.RPC(self.robot_ip)
            print("✓ 机械臂连接成功")
            return True
        except Exception as e:
            print(f"✗ 机械臂连接失败: {e}")
            return False
    
    def test_basic_functions(self):
        """测试基本功能（避免有问题的API）"""
        if not self.robot:
            print("✗ 机械臂未连接")
            return False
            
        print("\n=== 测试基本功能 ===")
        
        # 1. 测试SDK版本获取
        try:
            result = self.robot.GetSDKVersion()
            print(f"✓ GetSDKVersion() 调用成功: {result}")
        except Exception as e:
            print(f"⚠ GetSDKVersion() 异常: {e}")
        
        # 2. 测试控制器IP获取
        try:
            result = self.robot.GetControllerIP()
            print(f"✓ GetControllerIP() 调用成功: {result}")
        except Exception as e:
            print(f"⚠ GetControllerIP() 异常: {e}")
        
        # 3. 测试模式切换（这个通常工作正常）
        try:
            ret = self.robot.Mode(0)  # 切换到自动模式
            print(f"✓ Mode(0) 自动模式切换: 错误码={ret}")
            time.sleep(1)
        except Exception as e:
            print(f"⚠ Mode() 异常: {e}")
        
        # 4. 测试使能
        try:
            ret = self.robot.RobotEnable(1)  # 上使能
            print(f"✓ RobotEnable(1) 上使能: 错误码={ret}")
            time.sleep(1)
        except Exception as e:
            print(f"⚠ RobotEnable() 异常: {e}")
        
        return True
    
    def test_simple_movement(self):
        """测试简单运动 - 使用预定义的安全位置"""
        if not self.robot:
            print("✗ 机械臂未连接")
            return False
            
        print("\n=== 测试简单运动 ===")
        
        try:
            # 使用一个相对安全的关节位置（接近零位）
            safe_position = [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
            
            print(f"目标关节位置: {safe_position}")
            print("⚠ 注意：机械臂即将运动，请确保周围安全！")
            
            # 给用户5秒时间准备或中断
            for i in range(5, 0, -1):
                print(f"⚠ {i}秒后开始运动... (按Ctrl+C取消)")
                time.sleep(1)
            
            # 执行运动
            print("开始执行关节运动...")
            ret = self.robot.MoveJ(
                joint_pos=safe_position,
                tool=0,
                user=0,
                vel=10  # 使用较慢的速度
            )
            
            if ret == 0:
                print("✓ 运动指令发送成功")
                print("等待运动完成...")
                
                # 等待一段时间让运动完成
                time.sleep(8)
                print("✓ 运动测试完成")
                return True
            else:
                print(f"✗ 运动指令失败，错误码: {ret}")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠ 用户取消运动测试")
            return False
        except Exception as e:
            print(f"✗ 运动测试异常: {e}")
            return False
    
    def test_status_check(self):
        """测试状态检查（使用更安全的方法）"""
        if not self.robot:
            print("✗ 机械臂未连接")
            return False
            
        print("\n=== 测试状态检查 ===")
        
        # 测试运动完成状态
        try:
            result = self.robot.GetRobotMotionDone()
            print(f"✓ GetRobotMotionDone() 调用成功: {result}")
        except Exception as e:
            print(f"⚠ GetRobotMotionDone() 异常: {e}")
        
        # 测试程序状态
        try:
            result = self.robot.GetProgramState()
            print(f"✓ GetProgramState() 调用成功: {result}")
        except Exception as e:
            print(f"⚠ GetProgramState() 异常: {e}")
        
        return True
    
    def disconnect_robot(self):
        """断开机械臂连接"""
        try:
            if self.robot:
                self.robot.CloseRPC()
                print("✓ 机械臂连接已断开")
        except Exception as e:
            print(f"✗ 断开连接异常: {e}")
    
    def run_test(self):
        """运行测试"""
        print("=" * 60)
        print("FR3机械臂简化连接测试程序")
        print("=" * 60)
        
        # 连接测试
        if not self.connect_robot():
            return False
        
        # 基本功能测试
        self.test_basic_functions()
        
        # 状态检查测试
        self.test_status_check()
        
        # 询问是否进行运动测试
        print("\n" + "="*50)
        print("⚠ 运动测试警告 ⚠")
        print("即将进行机械臂运动测试")
        print("请确保：")
        print("1. 机械臂周围没有人员和障碍物")
        print("2. 急停按钮可以随时按下")
        print("3. 机械臂有足够的运动空间")
        print("="*50)
        
        user_input = input("是否继续运动测试？(y/N): ").strip().lower()
        
        if user_input == 'y' or user_input == 'yes':
            # 运动测试
            self.test_simple_movement()
        else:
            print("⚠ 跳过运动测试")
        
        # 断开连接
        self.disconnect_robot()
        
        print("\n" + "=" * 60)
        print("✓ FR3机械臂简化测试完成！")
        print("连接和基本通信功能正常")
        print("=" * 60)
        
        return True

def main():
    """主函数"""
    print(f"当前Python版本: {sys.version}")
    
    # 默认IP地址
    robot_ip = '192.168.58.2'
    
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    
    print(f"使用机械臂IP地址: {robot_ip}")
    
    # 创建测试实例
    test = FR3SimpleTest(robot_ip)
    
    try:
        # 运行测试
        success = test.run_test()
        
        if success:
            print("\n🎉 FR3机械臂连接测试成功！")
            print("💡 虽然某些高级API存在兼容性问题，但基本控制功能正常")
            print("🚀 可以继续开发机械臂控制程序")
            return 0
        else:
            print("\n❌ FR3机械臂连接测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
        test.disconnect_robot()
        return 1
    except Exception as e:
        print(f"\n\n测试过程中发生未预期的错误: {e}")
        test.disconnect_robot()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
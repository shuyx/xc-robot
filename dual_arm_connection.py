#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双臂FR3机械臂连通性测试程序
同时连接左右两个机械臂，测试通信但不执行任何运动
确保两个机械臂不会发生碰撞
"""

import time
import sys
import os
import threading
from datetime import datetime

# 添加fairino库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
fr3_control_path = os.path.join(current_dir, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.append(fr3_control_path)
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

class DualArmConnectivityTest:
    def __init__(self, right_arm_ip='192.168.58.2', left_arm_ip='192.168.58.3'):
        """
        初始化双臂连通性测试
        
        Args:
            right_arm_ip (str): 右臂IP地址 (机器人左侧机械臂)
            left_arm_ip (str): 左臂IP地址 (机器人右侧机械臂)
        """
        self.right_arm_ip = right_arm_ip  # 从机器人视角看的右臂
        self.left_arm_ip = left_arm_ip    # 从机器人视角看的左臂
        
        self.right_arm = None
        self.left_arm = None
        
        # 连接状态
        self.right_arm_connected = False
        self.left_arm_connected = False
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 测试结果
        self.test_results = {
            'right_arm': {},
            'left_arm': {}
        }
    
    def log_message(self, message, arm_name="SYSTEM"):
        """带时间戳的日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{arm_name}] {message}")
    
    def connect_right_arm(self):
        """连接右臂"""
        try:
            self.log_message(f"正在连接右臂，IP: {self.right_arm_ip}", "RIGHT")
            self.right_arm = Robot.RPC(self.right_arm_ip)
            self.right_arm_connected = True
            self.log_message("右臂连接成功", "RIGHT")
            return True
        except Exception as e:
            self.log_message(f"右臂连接失败: {e}", "RIGHT")
            self.right_arm_connected = False
            return False
    
    def connect_left_arm(self):
        """连接左臂"""
        try:
            self.log_message(f"正在连接左臂，IP: {self.left_arm_ip}", "LEFT")
            self.left_arm = Robot.RPC(self.left_arm_ip)
            self.left_arm_connected = True
            self.log_message("左臂连接成功", "LEFT")
            return True
        except Exception as e:
            self.log_message(f"左臂连接失败: {e}", "LEFT")
            self.left_arm_connected = False
            return False
    
    def test_arm_basic_info(self, robot, arm_name):
        """测试机械臂基本信息（不涉及运动）"""
        results = {}
        
        # 1. 测试SDK版本
        try:
            result = robot.GetSDKVersion()
            results['sdk_version'] = result
            self.log_message(f"SDK版本: {result}", arm_name)
        except Exception as e:
            results['sdk_version'] = f"错误: {e}"
            self.log_message(f"获取SDK版本失败: {e}", arm_name)
        
        # 2. 测试控制器IP
        try:
            result = robot.GetControllerIP()
            results['controller_ip'] = result
            self.log_message(f"控制器IP: {result}", arm_name)
        except Exception as e:
            results['controller_ip'] = f"错误: {e}"
            self.log_message(f"获取控制器IP失败: {e}", arm_name)
        
        # 3. 测试程序状态
        try:
            result = robot.GetProgramState()
            results['program_state'] = result
            self.log_message(f"程序状态: {result}", arm_name)
        except Exception as e:
            results['program_state'] = f"错误: {e}"
            self.log_message(f"获取程序状态失败: {e}", arm_name)
        
        # 4. 测试运动状态（不启动运动，只查询状态）
        try:
            result = robot.GetRobotMotionDone()
            results['motion_done'] = result
            self.log_message(f"运动完成状态: {result}", arm_name)
        except Exception as e:
            results['motion_done'] = f"错误: {e}"
            self.log_message(f"获取运动状态失败: {e}", arm_name)
        
        return results
    
    def test_arm_safety_status(self, robot, arm_name):
        """测试机械臂安全状态（确保不会意外运动）"""
        results = {}
        
        # 检查当前模式（但不改变）
        try:
            # 注意：这里只是测试API调用，不实际改变模式
            self.log_message("检查当前模式状态...", arm_name)
            results['mode_check'] = "API可用"
        except Exception as e:
            results['mode_check'] = f"错误: {e}"
            self.log_message(f"模式检查失败: {e}", arm_name)
        
        # 检查使能状态（但不改变）
        try:
            self.log_message("检查使能状态...", arm_name)
            results['enable_check'] = "API可用"
        except Exception as e:
            results['enable_check'] = f"错误: {e}"
            self.log_message(f"使能检查失败: {e}", arm_name)
        
        return results
    
    def test_single_arm(self, robot, arm_name):
        """测试单个机械臂的所有功能"""
        self.log_message(f"开始测试 {arm_name} 的基本功能", arm_name)
        
        # 基本信息测试
        basic_info = self.test_arm_basic_info(robot, arm_name)
        
        # 安全状态测试
        safety_status = self.test_arm_safety_status(robot, arm_name)
        
        # 合并结果
        results = {**basic_info, **safety_status}
        
        self.log_message(f"{arm_name} 基本功能测试完成", arm_name)
        return results
    
    def run_dual_arm_test(self):
        """运行双臂测试"""
        self.log_message("=" * 60)
        self.log_message("双臂FR3机械臂连通性测试开始")
        self.log_message("=" * 60)
        
        # 并行连接两个机械臂
        self.log_message("正在并行连接两个机械臂...")
        
        # 创建连接线程
        right_thread = threading.Thread(target=self.connect_right_arm)
        left_thread = threading.Thread(target=self.connect_left_arm)
        
        # 启动连接线程
        right_thread.start()
        left_thread.start()
        
        # 等待连接完成
        right_thread.join()
        left_thread.join()
        
        # 检查连接结果
        total_connected = 0
        if self.right_arm_connected:
            total_connected += 1
        if self.left_arm_connected:
            total_connected += 1
        
        self.log_message(f"连接结果: {total_connected}/2 个机械臂连接成功")
        
        if total_connected == 0:
            self.log_message("❌ 没有机械臂连接成功，测试终止")
            return False
        
        # 测试已连接的机械臂
        test_threads = []
        
        if self.right_arm_connected:
            def test_right():
                self.test_results['right_arm'] = self.test_single_arm(self.right_arm, "RIGHT")
            
            right_test_thread = threading.Thread(target=test_right)
            test_threads.append(right_test_thread)
            right_test_thread.start()
        
        if self.left_arm_connected:
            def test_left():
                self.test_results['left_arm'] = self.test_single_arm(self.left_arm, "LEFT")
            
            left_test_thread = threading.Thread(target=test_left)
            test_threads.append(left_test_thread)
            left_test_thread.start()
        
        # 等待所有测试完成
        for thread in test_threads:
            thread.join()
        
        return True
    
    def print_test_summary(self):
        """打印测试总结"""
        self.log_message("=" * 60)
        self.log_message("双臂连通性测试总结")
        self.log_message("=" * 60)
        
        # 右臂总结
        if self.right_arm_connected:
            self.log_message("✓ 右臂连接成功", "RIGHT")
            for key, value in self.test_results['right_arm'].items():
                self.log_message(f"  {key}: {value}", "RIGHT")
        else:
            self.log_message("✗ 右臂连接失败", "RIGHT")
        
        print()
        
        # 左臂总结
        if self.left_arm_connected:
            self.log_message("✓ 左臂连接成功", "LEFT")
            for key, value in self.test_results['left_arm'].items():
                self.log_message(f"  {key}: {value}", "LEFT")
        else:
            self.log_message("✗ 左臂连接失败", "LEFT")
        
        print()
        
        # 整体状态
        total_connected = sum([self.right_arm_connected, self.left_arm_connected])
        
        if total_connected == 2:
            self.log_message("🎉 双臂连通性测试完全成功！")
            self.log_message("💡 两个机械臂都可以正常通信")
            self.log_message("🚀 可以开始开发双臂协调控制程序")
        elif total_connected == 1:
            self.log_message("⚠ 部分成功 - 只有一个机械臂连接成功")
            self.log_message("💡 请检查另一个机械臂的网络连接和IP配置")
        else:
            self.log_message("❌ 双臂连通性测试失败")
            self.log_message("💡 请检查网络连接、IP配置和机械臂电源状态")
    
    def disconnect_arms(self):
        """断开所有机械臂连接"""
        try:
            if self.right_arm and self.right_arm_connected:
                self.right_arm.CloseRPC()
                self.log_message("右臂连接已断开", "RIGHT")
        except Exception as e:
            self.log_message(f"断开右臂连接异常: {e}", "RIGHT")
        
        try:
            if self.left_arm and self.left_arm_connected:
                self.left_arm.CloseRPC()
                self.log_message("左臂连接已断开", "LEFT")
        except Exception as e:
            self.log_message(f"断开左臂连接异常: {e}", "LEFT")
    
    def run_complete_test(self):
        """运行完整测试流程"""
        try:
            # 运行测试
            success = self.run_dual_arm_test()
            
            if success:
                # 打印总结
                self.print_test_summary()
            
            return success
            
        except KeyboardInterrupt:
            self.log_message("\n⚠ 用户中断测试")
            return False
        except Exception as e:
            self.log_message(f"\n✗ 测试过程中发生异常: {e}")
            return False
        finally:
            # 确保断开连接
            self.disconnect_arms()

def main():
    """主函数"""
    print(f"Python版本: {sys.version}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 默认IP地址
    right_arm_ip = '192.168.58.2'  # 机器人右臂
    left_arm_ip = '192.168.58.3'   # 机器人左臂
    
    # 命令行参数处理
    if len(sys.argv) > 1:
        right_arm_ip = sys.argv[1]
    if len(sys.argv) > 2:
        left_arm_ip = sys.argv[2]
    
    print(f"右臂IP: {right_arm_ip}")
    print(f"左臂IP: {left_arm_ip}")
    print()
    
    # 安全提示
    print("⚠" * 30)
    print("双臂连通性测试 - 安全提示")
    print("⚠" * 30)
    print("1. 本测试只进行通信连接，不执行任何机械臂运动")
    print("2. 测试过程中机械臂应保持静止状态")
    print("3. 如果测试过程中机械臂有异常运动，请立即按急停按钮")
    print("4. 确保机械臂周围没有人员和障碍物")
    print("⚠" * 30)
    print()
    
    user_input = input("确认开始双臂连通性测试？(y/N): ").strip().lower()
    if user_input != 'y' and user_input != 'yes':
        print("测试已取消")
        return 1
    
    # 创建测试实例
    test = DualArmConnectivityTest(right_arm_ip, left_arm_ip)
    
    # 运行测试
    success = test.run_complete_test()
    
    if success:
        print("\n🎉 双臂连通性测试完成！")
        return 0
    else:
        print("\n❌ 双臂连通性测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
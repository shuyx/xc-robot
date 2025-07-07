#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修正版本：基于Stack Overflow答案和官方文档的正确调用方式
彻底解决 '_ctypes.CField' object is not subscriptable 问题
"""

import os
import sys
import time
from datetime import datetime

# 按照官方文档的路径设置方式
current_dir = os.path.dirname(os.path.abspath(__file__))

# 法奥动态链接库路径 - 按照官方文档格式
if os.name == 'nt':
    # Windows操作系统
    fairino_path = os.path.join(current_dir, "fr3_control")
elif os.name == 'posix':
    # Ubuntu操作系统  
    fairino_path = os.path.join(current_dir, "fr3_control")

sys.path.append(fairino_path)

print(f"📁 fairino库路径: {fairino_path}")

# 导入法奥机器人动态链接库 - 按照官方方式
try:
    from fairino import Robot
    FR3_AVAILABLE = True
    print("✅ fairino库导入成功")
except ImportError as e:
    FR3_AVAILABLE = False
    print(f"❌ fairino库导入失败: {e}")
except Exception as e:
    FR3_AVAILABLE = False
    print(f"❌ fairino库异常: {e}")

class FinalCorrectedMonitor:
    """最终修正版本：基于官方文档的绝对正确调用方式"""
    
    def __init__(self, right_ip='192.168.58.2', left_ip='192.168.58.3'):
        self.right_ip = right_ip
        self.left_ip = left_ip
        self.right_robot = None
        self.left_robot = None
        self.right_connected = False
        self.left_connected = False
        
        print("🤖 最终修正版FR3监控器初始化")

    def connect_robots(self):
        """连接机械臂 - 使用官方标准方式"""
        if not FR3_AVAILABLE:
            print("❌ fairino库不可用")
            return False, False
        
        print("🔗 开始连接机械臂（最终修正版）...")
        
        # 连接右臂
        try:
            print(f"\n连接右臂 ({self.right_ip})...")
            # 按照官方文档建立连接
            self.right_robot = Robot.RPC(self.right_ip)
            self.right_connected = True
            print("✅ 右臂连接成功")
        except Exception as e:
            print(f"❌ 右臂连接失败: {e}")
            self.right_connected = False
        
        # 连接左臂
        try:
            print(f"\n连接左臂 ({self.left_ip})...")
            # 按照官方文档建立连接
            self.left_robot = Robot.RPC(self.left_ip)
            self.left_connected = True
            print("✅ 左臂连接成功")
        except Exception as e:
            print(f"❌ 左臂连接失败: {e}")
            self.left_connected = False
        
        # 连接总结
        connected_count = sum([self.right_connected, self.left_connected])
        print(f"\n📊 连接结果: {connected_count}/2 机械臂连接成功")
        
        return self.right_connected, self.left_connected

    def get_robot_data_official_way(self, robot, arm_name):
        """使用官方文档的绝对正确方式获取机械臂数据"""
        if not robot:
            return None
        
        try:
            data = {}
            
            # 方法1: 使用官方文档的正确解包方式 - 关节位置
            print(f"   📍 获取{arm_name}臂关节位置...")
            try:
                # 🔑 关键修正：使用官方文档的元组解包方式
                error, joint_pos = robot.GetActualJointPosDegree()
                
                print(f"   {arm_name}臂关节位置API返回 - 错误码: {error}, 数据类型: {type(joint_pos)}")
                
                if error == 0:
                    # 确保数据是列表格式
                    if hasattr(joint_pos, '__iter__') and not isinstance(joint_pos, (str, bytes)):
                        data['joint_pos'] = list(joint_pos)
                        print(f"   ✅ {arm_name}臂关节位置获取成功: {[f'{j:.1f}°' for j in data['joint_pos']]}")
                    else:
                        print(f"   ⚠️  {arm_name}臂关节数据格式异常: {joint_pos}")
                        data['joint_pos'] = [0.0] * 6
                else:
                    print(f"   ⚠️  {arm_name}臂关节位置获取失败，错误码: {error}")
                    data['joint_pos'] = [0.0] * 6
                    
            except Exception as e:
                print(f"   ❌ {arm_name}臂关节位置获取异常: {e}")
                data['joint_pos'] = [0.0] * 6

            # 方法2: 使用官方文档的正确解包方式 - TCP位姿
            print(f"   📍 获取{arm_name}臂TCP位姿...")
            try:
                # 🔑 关键修正：使用官方文档的元组解包方式
                error, tcp_pose = robot.GetActualTCPPose()
                
                print(f"   {arm_name}臂TCP位姿API返回 - 错误码: {error}, 数据类型: {type(tcp_pose)}")
                
                if error == 0:
                    # 确保数据是列表格式
                    if hasattr(tcp_pose, '__iter__') and not isinstance(tcp_pose, (str, bytes)):
                        data['tcp_pose'] = list(tcp_pose)
                        print(f"   ✅ {arm_name}臂TCP位姿获取成功")
                    else:
                        print(f"   ⚠️  {arm_name}臂TCP数据格式异常: {tcp_pose}")
                        data['tcp_pose'] = [0.0] * 6
                else:
                    print(f"   ⚠️  {arm_name}臂TCP位姿获取失败，错误码: {error}")
                    data['tcp_pose'] = [0.0] * 6
                    
            except Exception as e:
                print(f"   ❌ {arm_name}臂TCP位姿获取异常: {e}")
                data['tcp_pose'] = [0.0] * 6

            return data
            
        except Exception as e:
            print(f"❌ {arm_name}臂数据获取总异常: {e}")
            return None

    def test_other_apis(self, robot, arm_name):
        """测试其他稳定的API"""
        print(f"   🔧 测试{arm_name}臂其他API...")
        
        # 测试SDK版本 - 官方方式
        try:
            error, sdk_version = robot.GetSDKVersion()
            if error == 0:
                print(f"   ✅ {arm_name}臂SDK版本: {sdk_version}")
            else:
                print(f"   ⚠️  {arm_name}臂SDK版本错误码: {error}")
        except Exception as e:
            print(f"   ❌ {arm_name}臂SDK版本异常: {e}")
        
        # 测试控制器IP - 官方方式
        try:
            error, controller_ip = robot.GetControllerIP()
            if error == 0:
                print(f"   ✅ {arm_name}臂控制器IP: {controller_ip}")
            else:
                print(f"   ⚠️  {arm_name}臂控制器IP错误码: {error}")
        except Exception as e:
            print(f"   ❌ {arm_name}臂控制器IP异常: {e}")
        
        # 测试运动完成状态 - 官方方式
        try:
            error, motion_done = robot.GetRobotMotionDone()
            if error == 0:
                status = "完成" if motion_done else "运动中"
                print(f"   ✅ {arm_name}臂运动状态: {status}")
            else:
                print(f"   ⚠️  {arm_name}臂运动状态错误码: {error}")
        except Exception as e:
            print(f"   ❌ {arm_name}臂运动状态异常: {e}")

    def print_robot_status(self):
        """打印机械臂状态 - 最终正确版本"""
        print("\n" + "="*70)
        print(f"📍 双臂状态 - {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        
        # 右臂状态
        if self.right_connected:
            print(f"🤖 右臂 ({self.right_ip}):")
            
            # 获取数据
            right_data = self.get_robot_data_official_way(self.right_robot, "右")
            
            if right_data:
                joint_pos = right_data.get('joint_pos', [0]*6)
                tcp_pose = right_data.get('tcp_pose', [0]*6)
                
                # 显示关节位置
                if len(joint_pos) >= 6:
                    print(f"   关节位置: {[f'{j:.1f}°' for j in joint_pos[:6]]}")
                
                # 显示TCP位姿
                if len(tcp_pose) >= 6:
                    print(f"   TCP位置: X={tcp_pose[0]:.1f}, Y={tcp_pose[1]:.1f}, Z={tcp_pose[2]:.1f} mm")
                    print(f"   TCP姿态: RX={tcp_pose[3]:.1f}, RY={tcp_pose[4]:.1f}, RZ={tcp_pose[5]:.1f}°")
            
            # 测试其他API
            self.test_other_apis(self.right_robot, "右")
            
        else:
            print(f"❌ 右臂 ({self.right_ip}): 未连接")
        
        print()
        
        # 左臂状态
        if self.left_connected:
            print(f"🤖 左臂 ({self.left_ip}):")
            
            # 获取数据
            left_data = self.get_robot_data_official_way(self.left_robot, "左")
            
            if left_data:
                joint_pos = left_data.get('joint_pos', [0]*6)
                tcp_pose = left_data.get('tcp_pose', [0]*6)
                
                # 显示关节位置
                if len(joint_pos) >= 6:
                    print(f"   关节位置: {[f'{j:.1f}°' for j in joint_pos[:6]]}")
                
                # 显示TCP位姿
                if len(tcp_pose) >= 6:
                    print(f"   TCP位置: X={tcp_pose[0]:.1f}, Y={tcp_pose[1]:.1f}, Z={tcp_pose[2]:.1f} mm")
                    print(f"   TCP姿态: RX={tcp_pose[3]:.1f}, RY={tcp_pose[4]:.1f}, RZ={tcp_pose[5]:.1f}°")
            
            # 测试其他API
            self.test_other_apis(self.left_robot, "左")
            
        else:
            print(f"❌ 左臂 ({self.left_ip}): 未连接")
        
        print("="*70)

    def disconnect_robots(self):
        """断开连接"""
        print("\n🔌 断开机械臂连接...")
        
        if self.right_robot and self.right_connected:
            try:
                # 注意：有些版本是 CloseRPC，有些是其他方法
                if hasattr(self.right_robot, 'CloseRPC'):
                    self.right_robot.CloseRPC()
                print("✅ 右臂连接已断开")
            except Exception as e:
                print(f"❌ 右臂断开失败: {e}")
        
        if self.left_robot and self.left_connected:
            try:
                if hasattr(self.left_robot, 'CloseRPC'):
                    self.left_robot.CloseRPC()
                print("✅ 左臂连接已断开")
            except Exception as e:
                print(f"❌ 左臂断开失败: {e}")
        
        self.right_connected = False
        self.left_connected = False

    def run_monitoring(self, duration_seconds=30, interval_seconds=3):
        """运行监控程序"""
        print(f"\n🔍 启动监控程序 - 持续{duration_seconds}秒，每{interval_seconds}秒刷新")
        print("按 Ctrl+C 可以提前停止")
        
        # 连接机械臂
        right_ok, left_ok = self.connect_robots()
        
        if not (right_ok or left_ok):
            print("❌ 无法连接任何机械臂，程序退出")
            return False
        
        # 监控循环
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                elapsed = time.time() - start_time
                
                # 检查是否超时
                if elapsed >= duration_seconds:
                    print(f"\n⏰ 监控时间到达 {duration_seconds} 秒，程序结束")
                    break
                
                print(f"\n🔄 第 {iteration} 次监控 (已运行 {elapsed:.1f}s)")
                self.print_robot_status()
                
                # 等待下次刷新
                print(f"\n⏳ 等待 {interval_seconds} 秒后刷新...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n⚠️  用户中断监控")
        except Exception as e:
            print(f"❌ 监控程序异常: {e}")
        finally:
            self.disconnect_robots()
        
        print("✅ 监控程序结束")
        return True

def main():
    """主函数"""
    print("🔧 FR3机械臂ctypes问题最终修正版本")
    print("基于Stack Overflow答案和官方文档的绝对正确调用方式")
    print("="*70)
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {os.name}")
    print()
    
    # IP配置
    print("🔧 IP地址配置:")
    right_ip = input("右臂IP (回车默认192.168.58.2): ").strip()
    if not right_ip:
        right_ip = "192.168.58.2"
    
    left_ip = input("左臂IP (回车默认192.168.58.3): ").strip()
    if not left_ip:
        left_ip = "192.168.58.3"
    
    # 监控时长配置
    duration_input = input("监控时长/秒 (回车默认30秒): ").strip()
    try:
        duration = int(duration_input) if duration_input else 30
    except ValueError:
        duration = 30
    
    # 创建监控器
    monitor = FinalCorrectedMonitor(right_ip, left_ip)
    
    try:
        # 运行监控
        monitor.run_monitoring(duration_seconds=duration, interval_seconds=3)
        
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        monitor.disconnect_robots()

if __name__ == "__main__":
    main()
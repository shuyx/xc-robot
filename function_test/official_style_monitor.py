#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照法奥意威官方文档标准的调用方式
解决_ctypes.CField错误
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

class OfficialStyleMonitor:
    """按照官方文档标准的机械臂监控"""
    
    def __init__(self, right_ip='192.168.58.2', left_ip='192.168.58.3'):
        self.right_ip = right_ip
        self.left_ip = left_ip
        self.right_robot = None
        self.left_robot = None
        self.right_connected = False
        self.left_connected = False
        
        print("🤖 官方标准调用方式监控器初始化")

    def safe_robot_call(self, robot, method_name, *args, **kwargs):
        """安全的机械臂API调用，处理ctypes兼容性问题"""
        try:
            method = getattr(robot, method_name)
            result = method(*args, **kwargs)
            
            # 检查返回结果是否为元组并且长度足够
            if isinstance(result, tuple) and len(result) >= 2:
                error_code = int(result[0])
                data = result[1]
                
                # 确保数据部分是列表
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    # 转换为浮点数列表，增加鲁棒性
                    try:
                        data = [float(x) for x in data]
                    except (ValueError, TypeError):
                        data = list(data)
                
                return error_code, data
            else:
                # 如果不是预期的元组格式，也尝试作为成功结果返回
                # 这可以处理那些只返回一个值的API
                return 0, result

        except Exception as e:
            print(f"⚠️  API调用 {method_name} 失败: {e}")
            return -1, None
    
    def test_basic_connection(self, robot, ip, arm_name):
        """测试基本连接 - 按照官方示例"""
        try:
            print(f"测试{arm_name}臂基本连接...")
            
            # 1. 测试RPC连接状态
            if hasattr(robot, 'is_conect'):
                if robot.is_conect:
                    print(f"   ✅ {arm_name}臂RPC连接成功")
                else:
                    print(f"   ❌ {arm_name}臂RPC连接失败")
                    return False
            
            # 2. 获取SDK版本 - 官方测试方法
            try:
                error, sdk = robot.GetSDKVersion()
                if error == 0:
                    print(f"   ✅ {arm_name}臂SDK版本: {sdk}")
                else:
                    print(f"   ⚠️  {arm_name}臂SDK版本获取错误: {error}")
            except Exception as e:
                print(f"   ⚠️  {arm_name}臂SDK版本获取异常: {e}")
            
            # 3. 获取控制器IP - 官方测试方法
            try:
                error, controller_ip = robot.GetControllerIP()
                if error == 0:
                    print(f"   ✅ {arm_name}臂控制器IP: {controller_ip}")
                else:
                    print(f"   ⚠️  {arm_name}臂控制器IP获取错误: {error}")
            except Exception as e:
                print(f"   ⚠️  {arm_name}臂控制器IP获取异常: {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ {arm_name}臂基本连接测试失败: {e}")
            return False
    
    def connect_robots(self):
        """连接机械臂 - 使用官方标准方式"""
        if not FR3_AVAILABLE:
            print("❌ fairino库不可用")
            return False, False
        
        print("🔗 开始连接机械臂（官方标准方式）...")
        
        # 连接右臂
        try:
            print(f"\n连接右臂 ({self.right_ip})...")
            # 按照官方文档建立连接
            self.right_robot = Robot.RPC(self.right_ip)
            
            if self.test_basic_connection(self.right_robot, self.right_ip, "右"):
                self.right_connected = True
                print("✅ 右臂连接验证成功")
            else:
                self.right_connected = False
                
        except Exception as e:
            print(f"❌ 右臂连接失败: {e}")
            self.right_connected = False
        
        # 连接左臂
        try:
            print(f"\n连接左臂 ({self.left_ip})...")
            # 按照官方文档建立连接
            self.left_robot = Robot.RPC(self.left_ip)
            
            if self.test_basic_connection(self.left_robot, self.left_ip, "左"):
                self.left_connected = True
                print("✅ 左臂连接验证成功")
            else:
                self.left_connected = False
                
        except Exception as e:
            print(f"❌ 左臂连接失败: {e}")
            self.left_connected = False
        
        # 连接总结
        connected_count = sum([self.right_connected, self.left_connected])
        print(f"\n📊 连接结果: {connected_count}/2 机械臂连接成功")
        
        return self.right_connected, self.left_connected
    
    # def get_robot_data_safe(self, robot, arm_name):
    #     """安全获取机械臂数据 - 处理ctypes问题"""
    #     if not robot:
    #         return None
        
    #     try:
    #         data = {}
            
    #         # 方法1: 尝试直接调用（官方方式）
    #         try:
    #             error = robot.GetActualJointPosDegree()
    #             print(f"   {arm_name}臂GetActualJointPosDegree返回类型: {type(error)}")
    #             print(f"   {arm_name}臂GetActualJointPosDegree内容: {error}")
                
    #             # 检查返回值结构
    #             if hasattr(error, '__len__') and len(error) >= 2:
    #                 error_code = error[0]
    #                 joint_data = error[1]
    #                 print(f"   {arm_name}臂解析 - 错误码: {error_code}, 数据: {joint_data}")
                    
    #                 if error_code == 0:
    #                     data['joint_pos'] = list(joint_data) if joint_data else [0.0]*6
    #                 else:
    #                     print(f"   ⚠️  {arm_name}臂关节位置错误码: {error_code}")
    #                     data['joint_pos'] = [0.0] * 6
    #             else:
    #                 print(f"   ⚠️  {arm_name}臂返回值格式异常")
    #                 data['joint_pos'] = [0.0] * 6
                    
    #         except Exception as e:
    #             print(f"   ❌ {arm_name}臂关节位置获取异常: {e}")
    #             data['joint_pos'] = [0.0] * 6
            
    #         # 方法2: 获取TCP位姿
    #         try:
    #             tcp_result = robot.GetActualTCPPose()
    #             print(f"   {arm_name}臂GetActualTCPPose返回类型: {type(tcp_result)}")
                
    #             if hasattr(tcp_result, '__len__') and len(tcp_result) >= 2:
    #                 error_code = tcp_result[0]
    #                 tcp_data = tcp_result[1]
                    
    #                 if error_code == 0:
    #                     data['tcp_pose'] = list(tcp_data) if tcp_data else [0.0]*6
    #                 else:
    #                     print(f"   ⚠️  {arm_name}臂TCP位姿错误码: {error_code}")
    #                     data['tcp_pose'] = [0.0] * 6
    #             else:
    #                 print(f"   ⚠️  {arm_name}臂TCP返回值格式异常")
    #                 data['tcp_pose'] = [0.0] * 6
                    
    #         except Exception as e:
    #             print(f"   ❌ {arm_name}臂TCP位姿获取异常: {e}")
    #             data['tcp_pose'] = [0.0] * 6
            
    #         return data
            
    #     except Exception as e:
    #         print(f"❌ {arm_name}臂数据获取总异常: {e}")
    #         return None

    def get_robot_data_safe(self, robot, arm_name):
        """安全获取机械臂数据 - 使用安全调用适配器"""
        if not robot:
            return None
        
        try:
            data = {}
            
            # 使用安全适配器获取关节位置
            error_code, joint_pos = self.safe_robot_call(robot, 'GetActualJointPosDegree')
            if error_code == 0 and joint_pos is not None:
                data['joint_pos'] = list(joint_pos)
            else:
                print(f"   ⚠️  {arm_name}臂关节位置获取失败，错误码: {error_code}")
                data['joint_pos'] = [0.0] * 6
            
            # 使用安全适配器获取TCP位姿
            error_code, tcp_pose = self.safe_robot_call(robot, 'GetActualTCPPose')
            if error_code == 0 and tcp_pose is not None:
                data['tcp_pose'] = list(tcp_pose)
            else:
                print(f"   ⚠️  {arm_name}臂TCP位姿获取失败，错误码: {error_code}")
                data['tcp_pose'] = [0.0] * 6
                
            return data
            
        except Exception as e:
            print(f"❌ {arm_name}臂数据获取总异常: {e}")
            return None
    
    def print_robot_status(self):
        """打印机械臂状态"""
        print("\n" + "="*70)
        print(f"📍 双臂状态 - {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        
        # 右臂状态
        if self.right_connected:
            print(f"🤖 右臂 ({self.right_ip}):")
            right_data = self.get_robot_data_safe(self.right_robot, "右")
            if right_data:
                joint_pos = right_data.get('joint_pos', [0]*6)
                tcp_pose = right_data.get('tcp_pose', [0]*6)
                
                print(f"   关节位置: {[f'{j:.1f}°' for j in joint_pos[:6]]}")
                if len(tcp_pose) >= 6:
                    print(f"   TCP位置: X={tcp_pose[0]:.1f}, Y={tcp_pose[1]:.1f}, Z={tcp_pose[2]:.1f} mm")
                    print(f"   TCP姿态: RX={tcp_pose[3]:.1f}, RY={tcp_pose[4]:.1f}, RZ={tcp_pose[5]:.1f}°")
        else:
            print(f"❌ 右臂 ({self.right_ip}): 未连接")
        
        print()
        
        # 左臂状态
        if self.left_connected:
            print(f"🤖 左臂 ({self.left_ip}):")
            left_data = self.get_robot_data_safe(self.left_robot, "左")
            if left_data:
                joint_pos = left_data.get('joint_pos', [0]*6)
                tcp_pose = left_data.get('tcp_pose', [0]*6)
                
                print(f"   关节位置: {[f'{j:.1f}°' for j in joint_pos[:6]]}")
                if len(tcp_pose) >= 6:
                    print(f"   TCP位置: X={tcp_pose[0]:.1f}, Y={tcp_pose[1]:.1f}, Z={tcp_pose[2]:.1f} mm")
                    print(f"   TCP姿态: RX={tcp_pose[3]:.1f}, RY={tcp_pose[4]:.1f}, RZ={tcp_pose[5]:.1f}°")
        else:
            print(f"❌ 左臂 ({self.left_ip}): 未连接")
        
        print("="*70)
    
    def test_robot_enable_mode(self, robot, arm_name):
        """测试机械臂使能和模式 - 按照官方示例"""
        if not robot:
            return False
        
        try:
            print(f"\n🔧 测试{arm_name}臂使能和模式设置...")
            
            # 1. 设置自动模式 - 官方示例
            print(f"   设置{arm_name}臂为自动模式...")
            mode_result = robot.Mode(state=0)  # 0-自动模式
            print(f"   {arm_name}臂自动模式设置结果: {mode_result}")
            
            time.sleep(1)
            
            # 2. 上使能 - 官方示例
            print(f"   {arm_name}臂上使能...")
            enable_result = robot.RobotEnable(state=1)  # 1-上使能
            print(f"   {arm_name}臂使能结果: {enable_result}")
            
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"   ❌ {arm_name}臂使能模式测试失败: {e}")
            return False
    
    def disconnect_robots(self):
        """断开连接"""
        print("\n🔌 断开机械臂连接...")
        
        if self.right_robot and self.right_connected:
            try:
                self.right_robot.CloseRPC()
                print("✅ 右臂连接已断开")
            except Exception as e:
                print(f"❌ 右臂断开失败: {e}")
        
        if self.left_robot and self.left_connected:
            try:
                self.left_robot.CloseRPC()
                print("✅ 左臂连接已断开")
            except Exception as e:
                print(f"❌ 左臂断开失败: {e}")
        
        self.right_connected = False
        self.left_connected = False
    
    def run_diagnostic_test(self):
        """运行诊断测试"""
        print("\n🧪 官方标准调用方式诊断测试")
        print("="*60)
        
        # 1. 连接测试
        right_ok, left_ok = self.connect_robots()
        
        if not (right_ok or left_ok):
            print("❌ 无法连接任何机械臂")
            return False
        
        # 2. 数据获取测试
        print("\n📊 数据获取测试:")
        for i in range(3):
            print(f"\n--- 第{i+1}次测试 ---")
            self.print_robot_status()
            if i < 2:
                time.sleep(2)
        
        # 3. 使能模式测试（可选）
        test_enable = input("\n是否测试使能和模式设置? (y/N): ").strip().lower()
        if test_enable == 'y':
            if self.right_connected:
                self.test_robot_enable_mode(self.right_robot, "右")
            if self.left_connected:
                self.test_robot_enable_mode(self.left_robot, "左")
        
        # 4. 断开连接
        self.disconnect_robots()
        
        print("\n✅ 诊断测试完成")
        return True

def main():
    """主函数"""
    print("🔧 法奥意威FR3官方标准调用方式测试")
    print("解决 _ctypes.CField 兼容性问题")
    print("="*60)
    
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
    
    # 创建监控器
    monitor = OfficialStyleMonitor(right_ip, left_ip)
    
    try:
        # 运行诊断测试
        monitor.run_diagnostic_test()
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        monitor.disconnect_robots()
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        monitor.disconnect_robots()

if __name__ == "__main__":
    main()
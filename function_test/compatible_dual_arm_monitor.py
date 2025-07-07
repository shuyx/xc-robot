#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兼容性双臂监控工具
解决'_ctypes.CField' object is not subscriptable错误
"""

import sys
import os
import time
import json
import math
from datetime import datetime

# 添加fr3_control路径到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
fr3_control_path = os.path.join(current_dir, 'fr3_control')
sys.path.insert(0, fr3_control_path)

print(f"📁 当前目录: {current_dir}")
print(f"📁 FR3控制路径: {fr3_control_path}")

# 导入FR3库 - 使用更安全的方式
try:
    from fairino import Robot
    FR3_AVAILABLE = True
    print("✅ FR3库导入成功")
except ImportError as e:
    FR3_AVAILABLE = False
    print(f"❌ FR3库导入失败: {e}")
except Exception as e:
    FR3_AVAILABLE = False
    print(f"❌ FR3库导入异常: {e}")

class SafeDualArmMonitor:
    """兼容性双臂监控器 - 处理ctypes兼容性问题"""
    
    def __init__(self, right_ip: str = "192.168.58.2", left_ip: str = "192.168.58.3"):
        self.right_ip = right_ip
        self.left_ip = left_ip
        
        # 机械臂连接
        self.right_arm = None
        self.left_arm = None
        self.right_connected = False
        self.left_connected = False
        
        print("🤖 兼容性双臂监控器初始化完成")
    
    def safe_robot_call(self, robot, method_name, *args, **kwargs):
        """安全的机械臂API调用，处理ctypes兼容性问题"""
        try:
            method = getattr(robot, method_name)
            result = method(*args, **kwargs)
            
            # 处理可能的ctypes返回值问题
            if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                # 如果是可迭代的，尝试转换为列表
                try:
                    if len(result) == 2:  # (error_code, data) 格式
                        error_code = int(result[0]) if hasattr(result[0], '__int__') else result[0]
                        data = result[1]
                        
                        # 处理数据部分
                        if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                            try:
                                data = [float(x) if hasattr(x, '__float__') else x for x in data]
                            except:
                                data = list(data) if data else []
                        
                        return error_code, data
                    else:
                        # 单一返回值
                        return result
                except (TypeError, IndexError):
                    return result
            else:
                return result
                
        except Exception as e:
            print(f"⚠️  API调用 {method_name} 失败: {e}")
            return -1, None
    
    def connect_arms(self):
        """连接双臂机械臂 - 使用安全调用方式"""
        if not FR3_AVAILABLE:
            print("❌ FR3库不可用，无法连接机械臂")
            return False, False
        
        print("🔗 开始连接机械臂...")
        
        # 连接右臂
        try:
            print(f"连接右臂 ({self.right_ip})...")
            self.right_arm = Robot.RPC(self.right_ip)
            
            # 使用安全调用测试连接
            error, data = self.safe_robot_call(self.right_arm, 'GetActualJointPosDegree')
            
            if error == 0 and data is not None:
                self.right_connected = True
                print("✅ 右臂连接成功")
                print(f"   测试数据: {data[:3] if len(data) >= 3 else data}...")
            else:
                print(f"❌ 右臂响应错误，错误码: {error}")
                self.right_connected = False
                
        except Exception as e:
            print(f"❌ 右臂连接失败: {e}")
            self.right_connected = False
        
        # 连接左臂
        try:
            print(f"连接左臂 ({self.left_ip})...")
            self.left_arm = Robot.RPC(self.left_ip)
            
            # 使用安全调用测试连接
            error, data = self.safe_robot_call(self.left_arm, 'GetActualJointPosDegree')
            
            if error == 0 and data is not None:
                self.left_connected = True
                print("✅ 左臂连接成功")
                print(f"   测试数据: {data[:3] if len(data) >= 3 else data}...")
            else:
                print(f"❌ 左臂响应错误，错误码: {error}")
                self.left_connected = False
                
        except Exception as e:
            print(f"❌ 左臂连接失败: {e}")
            self.left_connected = False
        
        # 连接总结
        connected_count = sum([self.right_connected, self.left_connected])
        print(f"\n📊 连接结果: {connected_count}/2 机械臂连接成功")
        
        if self.right_connected:
            print(f"   ✅ 右臂: {self.right_ip}")
        if self.left_connected:
            print(f"   ✅ 左臂: {self.left_ip}")
        
        return self.right_connected, self.left_connected
    
    def get_arm_data(self, robot, arm_name: str):
        """获取单个机械臂数据 - 使用安全调用"""
        if not robot:
            return None
        
        try:
            data = {}
            
            # 获取关节位置
            error, joint_pos = self.safe_robot_call(robot, 'GetActualJointPosDegree')
            if error == 0 and joint_pos is not None:
                # 确保是6个关节的数据
                if len(joint_pos) >= 6:
                    data['joint_pos'] = joint_pos[:6]
                else:
                    data['joint_pos'] = joint_pos + [0.0] * (6 - len(joint_pos))
            else:
                print(f"⚠️  {arm_name}臂关节位置获取失败，错误码: {error}")
                data['joint_pos'] = [0.0] * 6
            
            # 获取TCP位姿
            error, tcp_pose = self.safe_robot_call(robot, 'GetActualTCPPose')
            if error == 0 and tcp_pose is not None:
                # 确保是6个自由度的数据
                if len(tcp_pose) >= 6:
                    data['tcp_pose'] = tcp_pose[:6]
                else:
                    data['tcp_pose'] = tcp_pose + [0.0] * (6 - len(tcp_pose))
            else:
                print(f"⚠️  {arm_name}臂TCP位姿获取失败，错误码: {error}")
                data['tcp_pose'] = [0.0] * 6
            
            # 获取关节速度（可选）
            try:
                error, joint_speeds = self.safe_robot_call(robot, 'GetActualJointSpeedsDegree')
                if error == 0 and joint_speeds is not None:
                    if len(joint_speeds) >= 6:
                        data['joint_speeds'] = joint_speeds[:6]
                        data['is_moving'] = any(abs(speed) > 0.1 for speed in joint_speeds[:6])
                    else:
                        data['joint_speeds'] = joint_speeds + [0.0] * (6 - len(joint_speeds))
                        data['is_moving'] = any(abs(speed) > 0.1 for speed in data['joint_speeds'])
                else:
                    data['joint_speeds'] = [0.0] * 6
                    data['is_moving'] = False
            except:
                # 如果速度获取失败，设为静止状态
                data['joint_speeds'] = [0.0] * 6
                data['is_moving'] = False
            
            return data
            
        except Exception as e:
            print(f"❌ 获取{arm_name}臂数据异常: {e}")
            return None
    
    def calculate_distance(self, pos1, pos2):
        """计算两点间距离"""
        if not pos1 or not pos2 or len(pos1) < 3 or len(pos2) < 3:
            return float('inf')
        
        try:
            dx = float(pos1[0]) - float(pos2[0])
            dy = float(pos1[1]) - float(pos2[1])
            dz = float(pos1[2]) - float(pos2[2])
            
            return math.sqrt(dx*dx + dy*dy + dz*dz)
        except (ValueError, TypeError):
            return float('inf')
    
    def print_current_status(self):
        """打印当前状态"""
        print("\n" + "="*70)
        print(f"📍 双臂实时状态 - {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        
        # 获取数据
        right_data = None
        left_data = None
        
        if self.right_connected:
            right_data = self.get_arm_data(self.right_arm, "右")
        
        if self.left_connected:
            left_data = self.get_arm_data(self.left_arm, "左")
        
        # 显示右臂状态
        if right_data and right_data.get('joint_pos'):
            print(f"🤖 右臂 ({self.right_ip}):")
            try:
                joint_str = [f'{float(j):.1f}°' for j in right_data['joint_pos']]
                print(f"   关节位置: {joint_str}")
                
                tcp = right_data['tcp_pose']
                print(f"   TCP位置:  X={float(tcp[0]):.1f}, Y={float(tcp[1]):.1f}, Z={float(tcp[2]):.1f} mm")
                print(f"   TCP姿态:  RX={float(tcp[3]):.1f}, RY={float(tcp[4]):.1f}, RZ={float(tcp[5]):.1f}°")
                print(f"   运动状态: {'🟢 运动中' if right_data.get('is_moving', False) else '⚪ 静止'}")
            except (ValueError, TypeError, IndexError) as e:
                print(f"   ⚠️  数据格式错误: {e}")
        else:
            print(f"❌ 右臂 ({self.right_ip}): 无数据")
        
        print()
        
        # 显示左臂状态
        if left_data and left_data.get('joint_pos'):
            print(f"🤖 左臂 ({self.left_ip}):")
            try:
                joint_str = [f'{float(j):.1f}°' for j in left_data['joint_pos']]
                print(f"   关节位置: {joint_str}")
                
                tcp = left_data['tcp_pose']
                print(f"   TCP位置:  X={float(tcp[0]):.1f}, Y={float(tcp[1]):.1f}, Z={float(tcp[2]):.1f} mm")
                print(f"   TCP姿态:  RX={float(tcp[3]):.1f}, RY={float(tcp[4]):.1f}, RZ={float(tcp[5]):.1f}°")
                print(f"   运动状态: {'🟢 运动中' if left_data.get('is_moving', False) else '⚪ 静止'}")
            except (ValueError, TypeError, IndexError) as e:
                print(f"   ⚠️  数据格式错误: {e}")
        else:
            print(f"❌ 左臂 ({self.left_ip}): 无数据")
        
        # 显示双臂关系
        if (right_data and right_data.get('tcp_pose') and 
            left_data and left_data.get('tcp_pose')):
            try:
                distance = self.calculate_distance(right_data['tcp_pose'], left_data['tcp_pose'])
                print(f"\n🔗 双臂关系:")
                print(f"   TCP间距离: {distance:.1f} mm")
                
                # 安全评估
                if distance < 200:
                    print(f"   ⚠️  【危险】距离过近! 建议立即停止运动")
                elif distance < 300:
                    print(f"   ⚡ 【警告】距离较近，请注意安全")
                else:
                    print(f"   ✅ 【安全】距离正常")
            except Exception as e:
                print(f"   ⚠️  距离计算错误: {e}")
        
        print("="*70)
    
    def record_calibration_point(self):
        """记录一个标定点"""
        if not (self.right_connected and self.left_connected):
            print("❌ 需要双臂都连接才能记录标定点")
            return None
        
        right_data = self.get_arm_data(self.right_arm, "右")
        left_data = self.get_arm_data(self.left_arm, "左")
        
        if (right_data and right_data.get('tcp_pose') and 
            left_data and left_data.get('tcp_pose')):
            try:
                point = {
                    "timestamp": datetime.now().isoformat(),
                    "right_tcp": [float(x) for x in right_data['tcp_pose'][:3]],
                    "left_tcp": [float(x) for x in left_data['tcp_pose'][:3]]
                }
                
                print(f"✅ 标定点已记录:")
                print(f"   右臂位置: {point['right_tcp']}")
                print(f"   左臂位置: {point['left_tcp']}")
                
                return point
            except (ValueError, TypeError) as e:
                print(f"❌ 数据转换错误: {e}")
                return None
        else:
            print("❌ 无法获取位置数据")
            return None
    
    def disconnect_arms(self):
        """断开连接"""
        print("🔌 断开机械臂连接...")
        
        if self.right_arm and self.right_connected:
            try:
                self.right_arm.CloseRPC()
                print("✅ 右臂连接已断开")
            except Exception as e:
                print(f"❌ 断开右臂失败: {e}")
        
        if self.left_arm and self.left_connected:
            try:
                self.left_arm.CloseRPC()
                print("✅ 左臂连接已断开")
            except Exception as e:
                print(f"❌ 断开左臂失败: {e}")
        
        self.right_connected = False
        self.left_connected = False
    
    def test_connection_only(self):
        """仅测试连接，不进入主循环"""
        print("\n🧪 连接测试模式")
        print("="*50)
        
        # 连接测试
        right_ok, left_ok = self.connect_arms()
        
        if not (right_ok or left_ok):
            print("❌ 无法连接任何机械臂")
            return
        
        # 数据获取测试
        print("\n📊 数据获取测试:")
        for i in range(3):
            print(f"\n第 {i+1} 次测试:")
            self.print_current_status()
            if i < 2:
                time.sleep(2)
        
        # 断开连接
        self.disconnect_arms()
        print("\n✅ 连接测试完成")
    
    def run(self):
        """运行监控程序"""
        print("\n" + "="*70)
        print("🤖 兼容性双臂实时监控工具")
        print("="*70)
        
        # 先提供测试选项
        print("请选择运行模式:")
        print("1. 完整功能模式")
        print("2. 仅连接测试")
        
        try:
            mode = input("请选择 (1-2): ").strip()
        except KeyboardInterrupt:
            print("\n⚠️  用户中断")
            return
        
        if mode == "2":
            self.test_connection_only()
            return
        
        # 连接机械臂
        right_ok, left_ok = self.connect_arms()
        
        if not (right_ok or left_ok):
            print("❌ 无法连接任何机械臂，程序退出")
            return
        
        try:
            while True:
                print("\n" + "="*50)
                print("📋 主菜单")
                print("="*50)
                print("1. 查看当前状态")
                print("2. 连续监控（按Ctrl+C停止）")
                print("3. 退出程序")
                
                try:
                    choice = input("\n请选择操作 (1-3): ").strip()
                except KeyboardInterrupt:
                    print("\n⚠️  用户中断")
                    break
                
                if choice == "1":
                    self.print_current_status()
                
                elif choice == "2":
                    print("🔄 开始连续监控，按 Ctrl+C 停止...")
                    try:
                        while True:
                            self.print_current_status()
                            time.sleep(3)  # 每3秒更新一次，避免过于频繁
                    except KeyboardInterrupt:
                        print("\n⏹️  连续监控已停止")
                
                elif choice == "3":
                    print("👋 程序退出")
                    break
                
                else:
                    print("❌ 无效选择，请重新输入")
        
        except Exception as e:
            print(f"❌ 程序异常: {e}")
        
        finally:
            self.disconnect_arms()

def main():
    """主函数"""
    print("🔧 兼容性双臂监控工具启动")
    print("解决 '_ctypes.CField' 兼容性问题")
    
    # IP地址配置
    print("\n🔧 IP地址配置:")
    print("   默认右臂IP: 192.168.58.2")
    print("   默认左臂IP: 192.168.58.3")
    
    try:
        change_ip = input("是否需要修改IP地址? (y/N): ").strip().lower()
        
        if change_ip == 'y':
            right_ip = input("请输入右臂IP (回车使用默认): ").strip()
            if not right_ip:
                right_ip = "192.168.58.2"
            
            left_ip = input("请输入左臂IP (回车使用默认): ").strip()
            if not left_ip:
                left_ip = "192.168.58.3"
            
            monitor = SafeDualArmMonitor(right_ip, left_ip)
        else:
            monitor = SafeDualArmMonitor()
        
        # 运行监控程序
        monitor.run()
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断，程序退出")
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")

if __name__ == "__main__":
    main()
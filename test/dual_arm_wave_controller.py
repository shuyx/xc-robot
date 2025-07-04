#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双臂机械臂调试测试程序
专门用于调试 ctypes 错误和同步问题
"""

import time
import sys
import os
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
    import Robot
    print("✓ 成功导入fairino.Robot")
except ImportError as e:
    print(f"✗ 导入fairino.Robot失败: {e}")
    sys.exit(1)

class DualArmDebugTest:
    def __init__(self, right_arm_ip='192.168.58.2', left_arm_ip='192.168.58.3'):
        """调试测试初始化"""
        self.right_arm_ip = right_arm_ip
        self.left_arm_ip = left_arm_ip
        self.right_arm = None
        self.left_arm = None
        self.right_connected = False
        self.left_connected = False

    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")

    def safe_get_data(self, result, data_name="数据"):
        """安全获取数据的调试版本"""
        self.log(f"开始解析{data_name}...")
        self.log(f"原始结果类型: {type(result)}")
        self.log(f"原始结果内容: {result}")
        
        try:
            # 检查是否为None
            if result is None:
                self.log("结果为None", "ERROR")
                return None
            
            # 检查是否为元组
            if isinstance(result, tuple):
                self.log(f"结果是元组，长度: {len(result)}")
                
                if len(result) >= 2:
                    error_code = result[0]
                    data = result[1]
                    
                    self.log(f"错误码: {error_code}")
                    self.log(f"数据类型: {type(data)}")
                    self.log(f"数据内容: {data}")
                    
                    if error_code != 0:
                        self.log(f"API返回错误码: {error_code}", "ERROR")
                        return None
                    
                    # 尝试不同的数据提取方式
                    if data is None:
                        self.log("数据为None", "ERROR")
                        return None
                    
                    # 方式1：直接索引
                    try:
                        if hasattr(data, '__len__') and len(data) >= 6:
                            pose = [float(data[i]) for i in range(6)]
                            self.log(f"方式1成功: {pose}")
                            return pose
                    except Exception as e:
                        self.log(f"方式1失败: {e}")
                    
                    # 方式2：检查ctypes特殊属性
                    try:
                        self.log(f"检查数据属性: {dir(data)}")
                        
                        if hasattr(data, '__getitem__'):
                            pose = []
                            for i in range(6):
                                value = data[i]
                                self.log(f"索引{i}: {value} (类型: {type(value)})")
                                pose.append(float(value))
                            self.log(f"方式2成功: {pose}")
                            return pose
                    except Exception as e:
                        self.log(f"方式2失败: {e}")
                    
                    # 方式3：其他尝试
                    try:
                        if hasattr(data, 'contents'):
                            actual_data = data.contents
                            self.log(f"contents属性: {actual_data}")
                            if hasattr(actual_data, '__len__'):
                                pose = [float(actual_data[i]) for i in range(6)]
                                self.log(f"方式3成功: {pose}")
                                return pose
                    except Exception as e:
                        self.log(f"方式3失败: {e}")
                
            # 直接是数组的情况
            elif hasattr(result, '__len__') and len(result) >= 6:
                try:
                    pose = [float(result[i]) for i in range(6)]
                    self.log(f"直接数组成功: {pose}")
                    return pose
                except Exception as e:
                    self.log(f"直接数组失败: {e}")
            
            self.log("所有数据提取方式都失败", "ERROR")
            return None
            
        except Exception as e:
            self.log(f"数据解析异常: {e}", "ERROR")
            return None

    def test_connection(self):
        """测试连接"""
        self.log("开始测试双臂连接...")
        
        # 测试右臂连接
        try:
            self.log("连接右臂...")
            self.right_arm = Robot.RPC(self.right_arm_ip)
            self.right_connected = True
            self.log("✓ 右臂连接成功")
        except Exception as e:
            self.log(f"✗ 右臂连接失败: {e}", "ERROR")
            return False
        
        # 测试左臂连接
        try:
            self.log("连接左臂...")
            self.left_arm = Robot.RPC(self.left_arm_ip)
            self.left_connected = True
            self.log("✓ 左臂连接成功")
        except Exception as e:
            self.log(f"✗ 左臂连接失败: {e}", "ERROR")
            return False
        
        return True

    def test_basic_info(self):
        """测试基本信息获取"""
        self.log("=" * 50)
        self.log("测试基本信息获取")
        self.log("=" * 50)
        
        robots = []
        if self.right_connected:
            robots.append((self.right_arm, "RIGHT"))
        if self.left_connected:
            robots.append((self.left_arm, "LEFT"))
        
        for robot, name in robots:
            self.log(f"测试{name}臂基本信息...")
            
            # 测试SDK版本
            try:
                result = robot.GetSDKVersion()
                self.log(f"{name}臂SDK版本结果: {result}")
            except Exception as e:
                self.log(f"{name}臂SDK版本获取失败: {e}", "ERROR")
            
            # 测试控制器IP
            try:
                result = robot.GetControllerIP()
                self.log(f"{name}臂控制器IP结果: {result}")
            except Exception as e:
                self.log(f"{name}臂控制器IP获取失败: {e}", "ERROR")

    def test_pose_methods(self):
        """测试各种位姿获取方法"""
        self.log("=" * 50)
        self.log("测试位姿获取方法")
        self.log("=" * 50)
        
        robots = []
        if self.right_connected:
            robots.append((self.right_arm, "RIGHT"))
        if self.left_connected:
            robots.append((self.left_arm, "LEFT"))
        
        for robot, name in robots:
            self.log(f"测试{name}臂位姿获取...")
            
            # 方法1：GetActualTCPPose
            self.log(f"--- {name}臂 GetActualTCPPose ---")
            try:
                result = robot.GetActualTCPPose()
                pose = self.safe_get_data(result, f"{name}臂TCP位姿")
                if pose:
                    self.log(f"✓ {name}臂TCP位姿: {pose}")
                else:
                    self.log(f"✗ {name}臂TCP位姿获取失败")
            except Exception as e:
                self.log(f"✗ {name}臂TCP位姿异常: {e}", "ERROR")
            
            # 方法2：GetActualToolFlangePose
            self.log(f"--- {name}臂 GetActualToolFlangePose ---")
            try:
                result = robot.GetActualToolFlangePose()
                pose = self.safe_get_data(result, f"{name}臂法兰位姿")
                if pose:
                    self.log(f"✓ {name}臂法兰位姿: {pose}")
                else:
                    self.log(f"✗ {name}臂法兰位姿获取失败")
            except Exception as e:
                self.log(f"✗ {name}臂法兰位姿异常: {e}", "ERROR")
            
            # 方法3：通过关节位置计算
            self.log(f"--- {name}臂 通过关节位置计算 ---")
            try:
                joint_result = robot.GetActualJointPosDegree()
                joint_pos = self.safe_get_data(joint_result, f"{name}臂关节位置")
                if joint_pos:
                    self.log(f"✓ {name}臂关节位置: {joint_pos}")
                    
                    # 计算正运动学
                    fk_result = robot.GetForwardKin(joint_pos)
                    tcp_pose = self.safe_get_data(fk_result, f"{name}臂正运动学")
                    if tcp_pose:
                        self.log(f"✓ {name}臂正运动学结果: {tcp_pose}")
                    else:
                        self.log(f"✗ {name}臂正运动学计算失败")
                else:
                    self.log(f"✗ {name}臂关节位置获取失败")
            except Exception as e:
                self.log(f"✗ {name}臂关节位置异常: {e}", "ERROR")

    def test_enable_and_mode(self):
        """测试使能和模式切换"""
        self.log("=" * 50)
        self.log("测试使能和模式切换")
        self.log("=" * 50)
        
        robots = []
        if self.right_connected:
            robots.append((self.right_arm, "RIGHT"))
        if self.left_connected:
            robots.append((self.left_arm, "LEFT"))
        
        for robot, name in robots:
            self.log(f"测试{name}臂使能和模式...")
            
            try:
                # 切换到自动模式
                ret = robot.Mode(0)
                self.log(f"{name}臂Mode(0): {ret}")
                time.sleep(1)
                
                # 上使能
                ret = robot.RobotEnable(1)
                self.log(f"{name}臂RobotEnable(1): {ret}")
                time.sleep(1)
                
                self.log(f"✓ {name}臂准备完成")
                
            except Exception as e:
                self.log(f"✗ {name}臂准备失败: {e}", "ERROR")

    def test_simple_movement(self):
        """测试简单运动"""
        self.log("=" * 50)
        self.log("测试简单运动")
        self.log("=" * 50)
        
        print("⚠️  即将测试机械臂运动，请确保周围安全！")
        user_input = input("确认继续运动测试？(y/N): ").strip().lower()
        if user_input != 'y' and user_input != 'yes':
            self.log("用户取消运动测试")
            return
        
        robots = []
        if self.right_connected:
            robots.append((self.right_arm, "RIGHT"))
        if self.left_connected:
            robots.append((self.left_arm, "LEFT"))
        
        for robot, name in robots:
            self.log(f"测试{name}臂简单运动...")
            
            try:
                # 获取当前位姿
                result = robot.GetActualTCPPose()
                current_pose = self.safe_get_data(result, f"{name}臂当前位姿")
                
                if current_pose:
                    self.log(f"{name}臂当前位姿: {current_pose}")
                    
                    # 计算小幅移动目标（Z轴+5cm）
                    target_pose = current_pose.copy()
                    target_pose[2] += 50.0  # Z轴上移5cm
                    
                    self.log(f"{name}臂目标位姿: {target_pose}")
                    
                    # 执行运动
                    self.log(f"开始{name}臂运动...")
                    ret = robot.MoveL(target_pose, 0, 0, vel=10)  # 慢速运动
                    
                    if ret == 0:
                        self.log(f"✓ {name}臂运动指令发送成功")
                        time.sleep(3)  # 等待运动完成
                        
                        # 返回原位
                        self.log(f"开始{name}臂返回原位...")
                        ret = robot.MoveL(current_pose, 0, 0, vel=10)
                        if ret == 0:
                            self.log(f"✓ {name}臂返回原位成功")
                        else:
                            self.log(f"✗ {name}臂返回原位失败: {ret}", "ERROR")
                    else:
                        self.log(f"✗ {name}臂运动失败: {ret}", "ERROR")
                else:
                    self.log(f"✗ 无法获取{name}臂当前位姿，跳过运动测试")
                    
            except Exception as e:
                self.log(f"✗ {name}臂运动测试异常: {e}", "ERROR")

    def disconnect(self):
        """断开连接"""
        try:
            if self.right_arm and self.right_connected:
                self.right_arm.CloseRPC()
                self.log("右臂连接已断开")
        except Exception as e:
            self.log(f"断开右臂连接异常: {e}", "ERROR")
        
        try:
            if self.left_arm and self.left_connected:
                self.left_arm.CloseRPC()
                self.log("左臂连接已断开")
        except Exception as e:
            self.log(f"断开左臂连接异常: {e}", "ERROR")

    def run_debug_test(self):
        """运行调试测试"""
        try:
            self.log("=" * 70)
            self.log("双臂机械臂调试测试开始")
            self.log("=" * 70)
            
            # 1. 连接测试
            if not self.test_connection():
                return False
            
            # 2. 基本信息测试
            self.test_basic_info()
            
            # 3. 位姿获取测试
            self.test_pose_methods()
            
            # 4. 使能和模式测试
            self.test_enable_and_mode()
            
            # 5. 简单运动测试（可选）
            print("\n" + "="*50)
            print("是否进行运动测试？")
            print("注意：这将使机械臂进行小幅运动")
            user_input = input("继续运动测试？(y/N): ").strip().lower()
            if user_input == 'y' or user_input == 'yes':
                self.test_simple_movement()
            
            self.log("=" * 70)
            self.log("调试测试完成")
            self.log("=" * 70)
            
            return True
            
        except KeyboardInterrupt:
            self.log("用户中断测试", "WARNING")
            return False
        except Exception as e:
            self.log(f"测试过程异常: {e}", "ERROR")
            return False
        finally:
            self.disconnect()

def main():
    """主函数"""
    print("=" * 70)
    print("双臂FR3机械臂调试测试程序")
    print("用于调试ctypes错误和连接问题")
    print("=" * 70)
    print(f"Python版本: {sys.version}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # IP地址配置
    right_arm_ip = '192.168.58.2'
    left_arm_ip = '192.168.58.3'
    
    if len(sys.argv) > 1:
        right_arm_ip = sys.argv[1]
    if len(sys.argv) > 2:
        left_arm_ip = sys.argv[2]
    
    print(f"右臂IP: {right_arm_ip}")
    print(f"左臂IP: {left_arm_ip}")
    print()
    
    print("🔍 调试测试内容:")
    print("1. 双臂连接测试")
    print("2. 基本信息获取测试")
    print("3. 多种位姿获取方法测试")
    print("4. 使能和模式切换测试")
    print("5. 简单运动测试（可选）")
    print()
    
    print("⚠️  安全提示:")
    print("• 确保机械臂周围无障碍物")
    print("• 急停按钮随时可用")
    print("• 运动测试为小幅度移动")
    print("• 如有异常立即按Ctrl+C")
    print()
    
    user_input = input("确认开始调试测试？(y/N): ").strip().lower()
    if user_input != 'y' and user_input != 'yes':
        print("测试已取消")
        return 1
    
    # 创建调试测试实例
    debug_test = DualArmDebugTest(right_arm_ip, left_arm_ip)
    
    try:
        success = debug_test.run_debug_test()
        
        if success:
            print("\n🎉 调试测试完成！")
            print("💡 请查看上述日志，分析可能的问题")
            return 0
        else:
            print("\n❌ 调试测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
        debug_test.disconnect()
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        debug_test.disconnect()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
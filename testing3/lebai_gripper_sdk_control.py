#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪SDK控制脚本 
通过FR3 SDK的MoveGripper接口控制乐白夹爪
结合末端通讯参数配置实现直接控制
"""

import sys
import os
import time
from typing import Optional, Tuple

# 添加项目内fairino库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

try:
    from fairino import Robot
    print("✓ 成功导入项目内fairino库")
except ImportError as e:
    print(f"✗ 导入fairino库失败: {e}")
    print(f"请确保FR3控制路径存在: {fr3_control_path}")
    print("或检查fairino/Robot.py文件是否存在")
    sys.exit(1)


class LebaiGripperSDKControl:
    """基于FR3 SDK的乐白夹爪控制器"""
    
    def __init__(self, robot_ip: str = '192.168.58.2'):
        """
        初始化夹爪控制器
        
        Args:
            robot_ip: FR3机器人IP地址
        """
        self.robot_ip = robot_ip
        self.robot = None
        
    def connect(self) -> bool:
        """连接到FR3机器人控制器"""
        try:
            print(f"正在连接机器人控制器 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            
            # 初始化日志
            self.robot.LoggerInit(output_model=0)
            self.robot.SetLoggerLevel(4)
            
            print("✓ 机器人连接成功")
            return True
            
        except Exception as e:
            print(f"✗ 机器人连接失败: {e}")
            return False
    
    def configure_end_communication(self) -> bool:
        """配置末端通讯参数"""
        try:
            print("配置末端485通讯参数...")
            
            # 设置末端通讯参数 (基于乐白夹爪要求: 115200, 8N1)
            result = self.robot.SetAxleCommunicationParam(
                7,     # 波特率: 7-115200
                8,     # 数据位: 8
                1,     # 停止位: 1
                0,     # 校验位: 0-None
                100,   # 超时时间: 100ms
                3,     # 超时次数: 3
                50     # 周期性指令时间间隔: 50ms
            )
            
            if result == 0:
                print("✓ 末端通讯参数配置成功")
                
                # 获取并验证配置
                params = self.robot.GetAxleCommunicationParam()
                print(f"  当前配置: {params}")
                return True
            else:
                print(f"✗ 末端通讯参数配置失败，错误码: {result}")
                return False
                
        except Exception as e:
            print(f"✗ 配置末端通讯参数异常: {e}")
            return False
    
    def activate_gripper(self) -> bool:
        """激活夹爪"""
        try:
            print("=== 激活夹爪 ===")
            
            # 复位夹爪
            print("步骤1: 复位夹爪")
            result = self.robot.ActGripper(1, 0)  # 设备ID=1, 复位
            print(f"复位结果: {result}")
            time.sleep(1)
            
            # 激活夹爪
            print("步骤2: 激活夹爪")
            result = self.robot.ActGripper(1, 1)  # 设备ID=1, 激活
            print(f"激活结果: {result}")
            time.sleep(2)
            
            print("✓ 夹爪激活完成")
            return True
            
        except Exception as e:
            print(f"✗ 夹爪激活失败: {e}")
            return False
    
    def move_gripper(self, position: int, speed: int = 50, force: int = 50, timeout: int = 5000) -> bool:
        """
        移动夹爪到指定位置
        
        Args:
            position: 位置 (0-100, 0=张开, 100=闭合)
            speed: 速度 (0-100)
            force: 力度 (0-100)
            timeout: 超时时间 (ms)
        """
        try:
            position = max(0, min(100, position))
            speed = max(0, min(100, speed))
            force = max(0, min(100, force))
            
            print(f"移动夹爪 - 位置:{position}%, 速度:{speed}%, 力度:{force}%")
            
            # MoveGripper(设备ID, 位置, 速度, 力度, 超时, 标志)
            result = self.robot.MoveGripper(1, position, speed, force, timeout, 0)
            
            if result == 0:
                print(f"✓ 夹爪移动命令发送成功")
                return True
            else:
                print(f"✗ 夹爪移动失败，错误码: {result}")
                return False
                
        except Exception as e:
            print(f"✗ 夹爪移动异常: {e}")
            return False
    
    def get_gripper_status(self) -> Optional[dict]:
        """获取夹爪状态"""
        try:
            # 获取夹爪运动状态
            motion_done = self.robot.GetGripperMotionDone()
            
            # 获取机器人状态包中的夹爪信息
            state = self.robot.robot_state_pkg
            if hasattr(state, 'gripper_position'):
                gripper_pos = state.gripper_position
            else:
                gripper_pos = None
            
            status = {
                'motion_done': motion_done,
                'position': gripper_pos,
                'timestamp': time.time()
            }
            
            return status
            
        except Exception as e:
            print(f"获取夹爪状态失败: {e}")
            return None
    
    def open_gripper(self, force: int = 25, speed: int = 50) -> bool:
        """张开夹爪"""
        print("=== 张开夹爪 ===")
        return self.move_gripper(0, speed, force)
    
    def close_gripper(self, force: int = 50, speed: int = 50) -> bool:
        """闭合夹爪"""
        print("=== 闭合夹爪 ===")
        return self.move_gripper(100, speed, force)
    
    def set_gripper_position(self, position: int, force: int = 35, speed: int = 50) -> bool:
        """设置夹爪到指定位置"""
        print(f"=== 设置夹爪位置到 {position}% ===")
        return self.move_gripper(position, speed, force)
    
    def wait_for_motion_done(self, timeout: int = 10) -> bool:
        """等待夹爪运动完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_gripper_status()
                if status and status['motion_done'] == 1:
                    print("✓ 夹爪运动完成")
                    return True
                time.sleep(0.1)
            except:
                pass
        
        print("⚠ 等待夹爪运动完成超时")
        return False
    
    def gripper_test_sequence(self) -> bool:
        """执行夹爪测试序列"""
        try:
            print("=== 开始夹爪测试序列 ===")
            
            # 测试步骤
            test_steps = [
                {
                    'name': '张开夹爪',
                    'action': lambda: self.open_gripper(force=25, speed=50),
                    'wait_time': 3
                },
                {
                    'name': '闭合夹爪',
                    'action': lambda: self.close_gripper(force=50, speed=50),
                    'wait_time': 3
                },
                {
                    'name': '设置半开位置',
                    'action': lambda: self.set_gripper_position(50, force=35, speed=50),
                    'wait_time': 2
                }
            ]
            
            for i, step in enumerate(test_steps, 1):
                print(f"\n步骤 {i}: {step['name']}")
                
                # 执行动作
                if not step['action']():
                    print(f"✗ {step['name']} 失败")
                    return False
                
                # 等待完成
                print(f"等待 {step['wait_time']} 秒...")
                time.sleep(step['wait_time'])
                
                # 获取状态
                status = self.get_gripper_status()
                if status:
                    print(f"  状态: 运动完成={status['motion_done']}, 位置={status['position']}")
                
                print(f"✓ {step['name']} 完成")
            
            print("\n🎉 夹爪测试序列全部完成！")
            return True
            
        except Exception as e:
            print(f"✗ 测试序列异常: {e}")
            return False
    
    def interactive_control(self):
        """交互式控制模式"""
        print("\n=== 进入交互式控制模式 ===")
        print("可用命令:")
        print("  open [force] - 张开夹爪，可选力度参数")
        print("  close [force] - 闭合夹爪，可选力度参数")
        print("  pos <position> [force] - 设置位置，必需位置参数，可选力度参数")
        print("  status - 显示夹爪状态")
        print("  quit - 退出")
        
        while True:
            try:
                cmd = input("\n请输入命令: ").strip().lower()
                
                if cmd == 'quit' or cmd == 'q':
                    break
                elif cmd == 'status':
                    status = self.get_gripper_status()
                    if status:
                        print(f"夹爪状态: {status}")
                    else:
                        print("获取状态失败")
                elif cmd.startswith('open'):
                    parts = cmd.split()
                    force = int(parts[1]) if len(parts) > 1 else 25
                    self.open_gripper(force)
                elif cmd.startswith('close'):
                    parts = cmd.split()
                    force = int(parts[1]) if len(parts) > 1 else 50
                    self.close_gripper(force)
                elif cmd.startswith('pos'):
                    parts = cmd.split()
                    if len(parts) < 2:
                        print("错误: 需要位置参数")
                        continue
                    position = int(parts[1])
                    force = int(parts[2]) if len(parts) > 2 else 35
                    self.set_gripper_position(position, force)
                else:
                    print("未知命令，请重新输入")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"命令执行错误: {e}")
        
        print("退出交互式控制模式")
    
    def disconnect(self):
        """断开连接"""
        if self.robot:
            print("断开机器人连接")
            self.robot = None


def main():
    """主函数"""
    print("=== 乐白夹爪SDK控制程序 ===")
    print("版本: 1.0")
    print("基于: FR3 SDK + MoveGripper接口")
    print()
    
    # 创建夹爪控制器
    gripper = LebaiGripperSDKControl(robot_ip='192.168.58.2')
    
    try:
        # 连接机器人
        if not gripper.connect():
            return False
        
        # 配置末端通讯参数
        if not gripper.configure_end_communication():
            print("⚠ 通讯参数配置失败，但继续尝试...")
        
        # 激活夹爪
        if not gripper.activate_gripper():
            print("⚠ 夹爪激活失败，但继续尝试...")
        
        # 执行测试序列
        print("\n选择操作模式:")
        print("1. 自动测试序列")
        print("2. 交互式控制")
        
        choice = input("请选择 (1-2): ").strip()
        
        if choice == '1':
            success = gripper.gripper_test_sequence()
            if success:
                print("\n🎉 自动测试完成！")
            else:
                print("\n❌ 自动测试失败")
        elif choice == '2':
            gripper.interactive_control()
        else:
            print("无效选择，执行默认测试序列")
            gripper.gripper_test_sequence()
        
        return True
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return False
        
    except Exception as e:
        print(f"\n程序异常: {e}")
        return False
        
    finally:
        gripper.disconnect()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
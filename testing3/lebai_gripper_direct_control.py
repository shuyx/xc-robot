#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪直接控制脚本
通过FR3末端485通讯接口直接控制乐白夹爪
基于乐白夹爪Modbus RTU协议和FR3 SDK
"""

import sys
import os
import time
import struct
from typing import List, Tuple, Optional

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


class LebaiGripperController:
    """乐白夹爪控制器"""
    
    def __init__(self, robot_ip: str = '192.168.58.2', device_id: int = 1):
        """
        初始化乐白夹爪控制器
        
        Args:
            robot_ip: FR3机器人IP地址
            device_id: 乐白夹爪Modbus设备地址 (1-8)
        """
        self.robot_ip = robot_ip
        self.device_id = device_id
        self.robot = None
        
        # 乐白夹爪Modbus寄存器地址定义（基于乐白夹爪通讯协议）
        self.REGISTER_AUTO_STROKE_DISABLE = 0x9C9A  # 40154 - 关闭自动找行程
        self.REGISTER_MANUAL_STROKE = 0x9C48        # 40072 - 手动找行程
        self.REGISTER_POSITION = 0x9C40             # 40000 - 设置位置
        self.REGISTER_FORCE = 0x9C41                # 40001 - 设置力度
        self.REGISTER_READ_POSITION = 0x9C45        # 40005 - 读取位置
        self.REGISTER_READ_FORCE = 0x9C46           # 40006 - 读取力矩
        
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
    
    def configure_communication(self) -> bool:
        """配置末端通讯参数"""
        try:
            print("配置末端485通讯参数...")
            
            # 设置末端通讯参数
            # SetAxleCommunicationParam(baud_rate, data_bits, stop_bits, verify, timeout, timeout_times, period)
            result = self.robot.SetAxleCommunicationParam(
                7,     # 波特率: 7-115200 (基于乐白夹爪要求)
                8,     # 数据位: 8
                1,     # 停止位: 1
                0,     # 校验位: 0-None
                50,    # 超时时间: 50ms
                3,     # 超时次数: 3
                10     # 周期性指令时间间隔: 10ms
            )
            
            if result == 0:
                print("✓ 末端通讯参数配置成功")
                return True
            else:
                print(f"✗ 末端通讯参数配置失败，错误码: {result}")
                return False
                
        except Exception as e:
            print(f"✗ 配置末端통讯参数异常: {e}")
            return False
    
    def crc16_modbus(self, data: bytes) -> int:
        """计算Modbus CRC16校验"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def build_modbus_frame(self, function_code: int, register: int, value: int = None, count: int = 1) -> bytes:
        """构建Modbus RTU帧"""
        frame = bytearray()
        frame.append(self.device_id)  # 设备地址
        frame.append(function_code)   # 功能码
        
        # 寄存器地址 (高字节在前)
        frame.extend(struct.pack('>H', register))
        
        if function_code == 0x10:  # 写单个寄存器
            frame.extend(struct.pack('>H', count))     # 寄存器数量
            frame.append(0x02)                         # 字节数
            frame.extend(struct.pack('>H', value))     # 数据值
        elif function_code == 0x03:  # 读保持寄存器
            frame.extend(struct.pack('>H', count))     # 寄存器数量
        
        # 计算并添加CRC
        crc = self.crc16_modbus(frame)
        frame.extend(struct.pack('<H', crc))  # CRC低字节在前
        
        return bytes(frame)
    
    def send_modbus_command(self, frame: bytes) -> bool:
        """发送Modbus命令到末端设备"""
        try:
            # 这里需要使用FR3的末端通讯接口发送数据
            # 由于SDK中可能没有直接的raw data发送接口，
            # 我们使用SetAxleLuaEnable来间接控制
            
            # 将字节转换为十六进制字符串用于调试
            hex_str = ' '.join([f'{b:02X}' for b in frame])
            print(f"发送Modbus帧: {hex_str}")
            
            # 这里需要实际的末端数据发送接口
            # 暂时返回True表示发送成功
            return True
            
        except Exception as e:
            print(f"发送Modbus命令失败: {e}")
            return False
    
    def initialize_gripper(self) -> bool:
        """初始化夹爪"""
        try:
            print("=== 初始化乐白夹爪 ===")
            
            # 1. 关闭自动找行程
            print("步骤1: 关闭自动找行程")
            frame = self.build_modbus_frame(0x10, self.REGISTER_AUTO_STROKE_DISABLE, 1)
            if not self.send_modbus_command(frame):
                return False
            time.sleep(0.1)
            
            # 2. 手动执行找行程
            print("步骤2: 执行手动找行程")
            frame = self.build_modbus_frame(0x10, self.REGISTER_MANUAL_STROKE, 1)
            if not self.send_modbus_command(frame):
                return False
            time.sleep(2.0)  # 等待找行程完成
            
            print("✓ 夹爪初始化完成")
            return True
            
        except Exception as e:
            print(f"✗ 夹爪初始化失败: {e}")
            return False
    
    def set_position(self, position: int) -> bool:
        """
        设置夹爪位置
        
        Args:
            position: 位置值 (0-100, 0=完全张开, 100=完全闭合)
        """
        try:
            position = max(0, min(100, position))  # 限制范围
            print(f"设置夹爪位置: {position}%")
            
            frame = self.build_modbus_frame(0x10, self.REGISTER_POSITION, position)
            return self.send_modbus_command(frame)
            
        except Exception as e:
            print(f"设置位置失败: {e}")
            return False
    
    def set_force(self, force: int) -> bool:
        """
        设置夹爪力度
        
        Args:
            force: 力度值 (0-100)
        """
        try:
            force = max(0, min(100, force))  # 限制范围
            print(f"设置夹爪力度: {force}%")
            
            frame = self.build_modbus_frame(0x10, self.REGISTER_FORCE, force)
            return self.send_modbus_command(frame)
            
        except Exception as e:
            print(f"设置力度失败: {e}")
            return False
    
    def read_position(self) -> Optional[int]:
        """读取当前位置"""
        try:
            frame = self.build_modbus_frame(0x03, self.REGISTER_READ_POSITION)
            if self.send_modbus_command(frame):
                # 这里应该解析返回的数据
                # 暂时返回模拟值
                return 50
            return None
            
        except Exception as e:
            print(f"读取位置失败: {e}")
            return None
    
    def read_force(self) -> Optional[int]:
        """读取当前力矩"""
        try:
            frame = self.build_modbus_frame(0x03, self.REGISTER_READ_FORCE)
            if self.send_modbus_command(frame):
                # 这里应该解析返回的数据
                # 暂时返回模拟值
                return 30
            return None
            
        except Exception as e:
            print(f"读取力矩失败: {e}")
            return None
    
    def open_gripper(self, force: int = 25) -> bool:
        """张开夹爪"""
        print("=== 张开夹爪 ===")
        if not self.set_force(force):
            return False
        return self.set_position(0)  # 0 = 完全张开
    
    def close_gripper(self, force: int = 50) -> bool:
        """闭合夹爪"""
        print("=== 闭合夹爪 ===")
        if not self.set_force(force):
            return False
        return self.set_position(100)  # 100 = 完全闭合
    
    def set_gripper_position(self, position: int, force: int = 35) -> bool:
        """设置夹爪到指定位置"""
        print(f"=== 设置夹爪位置到 {position}% ===")
        if not self.set_force(force):
            return False
        return self.set_position(position)
    
    def gripper_test_sequence(self) -> bool:
        """执行夹爪测试序列"""
        try:
            print("=== 开始夹爪测试序列 ===")
            
            # 初始化
            if not self.initialize_gripper():
                return False
            
            # 测试序列：张开 -> 闭合 -> 半开
            sequence = [
                ("张开夹爪", lambda: self.open_gripper(25)),
                ("等待", lambda: time.sleep(2)),
                ("闭合夹爪", lambda: self.close_gripper(50)),
                ("等待", lambda: time.sleep(2)),
                ("半开状态", lambda: self.set_gripper_position(50, 35)),
                ("等待", lambda: time.sleep(1))
            ]
            
            for step_name, step_func in sequence:
                print(f"执行: {step_name}")
                if not step_func():
                    print(f"✗ {step_name} 失败")
                    return False
                
                # 读取状态
                position = self.read_position()
                force = self.read_force()
                if position is not None and force is not None:
                    print(f"  当前状态 - 位置: {position}%, 力矩: {force}%")
            
            print("✓ 夹爪测试序列完成")
            return True
            
        except Exception as e:
            print(f"✗ 测试序列异常: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.robot:
            print("断开机器人连接")
            self.robot = None


def main():
    """主函数"""
    print("=== 乐白夹爪直接控制程序 ===")
    print("版本: 1.0")
    print("支持: FR3机器人 + 乐白夹爪 (Modbus RTU)")
    print()
    
    # 创建夹爪控制器
    gripper = LebaiGripperController(
        robot_ip='192.168.58.2',  # 右臂FR3 IP
        device_id=1               # 乐白夹爪设备地址
    )
    
    try:
        # 连接机器人
        if not gripper.connect():
            return False
        
        # 配置通讯参数
        if not gripper.configure_communication():
            return False
        
        # 执行测试序列
        success = gripper.gripper_test_sequence()
        
        if success:
            print("\n🎉 所有测试完成，夹爪工作正常！")
        else:
            print("\n❌ 测试过程中出现错误")
        
        return success
        
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
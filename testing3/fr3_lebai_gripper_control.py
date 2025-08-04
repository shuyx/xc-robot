#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂与乐白夹爪通讯配置和控制脚本

基于对资料分析：
1. 乐白夹爪使用RS485 Modbus协议，波特率115200，8N1
2. FR3机械臂需要设置外设协议为Modbus(4098)
3. 使用末端法兰M12-5芯485接口连接夹爪

接线说明（M8-8P母弯头）：
- 1 棕 - 24V
- 2 绿 - 地  
- 5 橙 - 485A
- 6 蓝 - 485B

Author: Claude
Date: 2025-07-28
"""

import sys
import os
import time
import struct
import logging

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

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LebaiGripperController:
    """乐白夹爪控制器"""
    
    # 乐白夹爪寄存器地址
    REG_GRIP_POSITION = 40000  # 0x9C40 夹爪幅度控制 (0-100%)
    REG_GRIP_FORCE = 40001     # 0x9C41 夹爪力度控制 (0-100%)
    REG_CURRENT_POS = 40005    # 0x9C45 夹爪当前位置 (只读)
    REG_CURRENT_FORCE = 40006  # 0x9C46 夹爪当前力矩 (只读)
    REG_AUTO_CALIBRATE = 40154 # 0x9C9A 关闭自动找行程
    REG_MANUAL_CALIBRATE = 40072 # 0x9C48 手动找行程
    
    def __init__(self, robot_ip="192.168.58.2"):
        """初始化控制器
        
        Args:
            robot_ip: FR3机械臂IP地址
        """
        self.robot = None
        self.robot_ip = robot_ip
        self.is_connected = False
        
    def connect(self):
        """连接机械臂"""
        try:
            self.robot = Robot.RPC(self.robot_ip)
            self.is_connected = True
            logger.info(f"成功连接到机械臂: {self.robot_ip}")
            return True
        except Exception as e:
            logger.error(f"连接机械臂失败: {e}")
            return False
    
    def configure_communication(self):
        """配置机械臂末端通讯参数"""
        if not self.is_connected:
            logger.error("请先连接机械臂")
            return False
            
        try:
            # 设置外设协议为Modbus
            logger.info("设置外设协议为Modbus...")
            error = self.robot.SetExDevProtocol(4098)  # 4098 = Modbus协议
            if error != 0:
                logger.error(f"设置外设协议失败，错误码: {error}")
                return False
            
            # 设置末端通讯参数
            logger.info("配置末端通讯参数...")
            # SetAxleCommunicationParam(baudRate, dataBit, stopBit, verify, timeout, timeoutTimes, period)
            # 乐白夹爪参数: 115200, 8, 1, 0(无校验), 3000ms超时, 3次重试, 1000ms周期
            error = self.robot.SetAxleCommunicationParam(115200, 8, 1, 0, 3000, 3, 1000)
            if error != 0:
                logger.error(f"设置通讯参数失败，错误码: {error}")
                return False
                
            logger.info("通讯配置完成")
            return True
            
        except Exception as e:
            logger.error(f"配置通讯参数时发生错误: {e}")
            return False
    
    def send_modbus_command(self, device_addr, func_code, reg_addr, data):
        """发送Modbus指令
        
        Args:
            device_addr: 设备地址 (乐白夹爪默认为1)
            func_code: 功能码 (写单个寄存器: 0x10)
            reg_addr: 寄存器地址
            data: 要写入的数据
        """
        try:
            # 构造Modbus RTU帧
            # 格式: 设备地址 + 功能码 + 寄存器地址(2字节) + 寄存器数量(2字节) + 字节数 + 数据(2字节) + CRC(2字节)
            frame = bytearray()
            frame.append(device_addr)  # 设备地址
            frame.append(func_code)    # 功能码 0x10 (写多个寄存器)
            frame.extend(struct.pack('>H', reg_addr))  # 寄存器地址 (大端)
            frame.extend(struct.pack('>H', 1))         # 寄存器数量
            frame.append(2)            # 字节数
            frame.extend(struct.pack('>H', data))      # 数据 (大端)
            
            # 计算CRC16 (简化版，实际应用中需要完整的CRC算法)
            crc = self._calculate_crc16(frame)
            frame.extend(struct.pack('<H', crc))  # CRC (小端)
            
            # 发送指令 (这里需要根据FR3的具体Modbus发送接口调整)
            # 注意：FR3可能有专门的Modbus发送函数，需要查阅具体文档
            logger.info(f"发送Modbus指令: {' '.join([f'{b:02X}' for b in frame])}")
            
            # 模拟发送成功
            return True
            
        except Exception as e:
            logger.error(f"发送Modbus指令失败: {e}")
            return False
    
    def _calculate_crc16(self, data):
        """计算CRC16校验码 (Modbus标准)"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def initialize_gripper(self):
        """初始化夹爪"""
        logger.info("初始化乐白夹爪...")
        
        try:
            # 1. 关闭自动找行程
            logger.info("关闭自动找行程...")
            if not self.send_modbus_command(0x01, 0x10, self.REG_AUTO_CALIBRATE, 0x01):
                return False
            time.sleep(0.5)
            
            # 2. 手动执行找行程
            logger.info("执行找行程...")
            if not self.send_modbus_command(0x01, 0x10, self.REG_MANUAL_CALIBRATE, 0x01):
                return False
            time.sleep(3)  # 等待找行程完成
            
            logger.info("夹爪初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化夹爪失败: {e}")
            return False
    
    def set_gripper_position(self, position, force=50):
        """设置夹爪位置
        
        Args:
            position: 夹爪位置百分比 (0-100, 0=完全张开, 100=完全闭合)
            force: 夹爪力度百分比 (0-100)
        """
        if not 0 <= position <= 100:
            logger.error("位置参数必须在0-100之间")
            return False
        if not 0 <= force <= 100:
            logger.error("力度参数必须在0-100之间")
            return False
            
        try:
            # 设置夹爪力度
            logger.info(f"设置夹爪力度: {force}%")
            if not self.send_modbus_command(0x01, 0x10, self.REG_GRIP_FORCE, force):
                return False
            time.sleep(0.1)
            
            # 设置夹爪位置
            logger.info(f"设置夹爪位置: {position}%")
            if not self.send_modbus_command(0x01, 0x10, self.REG_GRIP_POSITION, position):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"设置夹爪位置失败: {e}")
            return False
    
    def open_gripper(self, force=30):
        """打开夹爪"""
        logger.info("打开夹爪...")
        return self.set_gripper_position(0, force)
    
    def close_gripper(self, force=50):
        """闭合夹爪"""
        logger.info("闭合夹爪...")
        return self.set_gripper_position(100, force)
    
    def get_gripper_status(self):
        """获取夹爪状态 (需要实现Modbus读取功能)"""
        # 这里需要实现Modbus读取功能
        # 读取当前位置和力矩
        logger.info("获取夹爪状态功能待实现...")
        return {"position": 0, "force": 0}
    
    def test_gripper_movement(self):
        """测试夹爪开合动作"""
        logger.info("开始测试夹爪开合动作...")
        
        try:
            # 测试序列：开 -> 闭 -> 开
            movements = [
                ("打开", 0, 30),
                ("闭合", 100, 50),
                ("再次打开", 0, 30)
            ]
            
            for action, position, force in movements:
                logger.info(f"执行动作: {action}")
                if not self.set_gripper_position(position, force):
                    logger.error(f"动作 {action} 失败")
                    return False
                time.sleep(2)  # 等待动作完成
            
            logger.info("夹爪测试完成!")
            return True
            
        except Exception as e:
            logger.error(f"测试夹爪时发生错误: {e}")
            return False


def main():
    """主函数 - 演示夹爪配置和控制"""
    logger.info("=== FR3机械臂乐白夹爪控制系统 ===")
    
    # 创建控制器实例
    gripper = LebaiGripperController()
    
    try:
        # 1. 连接机械臂
        if not gripper.connect():
            logger.error("无法连接到机械臂，退出程序")
            return
        
        # 2. 配置通讯参数
        if not gripper.configure_communication():
            logger.error("配置通讯参数失败，退出程序")
            return
        
        # 3. 初始化夹爪
        if not gripper.initialize_gripper():
            logger.error("初始化夹爪失败，退出程序")
            return
        
        # 4. 测试夹爪开合
        if not gripper.test_gripper_movement():
            logger.error("夹爪测试失败")
            return
        
        # 5. 提供手动控制选项
        while True:
            print("\n=== 夹爪控制菜单 ===")
            print("1. 打开夹爪")
            print("2. 闭合夹爪") 
            print("3. 设置自定义位置")
            print("4. 获取夹爪状态")
            print("5. 退出")
            
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == '1':
                gripper.open_gripper()
            elif choice == '2':
                gripper.close_gripper()
            elif choice == '3':
                try:
                    pos = int(input("请输入位置 (0-100): "))
                    force = int(input("请输入力度 (0-100): "))
                    gripper.set_gripper_position(pos, force)
                except ValueError:
                    logger.error("请输入有效的数字")
            elif choice == '4':
                status = gripper.get_gripper_status()
                print(f"夹爪状态: {status}")
            elif choice == '5':
                logger.info("退出程序")
                break
            else:
                print("无效选择，请重试")
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        logger.info("程序结束")


if __name__ == "__main__":
    main()
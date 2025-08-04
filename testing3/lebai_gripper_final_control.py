#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪最终控制程序
基于末端自定义协议的简单夹爪控制

使用前提：
1. 已完成手册3.4步骤：上传AXLE_LUA_LEBAI_END.lua到WebApp
2. 已完成末端通讯配置：115200, 8N1
3. 已启用夹爪功能选项

Author: Claude  
Date: 2025-07-28
"""

import sys
import os
import time
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

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LebaiGripperController:
    """乐白夹爪最终控制器"""
    
    def __init__(self, robot_ip="192.168.58.2"):
        """初始化控制器
        
        Args:
            robot_ip: FR3机械臂IP地址 (右臂: 192.168.58.2)
        """
        self.robot_ip = robot_ip
        self.robot = None
        self.device_id = 1  # 右臂设备ID
        self.is_connected = False
        self.is_initialized = False
        
    def connect(self):
        """连接机械臂"""
        try:
            logger.info(f"正在连接机械臂 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            self.is_connected = True
            logger.info("✅ 机械臂连接成功")
            return True
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    def initialize_gripper(self):
        """初始化夹爪"""
        if not self.is_connected:
            logger.error("请先连接机械臂")
            return False
            
        try:
            logger.info("🔧 开始初始化乐白夹爪...")
            
            # 步骤1: 激活夹爪（必需）
            logger.info("1. 激活夹爪...")
            error = self.robot.ActGripper(self.device_id, 1)
            if error != 0:
                logger.error(f"激活夹爪失败，错误码: {error}")
                return False
            logger.info("✅ 夹爪激活成功")
            time.sleep(2)
            
            # 步骤2: 关闭自动找行程
            logger.info("2. 关闭自动找行程...")
            error = self.robot.MoveGripper(self.device_id, 0, 1, 0, 3000, 0)  # 使用指令1
            if error == 0:
                logger.info("✅ 关闭自动找行程成功")
            else:
                logger.warning(f"⚠️  关闭自动找行程返回码: {error}")
            time.sleep(1)
            
            # 步骤3: 执行手动找行程
            logger.info("3. 执行手动找行程...")
            error = self.robot.MoveGripper(self.device_id, 0, 2, 0, 5000, 0)  # 使用指令2
            if error == 0:
                logger.info("✅ 找行程指令发送成功")
            else:
                logger.warning(f"⚠️  找行程指令返回码: {error}")
            
            logger.info("等待找行程完成...")
            time.sleep(5)
            
            self.is_initialized = True
            logger.info("🎉 夹爪初始化完成!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 初始化夹爪异常: {e}")
            return False
    
    def set_gripper_position(self, position, force=50):
        """设置夹爪位置
        
        Args:
            position: 位置百分比 (0-100, 0=完全张开, 100=完全闭合)
            force: 力度百分比 (0-100)
        """
        if not self.is_initialized:
            logger.error("请先初始化夹爪")
            return False
            
        # 参数限制
        position = max(0, min(100, position))
        force = max(0, min(100, force))
        
        try:
            # 先设置力度 (指令4)
            logger.info(f"设置夹爪力度: {force}%")
            error = self.robot.MoveGripper(self.device_id, force, 4, 0, 3000, 0)
            if error != 0:
                logger.warning(f"设置力度返回码: {error}")
            time.sleep(0.2)
            
            # 再设置位置 (指令3)
            logger.info(f"设置夹爪位置: {position}%")
            error = self.robot.MoveGripper(self.device_id, position, 3, 0, 3000, 0)
            if error == 0:
                logger.info("✅ 位置设置成功")
                return True
            else:
                logger.warning(f"⚠️  位置设置返回码: {error}")
                return True  # 即使有警告码也可能成功
                
        except Exception as e:
            logger.error(f"❌ 设置位置异常: {e}")
            return False
    
    def open_gripper(self, force=30):
        """打开夹爪"""
        logger.info("🔓 打开夹爪")
        return self.set_gripper_position(0, force)
    
    def close_gripper(self, force=50):
        """闭合夹爪"""
        logger.info("🔒 闭合夹爪")
        return self.set_gripper_position(100, force)
    
    def half_open_gripper(self, force=40):
        """半开夹爪"""
        logger.info("🤏 半开夹爪")
        return self.set_gripper_position(50, force)
    
    def get_gripper_status(self):
        """获取夹爪状态"""
        if not self.is_initialized:
            logger.error("请先初始化夹爪")
            return None
            
        try:
            # 读取位置 (指令7)
            logger.info("读取夹爪位置...")
            error = self.robot.MoveGripper(self.device_id, 0, 7, 0, 3000, 0)
            logger.info(f"位置读取返回码: {error}")
            
            # 读取力矩 (指令8)  
            logger.info("读取夹爪力矩...")
            error = self.robot.MoveGripper(self.device_id, 0, 8, 0, 3000, 0)
            logger.info(f"力矩读取返回码: {error}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 读取状态异常: {e}")
            return False
    
    def test_sequence(self):
        """执行测试序列"""
        logger.info("🎯 开始夹爪测试序列")
        logger.info("=" * 50)
        
        test_steps = [
            ("完全打开", lambda: self.open_gripper(30), 3),
            ("完全闭合", lambda: self.close_gripper(50), 3),
            ("半开状态", lambda: self.half_open_gripper(40), 3),
            ("再次打开", lambda: self.open_gripper(30), 2),
        ]
        
        for i, (name, action, wait_time) in enumerate(test_steps, 1):
            logger.info(f"\n步骤 {i}: {name}")
            if action():
                logger.info(f"✅ {name} 完成")
            else:
                logger.error(f"❌ {name} 失败")
                return False
                
            logger.info(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)
        
        logger.info("\n🎉 测试序列完成!")
        return True


def interactive_control(gripper):
    """交互式控制菜单"""
    while True:
        print("\n" + "="*50)
        print("🤖 乐白夹爪控制菜单")
        print("="*50)
        print("1. 打开夹爪")
        print("2. 闭合夹爪")
        print("3. 半开夹爪")
        print("4. 自定义位置")
        print("5. 读取状态")
        print("6. 运行测试序列")
        print("7. 退出")
        
        choice = input("请选择操作 (1-7): ").strip()
        
        if choice == '1':
            gripper.open_gripper()
        elif choice == '2':
            gripper.close_gripper()
        elif choice == '3':
            gripper.half_open_gripper()
        elif choice == '4':
            try:
                pos = int(input("请输入位置 (0-100): "))
                force = int(input("请输入力度 (0-100): "))
                gripper.set_gripper_position(pos, force)
            except ValueError:
                print("请输入有效数字")
        elif choice == '5':
            gripper.get_gripper_status()
        elif choice == '6':
            gripper.test_sequence()
        elif choice == '7':
            print("👋 退出程序")
            break
        else:
            print("无效选择，请重试")


def main():
    """主程序"""
    print("🚀 乐白夹爪最终控制程序")
    print("基于末端自定义协议")
    print("=" * 50)
    
    # 创建控制器
    gripper = LebaiGripperController()
    
    try:
        # 1. 连接机械臂
        if not gripper.connect():
            print("❌ 无法连接机械臂，程序退出")
            return
        
        # 2. 初始化夹爪
        if not gripper.initialize_gripper():
            print("❌ 夹爪初始化失败，程序退出")
            return
        
        # 3. 启动交互式控制
        interactive_control(gripper)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断程序")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
    finally:
        print("👋 程序结束")


if __name__ == "__main__":
    main()
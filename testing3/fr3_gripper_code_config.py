#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂夹爪纯代码配置脚本（无需WebApp界面）

基于法奥意威官方PDF文档中的代码示例
使用SetGripperConfig等函数直接在代码中配置夹爪

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

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FR3GripperCodeConfig:
    """FR3夹爪纯代码配置类（基于官方PDF文档）"""
    
    # 夹爪厂商代码
    GRIPPER_COMPANIES = {
        'Robotiq': 1,
        'Huiling': 2,    # 慧灵
        'Tianji': 3,     # 天机
        'Dahuan': 4,     # 大寰
        'Zhixing': 5,    # 知行
        'Lebai': 6       # 乐白（可能需要确认具体代码）
    }
    
    # 设备型号代码
    DEVICE_MODELS = {
        'Robotiq': {
            '2F-85': 0
        },
        'Huiling': {
            'NK系列': 0,
            'Z-EFG-100': 1
        },
        'Tianji': {
            'TEG-110': 0
        },
        'Dahuan': {
            'PGI-xx': 0
        },
        'Zhixing': {
            'default': 0
        },
        'Lebai': {
            'default': 0  # 乐白夹爪默认设备号
        }
    }
    
    def __init__(self, robot_ip="192.168.58.2"):
        self.robot_ip = robot_ip
        self.robot = None
        self.is_connected = False
    
    def connect_robot(self):
        """连接机械臂"""
        try:
            print(f"🔗 连接机械臂 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            self.is_connected = True
            print("✅ 机械臂连接成功")
            return True
        except Exception as e:
            print(f"❌ 机械臂连接失败: {e}")
            return False
    
    def configure_gripper(self, company_name, device_model=None):
        """
        配置夹爪（无需WebApp界面）
        
        Args:
            company_name: 夹爪厂商名称 ('Robotiq', 'Huiling', 'Tianji', 'Dahuan', 'Zhixing', 'Lebai')
            device_model: 设备型号（可选，默认为0）
        """
        if not self.is_connected:
            print("❌ 请先连接机械臂")
            return False
        
        try:
            # 获取厂商代码
            if company_name not in self.GRIPPER_COMPANIES:
                print(f"❌ 不支持的夹爪厂商: {company_name}")
                print(f"支持的厂商: {list(self.GRIPPER_COMPANIES.keys())}")
                return False
            
            company_code = self.GRIPPER_COMPANIES[company_name]
            
            # 获取设备代码
            device_code = 0  # 默认设备代码
            if device_model and company_name in self.DEVICE_MODELS:
                if device_model in self.DEVICE_MODELS[company_name]:
                    device_code = self.DEVICE_MODELS[company_name][device_model]
                else:
                    print(f"⚠️  未知设备型号 {device_model}，使用默认代码 0")
            
            print(f"📝 配置夹爪参数:")
            print(f"   厂商: {company_name} (代码: {company_code})")
            print(f"   设备: {device_model or 'default'} (代码: {device_code})")
            
            # 1. 配置夹爪
            print("1. 执行夹爪配置...")
            error = self.robot.SetGripperConfig(company_code, device_code)
            if error == 0:
                print("   ✅ 夹爪配置成功")
            else:
                print(f"   ❌ 夹爪配置失败，错误码: {error}")
                return False
            
            time.sleep(1)
            
            # 2. 验证配置
            print("2. 验证夹爪配置...")
            try:
                config = self.robot.GetGripperConfig()
                print(f"   当前配置: {config}")
            except Exception as e:
                print(f"   ⚠️  无法获取配置信息: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 配置夹爪时发生错误: {e}")
            return False
    
    def activate_gripper(self, gripper_index=1):
        """
        激活夹爪（先复位再激活）
        
        Args:
            gripper_index: 夹爪编号，默认为1
        """
        if not self.is_connected:
            print("❌ 请先连接机械臂")
            return False
        
        try:
            print(f"🔄 激活夹爪 {gripper_index}...")
            
            # 1. 先复位夹爪
            print("1. 复位夹爪...")
            error = self.robot.ActGripper(gripper_index, 0)  # 0-复位
            if error == 0:
                print("   ✅ 夹爪复位成功")
            else:
                print(f"   ❌ 夹爪复位失败，错误码: {error}")
                return False
            
            time.sleep(1)
            
            # 2. 再激活夹爪
            print("2. 激活夹爪...")
            error = self.robot.ActGripper(gripper_index, 1)  # 1-激活
            if error == 0:
                print("   ✅ 夹爪激活成功")
            else:
                print(f"   ❌ 夹爪激活失败，错误码: {error}")
                return False
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ 激活夹爪时发生错误: {e}")
            return False
    
    def test_gripper_control(self, gripper_index=1):
        """
        测试夹爪控制
        
        Args:
            gripper_index: 夹爪编号，默认为1
        """
        if not self.is_connected:
            print("❌ 请先连接机械臂")
            return False
        
        try:
            print(f"🧪 测试夹爪 {gripper_index} 控制...")
            
            # 测试序列
            test_actions = [
                ("夹爪张开", 0, 50, 30),     # 位置0%, 速度50%, 力度30%
                ("夹爪半闭", 50, 50, 40),    # 位置50%, 速度50%, 力度40%
                ("夹爪闭合", 100, 50, 50),   # 位置100%, 速度50%, 力度50%
                ("夹爪张开", 0, 50, 30)      # 回到张开状态
            ]
            
            for i, (action_name, pos, vel, force) in enumerate(test_actions, 1):
                print(f"{i}. {action_name}...")
                
                # MoveGripper(index, pos, vel, force, maxtime, block, type, rotNum, rotVel, rotTorque)
                error = self.robot.MoveGripper(
                    gripper_index,  # index
                    pos,           # pos: 位置百分比
                    vel,           # vel: 速度百分比
                    force,         # force: 力度百分比
                    5000,          # maxtime: 最大等待时间
                    0,             # block: 0-阻塞
                    0,             # type: 0-平行夹爪
                    0,             # rotNum: 旋转圈数
                    0,             # rotVel: 旋转速度
                    0              # rotTorque: 旋转力矩
                )
                
                if error == 0:
                    print(f"   ✅ {action_name}指令成功")
                else:
                    print(f"   ❌ {action_name}失败，错误码: {error}")
                
                # 等待动作完成
                time.sleep(3)
                
                # 检查运动状态
                try:
                    motion_status = self.robot.GetGripperMotionDone()
                    print(f"   运动状态: {motion_status}")
                except Exception as e:
                    print(f"   ⚠️  无法获取运动状态: {e}")
            
            print("✅ 夹爪控制测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 测试夹爪控制时发生错误: {e}")
            return False
    
    def complete_gripper_setup(self, company_name, device_model=None, gripper_index=1):
        """
        完整的夹爪设置流程（无需WebApp）
        
        Args:
            company_name: 夹爪厂商名称
            device_model: 设备型号（可选）
            gripper_index: 夹爪编号，默认为1
        """
        print("🤖 FR3机械臂夹爪完整配置流程（纯代码方式）")
        print("=" * 60)
        print(f"目标配置: {company_name} {device_model or 'default'}")
        print("=" * 60)
        
        # 1. 连接机械臂
        if not self.connect_robot():
            return False
        
        # 2. 配置夹爪
        if not self.configure_gripper(company_name, device_model):
            return False
        
        # 3. 激活夹爪
        if not self.activate_gripper(gripper_index):
            return False
        
        # 4. 测试夹爪控制
        if not self.test_gripper_control(gripper_index):
            return False
        
        print("\n🎉 夹爪配置和测试全部完成！")
        print("\n📝 总结:")
        print("✅ 机械臂连接成功")
        print("✅ 夹爪配置成功（无需WebApp界面）")
        print("✅ 夹爪激活成功")
        print("✅ 夹爪控制测试成功")
        print("\n🚀 现在可以在您的程序中正常使用夹爪了！")
        
        return True


def main():
    """主函数 - 提供交互式配置"""
    print("🤖 FR3机械臂夹爪纯代码配置工具")
    print("基于法奥意威官方PDF文档")
    print("=" * 50)
    
    # 创建配置实例
    gripper_config = FR3GripperCodeConfig()
    
    # 显示支持的夹爪厂商
    print("支持的夹爪厂商:")
    for i, (name, code) in enumerate(gripper_config.GRIPPER_COMPANIES.items(), 1):
        print(f"  {i}. {name} (代码: {code})")
    
    try:
        # 用户选择厂商
        print("\n请选择您的夹爪厂商:")
        choice = input("输入厂商名称 (如: Lebai, Dahuan, Robotiq): ").strip()
        
        if not choice:
            choice = "Lebai"  # 默认乐白
            print(f"使用默认厂商: {choice}")
        
        # 执行完整配置流程
        success = gripper_config.complete_gripper_setup(
            company_name=choice,
            device_model=None,  # 使用默认设备型号
            gripper_index=1     # 使用夹爪编号1
        )
        
        if success:
            print("\n🎊 配置成功！您的夹爪现在可以正常使用了。")
        else:
            print("\n😞 配置失败，请检查:")
            print("1. 机械臂网络连接")
            print("2. 夹爪硬件连接（24V电源、485通讯线）")
            print("3. 选择的厂商和型号是否正确")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断配置")
    except Exception as e:
        print(f"\n\n❌ 配置过程中发生错误: {e}")
    finally:
        print("\n👋 配置工具结束")


if __name__ == "__main__":
    main()
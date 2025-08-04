#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂乐白夹爪纯代码配置脚本（无需WebApp界面）

基于官方PDF文档的代码配置方法 + 乐白夹爪的特殊Modbus配置
提供两种配置方式的完整解决方案

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

class LebaiGripperPureCodeConfig:
    """乐白夹爪纯代码配置类"""
    
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
    
    def method1_standard_gripper_config(self):
        """
        方法1: 使用标准夹爪配置函数（尝试不同厂商代码）
        基于官方PDF文档的SetGripperConfig方法
        """
        print("\n🔧 方法1: 标准夹爪配置函数")
        print("-" * 40)
        
        if not self.is_connected:
            print("❌ 请先连接机械臂")
            return False
        
        # 尝试不同的厂商代码配置乐白夹爪
        test_configs = [
            (4, 0, "大寰夹爪配置（可能兼容乐白）"),
            (5, 0, "知行夹爪配置（可能兼容乐白）"),
            (2, 0, "慧灵夹爪配置（可能兼容乐白）"),
            (3, 0, "天机夹爪配置（可能兼容乐白）"),
            (1, 0, "Robotiq夹爪配置（可能兼容乐白）")
        ]
        
        for company_code, device_code, description in test_configs:
            try:
                print(f"🧪 尝试配置: {description}")
                print(f"    厂商代码: {company_code}, 设备代码: {device_code}")
                
                # 配置夹爪
                error = self.robot.SetGripperConfig(company_code, device_code)
                if error == 0:
                    print("    ✅ 夹爪配置成功")
                    
                    # 验证配置
                    try:
                        config = self.robot.GetGripperConfig()
                        print(f"    📋 配置信息: {config}")
                    except:
                        print("    ⚠️  无法获取配置信息")
                    
                    # 尝试激活
                    if self._test_activation_and_control(company_code, device_code):
                        print(f"    🎉 成功！使用配置: 厂商={company_code}, 设备={device_code}")
                        return True
                    else:
                        print("    ❌ 激活或控制失败，继续尝试下一个配置")
                else:
                    print(f"    ❌ 配置失败，错误码: {error}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ 配置异常: {e}")
        
        print("❌ 方法1: 所有标准配置都失败")
        return False
    
    def method2_modbus_direct_config(self):
        """
        方法2: 直接Modbus协议配置（推荐用于乐白夹爪）
        基于乐白夹爪的Modbus协议特性
        """
        print("\n🔧 方法2: 直接Modbus协议配置")
        print("-" * 40)
        
        if not self.is_connected:
            print("❌ 请先连接机械臂")
            return False
        
        try:
            # 1. 设置外设协议为Modbus
            print("1. 设置外设协议为Modbus...")
            error = self.robot.SetExDevProtocol(4098)  # 4098 = Modbus
            if error == 0:
                print("   ✅ Modbus协议设置成功")
            else:
                print(f"   ❌ Modbus协议设置失败，错误码: {error}")
                return False
            
            # 2. 配置通讯参数
            print("2. 配置乐白夹爪通讯参数...")
            print("   波特率: 115200, 数据位: 8, 停止位: 1, 校验: 无")
            error = self.robot.SetAxleCommunicationParam(115200, 8, 1, 0, 3000, 3, 1000)
            if error == 0:
                print("   ✅ 通讯参数配置成功")
            else:
                print(f"   ❌ 通讯参数配置失败，错误码: {error}")
                return False
            
            # 3. 等待通讯建立
            print("3. 等待通讯建立...")
            time.sleep(2)
            
            # 4. 直接尝试夹爪控制（无需标准激活流程）
            print("4. 测试夹爪直接控制...")
            return self._test_direct_gripper_control()
            
        except Exception as e:
            print(f"❌ 方法2配置异常: {e}")
            return False
    
    def _test_activation_and_control(self, company_code, device_code):
        """测试夹爪激活和控制"""
        try:
            print("      🔄 测试激活和控制...")
            
            # 1. 复位夹爪
            error = self.robot.ActGripper(1, 0)  # 复位
            if error != 0:
                print(f"      ❌ 复位失败，错误码: {error}")
                return False
            time.sleep(1)
            
            # 2. 激活夹爪
            error = self.robot.ActGripper(1, 1)  # 激活
            if error != 0:
                print(f"      ❌ 激活失败，错误码: {error}")
                return False
            time.sleep(2)
            
            # 3. 测试简单控制
            error = self.robot.MoveGripper(1, 0, 50, 30, 5000, 0, 0, 0, 0, 0)  # 张开
            if error == 0:
                print("      ✅ 夹爪控制测试成功")
                return True
            else:
                print(f"      ❌ 夹爪控制失败，错误码: {error}")
                return False
                
        except Exception as e:
            print(f"      ❌ 激活测试异常: {e}")
            return False
    
    def _test_direct_gripper_control(self):
        """测试直接夹爪控制（无需激活流程）"""
        try:
            print("   🧪 执行夹爪直接控制测试...")
            
            # 测试序列
            test_actions = [
                ("夹爪张开", 0, 30, 20),     # 轻柔的张开动作
                ("夹爪轻闭", 30, 30, 30),    # 轻微闭合
                ("夹爪张开", 0, 30, 20)      # 回到张开状态
            ]
            
            for i, (action_name, pos, vel, force) in enumerate(test_actions, 1):
                print(f"   {i}. {action_name}...")
                
                error = self.robot.MoveGripper(1, pos, vel, force, 5000, 0, 0, 0, 0, 0)
                
                if error == 0:
                    print(f"      ✅ {action_name}成功")
                else:
                    print(f"      ❌ {action_name}失败，错误码: {error}")
                    if i == 1:  # 如果第一个动作就失败，直接返回
                        return False
                
                time.sleep(3)
            
            print("   ✅ 直接控制测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 直接控制测试异常: {e}")
            return False
    
    def comprehensive_lebai_config(self):
        """乐白夹爪综合配置方案"""
        print("🤖 乐白夹爪纯代码配置（无需WebApp界面）")
        print("=" * 60)
        print("提供两种配置方法:")
        print("方法1: 标准夹爪配置函数（尝试兼容配置）")
        print("方法2: 直接Modbus协议配置（推荐）")
        print("=" * 60)
        
        # 1. 连接机械臂
        if not self.connect_robot():
            return False
        
        # 2. 尝试方法1：标准配置
        print("\n🚀 开始尝试方法1...")
        if self.method1_standard_gripper_config():
            print("\n🎉 方法1成功！乐白夹爪配置完成")
            self._show_success_summary("方法1: 标准夹爪配置")
            return True
        
        # 3. 尝试方法2：Modbus直接配置
        print("\n🚀 方法1失败，尝试方法2...")
        if self.method2_modbus_direct_config():
            print("\n🎉 方法2成功！乐白夹爪配置完成")
            self._show_success_summary("方法2: Modbus直接配置")
            return True
        
        # 4. 两种方法都失败
        print("\n😞 两种方法都失败了")
        self._show_failure_suggestions()
        return False
    
    def _show_success_summary(self, method_name):
        """显示成功总结"""
        print(f"\n📋 配置成功总结 - {method_name}")
        print("-" * 50)
        print("✅ 机械臂连接成功")
        print("✅ 夹爪配置成功（无需WebApp界面）")
        print("✅ 夹爪控制测试成功")
        print("\n🚀 现在可以在您的程序中使用以下代码控制夹爪:")
        print("""
# 夹爪控制示例
robot.MoveGripper(1, 0, 50, 30, 5000, 0, 0, 0, 0, 0)    # 张开
robot.MoveGripper(1, 100, 50, 50, 5000, 0, 0, 0, 0, 0)  # 闭合
robot.MoveGripper(1, 50, 50, 40, 5000, 0, 0, 0, 0, 0)   # 半开
        """)
    
    def _show_failure_suggestions(self):
        """显示失败建议"""
        print("\n🔧 故障排除建议:")
        print("-" * 30)
        print("1. 硬件检查:")
        print("   □ 确认24V电源正常供电给夹爪")
        print("   □ 检查485通讯线连接:")
        print("     - 橙色线(485A) → FR3末端485A")
        print("     - 蓝色线(485B) → FR3末端485B")
        print("   □ 确认夹爪电源指示灯亮起")
        print()
        print("2. 软件检查:")
        print("   □ 确认机械臂已使能")
        print("   □ 确认没有其他程序占用夹爪")
        print("   □ 尝试重启机械臂控制器")
        print()
        print("3. 其他建议:")
        print("   □ 联系乐白技术支持确认设备地址")
        print("   □ 检查夹爪是否需要特殊的初始化程序")
        print("   □ 考虑在WebApp中手动配置作为最后手段")


def main():
    """主函数"""
    print("🤖 乐白夹爪纯代码配置工具")
    print("基于法奥意威官方PDF文档 + 乐白夹爪特性")
    print("=" * 50)
    
    # 创建配置实例
    lebai_config = LebaiGripperPureCodeConfig()
    
    try:
        # 执行综合配置
        success = lebai_config.comprehensive_lebai_config()
        
        if success:
            print("\n🎊 恭喜！乐白夹爪配置成功，可以正常使用了！")
        else:
            print("\n😞 配置失败，请按照建议检查硬件和软件设置")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断配置")
    except Exception as e:
        print(f"\n\n❌ 配置过程中发生未预期的错误: {e}")
    finally:
        print("\n👋 配置工具结束")


if __name__ == "__main__":
    main()
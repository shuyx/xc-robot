#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂与乐白夹爪配置指南和简化测试脚本

基于分析的文档资料，提供分步配置指导和基础测试功能
注意：本脚本需要根据实际硬件连接情况调整

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

class FR3GripperSetup:
    """FR3机械臂夹爪配置助手"""
    
    def __init__(self, robot_ip="192.168.58.2"):
        self.robot_ip = robot_ip
        self.robot = None
        
    def connect_robot(self):
        """连接机械臂"""
        try:
            self.robot = Robot.RPC(self.robot_ip)
            logger.info(f"✓ 成功连接到FR3机械臂: {self.robot_ip}")
            return True
        except Exception as e:
            logger.error(f"✗ 连接失败: {e}")
            return False
    
    def configure_modbus_communication(self):
        """配置Modbus通讯参数"""
        if not self.robot:
            logger.error("请先连接机械臂")
            return False
            
        try:
            logger.info("开始配置Modbus通讯...")
            
            # 1. 设置外设协议为Modbus
            logger.info("1. 设置外设协议为Modbus(4098)...")
            error = self.robot.SetExDevProtocol(4098)
            if error == 0:
                logger.info("   ✓ 外设协议设置成功")
            else:
                logger.error(f"   ✗ 外设协议设置失败，错误码: {error}")
                return False
            
            # 2. 配置末端通讯参数 (乐白夹爪: 115200, 8N1)
            logger.info("2. 配置末端通讯参数...")
            logger.info("   波特率: 115200, 数据位: 8, 停止位: 1, 校验: 无")
            # SetAxleCommunicationParam(baudRate, dataBit, stopBit, verify, timeout, timeoutTimes, period)
            error = self.robot.SetAxleCommunicationParam(115200, 8, 1, 0, 3000, 3, 1000)
            if error == 0:
                logger.info("   ✓ 通讯参数配置成功")
            else:
                logger.error(f"   ✗ 通讯参数配置失败，错误码: {error}")
                return False
            
            logger.info("✓ Modbus通讯配置完成!")
            return True
            
        except Exception as e:
            logger.error(f"配置通讯时发生错误: {e}")
            return False
    
    def verify_configuration(self):
        """验证配置"""
        try:
            logger.info("验证当前配置...")
            
            # 获取当前外设协议
            try:
                protocol = self.robot.GetExDevProtocol()
                logger.info(f"当前外设协议: {protocol}")
            except:
                logger.warning("无法获取外设协议信息")
            
            # 获取当前通讯参数
            try:
                params = self.robot.GetAxleCommunicationParam()
                logger.info(f"当前通讯参数: {params}")
            except:
                logger.warning("无法获取通讯参数信息")
                
            return True
            
        except Exception as e:
            logger.error(f"验证配置时发生错误: {e}")
            return False
    
    def test_basic_io(self):
        """测试基础IO功能"""
        logger.info("测试机械臂基础IO功能...")
        
        try:
            # 测试工具DO
            logger.info("测试工具数字输出...")
            for i in range(2):  # 工具DO 0-1
                self.robot.SetToolDO(i, 1)
                time.sleep(0.5)
                self.robot.SetToolDO(i, 0)
                time.sleep(0.5)
            logger.info("✓ 工具DO测试完成")
            
            # 测试工具DI读取
            logger.info("读取工具数字输入状态...")
            for i in range(2):  # 工具DI 0-1
                error, status = self.robot.GetToolDI(i)
                logger.info(f"工具DI{i}: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"IO测试失败: {e}")
            return False


def print_hardware_checklist():
    """打印硬件连接检查清单"""
    print("\n" + "="*60)
    print("         FR3机械臂与乐白夹爪硬件连接检查清单")
    print("="*60)
    print()
    print("📋 请确认以下硬件连接：")
    print()
    print("1. 🔌 电源连接:")
    print("   □ 乐白夹爪已连接24V DC电源")
    print("   □ 电源指示灯正常亮起")
    print()
    print("2. 📡 通讯连接 (M8-8P母弯头):")
    print("   □ 1号针脚(棕色) → 24V")
    print("   □ 2号针脚(绿色) → 地")
    print("   □ 5号针脚(橙色) → 485A")
    print("   □ 6号针脚(蓝色) → 485B")
    print("   □ 连接到FR3末端法兰M12-5芯485接口")
    print()
    print("3. 🔧 机械安装:")
    print("   □ 夹爪已正确安装到机械臂末端法兰")
    print("   □ 固定螺丝已拧紧")
    print("   □ 夹爪活动范围无障碍物")
    print()
    print("4. 💻 软件准备:")
    print("   □ FR3机械臂控制器已启动")
    print("   □ 网络连接正常")
    print("   □ Python环境已安装fairino库")
    print()
    input("✅ 确认以上检查项目完成后，按回车键继续...")


def print_troubleshooting_guide():
    """打印故障排除指南"""
    print("\n" + "="*60)
    print("                    故障排除指南")
    print("="*60)
    print()
    print("❌ 常见问题和解决方案:")
    print()
    print("1. 连接机械臂失败:")
    print("   - 检查网络连接和IP地址")
    print("   - 确认机械臂控制器已启动")
    print("   - 尝试ping机械臂IP地址")
    print()
    print("2. 外设协议设置失败:")
    print("   - 确认机械臂固件版本支持Modbus")
    print("   - 检查是否有其他程序占用外设接口")
    print("   - 尝试重启机械臂控制器")
    print()
    print("3. 夹爪无响应:")
    print("   - 检查24V电源是否正常")
    print("   - 确认485线序连接正确")
    print("   - 检查波特率设置(115200)")
    print("   - 确认夹爪设备地址(默认为01)")
    print()
    print("4. 通讯不稳定:")
    print("   - 检查485线缆质量和屏蔽")
    print("   - 确认接地连接良好")
    print("   - 调整通讯超时时间")
    print()


def main():
    """主配置向导"""
    print("\n🤖 FR3机械臂与乐白夹爪配置向导")
    print("基于官方文档资料开发")
    print("-" * 50)
    
    # 硬件检查
    print_hardware_checklist()
    
    # 创建配置实例
    setup = FR3GripperSetup()
    
    try:
        # 1. 连接机械臂
        print("\n📡 步骤1: 连接机械臂")
        if not setup.connect_robot():
            print_troubleshooting_guide()
            return
        
        # 2. 配置通讯
        print("\n⚙️  步骤2: 配置Modbus通讯")
        if not setup.configure_modbus_communication():
            print_troubleshooting_guide()
            return
        
        # 3. 验证配置
        print("\n🔍 步骤3: 验证配置")
        setup.verify_configuration()
        
        # 4. 测试基础功能
        print("\n🧪 步骤4: 测试基础IO功能")
        setup.test_basic_io()
        
        print("\n" + "="*60)
        print("✅ 配置完成!")
        print("="*60)
        print()
        print("📝 接下来的步骤:")
        print("1. 在FR3 WebApp中进入外设配置界面")
        print("2. 选择设备类型为'夹爪设备'")
        print("3. 配置厂商为乐白，选择对应型号")
        print("4. 点击'配置'并等待成功提示")
        print("5. 先点击'复位'，再点击'激活'")
        print("6. 使用MoveGripper指令测试夹爪动作:")
        print("   - MoveGripper(1,100,41,45,3000,0)  # 夹爪抓取")
        print("   - MoveGripper(1,0,41,45,3000,0)    # 夹爪释放")
        print()
        print("🔧 Modbus寄存器地址参考:")
        print("   - 40000 (0x9C40): 夹爪幅度控制 (0-100%)")
        print("   - 40001 (0x9C41): 夹爪力度控制 (0-100%)")
        print("   - 40005 (0x9C45): 夹爪当前位置 (只读)")
        print("   - 40006 (0x9C46): 夹爪当前力矩 (只读)")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断配置过程")
    except Exception as e:
        print(f"\n\n❌ 配置过程中发生错误: {e}")
        print_troubleshooting_guide()
    finally:
        print("\n👋 配置向导结束")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂乐白夹爪故障排除和诊断脚本

用于诊断和解决常见的夹爪控制问题
包含错误码分析、状态检查和修复建议

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

class FR3GripperDiagnostic:
    """FR3夹爪诊断工具"""
    
    # 常见错误码及其说明
    ERROR_CODES = {
        0: "执行成功",
        14: "指令执行失败 - 检查Web界面或状态反馈是否报故障",
        18: "程序正在运行 - 先停止当前程序，再进行其他操作",
        32: "关节超限 - 切换至拖动模式，将关节移动至软限位范围内",
        38: "奇异位姿 - 请更换位姿",
        59: "力/扭矩传感器未激活 - 激活力传感器",
        68: "夹爪运动报错 - 检查夹爪通信状态是否正常",
        69: "通道错误 - 检查IO编号是否在范围内",
        70: "等待超时 - 检查IO信号是否输入或接线是否正确",
        73: "可能的夹爪通信或配置问题",
        101: "机器人未使能 - 请先使能机器人"
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
    
    def explain_error_code(self, error_code):
        """解释错误码"""
        if error_code in self.ERROR_CODES:
            return self.ERROR_CODES[error_code]
        else:
            return f"未知错误码 {error_code} - 请查阅完整的SDK错误码对照表"
    
    def check_robot_status(self):
        """检查机械臂基本状态"""
        print("\n🔍 检查机械臂基本状态...")
        
        try:
            # 检查机器人连接状态
            print("1. 检查机器人连接状态...")
            if self.is_connected:
                print("   ✅ 机器人连接正常")
            else:
                print("   ❌ 机器人未连接")
                return False
            
            # 检查机器人使能状态
            print("2. 检查机器人使能状态...")
            try:
                # 这里可以添加获取机器人状态的代码
                print("   ⚠️  需要在WebApp中确认机器人已使能")
            except:
                print("   ⚠️  无法获取使能状态，请在WebApp中确认")
            
            print("3. 检查机器人运行状态...")
            try:
                # 检查是否有程序在运行
                print("   ⚠️  请确认没有其他程序在运行")
            except:
                print("   ⚠️  无法获取运行状态")
            
            return True
            
        except Exception as e:
            print(f"❌ 状态检查失败: {e}")
            return False
    
    def check_communication_config(self):
        """检查通讯配置"""
        print("\n📡 检查通讯配置...")
        
        try:
            # 检查外设协议
            print("1. 检查外设协议...")
            try:
                protocol = self.robot.GetExDevProtocol()
                if protocol == 4098:
                    print("   ✅ 外设协议已设置为Modbus(4098)")
                else:
                    print(f"   ❌ 外设协议错误: {protocol}，应该是4098")
                    return False
            except Exception as e:
                print(f"   ⚠️  无法获取外设协议: {e}")
            
            # 检查通讯参数
            print("2. 检查通讯参数...")
            try:
                result = self.robot.GetAxleCommunicationParam()
                if len(result) >= 8:  # error + 7个参数
                    error, baudRate, dataBit, stopBit, verify, timeout, timeoutTimes, period = result
                    if error == 0:
                        print(f"   波特率: {baudRate}")
                        print(f"   数据位: {dataBit}")
                        print(f"   停止位: {stopBit}")
                        print(f"   校验位: {verify}")
                        print(f"   超时: {timeout}ms")
                        
                        if baudRate == 115200 and dataBit == 8 and stopBit == 1 and verify == 0:
                            print("   ✅ 通讯参数配置正确")
                        else:
                            print("   ❌ 通讯参数不匹配乐白夹爪要求")
                            return False
                    else:
                        print(f"   ❌ 获取通讯参数失败，错误码: {error}")
                        return False
                else:
                    print("   ❌ 通讯参数格式异常")
                    return False
            except Exception as e:
                print(f"   ⚠️  无法获取通讯参数: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 通讯配置检查失败: {e}")
            return False
    
    def configure_gripper_communication(self):
        """配置夹爪通讯"""
        print("\n⚙️ 重新配置夹爪通讯...")
        
        try:
            # 设置Modbus协议
            print("1. 设置Modbus协议...")
            error = self.robot.SetExDevProtocol(4098)
            if error == 0:
                print("   ✅ Modbus协议设置成功")
            else:
                print(f"   ❌ Modbus协议设置失败，错误码: {error}")
                print(f"   说明: {self.explain_error_code(error)}")
                return False
            
            # 设置通讯参数
            print("2. 设置通讯参数...")
            error = self.robot.SetAxleCommunicationParam(115200, 8, 1, 0, 3000, 3, 1000)
            if error == 0:
                print("   ✅ 通讯参数设置成功")
            else:
                print(f"   ❌ 通讯参数设置失败，错误码: {error}")
                print(f"   说明: {self.explain_error_code(error)}")
                return False
            
            print("✅ 夹爪通讯配置完成")
            return True
            
        except Exception as e:
            print(f"❌ 配置夹爪通讯失败: {e}")
            return False
    
    def test_gripper_simple(self):
        """简单夹爪测试"""
        print("\n🧪 执行简单夹爪测试...")
        
        try:
            test_cases = [
                ("打开夹爪", 0, 30, 20),    # 位置0%, 速度30%, 力度20%
                ("轻微闭合", 30, 30, 20),   # 位置30%, 速度30%, 力度20%
                ("回到中间位置", 50, 30, 20) # 位置50%, 速度30%, 力度20%
            ]
            
            for i, (description, pos, vel, force) in enumerate(test_cases, 1):
                print(f"{i}. {description}...")
                error = self.robot.MoveGripper(1, pos, vel, force, 5000, 0, 0, 0, 0, 0)
                
                if error == 0:
                    print(f"   ✅ {description}指令发送成功")
                else:
                    print(f"   ❌ {description}失败，错误码: {error}")
                    print(f"   说明: {self.explain_error_code(error)}")
                    
                    # 对于错误73提供专门的建议
                    if error == 73:
                        self.provide_error_73_solutions()
                
                time.sleep(3)  # 等待动作完成
            
            return True
            
        except Exception as e:
            print(f"❌ 夹爪测试失败: {e}")
            return False
    
    def provide_error_73_solutions(self):
        """针对错误码73提供解决方案"""
        print("\n🔧 错误码73解决方案:")
        print("   可能原因:")
        print("   1. 夹爪未在WebApp中正确配置")
        print("   2. 夹爪未激活或复位")
        print("   3. 485通讯线连接异常") 
        print("   4. 24V电源供电不正常")
        print("   5. 夹爪设备地址不匹配")
        print("\n   建议操作:")
        print("   1. 在FR3 WebApp中进入'末端外设配置'")
        print("   2. 选择设备类型为'夹爪设备'")
        print("   3. 配置厂商为'乐白'，选择对应型号")
        print("   4. 点击'配置'按钮")
        print("   5. 先点击'复位'，再点击'激活'")
        print("   6. 检查24V电源和485线连接")
    
    def comprehensive_diagnostic(self):
        """综合诊断"""
        print("🔧 FR3机械臂乐白夹爪综合诊断")
        print("=" * 50)
        
        # 1. 连接测试
        if not self.connect_robot():
            print("\n❌ 诊断终止：无法连接机械臂")
            return False
        
        # 2. 基本状态检查
        if not self.check_robot_status():
            print("\n⚠️  机器人状态异常，但继续诊断...")
        
        # 3. 通讯配置检查
        config_ok = self.check_communication_config()
        
        # 4. 如果配置有问题，尝试重新配置
        if not config_ok:
            print("\n🔄 尝试重新配置...")
            if not self.configure_gripper_communication():
                print("\n❌ 诊断终止：无法配置通讯")
                return False
        
        # 5. 夹爪测试
        self.test_gripper_simple()
        
        # 6. 总结和建议
        print("\n📋 诊断总结:")
        print("1. 如果所有指令都成功但夹爪不动作:")
        print("   - 检查24V电源供电")
        print("   - 确认485线接线正确")
        print("   - 在WebApp中配置和激活夹爪")
        print()
        print("2. 如果出现错误码73:")
        print("   - 优先在WebApp中进行夹爪配置")
        print("   - 确保先复位再激活")
        print("   - 检查硬件连接")
        print()
        print("3. 如果持续失败:")
        print("   - 联系技术支持")
        print("   - 提供错误码和日志信息")
        
        return True


def main():
    """主函数"""
    print("🔧 FR3机械臂乐白夹爪故障排除工具")
    print("=" * 50)
    
    # 创建诊断实例
    diagnostic = FR3GripperDiagnostic()
    
    # 执行综合诊断
    try:
        diagnostic.comprehensive_diagnostic()
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断诊断")
    except Exception as e:
        print(f"\n\n❌ 诊断过程中发生未预期的错误: {e}")
    finally:
        print("\n👋 诊断结束")


if __name__ == "__main__":
    main()
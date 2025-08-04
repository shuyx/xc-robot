#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪高级诊断脚本
专门针对错误码73进行深度分析和可能的解决方案

基于前面的测试结果：
- 配置成功（SetGripperConfig, ActGripper都成功）
- 控制失败（MoveGripper返回错误码73）
- 问题可能在于指令格式或通讯协议层面

Author: Claude
Date: 2025-07-28
"""

import sys
import os
import time

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

class LebaiFR3DiagnosticTool:
    """乐白夹爪FR3诊断工具"""
    
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
            print("✅ 连接成功")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def get_error_code_explanation(self, error_code):
        """获取错误码解释"""
        error_explanations = {
            73: "通讯错误 - 夹爪响应超时或指令格式不匹配",
            0: "成功",
            -1: "一般错误",
            -2: "参数错误",
            -3: "设备未就绪",
            -4: "设备繁忙",
            -5: "超时",
            -6: "不支持的功能"
        }
        return error_explanations.get(error_code, f"未知错误码: {error_code}")
    
    def test_basic_configuration(self):
        """测试基础配置"""
        print("\n🔍 1. 基础配置诊断")
        print("-" * 40)
        
        try:
            # 测试夹爪配置
            print("   配置夹爪（大寰兼容模式）...")
            error = self.robot.SetGripperConfig(4, 0)
            print(f"   SetGripperConfig结果: {error} ({self.get_error_code_explanation(error)})")
            
            if error != 0:
                return False
            
            time.sleep(1)
            
            # 获取当前配置
            try:
                config = self.robot.GetGripperConfig()
                print(f"   当前夹爪配置: {config}")
            except Exception as e:
                print(f"   获取配置失败: {e}")
            
            # 测试激活
            print("   复位夹爪...")
            error = self.robot.ActGripper(1, 0)
            print(f"   ActGripper(复位)结果: {error} ({self.get_error_code_explanation(error)})")
            
            time.sleep(1)
            
            print("   激活夹爪...")
            error = self.robot.ActGripper(1, 1)  
            print(f"   ActGripper(激活)结果: {error} ({self.get_error_code_explanation(error)})")
            
            time.sleep(2)
            
            return error == 0
            
        except Exception as e:
            print(f"   ❌ 基础配置异常: {e}")
            return False
    
    def test_move_gripper_variations(self):
        """测试不同的MoveGripper参数组合"""
        print("\n🔍 2. MoveGripper参数变化测试")
        print("-" * 40)
        
        # 不同的参数组合
        test_variations = [
            {
                "name": "标准参数",
                "params": (1, 0, 50, 30, 5000, 0, 0, 0, 0, 0)
            },
            {
                "name": "最小参数", 
                "params": (1, 0, 10, 10, 3000, 0, 0, 0, 0, 0)
            },
            {
                "name": "无阻塞模式",
                "params": (1, 0, 30, 20, 5000, 1, 0, 0, 0, 0)  # block=1
            },
            {
                "name": "不同位置",
                "params": (1, 10, 30, 20, 5000, 0, 0, 0, 0, 0)  # pos=10而不是0
            },
            {
                "name": "更长超时",
                "params": (1, 0, 30, 20, 10000, 0, 0, 0, 0, 0)  # maxtime=10000
            }
        ]
        
        success_count = 0
        
        for variation in test_variations:
            try:
                print(f"   测试: {variation['name']}")
                print(f"   参数: {variation['params']}")
                
                error = self.robot.MoveGripper(*variation['params'])
                result = self.get_error_code_explanation(error)
                
                if error == 0:
                    print(f"   ✅ 成功: {result}")
                    success_count += 1
                else:
                    print(f"   ❌ 失败: {result}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ 异常: {e}")
        
        print(f"\n   📊 成功率: {success_count}/{len(test_variations)}")
        return success_count > 0
    
    def test_alternative_gripper_functions(self):
        """测试其他可能的夹爪控制函数"""
        print("\n🔍 3. 替代夹爪控制函数测试")
        print("-" * 40)
        
        # 尝试其他可能的夹爪函数
        alternative_tests = [
            {
                "name": "GetGripperMotionDone",
                "func": lambda: self.robot.GetGripperMotionDone(),
                "description": "检查夹爪运动是否完成"
            },
            {
                "name": "SetGripperMaxCurrent", 
                "func": lambda: self.robot.SetGripperMaxCurrent(1, 100),
                "description": "设置夹爪最大电流"
            }
        ]
        
        for test in alternative_tests:
            try:
                print(f"   测试: {test['name']} - {test['description']}")
                result = test['func']()
                print(f"   结果: {result}")
            except AttributeError:
                print(f"   ⚠️  函数不存在: {test['name']}")
            except Exception as e:
                print(f"   ❌ 执行失败: {e}")
        
        return True
    
    def test_communication_status(self):
        """测试通讯状态"""
        print("\n🔍 4. 通讯状态诊断")
        print("-" * 40)
        
        try:
            # 获取机械臂状态
            print("   获取机械臂状态...")
            try:
                robot_state = self.robot.GetRobotRealTimeState()
                print(f"   机械臂实时状态: 部分信息获取成功")
            except Exception as e:
                print(f"   获取机械臂状态失败: {e}")
            
            # 尝试获取末端通讯状态
            print("   检查末端通讯...")
            try:
                # 尝试获取末端负载信息（如果存在此函数）
                payload = self.robot.GetRobotCurPayload()
                print(f"   当前负载: {payload}")
            except Exception as e:
                print(f"   获取负载信息失败: {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 通讯诊断异常: {e}")
            return False
    
    def provide_advanced_solutions(self):
        """提供高级解决方案"""
        print("\n💡 高级解决方案建议")
        print("=" * 50)
        
        print("基于诊断结果，错误码73的可能原因和解决方案:")
        print()
        
        print("🔧 原因分析:")
        print("1. 乐白夹爪需要特定的Modbus指令格式")
        print("2. FR3的MoveGripper可能不完全兼容乐白协议")
        print("3. 夹爪可能需要特殊的初始化序列")
        print()
        
        print("🚀 解决方案:")
        print("方案A: WebApp配置法（推荐尝试）")
        print("  1. 在FR3 WebApp中进入'外设配置'")
        print("  2. 选择'夹爪设备'，厂商选择'乐白'")
        print("  3. 完成配置后再使用代码控制")
        print()
        
        print("方案B: 直接Modbus通讯法")
        print("  1. 查找FR3是否支持WriteModbusRegister函数")
        print("  2. 直接写入乐白夹爪的Modbus寄存器:")
        print("     - 40000 (0x9C40): 位置控制 (0-100)")
        print("     - 40001 (0x9C41): 力度控制 (0-100)")
        print()
        
        print("方案C: 联系技术支持")
        print("  1. 联系法奥意威确认乐白夹爪支持状态")
        print("  2. 获取专门的乐白夹爪驱动或配置文件")
        print("  3. 确认FR3固件版本是否支持乐白夹爪")
        print()
        
        print("方案D: 固件和驱动检查")
        print("  1. 确认FR3固件版本")
        print("  2. 检查是否需要更新夹爪驱动")
        print("  3. 验证乐白夹爪固件版本")
    
    def comprehensive_diagnosis(self):
        """综合诊断"""
        print("🔬 乐白夹爪FR3深度诊断工具")
        print("专门解决错误码73问题")
        print("=" * 60)
        
        # 1. 连接机械臂
        if not self.connect_robot():
            return False
        
        # 2. 基础配置测试
        basic_ok = self.test_basic_configuration()
        
        # 3. MoveGripper变化测试
        move_ok = self.test_move_gripper_variations()
        
        # 4. 替代函数测试
        alt_ok = self.test_alternative_gripper_functions()
        
        # 5. 通讯状态测试
        comm_ok = self.test_communication_status()
        
        # 6. 提供解决方案
        self.provide_advanced_solutions()
        
        print(f"\n📊 诊断总结:")
        print(f"基础配置: {'✅' if basic_ok else '❌'}")
        print(f"MoveGripper测试: {'✅' if move_ok else '❌'}")
        print(f"替代函数: {'✅' if alt_ok else '❌'}")
        print(f"通讯状态: {'✅' if comm_ok else '❌'}")
        
        return basic_ok and move_ok

def main():
    """主函数"""
    print("🔬 乐白夹爪FR3高级诊断工具")
    print("专门分析错误码73问题")
    print("=" * 50)
    
    diagnostic = LebaiFR3DiagnosticTool()
    
    try:
        success = diagnostic.comprehensive_diagnosis()
        
        if success:
            print("\n🎊 诊断完成，部分功能正常")
        else:
            print("\n😞 诊断发现问题，请参考解决方案")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断诊断")
    except Exception as e:
        print(f"\n\n❌ 诊断过程异常: {e}")
    finally:
        print("\n👋 诊断结束")

if __name__ == "__main__":
    main()
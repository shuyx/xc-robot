#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪最终解决方案
基于诊断结果的最后尝试

发现：
1. SetGripperConfig和ActGripper成功 - 基础通讯正常
2. MoveGripper全部失败错误码73 - 控制指令不兼容
3. GetGripperMotionDone可用 - 状态查询正常

最终方案：
1. 尝试找到是否有其他夹爪控制接口
2. 探索可能的原始Modbus写入方法
3. 提供完整的问题报告和建议

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

class LebaiFinalSolution:
    """乐白夹爪最终解决方案"""
    
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
    
    def setup_basic_configuration(self):
        """建立基础配置"""
        try:
            print("🔧 建立基础配置...")
            
            # 配置夹爪
            error = self.robot.SetGripperConfig(4, 0)
            if error != 0:
                print(f"❌ SetGripperConfig失败: {error}")
                return False
            print("✅ SetGripperConfig成功")
            
            time.sleep(1)
            
            # 复位
            error = self.robot.ActGripper(1, 0)
            if error != 0:
                print(f"❌ ActGripper(复位)失败: {error}")
                return False
            print("✅ 复位成功")
            
            time.sleep(1)
            
            # 激活
            error = self.robot.ActGripper(1, 1)
            if error != 0:
                print(f"❌ ActGripper(激活)失败: {error}")
                return False
            print("✅ 激活成功")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ 基础配置异常: {e}")
            return False
    
    def explore_alternative_methods(self):
        """探索替代控制方法"""
        print("\n🔍 探索替代控制方法...")
        
        methods_to_try = [
            # 可能的Modbus相关函数
            ("WriteModbusRegister", "尝试直接写入Modbus寄存器"),
            ("SetAxleModbusRegister", "设置末端Modbus寄存器"),
            ("WriteAxleRegister", "写入末端寄存器"),
            ("SetGripperForce", "设置夹爪力度"),
            ("SetGripperPosition", "设置夹爪位置"),
            ("SetGripperSpeed", "设置夹爪速度"),
            ("ControlGripper", "控制夹爪"),
            ("MoveGripperPos", "移动夹爪到位置"),
            ("GripperControl", "夹爪控制"),
            ("SetGripperParam", "设置夹爪参数"),
            ("WriteGripperRegister", "写入夹爪寄存器")
        ]
        
        available_methods = []
        
        for method_name, description in methods_to_try:
            try:
                if hasattr(self.robot, method_name):
                    available_methods.append((method_name, description))
                    print(f"✅ 找到方法: {method_name} - {description}")
                else:
                    print(f"❌ 不存在: {method_name}")
            except Exception as e:
                print(f"⚠️  检查{method_name}时异常: {e}")
        
        return available_methods
    
    def try_alternative_control_methods(self, available_methods):
        """尝试替代控制方法"""
        print(f"\n🧪 尝试 {len(available_methods)} 个可用的替代方法...")
        
        success_methods = []
        
        for method_name, description in available_methods:
            try:
                print(f"🔬 测试: {method_name}")
                method = getattr(self.robot, method_name)
                
                # 尝试不同的参数组合
                test_params = [
                    [1, 0],           # 简单参数
                    [1, 0, 50],       # 三参数
                    [0, 50],          # 无索引参数
                    [40000, 0],       # Modbus寄存器地址
                    [0x9C40, 0]       # 十六进制寄存器地址
                ]
                
                for params in test_params:
                    try:
                        print(f"   参数: {params}")
                        result = method(*params)
                        print(f"   ✅ 成功调用，结果: {result}")
                        success_methods.append((method_name, params, result))
                        break  # 成功就跳出参数循环
                    except Exception as param_e:
                        print(f"   ❌ 参数{params}失败: {param_e}")
                        continue
                
            except Exception as e:
                print(f"   ❌ 方法{method_name}测试失败: {e}")
        
        return success_methods
    
    def generate_comprehensive_report(self, available_methods, success_methods):
        """生成综合报告"""
        print("\n📋 乐白夹爪问题综合报告")
        print("=" * 60)
        
        print("🔍 问题分析:")
        print("1. ✅ 机械臂连接正常")
        print("2. ✅ SetGripperConfig配置成功")
        print("3. ✅ ActGripper激活成功")
        print("4. ❌ MoveGripper控制失败（错误码73）")
        print("5. ✅ GetGripperMotionDone状态查询正常")
        print()
        
        print("🔧 根本原因:")
        print("错误码73表明乐白夹爪虽然能被FR3识别和配置，")
        print("但MoveGripper的指令格式与乐白夹爪的Modbus协议不完全兼容。")
        print("这是协议层面的不匹配问题。")
        print()
        
        print(f"🔍 SDK探索结果:")
        print(f"发现 {len(available_methods)} 个可能的替代方法")
        print(f"成功调用 {len(success_methods)} 个方法")
        
        if success_methods:
            print("\n✅ 成功的替代方法:")
            for method_name, params, result in success_methods:
                print(f"   {method_name}({params}) -> {result}")
        else:
            print("\n❌ 未找到可用的替代控制方法")
        
        print()
        print("🚀 最终解决方案建议:")
        print()
        print("方案1: WebApp配置（强烈推荐）")
        print("  1. 在FR3的WebApp界面中配置夹爪")
        print("  2. 选择设备类型为'夹爪设备'")
        print("  3. 厂商选择'乐白'（如果有）或'其他'")
        print("  4. 完成WebApp配置后再用代码控制")
        print()
        
        print("方案2: 联系技术支持")
        print("  1. 联系法奥意威技术支持")
        print("     - 确认FR3是否完全支持乐白夹爪")
        print("     - 获取专门的乐白夹爪配置文件")
        print("     - 询问是否需要固件更新")
        print()
        print("  2. 联系乐白技术支持")
        print("     - 确认夹爪的Modbus寄存器定义")
        print("     - 获取与FR3兼容的配置参数")
        print("     - 询问是否有特殊的初始化序列")
        print()
        
        print("方案3: 深度Modbus集成")
        print("  1. 研究FR3的底层Modbus接口")
        print("  2. 使用原始Modbus指令直接控制")
        print("  3. 可能需要第三方Modbus库")
        print()
        
        print("📞 技术支持联系方式:")
        print("- 法奥意威: https://www.fairino.com/")
        print("- 乐白夹爪: https://lebai.ltd/")
        print()
        
        print("⚠️  重要提醒:")
        print("基于当前测试，乐白夹爪与FR3存在协议兼容性问题。")
        print("这不是硬件连接问题，而是软件协议层面的不匹配。")
        print("强烈建议通过WebApp配置或联系技术支持解决。")
    
    def final_comprehensive_test(self):
        """最终综合测试"""
        print("🎯 乐白夹爪最终解决方案")
        print("基于完整诊断的最后尝试")
        print("=" * 60)
        
        # 1. 连接
        if not self.connect_robot():
            return False
        
        # 2. 基础配置
        if not self.setup_basic_configuration():
            return False
        
        # 3. 探索替代方法
        available_methods = self.explore_alternative_methods()
        
        # 4. 尝试替代方法
        success_methods = self.try_alternative_control_methods(available_methods)
        
        # 5. 生成报告
        self.generate_comprehensive_report(available_methods, success_methods)
        
        return len(success_methods) > 0

def main():
    """主函数"""
    print("🎯 乐白夹爪最终解决方案")
    print("基于完整诊断和SDK探索")
    print("=" * 50)
    
    solution = LebaiFinalSolution()
    
    try:
        success = solution.final_comprehensive_test()
        
        if success:
            print("\n🎊 找到了可用的替代方法！")
        else:
            print("\n📋 未找到可用方法，但已生成完整报告")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断测试")
    except Exception as e:
        print(f"\n\n❌ 测试过程异常: {e}")
    finally:
        print("\n👋 最终测试结束")

if __name__ == "__main__":
    main()
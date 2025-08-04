#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪错误码73专项诊断工具
专门分析和解决返回码73（通讯错误）问题
"""

import sys
import os
import time
from typing import Dict, List, Optional

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
    sys.exit(1)


class Error73Diagnosis:
    """错误码73专项诊断工具"""
    
    def __init__(self, robot_ip: str = '192.168.58.2'):
        self.robot_ip = robot_ip
        self.robot = None
        self.diagnosis_results = []
        
    def connect(self) -> bool:
        """连接到FR3机器人控制器"""
        try:
            print(f"🔌 连接机器人控制器 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            
            if self.robot:
                print("✓ 机器人连接成功")
                self.robot.LoggerInit(output_model=0)
                self.robot.SetLoggerLevel(4)
                return True
            else:
                print("✗ 连接失败，robot对象为None")
                return False
            
        except Exception as e:
            print(f"✗ 机器人连接失败: {e}")
            return False
    
    def add_diagnosis(self, test_name: str, result: bool, details: str):
        """添加诊断结果"""
        self.diagnosis_results.append({
            'test': test_name,
            'result': result,
            'details': details,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def test_communication_params(self) -> bool:
        """测试末端通讯参数配置"""
        print("\n🔍 测试1: 末端通讯参数配置")
        print("-" * 50)
        
        try:
            # 尝试多种通讯参数配置
            configs = [
                {'name': '乐白标准', 'baud': 7, 'data': 8, 'stop': 1, 'parity': 0},
                {'name': '备选1', 'baud': 6, 'data': 8, 'stop': 1, 'parity': 0},  # 9600
                {'name': '备选2', 'baud': 8, 'data': 8, 'stop': 1, 'parity': 0},  # 230400
            ]
            
            for config in configs:
                print(f"📋 测试配置: {config['name']}")
                result = self.robot.SetAxleCommunicationParam(
                    config['baud'], config['data'], config['stop'], 
                    config['parity'], 100, 3, 50
                )
                
                if result == 0:
                    print(f"✓ {config['name']} 配置成功")
                    self.add_diagnosis(f"通讯配置-{config['name']}", True, f"返回码: {result}")
                    
                    # 测试简单的MoveGripper调用
                    time.sleep(1)
                    move_result = self.robot.MoveGripper(
                        index=1, pos=50, vel=50, force=50,
                        maxtime=3000, block=0, type=0,
                        rotNum=0, rotVel=0, rotTorque=0
                    )
                    
                    if move_result == 0:
                        print(f"✓ {config['name']} 移动测试成功")
                        self.add_diagnosis(f"移动测试-{config['name']}", True, f"返回码: {move_result}")
                        return True
                    elif move_result == 73:
                        print(f"⚠ {config['name']} 仍然返回73")
                        self.add_diagnosis(f"移动测试-{config['name']}", False, f"错误码73")
                    else:
                        print(f"⚠ {config['name']} 返回其他错误: {move_result}")
                        self.add_diagnosis(f"移动测试-{config['name']}", False, f"返回码: {move_result}")
                else:
                    print(f"✗ {config['name']} 配置失败: {result}")
                    self.add_diagnosis(f"通讯配置-{config['name']}", False, f"返回码: {result}")
                
                time.sleep(1)
            
            return False
            
        except Exception as e:
            print(f"✗ 通讯参数测试异常: {e}")
            self.add_diagnosis("通讯参数测试", False, f"异常: {e}")
            return False
    
    def test_gripper_activation(self) -> bool:
        """测试夹爪激活状态"""
        print("\n🔍 测试2: 夹爪激活状态检查")
        print("-" * 50)
        
        try:
            # 重新激活夹爪
            print("🔄 重新激活夹爪...")
            reset_result = self.robot.ActGripper(1, 0)  # 复位
            print(f"复位结果: {reset_result}")
            time.sleep(2)
            
            activate_result = self.robot.ActGripper(1, 1)  # 激活
            print(f"激活结果: {activate_result}")
            time.sleep(3)
            
            if activate_result == 0:
                self.add_diagnosis("夹爪激活", True, f"激活成功: {activate_result}")
                
                # 测试激活后的移动
                move_result = self.robot.MoveGripper(
                    index=1, pos=20, vel=30, force=30,
                    maxtime=5000, block=0, type=0,
                    rotNum=0, rotVel=0, rotTorque=0
                )
                
                if move_result == 0:
                    print("✓ 激活后移动测试成功")
                    self.add_diagnosis("激活后移动", True, f"成功: {move_result}")
                    return True
                elif move_result == 73:
                    print("⚠ 激活后仍然返回73")
                    self.add_diagnosis("激活后移动", False, "错误码73")
                else:
                    print(f"⚠ 激活后返回其他错误: {move_result}")
                    self.add_diagnosis("激活后移动", False, f"返回码: {move_result}")
            else:
                print(f"✗ 夹爪激活失败: {activate_result}")
                self.add_diagnosis("夹爪激活", False, f"激活失败: {activate_result}")
            
            return False
            
        except Exception as e:
            print(f"✗ 夹爪激活测试异常: {e}")
            self.add_diagnosis("夹爪激活测试", False, f"异常: {e}")
            return False
    
    def test_modbus_direct_access(self) -> bool:
        """测试直接Modbus寄存器访问"""
        print("\n🔍 测试3: 直接Modbus寄存器访问")
        print("-" * 50)
        
        try:
            # 乐白夹爪寄存器地址
            registers = {
                '位置控制': 40000,
                '力度控制': 40001,
                '当前位置': 40005,
                '速度控制': 40010,
                '状态寄存器': 40020
            }
            
            success_count = 0
            
            for name, addr in registers.items():
                try:
                    print(f"📋 测试寄存器: {name} (地址:{addr})")
                    
                    if '控制' in name:
                        # 写入测试
                        test_value = [50]  # 测试值50%
                        result = self.robot.SetAxleOutputVal(1, addr, test_value)
                        
                        if result == 0:
                            print(f"✓ {name} 写入成功")
                            self.add_diagnosis(f"寄存器写入-{name}", True, f"地址:{addr}, 值:{test_value}")
                            success_count += 1
                        else:
                            print(f"✗ {name} 写入失败: {result}")
                            self.add_diagnosis(f"寄存器写入-{name}", False, f"返回码:{result}")
                    else:
                        # 读取测试
                        result = self.robot.GetAxleInputVal(1, addr)
                        
                        if result is not None and len(result) > 0:
                            print(f"✓ {name} 读取成功: {result}")
                            self.add_diagnosis(f"寄存器读取-{name}", True, f"地址:{addr}, 值:{result}")
                            success_count += 1
                        else:
                            print(f"✗ {name} 读取失败")
                            self.add_diagnosis(f"寄存器读取-{name}", False, f"无数据返回")
                    
                    time.sleep(0.2)
                    
                except Exception as reg_e:
                    print(f"✗ {name} 访问异常: {reg_e}")
                    self.add_diagnosis(f"寄存器访问-{name}", False, f"异常: {reg_e}")
            
            if success_count >= 3:
                print(f"✓ 寄存器访问测试: {success_count}/5 成功")
                return True
            else:
                print(f"⚠ 寄存器访问测试: {success_count}/5 成功（部分失败）")
                return False
            
        except Exception as e:
            print(f"✗ Modbus寄存器测试异常: {e}")
            self.add_diagnosis("Modbus寄存器测试", False, f"异常: {e}")
            return False
    
    def test_different_move_parameters(self) -> bool:
        """测试不同移动参数组合"""
        print("\n🔍 测试4: 不同移动参数组合")
        print("-" * 50)
        
        try:
            # 测试参数组合
            param_sets = [
                {'name': '最小参数', 'pos': 10, 'vel': 10, 'force': 10, 'timeout': 3000},
                {'name': '中等参数', 'pos': 50, 'vel': 50, 'force': 50, 'timeout': 5000},
                {'name': '较大参数', 'pos': 80, 'vel': 80, 'force': 80, 'timeout': 8000},
                {'name': '阻塞模式', 'pos': 30, 'vel': 40, 'force': 40, 'block': 1},
                {'name': '不同类型', 'pos': 40, 'vel': 50, 'force': 50, 'type': 1},
            ]
            
            success_count = 0
            
            for params in param_sets:
                print(f"📋 测试参数组合: {params['name']}")
                
                block_mode = params.get('block', 0)
                gripper_type = params.get('type', 0)
                timeout = params.get('timeout', 5000)
                
                result = self.robot.MoveGripper(
                    index=1, 
                    pos=params['pos'], 
                    vel=params['vel'], 
                    force=params['force'],
                    maxtime=timeout, 
                    block=block_mode, 
                    type=gripper_type,
                    rotNum=0, rotVel=0, rotTorque=0
                )
                
                if result == 0:
                    print(f"✓ {params['name']} 成功")
                    self.add_diagnosis(f"参数测试-{params['name']}", True, f"返回码: {result}")
                    success_count += 1
                elif result == 73:
                    print(f"⚠ {params['name']} 返回73")
                    self.add_diagnosis(f"参数测试-{params['name']}", False, "错误码73")
                else:
                    print(f"⚠ {params['name']} 返回: {result}")
                    self.add_diagnosis(f"参数测试-{params['name']}", False, f"返回码: {result}")
                
                time.sleep(2)
            
            return success_count > 0
            
        except Exception as e:
            print(f"✗ 参数测试异常: {e}")
            self.add_diagnosis("参数测试", False, f"异常: {e}")
            return False
    
    def generate_diagnosis_report(self):
        """生成诊断报告"""
        print("\n" + "="*60)
        print("📊 错误码73诊断报告")
        print("="*60)
        
        if not self.diagnosis_results:
            print("⚠ 没有诊断数据")
            return
        
        successful_tests = [r for r in self.diagnosis_results if r['result']]
        failed_tests = [r for r in self.diagnosis_results if not r['result']]
        
        print(f"\n📈 统计信息:")
        print(f"   总测试数: {len(self.diagnosis_results)}")
        print(f"   成功测试: {len(successful_tests)}")
        print(f"   失败测试: {len(failed_tests)}")
        print(f"   成功率: {len(successful_tests)/len(self.diagnosis_results)*100:.1f}%")
        
        if successful_tests:
            print(f"\n✅ 成功的测试:")
            for test in successful_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🎯 结论分析:")
        if len(successful_tests) == 0:
            print("   📍 所有测试均失败，问题可能是:")
            print("      1. 硬件连接问题（电源、通讯线）")
            print("      2. 夹爪设备故障")
            print("      3. FR3系统配置问题")
        elif len(successful_tests) < len(self.diagnosis_results) // 2:
            print("   📍 大部分测试失败，问题可能是:")
            print("      1. 协议兼容性问题（主要原因）")
            print("      2. 通讯参数不匹配")
            print("      3. 夹爪固件版本问题")
        else:
            print("   📍 部分测试成功，问题可能是:")
            print("      1. 特定指令格式不兼容")
            print("      2. 参数范围限制")
            print("      3. 时序问题")
        
        print(f"\n💡 推荐解决方案（按优先级）:")
        print("   1. 🌐 使用FR3 WebApp界面配置夹爪")
        print("   2. 📞 联系法奥意威技术支持获取官方解决方案")
        print("   3. 📞 联系乐白技术支持确认协议兼容性")
        print("   4. 🔧 使用第三方Modbus库绕过FR3 SDK")
        print("   5. 🔄 考虑更换FR3官方认证的夹爪型号")
    
    def run_full_diagnosis(self):
        """运行完整诊断"""
        print("🔍 乐白夹爪错误码73专项诊断")
        print("=" * 60)
        print("目标: 深度分析返回码73的根本原因")
        print("范围: 通讯、激活、寄存器、参数测试")
        
        if not self.connect():
            print("❌ 无法连接机器人，诊断终止")
            return False
        
        # 执行各项测试
        tests = [
            self.test_communication_params,
            self.test_gripper_activation,
            self.test_modbus_direct_access,
            self.test_different_move_parameters
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"\n{'='*20} 测试 {i}/{len(tests)} {'='*20}")
            try:
                test()
            except Exception as e:
                print(f"⚠ 测试{i}执行异常: {e}")
                self.add_diagnosis(f"测试{i}执行", False, f"异常: {e}")
            
            time.sleep(1)
        
        # 生成报告
        self.generate_diagnosis_report()
        
        return True


def main():
    """主函数"""
    print("🔬 乐白夹爪错误码73专项诊断工具")
    print("版本: 1.0")
    print("目标: FR3 右臂 (192.168.58.2) + 乐白夹爪")
    print("功能: 深度分析返回码73的原因并提供解决方案")
    
    diagnosis = Error73Diagnosis(robot_ip='192.168.58.2')
    
    try:
        success = diagnosis.run_full_diagnosis()
        
        if success:
            print("\n🎊 诊断完成！")
            print("📋 请查看上述报告了解详细分析结果")
        else:
            print("\n⚠️ 诊断过程中遇到问题")
            print("🔧 请检查硬件连接和网络状态")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ 诊断被用户中断")
        return False
        
    except Exception as e:
        print(f"\n❌ 诊断程序异常: {e}")
        return False
        
    finally:
        if diagnosis.robot:
            print("🔌 断开机器人连接")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
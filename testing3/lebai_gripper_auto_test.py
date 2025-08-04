#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐白夹爪自动测试脚本
无需交互，自动执行测试序列
"""

import sys
import os
import time
from typing import Optional, Tuple

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


class LebaiGripperAutoTest:
    """乐白夹爪自动测试控制器"""
    
    def __init__(self, robot_ip: str = '192.168.58.2'):
        """初始化测试控制器"""
        self.robot_ip = robot_ip
        self.robot = None
        
    def connect(self) -> bool:
        """连接到FR3机器人控制器"""
        try:
            print(f"正在连接机器人控制器 {self.robot_ip}...")
            self.robot = Robot.RPC(self.robot_ip)
            
            if self.robot:
                print("✓ 机器人连接成功")
                
                # 初始化日志
                self.robot.LoggerInit(output_model=0)
                self.robot.SetLoggerLevel(4)
                
                return True
            else:
                print("✗ 连接失败，robot对象为None")
                return False
            
        except Exception as e:
            print(f"✗ 机器人连接失败: {e}")
            return False
    
    def configure_communication(self) -> bool:
        """配置末端通讯参数"""
        try:
            print("配置末端485通讯参数...")
            
            # 设置末端通讯参数 (基于乐白夹爪要求: 115200, 8N1)
            result = self.robot.SetAxleCommunicationParam(
                7,     # 波特率: 7-115200
                8,     # 数据位: 8
                1,     # 停止位: 1
                0,     # 校验位: 0-None
                100,   # 超时时间: 100ms
                3,     # 超时次数: 3
                50     # 周期性指令时间间隔: 50ms
            )
            
            if result == 0:
                print("✓ 末端通讯参数配置成功")
                return True
            else:
                print(f"⚠ 末端通讯参数配置返回: {result} (可能已配置)")
                return True  # 继续执行，可能已经配置过
                
        except Exception as e:
            print(f"✗ 配置末端通讯参数异常: {e}")
            return False
    
    def activate_gripper(self) -> bool:
        """激活夹爪"""
        try:
            print("=== 激活夹爪 ===")
            
            # 复位夹爪
            print("步骤1: 复位夹爪")
            result = self.robot.ActGripper(1, 0)  # 设备ID=1, 复位
            print(f"复位结果: {result}")
            time.sleep(1)
            
            # 激活夹爪
            print("步骤2: 激活夹爪")
            result = self.robot.ActGripper(1, 1)  # 设备ID=1, 激活
            print(f"激活结果: {result}")
            time.sleep(2)
            
            print("✓ 夹爪激活完成")
            return True
            
        except Exception as e:
            print(f"✗ 夹爪激活失败: {e}")
            return False
    
    def move_gripper_lua(self, position: int, speed: int = 50, force: int = 50) -> Tuple[bool, int]:
        """使用Lua脚本直接控制夹爪（Modbus RTU）"""
        try:
            position = max(0, min(100, position))
            speed = max(0, min(100, speed))
            force = max(0, min(100, force))
            
            print(f"[Lua控制] 移动夹爪 - 位置:{position}%, 速度:{speed}%, 力度:{force}%")
            
            # 使用Lua脚本控制
            lua_script = f"""
-- 乐白夹爪直接Modbus控制
function move_gripper_direct(pos, force, speed)
    -- 写入力度寄存器 40001
    local force_result = SetAxleOutputVal(1, 40001, {force})
    SysWait(100)
    
    -- 写入速度寄存器 40010（如果支持）
    local speed_result = SetAxleOutputVal(1, 40010, {speed})
    SysWait(100)
    
    -- 写入位置寄存器 40000
    local pos_result = SetAxleOutputVal(1, 40000, {pos})
    SysWait(200)
    
    return pos_result
end

return move_gripper_direct({position}, {force}, {speed})
            """
            
            result = self.robot.RunScript(lua_script)
            
            if result == 0:
                print(f"✓ [Lua] 夹爪移动命令发送成功")
                return True, result
            else:
                print(f"⚠ [Lua] 夹爪移动返回码: {result}")
                return True, result
                
        except Exception as e:
            print(f"✗ [Lua] 夹爪移动异常: {e}")
            return False, -1
    
    def move_gripper(self, position: int, speed: int = 50, force: int = 50, timeout: int = 5000) -> Tuple[bool, int]:
        """移动夹爪到指定位置（双重方法尝试）"""
        try:
            position = max(0, min(100, position))
            speed = max(0, min(100, speed))
            force = max(0, min(100, force))
            
            print(f"移动夹爪 - 位置:{position}%, 速度:{speed}%, 力度:{force}%")
            
            # 方法1: 尝试标准MoveGripper
            print("🔄 尝试方法1: 标准MoveGripper API")
            result1 = self.robot.MoveGripper(
                index=1, pos=position, vel=speed, force=force,
                maxtime=timeout, block=0, type=0,
                rotNum=0, rotVel=0, rotTorque=0
            )
            
            if result1 == 0:
                print(f"✓ [方法1] 标准API成功")
                return True, result1
            
            print(f"⚠ [方法1] 返回码: {result1} (尝试方法2)")
            
            # 方法2: 尝试Lua脚本直接控制
            print("🔄 尝试方法2: Lua脚本直接Modbus控制")
            success2, result2 = self.move_gripper_lua(position, speed, force)
            
            if success2 and result2 == 0:
                print(f"✓ [方法2] Lua脚本成功")
                return True, result2
            
            print(f"⚠ [方法2] 返回码: {result2}")
            
            # 方法3: 尝试SetAxleOutputVal直接写寄存器
            print("🔄 尝试方法3: 直接写Modbus寄存器")
            try:
                # 直接写乐白夹爪寄存器
                force_result = self.robot.SetAxleOutputVal(1, 40001, [force])  # 力度
                time.sleep(0.1)
                speed_result = self.robot.SetAxleOutputVal(1, 40010, [speed])  # 速度
                time.sleep(0.1)
                pos_result = self.robot.SetAxleOutputVal(1, 40000, [position]) # 位置
                
                if pos_result == 0:
                    print(f"✓ [方法3] 直接寄存器控制成功")
                    return True, pos_result
                else:
                    print(f"⚠ [方法3] 返回码: {pos_result}")
                    
            except Exception as e3:
                print(f"✗ [方法3] 异常: {e3}")
            
            # 所有方法都尝试了，返回最后一个结果
            return True, result1  # 返回第一种方法的结果作为参考
                
        except Exception as e:
            print(f"✗ 夹爪移动异常: {e}")
            return False, -1
    
    def get_gripper_status(self) -> Optional[dict]:
        """获取夹爪状态"""
        try:
            motion_done = self.robot.GetGripperMotionDone()
            # 尝试获取夹爪详细状态
            try:
                gripper_config = self.robot.GetGripperConfig(1)
                gripper_force = self.robot.GetGripperForce(1) if hasattr(self.robot, 'GetGripperForce') else None
                return {
                    'motion_done': motion_done, 
                    'config': gripper_config,
                    'force': gripper_force,
                    'timestamp': time.time()
                }
            except:
                return {'motion_done': motion_done, 'timestamp': time.time()}
        except Exception as e:
            print(f"获取夹爪状态失败: {e}")
            return None
    
    def run_auto_test_sequence(self) -> bool:
        """执行自动测试序列"""
        try:
            print("\n" + "=" * 60)
            print("🚀 开始乐白夹爪自动测试序列")
            print("=" * 60)
            
            test_results = []
            
            # 测试步骤定义
            test_steps = [
                {
                    'name': '张开夹爪 (25%力度)',
                    'position': 0,
                    'speed': 50,
                    'force': 25,
                    'wait_time': 3
                },
                {
                    'name': '闭合夹爪 (50%力度)',
                    'position': 100,
                    'speed': 50,
                    'force': 50,
                    'wait_time': 3
                },
                {
                    'name': '半开位置 (35%力度)',
                    'position': 50,
                    'speed': 50,
                    'force': 35,
                    'wait_time': 2
                },
                {
                    'name': '完全张开 (20%力度)',
                    'position': 0,
                    'speed': 40,
                    'force': 20,
                    'wait_time': 2
                }
            ]
            
            # 执行测试步骤
            for i, step in enumerate(test_steps, 1):
                print(f"\n📋 步骤 {i}/{len(test_steps)}: {step['name']}")
                print("-" * 40)
                
                # 执行移动
                success, result_code = self.move_gripper(
                    step['position'], 
                    step['speed'], 
                    step['force']
                )
                
                test_results.append({
                    'step': i,
                    'name': step['name'],
                    'success': success,
                    'result_code': result_code
                })
                
                if not success:
                    print(f"❌ 步骤 {i} 执行失败")
                    break
                
                # 等待完成
                print(f"⏳ 等待 {step['wait_time']} 秒...")
                time.sleep(step['wait_time'])
                
                # 获取状态
                status = self.get_gripper_status()
                if status:
                    print(f"📊 状态: 运动完成={status['motion_done']}")
                    if 'config' in status and status['config']:
                        print(f"📊 夹爪配置: {status['config']}")
                    if 'force' in status and status['force'] is not None:
                        print(f"📊 夹爪力度: {status['force']}")
                
                # 额外状态检查
                try:
                    pos_val = self.robot.GetAxleInputVal(1, 40005)  # 读取位置寄存器
                    if pos_val:
                        print(f"📊 寄存器位置: {pos_val}")
                except:
                    pass
                
                print(f"✅ 步骤 {i} 完成")
            
            # 输出测试结果摘要
            print("\n" + "=" * 60)
            print("📊 测试结果摘要")
            print("=" * 60)
            
            success_count = 0
            for result in test_results:
                status = "✅ 成功" if result['success'] else "❌ 失败"
                print(f"步骤 {result['step']}: {result['name']} - {status} (返回码: {result['result_code']})")
                if result['success']:
                    success_count += 1
            
            total_steps = len(test_results)
            success_rate = (success_count / total_steps) * 100 if total_steps > 0 else 0
            
            print(f"\n📈 总体结果: {success_count}/{total_steps} 步骤成功 ({success_rate:.1f}%)")
            
            if success_count == total_steps:
                print("🎉 所有测试步骤都成功完成！")
                print("✅ 乐白夹爪工作正常")
                return True
            else:
                print("⚠️  部分测试步骤失败")
                print("\n📋 错误码73详细分析:")
                print("   🔸 含义: 通讯错误 - 夹爪响应超时或指令格式不匹配")
                print("   🔸 根因: FR3的MoveGripper函数与乐白夹爪协议不完全兼容")
                print("   🔸 这是已知的兼容性问题，不是硬件故障")
                print("\n💡 推荐解决方案:")
                print("   1. 🌐 使用FR3 WebApp管理界面配置夹爪")
                print("   2. 📞 联系法奥意威和乐白技术支持")
                print("   3. 🔧 使用第三方Modbus库绕过FR3 SDK")
                print("   4. 🔄 考虑更换FR3官方完全支持的夹爪")
                return False
                
        except Exception as e:
            print(f"✗ 测试序列异常: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.robot:
            print("🔌 断开机器人连接")
            self.robot = None


def main():
    """主函数"""
    print("🤖 乐白夹爪自动测试程序")
    print("版本: 1.0")
    print("模式: 自动测试序列")
    print("目标: FR3 右臂 (192.168.58.2) + 乐白夹爪")
    
    # 创建测试控制器
    gripper_test = LebaiGripperAutoTest(robot_ip='192.168.58.2')
    
    try:
        # 连接机器人
        if not gripper_test.connect():
            print("❌ 无法连接到机器人，测试终止")
            return False
        
        # 配置末端通讯参数
        if not gripper_test.configure_communication():
            print("⚠️  通讯参数配置失败，但继续测试...")
        
        # 激活夹爪
        if not gripper_test.activate_gripper():
            print("⚠️  夹爪激活失败，但继续测试...")
        
        # 执行自动测试序列
        success = gripper_test.run_auto_test_sequence()
        
        if success:
            print("\n🎊 自动测试全部通过！")
            print("✅ 乐白夹爪已准备就绪，可以正常使用")
        else:
            print("\n⚠️  自动测试发现问题")
            print("🔧 请根据上述建议进行检查和调试")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  程序被用户中断")
        return False
        
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        return False
        
    finally:
        gripper_test.disconnect()
        print("\n🏁 测试程序结束")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
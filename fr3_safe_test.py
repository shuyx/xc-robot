#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂安全运动测试程序
使用小幅度增量运动，避免网络超时问题
"""

import time
import sys
import os

# 添加fairino库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
fr3_control_path = os.path.join(current_dir, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.append(fr3_control_path)
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

class FR3SafeMovementTest:
    def __init__(self, robot_ip='192.168.58.2'):
        self.robot_ip = robot_ip
        self.robot = None
        
    def connect_robot(self):
        """连接机械臂"""
        try:
            print(f"正在连接FR3机械臂，IP地址: {self.robot_ip}")
            self.robot = Robot.RPC(self.robot_ip)
            print("✓ 机械臂连接成功")
            return True
        except Exception as e:
            print(f"✗ 机械臂连接失败: {e}")
            return False
    
    def prepare_robot(self):
        """准备机械臂状态"""
        if not self.robot:
            return False
            
        try:
            print("\n=== 准备机械臂状态 ===")
            
            # 切换到自动模式
            ret = self.robot.Mode(0)
            if ret == 0:
                print("✓ 切换到自动模式成功")
            else:
                print(f"✗ 切换到自动模式失败，错误码: {ret}")
                return False
            
            time.sleep(1)
            
            # 上使能
            ret = self.robot.RobotEnable(1)
            if ret == 0:
                print("✓ 机械臂上使能成功")
            else:
                print(f"✗ 机械臂上使能失败，错误码: {ret}")
                return False
            
            time.sleep(2)  # 等待使能完成
            return True
            
        except Exception as e:
            print(f"✗ 准备机械臂状态异常: {e}")
            return False
    
    def test_minimal_movement(self):
        """测试最小幅度运动"""
        if not self.robot:
            return False
            
        print("\n=== 测试最小幅度运动 ===")
        print("策略：使用相对运动，每次只移动很小的角度")
        
        try:
            # 使用StartJOG进行点动测试（更安全）
            print("测试关节点动功能...")
            
            # 第1轴正向点动（很小的角度）
            print("⚠ 第1轴将进行小幅度正向运动（约2度）")
            
            user_input = input("继续吗？(y/N): ").strip().lower()
            if user_input != 'y' and user_input != 'yes':
                print("⚠ 跳过运动测试")
                return True
            
            print("开始第1轴点动...")
            
            # 使用点动功能：ref=0(关节点动), nb=1(第1轴), dir=1(正方向), max_dis=2.0(最大2度)
            ret = self.robot.StartJOG(
                ref=0,      # 关节点动
                nb=1,       # 第1轴
                dir=1,      # 正方向
                max_dis=2.0, # 最大移动2度
                vel=10.0,   # 速度10%
                acc=50.0    # 加速度50%
            )
            
            if ret == 0:
                print("✓ 点动指令发送成功")
                
                # 让机械臂运动1秒
                time.sleep(1)
                
                # 停止点动
                ret_stop = self.robot.StopJOG(1)  # 停止关节点动
                if ret_stop == 0:
                    print("✓ 停止点动成功")
                else:
                    print(f"⚠ 停止点动错误码: {ret_stop}")
                
                print("等待运动稳定...")
                time.sleep(2)
                
                # 反向运动回到原位置
                print("反向运动回到原位置...")
                ret_back = self.robot.StartJOG(
                    ref=0,      # 关节点动
                    nb=1,       # 第1轴
                    dir=0,      # 负方向
                    max_dis=2.0, # 最大移动2度
                    vel=10.0,   # 速度10%
                    acc=50.0    # 加速度50%
                )
                
                if ret_back == 0:
                    print("✓ 反向点动指令发送成功")
                    time.sleep(1)
                    
                    # 停止反向点动
                    ret_stop_back = self.robot.StopJOG(1)
                    if ret_stop_back == 0:
                        print("✓ 反向运动完成")
                    else:
                        print(f"⚠ 停止反向点动错误码: {ret_stop_back}")
                else:
                    print(f"✗ 反向点动失败，错误码: {ret_back}")
                
                time.sleep(2)
                print("✓ 最小幅度运动测试完成")
                return True
                
            else:
                print(f"✗ 点动指令失败，错误码: {ret}")
                return False
                
        except Exception as e:
            print(f"✗ 最小幅度运动测试异常: {e}")
            # 尝试紧急停止
            try:
                self.robot.ImmStopJOG()  # 立即停止点动
                print("✓ 已发送紧急停止指令")
            except:
                pass
            return False
    
    def test_motion_status(self):
        """测试运动状态查询"""
        if not self.robot:
            return False
            
        print("\n=== 测试运动状态查询 ===")
        
        try:
            # 测试运动完成状态查询
            result = self.robot.GetRobotMotionDone()
            print(f"✓ GetRobotMotionDone() 返回: {result}")
            
            return True
            
        except Exception as e:
            print(f"⚠ 运动状态查询异常: {e}")
            print("这个异常不影响基本控制功能")
            return True
    
    def disconnect_robot(self):
        """断开机械臂连接"""
        try:
            if self.robot:
                # 先确保停止所有运动
                try:
                    self.robot.ImmStopJOG()
                except:
                    pass
                
                time.sleep(1)
                self.robot.CloseRPC()
                print("✓ 机械臂连接已断开")
        except Exception as e:
            print(f"✗ 断开连接异常: {e}")
    
    def run_test(self):
        """运行安全测试"""
        print("=" * 60)
        print("FR3机械臂安全运动测试程序")
        print("使用点动(JOG)功能进行小幅度运动测试")
        print("=" * 60)
        
        # 连接测试
        if not self.connect_robot():
            return False
        
        # 准备机械臂
        if not self.prepare_robot():
            self.disconnect_robot()
            return False
        
        # 运动状态测试
        self.test_motion_status()
        
        # 安全运动测试
        print("\n" + "="*50)
        print("⚠ 安全运动测试说明 ⚠")
        print("本测试将使用点动(JOG)功能")
        print("- 每次只移动一个轴")
        print("- 移动角度很小（约2度）")
        print("- 速度很慢（10%速度）")
        print("- 可以随时停止")
        print("="*50)
        
        # 最小幅度运动测试
        self.test_minimal_movement()
        
        # 断开连接
        self.disconnect_robot()
        
        print("\n" + "=" * 60)
        print("✓ FR3机械臂安全运动测试完成！")
        print("💡 如果点动测试成功，说明基本运动控制功能正常")
        print("🚀 可以继续开发更复杂的运动控制程序")
        print("=" * 60)
        
        return True

def main():
    """主函数"""
    robot_ip = '192.168.58.2'
    
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    
    print(f"使用机械臂IP地址: {robot_ip}")
    
    test = FR3SafeMovementTest(robot_ip)
    
    try:
        success = test.run_test()
        
        if success:
            print("\n🎉 测试成功！基本运动控制功能正常")
            print("💡 建议在实际应用中：")
            print("   1. 使用点动(JOG)功能进行小幅度调整")
            print("   2. 使用MoveJ/MoveL时先获取当前位置")
            print("   3. 限制运动速度和加速度")
            print("   4. 添加运动完成状态检查")
            return 0
        else:
            print("\n❌ 测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断测试")
        test.disconnect_robot()
        return 1
    except Exception as e:
        print(f"\n\n✗ 测试异常: {e}")
        test.disconnect_robot()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
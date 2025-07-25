#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂连接和运动测试程序
集成连接测试、安全运动测试和标准运动测试
兼容原有的fr3_simple_test.py接口
"""

import time
import sys
import os

# 强制设置到项目根目录
script_path = os.path.abspath(__file__)
tests_dir = os.path.dirname(script_path)
project_root = os.path.dirname(tests_dir)
os.chdir(project_root)

# 添加fr3_control路径
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

class FR3ComprehensiveTest:
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
    
    def test_basic_functions(self):
        """测试基本功能"""
        if not self.robot:
            return False
            
        print("\n=== 测试基本功能 ===")
        
        # SDK版本
        try:
            result = self.robot.GetSDKVersion()
            print(f"✓ SDK版本: {result}")
        except Exception as e:
            print(f"⚠ GetSDKVersion() 异常: {e}")
        
        # 控制器IP
        try:
            result = self.robot.GetControllerIP()
            print(f"✓ 控制器IP: {result}")
        except Exception as e:
            print(f"⚠ GetControllerIP() 异常: {e}")
        
        return True
    
    def prepare_robot(self):
        """准备机械臂（模式切换和使能）"""
        if not self.robot:
            return False
            
        try:
            print("\n=== 准备机械臂状态 ===")
            
            # 自动模式
            ret = self.robot.Mode(0)
            if ret == 0:
                print("✓ 切换到自动模式")
            else:
                print(f"⚠ 模式切换错误码: {ret}")
            
            time.sleep(1)
            
            # 上使能
            ret = self.robot.RobotEnable(1)
            if ret == 0:
                print("✓ 机械臂已使能")
            else:
                print(f"⚠ 使能错误码: {ret}")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"✗ 准备机械臂异常: {e}")
            return False
    
    def test_jog_movement(self):
        """测试点动运动（安全）"""
        if not self.robot:
            return False
            
        print("\n=== 安全点动测试 ===")
        print("使用JOG功能进行小幅度运动（2度）")
        
        try:
            print("⚠ 第1轴将进行小幅度运动")
            user_input = input("继续点动测试？(y/N): ").strip().lower()
            if user_input != 'y':
                print("⚠ 跳过点动测试")
                return True
            
            # 正向点动
            print("开始正向点动...")
            ret = self.robot.StartJOG(
                ref=0,      # 关节点动
                nb=1,       # 第1轴
                dir=1,      # 正方向
                max_dis=2.0, # 2度
                vel=10.0,   # 10%速度
                acc=50.0    # 50%加速度
            )
            
            if ret == 0:
                print("✓ 点动指令成功")
                time.sleep(1)
                
                # 停止点动
                self.robot.StopJOG(1)
                print("✓ 停止点动")
                time.sleep(1)
                
                # 反向回到原位
                print("反向回到原位...")
                ret_back = self.robot.StartJOG(ref=0, nb=1, dir=0, max_dis=2.0, vel=10.0, acc=50.0)
                if ret_back == 0:
                    time.sleep(1)
                    self.robot.StopJOG(1)
                    print("✓ 点动测试完成")
                
                return True
            else:
                print(f"✗ 点动失败，错误码: {ret}")
                return False
                
        except Exception as e:
            print(f"✗ 点动测试异常: {e}")
            try:
                self.robot.ImmStopJOG()
            except:
                pass
            return False
    
    def test_movej_movement(self):
        """测试MoveJ运动（标准）"""
        if not self.robot:
            return False
            
        print("\n=== 标准MoveJ测试 ===")
        print("使用MoveJ移动到安全位置")
        
        try:
            safe_position = [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]
            print(f"目标位置: {safe_position}")
            print("⚠ 注意：机械臂将进行较大幅度运动")
            
            user_input = input("继续MoveJ测试？(y/N): ").strip().lower()
            if user_input != 'y':
                print("⚠ 跳过MoveJ测试")
                return True
            
            # 倒计时
            for i in range(3, 0, -1):
                print(f"⚠ {i}秒后开始运动...")
                time.sleep(1)
            
            # 执行运动
            ret = self.robot.MoveJ(
                joint_pos=safe_position,
                tool=0,
                user=0,
                vel=15  # 较慢速度
            )
            
            if ret == 0:
                print("✓ MoveJ指令发送成功")
                print("等待运动完成...")
                time.sleep(8)
                print("✓ MoveJ测试完成")
                return True
            else:
                print(f"✗ MoveJ失败，错误码: {ret}")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠ 用户中断MoveJ测试")
            return False
        except Exception as e:
            print(f"✗ MoveJ测试异常: {e}")
            return False
    
    def test_status_queries(self):
        """测试状态查询"""
        if not self.robot:
            return False
            
        print("\n=== 状态查询测试 ===")
        
        # 运动完成状态
        try:
            result = self.robot.GetRobotMotionDone()
            print(f"✓ 运动完成状态: {result}")
        except Exception as e:
            print(f"⚠ GetRobotMotionDone() 异常: {e}")
        
        # 程序状态
        try:
            result = self.robot.GetProgramState()
            print(f"✓ 程序状态: {result}")
        except Exception as e:
            print(f"⚠ GetProgramState() 异常: {e}")
        
        return True
    
    def disconnect_robot(self):
        """断开连接"""
        try:
            if self.robot:
                # 安全停止
                try:
                    self.robot.ImmStopJOG()
                except:
                    pass
                time.sleep(1)
                self.robot.CloseRPC()
                print("✓ 机械臂连接已断开")
        except Exception as e:
            print(f"✗ 断开连接异常: {e}")
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("=" * 60)
        print("FR3机械臂综合测试程序")
        print("包含连接、安全点动、标准运动测试")
        print("=" * 60)
        
        # 1. 连接测试
        if not self.connect_robot():
            return False
        
        # 2. 基本功能测试
        self.test_basic_functions()
        
        # 3. 准备机械臂
        if not self.prepare_robot():
            self.disconnect_robot()
            return False
        
        # 4. 状态查询测试
        self.test_status_queries()
        
        # 5. 运动测试选择
        print("\n" + "="*50)
        print("运动测试选项:")
        print("1. 安全点动测试 (推荐首次使用)")
        print("2. 标准MoveJ测试")
        print("3. 两个都测试")
        print("4. 跳过运动测试")
        print("="*50)
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            self.test_jog_movement()
        elif choice == "2":
            self.test_movej_movement()
        elif choice == "3":
            self.test_jog_movement()
            if input("\n继续MoveJ测试？(y/N): ").strip().lower() == 'y':
                self.test_movej_movement()
        else:
            print("⚠ 跳过运动测试")
        
        # 6. 断开连接
        self.disconnect_robot()
        
        print("\n" + "=" * 60)
        print("✓ FR3机械臂综合测试完成！")
        print("💡 测试建议:")
        print("  - 首次使用：选择安全点动测试")
        print("  - 熟悉后：使用标准MoveJ测试")
        print("  - 开发时：根据需要选择测试类型")
        print("=" * 60)
        
        return True

def main():
    """主函数"""
    robot_ip = '192.168.58.2'
    
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    
    print(f"使用机械臂IP: {robot_ip}")
    
    test = FR3ComprehensiveTest(robot_ip)
    
    try:
        success = test.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠ 用户中断测试")
        test.disconnect_robot()
        return 1
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        test.disconnect_robot()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
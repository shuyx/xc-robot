#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂连接测试脚本
专门用于测试FR3机械臂连接状态并实时显示TCP位姿和关节角度

功能：
1. 测试机械臂连接
2. 显示当前TCP位姿(位置+姿态)
3. 显示当前关节角度
4. 实时监控模式
"""
import sys
import os
import time
from datetime import datetime
import math

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

sys.path.insert(0, project_root)

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
except ImportError as e:
    print(f"❌ fairino库导入失败: {e}")
    print("💡 请确认:")
    print("   1. fairino库已正确安装")
    print("   2. Python路径配置正确")
    print("   3. 机械臂SDK环境已配置")
    sys.exit(1)

class ArmConnectionTester:
    """机械臂连接测试器"""
    
    def __init__(self, arm_ip="192.168.58.2"):
        self.arm_ip = arm_ip
        self.robot = None
        self.is_connected = False
        self.is_enabled = False
        
        print(f"🤖 机械臂连接测试器")
        print(f"🔗 目标机械臂IP: {self.arm_ip}")
        print("=" * 60)
    
    def connect(self):
        """连接机械臂"""
        try:
            print(f"🔗 正在连接机械臂 {self.arm_ip}...")
            self.robot = Robot.RPC(self.arm_ip)
            
            # 检查连接状态
            if not hasattr(self.robot, 'is_conect') or not self.robot.is_conect:
                print("❌ 机械臂连接失败")
                print("💡 请检查:")
                print("   1. 机械臂电源是否开启")
                print("   2. 网络连接是否正常")
                print("   3. IP地址是否正确")
                print("   4. 防火墙设置")
                return False
            
            print("✅ 机械臂连接成功!")
            self.is_connected = True
            
            # 获取机械臂基本信息
            self.show_robot_info()
            
            return True
            
        except Exception as e:
            print(f"❌ 机械臂连接异常: {e}")
            print("💡 可能的原因:")
            print("   1. 机械臂未启动或网络不通")
            print("   2. IP地址错误")
            print("   3. RPC服务未运行")
            return False
    
    def show_robot_info(self):
        """显示机械臂基本信息"""
        if not self.is_connected:
            return
        
        try:
            print("\n📋 机械臂基本信息:")
            print("-" * 40)
            
            # 获取机械臂状态
            try:
                if hasattr(self.robot, 'GetRobotInstallAngle'):
                    error, install_angle = self.robot.GetRobotInstallAngle()
                    if error == 0:
                        print(f"   安装角度: {install_angle}°")
            except:
                pass
            
            # 获取使能状态
            try:
                if hasattr(self.robot, 'IsRobotEnable'):
                    error, enabled = self.robot.IsRobotEnable()
                    if error == 0:
                        enable_status = "已使能" if enabled == 1 else "未使能"
                        print(f"   使能状态: {enable_status}")
                        self.is_enabled = (enabled == 1)
            except:
                pass
            
            # 获取工作模式
            try:
                if hasattr(self.robot, 'Mode'):
                    # 这里只是尝试获取，不设置
                    print(f"   连接状态: 正常")
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ 获取机械臂信息异常: {e}")
    
    def get_current_tcp_pose(self):
        """获取当前TCP位姿"""
        if not self.is_connected:
            return None, "机械臂未连接"
        
        try:
            error, current_tcp = self.robot.GetActualToolFlangePose()
            if error == 0:
                return current_tcp, None
            else:
                return None, f"获取TCP位姿失败，错误码: {error}"
        except Exception as e:
            return None, f"获取TCP位姿异常: {e}"
    
    def get_current_joint_angles(self):
        """获取当前关节角度"""
        if not self.is_connected:
            return None, "机械臂未连接"
        
        try:
            error, current_joints = self.robot.GetActualJointPosDegree()
            if error == 0:
                return current_joints, None
            else:
                return None, f"获取关节角度失败，错误码: {error}"
        except Exception as e:
            return None, f"获取关节角度异常: {e}"
    
    def get_motion_status(self):
        """获取运动状态"""
        if not self.is_connected:
            return None, "机械臂未连接"
        
        try:
            # 尝试不同的方法获取运动状态
            if hasattr(self.robot, 'GetRobotMotionDone'):
                error, done = self.robot.GetRobotMotionDone()
                if error == 0:
                    return "静止" if done == 1 else "运动中", None
            elif hasattr(self.robot, 'robot_state_pkg'):
                done = self.robot.robot_state_pkg.motion_done
                return "静止" if done == 1 else "运动中", None
            else:
                return "未知", None
        except Exception as e:
            return None, f"获取运动状态异常: {e}"
    
    def show_current_status(self):
        """显示当前状态"""
        if not self.is_connected:
            print("❌ 机械臂未连接")
            return
        
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - 机械臂当前状态")
        print("=" * 60)
        
        # 获取TCP位姿
        tcp_pose, tcp_error = self.get_current_tcp_pose()
        if tcp_pose:
            print("📍 当前TCP位置:")
            print(f"   X={tcp_pose[0]:.1f}, Y={tcp_pose[1]:.1f}, Z={tcp_pose[2]:.1f}")
            print("📍 当前TCP姿态:")
            print(f"   RX={tcp_pose[3]:.1f}, RY={tcp_pose[4]:.1f}, RZ={tcp_pose[5]:.1f}")
            print("📍 TCP位姿列表格式:")
            tcp_list = [round(tcp_pose[i], 1) for i in range(6)]
            print(f"   {tcp_list}")
        else:
            print(f"📍 TCP位姿: ❌ {tcp_error}")
        
        # 获取关节角度
        joint_angles, joint_error = self.get_current_joint_angles()
        if joint_angles:
            print("🔧 当前关节角度:")
            print(f"   J1={joint_angles[0]:.2f}°, J2={joint_angles[1]:.2f}°, J3={joint_angles[2]:.2f}°")
            print(f"   J4={joint_angles[3]:.2f}°, J5={joint_angles[4]:.2f}°, J6={joint_angles[5]:.2f}°")
            print("🔧 关节角度列表格式:")
            joint_list = [round(joint_angles[i], 2) for i in range(6)]
            print(f"   {joint_list}")
        else:
            print(f"🔧 关节角度: ❌ {joint_error}")
        
        # 获取运动状态
        motion_status, motion_error = self.get_motion_status()
        if motion_status:
            print(f"🏃 运动状态: {motion_status}")
        else:
            print(f"🏃 运动状态: ❌ {motion_error}")
        
        # 显示使能状态
        enable_status = "已使能" if self.is_enabled else "未使能"
        print(f"⚡ 使能状态: {enable_status}")
        
        print("-" * 60)
    
    def enable_robot(self):
        """使能机械臂"""
        if not self.is_connected:
            print("❌ 机械臂未连接，无法使能")
            return False
        
        try:
            print("⚡ 准备使能机械臂...")
            
            # 设置自动模式
            ret = self.robot.Mode(0)
            if ret != 0:
                print(f"❌ 设置自动模式失败，错误码: {ret}")
                return False
            print("✅ 已切换到自动模式")
            
            time.sleep(0.5)
            
            # 上使能
            ret = self.robot.RobotEnable(1)
            if ret != 0:
                print(f"❌ 使能失败，错误码: {ret}")
                return False
            print("✅ 机械臂已使能")
            
            time.sleep(1.0)
            self.is_enabled = True
            return True
            
        except Exception as e:
            print(f"❌ 机械臂使能异常: {e}")
            return False
    
    def disable_robot(self):
        """下使能机械臂"""
        if not self.is_connected:
            return
        
        try:
            if self.is_enabled:
                ret = self.robot.RobotEnable(0)
                if ret == 0:
                    print("⬇️ 机械臂已下使能")
                    self.is_enabled = False
                else:
                    print(f"⚠️ 下使能失败，错误码: {ret}")
        except Exception as e:
            print(f"⚠️ 下使能异常: {e}")
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.robot and self.is_connected:
                # 先下使能
                self.disable_robot()
                
                time.sleep(0.5)
                
                # 关闭RPC连接
                self.robot.CloseRPC()
                print("🔌 机械臂连接已关闭")
                
            self.is_connected = False
            
        except Exception as e:
            print(f"⚠️ 断开连接异常: {e}")
    
    def show_help(self):
        """显示帮助"""
        print("\n" + "=" * 60)
        print("                机械臂连接测试工具")
        print("=" * 60)
        print("  【基本操作】")
        print("  S - 显示当前状态（TCP位姿+关节角度）")
        print("  C - 连续监控模式（每2秒刷新）")
        print("  R - 重新连接机械臂")
        print("")
        print("  【控制操作】")
        print("  E - 使能机械臂")
        print("  D - 下使能机械臂")
        print("")
        print("  【系统操作】")
        print("  H - 显示帮助")
        print("  Q - 退出程序")
        print("=" * 60)
        print("💡 提示:")
        print("   • 连接成功后可以看到实时的TCP位姿和关节角度")
        print("   • 使能后可以通过其他程序控制机械臂运动")
        print("   • 连续监控模式按Ctrl+C退出到命令模式")
        print("=" * 60)
    
    def continuous_monitor(self):
        """连续监控模式"""
        print("\n🔄 进入连续监控模式 (按 Ctrl+C 退出)")
        print("⏱️  每2秒刷新一次")
        print("-" * 60)
        
        try:
            while True:
                # 清屏（在支持的终端中）
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("🔄 连续监控模式 - 按 Ctrl+C 退出")
                self.show_current_status()
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️  退出连续监控模式")
    
    def run_interactive(self):
        """运行交互模式"""
        print("\n🚀 机械臂连接测试工具启动")
        
        # 尝试连接
        if not self.connect():
            print("\n❌ 连接失败，程序退出")
            return
        
        # 显示帮助
        self.show_help()
        
        # 显示初始状态
        self.show_current_status()
        
        print(f"\n请输入命令 (输入 H 查看帮助):")
        
        try:
            while True:
                try:
                    command = input(">>> ").strip().lower()
                    
                    if not command:
                        continue
                    
                    if command in ['q', 'quit', 'exit']:
                        print("👋 正在退出...")
                        break
                    
                    elif command == 's':
                        # 显示状态
                        self.show_current_status()
                    
                    elif command == 'c':
                        # 连续监控
                        self.continuous_monitor()
                    
                    elif command == 'r':
                        # 重新连接
                        print("🔄 重新连接机械臂...")
                        self.disconnect()
                        time.sleep(1)
                        self.connect()
                    
                    elif command == 'e':
                        # 使能
                        self.enable_robot()
                    
                    elif command == 'd':
                        # 下使能
                        self.disable_robot()
                    
                    elif command in ['h', 'help']:
                        # 显示帮助
                        self.show_help()
                    
                    else:
                        print(f"❓ 未知命令: {command}")
                        print("💡 输入 H 查看帮助")
                
                except KeyboardInterrupt:
                    print("\n⚠️  检测到中断信号")
                    break
                except Exception as e:
                    print(f"❌ 命令执行错误: {e}")
        
        finally:
            self.disconnect()
            print("👋 程序已退出")
    
    def run_once(self):
        """运行一次性测试"""
        print("\n🚀 机械臂连接测试")
        
        # 连接测试
        if not self.connect():
            return False
        
        # 显示状态
        self.show_current_status()
        
        # 断开连接
        self.disconnect()
        return True

def main():
    """主函数"""
    import sys
    
    # 解析命令行参数
    arm_ip = "192.168.58.2"  # 默认机械臂IP
    interactive = True  # 默认交互模式
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("机械臂连接测试工具")
            print("用法:")
            print("  python3 test_arm_connection.py [IP地址] [模式]")
            print("参数:")
            print("  IP地址: 机械臂IP地址 (默认: 192.168.58.2)")
            print("  模式:")
            print("    -i, --interactive: 交互模式 (默认)")
            print("    -o, --once: 一次性测试模式")
            print("示例:")
            print("  python3 test_arm_connection.py")
            print("  python3 test_arm_connection.py 192.168.58.2")
            print("  python3 test_arm_connection.py 192.168.58.2 --once")
            return
        
        arm_ip = sys.argv[1]
        
        if len(sys.argv) > 2 and sys.argv[2] in ['-o', '--once']:
            interactive = False
    
    # 创建测试器
    tester = ArmConnectionTester(arm_ip)
    
    try:
        if interactive:
            tester.run_interactive()
        else:
            success = tester.run_once()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️  程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
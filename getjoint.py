#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simple3.py - 最终可工作版本
基于您的环境，使用可靠的robot_state_pkg方法
完全避开ctypes问题
"""

import os
import sys
import time

# 1. 设置路径
print("⚙️ 正在设置系统路径...")
fairino_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr3_control")
sys.path.append(fairino_path)
print(f"✅ 系统路径已添加: {fairino_path}")

# 2. 导入Robot
try:
    from fairino import Robot
    print("✅ 成功导入 'from fairino import Robot'")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def test_api_call(robot):
    """测试API调用方式（可能失败）"""
    print("\n🔍 测试API调用方式:")
    try:
        ret = robot.GetActualJointPosDegree()
        print(f"API返回值类型: {type(ret)}")
        print(f"API返回值内容: {ret}")
        
        if isinstance(ret, tuple) and len(ret) == 2:
            error_code, joint_data = ret
            print(f"错误码: {error_code}")
            print(f"关节数据: {joint_data}")
            
            if error_code == 0:
                print(f"✅ API调用成功: {[f'{j:.2f}°' for j in joint_data]}")
                return True, joint_data
            else:
                print(f"❌ API返回错误码: {error_code}")
                return False, None
        else:
            print("❌ API返回格式不正确")
            return False, None
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return False, None

def test_robot_state_pkg(robot):
    """测试robot_state_pkg方式（推荐）"""
    print("\n🔍 测试robot_state_pkg方式:")
    try:
        if hasattr(robot, 'robot_state_pkg'):
            print("✅ robot_state_pkg属性存在")
            
            # 方法1：逐个获取
            print("📋 方法1 - 逐个获取关节位置:")
            joint_positions = []
            for i in range(6):
                pos = robot.robot_state_pkg.jt_cur_pos[i]
                joint_positions.append(pos)
                print(f"  关节{i+1}: {pos:8.3f}°")
            
            print(f"✅ 完整关节位置: {[f'{j:.2f}°' for j in joint_positions]}")
            
            # 方法2：一次性获取所有数据
            print("\n📋 方法2 - 获取所有机器人数据:")
            print(f"程序状态: {robot.robot_state_pkg.program_state}")
            print(f"机器人状态: {robot.robot_state_pkg.robot_state}")
            print(f"机器人模式: {robot.robot_state_pkg.robot_mode}")
            print(f"主故障码: {robot.robot_state_pkg.main_code}")
            print(f"子故障码: {robot.robot_state_pkg.sub_code}")
            
            # 工具位姿
            tool_pose = [robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
            print(f"工具位姿: X={tool_pose[0]:.1f}, Y={tool_pose[1]:.1f}, Z={tool_pose[2]:.1f}")
            print(f"        RX={tool_pose[3]:.1f}, RY={tool_pose[4]:.1f}, RZ={tool_pose[5]:.1f}")
            
            return True, joint_positions
            
        else:
            print("❌ robot_state_pkg属性不存在")
            return False, None
            
    except Exception as e:
        print(f"❌ robot_state_pkg访问失败: {e}")
        return False, None

def create_joint_reader(robot):
    """创建关节数据读取器"""
    print("\n🛠️ 创建关节数据读取器:")
    
    def get_joint_positions():
        """获取关节位置的可靠方法"""
        try:
            return [robot.robot_state_pkg.jt_cur_pos[i] for i in range(6)]
        except:
            return None
    
    def get_tool_pose():
        """获取工具位姿"""
        try:
            return [robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
        except:
            return None
    
    def get_robot_status():
        """获取机器人状态"""
        try:
            return {
                'program_state': robot.robot_state_pkg.program_state,
                'robot_state': robot.robot_state_pkg.robot_state,
                'robot_mode': robot.robot_state_pkg.robot_mode,
                'main_code': robot.robot_state_pkg.main_code,
                'sub_code': robot.robot_state_pkg.sub_code,
                'motion_done': robot.robot_state_pkg.motion_done
            }
        except:
            return None
    
    # 测试读取器
    joints = get_joint_positions()
    if joints:
        print(f"✅ 读取器创建成功，当前关节位置: {[f'{j:.2f}°' for j in joints]}")
        
        tool = get_tool_pose()
        if tool:
            print(f"✅ 工具位姿: {[f'{p:.1f}' for p in tool]}")
        
        status = get_robot_status()
        if status:
            print(f"✅ 机器人状态: {status}")
        
        return get_joint_positions, get_tool_pose, get_robot_status
    else:
        print("❌ 读取器创建失败")
        return None, None, None

def continuous_monitoring(robot, duration=10):
    """持续监控演示"""
    print(f"\n🔄 开始持续监控 ({duration}秒):")
    
    try:
        for i in range(duration):
            print(f"\n--- 周期 {i+1} ---")
            
            # 获取关节位置
            try:
                joints = [robot.robot_state_pkg.jt_cur_pos[j] for j in range(6)]
                print(f"关节位置: {[f'{j:6.1f}°' for j in joints]}")
                
                # 获取工具位姿
                tool = [robot.robot_state_pkg.tl_cur_pos[j] for j in range(6)]
                print(f"工具位姿: X={tool[0]:6.1f}, Y={tool[1]:6.1f}, Z={tool[2]:6.1f}")
                
                # 获取状态
                status = robot.robot_state_pkg.robot_state
                print(f"机器人状态: {status} ", end="")
                if status == 1:
                    print("(停止)")
                elif status == 2:
                    print("(运行)")
                elif status == 3:
                    print("(暂停)")
                elif status == 4:
                    print("(拖动)")
                else:
                    print("(未知)")
                    
            except Exception as e:
                print(f"❌ 监控周期 {i+1} 失败: {e}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断监控")

def main():
    """主函数"""
    print("🚀 FR3机械臂最终测试方案")
    print("专注于可靠的robot_state_pkg方法")
    print("=" * 50)
    
    robot = None
    try:
        # 1. 连接机器人
        print("🔗 连接机器人...")
        robot = Robot.RPC('192.168.58.2')
        print("✅ 机器人连接成功")
        
        # 2. 设置模式和使能
        print("⚙️ 设置自动模式...")
        robot.Mode(0)
        time.sleep(1)
        
        print("⚙️ 使能机器人...")
        enable_ret = robot.RobotEnable(1)
        if enable_ret != 0:
            print(f"⚠️ 使能返回码: {enable_ret}")
        else:
            print("✅ 机器人使能成功")
        
        time.sleep(2)  # 等待稳定
        
        # 3. 测试API调用（可能失败）
        api_success, api_data = test_api_call(robot)
        
        # 4. 测试robot_state_pkg（推荐方法）
        pkg_success, pkg_data = test_robot_state_pkg(robot)
        
        # 5. 创建数据读取器
        if pkg_success:
            get_joints, get_tool, get_status = create_joint_reader(robot)
            
            if get_joints:
                # 6. 询问是否进行持续监控
                print("\n" + "=" * 50)
                choice = input("是否进行持续监控演示？(y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    duration = input("监控时长(秒，默认10): ").strip()
                    try:
                        duration = int(duration) if duration else 10
                    except:
                        duration = 10
                    continuous_monitoring(robot, duration)
        
        # 7. 总结
        print("\n" + "=" * 50)
        print("📋 测试结果总结:")
        print(f"API调用方式: {'✅ 成功' if api_success else '❌ 失败 (ctypes问题)'}")
        print(f"robot_state_pkg方式: {'✅ 成功' if pkg_success else '❌ 失败'}")
        
        if pkg_success:
            print("\n🎉 推荐使用robot_state_pkg方式！")
            print("💡 这种方式稳定可靠，完全避开了ctypes问题")
        else:
            print("\n❌ 需要检查机器人连接和状态")
        
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if robot:
            try:
                robot.CloseRPC()
                print("\n✅ 机器人连接已断开")
            except:
                pass

if __name__ == "__main__":
    main()
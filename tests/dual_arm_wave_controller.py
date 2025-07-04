#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simpletest.py - 极简版机械臂测试程序
只获取：1. 关节角度  2. 工具位姿
"""

import os
import sys
import time
from datetime import datetime

# 导入设置
fairino_path = "./fr3_control/"
sys.path.append(fairino_path)

try:
    from fairino import Robot
    print("✅ 成功导入 fairino.Robot")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def safe_parse_data(result, data_name="数据"):
    """安全解析API返回的数据"""
    try:
        if result is None:
            return None
        
        if isinstance(result, tuple) and len(result) >= 2:
            error_code = result[0]
            data = result[1]
            
            if error_code != 0:
                print(f"❌ API错误码: {error_code}")
                return None
            
            # 尝试多种解析方式
            try:
                # 方式1: 直接索引
                return [float(data[i]) for i in range(6)]
            except:
                try:
                    # 方式2: 列表转换
                    return [float(x) for x in list(data)[:6]]
                except:
                    try:
                        # 方式3: 逐个获取
                        result_list = []
                        for i in range(6):
                            result_list.append(float(data[i]))
                        return result_list
                    except:
                        return None
        return None
    except Exception as e:
        print(f"❌ 解析{data_name}失败: {e}")
        return None

def test_robot_state_pkg(robot):
    """测试robot_state_pkg方式获取数据"""
    print("\n🎯 方式1: robot_state_pkg")
    
    try:
        time.sleep(0.5)  # 等待初始化
        
        if hasattr(robot, 'robot_state_pkg'):
            # 获取关节角度
            joint_angles = [robot.robot_state_pkg.jt_cur_pos[i] for i in range(6)]
            print(f"关节角度: {[f'{j:.2f}°' for j in joint_angles]}")
            
            # 获取工具位姿
            tool_pose = [robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
            print(f"工具位姿: X={tool_pose[0]:.2f}, Y={tool_pose[1]:.2f}, Z={tool_pose[2]:.2f} mm")
            print(f"          RX={tool_pose[3]:.2f}, RY={tool_pose[4]:.2f}, RZ={tool_pose[5]:.2f} °")
            
            return True
        else:
            print("❌ robot_state_pkg 不可用")
            return False
            
    except Exception as e:
        print(f"❌ robot_state_pkg 失败: {e}")
        return False

def test_api_calls(robot):
    """测试API调用方式获取数据"""
    print("\n🎯 方式2: API调用")
    
    success_count = 0
    
    # 测试关节角度
    try:
        result = robot.GetActualJointPosDegree()
        joint_data = safe_parse_data(result, "关节角度")
        if joint_data:
            print(f"关节角度: {[f'{j:.2f}°' for j in joint_data]}")
            success_count += 1
        else:
            print("❌ 关节角度获取失败")
    except Exception as e:
        print(f"❌ 关节角度API异常: {e}")
    
    # 测试工具位姿
    try:
        result = robot.GetActualTCPPose()
        pose_data = safe_parse_data(result, "工具位姿")
        if pose_data:
            print(f"工具位姿: X={pose_data[0]:.2f}, Y={pose_data[1]:.2f}, Z={pose_data[2]:.2f} mm")
            print(f"          RX={pose_data[3]:.2f}, RY={pose_data[4]:.2f}, RZ={pose_data[5]:.2f} °")
            success_count += 1
        else:
            print("❌ 工具位姿获取失败")
    except Exception as e:
        print(f"❌ 工具位姿API异常: {e}")
    
    return success_count >= 1

def continuous_monitor(robot, duration=10):
    """连续监控"""
    print(f"\n🔄 连续监控 ({duration}秒)")
    
    count = 0
    success_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            count += 1
            print(f"\n--- 周期 #{count} ---")
            
            # 优先使用robot_state_pkg
            try:
                if hasattr(robot, 'robot_state_pkg'):
                    joint_angles = [robot.robot_state_pkg.jt_cur_pos[i] for i in range(6)]
                    tool_pose = [robot.robot_state_pkg.tl_cur_pos[i] for i in range(6)]
                    
                    print(f"关节: {[f'{j:.1f}°' for j in joint_angles]}")
                    print(f"位姿: X={tool_pose[0]:.1f}, Y={tool_pose[1]:.1f}, Z={tool_pose[2]:.1f}")
                    success_count += 1
                else:
                    # 备用API调用
                    joint_result = robot.GetActualJointPosDegree()
                    pose_result = robot.GetActualTCPPose()
                    
                    joint_data = safe_parse_data(joint_result)
                    pose_data = safe_parse_data(pose_result)
                    
                    if joint_data and pose_data:
                        print(f"关节: {[f'{j:.1f}°' for j in joint_data]}")
                        print(f"位姿: X={pose_data[0]:.1f}, Y={pose_data[1]:.1f}, Z={pose_data[2]:.1f}")
                        success_count += 1
                    else:
                        print("❌ 数据获取失败")
            except Exception as e:
                print(f"❌ 监控失败: {e}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    
    print(f"\n📊 成功率: {success_count}/{count} ({success_count/count*100:.1f}%)")

def main():
    """主函数"""
    print("🚀 极简版机械臂测试")
    print("功能: 关节角度 + 工具位姿")
    print("=" * 40)
    
    # 连接机械臂
    try:
        robot = Robot.RPC('192.168.58.2')
        print("✅ 连接成功")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    try:
        # 测试两种数据获取方式
        state_pkg_ok = test_robot_state_pkg(robot)
        api_ok = test_api_calls(robot)
        
        # 总结
        print("\n📋 测试结果:")
        print(f"robot_state_pkg: {'✅' if state_pkg_ok else '❌'}")
        print(f"API调用: {'✅' if api_ok else '❌'}")
        
        # 连续监控选项
        if state_pkg_ok or api_ok:
            choice = input("\n是否连续监控？(y/n): ")
            if choice.lower() == 'y':
                continuous_monitor(robot, 15)
        else:
            print("\n💥 所有方式都失败")
    
    finally:
        try:
            robot.CloseRPC()
            print("\n✅ 连接已断开")
        except:
            pass

if __name__ == "__main__":
    main()
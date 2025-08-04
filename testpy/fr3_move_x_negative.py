#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time

# 添加FR3控制库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')

if os.path.exists(fr3_control_path):
    sys.path.insert(0, fr3_control_path)
    print(f"✓ 已添加fr3_control路径: {fr3_control_path}")
else:
    print(f"✗ 未找到fr3_control文件夹: {fr3_control_path}")
    sys.exit(1)

try:
    from fairino import Robot
    print("✅ fairino库导入成功")
except ImportError as e:
    print(f"❌ fairino库导入失败: {e}")
    sys.exit(1)

def move_x_negative_11cm():
    """让机械臂末端沿x轴负方向移动11cm"""
    robot = None
    
    try:
        # 1. 连接机械臂
        print("🔗 正在连接机械臂...")
        robot = Robot.RPC('192.168.58.2')
        
        if not hasattr(robot, 'is_conect') or not robot.is_conect:
            print("❌ 连接失败")
            return False
        print("✅ 机械臂连接成功")
        
        # 2. 设置自动模式并使能
        print("⚡ 准备机械臂...")
        ret = robot.Mode(0)
        if ret != 0:
            print(f"❌ 设置自动模式失败，错误码: {ret}")
            return False
        
        time.sleep(0.5)
        
        ret = robot.RobotEnable(1)
        if ret != 0:
            print(f"❌ 使能失败，错误码: {ret}")
            return False
        print("✅ 机械臂已使能")
        
        time.sleep(1.5)
        
        # 3. 获取当前TCP位置
        print("📍 获取当前TCP位置...")
        error, current_tcp = robot.GetActualToolFlangePose()
        if error != 0:
            print(f"❌ 获取TCP位置失败，错误码: {error}")
            return False
        
        print(f"当前TCP位置: X={current_tcp[0]:.1f}, Y={current_tcp[1]:.1f}, Z={current_tcp[2]:.1f}")
        print(f"当前TCP姿态: RX={current_tcp[3]:.1f}, RY={current_tcp[4]:.1f}, RZ={current_tcp[5]:.1f}")
        
        # 4. 计算目标位置（z轴负方向移动110mm）
        target_tcp = current_tcp.copy()
        target_tcp[2] = current_tcp[2] - 110.0  # z轴负方向移动11cm (110mm)
        
        print(f"目标TCP位置: X={target_tcp[0]:.1f}, Y={target_tcp[1]:.1f}, Z={target_tcp[2]:.1f}")
        print(f"Z轴移动距离: {abs(target_tcp[2] - current_tcp[2]):.1f}mm")
        
        # 5. 使用ServoCart进行直线运动
        print("🚀 开始执行直线运动...")
        
        # 启动伺服模式
        ret = robot.ServoMoveStart()
        if ret != 0:
            print(f"❌ 伺服运动开始失败，错误码: {ret}")
            return False
        print("✅ 伺服模式已启动")
        
        # 生成轨迹点（插值）
        steps = 100
        servo_speed = 10.0
        cycle_time = 0.008
        
        print(f"生成{steps}个轨迹点...")
        for i in range(steps + 1):
            t = i / steps
            # 使用S曲线插值使运动更平滑
            t_smooth = 3 * t * t - 2 * t * t * t
            
            interpolated_pos = []
            for j in range(6):
                interpolated_value = current_tcp[j] + t_smooth * (target_tcp[j] - current_tcp[j])
                interpolated_pos.append(interpolated_value)
            
            # 发送伺服指令
            ret = robot.ServoCart(mode=0, desc_pos=interpolated_pos, vel=servo_speed)
            if ret != 0 and i % 20 == 0:
                print(f"⚠️ 轨迹点 {i} 执行失败，错误码: {ret}")
            
            if i % 25 == 0:
                progress = (i / steps) * 100
                print(f"进度: {progress:.1f}%")
            
            time.sleep(cycle_time)
        
        print("✅ 轨迹跟随完成")
        
        # 结束伺服模式
        ret = robot.ServoMoveEnd()
        if ret != 0:
            print(f"⚠️ 伺服运动结束警告，错误码: {ret}")
        else:
            print("✅ 伺服模式已结束")
        
        # 6. 验证最终位置
        time.sleep(0.5)
        error, final_tcp = robot.GetActualToolFlangePose()
        if error == 0:
            print(f"最终TCP位置: X={final_tcp[0]:.1f}, Y={final_tcp[1]:.1f}, Z={final_tcp[2]:.1f}")
            
            z_error = abs(final_tcp[2] - target_tcp[2])
            print(f"Z轴位置误差: {z_error:.1f}mm")
            
            if z_error < 5.0:
                print("✅ 运动完成，精度良好！")
                return True
            else:
                print("⚠️ 运动完成，但精度有待改善")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ 运动异常: {e}")
        return False
    
    finally:
        # 清理资源
        if robot:
            try:
                robot.ServoMoveEnd()
                robot.RobotEnable(0)
                robot.CloseRPC()
                print("🔌 连接已关闭")
            except:
                pass

def main():
    print("🤖 FR3机械臂Z轴负方向移动程序")
    print("📏 移动距离: 11cm (110mm)")
    print("🎯 运动方式: ServoCart直线运动")
    
    confirm = input("\n确认开始运动？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 运动已取消")
        return 1
    
    success = move_x_negative_11cm()
    
    if success:
        print("\n🎉 Z轴负方向移动完成！")
        return 0
    else:
        print("\n❌ Z轴移动失败")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 用户中断程序")
        sys.exit(1)
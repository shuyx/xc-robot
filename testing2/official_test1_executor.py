#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全基于FR3官方示例的test1.lua执行器
严格按照官方WebAPP程序使用接口实现
"""

import os
import sys
import time

# 添加FR3控制模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

try:
    from fairino import Robot
except ImportError as e:
    print(f"❌ 导入fairino模块失败: {e}")
    print(f"请检查fr3_control目录路径: {fr3_control_path}")
    print("确保以下文件存在:")
    print(f"  - {os.path.join(fr3_control_path, 'fairino', 'Robot.py')}")
    sys.exit(1)

def print_program_state(robot):
    """查询和打印程序状态 - 官方示例函数"""
    pstate = robot.GetProgramState()    # 查询程序运行状态,1-程序停止或无程序运行，2-程序运行中，3-程序暂停
    linenum = robot.GetCurrentLine()    # 查询当前作业程序执行的行号
    name = robot.GetLoadedProgram()     # 查询已加载的作业程序名
    
    print("the robot program state is:", pstate[1])
    print("the robot program line number is:", linenum[1])  
    print("the robot program name is:", name[1])
    time.sleep(1)

def execute_test1_lua_official():
    """执行test1.lua - 完全按照官方示例"""
    
    print("=" * 60)
    print("FR3机械臂 test1.lua 官方示例执行器")
    print("基于FR3官方WebAPP程序使用接口")
    print("=" * 60)
    
    try:
        # 与机器人控制器建立连接，连接成功返回一个机器人对象
        print("正在连接机器人控制器 192.168.58.2 ...")
        robot = Robot.RPC('192.168.58.2')
        
        if robot is None:
            print("❌ 连接失败！请检查机器人IP和网络连接")
            return False
        
        print("✅ 连接成功！")
        
        # 机器人webapp程序使用接口
        print("\n设置机器人为自动运行模式...")
        robot.Mode(0)  # 机器人切入自动运行模式
        
        print("\n初始状态检查:")
        print_program_state(robot)
        
        # 加载要执行的机器人程序
        print("\n正在加载 /fruser/test1.lua 程序...")
        ret = robot.ProgramLoad('/fruser/test1.lua')  # 加载要执行的机器人程序
        print("加载要执行的机器人程序错误码:", ret)
        
        if ret != 0:
            print(f"❌ 程序加载失败，错误码: {ret}")
            print("请检查:")
            print("1. /fruser/test1.lua 文件是否存在")
            print("2. 程序语法是否正确")
            return False
        
        print("✅ 程序加载成功！")
        
        # 执行机器人程序
        print("\n开始执行机器人程序...")
        ret = robot.ProgramRun()  # 执行机器人程序
        print("执行机器人程序错误码:", ret)
        
        if ret != 0:
            print(f"❌ 程序执行失败，错误码: {ret}")
            return False
        
        print("✅ 程序开始执行！")
        
        # 监控程序执行
        print("\n开始监控程序执行状态...")
        print("(按 Ctrl+C 可以中断监控)")
        
        try:
            while True:
                time.sleep(2)
                print("\n" + "="*30)
                print_program_state(robot)
                
                # 检查程序是否执行完成
                pstate = robot.GetProgramState()
                if pstate[1] == 1:  # 程序停止或无程序运行
                    print("🎉 程序执行完成！")
                    break
                elif pstate[1] == 2:  # 程序运行中
                    print("⏳ 程序正在运行中...")
                elif pstate[1] == 3:  # 程序暂停
                    print("⏸️  程序已暂停")
                    
        except KeyboardInterrupt:
            print("\n⚠️  用户中断监控")
            
            # 询问是否需要进行程序控制操作
            while True:
                choice = input("\n请选择操作:\n1. 暂停程序\n2. 恢复程序\n3. 停止程序\n4. 退出\n请输入选择 (1-4): ").strip()
                
                if choice == '1':
                    ret = robot.ProgramPause()  # 暂停正在执行的机器人程序
                    print("暂停正在执行的机器人程序错误码:", ret)
                    time.sleep(2)
                    print_program_state(robot)
                    
                elif choice == '2':
                    ret = robot.ProgramResume()  # 恢复暂停执行的机器人程序
                    print("恢复暂停执行的机器人程序错误码:", ret)
                    time.sleep(2)
                    print_program_state(robot)
                    
                elif choice == '3':
                    ret = robot.ProgramStop()  # 停止正在执行的机器人程序
                    print("停止正在执行的机器人程序错误码:", ret)
                    time.sleep(2)
                    print_program_state(robot)
                    break
                    
                elif choice == '4':
                    break
                    
                else:
                    print("无效选择，请重新输入")
        
        # 最终状态检查
        print("\n最终状态:")
        print_program_state(robot)
        
        # 询问是否设置为开机自动加载默认程序
        set_default = input("\n是否设置test1.lua为开机自动加载的默认程序? (y/n): ").strip().lower()
        if set_default in ['y', 'yes']:
            flag = 1  # 0-开机不自动加载默认程序，1-开机自动加载默认程序
            ret = robot.LoadDefaultProgConfig(flag, '/fruser/test1.lua')  # 设置开机自动加载默认程序
            print("设置开机自动加载默认程序错误码:", ret)
            if ret == 0:
                print("✅ 成功设置为开机自动加载程序")
            else:
                print(f"❌ 设置失败，错误码: {ret}")
        
        print("\n程序执行完成！")
        return True
        
    except Exception as e:
        print(f"\n💥 执行过程中发生异常: {e}")
        return False
    
    finally:
        # 注意：官方示例中没有显式关闭连接，但为了资源管理，我们添加这个
        try:
            if 'robot' in locals() and robot:
                robot.CloseRPC()
                print("✅ 已断开机器人连接")
        except:
            pass

def main():
    """主函数"""
    success = execute_test1_lua_official()
    
    if success:
        print("\n🎉 test1.lua 程序执行成功完成！")
    else:
        print("\n❌ test1.lua 程序执行失败！")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
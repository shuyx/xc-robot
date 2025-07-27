#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门用于执行test1.lua程序的简化脚本
"""

import sys
import os
import time

# 添加当前目录到Python路径，以便导入FR3执行器
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入FR3执行器
from fr3_lua_executor import FR3LuaExecutor

def execute_test1_lua():
    """执行test1.lua程序的主函数"""
    
    print("=" * 60)
    print("FR3机械臂 test1.lua 程序执行器")
    print("=" * 60)
    
    # 创建执行器
    executor = FR3LuaExecutor("192.168.58.2")
    
    try:
        # 连接机械臂
        print("正在连接到FR3机械臂...")
        if not executor.connect():
            print("❌ 连接失败！请检查:")
            print("   1. 机械臂是否开机")
            print("   2. 网络连接是否正常")
            print("   3. IP地址 192.168.58.2 是否正确")
            return False
        
        print("✅ 连接成功！")
        
        # 检查当前状态
        print("\n检查机械臂当前状态...")
        state_info = executor.get_program_state()
        
        if 'program_state' in state_info:
            current_state = state_info['program_state']['description']
            print(f"当前状态: {current_state}")
        
        if 'loaded_program' in state_info:
            loaded_program = state_info['loaded_program']['program_name']
            print(f"已加载程序: {loaded_program}")
        
        # 执行test1.lua程序
        print("\n" + "=" * 40)
        print("开始执行 /fruser/test1.lua 程序")
        print("=" * 40)
        
        result = executor.execute_lua_program("/fruser/test1.lua", monitor=True)
        
        if result['success']:
            print("\n🎉 test1.lua 程序执行成功完成！")
            
            # 显示执行摘要
            if 'steps' in result and 'monitor' in result['steps']:
                monitor_data = result['steps']['monitor']
                if 'execution_log' in monitor_data:
                    print(f"\n📊 执行摘要:")
                    print(f"   - 监控记录数: {len(monitor_data['execution_log'])}")
                    if monitor_data['execution_log']:
                        start_time = monitor_data['execution_log'][0]['timestamp']
                        end_time = monitor_data['execution_log'][-1]['timestamp']
                        print(f"   - 开始时间: {start_time}")
                        print(f"   - 结束时间: {end_time}")
            
            return True
        else:
            print(f"\n❌ test1.lua 程序执行失败!")
            if 'error' in result:
                print(f"错误信息: {result['error']}")
            return False
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断程序执行")
        print("正在停止机械臂程序...")
        executor.stop_lua_program()
        return False
    
    except Exception as e:
        print(f"\n💥 执行过程中发生异常: {e}")
        return False
    
    finally:
        print("\n断开机械臂连接...")
        executor.disconnect()
        print("程序结束")

if __name__ == "__main__":
    success = execute_test1_lua()
    sys.exit(0 if success else 1)
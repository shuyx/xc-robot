#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试fairino模块导入
"""

import os
import sys

def test_fairino_import():
    """测试fairino模块导入"""
    
    print("=" * 50)
    print("FR3 fairino模块导入测试")
    print("=" * 50)
    
    # 显示当前路径信息
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fr3_control_path = os.path.join(project_root, 'fr3_control')
    fairino_path = os.path.join(fr3_control_path, 'fairino')
    robot_py_path = os.path.join(fairino_path, 'Robot.py')
    
    print(f"当前目录: {current_dir}")
    print(f"项目根目录: {project_root}")
    print(f"FR3控制路径: {fr3_control_path}")
    print(f"fairino路径: {fairino_path}")
    print(f"Robot.py路径: {robot_py_path}")
    
    # 检查路径是否存在
    print("\n路径检查:")
    print(f"fr3_control目录存在: {os.path.exists(fr3_control_path)}")
    print(f"fairino目录存在: {os.path.exists(fairino_path)}")
    print(f"Robot.py文件存在: {os.path.exists(robot_py_path)}")
    
    # 检查__init__.py文件
    init_py_path = os.path.join(fairino_path, '__init__.py')
    print(f"__init__.py文件存在: {os.path.exists(init_py_path)}")
    
    if not os.path.exists(init_py_path):
        print("⚠️  创建__init__.py文件...")
        try:
            with open(init_py_path, 'w') as f:
                f.write('# fairino package\n')
            print("✅ __init__.py文件创建成功")
        except Exception as e:
            print(f"❌ 创建__init__.py失败: {e}")
    
    # 添加路径到sys.path
    print(f"\n添加路径到sys.path: {fr3_control_path}")
    sys.path.insert(0, fr3_control_path)
    
    print("当前Python路径:")
    for i, path in enumerate(sys.path[:5]):  # 只显示前5个路径
        print(f"  {i}: {path}")
    
    # 尝试导入
    print("\n尝试导入fairino模块...")
    try:
        from fairino import Robot
        print("✅ fairino.Robot导入成功!")
        
        # 尝试创建Robot实例（不连接）
        print("✅ fairino模块可用，Robot类已导入")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        
        # 尝试直接导入Robot.py
        print("\n尝试直接导入Robot.py...")
        try:
            sys.path.insert(0, fairino_path)
            import Robot as RobotModule
            print("✅ 直接导入Robot.py成功!")
            print("可以使用: import Robot; robot = Robot.RPC('192.168.58.2')")
            return True
        except Exception as e2:
            print(f"❌ 直接导入也失败: {e2}")
            return False
    
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_fairino_import()
    if success:
        print("\n🎉 模块导入测试成功!")
        print("现在可以使用official_test1_executor.py了")
    else:
        print("\n❌ 模块导入测试失败!")
        print("请检查fr3_control目录结构")
    
    input("\n按回车键退出...")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3库诊断工具
用于检查fairino库的安装和导入状态
"""

import sys
import os
import subprocess

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境信息:")
    print(f"   Python版本: {sys.version}")
    print(f"   Python路径: {sys.executable}")
    print(f"   虚拟环境: {'是' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '否'}")
    print()

def check_installed_packages():
    """检查已安装的包"""
    print("📦 检查已安装的包:")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            fairino_found = False
            for line in lines:
                if 'fairino' in line.lower() or 'fr3' in line.lower():
                    print(f"   ✅ {line}")
                    fairino_found = True
            
            if not fairino_found:
                print("   ❌ 未找到fairino相关包")
                print("   💡 尝试安装: pip install fairino")
        else:
            print("   ❌ 无法获取包列表")
    except Exception as e:
        print(f"   ❌ 检查包列表失败: {e}")
    print()

def test_fairino_import():
    """测试fairino库导入"""
    print("🔌 测试fairino库导入:")
    
    # 测试1: 基本导入
    try:
        import fairino
        print("   ✅ fairino模块导入成功")
        print(f"   📍 模块路径: {fairino.__file__}")
    except ImportError as e:
        print(f"   ❌ fairino模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"   ❌ fairino模块导入异常: {e}")
        return False
    
    # 测试2: Robot类导入
    try:
        from fairino import Robot
        print("   ✅ Robot类导入成功")
    except ImportError as e:
        print(f"   ❌ Robot类导入失败: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Robot类导入异常: {e}")
        return False
    
    # 测试3: 检查Robot类属性
    try:
        # 检查RPC方法是否存在
        if hasattr(Robot, 'RPC'):
            print("   ✅ Robot.RPC方法存在")
        else:
            print("   ⚠️  Robot.RPC方法不存在")
        
        # 尝试创建Robot实例（不连接）
        print("   ✅ fairino库检查完成")
        return True
        
    except Exception as e:
        print(f"   ❌ Robot类检查异常: {e}")
        return False

def check_network_connectivity():
    """检查网络连通性"""
    print("🌐 检查网络连通性:")
    
    test_ips = ["192.168.58.2", "192.168.58.3"]
    
    for ip in test_ips:
        try:
            # 使用ping测试网络连通性
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                      capture_output=True, text=True)
            else:  # Linux/Mac
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {ip} 网络连通")
            else:
                print(f"   ❌ {ip} 网络不通")
                
        except Exception as e:
            print(f"   ❌ {ip} 网络测试失败: {e}")
    print()

def suggest_solutions():
    """建议解决方案"""
    print("💡 解决方案建议:")
    print("1. 确认fairino库安装:")
    print("   pip install fairino")
    print()
    print("2. 如果使用conda环境:")
    print("   conda install fairino")
    print()
    print("3. 检查虚拟环境:")
    print("   确保在正确的虚拟环境中安装和运行")
    print()
    print("4. 重新安装:")
    print("   pip uninstall fairino")
    print("   pip install fairino")
    print()
    print("5. 检查Python位数:")
    print("   确保Python版本与FR3 SDK兼容")
    print()

def test_robot_connection():
    """测试机械臂连接"""
    print("🤖 测试机械臂连接:")
    
    try:
        from fairino import Robot
        
        # 测试右臂连接
        print("   测试右臂连接 (192.168.58.2)...")
        try:
            robot = Robot.RPC('192.168.58.2')
            error, _ = robot.GetActualJointPosDegree()
            if error == 0:
                print("   ✅ 右臂连接成功")
                robot.CloseRPC()
            else:
                print(f"   ❌ 右臂连接失败，错误码: {error}")
        except Exception as e:
            print(f"   ❌ 右臂连接异常: {e}")
        
        # 测试左臂连接
        print("   测试左臂连接 (192.168.58.3)...")
        try:
            robot = Robot.RPC('192.168.58.3')
            error, _ = robot.GetActualJointPosDegree()
            if error == 0:
                print("   ✅ 左臂连接成功")
                robot.CloseRPC()
            else:
                print(f"   ❌ 左臂连接失败，错误码: {error}")
        except Exception as e:
            print(f"   ❌ 左臂连接异常: {e}")
            
    except ImportError:
        print("   ❌ 无法导入fairino库，跳过连接测试")
    except Exception as e:
        print(f"   ❌ 连接测试异常: {e}")
    print()

def main():
    """主函数"""
    print("=" * 80)
    print("🔧 FR3库诊断工具")
    print("=" * 80)
    print()
    
    # 1. 检查Python环境
    check_python_environment()
    
    # 2. 检查已安装的包
    check_installed_packages()
    
    # 3. 测试fairino库导入
    import_success = test_fairino_import()
    
    # 4. 检查网络连通性
    check_network_connectivity()
    
    # 5. 如果库导入成功，测试连接
    if import_success:
        test_robot_connection()
    
    # 6. 建议解决方案
    if not import_success:
        suggest_solutions()
    
    print("=" * 80)
    print("🏁 诊断完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 测试系统API服务器启动脚本
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def setup_paths():
    """设置Python路径"""
    project_root = Path(__file__).parent.parent.parent
    testing_path = project_root / 'testing' / 'lua_scripts'
    
    # 添加到Python路径
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(testing_path))
    
    return project_root, testing_path

def check_dependencies():
    """检查依赖"""
    required_packages = ['flask', 'flask-cors', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"缺少以下依赖包: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    
    return True

def check_lua_availability():
    """检查Lua是否可用"""
    try:
        result = subprocess.run(['lua', '-v'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Lua版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ Lua不可用")
            return False
    except FileNotFoundError:
        print("❌ 未找到Lua解释器")
        print("请安装Lua: ")
        print("  Windows: choco install lua")
        print("  Linux: sudo apt-get install lua5.3")
        print("  macOS: brew install lua")
        return False

def start_test_api_server():
    """启动测试API服务器"""
    project_root, testing_path = setup_paths()
    
    print("="*60)
    print("XC-ROBOT 测试系统API服务器启动")
    print("="*60)
    
    # 检查依赖
    print("1. 检查Python依赖...")
    if not check_dependencies():
        return 1
    
    print("2. 检查Lua环境...")
    if not check_lua_availability():
        print("⚠️  Lua不可用，部分功能可能受限")
    
    # 检查测试API文件
    api_file = testing_path / 'web_api.py'
    if not api_file.exists():
        print(f"❌ 测试API文件不存在: {api_file}")
        return 1
    
    print("3. 启动测试API服务器...")
    print(f"   项目根目录: {project_root}")
    print(f"   API文件路径: {api_file}")
    print(f"   服务地址: http://localhost:5000")
    print("   API端点:")
    print("     POST /api/test/connection - 设备连接测试")
    print("     POST /api/test/run - 运行测试程序")
    print("     POST /api/test/validate - 安全验证")
    print("     GET  /api/test/results - 获取测试结果")
    print("     GET  /api/logs - 获取系统日志")
    print("     POST /api/emergency_stop - 紧急停止")
    print()
    
    try:
        # 切换到正确的工作目录
        os.chdir(project_root)
        
        # 启动Flask应用
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        env['FLASK_APP'] = str(api_file)
        env['FLASK_ENV'] = 'development'
        
        process = subprocess.Popen([
            sys.executable, str(api_file)
        ], env=env, cwd=project_root)
        
        print(f"✅ 测试API服务器已启动 (PID: {process.pid})")
        print("按 Ctrl+C 停止服务器")
        
        # 等待进程结束
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止服务器...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("强制终止服务器...")
                process.kill()
            print("服务器已停止")
        
        return 0
        
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return 1

def main():
    """主函数"""
    try:
        exit_code = start_test_api_server()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"启动脚本异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
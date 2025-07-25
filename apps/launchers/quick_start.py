#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 快速启动和环境检查脚本
适配现有项目结构，一键检查环境、测试连接、启动系统
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_banner():
    """打印启动横幅"""
    print("=" * 80)
    print("    XC-ROBOT 轮式双臂类人形机器人控制系统")
    print("    基于现有项目结构的快速启动脚本")
    print("=" * 80)
    print(f"    启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    工作目录: {os.getcwd()}")
    print("=" * 80)

def check_project_structure():
    """检查项目结构"""
    print("\n🔍 [步骤1/6] 检查项目结构")
    print("-" * 50)
    
    # 检查必需目录
    required_dirs = [
        ("fr3_control", "FR3控制库目录"),
        ("main_control", "主控制模块目录"),
        ("tests", "测试目录"),
    ]
    
    # 检查可选目录
    # 检查可选目录
    optional_dirs = [
        ("venv", "虚拟环境目录"),
        ("logs", "日志目录"),
        ("config", "配置目录")
    ]
    
    all_good = True
    
    for dir_name, description in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {description}: {dir_name}/")
        else:
            print(f"  ❌ {description}: {dir_name}/ - 缺失")
            all_good = False
    
    for dir_name, description in optional_dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {description}: {dir_name}/")
        else:
            print(f"  ⚠️  {description}: {dir_name}/ - 建议创建")
    
    # 检查关键文件
    key_files = [
        ("fr3_control/fairino", "FR3库"),
        ("main_control/robot_controller.py", "机器人控制器"),
        ("tests/dual_arm_connection.py", "双臂连接测试"),
        ("tests/fr3_simple_test.py", "FR3简单测试")
    ]
    
    print(f"\n关键文件检查:")
    for file_path, description in key_files:
        if os.path.exists(file_path):
            print(f"  ✅ {description}: {file_path}")
        else:
            print(f"  ⚠️  {description}: {file_path} - 未找到")
    
    return all_good

def check_python_environment():
    """检查Python环境"""
    print("\n🐍 [步骤2/6] 检查Python环境")
    print("-" * 50)
    
    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  Python版本: {python_version}")
    
    if sys.version_info >= (3, 8):
        print("  ✅ Python版本符合要求 (>= 3.8)")
    else:
        print("  ❌ Python版本过低，建议升级到3.8+")
        return False
    
    # 检查虚拟环境
    venv_exists = os.path.exists("venv")
    if venv_exists:
        print("  ✅ 虚拟环境存在")
        
        # 检查虚拟环境中的Python
        if os.name == 'nt':  # Windows
            venv_python = "venv\\Scripts\\python.exe"
        else:  # Linux/Mac
            venv_python = "venv/bin/python"
        
        if os.path.exists(venv_python):
            print("  ✅ 虚拟环境Python可执行文件存在")
            return True
        else:
            print("  ❌ 虚拟环境Python可执行文件缺失")
            return False
    else:
        print("  ⚠️  虚拟环境不存在，将使用系统Python")
        return True

def check_dependencies():
    """检查依赖包"""
    print("\n📦 [步骤3/6] 检查Python依赖包")
    print("-" * 50)
    
    # 确定Python执行路径
    if os.path.exists("venv"):
        if os.name == 'nt':
            python_exe = "venv\\Scripts\\python.exe"
        else:
            python_exe = "venv/bin/python"
    else:
        python_exe = sys.executable
    
    # 检查关键依赖
    dependencies = [
        ("requests", "HTTP请求库"),
        ("yaml", "YAML配置解析"),
        ("numpy", "数值计算库"),
        ("threading", "多线程支持（内置）")
    ]
    
    all_good = True
    for dep_name, description in dependencies:
        try:
            if dep_name == "threading":
                # 内置模块
                import threading
                print(f"  ✅ {description}")
            elif dep_name == "yaml":
                import yaml
                print(f"  ✅ {description}")
            else:
                result = subprocess.run(
                    [python_exe, "-c", f"import {dep_name}; print('{dep_name} OK')"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description} - 导入失败")
                    all_good = False
        except Exception as e:
            print(f"  ❌ {description} - 检查异常: {e}")
            all_good = False
    
    return all_good

def check_fr3_library():
    """检查FR3机械臂库"""
    print("\n🤖 [步骤4/6] 检查FR3机械臂库")
    print("-" * 50)
    
    # 检查FR3控制目录
    fr3_control_path = Path("fr3_control")
    if not fr3_control_path.exists():
        print("  ❌ fr3_control目录不存在")
        return False
    
    # 检查fairino库
    fairino_path = fr3_control_path / "fairino"
    if fairino_path.exists():
        print("  ✅ fairino库目录存在")
    else:
        print("  ❌ fairino库目录不存在")
        return False
    
    # 检查关键文件（不强制要求fairino.dll）
    required_files = [
        "fairino/__init__.py"
    ]
    
    optional_files = [
        "fairino.dll",
        "libfairino",
        "fr3_wrapper.py"
    ]
    
    missing_required = []
    for file_rel_path in required_files:
        file_path = fr3_control_path / file_rel_path
        if file_path.exists():
            print(f"  ✅ {file_rel_path}")
        else:
            print(f"  ❌ {file_rel_path} - 缺失")
            missing_required.append(file_rel_path)
    
    # 检查可选文件
    for file_rel_path in optional_files:
        file_path = fr3_control_path / file_rel_path
        if file_path.exists():
            print(f"  ✅ {file_rel_path} (可选)")
        else:
            print(f"  ℹ️  {file_rel_path} - 未找到（可选）")
    
    if missing_required:
        print(f"  ❌ 缺失 {len(missing_required)} 个必需文件")
        return False
    
    # 尝试导入测试
    try:
        if os.path.exists("venv"):
            if os.name == 'nt':
                python_exe = "venv\\Scripts\\python.exe"
            else:
                python_exe = "venv/bin/python"
        else:
            python_exe = sys.executable
        
        test_code = """
import sys
import os
sys.path.append('fr3_control')
try:
    from fairino import Robot
    print('fairino导入成功')
except Exception as e:
    print(f'fairino导入失败: {e}')
    raise
"""
        
        result = subprocess.run(
            [python_exe, "-c", test_code],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0 and "fairino导入成功" in result.stdout:
            print("  ✅ fairino库导入测试成功")
            return True
        else:
            print("  ❌ fairino库导入测试失败")
            if result.stderr:
                print(f"     错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ fairino库导入测试异常: {e}")
        return False

def test_network_connectivity():
    """测试网络连通性"""
    print("\n🌐 [步骤5/6] 测试网络连通性")
    print("-" * 50)
    
    # 测试目标IP地址
    test_ips = [
        ("192.168.58.2", "FR3右臂机械臂"),
        ("192.168.58.3", "FR3左臂机械臂"),
        ("192.168.31.211", "Hermes底盘（如果可用）")
    ]
    
    connectivity_results = []
    
    for ip, description in test_ips:
        try:
            if os.name == 'nt':  # Windows
                cmd = ["ping", "-n", "2", ip]
            else:  # Linux/Mac
                cmd = ["ping", "-c", "2", ip]
            
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                print(f"  ✅ {description} ({ip}) - 网络连通")
                connectivity_results.append(True)
            else:
                print(f"  ❌ {description} ({ip}) - 网络不通")
                connectivity_results.append(False)
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  {description} ({ip}) - ping超时")
            connectivity_results.append(False)
        except Exception as e:
            print(f"  ❌ {description} ({ip}) - 测试异常: {e}")
            connectivity_results.append(False)
    
    # 至少需要一个机械臂连通
    return any(connectivity_results[:2])

def run_test_scripts():
    """运行现有测试脚本"""
    print("\n🧪 [步骤6/6] 运行现有测试脚本")
    print("-" * 50)
    
    # 查找可用的测试脚本
    test_scripts = [
        ("tests/fr3_simple_test.py", "FR3简单连接测试"),
        ("tests/dual_arm_connection.py", "双臂连接测试"),
        ("tests/hermes_test_connection.py", "Hermes连接测试")
    ]
    
    # 确定Python执行路径
    if os.path.exists("venv"):
        if os.name == 'nt':
            python_exe = "venv\\Scripts\\python.exe"
        else:
            python_exe = "venv/bin/python"
    else:
        python_exe = sys.executable
    
    # 检查测试脚本是否存在
    available_tests = []
    for script, description in test_scripts:
        if os.path.exists(script):
            available_tests.append((script, description))
    
    if not available_tests:
        print("  ⚠️  未找到可用的测试脚本")
        return True
    
    print(f"  发现 {len(available_tests)} 个测试脚本")
    print("  📝 注意：测试将从项目根目录运行，以确保正确的路径解析")
    
    # 询问是否运行测试
    print("\n  是否运行快速测试？")
    print("  y - 运行所有测试")
    print("  s - 选择性运行")
    print("  n - 跳过测试")
    
    choice = input("  请选择 (y/s/n): ").strip().lower()
    
    if choice == 'n':
        print("  ⚠️  跳过测试")
        return True
    elif choice == 's':
        return run_selective_tests(available_tests, python_exe)
    else:
        return run_all_tests(available_tests, python_exe)

def run_all_tests(available_tests, python_exe):
    """运行所有测试"""
    print("  运行所有测试...")
    
    # 获取项目根目录的绝对路径
    project_root = os.path.abspath(os.getcwd())
    
    for script, description in available_tests:
        print(f"\n  📝 运行 {description}...")
        try:
            # 创建修改后的环境变量，包含项目根目录路径
            env = os.environ.copy()
            env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
            env['PYTHONIOENCODING'] = 'utf-8'  # 强制使用UTF-8编码
            
            # 运行测试，确保从项目根目录运行，并传递环境变量
            result = subprocess.run(
                [python_exe, script],
                cwd=project_root,  # 设置工作目录为项目根目录
                env=env,           # 传递修改后的环境变量
                capture_output=True, text=True, timeout=60,
                encoding='utf-8', errors='replace'  # 强制UTF-8编码，遇到问题时替换字符
            )
            
            if result.returncode == 0:
                print(f"    ✅ {description} - 成功")
                # 显示成功输出的关键信息
                if result.stdout:
                    success_lines = [line for line in result.stdout.split('\n') 
                                   if '✓' in line or '[OK]' in line or '成功' in line or 'SUCCESS' in line]
                    for line in success_lines[:3]:  # 只显示前3行成功信息
                        if line.strip():
                            try:
                                print(f"      {line.strip()}")
                            except UnicodeEncodeError:
                                # 如果还是有编码问题，安全地显示
                                safe_line = line.encode('ascii', errors='ignore').decode('ascii')
                                print(f"      {safe_line.strip()}")
            else:
                print(f"    ❌ {description} - 失败")
                if result.stderr:
                    # 显示错误信息的关键部分，处理编码问题
                    error_lines = result.stderr.split('\n')
                    for line in error_lines[:5]:  # 显示前5行错误信息
                        if line.strip() and 'Traceback' not in line:
                            try:
                                print(f"      {line.strip()}")
                            except UnicodeEncodeError:
                                safe_line = line.encode('ascii', errors='ignore').decode('ascii')
                                print(f"      {safe_line.strip()}")
                if result.stdout:
                    # 也检查stdout中的错误信息
                    stdout_lines = result.stdout.split('\n')
                    for line in stdout_lines[:3]:
                        if '✗' in line or '[ERROR]' in line or '失败' in line or 'ERROR' in line:
                            try:
                                print(f"      {line.strip()}")
                            except UnicodeEncodeError:
                                safe_line = line.encode('ascii', errors='ignore').decode('ascii')
                                print(f"      {safe_line.strip()}")
                            
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  {description} - 超时（60秒）")
        except Exception as e:
            print(f"    ❌ {description} - 异常: {e}")
    
    return True

def run_selective_tests(available_tests, python_exe):
    """选择性运行测试"""
    print("  可用测试:")
    for i, (script, description) in enumerate(available_tests, 1):
        print(f"    {i}. {description}")
    
    try:
        selection = input("  请输入要运行的测试编号 (多个用逗号分隔): ").strip()
        if not selection:
            print("  ⚠️  未选择测试")
            return True
        
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        
        # 获取项目根目录的绝对路径
        project_root = os.path.abspath(os.getcwd())
        
        for idx in indices:
            if 0 <= idx < len(available_tests):
                script, description = available_tests[idx]
                print(f"\n  📝 运行 {description}...")
                
                try:
                    # 创建修改后的环境变量
                    env = os.environ.copy()
                    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
                    
                    result = subprocess.run(
                        [python_exe, script],
                        cwd=project_root,  # 设置工作目录为项目根目录
                        env=env,           # 传递修改后的环境变量
                        capture_output=True, text=True, timeout=60
                    )
                    
                    if result.returncode == 0:
                        print(f"    ✅ {description} - 成功")
                        # 显示一些成功的关键信息
                        if result.stdout:
                            success_lines = [line for line in result.stdout.split('\n') if '✓' in line or '成功' in line]
                            for line in success_lines[:2]:
                                if line.strip():
                                    print(f"      {line.strip()}")
                    else:
                        print(f"    ❌ {description} - 失败")
                        if result.stderr:
                            error_lines = result.stderr.split('\n')
                            for line in error_lines[:3]:
                                if line.strip() and 'Traceback' not in line:
                                    print(f"      {line.strip()}")
                except Exception as e:
                    print(f"    ❌ {description} - 异常: {e}")
            else:
                print(f"    ❌ 无效编号: {idx + 1}")
        
        return True
        
    except ValueError:
        print("    ❌ 输入格式错误")
        return False

def create_missing_files():
    """创建缺失的基础文件"""
    print("\n⚙️  创建缺失的基础文件")
    print("-" * 50)
    
    files_created = []
    
    # 创建配置文件
    if not os.path.exists("robot_config.yaml"):
        config_content = """# XC-ROBOT 基础配置
system:
  name: "XC-ROBOT"
  version: "1.0.0"

network:
  hermes_url: "http://192.168.1.100"
  right_arm_ip: "192.168.58.2"
  left_arm_ip: "192.168.58.3"

motion:
  default_velocity: 20
  timeout: 30
  home_position: [0.0, -20.0, -90.0, -90.0, 90.0, 0.0]

logging:
  level: "INFO"
"""
        try:
            with open("robot_config.yaml", 'w', encoding='utf-8') as f:
                f.write(config_content)
            print("  ✅ 创建 robot_config.yaml")
            files_created.append("robot_config.yaml")
        except Exception as e:
            print(f"  ❌ 创建 robot_config.yaml 失败: {e}")
    
    # 创建logs目录
    if not os.path.exists("logs"):
        try:
            os.makedirs("logs")
            print("  ✅ 创建 logs/ 目录")
            files_created.append("logs/")
        except Exception as e:
            print(f"  ❌ 创建 logs/ 目录失败: {e}")
    
    # 创建requirements.txt
    if not os.path.exists("requirements.txt"):
        requirements = """requests>=2.28.0
PyYAML>=6.0
numpy>=1.21.0
"""
        try:
            with open("requirements.txt", 'w', encoding='utf-8') as f:
                f.write(requirements)
            print("  ✅ 创建 requirements.txt")
            files_created.append("requirements.txt")
        except Exception as e:
            print(f"  ❌ 创建 requirements.txt 失败: {e}")
    
    return files_created

def show_system_summary(checks_passed):
    """显示系统检查摘要"""
    print("\n" + "=" * 80)
    print("    系统检查摘要")
    print("=" * 80)
    
    check_names = [
        "项目结构",
        "Python环境", 
        "依赖包",
        "FR3库",
        "网络连通",
        "测试脚本"
    ]
    
    passed_count = sum(checks_passed)
    total_count = len(checks_passed)
    
    print(f"\n检查结果: {passed_count}/{total_count} 项通过\n")
    
    for i, (name, passed) in enumerate(zip(check_names, checks_passed)):
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name:10} {status}")
    
    # 给出建议
    if passed_count == total_count:
        print(f"\n🎉 所有检查都通过了！")
        print(f"🚀 系统已准备就绪，可以启动XC-ROBOT")
        return True
    elif passed_count >= total_count * 0.7:
        print(f"\n⚠️  大部分检查通过，系统基本可用")
        print(f"💡 建议解决剩余问题后再使用")
        return True
    else:
        print(f"\n❌ 检查失败项较多，需要解决问题")
        print(f"📝 请参考上述检查结果解决问题")
        return False

def show_next_steps():
    """显示后续步骤"""
    print(f"\n" + "=" * 60)
    print(f"    后续步骤")
    print(f"=" * 60)
    
    print(f"\n🚀 启动系统:")
    if os.path.exists("main.py"):
        if os.path.exists("venv"):
            if os.name == 'nt':
                print(f"   venv\\Scripts\\python.exe main.py")
            else:
                print(f"   venv/bin/python main.py")
        else:
            print(f"   python main.py")
    else:
        print(f"   请先创建 main.py 主程序文件")
    
    print(f"\n🔧 手动测试:")
    print(f"   python fr3_simple_test.py          # 测试单臂连接")
    print(f"   python dual_arm_connection.py      # 测试双臂连接")
    
    print(f"\n📁 项目文件:")
    print(f"   robot_config.yaml                  # 主配置文件")
    print(f"   logs/                              # 日志目录")
    print(f"   fr3_control/                       # FR3控制库")
    print(f"   main_control/                      # 主控制模块")

def main():
    """主函数"""
    print_banner()
    
    # 检查是否在正确目录
    if not (os.path.exists("fr3_control") or os.path.exists("main_control")):
        print("\n⚠️  警告: 当前目录可能不是XC-ROBOT项目根目录")
        print("请确保在包含 fr3_control/ 和 main_control/ 的目录中运行")
        
        continue_anyway = input("\n继续检查？(y/N): ").strip().lower()
        if continue_anyway not in ['y', 'yes']:
            print("请切换到正确目录后重新运行")
            return 1
    
    # 创建缺失文件
    created_files = create_missing_files()
    if created_files:
        print(f"  💾 创建了 {len(created_files)} 个文件")
    
    # 执行检查步骤
    checks = [
        check_project_structure,
        check_python_environment,
        check_dependencies,
        check_fr3_library,
        test_network_connectivity,
        run_test_scripts  # 更新函数名
    ]
    
    results = []
    for check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except KeyboardInterrupt:
            print(f"\n\n⚠️  用户中断检查")
            return 1
        except Exception as e:
            print(f"\n❌ 检查过程异常: {e}")
            results.append(False)
    
    # 显示摘要
    system_ready = show_system_summary(results)
    
    if system_ready:
        show_next_steps()
        
        # 询问是否启动主程序
        if os.path.exists("main.py"):
            print(f"\n" + "="*50)
            start_main = input("是否立即启动XC-ROBOT主程序？(y/N): ").strip().lower()
            if start_main in ['y', 'yes']:
                print(f"\n🚀 启动XC-ROBOT主程序...")
                try:
                    if os.path.exists("venv"):
                        if os.name == 'nt':
                            python_exe = "venv\\Scripts\\python.exe"
                        else:
                            python_exe = "venv/bin/python"
                    else:
                        python_exe = sys.executable
                    
                    subprocess.run([python_exe, "main.py"])
                except KeyboardInterrupt:
                    print(f"\n⚠️  主程序被用户中断")
                except Exception as e:
                    print(f"\n❌ 启动主程序失败: {e}")
    
    return 0 if system_ready else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n⚠️  程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 程序执行异常: {e}")
        sys.exit(1)
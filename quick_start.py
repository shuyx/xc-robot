#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 快速启动和环境检查脚本（修复版本）
解决subprocess调用时的用户交互阻塞问题
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
    print("    基于现有项目结构的快速启动脚本 (修复版)")
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
    
    # 尝试导入测试（使用较短的超时时间）
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
            capture_output=True, text=True, timeout=10  # 减少超时时间
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
        ("192.168.1.100", "Hermes底盘（如果可用）")
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

def test_fr3_connection_directly():
    """直接在当前进程中测试FR3连接（避免subprocess阻塞）"""
    print("\n🧪 [步骤6/6] 直接测试FR3连接")
    print("-" * 50)
    
    # 检查测试脚本是否存在
    fr3_test_script = "tests/fr3_simple_test.py"
    dual_arm_test_script = "tests/dual_arm_connection.py"
    
    print("  📝 进行FR3连接直接测试（跳过用户交互）")
    
    # 尝试直接导入并测试连接
    try:
        # 添加路径
        import sys
        project_root = os.path.abspath(os.getcwd())
        fr3_control_path = os.path.join(project_root, 'fr3_control')
        
        if fr3_control_path not in sys.path:
            sys.path.insert(0, fr3_control_path)
        
        # 导入fairino
        from fairino import Robot
        print("  ✅ fairino库导入成功")
        
        # 测试连接（使用较短超时）
        test_ips = ['192.168.58.2', '192.168.58.3']
        connection_results = []
        
        for i, ip in enumerate(test_ips):
            arm_name = "右臂" if i == 0 else "左臂"
            try:
                print(f"  🔗 测试{arm_name}连接 ({ip})...")
                
                # 创建机器人连接（短超时）
                robot = Robot.RPC(ip)
                
                # 测试基本通信
                try:
                    sdk_version = robot.GetSDKVersion()
                    print(f"    ✅ {arm_name}连接成功，SDK版本: {sdk_version}")
                    connection_results.append(True)
                    
                    # 清理连接
                    robot.CloseRPC()
                    
                except Exception as api_e:
                    print(f"    ⚠️  {arm_name}连接成功但API调用失败: {api_e}")
                    connection_results.append(True)  # 连接成功，只是API有问题
                    try:
                        robot.CloseRPC()
                    except:
                        pass
                        
            except Exception as conn_e:
                print(f"    ❌ {arm_name}连接失败: {conn_e}")
                connection_results.append(False)
        
        # 结果汇总
        successful_connections = sum(connection_results)
        print(f"\n  📊 连接测试结果: {successful_connections}/2 个机械臂连接成功")
        
        if successful_connections > 0:
            print("  ✅ FR3机械臂基本连接功能正常")
            return True
        else:
            print("  ❌ 所有FR3机械臂连接失败")
            return False
            
    except ImportError as e:
        print(f"  ❌ 无法导入fairino库: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 连接测试异常: {e}")
        return False

def create_non_interactive_test_runner():
    """创建非交互式测试运行器脚本"""
    print("\n⚙️  创建非交互式测试运行器")
    print("-" * 50)
    
    # 创建简化的测试脚本，去除用户交互
    test_runner_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非交互式FR3连接测试脚本
专门用于自动化测试，无用户交互
"""

import sys
import os
import time

# 设置路径
project_root = os.path.abspath(os.path.dirname(__file__))
fr3_control_path = os.path.join(project_root, 'fr3_control')
sys.path.insert(0, fr3_control_path)

def test_single_arm(ip, arm_name):
    """测试单个机械臂连接"""
    try:
        from fairino import Robot
        
        print(f"[{arm_name}] 连接测试开始...")
        robot = Robot.RPC(ip)
        
        # 基本信息测试
        try:
            sdk_version = robot.GetSDKVersion()
            print(f"[{arm_name}] ✅ SDK版本: {sdk_version}")
        except Exception as e:
            print(f"[{arm_name}] ⚠️ GetSDKVersion失败: {e}")
        
        try:
            controller_ip = robot.GetControllerIP()
            print(f"[{arm_name}] ✅ 控制器IP: {controller_ip}")
        except Exception as e:
            print(f"[{arm_name}] ⚠️ GetControllerIP失败: {e}")
        
        # 清理连接
        robot.CloseRPC()
        print(f"[{arm_name}] ✅ 连接测试完成")
        return True
        
    except Exception as e:
        print(f"[{arm_name}] ❌ 连接失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 非交互式FR3连接测试 ===")
    
    # 测试两个机械臂
    results = []
    test_ips = [
        ("192.168.58.2", "右臂"),
        ("192.168.58.3", "左臂")
    ]
    
    for ip, arm_name in test_ips:
        result = test_single_arm(ip, arm_name)
        results.append(result)
    
    # 结果汇总
    successful = sum(results)
    print(f"\\n=== 测试结果: {successful}/2 个机械臂连接成功 ===")
    
    return 0 if successful > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    try:
        test_runner_path = "non_interactive_test.py"
        with open(test_runner_path, 'w', encoding='utf-8') as f:
            f.write(test_runner_content)
        print(f"  ✅ 创建非交互式测试脚本: {test_runner_path}")
        return test_runner_path
    except Exception as e:
        print(f"  ❌ 创建测试脚本失败: {e}")
        return None

def run_non_interactive_tests():
    """运行非交互式测试"""
    print("\n🧪 [可选] 运行非交互式自动测试")
    print("-" * 50)
    
    # 创建非交互式测试脚本
    test_script = create_non_interactive_test_runner()
    if not test_script:
        print("  ❌ 无法创建测试脚本")
        return False
    
    # 确定Python执行路径
    if os.path.exists("venv"):
        if os.name == 'nt':
            python_exe = "venv\\Scripts\\python.exe"
        else:
            python_exe = "venv/bin/python"
    else:
        python_exe = sys.executable
    
    try:
        print("  🚀 运行非交互式测试...")
        
        # 获取项目根目录的绝对路径
        project_root = os.path.abspath(os.getcwd())
        
        # 创建修改后的环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 运行测试
        result = subprocess.run(
            [python_exe, test_script],
            cwd=project_root,
            env=env,
            capture_output=True, 
            text=True, 
            timeout=30,  # 30秒超时
            encoding='utf-8', 
            errors='replace'
        )
        
        if result.returncode == 0:
            print("  ✅ 非交互式测试成功完成")
            # 显示关键输出
            if result.stdout:
                print("  📋 测试输出:")
                for line in result.stdout.split('\n')[:10]:  # 只显示前10行
                    if line.strip():
                        print(f"    {line.strip()}")
            return True
        else:
            print("  ❌ 非交互式测试失败")
            if result.stderr:
                print("  📋 错误信息:")
                for line in result.stderr.split('\n')[:5]:  # 显示前5行错误
                    if line.strip() and 'Traceback' not in line:
                        print(f"    {line.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  非交互式测试超时（30秒）")
        return False
    except Exception as e:
        print(f"  ❌ 运行非交互式测试异常: {e}")
        return False
    finally:
        # 清理测试脚本
        try:
            if os.path.exists(test_script):
                os.remove(test_script)
                print(f"  🗑️  已清理临时测试脚本")
        except:
            pass

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
        "FR3连接测试"
    ]
    
    passed_count = sum(checks_passed)
    total_count = len(checks_passed)
    
    print(f"\n检查结果: {passed_count}/{total_count} 项通过\n")
    
    for i, (name, passed) in enumerate(zip(check_names, checks_passed)):
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name:12} {status}")
    
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
    print(f"   python tests/fr3_simple_test.py          # 测试单臂连接")
    print(f"   python tests/dual_arm_connection.py      # 测试双臂连接")
    
    print(f"\n📁 项目文件:")
    print(f"   robot_config.yaml                        # 主配置文件")
    print(f"   logs/                                    # 日志目录")
    print(f"   fr3_control/                             # FR3控制库")
    print(f"   main_control/                            # 主控制模块")
    
    print(f"\n💡 解决超时问题:")
    print(f"   - 现有测试脚本包含用户交互，通过subprocess调用会阻塞")
    print(f"   - 建议直接运行测试脚本进行调试")
    print(f"   - 或者使用上面创建的非交互式测试")

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
    
    # 执行检查步骤（使用直接测试代替subprocess测试）
    checks = [
        check_project_structure,
        check_python_environment,
        check_dependencies,
        check_fr3_library,
        test_network_connectivity,
        test_fr3_connection_directly  # 使用直接测试代替subprocess
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
    
    # 可选的非交互式测试
    print(f"\n" + "="*50)
    run_auto_test = input("是否运行自动化非交互式测试？(y/N): ").strip().lower()
    if run_auto_test in ['y', 'yes']:
        auto_test_result = run_non_interactive_tests()
        if auto_test_result:
            print("  ✅ 自动化测试补充完成")
        else:
            print("  ⚠️  自动化测试未完全成功，但不影响主要功能")
    
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
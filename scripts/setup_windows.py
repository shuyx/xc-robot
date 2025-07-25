#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows环境自动适配脚本
检测、安装和配置Windows环境下的XC-ROBOT依赖
"""

import os
import sys
import subprocess
import platform
import json
import shutil
from pathlib import Path
import urllib.request

class WindowsSetup:
    """Windows环境自动配置器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.is_admin = self._check_admin_rights()
        self.python_version = sys.version_info
        self.system_info = self._get_system_info()
        
    def _check_admin_rights(self) -> bool:
        """检查是否有管理员权限"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _get_system_info(self) -> dict:
        """获取系统信息"""
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'architecture': platform.architecture()[0],
            'windows_version': platform.win32_ver() if hasattr(platform, 'win32_ver') else None
        }
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("🔍 检查Python版本...")
        if self.python_version >= (3, 7):
            print(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro} - 版本符合要求")
            return True
        else:
            print(f"❌ Python版本过低: {self.python_version.major}.{self.python_version.minor}")
            print("   请安装Python 3.7+: https://www.python.org/downloads/")
            return False
    
    def check_git(self) -> bool:
        """检查Git是否安装"""
        print("🔍 检查Git...")
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git未安装")
            print("   请安装Git: https://git-scm.com/download/win")
            return False
    
    def setup_virtual_environment(self) -> bool:
        """设置虚拟环境"""
        print("🔍 设置Python虚拟环境...")
        
        venv_path = self.project_root / "venv"
        
        # 如果已存在虚拟环境，询问是否重建
        if venv_path.exists():
            print(f"⚠️ 虚拟环境已存在: {venv_path}")
            choice = input("是否重建虚拟环境? (y/N): ").lower()
            if choice == 'y':
                print("🗑️ 删除现有虚拟环境...")
                shutil.rmtree(venv_path)
            else:
                print("✅ 使用现有虚拟环境")
                return True
        
        try:
            print("📦 创建虚拟环境...")
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], 
                          check=True)
            print(f"✅ 虚拟环境创建成功: {venv_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 虚拟环境创建失败: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        print("📦 安装项目依赖...")
        
        venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
        venv_pip = self.project_root / "venv" / "Scripts" / "pip.exe"
        
        if not venv_python.exists():
            print("❌ 虚拟环境Python不存在")
            return False
        
        try:
            # 升级pip
            print("⬆️ 升级pip...")
            subprocess.run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                          check=True)
            
            # 安装核心依赖
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                print("📋 安装核心依赖...")
                subprocess.run([str(venv_pip), 'install', '-r', str(requirements_file)], 
                              check=True)
                print("✅ 核心依赖安装完成")
            else:
                print("❌ requirements.txt 文件不存在")
                return False
            
            # 询问是否安装可选依赖
            optional_deps = {
                "开发工具": "requirements/dev.txt",
                "监控图表": "requirements/monitoring.txt", 
                "VTK 3D仿真": "requirements/simulation_vtk.txt"
            }
            
            for name, file_path in optional_deps.items():
                req_file = self.project_root / file_path
                if req_file.exists():
                    choice = input(f"是否安装 {name}? (y/N): ").lower()
                    if choice == 'y':
                        print(f"📦 安装 {name}...")
                        subprocess.run([str(venv_pip), 'install', '-r', str(req_file)], 
                                      check=True)
                        print(f"✅ {name} 安装完成")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    
    def configure_platform(self) -> bool:
        """配置平台特定设置"""
        print("⚙️ 配置Windows平台设置...")
        
        try:
            # 导入平台配置模块
            sys.path.insert(0, str(self.project_root))
            from core.platform.config import auto_configure
            
            # 自动配置
            adapter = auto_configure()
            print("✅ 平台配置完成")
            return True
            
        except Exception as e:
            print(f"❌ 平台配置失败: {e}")
            return False
    
    def create_shortcuts(self) -> bool:
        """创建Windows快捷方式和启动脚本"""
        print("🔗 创建启动脚本...")
        
        try:
            # 创建批处理启动脚本
            bat_content = f"""@echo off
title XC-ROBOT Control System
cd /d "{self.project_root}"
echo ==========================================
echo 🤖 XC-ROBOT 机器人控制系统
echo ==========================================
echo.

REM 激活虚拟环境
call venv\\Scripts\\activate.bat

REM 检查依赖
echo 🔍 检查运行环境...
python -c "import PyQt5; print('✅ PyQt5 可用')" 2>nul || (echo ❌ PyQt5 未安装 && pause && exit)
python -c "import numpy; print('✅ NumPy 可用')" 2>nul || (echo ❌ NumPy 未安装 && pause && exit)

echo.
echo 🚀 启动GUI界面...
python apps/launchers/start_desktop_gui.py

echo.
echo 程序已退出
pause
"""
            
            # 写入启动脚本
            start_script = self.project_root / "start_xc_robot.bat"
            with open(start_script, 'w', encoding='gbk') as f:
                f.write(bat_content)
            
            print(f"✅ 启动脚本创建: {start_script}")
            
            # 创建Web版本启动脚本
            web_bat_content = f"""@echo off
title XC-ROBOT Web Interface
cd /d "{self.project_root}"
echo ==========================================
echo 🌐 XC-ROBOT Web 界面
echo ==========================================

call venv\\Scripts\\activate.bat
echo 🚀 启动Web服务器...
python apps/launchers/start_web_dev.py

pause
"""
            web_script = self.project_root / "start_web_interface.bat"
            with open(web_script, 'w', encoding='gbk') as f:
                f.write(web_bat_content)
            
            print(f"✅ Web启动脚本创建: {web_script}")
            return True
            
        except Exception as e:
            print(f"❌ 启动脚本创建失败: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """验证安装"""
        print("🔍 验证安装...")
        
        venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
        
        # 检查关键模块
        test_modules = [
            'PyQt5',
            'numpy', 
            'requests',
            'cv2'
        ]
        
        all_good = True
        for module in test_modules:
            try:
                subprocess.run([str(venv_python), '-c', f'import {module}'], 
                              check=True, capture_output=True)
                print(f"✅ {module}")
            except subprocess.CalledProcessError:
                print(f"❌ {module}")
                all_good = False
        
        return all_good
    
    def run_setup(self) -> bool:
        """运行完整设置流程"""
        print("=" * 60)
        print("🤖 XC-ROBOT Windows 环境自动配置")
        print("=" * 60)
        print()
        
        # 显示系统信息
        print("💻 系统信息:")
        for key, value in self.system_info.items():
            print(f"   {key}: {value}")
        print()
        
        steps = [
            ("检查Python版本", self.check_python_version),
            ("检查Git", self.check_git),
            ("设置虚拟环境", self.setup_virtual_environment),
            ("安装依赖", self.install_dependencies),
            ("配置平台", self.configure_platform),
            ("创建启动脚本", self.create_shortcuts),
            ("验证安装", self.verify_installation)
        ]
        
        for step_name, step_func in steps:
            print(f"📋 步骤: {step_name}")
            if not step_func():
                print(f"❌ 步骤失败: {step_name}")
                return False
            print()
        
        print("🎉 Windows环境配置完成!")
        print()
        print("📋 使用说明:")
        print("   1. 双击 'start_xc_robot.bat' 启动桌面GUI")
        print("   2. 双击 'start_web_interface.bat' 启动Web界面")
        print("   3. 命令行: cd 到项目目录，运行 'venv\\Scripts\\activate.bat'")
        print()
        print("🔗 快捷方式:")
        print(f"   桌面GUI: {self.project_root / 'start_xc_robot.bat'}")
        print(f"   Web界面: {self.project_root / 'start_web_interface.bat'}")
        
        return True

def main():
    """主函数"""
    if platform.system() != 'Windows':
        print("❌ 此脚本仅适用于Windows系统")
        return False
    
    setup = WindowsSetup()
    return setup.run_setup()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 配置失败，请检查错误信息")
        input("按Enter键退出...")
        sys.exit(1)
    else:
        print("\n✅ 配置成功完成!")
        input("按Enter键退出...")
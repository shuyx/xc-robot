#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 跨平台自动适配配置系统
自动检测并适配 Mac/Windows/Linux 平台差异
"""

import os
import sys
import platform
import json
from pathlib import Path
from typing import Dict, Any, Optional

class PlatformAdapter:
    """跨平台适配器 - 自动处理平台差异"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_mac = self.platform == 'darwin'
        self.is_windows = self.platform == 'windows'
        self.is_linux = self.platform == 'linux'
        
        # 项目根目录
        self.project_root = Path(__file__).parent
        
        # 加载平台配置
        self.config = self._load_platform_config()
        
    def _load_platform_config(self) -> Dict[str, Any]:
        """加载平台配置文件"""
        config_file = self.project_root / 'config' / 'platform_configs.json'
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建默认配置
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认平台配置"""
        default_config = {
            "darwin": {  # macOS
                "python_executable": "python3",
                "gui_framework": "PyQt5",
                "file_separator": "/",
                "default_font": "SF Pro Display",
                "window_scaling": 1.0,
                "robot_libs": {
                    "fairino": "fr3_control/fairino/Robot.py",
                    "opencv": "cv2"
                },
                "network": {
                    "fr3_right_ip": "192.168.58.2",
                    "fr3_left_ip": "192.168.58.3",
                    "hermes_ip": "192.168.0.100"
                },
                "paths": {
                    "venv": "./venv/bin/activate",
                    "logs": "./logs",
                    "data": "./data"
                }
            },
            "windows": {  # Windows
                "python_executable": "python",
                "gui_framework": "PyQt5", 
                "file_separator": "\\",
                "default_font": "Segoe UI",
                "window_scaling": 1.25,
                "robot_libs": {
                    "fairino": "fr3_control\\fairino\\Robot.py",
                    "opencv": "cv2"
                },
                "network": {
                    "fr3_right_ip": "192.168.58.2", 
                    "fr3_left_ip": "192.168.58.3",
                    "hermes_ip": "192.168.0.100"
                },
                "paths": {
                    "venv": ".\\venv\\Scripts\\activate.bat",
                    "logs": ".\\logs",
                    "data": ".\\data"
                }
            },
            "linux": {  # Linux
                "python_executable": "python3",
                "gui_framework": "PyQt5",
                "file_separator": "/",
                "default_font": "Ubuntu",
                "window_scaling": 1.0,
                "robot_libs": {
                    "fairino": "fr3_control/fairino/Robot.py",
                    "opencv": "cv2"
                },
                "network": {
                    "fr3_right_ip": "192.168.58.2",
                    "fr3_left_ip": "192.168.58.3", 
                    "hermes_ip": "192.168.0.100"
                },
                "paths": {
                    "venv": "./venv/bin/activate",
                    "logs": "./logs",
                    "data": "./data"
                }
            }
        }
        
        # 保存默认配置
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置到文件"""
        config_dir = self.project_root / 'config'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'platform_configs.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, indent=2, ensure_ascii=False, fp=f)
    
    def get_platform_config(self) -> Dict[str, Any]:
        """获取当前平台配置"""
        return self.config.get(self.platform, {})
    
    def get_path(self, path_type: str) -> str:
        """获取平台适配的路径"""
        platform_config = self.get_platform_config()
        paths = platform_config.get('paths', {})
        return paths.get(path_type, '')
    
    def get_robot_lib_path(self, lib_name: str) -> str:
        """获取机器人库路径"""
        platform_config = self.get_platform_config()
        robot_libs = platform_config.get('robot_libs', {})
        return robot_libs.get(lib_name, '')
    
    def get_network_config(self, device: str) -> str:
        """获取网络设备IP配置"""
        platform_config = self.get_platform_config()
        network = platform_config.get('network', {})
        return network.get(device, '')
    
    def get_gui_config(self) -> Dict[str, Any]:
        """获取GUI配置"""
        platform_config = self.get_platform_config()
        return {
            'framework': platform_config.get('gui_framework', 'PyQt5'),
            'font': platform_config.get('default_font', 'Arial'),
            'scaling': platform_config.get('window_scaling', 1.0)
        }
    
    def adapt_file_path(self, path: str) -> str:
        """适配文件路径到当前平台"""
        if self.is_windows:
            return path.replace('/', '\\')
        else:
            return path.replace('\\', '/')
    
    def get_startup_command(self) -> str:
        """获取平台适配的启动命令"""
        platform_config = self.get_platform_config()
        python_exe = platform_config.get('python_executable', 'python')
        
        if self.is_windows:
            return f"{python_exe} start_gui.py"
        else:
            return f"{python_exe} start_gui.py"
    
    def check_dependencies(self) -> Dict[str, bool]:
        """检查平台依赖是否满足"""
        dependencies = {}
        
        # 检查Python版本
        python_version = sys.version_info
        dependencies['python'] = python_version >= (3, 7)
        
        # 检查必要的包
        required_packages = ['PyQt5', 'requests', 'numpy']
        for package in required_packages:
            try:
                __import__(package)
                dependencies[package] = True
            except ImportError:
                dependencies[package] = False
        
        # 检查机器人库
        fairino_path = self.get_robot_lib_path('fairino')
        if fairino_path:
            dependencies['fairino'] = (self.project_root / fairino_path).exists()
        else:
            dependencies['fairino'] = False
            
        return dependencies
    
    def generate_platform_specific_files(self):
        """生成平台特定的文件"""
        # 生成启动脚本
        self._generate_startup_scripts()
        
        # 生成配置文件
        self._generate_config_files()
    
    def _generate_startup_scripts(self):
        """生成平台特定的启动脚本"""
        platform_config = self.get_platform_config()
        python_exe = platform_config.get('python_executable', 'python')
        venv_path = platform_config.get('paths', {}).get('venv', '')
        
        if self.is_windows:
            # Windows批处理文件
            bat_content = f"""@echo off
echo Starting XC-ROBOT GUI on Windows...
call {venv_path}
{python_exe} start_gui.py
pause
"""
            with open(self.project_root / 'start_xc_robot.bat', 'w', encoding='utf-8') as f:
                f.write(bat_content)
        
        else:
            # Mac/Linux shell脚本
            sh_content = f"""#!/bin/bash
echo "Starting XC-ROBOT GUI on {self.platform.title()}..."
source {venv_path}
{python_exe} start_gui.py
"""
            script_file = self.project_root / 'start_xc_robot.sh'
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            # 设置执行权限
            os.chmod(script_file, 0o755)
    
    def _generate_config_files(self):
        """生成平台配置文件"""
        # 生成GUI配置
        gui_config = self.get_gui_config()
        gui_config_file = self.project_root / 'config' / f'gui_config_{self.platform}.json'
        
        with open(gui_config_file, 'w', encoding='utf-8') as f:
            json.dump(gui_config, indent=2, ensure_ascii=False, fp=f)
        
        # 生成网络配置
        network_config = self.get_platform_config().get('network', {})
        network_config_file = self.project_root / 'config' / f'network_config_{self.platform}.json'
        
        with open(network_config_file, 'w', encoding='utf-8') as f:
            json.dump(network_config, indent=2, ensure_ascii=False, fp=f)

# 全局平台适配器实例
platform_adapter = PlatformAdapter()

def get_platform_adapter() -> PlatformAdapter:
    """获取平台适配器实例"""
    return platform_adapter

def auto_configure():
    """自动配置当前平台"""
    adapter = get_platform_adapter()
    
    print(f"检测到平台: {adapter.platform.title()}")
    print("正在生成平台特定配置...")
    
    # 生成平台文件
    adapter.generate_platform_specific_files()
    
    # 检查依赖
    deps = adapter.check_dependencies()
    print("\n依赖检查结果:")
    for dep, status in deps.items():
        status_str = "✅" if status else "❌"
        print(f"  {dep}: {status_str}")
    
    # 显示配置信息
    config = adapter.get_platform_config()
    print(f"\n平台配置:")
    print(f"  Python: {config.get('python_executable', 'python')}")
    print(f"  GUI框架: {config.get('gui_framework', 'PyQt5')}")
    print(f"  默认字体: {config.get('default_font', 'Arial')}")
    print(f"  窗口缩放: {config.get('window_scaling', 1.0)}")
    
    print(f"\n配置完成! 平台: {adapter.platform.title()}")
    return adapter

if __name__ == "__main__":
    auto_configure()
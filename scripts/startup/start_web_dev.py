#!/usr/bin/env python3
"""
XC-ROBOT Web开发环境启动脚本 (虚拟环境版本)
自动激活虚拟环境并启动Web开发环境
"""

import os
import sys
import subprocess
from pathlib import Path

def activate_venv_and_run():
    """激活虚拟环境并启动Web开发环境"""
    project_root = Path(__file__).parent
    venv_python = project_root / "venv" / "bin" / "python"
    launcher_script = project_root / "apps" / "launchers" / "start_xc_robot.py"
    
    if not venv_python.exists():
        print("❌ 虚拟环境不存在，请先创建虚拟环境")
        print("💡 运行: python3 -m venv venv")
        return 1
    
    if not launcher_script.exists():
        print("❌ 启动脚本不存在")
        return 1
    
    print("🔧 使用虚拟环境启动Web开发环境...")
    print(f"📍 虚拟环境路径: {venv_python}")
    print("=" * 50)
    
    # 使用虚拟环境的Python运行启动脚本
    try:
        return subprocess.call([str(venv_python), str(launcher_script), "web-dev"])
    except KeyboardInterrupt:
        print("\n🛑 用户中断启动")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = activate_venv_and_run()
    sys.exit(exit_code)
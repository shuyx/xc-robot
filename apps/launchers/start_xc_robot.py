#!/usr/bin/env python3
"""
XC-ROBOT 主启动脚本
支持多种启动模式的统一入口
"""

import sys
import argparse
import subprocess
from pathlib import Path

class XCRobotLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.launchers_dir = Path(__file__).parent
    
    def start_api_server(self):
        """启动API服务器"""
        print("🔧 启动API服务器模式...")
        script = self.launchers_dir / "start_api_server.py"
        return subprocess.call([sys.executable, str(script)])
    
    def start_desktop_gui(self):
        """启动桌面GUI"""
        print("🖥️ 启动桌面GUI模式...")
        script = self.launchers_dir / "start_desktop_gui.py"
        return subprocess.call([sys.executable, str(script)])
    
    def start_web_dev(self):
        """启动Web开发环境"""
        print("🌐 启动Web开发模式...")
        script = self.launchers_dir / "start_web_dev.py"
        return subprocess.call([sys.executable, str(script)])
    
    def start_robotsim(self):
        """启动机器人仿真"""
        print("🤖 启动机器人仿真模式...")
        script = self.launchers_dir / "start_robotsim.py"
        return subprocess.call([sys.executable, str(script)])
    
    def quick_start(self):
        """快速启动"""
        print("⚡ 快速启动模式...")
        script = self.launchers_dir / "quick_start.py"
        return subprocess.call([sys.executable, str(script)])

def main():
    parser = argparse.ArgumentParser(
        description='XC-ROBOT 统一启动器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
启动模式说明:
  api       - 仅启动API服务器 (用于生产部署)
  desktop   - 启动桌面GUI应用 (PyQt5界面)
  web-dev   - 启动Web开发环境 (API服务器 + 前端开发服务器)
  sim       - 启动机器人仿真模式
  quick     - 快速启动 (自动选择最佳模式)

示例:
  python start_xc_robot.py api          # 仅启动API服务器
  python start_xc_robot.py desktop      # 启动桌面应用
  python start_xc_robot.py web-dev      # 启动Web开发环境
  python start_xc_robot.py sim          # 启动仿真模式
  python start_xc_robot.py quick        # 快速启动
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['api', 'desktop', 'web-dev', 'sim', 'quick'],
        help='启动模式'
    )
    
    args = parser.parse_args()
    
    launcher = XCRobotLauncher()
    
    print("🚀 XC-ROBOT 统一启动器")
    print("=" * 50)
    
    try:
        if args.mode == 'api':
            return launcher.start_api_server()
        elif args.mode == 'desktop':
            return launcher.start_desktop_gui()
        elif args.mode == 'web-dev':
            return launcher.start_web_dev()
        elif args.mode == 'sim':
            return launcher.start_robotsim()
        elif args.mode == 'quick':
            return launcher.quick_start()
        else:
            print(f"❌ 未知的启动模式: {args.mode}")
            return 1
    except KeyboardInterrupt:
        print("\n🛑 用户中断启动")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
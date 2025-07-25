#!/usr/bin/env python3
"""
XC-ROBOT Web开发环境启动脚本
同时启动API服务器和前端开发服务器
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

class XCRobotWebDevLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.api_process = None
        self.frontend_process = None
        
    def start_api_server(self):
        """启动API服务器"""
        print("🔧 启动API服务器...")
        api_script = self.project_root / "apps" / "launchers" / "start_api_server.py"
        
        try:
            self.api_process = subprocess.Popen(
                [sys.executable, str(api_script)],
                cwd=self.project_root
            )
            print(f"✅ API服务器已启动 (PID: {self.api_process.pid})")
            time.sleep(2)  # 等待API服务器启动
        except Exception as e:
            print(f"❌ API服务器启动失败: {e}")
            return False
        return True
    
    def start_frontend_dev_server(self):
        """启动前端开发服务器"""
        print("🌐 启动前端开发服务器...")
        dev_server_script = self.project_root / "apps" / "web" / "dev_server" / "simple_server.py"
        
        try:
            self.frontend_process = subprocess.Popen(
                [sys.executable, str(dev_server_script), "--port", "3000"],
                cwd=self.project_root
            )
            print(f"✅ 前端开发服务器已启动 (PID: {self.frontend_process.pid})")
        except Exception as e:
            print(f"❌ 前端开发服务器启动失败: {e}")
            return False
        return True
    
    def stop_servers(self):
        """停止所有服务器"""
        print("\n🛑 正在停止服务器...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ API服务器已停止")
            except subprocess.TimeoutExpired:
                self.api_process.kill()
                print("⚠️ API服务器被强制终止")
            except Exception as e:
                print(f"❌ 停止API服务器时出错: {e}")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ 前端开发服务器已停止")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                print("⚠️ 前端开发服务器被强制终止")
            except Exception as e:
                print(f"❌ 停止前端开发服务器时出错: {e}")
    
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        self.stop_servers()
        sys.exit(0)
    
    def run(self):
        """运行开发环境"""
        print("🚀 XC-ROBOT Web开发环境启动器")
        print("=" * 50)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 启动API服务器
        if not self.start_api_server():
            print("❌ 无法启动API服务器，退出")
            return
        
        # 启动前端开发服务器
        if not self.start_frontend_dev_server():
            print("❌ 无法启动前端开发服务器，停止API服务器")
            self.stop_servers()
            return
        
        print("\n🎉 开发环境启动完成！")
        print("📍 访问地址:")
        print("   - 前端测试界面: http://localhost:3000")
        print("   - API文档: http://localhost:8000/docs")
        print("   - API状态: http://localhost:8000/api/v1/system/health")
        print("\n💡 使用说明:")
        print("   - 前端代码修改会自动刷新浏览器")
        print("   - API修改需要重启开发环境")
        print("   - 按 Ctrl+C 停止所有服务")
        print("=" * 50)
        
        try:
            # 等待子进程
            while True:
                if self.api_process and self.api_process.poll() is not None:
                    print("❌ API服务器意外停止")
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ 前端开发服务器意外停止")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_servers()

def main():
    launcher = XCRobotWebDevLauncher()
    launcher.run()

if __name__ == '__main__':
    main()
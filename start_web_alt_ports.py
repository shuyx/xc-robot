#!/usr/bin/env python3
"""
XC-ROBOT Web开发环境启动脚本 - 使用备用端口
API: 8001, Frontend: 3001
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

class XCRobotWebDevLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.api_process = None
        self.frontend_process = None
        self.api_port = 8001
        self.frontend_port = 3001
        
    def start_api_server(self):
        """启动API服务器"""
        print(f"🔧 启动API服务器 (端口: {self.api_port})...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['API_PORT'] = str(self.api_port)
        
        try:
            # 直接启动uvicorn
            self.api_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "api.main:app",
                    "--host", "0.0.0.0",
                    "--port", str(self.api_port),
                    "--reload",
                    "--log-level", "info"
                ],
                cwd=self.project_root,
                env=env
            )
            print(f"✅ API服务器已启动 (PID: {self.api_process.pid})")
            time.sleep(3)  # 等待API服务器启动
        except Exception as e:
            print(f"❌ API服务器启动失败: {e}")
            return False
        return True
    
    def start_frontend_dev_server(self):
        """启动前端开发服务器"""
        print(f"🌐 启动前端开发服务器 (端口: {self.frontend_port})...")
        dev_server_script = self.project_root / "apps" / "web" / "dev_server" / "simple_server.py"
        
        try:
            self.frontend_process = subprocess.Popen(
                [sys.executable, str(dev_server_script), "--port", str(self.frontend_port)],
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
        print("🚀 XC-ROBOT Web开发环境启动器 (备用端口)")
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
        print(f"   - 前端测试界面: http://localhost:{self.frontend_port}")
        print(f"   - API文档: http://localhost:{self.api_port}/docs")
        print(f"   - API状态: http://localhost:{self.api_port}/api/v1/system/health")
        print("\n💡 使用说明:")
        print("   - 前端代码修改会自动刷新浏览器")
        print("   - API修改会自动重启服务")
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
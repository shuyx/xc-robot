#!/bin/bash
# XC-ROBOT Web GUI启动脚本 (macOS)

echo "🚀 XC-ROBOT Web GUI 启动脚本"
echo "========================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行环境配置"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查端口占用
check_port() {
    lsof -i :$1 > /dev/null 2>&1
}

# 找到可用端口
API_PORT=8000
FRONTEND_PORT=3000

if check_port $API_PORT; then
    echo "⚠️  端口 $API_PORT 被占用，使用备用端口 8001"
    API_PORT=8001
fi

if check_port $FRONTEND_PORT; then
    echo "⚠️  端口 $FRONTEND_PORT 被占用，使用备用端口 3001"
    FRONTEND_PORT=3001
fi

echo "📍 使用端口配置:"
echo "   - API服务器: $API_PORT"
echo "   - 前端服务器: $FRONTEND_PORT"
echo "========================================"

# 创建临时启动脚本
cat > /tmp/xc_robot_launcher.py << EOF
#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

class Launcher:
    def __init__(self):
        self.project_root = Path.cwd()
        self.api_process = None
        self.frontend_process = None
        self.api_port = $API_PORT
        self.frontend_port = $FRONTEND_PORT
        
    def start_api_server(self):
        print(f"🔧 启动API服务器 (端口: {self.api_port})...")
        try:
            self.api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "api.main:app",
                "--host", "0.0.0.0",
                "--port", str(self.api_port),
                "--reload"
            ])
            print(f"✅ API服务器已启动")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ API服务器启动失败: {e}")
            return False
    
    def start_frontend_dev_server(self):
        print(f"🌐 启动前端服务器 (端口: {self.frontend_port})...")
        dev_server = self.project_root / "apps/web/dev_server/simple_server.py"
        try:
            self.frontend_process = subprocess.Popen([
                sys.executable, str(dev_server),
                "--port", str(self.frontend_port)
            ])
            print(f"✅ 前端服务器已启动")
            return True
        except Exception as e:
            print(f"❌ 前端服务器启动失败: {e}")
            return False
    
    def stop_servers(self):
        print("\\n🛑 正在停止服务器...")
        for proc, name in [(self.api_process, "API"), (self.frontend_process, "前端")]:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    print(f"✅ {name}服务器已停止")
                except:
                    proc.kill()
    
    def signal_handler(self, signum, frame):
        self.stop_servers()
        sys.exit(0)
    
    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        if not self.start_api_server():
            return
        if not self.start_frontend_dev_server():
            self.stop_servers()
            return
        
        print("\\n🎉 Web GUI启动成功！")
        print("======================================")
        print(f"📍 访问地址:")
        print(f"   前端界面: http://localhost:{self.frontend_port}")
        print(f"   API文档: http://localhost:{self.api_port}/docs")
        print(f"   API状态: http://localhost:{self.api_port}/api/v1/system/health")
        print("\\n💡 按 Ctrl+C 停止所有服务")
        print("======================================\\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_servers()

if __name__ == '__main__':
    Launcher().run()
EOF

# 运行启动器
python /tmp/xc_robot_launcher.py
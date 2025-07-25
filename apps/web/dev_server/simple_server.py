#!/usr/bin/env python3
"""
XC-ROBOT Web前端开发服务器
简单的HTTP服务器，用于开发阶段提供静态文件服务
"""

import os
import sys
import http.server
import socketserver
from pathlib import Path

class XCRobotHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器，支持CORS和SPA路由"""
    
    def end_headers(self):
        # 添加CORS头部，允许跨域请求
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[XC-ROBOT Dev Server] {format % args}")

def start_dev_server(port=3000, directory=None):
    """启动开发服务器"""
    if directory is None:
        # 默认服务器当前脚本所在目录的上级目录（frontend目录）
        current_dir = Path(__file__).parent
        directory = current_dir.parent / "frontend"
    
    # 切换到前端目录
    os.chdir(directory)
    
    print(f"🚀 XC-ROBOT Web前端开发服务器启动中...")
    print(f"📁 服务目录: {directory}")
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"📱 移动端访问: http://0.0.0.0:{port}")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", port), XCRobotHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 开发服务器已停止")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {port} 已被占用，请尝试其他端口")
            print(f"💡 使用命令: python {__file__} --port 3001")
        else:
            print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

def main():
    """主函数，解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='XC-ROBOT Web前端开发服务器')
    parser.add_argument('--port', '-p', type=int, default=3000, 
                       help='服务器端口 (默认: 3000)')
    parser.add_argument('--directory', '-d', type=str, default=None,
                       help='静态文件目录 (默认: ../frontend)')
    
    args = parser.parse_args()
    
    start_dev_server(args.port, args.directory)

if __name__ == '__main__':
    main()
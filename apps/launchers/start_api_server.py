#!/usr/bin/env python3
"""
XC-ROBOT API服务器启动脚本
启动FastAPI后端服务，提供RESTful API和WebSocket接口
"""

import sys
import os
import uvicorn
from pathlib import Path

def setup_paths():
    """设置Python路径"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    api_dir = project_root / "api"
    core_dir = project_root / "core" 
    services_dir = project_root / "services"
    
    # 添加到Python路径
    for path in [project_root, api_dir, core_dir, services_dir]:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    
    return project_root

def check_dependencies():
    """检查依赖包"""
    missing = []
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "websockets",
        "pydantic",
        "multipart"  # python-multipart is imported as 'multipart'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def main():
    """主函数"""
    print("🚀 XC-ROBOT API服务器启动器")
    print("=" * 50)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print(f"💡 请运行: pip install {' '.join(missing)}")
        return 1
    
    # 设置路径
    project_root = setup_paths()
    
    try:
        # 导入FastAPI应用
        from api.main import app
        
        print("✅ FastAPI应用加载成功")
        print("📍 API服务地址:")
        print("   - API基础地址: http://localhost:8000/api/v1")
        print("   - API文档: http://localhost:8000/docs")
        print("   - WebSocket: ws://localhost:8000/ws")
        print("🔧 服务配置:")
        print("   - 主机: 0.0.0.0")
        print("   - 端口: 8000")
        print("   - 重载: 启用")
        print("   - 日志级别: info")
        print("=" * 50)
        
        # 启动服务器
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(project_root)],
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保API模块存在且路径正确")
        return 1
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
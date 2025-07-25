#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT GUI 启动脚本 - macOS优化版
"""

import sys
import os
from pathlib import Path

# 必须在任何Qt导入之前设置
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# 设置Qt WebEngine属性（必须在QApplication创建之前）
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# 设置项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps"))
sys.path.insert(0, str(project_root / "apps" / "desktop"))
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "services"))

def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT Control System")
    app.setApplicationVersion("3.1")
    app.setStyle('Fusion')
    
    try:
        # 导入主窗口
        from apps.desktop.main_window import XCRobotMainWindow
        
        # 创建主窗口
        window = XCRobotMainWindow()
        window.setWindowTitle("XC-ROBOT 双臂机器人控制系统")
        window.resize(1200, 800)
        window.show()
        
        print("✅ XC-ROBOT 桌面GUI启动成功!")
        print("📍 系统版本: v3.1")
        print("🖥️  界面类型: PyQt5 桌面应用")
        
        # 运行应用
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请检查以下内容:")
        print("1. 是否激活了虚拟环境: source venv/bin/activate")
        print("2. 是否安装了依赖: pip install -r requirements.txt")
        print("3. 文件路径是否正确")
        return 1
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
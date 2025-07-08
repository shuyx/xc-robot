#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 上位机软件启动脚本 - 精简版
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'gui'))

def check_dependencies():
    """检查必要的依赖包"""
    missing_packages = []
    
    try:
        import PyQt5
    except ImportError:
        missing_packages.append("PyQt5")
    
    try:
        import yaml
    except ImportError:
        missing_packages.append("PyYAML")
    
    try:
        import requests
    except ImportError:
        missing_packages.append("requests")
    
    return missing_packages

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用样式和字体
    app.setStyle('Fusion')
    # 使用系统默认字体
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        QMessageBox.critical(
            None, "依赖包缺失", 
            f"缺少以下依赖包:\n{', '.join(missing)}\n\n"
            f"请运行: pip install {' '.join(missing)}"
        )
        return 1
    
    try:
        # 导入主窗口
        from gui.main_window import XCRobotMainWindow
        
        # 创建并显示主窗口
        main_window = XCRobotMainWindow()
        main_window.show()
        
        # 运行应用程序
        return app.exec_()
        
    except ImportError as e:
        QMessageBox.critical(
            None, "导入错误", 
            f"无法导入GUI模块:\n{str(e)}"
        )
        return 1
    except Exception as e:
        QMessageBox.critical(
            None, "启动错误", 
            f"启动过程中发生错误:\n{str(e)}"
        )
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
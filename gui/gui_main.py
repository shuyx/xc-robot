#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 上位机软件启动脚本
gui_main.py
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'gui'))

def check_dependencies():
    """检查依赖包"""
    missing_packages = []
    
    try:
        import PyQt5
    except ImportError:
        missing_packages.append("PyQt5")
    
    try:
        import yaml
    except ImportError:
        missing_packages.append("PyYAML")
    
    return missing_packages

def create_splash_screen():
    """创建启动画面"""
    # 创建简单的启动画面
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(Qt.white)
    
    splash = QSplashScreen(splash_pixmap)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
    
    # 显示文字
    splash.showMessage("XC-ROBOT 上位机控制软件\n正在启动...", 
                      Qt.AlignCenter | Qt.AlignBottom, Qt.black)
    
    return splash

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("XC-Robotics")
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        QMessageBox.critical(
            None, "依赖包缺失", 
            f"缺少以下依赖包:\n{', '.join(missing)}\n\n"
            f"请运行以下命令安装:\n"
            f"pip install {' '.join(missing)}"
        )
        return 1
    
    # 显示启动画面
    splash = create_splash_screen()
    splash.show()
    
    # 处理事件，确保启动画面显示
    app.processEvents()
    
    try:
        # 导入主窗口（延迟导入以显示启动画面）
        splash.showMessage("正在加载主界面...", Qt.AlignCenter | Qt.AlignBottom, Qt.black)
        app.processEvents()
        
        from gui.main_window import XCRobotMainWindow
        
        # 创建主窗口
        splash.showMessage("正在初始化系统...", Qt.AlignCenter | Qt.AlignBottom, Qt.black)
        app.processEvents()
        
        main_window = XCRobotMainWindow()
        
        # 设置定时器关闭启动画面
        def close_splash():
            splash.close()
            main_window.show()
            main_window.log_message("XC-ROBOT 上位机软件启动成功", "SUCCESS")
        
        QTimer.singleShot(2000, close_splash)  # 2秒后关闭启动画面
        
        # 运行应用程序
        return app.exec_()
        
    except ImportError as e:
        splash.close()
        QMessageBox.critical(
            None, "导入错误", 
            f"无法导入GUI模块:\n{str(e)}\n\n"
            f"请确保GUI模块已正确安装"
        )
        return 1
    except Exception as e:
        splash.close()
        QMessageBox.critical(
            None, "启动错误", 
            f"启动过程中发生错误:\n{str(e)}"
        )
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
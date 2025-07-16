#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Web GUI 启动脚本
使用Qt+HTML混合界面
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont

def check_dependencies():
    """检查依赖包"""
    missing = []
    
    try:
        import PyQt5
    except ImportError:
        missing.append("PyQt5")
    
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        missing.append("PyQtWebEngine")
    
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    return missing

def setup_paths():
    """设置Python路径"""
    # 获取脚本所在目录（项目根目录）
    project_root = os.path.dirname(os.path.abspath(__file__))
    gui_dir = os.path.join(project_root, 'gui')
    widgets_dir = os.path.join(gui_dir, 'widgets')
    
    # 添加到Python路径
    for path in [project_root, gui_dir, widgets_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return gui_dir

def main():
    """主函数"""
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        if "PyQtWebEngine" in missing:
            print("注意: PyQtWebEngine 可能需要单独安装: pip install PyQtWebEngine")
        return 1
    
    # 设置路径
    gui_dir = setup_paths()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT Web")
    app.setApplicationVersion("2.0")
    app.setStyle('Fusion')
    
    # 使用系统默认字体，避免字体警告
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    try:
        # 使用延迟导入
        sys.path.insert(0, gui_dir)
        from gui import get_web_main_window
        
        # 创建并显示主窗口
        XCRobotWebMainWindow = get_web_main_window()
        window = XCRobotWebMainWindow()
        window.show()
        
        print("XC-ROBOT Web GUI 启动成功")
        print("界面风格: 现代化HTML5界面")
        print("后端: Python + PyQt5")
        print("前端: HTML5 + CSS3 + JavaScript")
        
        return app.exec_()
        
    except ImportError as e:
        error_msg = f"导入错误: {str(e)}\n\n请检查gui目录是否存在及文件是否完整"
        print(error_msg)
        QMessageBox.critical(None, "导入错误", error_msg)
        return 1
        
    except Exception as e:
        error_msg = f"启动错误: {str(e)}"
        print(error_msg)
        QMessageBox.critical(None, "启动错误", error_msg)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 独立启动脚本
放在项目根目录，解决导入问题
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
        return 1
    
    # 设置路径
    gui_dir = setup_paths()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT")
    app.setApplicationVersion("1.0.0")
    app.setStyle('Fusion')
    # 设置跨平台字体，Windows用微软雅黑，Mac用系统默认
    font = QFont()
    font.setFamily("Microsoft YaHei, PingFang SC, Helvetica, Arial")
    font.setPointSize(9)
    app.setFont(font)
    
    try:
        # 导入主窗口
        sys.path.insert(0, gui_dir)
        from main_window import XCRobotMainWindow
        
        # 创建并显示主窗口
        window = XCRobotMainWindow()
        window.show()
        
        print("XC-ROBOT GUI 启动成功")
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
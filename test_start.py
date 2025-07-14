#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试启动脚本 - 模拟start_gui.py的行为
"""

import sys
import os

# 完全模拟start_gui.py的行为
print("模拟start_gui.py启动过程...")

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont

def check_dependencies():
    """检查依赖包"""
    missing = []
    
    try:
        import PyQt5
        print("✓ PyQt5检查通过")
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import yaml
        print("✓ yaml检查通过")
    except ImportError:
        missing.append("PyYAML")
    
    try:
        import requests
        print("✓ requests检查通过")
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
    
    print(f"✓ 路径设置完成: {gui_dir}")
    return gui_dir

def main():
    """主函数"""
    print("1. 检查依赖...")
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        return 1
    
    print("2. 设置路径...")
    gui_dir = setup_paths()
    
    print("3. 创建QApplication...")
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT")
    app.setApplicationVersion("1.0.0")
    app.setStyle('Fusion')
    
    print("4. 设置字体...")
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    try:
        print("5. 延迟导入GUI...")
        sys.path.insert(0, gui_dir)
        from gui import get_main_window
        
        print("6. 创建主窗口...")
        XCRobotMainWindow = get_main_window()
        window = XCRobotMainWindow()
        
        print("7. 显示窗口...")
        window.show()
        
        print("✓ XC-ROBOT GUI 启动成功")
        
        # 5秒后自动退出用于测试
        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(5000)
        
        return app.exec_()
        
    except ImportError as e:
        error_msg = f"导入错误: {str(e)}"
        print(f"✗ {error_msg}")
        return 1
        
    except Exception as e:
        error_msg = f"启动错误: {str(e)}"
        print(f"✗ {error_msg}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"退出码: {exit_code}")
    sys.exit(exit_code)
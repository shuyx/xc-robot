#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 跨平台启动脚本
自动适配 Mac/Windows/Linux 平台差异
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont

# 导入平台适配器
try:
    from platform_config import get_platform_adapter
    platform_adapter = get_platform_adapter()
except ImportError:
    print("警告: 平台适配器不可用，使用默认配置")
    platform_adapter = None

def check_dependencies():
    """检查依赖包（平台适配版本）"""
    if platform_adapter:
        # 使用平台适配器检查依赖
        return platform_adapter.check_dependencies()
    else:
        # 回退到基础检查
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
        
        return {pkg: False for pkg in missing} if missing else {}

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
    """主函数（平台适配版本）"""
    # 平台信息
    if platform_adapter:
        print(f"检测到平台: {platform_adapter.platform.title()}")
    
    # 检查依赖
    deps = check_dependencies()
    if isinstance(deps, dict):
        failed_deps = [dep for dep, status in deps.items() if not status]
        if failed_deps:
            print(f"缺少依赖: {', '.join(failed_deps)}")
            if platform_adapter:
                python_exe = platform_adapter.get_platform_config().get('python_executable', 'python')
                print(f"请运行: {python_exe} -m pip install {' '.join(failed_deps)}")
            else:
                print(f"请运行: pip install {' '.join(failed_deps)}")
            return 1
    
    # 设置路径
    gui_dir = setup_paths()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("祥承 XC-ROBOT MVP1.0 Control SYSTEM")
    app.setApplicationVersion("2.6.3")
    app.setStyle('Fusion')
    
    # 平台适配的字体设置
    if platform_adapter:
        gui_config = platform_adapter.get_gui_config()
        font = QFont(gui_config.get('font', 'Arial'))
        font.setPointSize(9)
        # 应用窗口缩放
        scaling = gui_config.get('scaling', 1.0)
        if scaling != 1.0:
            font.setPointSize(int(9 * scaling))
    else:
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
        
        print("祥承 XC-ROBOT MVP1.0 Control SYSTEM 启动成功")
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
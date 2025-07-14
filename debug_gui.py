#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI启动调试脚本 - 逐步检查每个组件
"""

import sys
import os
import traceback

print("1. 开始调试GUI启动...")

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'gui'))

print("2. 尝试导入PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import Qt
    print("   ✓ PyQt5导入成功")
except Exception as e:
    print(f"   ✗ PyQt5导入失败: {e}")
    sys.exit(1)

print("3. 创建QApplication...")
try:
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT-DEBUG")
    print("   ✓ QApplication创建成功")
except Exception as e:
    print(f"   ✗ QApplication创建失败: {e}")
    sys.exit(1)

print("4. 尝试导入VTK...")
try:
    import vtk
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    print(f"   ✓ VTK导入成功，版本: {vtk.VTK_VERSION}")
except Exception as e:
    print(f"   ✗ VTK导入失败: {e}")
    vtk = None

print("5. 尝试导入GUI组件...")
try:
    from gui import get_main_window
    print("   ✓ GUI模块导入成功")
except Exception as e:
    print(f"   ✗ GUI模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print("6. 尝试创建主窗口类...")
try:
    XCRobotMainWindow = get_main_window()
    print("   ✓ 主窗口类获取成功")
except Exception as e:
    print(f"   ✗ 主窗口类获取失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print("7. 尝试实例化主窗口...")
try:
    window = XCRobotMainWindow()
    print("   ✓ 主窗口实例化成功")
except Exception as e:
    print(f"   ✗ 主窗口实例化失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print("8. 尝试显示主窗口...")
try:
    window.show()
    print("   ✓ 主窗口显示成功")
    print("\n🎉 GUI启动成功！3秒后自动退出...")
    
    # 3秒后自动退出
    from PyQt5.QtCore import QTimer
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(3000)
    
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"   ✗ 主窗口显示失败: {e}")
    traceback.print_exc()
    sys.exit(1)
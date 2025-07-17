#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试帮助菜单功能
"""

import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from gui.web_main_window import WebBridge

def test_help_menu():
    """测试帮助菜单功能"""
    
    print("=== 测试帮助菜单功能 ===")
    
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle("帮助菜单测试")
    window.resize(1000, 700)
    
    # 创建布局
    layout = QVBoxLayout()
    
    # 创建Web视图
    web_view = QWebEngineView()
    layout.addWidget(web_view)
    
    # 创建WebBridge实例
    bridge = WebBridge()
    
    # 设置Web通道
    channel = QWebChannel()
    channel.registerObject("bridge", bridge)
    web_view.page().setWebChannel(channel)
    
    # 加载HTML文件
    html_file = os.path.join(os.path.dirname(__file__), "UI", "xc_os_newui.html")
    if os.path.exists(html_file):
        web_view.load(QUrl.fromLocalFile(html_file))
        print(f"✓ 加载HTML文件: {html_file}")
    else:
        print(f"✗ HTML文件不存在: {html_file}")
        return
    
    # 设置窗口布局
    window.setLayout(layout)
    
    # 显示窗口
    window.show()
    
    print("✓ 帮助菜单测试界面已启动")
    print("请在界面中测试帮助菜单功能")
    print("点击帮助菜单项查看是否正常显示文档内容")
    
    # 运行应用程序
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n用户中断测试")

if __name__ == "__main__":
    test_help_menu()
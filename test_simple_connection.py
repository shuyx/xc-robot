#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化版连接测试控件
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.widgets.connection_widget import ConnectionWidget

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简化版连接测试控件")
        self.setGeometry(100, 100, 700, 500)
        
        # 创建中心控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建连接测试控件
        self.connection_widget = ConnectionWidget()
        
        # 连接日志信号
        self.connection_widget.log_message.connect(self.print_log)
        
        layout.addWidget(self.connection_widget)
        
        # 延迟显示信息
        QTimer.singleShot(1000, self.show_info)
    
    def print_log(self, message, level):
        """打印日志信息"""
        print(f"[{level}] {message}")
    
    def show_info(self):
        """显示功能说明"""
        print("\n=== 简化版连接测试控件 ===")
        print("功能说明：")
        print("1. 点击'连接状态'标签 - 仅查看界面，不执行连接")
        print("2. 点击'启动连接'按钮 - 触发实际的设备连接")
        print("3. 连接成功后，按钮变为'断开连接'")
        print("4. 支持批量连接和断开操作")
        print("5. 连接日志显示在底部面板")
        print("\n支持的设备：")
        
        for name, key, device_type, ip_widget in self.connection_widget.devices:
            print(f"- {name} ({device_type}): {ip_widget.text()}")
        
        print("\n这样的设计确保：")
        print("- 界面查看不会触发连接")
        print("- 只有点击启动按钮才会连接设备")
        print("- 连接状态清晰可见")
        print("- 操作简单直观")

def main():
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = TestMainWindow()
    window.show()
    
    print("连接测试控件已启动，按照您的需求进行了简化：")
    print("- 移除了复杂的设备监听功能")
    print("- 点击连接状态只是查看界面")
    print("- 点击启动按钮才会触发连接")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
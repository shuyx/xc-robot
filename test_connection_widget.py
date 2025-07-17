#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的连接测试控件
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
        self.setWindowTitle("连接测试控件 - 增强版")
        self.setGeometry(100, 100, 800, 600)
        
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
        
        # 延迟显示设备信息
        QTimer.singleShot(1000, self.show_device_info)
    
    def print_log(self, message, level):
        """打印日志信息"""
        print(f"[{level}] {message}")
    
    def show_device_info(self):
        """显示设备信息"""
        print("\n=== 设备控制面板信息 ===")
        print(f"支持的设备类型: {len(self.connection_widget.devices)}")
        
        for name, key, device_type, ip_widget in self.connection_widget.devices:
            print(f"- {name} ({key}): {device_type} - IP: {ip_widget.text()}")
        
        print(f"\n设备状态: {self.connection_widget.device_states}")
        print("\n=== 使用说明 ===")
        print("1. 点击各设备的'启动'按钮来启动设备监听")
        print("2. 设备启动后，'测试'按钮会被启用")
        print("3. 点击'测试'按钮来测试设备连接")
        print("4. 查看右侧信息面板了解设备状态")
        print("5. 点击'停止全部'来停止所有设备")

def main():
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = TestMainWindow()
    window.show()
    
    print("=== 连接测试控件启动成功 ===")
    print("已加载设备控制面板，包含以下功能：")
    print("- 启动/停止设备监听")
    print("- 连接测试")
    print("- 设备状态监控")
    print("- 批量操作")
    print("- 配置文件管理")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
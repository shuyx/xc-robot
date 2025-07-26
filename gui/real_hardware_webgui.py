#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Hardware Web GUI Application
基于真实硬件控制的Web GUI应用程序
整合FR3、Hermes、视觉、夹爪的完整控制系统
"""

import sys
import os
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, pyqtSlot

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.real_hardware_bridge import RealHardwareControlBridge

class RealHardwareWebGUI(QMainWindow):
    """真实硬件Web GUI主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("XC-Robot 真实硬件控制系统")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 创建硬件控制桥接器
        self.hardware_bridge = RealHardwareControlBridge()
        
        # 设置UI
        self._setup_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 加载Web页面
        self._load_web_page()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建Web视图
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # 设置Web通道
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("hardwareBridge", self.hardware_bridge)
        self.web_view.page().setWebChannel(self.web_channel)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 硬件桥接器信号
        self.hardware_bridge.log_message.connect(self._on_log_message)
        self.hardware_bridge.connection_status_changed.connect(self._on_connection_status_changed)
        self.hardware_bridge.test_progress_updated.connect(self._on_test_progress_updated)
        self.hardware_bridge.emergency_stop_triggered.connect(self._on_emergency_stop)
    
    def _load_web_page(self):
        """加载Web页面"""
        # Web页面路径
        html_file = project_root / "gui" / "real_hardware_interface.html"
        
        if html_file.exists():
            self.web_view.load(QUrl.fromLocalFile(str(html_file)))
        else:
            # 如果专用页面不存在，使用集成系统页面
            fallback_file = project_root / "gui" / "integrated_webgui_system.html"
            if fallback_file.exists():
                self.web_view.load(QUrl.fromLocalFile(str(fallback_file)))
            else:
                print("⚠️ 找不到Web界面文件")
    
    def _on_log_message(self, level: str, message: str):
        """处理日志消息"""
        print(f"[{level}] {message}")
    
    def _on_connection_status_changed(self, device_type: str, device_id: str, status: dict):
        """处理连接状态变化"""
        connected = status.get('connected', False)
        status_text = "已连接" if connected else "已断开"
        print(f"设备状态变化: {device_type}/{device_id} - {status_text}")
    
    def _on_test_progress_updated(self, test_id: str, progress_data: dict):
        """处理测试进度更新"""
        print(f"测试进度更新: {test_id} - {progress_data}")
    
    def _on_emergency_stop(self, reason: str):
        """处理紧急停止"""
        print(f"🚨 紧急停止触发: {reason}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 执行紧急停止
        self.hardware_bridge.emergency_stop_all("应用程序关闭")
        event.accept()


def main():
    """主函数"""
    # 创建QApplication
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = RealHardwareWebGUI()
    window.show()
    
    # 启动应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
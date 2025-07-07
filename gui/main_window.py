#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 主窗口 - 最终修复版
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
widgets_dir = os.path.join(current_dir, 'widgets')
sys.path.insert(0, widgets_dir)

# 导入控件 (删除config_widget导入)
from connection_widget import ConnectionWidget
from log_widget import LogWidget
from arm_control_widget import ArmControlWidget
from chassis_widget import ChassisWidget
from simulation_widget import SimulationWidget

class XCRobotMainWindow(QMainWindow):
    """XC-ROBOT 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XC-ROBOT 控制系统 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        self.setup_menu()
        self.setup_connections()
        
    def setup_ui(self):
        """设置主界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # 左侧控制面板
        self.tab_widget = QTabWidget()
        
        # 创建控制页面 (删除config_widget)
        self.connection_widget = ConnectionWidget()
        self.arm_control_widget = ArmControlWidget()
        self.chassis_widget = ChassisWidget()
        self.simulation_widget = SimulationWidget()
        
        # 添加选项卡 (只保留4个)
        self.tab_widget.addTab(self.connection_widget, "🔗 连接测试")
        self.tab_widget.addTab(self.arm_control_widget, "🤖 机械臂控制")
        self.tab_widget.addTab(self.chassis_widget, "🚛 底盘控制")
        self.tab_widget.addTab(self.simulation_widget, "🎮 仿真系统")
        
        # 右侧日志面板
        self.log_widget = LogWidget()
        
        # 布局
        layout.addWidget(self.tab_widget, 2)
        layout.addWidget(self.log_widget, 1)
        
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        save_log_action = QAction('保存日志', self)
        save_log_action.triggered.connect(self.save_log)
        file_menu.addAction(save_log_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        emergency_stop_action = QAction('紧急停止 (Ctrl+E)', self)
        emergency_stop_action.triggered.connect(self.emergency_stop)
        emergency_stop_action.setShortcut('Ctrl+E')
        tools_menu.addAction(emergency_stop_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """设置信号连接"""
        # 连接日志信号
        self.connection_widget.log_message.connect(self.log_widget.add_message)
        self.arm_control_widget.log_message.connect(self.log_widget.add_message)
        self.chassis_widget.log_message.connect(self.log_widget.add_message)
        self.simulation_widget.log_message.connect(self.log_widget.add_message)
        
        # 启动消息
        QTimer.singleShot(100, lambda: self.log_widget.add_message("XC-ROBOT 系统启动完成", "SUCCESS"))
    
    def save_log(self):
        """保存日志"""
        self.log_widget.save_logs()
    
    def emergency_stop(self):
        """紧急停止"""
        reply = QMessageBox.question(
            self, "紧急停止", "确定要执行紧急停止吗？\n这将停止所有机械臂和底盘运动！",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.log_widget.add_message("执行全系统紧急停止", "WARNING")
            # 通知各控件执行紧急停止
            try:
                if hasattr(self.arm_control_widget, 'emergency_stop'):
                    self.arm_control_widget.emergency_stop()
                if hasattr(self.chassis_widget, 'emergency_stop'):
                    self.chassis_widget.emergency_stop()
            except Exception as e:
                self.log_widget.add_message(f"紧急停止执行异常: {e}", "ERROR")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于 XC-ROBOT",
            "XC-ROBOT 轮式双臂类人形机器人控制系统\n"
            "版本: 1.0\n"
            "硬件: 思岚Hermes底盘 + 法奥意威FR3双臂\n"
            "软件: Python + PyQt5 + FR3控制库"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, "退出确认", "确定要退出XC-ROBOT控制软件吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.log_widget.add_message("系统正在关闭...", "INFO")
            event.accept()
        else:
            event.ignore()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT")
    app.setStyle('Fusion')
    app.setFont(QFont("Microsoft YaHei", 9))
    
    window = XCRobotMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
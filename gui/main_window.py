#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 上位机主窗口
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gui.widgets.connection_widget import ConnectionWidget
from gui.widgets.log_widget import LogWidget
from gui.widgets.arm_control_widget import ArmControlWidget
from gui.widgets.chassis_widget import ChassisWidget
from gui.widgets.config_widget import ConfigWidget

class XCRobotMainWindow(QMainWindow):
    """XC-ROBOT 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XC-ROBOT 上位机控制软件 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
    def setup_ui(self):
        """设置主界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧控制面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # 右侧日志和状态面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
    def create_left_panel(self):
        """创建左侧控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标签页控件
        tab_widget = QTabWidget()
        
        # 连接测试页面
        self.connection_widget = ConnectionWidget()
        tab_widget.addTab(self.connection_widget, "🔗 连接测试")
        
        # 单臂控制页面
        self.arm_control_widget = ArmControlWidget()
        tab_widget.addTab(self.arm_control_widget, "🤖 机械臂控制")
        
        # 底盘控制页面
        self.chassis_widget = ChassisWidget()
        tab_widget.addTab(self.chassis_widget, "🚛 底盘控制")
        
        # 配置管理页面
        self.config_widget = ConfigWidget()
        tab_widget.addTab(self.config_widget, "⚙️ 配置管理")
        
        layout.addWidget(tab_widget)
        return panel
        
    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 系统状态组
        status_group = QGroupBox("系统状态")
        status_layout = QGridLayout(status_group)
        
        # 状态指示灯
        self.status_labels = {}
        status_items = [
            ("右臂连接", "right_arm"),
            ("左臂连接", "left_arm"),
            ("底盘连接", "chassis"),
            ("系统就绪", "system")
        ]
        
        for i, (name, key) in enumerate(status_items):
            label = QLabel(name)
            status = QLabel("●")
            status.setStyleSheet("color: red; font-size: 16px;")
            self.status_labels[key] = status
            
            status_layout.addWidget(label, i, 0)
            status_layout.addWidget(status, i, 1)
        
        layout.addWidget(status_group)
        
        # 日志显示
        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget)
        
        return panel
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 保存日志
        save_log_action = QAction('保存日志', self)
        save_log_action.triggered.connect(self.save_log)
        file_menu.addAction(save_log_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        # 系统检查
        system_check_action = QAction('系统检查', self)
        system_check_action.triggered.connect(self.run_system_check)
        tools_menu.addAction(system_check_action)
        
        # 紧急停止
        emergency_stop_action = QAction('紧急停止', self)
        emergency_stop_action.triggered.connect(self.emergency_stop)
        emergency_stop_action.setShortcut('Ctrl+E')
        tools_menu.addAction(emergency_stop_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("系统已启动，等待连接...")
        
        # 添加时间显示
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        # 定时器更新时间
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def update_status(self, component: str, connected: bool):
        """更新连接状态"""
        if component in self.status_labels:
            color = "green" if connected else "red"
            self.status_labels[component].setStyleSheet(f"color: {color}; font-size: 16px;")
    
    def log_message(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        self.log_widget.add_message(message, level)
    
    def save_log(self):
        """保存日志"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存日志", f"xc_robot_log_{int(time.time())}.txt", "文本文件 (*.txt)"
        )
        if filename:
            self.log_widget.save_to_file(filename)
    
    def run_system_check(self):
        """运行系统检查"""
        self.log_message("开始系统检查...", "INFO")
        # 这里调用现有的quick_start.py功能
        pass
    
    def emergency_stop(self):
        """紧急停止"""
        reply = QMessageBox.question(
            self, "紧急停止", "确定要执行紧急停止吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.log_message("执行紧急停止", "WARNING")
            # 调用紧急停止功能
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于 XC-ROBOT",
            "XC-ROBOT 轮式双臂类人形机器人控制系统\n"
            "版本: 1.0\n"
            "基于思岚Hermes底盘和法奥意威FR3机械臂"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, "退出确认", "确定要退出XC-ROBOT控制软件吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 断开所有连接
            self.log_message("正在关闭系统...", "INFO")
            event.accept()
        else:
            event.ignore()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT")
    app.setOrganizationName("XC-Robotics")
    
    # 设置应用图标和样式
    app.setStyle('Fusion')  # 使用Fusion样式
    
    window = XCRobotMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
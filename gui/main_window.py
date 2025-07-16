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

# 延迟导入控件，防止VTK在QApplication初始化前被导入

class XCRobotMainWindow(QMainWindow):
    """XC-ROBOT 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("祥承 XC-ROBOT MVP1.0 Control SYSTEM")
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
        
        # 延迟导入和创建控制页面
        self.create_widgets()
        
        # 右侧日志面板
        from log_widget import LogWidget
        self.log_widget = LogWidget()
        
        # 布局 - 调整比例，缩小右侧日志框宽度
        layout.addWidget(self.tab_widget, 3)  # 左侧主控制区域占更多空间
        layout.addWidget(self.log_widget, 1)  # 右侧日志区域占较少空间
    
    def create_widgets(self):
        """创建所有控件，包括RobotSim"""
        try:
            # 导入基本控件
            from connection_widget import ConnectionWidget
            from arm_control_widget import ArmControlWidget
            from chassis_widget import ChassisWidget
            from simulation_widget import SimulationWidget
            
            # 创建基本控件
            self.connection_widget = ConnectionWidget()
            self.arm_control_widget = ArmControlWidget()
            self.chassis_widget = ChassisWidget()
            self.simulation_widget = SimulationWidget()
            
            # 添加基本控件选项卡
            self.tab_widget.addTab(self.connection_widget, "🔗 连接测试")
            self.tab_widget.addTab(self.arm_control_widget, "🤖 机械臂控制")
            self.tab_widget.addTab(self.chassis_widget, "🚛 底盘控制")
            self.tab_widget.addTab(self.simulation_widget, "🎮 仿真系统")
            
            # 同步创建 RobotSim 控件
            self.create_robot_sim_widget()
            
        except Exception as e:
            print(f"创建控件失败: {e}")
            # 如果失败，创建占位符
            placeholder = QLabel("控件加载失败")
            self.tab_widget.addTab(placeholder, "❌ 错误")
    
    def create_robot_sim_widget(self):
        """延迟创建 RobotSim 控件"""
        try:
            # 在QApplication已经创建后导入VTK相关组件
            from robot_sim_widget import RobotSimWidget
            
            # 创建RobotSim控件
            self.robot_sim_widget = RobotSimWidget()
            
            # 添加到选项卡
            self.tab_widget.addTab(self.robot_sim_widget, "🤖 RobotSim")
            
            print("RobotSim 控件创建成功")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"RobotSim 控件创建失败: {e}")
            print(f"详细错误信息:\n{error_details}")
            # 创建占位符
            placeholder = QLabel(f"RobotSim 不可用: {str(e)}")
            placeholder.setWordWrap(True)
            self.tab_widget.addTab(placeholder, "⚠️ RobotSim")
    
    def connect_basic_signals(self):
        """连接基本控件信号"""
        try:
            # 连接日志信号
            if hasattr(self, 'connection_widget'):
                self.connection_widget.log_message.connect(self.log_widget.add_message)
            if hasattr(self, 'arm_control_widget'):
                self.arm_control_widget.log_message.connect(self.log_widget.add_message)
            if hasattr(self, 'chassis_widget'):
                self.chassis_widget.log_message.connect(self.log_widget.add_message)
            if hasattr(self, 'simulation_widget'):
                self.simulation_widget.log_message.connect(self.log_widget.add_message)
            
            print("基本控件信号连接成功")
        except Exception as e:
            print(f"基本控件信号连接失败: {e}")
    
    def connect_robot_sim_signals(self):
        """连接 RobotSim 信号"""
        try:
            if hasattr(self, 'robot_sim_widget'):
                self.robot_sim_widget.log_message.connect(self.log_widget.add_message)
                print("RobotSim 信号连接成功")
        except Exception as e:
            print(f"RobotSim 信号连接失败: {e}")
        
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
        # 同步连接所有信号
        self.connect_basic_signals()
        self.connect_robot_sim_signals()
        
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
                if hasattr(self, 'arm_control_widget') and hasattr(self.arm_control_widget, 'emergency_stop'):
                    self.arm_control_widget.emergency_stop()
                if hasattr(self, 'chassis_widget') and hasattr(self.chassis_widget, 'emergency_stop'):
                    self.chassis_widget.emergency_stop()
                if hasattr(self, 'robot_sim_widget') and hasattr(self.robot_sim_widget, 'emergency_stop'):
                    self.robot_sim_widget.emergency_stop()
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
            
            # 清理各个组件的资源
            try:
                if hasattr(self, 'robot_sim_widget') and hasattr(self.robot_sim_widget, 'cleanup'):
                    self.robot_sim_widget.cleanup()
                    
            except Exception as e:
                print(f"关闭时清理资源出错: {e}")
            finally:
                event.accept()
        else:
            event.ignore()

def main():
    """主函数"""
    import signal
    
    app = QApplication(sys.argv)
    app.setApplicationName("XC-ROBOT")
    app.setStyle('Fusion')
    # 使用系统默认字体
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    window = XCRobotMainWindow()
    
    # 处理Ctrl+C信号
    def signal_handler(signum, frame):
        print("\n收到退出信号，正在关闭应用...")
        try:
            # 清理RobotSim资源
            if hasattr(window, 'robot_sim_widget') and hasattr(window.robot_sim_widget, 'cleanup'):
                window.robot_sim_widget.cleanup()
        except Exception as e:
            print(f"清理资源时出错: {e}")
        finally:
            app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 让Python能够处理信号
    import threading
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)
    
    window.show()
    
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n键盘中断，正在退出...")
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
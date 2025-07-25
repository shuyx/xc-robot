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
        self.setup_help_menu(help_menu)

        help_menu.addSeparator()

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_help_menu(self, help_menu):
        """动态创建帮助文档菜单"""
        # 导入帮助查看器窗口
        from help_viewer import HelpViewerWindow
        self.help_viewer = None

        # 获取Md_files目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        md_files_dir = os.path.join(project_root, 'Md_files')

        if not os.path.isdir(md_files_dir):
            no_docs_action = QAction("文档目录未找到", self)
            no_docs_action.setEnabled(False)
            help_menu.addAction(no_docs_action)
            return

        # 遍历目录并创建菜单项
        try:
            for item in sorted(os.listdir(md_files_dir)):
                if item.endswith('.html'):
                    # 从文件名创建菜单项文本 (e.g., "README.html" -> "README")
                    action_text = os.path.splitext(item)[0]
                    action = QAction(action_text, self)
                    
                    # 构建HTML文件的绝对路径
                    html_file_path = os.path.join(md_files_dir, item)
                    
                    # 使用lambda函数传递文件路径参数
                    action.triggered.connect(
                        lambda checked, path=html_file_path: self.show_help_document(path)
                    )
                    help_menu.addAction(action)
        except Exception as e:
            error_action = QAction(f"无法加载文档: {e}", self)
            error_action.setEnabled(False)
            help_menu.addAction(error_action)

    def show_help_document(self, file_path):
        """显示帮助文档"""
        try:
            # 如果帮助窗口不存在，则创建它
            if self.help_viewer is None:
                from help_viewer import HelpViewerWindow
                self.help_viewer = HelpViewerWindow(self)

            # 加载并显示HTML文件
            self.help_viewer.load_html_file(file_path)
            self.log_widget.add_message(f"正在显示帮助文档: {os.path.basename(file_path)}", "INFO")

        except ImportError:
            self.log_widget.add_message("无法导入HelpViewerWindow，请检查文件是否存在。", "ERROR")
        except Exception as e:
            self.log_widget.add_message(f"无法显示帮助文档: {e}", "ERROR")
            
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
        reply = self.show_custom_question("紧急停止", "确定要执行紧急停止吗？\n这将停止所有机械臂和底盘运动！")
        if reply:
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
        self.show_custom_about_dialog()
    
    def show_custom_about_dialog(self):
        """显示自定义关于对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("关于 XC-ROBOT")
        dialog.setFixedSize(480, 320)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                border-radius: 12px;
            }
            QLabel {
                color: #2c3e50;
                background: transparent;
            }
            QPushButton {
                background: #2ECC71;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #27AE60;
            }
            QPushButton:pressed {
                background: #229954;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # 标题和Logo区域
        header_layout = QHBoxLayout()
        
        # Logo (使用祥承电子实际logo)
        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), '..', 'UI', 'xc logo.jpg'))
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # 如果logo文件不存在，使用文字作为备用
            logo_label.setText("祥")
            logo_label.setStyleSheet("""
                QLabel {
                    background: #2ECC71;
                    border-radius: 24px;
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c3e50;
                }
            """)
            logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(48, 48)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("XC-ROBOT 控制系统")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 2px;
        """)
        
        company_label = QLabel("祥承机器人技术")
        company_label.setStyleSheet("""
            font-size: 12px;
            color: #2ECC71;
            font-weight: 600;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(company_label)
        
        header_layout.addWidget(logo_label)
        header_layout.addSpacing(15)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #dee2e6;")
        layout.addWidget(line)
        
        # 产品信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        version_label = QLabel("版本: 1.0 (传统Qt界面版)")
        version_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")
        
        hardware_label = QLabel("硬件配置:")
        hardware_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #6c757d; margin-top: 8px;")
        
        hardware_details = QLabel("• 思岚Hermes移动底盘\n• 法奥意威FR3双臂机械臂\n• ToF深度相机 × 3\n• 高性能控制计算机")
        hardware_details.setStyleSheet("font-size: 12px; color: #6c757d; margin-left: 10px;")
        
        software_label = QLabel("软件架构:")
        software_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #6c757d; margin-top: 8px;")
        
        software_details = QLabel("• Python + PyQt5 + VTK\n• 传统Qt控件界面\n• 实时控制 + 3D可视化")
        software_details.setStyleSheet("font-size: 12px; color: #6c757d; margin-left: 10px;")
        
        info_layout.addWidget(version_label)
        info_layout.addWidget(hardware_label)
        info_layout.addWidget(hardware_details)
        info_layout.addWidget(software_label)
        info_layout.addWidget(software_details)
        
        layout.addLayout(info_layout)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setFixedSize(80, 32)
        
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def show_custom_question(self, title, message):
        """显示自定义询问对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                background: transparent;
            }
            QPushButton#confirm {
                background: #2ECC71;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#confirm:hover {
                background: #27AE60;
            }
            QPushButton#cancel {
                background: #2c3e50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#cancel:hover {
                background: #34495e;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # 顶部标题区域
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), '..', 'UI', 'xc logo.jpg'))
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            # 如果logo文件不存在，使用文字作为备用
            logo_label.setText("祥")
            logo_label.setStyleSheet("""
                QLabel {
                    background: #2ECC71;
                    border-radius: 16px;
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                }
            """)
            logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(32, 32)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addSpacing(10)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 消息内容
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            font-size: 14px;
            color: #495057;
            line-height: 1.5;
        """)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        confirm_button = QPushButton("确定")
        confirm_button.setObjectName("confirm")
        confirm_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        
        return dialog.exec_() == QDialog.Accepted
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = self.show_custom_question("退出确认", "确定要退出XC-ROBOT控制软件吗？")
        if reply:
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
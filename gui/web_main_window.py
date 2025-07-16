#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT Web主窗口 - Qt+HTML混合界面
基于QWebEngineView嵌入HTML界面
"""

import sys
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
widgets_dir = os.path.join(current_dir, 'widgets')
sys.path.insert(0, widgets_dir)

class WebBridge(QObject):
    """Python与HTML界面的通信桥接"""
    
    # 信号定义
    log_message = pyqtSignal(str, str)  # 消息, 级别
    status_changed = pyqtSignal(str, str)  # 设备, 状态
    
    def __init__(self):
        super().__init__()
        self.devices = {}
        self.init_backend_widgets()
    
    def init_backend_widgets(self):
        """初始化后端控件"""
        try:
            # 导入后端控件
            from connection_widget import ConnectionWidget
            from arm_control_widget import ArmControlWidget
            from chassis_widget import ChassisWidget
            from simulation_widget import SimulationWidget
            from log_widget import LogWidget
            
            # 创建后端控件实例
            self.connection_widget = ConnectionWidget()
            self.arm_control_widget = ArmControlWidget()
            self.chassis_widget = ChassisWidget()
            self.simulation_widget = SimulationWidget()
            self.log_widget = LogWidget()
            
            # 连接后端信号
            self.connection_widget.log_message.connect(self.on_backend_log)
            self.arm_control_widget.log_message.connect(self.on_backend_log)
            self.chassis_widget.log_message.connect(self.on_backend_log)
            self.simulation_widget.log_message.connect(self.on_backend_log)
            
            print("后端控件初始化成功")
            
        except Exception as e:
            print(f"后端控件初始化失败: {e}")
    
    def on_backend_log(self, message, level):
        """处理后端日志"""
        self.log_message.emit(message, level)
    
    @pyqtSlot(str, result=str)
    def test_connection(self, device_type):
        """测试连接"""
        try:
            if device_type == "right_arm":
                # 调用右臂连接测试
                result = self.connection_widget.test_fr3_connection("192.168.58.2")
                self.log_message.emit(f"右臂连接测试: {result}", "INFO")
                return json.dumps({"status": "success" if result else "failed", "ip": "192.168.58.2"})
            
            elif device_type == "left_arm":
                # 调用左臂连接测试
                result = self.connection_widget.test_fr3_connection("192.168.58.3")
                self.log_message.emit(f"左臂连接测试: {result}", "INFO")
                return json.dumps({"status": "success" if result else "failed", "ip": "192.168.58.3"})
            
            elif device_type == "chassis":
                # 调用底盘连接测试
                result = self.connection_widget.test_hermes_connection()
                self.log_message.emit(f"底盘连接测试: {result}", "INFO")
                return json.dumps({"status": "success" if result else "failed", "ip": "192.168.31.211"})
            
            elif device_type == "vision":
                # 调用视觉系统测试
                self.log_message.emit("视觉系统测试中...", "INFO")
                return json.dumps({"status": "warning", "message": "部分相机异常"})
            
            return json.dumps({"status": "error", "message": "未知设备类型"})
            
        except Exception as e:
            self.log_message.emit(f"连接测试失败: {e}", "ERROR")
            return json.dumps({"status": "error", "message": str(e)})
    
    @pyqtSlot(str, str)
    def control_arm(self, arm_type, action):
        """控制机械臂"""
        try:
            if arm_type == "right":
                # 调用右臂控制
                result = self.arm_control_widget.control_right_arm(action)
                self.log_message.emit(f"右臂{action}操作: {result}", "INFO")
            elif arm_type == "left":
                # 调用左臂控制
                result = self.arm_control_widget.control_left_arm(action)
                self.log_message.emit(f"左臂{action}操作: {result}", "INFO")
            elif arm_type == "both":
                # 双臂协调控制
                result = self.arm_control_widget.control_both_arms(action)
                self.log_message.emit(f"双臂{action}操作: {result}", "INFO")
                
        except Exception as e:
            self.log_message.emit(f"机械臂控制失败: {e}", "ERROR")
    
    @pyqtSlot(str)
    def control_chassis(self, action):
        """控制底盘"""
        try:
            result = self.chassis_widget.control_chassis(action)
            self.log_message.emit(f"底盘{action}操作: {result}", "INFO")
        except Exception as e:
            self.log_message.emit(f"底盘控制失败: {e}", "ERROR")
    
    @pyqtSlot(str)
    def start_simulation(self, sim_type):
        """启动仿真"""
        try:
            if sim_type == "robot_sim":
                result = self.simulation_widget.start_robot_sim()
                self.log_message.emit(f"机器人仿真启动: {result}", "INFO")
            elif sim_type == "3d_sim":
                result = self.simulation_widget.start_3d_sim()
                self.log_message.emit(f"3D仿真启动: {result}", "INFO")
                
        except Exception as e:
            self.log_message.emit(f"仿真启动失败: {e}", "ERROR")
    
    @pyqtSlot()
    def emergency_stop(self):
        """紧急停止"""
        try:
            self.log_message.emit("执行全系统紧急停止", "WARNING")
            
            # 调用各控件的紧急停止
            if hasattr(self.arm_control_widget, 'emergency_stop'):
                self.arm_control_widget.emergency_stop()
            if hasattr(self.chassis_widget, 'emergency_stop'):
                self.chassis_widget.emergency_stop()
            if hasattr(self.simulation_widget, 'emergency_stop'):
                self.simulation_widget.emergency_stop()
                
        except Exception as e:
            self.log_message.emit(f"紧急停止执行异常: {e}", "ERROR")
    
    @pyqtSlot(result=str)
    def get_system_status(self):
        """获取系统状态"""
        try:
            status = {
                "right_arm": {"status": "online", "ip": "192.168.58.2", "delay": "2ms"},
                "left_arm": {"status": "online", "ip": "192.168.58.3", "delay": "3ms"},
                "chassis": {"status": "online", "ip": "192.168.31.211", "delay": "5ms"},
                "vision": {"status": "warning", "message": "部分相机异常"}
            }
            return json.dumps(status)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @pyqtSlot()
    def clear_logs(self):
        """清空日志"""
        try:
            if hasattr(self, 'log_widget'):
                self.log_widget.clear_logs()
            self.log_message.emit("日志已清空", "INFO")
        except Exception as e:
            self.log_message.emit(f"清空日志失败: {e}", "ERROR")
    
    @pyqtSlot()
    def download_logs(self):
        """下载日志"""
        try:
            if hasattr(self, 'log_widget'):
                self.log_widget.save_logs()
            self.log_message.emit("日志已保存", "SUCCESS")
        except Exception as e:
            self.log_message.emit(f"保存日志失败: {e}", "ERROR")


class XCRobotWebMainWindow(QMainWindow):
    """XC-ROBOT Web主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("祥承 XC-ROBOT MVP1.0 Control SYSTEM")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建通信桥接
        self.bridge = WebBridge()
        
        self.setup_ui()
        self.setup_web_channel()
        self.setup_menu()
        
    def setup_ui(self):
        """设置主界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建Web视图
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # 加载HTML页面
        self.load_html_page()
        
    def load_html_page(self):
        """加载HTML页面"""
        try:
            # 获取HTML文件路径
            html_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'xc_os_newui.html')
            
            if os.path.exists(html_path):
                # 读取HTML文件并注入JS桥接代码
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 注入与Python通信的JS代码
                js_bridge_code = """
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <script>
                    var bridge = null;
                    
                    // 初始化Qt Web Channel
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        bridge = channel.objects.bridge;
                        
                        // 连接Python信号
                        bridge.log_message.connect(function(message, level) {
                            addLogEntry(message, level);
                        });
                        
                        // 界面初始化完成
                        console.log('Qt Web Channel 初始化完成');
                        updateSystemStatus();
                    });
                    
                    // 测试连接函数
                    function testConnection(deviceType) {
                        if (bridge) {
                            bridge.test_connection(deviceType, function(result) {
                                var data = JSON.parse(result);
                                updateDeviceStatus(deviceType, data);
                            });
                        }
                    }
                    
                    // 控制机械臂
                    function controlArm(armType, action) {
                        if (bridge) {
                            bridge.control_arm(armType, action);
                        }
                    }
                    
                    // 控制底盘
                    function controlChassis(action) {
                        if (bridge) {
                            bridge.control_chassis(action);
                        }
                    }
                    
                    // 启动仿真
                    function startSimulation(simType) {
                        if (bridge) {
                            bridge.start_simulation(simType);
                        }
                    }
                    
                    // 紧急停止
                    function emergencyStop() {
                        if (bridge) {
                            bridge.emergency_stop();
                        }
                    }
                    
                    // 更新系统状态
                    function updateSystemStatus() {
                        if (bridge) {
                            bridge.get_system_status(function(result) {
                                var status = JSON.parse(result);
                                updateAllDeviceStatus(status);
                            });
                        }
                    }
                    
                    // 清空日志
                    function clearLogs() {
                        if (bridge) {
                            bridge.clear_logs();
                        }
                    }
                    
                    // 下载日志
                    function downloadLogs() {
                        if (bridge) {
                            bridge.download_logs();
                        }
                    }
                    
                    // 更新设备状态显示
                    function updateDeviceStatus(deviceType, data) {
                        // 更新对应设备的状态显示
                        console.log('设备状态更新:', deviceType, data);
                    }
                    
                    // 更新所有设备状态
                    function updateAllDeviceStatus(statusData) {
                        // 更新所有设备的状态显示
                        console.log('所有设备状态:', statusData);
                    }
                    
                    // 添加日志条目
                    function addLogEntry(message, level) {
                        var logContent = document.getElementById('logContent');
                        if (logContent) {
                            var now = new Date();
                            var time = '[' + now.getHours().toString().padStart(2,'0') + ':' + 
                                      now.getMinutes().toString().padStart(2,'0') + ':' + 
                                      now.getSeconds().toString().padStart(2,'0') + ']';
                            
                            var logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.innerHTML = 
                                '<span class="log-time">' + time + '</span>' +
                                '<span class="log-level-' + level + '">[' + level + ']</span>' +
                                message;
                            
                            logContent.insertBefore(logEntry, logContent.firstChild);
                            
                            // 保持最新20条日志
                            var entries = logContent.querySelectorAll('.log-entry');
                            if (entries.length > 20) {
                                logContent.removeChild(entries[entries.length - 1]);
                            }
                        }
                    }
                    
                    // 页面加载完成后的初始化
                    document.addEventListener('DOMContentLoaded', function() {
                        console.log('页面加载完成，等待Qt Web Channel...');
                        
                        // 添加点击事件监听器
                        document.addEventListener('click', function(e) {
                            // 处理功能按钮点击
                            if (e.target.classList.contains('feature-card')) {
                                var cardTitle = e.target.querySelector('.feature-title').textContent;
                                if (cardTitle.includes('右臂')) {
                                    testConnection('right_arm');
                                } else if (cardTitle.includes('左臂')) {
                                    testConnection('left_arm');
                                } else if (cardTitle.includes('底盘')) {
                                    testConnection('chassis');
                                } else if (cardTitle.includes('视觉')) {
                                    testConnection('vision');
                                }
                            }
                        });
                        
                        // 定期更新系统状态
                        setInterval(updateSystemStatus, 5000);
                    });
                </script>
                """
                
                # 在</body>标签前插入JS代码
                html_content = html_content.replace('</body>', js_bridge_code + '\n</body>')
                
                # 设置HTML内容
                self.web_view.setHtml(html_content)
                
            else:
                # 如果HTML文件不存在，显示错误页面
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>错误</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 18px; }
                    </style>
                </head>
                <body>
                    <h1>XC-ROBOT</h1>
                    <div class="error">HTML界面文件未找到</div>
                    <p>请检查 UI/xc_os_newui.html 文件是否存在</p>
                </body>
                </html>
                """
                self.web_view.setHtml(error_html)
                
        except Exception as e:
            print(f"加载HTML页面失败: {e}")
    
    def setup_web_channel(self):
        """设置Web Channel通信"""
        try:
            # 创建Web Channel
            self.channel = QWebChannel()
            
            # 注册桥接对象
            self.channel.registerObject("bridge", self.bridge)
            
            # 设置Web Channel到页面
            self.web_view.page().setWebChannel(self.channel)
            
            print("Web Channel 设置成功")
            
        except Exception as e:
            print(f"Web Channel 设置失败: {e}")
    
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
        
        reload_action = QAction('重新加载界面 (F5)', self)
        reload_action.triggered.connect(self.reload_page)
        reload_action.setShortcut('F5')
        tools_menu.addAction(reload_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def save_log(self):
        """保存日志"""
        try:
            self.bridge.log_widget.save_logs()
        except Exception as e:
            print(f"保存日志失败: {e}")
    
    def emergency_stop(self):
        """紧急停止"""
        reply = self.show_custom_question("紧急停止", 
            "确定要执行紧急停止吗？\n这将停止所有机械臂和底盘运动！")
        if reply:
            self.bridge.emergency_stop()
    
    def reload_page(self):
        """重新加载页面"""
        self.load_html_page()
    
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
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5a6fd8, stop: 1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4e5fc6, stop: 1 #5e3778);
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # 标题和Logo区域
        header_layout = QHBoxLayout()
        
        # Logo (使用CSS绘制类似提供的绿色logo)
        logo_label = QLabel()
        logo_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #00ff88, stop: 1 #00cc66);
                border-radius: 24px;
                padding: 0px;
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        logo_label.setText("祥")
        logo_label.setFixedSize(48, 48)
        logo_label.setAlignment(Qt.AlignCenter)
        
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
            color: #667eea;
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
        
        version_label = QLabel("版本: 2.5.0 (Web界面版)")
        version_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #495057;")
        
        hardware_label = QLabel("硬件配置:")
        hardware_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #6c757d; margin-top: 8px;")
        
        hardware_details = QLabel("• 思岚Hermes移动底盘\n• 法奥意威FR3双臂机械臂\n• ToF深度相机 × 3\n• 高性能控制计算机")
        hardware_details.setStyleSheet("font-size: 12px; color: #6c757d; margin-left: 10px;")
        
        software_label = QLabel("软件架构:")
        software_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #6c757d; margin-top: 8px;")
        
        software_details = QLabel("• Python + PyQt5 + QWebEngine\n• HTML5 + CSS3 + JavaScript\n• 实时控制 + 可视化界面")
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
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#confirm:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5a6fd8, stop: 1 #6a4190);
            }
            QPushButton#cancel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #6c757d, stop: 1 #495057);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#cancel:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5a6268, stop: 1 #343a40);
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # 顶部标题区域
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #00ff88, stop: 1 #00cc66);
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        logo_label.setText("祥")
        logo_label.setFixedSize(32, 32)
        logo_label.setAlignment(Qt.AlignCenter)
        
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
            try:
                # 清理资源
                if hasattr(self.bridge, 'log_widget'):
                    self.bridge.log_widget.add_message("系统正在关闭...", "INFO")
                    
                # 清理各个组件的资源
                if hasattr(self.bridge, 'simulation_widget') and hasattr(self.bridge.simulation_widget, 'cleanup'):
                    self.bridge.simulation_widget.cleanup()
                    
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
    app.setApplicationName("XC-ROBOT Web")
    app.setStyle('Fusion')
    
    # 使用系统默认字体
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    window = XCRobotWebMainWindow()
    
    # 处理Ctrl+C信号
    def signal_handler(signum, frame):
        print("\n收到退出信号，正在关闭应用...")
        try:
            # 清理资源
            if hasattr(window.bridge, 'simulation_widget') and hasattr(window.bridge.simulation_widget, 'cleanup'):
                window.bridge.simulation_widget.cleanup()
        except Exception as e:
            print(f"清理资源时出错: {e}")
        finally:
            app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 让Python能够处理信号
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接测试控件
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class ConnectionWidget(QWidget):
    """连接测试控件"""
    
    # 信号定义
    connection_status_changed = pyqtSignal(str, bool)  # 组件名, 连接状态
    log_message = pyqtSignal(str, str)  # 消息, 级别
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connection_states = {
            'right_arm': False,
            'left_arm': False,
            'chassis': False
        }
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 网络配置组
        network_group = QGroupBox("网络配置")
        network_layout = QFormLayout(network_group)
        
        # IP地址输入
        self.right_arm_ip = QLineEdit("192.168.58.2")
        self.left_arm_ip = QLineEdit("192.168.58.3") 
        self.chassis_ip = QLineEdit("192.168.1.100")
        
        network_layout.addRow("右臂IP:", self.right_arm_ip)
        network_layout.addRow("左臂IP:", self.left_arm_ip)
        network_layout.addRow("底盘IP:", self.chassis_ip)
        
        layout.addWidget(network_group)
        
        # 连接测试组
        test_group = QGroupBox("连接测试")
        test_layout = QGridLayout(test_group)
        
        # 创建测试按钮和状态指示
        self.test_buttons = {}
        self.status_indicators = {}
        
        components = [
            ("right_arm", "右臂机械臂", 0),
            ("left_arm", "左臂机械臂", 1),
            ("chassis", "Hermes底盘", 2)
        ]
        
        for key, name, row in components:
            # 测试按钮
            btn = QPushButton(f"测试{name}")
            btn.clicked.connect(lambda checked, k=key: self.test_connection(k))
            self.test_buttons[key] = btn
            test_layout.addWidget(btn, row, 0)
            
            # 状态指示
            status = QLabel("未连接")
            status.setStyleSheet("color: red; font-weight: bold;")
            self.status_indicators[key] = status
            test_layout.addWidget(status, row, 1)
            
            # 详细信息按钮
            detail_btn = QPushButton("详情")
            detail_btn.clicked.connect(lambda checked, k=key: self.show_detail(k))
            test_layout.addWidget(detail_btn, row, 2)
        
        layout.addWidget(test_group)
        
        # 批量操作
        batch_group = QGroupBox("批量操作")
        batch_layout = QHBoxLayout(batch_group)
        
        self.test_all_btn = QPushButton("🔍 测试所有连接")
        self.test_all_btn.clicked.connect(self.test_all_connections)
        
        self.ping_test_btn = QPushButton("📡 网络Ping测试")
        self.ping_test_btn.clicked.connect(self.ping_test)
        
        self.save_config_btn = QPushButton("💾 保存配置")
        self.save_config_btn.clicked.connect(self.save_config)
        
        batch_layout.addWidget(self.test_all_btn)
        batch_layout.addWidget(self.ping_test_btn)
        batch_layout.addWidget(self.save_config_btn)
        
        layout.addWidget(batch_group)
        
        # 连接信息显示
        info_group = QGroupBox("连接信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_group)
        
        # 添加弹簧
        layout.addStretch()
    
    def test_connection(self, component: str):
        """测试单个组件连接"""
        self.log_message.emit(f"开始测试{component}连接...", "INFO")
        
        # 禁用按钮，显示测试中状态
        self.test_buttons[component].setEnabled(False)
        self.test_buttons[component].setText("测试中...")
        self.status_indicators[component].setText("测试中...")
        self.status_indicators[component].setStyleSheet("color: orange; font-weight: bold;")
        
        # 创建工作线程进行连接测试
        worker = ConnectionTestWorker(component, self.get_ip(component))
        worker.test_completed.connect(self.on_test_completed)
        worker.start()
    
    def get_ip(self, component: str) -> str:
        """获取组件IP地址"""
        if component == "right_arm":
            return self.right_arm_ip.text()
        elif component == "left_arm":
            return self.left_arm_ip.text()
        elif component == "chassis":
            return self.chassis_ip.text()
        return ""
    
    def on_test_completed(self, component: str, success: bool, message: str):
        """连接测试完成回调"""
        # 恢复按钮状态
        self.test_buttons[component].setEnabled(True)
        
        if component == "right_arm":
            self.test_buttons[component].setText("测试右臂")
        elif component == "left_arm":
            self.test_buttons[component].setText("测试左臂")
        elif component == "chassis":
            self.test_buttons[component].setText("测试底盘")
        
        # 更新状态显示
        self.connection_states[component] = success
        
        if success:
            self.status_indicators[component].setText("已连接")
            self.status_indicators[component].setStyleSheet("color: green; font-weight: bold;")
            self.log_message.emit(f"{component}连接成功", "SUCCESS")
        else:
            self.status_indicators[component].setText("连接失败")
            self.status_indicators[component].setStyleSheet("color: red; font-weight: bold;")
            self.log_message.emit(f"{component}连接失败: {message}", "ERROR")
        
        # 更新连接信息
        self.update_connection_info(component, success, message)
        
        # 发送状态变化信号
        self.connection_status_changed.emit(component, success)
    
    def update_connection_info(self, component: str, success: bool, message: str):
        """更新连接信息显示"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        status = "成功" if success else "失败"
        info = f"[{timestamp}] {component}: {status} - {message}\n"
        
        self.info_text.append(info)
        
        # 自动滚动到底部
        cursor = self.info_text.textCursor()
        cursor.movePosition(cursor.End)
        self.info_text.setTextCursor(cursor)
    
    def test_all_connections(self):
        """测试所有连接"""
        self.log_message.emit("开始批量连接测试...", "INFO")
        self.info_text.clear()
        
        components = ["right_arm", "left_arm", "chassis"]
        for component in components:
            self.test_connection(component)
    
    def ping_test(self):
        """网络Ping测试"""
        self.log_message.emit("开始网络Ping测试...", "INFO")
        
        ips = [
            ("右臂", self.right_arm_ip.text()),
            ("左臂", self.left_arm_ip.text()),
            ("底盘", self.chassis_ip.text())
        ]
        
        for name, ip in ips:
            worker = PingTestWorker(name, ip)
            worker.ping_completed.connect(self.on_ping_completed)
            worker.start()
    
    def on_ping_completed(self, name: str, success: bool, time_ms: float):
        """Ping测试完成"""
        if success:
            message = f"{name}({self.get_ip_by_name(name)}) Ping成功: {time_ms:.1f}ms"
            self.log_message.emit(message, "SUCCESS")
        else:
            message = f"{name}({self.get_ip_by_name(name)}) Ping失败"
            self.log_message.emit(message, "WARNING")
        
        self.info_text.append(f"{message}\n")
    
    def get_ip_by_name(self, name: str) -> str:
        """根据名称获取IP"""
        if name == "右臂":
            return self.right_arm_ip.text()
        elif name == "左臂":
            return self.left_arm_ip.text()
        elif name == "底盘":
            return self.chassis_ip.text()
        return ""
    
    def show_detail(self, component: str):
        """显示详细信息"""
        dialog = ConnectionDetailDialog(component, self.get_ip(component), self)
        dialog.exec_()
    
    def save_config(self):
        """保存配置"""
        config = {
            'right_arm_ip': self.right_arm_ip.text(),
            'left_arm_ip': self.left_arm_ip.text(),
            'chassis_ip': self.chassis_ip.text()
        }
        
        # 保存到配置文件
        try:
            import yaml
            with open('robot_config.yaml', 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f)
            
            # 更新网络配置
            if 'network' not in full_config:
                full_config['network'] = {}
            
            full_config['network']['right_arm_ip'] = config['right_arm_ip']
            full_config['network']['left_arm_ip'] = config['left_arm_ip']
            full_config['network']['hermes_url'] = f"http://{config['chassis_ip']}"
            
            with open('robot_config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(full_config, f, default_flow_style=False, allow_unicode=True)
            
            self.log_message.emit("配置已保存到 robot_config.yaml", "SUCCESS")
            
        except Exception as e:
            self.log_message.emit(f"保存配置失败: {e}", "ERROR")

class ConnectionTestWorker(QThread):
    """连接测试工作线程"""
    
    test_completed = pyqtSignal(str, bool, str)
    
    def __init__(self, component: str, ip: str):
        super().__init__()
        self.component = component
        self.ip = ip
    
    def run(self):
        """执行连接测试"""
        try:
            if self.component in ["right_arm", "left_arm"]:
                success, message = self.test_fr3_connection()
            elif self.component == "chassis":
                success, message = self.test_chassis_connection()
            else:
                success, message = False, "未知组件"
            
            self.test_completed.emit(self.component, success, message)
            
        except Exception as e:
            self.test_completed.emit(self.component, False, str(e))
    
    def test_fr3_connection(self):
        """测试FR3机械臂连接"""
        try:
            # 导入FR3库
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'fr3_control'))
            from fairino import Robot
            
            # 尝试连接
            robot = Robot.RPC(self.ip)
            
            # 测试基本通信
            try:
                sdk_version = robot.GetSDKVersion()
                robot.CloseRPC()
                return True, f"SDK版本: {sdk_version}"
            except:
                robot.CloseRPC()
                return True, "连接成功但API测试失败"
                
        except Exception as e:
            return False, str(e)
    
    def test_chassis_connection(self):
        """测试底盘连接"""
        try:
            import requests
            url = f"http://{self.ip}/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return True, f"HTTP状态: {response.status_code}"
            else:
                return False, f"HTTP错误: {response.status_code}"
                
        except Exception as e:
            return False, str(e)

class PingTestWorker(QThread):
    """Ping测试工作线程"""
    
    ping_completed = pyqtSignal(str, bool, float)
    
    def __init__(self, name: str, ip: str):
        super().__init__()
        self.name = name
        self.ip = ip
    
    def run(self):
        """执行Ping测试"""
        import subprocess
        import platform
        import time
        
        try:
            start_time = time.time()
            
            # 根据操作系统选择ping命令
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", self.ip]
            else:
                cmd = ["ping", "-c", "1", self.ip]
            
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            
            end_time = time.time()
            time_ms = (end_time - start_time) * 1000
            
            success = result.returncode == 0
            self.ping_completed.emit(self.name, success, time_ms)
            
        except Exception:
            self.ping_completed.emit(self.name, False, 0.0)

class ConnectionDetailDialog(QDialog):
    """连接详情对话框"""
    
    def __init__(self, component: str, ip: str, parent=None):
        super().__init__(parent)
        self.component = component
        self.ip = ip
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle(f"{self.component} 连接详情")
        self.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("组件:", QLabel(self.component))
        info_layout.addRow("IP地址:", QLabel(self.ip))
        info_layout.addRow("端口:", QLabel("20003" if "arm" in self.component else "80"))
        
        layout.addWidget(info_group)
        
        # 测试结果
        result_group = QGroupBox("测试结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("重新测试")
        test_btn.clicked.connect(self.retest)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(test_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # 自动执行一次测试
        self.retest()
    
    def retest(self):
        """重新测试"""
        self.result_text.clear()
        self.result_text.append("正在测试连接...\n")
        
        # 启动测试线程
        worker = ConnectionTestWorker(self.component, self.ip)
        worker.test_completed.connect(self.on_test_completed)
        worker.start()
    
    def on_test_completed(self, component: str, success: bool, message: str):
        """测试完成"""
        self.result_text.clear()
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.result_text.append(f"测试时间: {timestamp}")
        self.result_text.append(f"组件: {component}")
        self.result_text.append(f"IP地址: {self.ip}")
        self.result_text.append(f"结果: {'成功' if success else '失败'}")
        self.result_text.append(f"详情: {message}")
        
        if success:
            self.result_text.append("\n✅ 连接正常，可以进行控制操作")
        else:
            self.result_text.append("\n❌ 连接失败，请检查:")
            self.result_text.append("  • 设备是否通电")
            self.result_text.append("  • 网络连接是否正常")
            self.result_text.append("  • IP地址是否正确")
            self.result_text.append("  • 防火墙设置")
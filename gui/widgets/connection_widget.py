#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接测试控件 - 修正IP和端口版
"""

import sys
import os
import requests
import yaml
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ConnectionWidget(QWidget):
    """连接测试控件"""
    
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.test_workers = {}  # 保存工作线程的引用
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # IP配置
        config_group = QGroupBox("网络配置")
        config_layout = QFormLayout()
        
        self.right_arm_ip = QLineEdit("192.168.58.2")
        self.left_arm_ip = QLineEdit("192.168.58.3")
        self.chassis_ip = QLineEdit("192.168.31.211")  # 修正的IP
        self.chassis_port = QLineEdit("1448")           # 新增端口配置
        
        config_layout.addRow("右臂IP:", self.right_arm_ip)
        config_layout.addRow("左臂IP:", self.left_arm_ip)
        config_layout.addRow("底盘IP:", self.chassis_ip)
        config_layout.addRow("底盘端口:", self.chassis_port)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 连接测试
        test_group = QGroupBox("连接测试")
        test_layout = QGridLayout()
        
        # 组件列表
        self.components = [
            ("右臂", "right_arm", self.right_arm_ip),
            ("左臂", "left_arm", self.left_arm_ip),
            ("底盘", "chassis", self.chassis_ip)
        ]
        
        self.test_buttons = {}
        self.status_labels = {}
        
        for i, (name, key, ip_widget) in enumerate(self.components):
            # 测试按钮
            test_btn = QPushButton(f"测试{name}")
            test_btn.clicked.connect(lambda checked, k=key: self.test_connection(k))
            self.test_buttons[key] = test_btn
            
            # 状态标签
            status_label = QLabel("未测试")
            status_label.setStyleSheet("color: gray;")
            self.status_labels[key] = status_label
            
            test_layout.addWidget(test_btn, i, 0)
            test_layout.addWidget(status_label, i, 1)
        
        # 批量操作按钮
        test_all_btn = QPushButton("测试全部")
        test_all_btn.clicked.connect(self.test_all_connections)
        
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        
        test_layout.addWidget(test_all_btn, 3, 0)
        test_layout.addWidget(save_btn, 3, 1)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # 连接信息显示
        info_group = QGroupBox("测试结果")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
    def test_connection(self, component):
        """测试单个组件连接"""
        # 如果该组件已有测试线程在运行，先停止它
        if component in self.test_workers and self.test_workers[component].isRunning():
            self.test_workers[component].quit()
            self.test_workers[component].wait()
        
        # 禁用按钮
        self.test_buttons[component].setEnabled(False)
        self.test_buttons[component].setText("测试中...")
        self.status_labels[component].setText("测试中...")
        self.status_labels[component].setStyleSheet("color: orange;")
        
        # 创建测试线程
        if component == "chassis":
            # 底盘需要IP和端口
            ip = self.chassis_ip.text()
            port = self.chassis_port.text()
            worker = ConnectionTestWorker(component, ip, port)
        else:
            # 机械臂只需要IP
            worker = ConnectionTestWorker(component, self.get_ip(component))
        
        # 保存线程引用
        self.test_workers[component] = worker
        
        # 连接信号
        worker.test_completed.connect(self.on_test_completed)
        worker.finished.connect(lambda: self.cleanup_worker(component))
        
        # 启动线程
        worker.start()
    
    def cleanup_worker(self, component):
        """清理工作线程"""
        if component in self.test_workers:
            worker = self.test_workers[component]
            if worker.isFinished():
                del self.test_workers[component]
    
    def get_ip(self, component):
        """获取组件IP地址"""
        ip_map = {
            "right_arm": self.right_arm_ip.text(),
            "left_arm": self.left_arm_ip.text(),
            "chassis": self.chassis_ip.text()
        }
        return ip_map.get(component, "")
    
    def on_test_completed(self, component, success, message):
        """测试完成回调"""
        # 恢复按钮
        self.test_buttons[component].setEnabled(True)
        
        component_names = {
            "right_arm": "测试右臂",
            "left_arm": "测试左臂", 
            "chassis": "测试底盘"
        }
        self.test_buttons[component].setText(component_names.get(component, "测试"))
        
        # 更新状态
        if success:
            self.status_labels[component].setText("连接成功")
            self.status_labels[component].setStyleSheet("color: green;")
            self.log_message.emit(f"{component}连接成功", "SUCCESS")
        else:
            self.status_labels[component].setText("连接失败")
            self.status_labels[component].setStyleSheet("color: red;")
            self.log_message.emit(f"{component}连接失败: {message}", "ERROR")
        
        # 添加到信息显示
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "成功" if success else "失败"
        info = f"[{timestamp}] {component}: {status} - {message}"
        self.info_text.append(info)
    
    def test_all_connections(self):
        """测试所有连接"""
        self.log_message.emit("开始批量连接测试", "INFO")
        self.info_text.clear()
        
        for name, key, _ in self.components:
            self.test_connection(key)
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            'network': {
                'right_arm_ip': self.right_arm_ip.text(),
                'left_arm_ip': self.left_arm_ip.text(),
                'chassis_ip': self.chassis_ip.text(),
                'chassis_port': int(self.chassis_port.text())
            }
        }
        
        try:
            # 尝试读取现有配置
            config_file = 'robot_config.yaml'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = yaml.safe_load(f) or {}
                existing_config.update(config)
                config = existing_config
            
            # 保存配置
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.log_message.emit("配置已保存", "SUCCESS")
            
        except Exception as e:
            self.log_message.emit(f"保存配置失败: {e}", "ERROR")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止所有正在运行的测试线程
        for component, worker in self.test_workers.items():
            if worker.isRunning():
                worker.quit()
                worker.wait(3000)  # 等待最多3秒
        event.accept()

class ConnectionTestWorker(QThread):
    """连接测试工作线程"""
    
    test_completed = pyqtSignal(str, bool, str)
    
    def __init__(self, component, ip, port=None):
        super().__init__()
        self.component = component
        self.ip = ip
        self.port = port
        self.finished.connect(self.deleteLater)  # 自动清理线程
    
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
        finally:
            self.quit()  # 确保线程正确退出
    
    def test_fr3_connection(self):
        """测试FR3机械臂连接"""
        try:
            # 尝试导入FR3库并连接
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'fr3_control'))
            from fairino import Robot
            
            robot = Robot.RPC(self.ip)
            
            # 测试基本通信
            try:
                error, version = robot.GetSDKVersion()
                robot.CloseRPC()
                if error == 0:
                    return True, f"SDK版本: {version}"
                else:
                    return False, f"API错误码: {error}"
            except:
                robot.CloseRPC()
                return True, "连接成功但版本获取失败"
                
        except Exception as e:
            return False, str(e)
    
    def test_chassis_connection(self):
        """测试底盘连接"""
        try:
            # 使用正确的Hermes API端点
            url = f"http://{self.ip}:{self.port}/api/core/system/v1/power/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return True, f"HTTP {response.status_code} - 电池状态获取成功"
            else:
                return False, f"HTTP错误: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "连接超时"
        except requests.exceptions.ConnectionError:
            return False, "连接被拒绝，请检查IP和端口"
        except Exception as e:
            return False, str(e)
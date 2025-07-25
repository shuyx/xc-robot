#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接测试控件 - 增强版设备管理
支持机器人、底盘、视觉、末端执行器等设备的启动、连接和监听
"""

import sys
import os
import requests
import yaml
import json
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ConnectionWidget(QWidget):
    """连接测试控件"""
    
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.test_workers = {}  # 保存工作线程的引用
        self.device_states = {}  # 保存设备状态
        self.setup_ui()
        self.load_config()
        
        # 添加启动按钮到界面顶部
        self.add_start_button()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 设备配置
        config_group = QGroupBox("设备配置")
        config_layout = QFormLayout()
        
        # 机器人设备
        self.right_arm_ip = QLineEdit("192.168.58.2")
        self.left_arm_ip = QLineEdit("192.168.58.3")
        
        # 底盘设备
        self.chassis_ip = QLineEdit("192.168.31.211")
        self.chassis_port = QLineEdit("1448")
        
        # 视觉设备
        self.vision_ip = QLineEdit("192.168.1.100")
        self.vision_port = QLineEdit("8080")
        
        # 末端执行器
        self.gripper_ip = QLineEdit("192.168.1.101")
        self.gripper_port = QLineEdit("9000")
        
        config_layout.addRow("右臂IP:", self.right_arm_ip)
        config_layout.addRow("左臂IP:", self.left_arm_ip)
        config_layout.addRow("底盘IP:", self.chassis_ip)
        config_layout.addRow("底盘端口:", self.chassis_port)
        config_layout.addRow("视觉系统IP:", self.vision_ip)
        config_layout.addRow("视觉系统端口:", self.vision_port)
        config_layout.addRow("末端执行器IP:", self.gripper_ip)
        config_layout.addRow("末端执行器端口:", self.gripper_port)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 连接状态面板
        device_group = QGroupBox("连接状态")
        device_layout = QGridLayout()
        
        # 设备列表
        self.devices = [
            ("右臂", "right_arm", "fr3", self.right_arm_ip),
            ("左臂", "left_arm", "fr3", self.left_arm_ip),
            ("底盘", "chassis", "hermes", self.chassis_ip),
            ("视觉系统", "vision", "camera", self.vision_ip),
            ("末端执行器", "gripper", "gripper", self.gripper_ip)
        ]
        
        self.start_buttons = {}
        self.status_labels = {}
        
        # 表头
        device_layout.addWidget(QLabel("设备名称"), 0, 0)
        device_layout.addWidget(QLabel("启动连接"), 0, 1)
        device_layout.addWidget(QLabel("连接状态"), 0, 2)
        
        for i, (name, key, device_type, ip_widget) in enumerate(self.devices, 1):
            # 设备名称
            device_layout.addWidget(QLabel(name), i, 0)
            
            # 启动按钮 - 点击后才会触发连接
            start_btn = QPushButton("启动连接")
            start_btn.clicked.connect(lambda checked, k=key: self.start_device_connection(k))
            self.start_buttons[key] = start_btn
            device_layout.addWidget(start_btn, i, 1)
            
            # 连接状态标签 - 只显示状态，不执行连接
            status_label = QLabel("未连接")
            status_label.setStyleSheet("color: gray;")
            status_label.setToolTip(f"点击查看{name}连接状态")
            self.status_labels[key] = status_label
            device_layout.addWidget(status_label, i, 2)
            
            # 初始化设备状态
            self.device_states[key] = {
                'connected': False,
                'type': device_type
            }
        
        # 批量操作按钮
        controls_layout = QHBoxLayout()
        
        start_all_btn = QPushButton("启动全部连接")
        start_all_btn.clicked.connect(self.start_all_connections)
        
        disconnect_all_btn = QPushButton("断开全部连接")
        disconnect_all_btn.clicked.connect(self.disconnect_all_devices)
        
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        
        controls_layout.addWidget(start_all_btn)
        controls_layout.addWidget(disconnect_all_btn)
        controls_layout.addWidget(save_btn)
        
        device_layout.addLayout(controls_layout, len(self.devices) + 1, 0, 1, 3)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # 连接日志显示
        info_group = QGroupBox("连接日志")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("连接日志将显示在这里...")
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
    def add_start_button(self):
        """添加启动连接按钮"""
        # 在界面顶部添加启动按钮
        start_button = QPushButton("🚀 启动连接机器人")
        start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 14px; padding: 10px; }")
        start_button.clicked.connect(self.start_robot_connection)
        
        # 插入到布局的第一个位置
        layout = self.layout()
        layout.insertWidget(0, start_button)
        
    def start_robot_connection(self):
        """启动机器人连接 - 将原有的自动连接代码放在这里"""
        self.log_message.emit("用户点击启动连接按钮", "INFO")
        # 这里放置原来自动执行的连接代码
        self.start_all_connections()
        
    def start_device_connection(self, device_key):
        """启动设备连接"""
        if device_key in self.test_workers and self.test_workers[device_key].isRunning():
            self.log_message.emit(f"{device_key}设备正在连接中", "WARNING")
            return
            
        # 更新按钮状态
        self.start_buttons[device_key].setText("连接中...")
        self.start_buttons[device_key].setEnabled(False)
        self.status_labels[device_key].setText("连接中...")
        self.status_labels[device_key].setStyleSheet("color: orange;")
        
        # 创建连接测试线程
        config = self.get_device_config(device_key)
        worker = ConnectionTestWorker(device_key, config)
        self.test_workers[device_key] = worker
        
        # 连接信号
        worker.test_completed.connect(self.on_connection_completed)
        worker.finished.connect(lambda: self.cleanup_worker(device_key))
        
        # 启动线程
        worker.start()
        
        self.log_message.emit(f"正在连接{device_key}设备...", "INFO")
    
    def disconnect_device(self, device_key):
        """断开设备连接"""
        if device_key in self.test_workers and self.test_workers[device_key].isRunning():
            self.test_workers[device_key].quit()
            self.test_workers[device_key].wait()
        
        # 重置设备状态
        self.device_states[device_key]['connected'] = False
        self.start_buttons[device_key].setText("启动连接")
        self.start_buttons[device_key].setEnabled(True)
        self.status_labels[device_key].setText("已断开")
        self.status_labels[device_key].setStyleSheet("color: gray;")
        
        self.log_message.emit(f"{device_key}设备已断开连接", "INFO")
        
        # 添加到日志
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        info = f"[{timestamp}] {device_key}设备已断开连接"
        self.info_text.append(info)
    
    
    def cleanup_worker(self, device_key):
        """清理连接测试线程"""
        if device_key in self.test_workers:
            worker = self.test_workers[device_key]
            if worker.isFinished():
                del self.test_workers[device_key]
    
    def get_device_config(self, device_key):
        """获取设备配置信息"""
        config_map = {
            "right_arm": {
                "ip": self.right_arm_ip.text(),
                "port": None,
                "type": "fr3"
            },
            "left_arm": {
                "ip": self.left_arm_ip.text(),
                "port": None,
                "type": "fr3"
            },
            "chassis": {
                "ip": self.chassis_ip.text(),
                "port": self.chassis_port.text(),
                "type": "hermes"
            },
            "vision": {
                "ip": self.vision_ip.text(),
                "port": self.vision_port.text(),
                "type": "camera"
            },
            "gripper": {
                "ip": self.gripper_ip.text(),
                "port": self.gripper_port.text(),
                "type": "gripper"
            }
        }
        return config_map.get(device_key, {})
    
    def on_connection_completed(self, device_key, success, message):
        """连接完成回调"""
        # 恢复按钮状态
        self.start_buttons[device_key].setEnabled(True)
        
        if success:
            self.device_states[device_key]['connected'] = True
            self.start_buttons[device_key].setText("断开连接")
            self.start_buttons[device_key].clicked.disconnect()
            self.start_buttons[device_key].clicked.connect(lambda checked, k=device_key: self.disconnect_device(k))
            self.status_labels[device_key].setText("已连接")
            self.status_labels[device_key].setStyleSheet("color: green;")
            self.log_message.emit(f"{device_key}连接成功: {message}", "SUCCESS")
        else:
            self.device_states[device_key]['connected'] = False
            self.start_buttons[device_key].setText("启动连接")
            self.status_labels[device_key].setText("连接失败")
            self.status_labels[device_key].setStyleSheet("color: red;")
            self.log_message.emit(f"{device_key}连接失败: {message}", "ERROR")
        
        # 添加到信息显示
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "成功" if success else "失败"
        info = f"[{timestamp}] {device_key}连接{status}: {message}"
        self.info_text.append(info)
    
    
    def start_all_connections(self):
        """启动所有设备连接"""
        self.log_message.emit("开始批量连接设备", "INFO")
        self.info_text.clear()
        
        for name, key, device_type, _ in self.devices:
            if not self.device_states[key]['connected']:
                self.start_device_connection(key)
                time.sleep(0.1)  # 稍微延迟避免同时连接
    
    def disconnect_all_devices(self):
        """断开所有设备连接"""
        self.log_message.emit("开始断开所有设备连接", "INFO")
        
        # 停止所有连接线程
        for device_key, worker in self.test_workers.items():
            if worker.isRunning():
                worker.quit()
                worker.wait(3000)
        
        # 重置所有设备状态
        for device_key in self.device_states:
            self.device_states[device_key]['connected'] = False
            
            # 重置界面元素
            self.start_buttons[device_key].setText("启动连接")
            self.start_buttons[device_key].setEnabled(True)
            self.start_buttons[device_key].clicked.disconnect()
            self.start_buttons[device_key].clicked.connect(lambda checked, k=device_key: self.start_device_connection(k))
            self.status_labels[device_key].setText("未连接")
            self.status_labels[device_key].setStyleSheet("color: gray;")
        
        self.log_message.emit("所有设备已断开连接", "INFO")
    
    def load_config(self):
        """从文件加载配置"""
        try:
            config_file = 'robot_config.yaml'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                # 加载网络配置
                if 'network' in config:
                    network = config['network']
                    if 'right_arm_ip' in network:
                        self.right_arm_ip.setText(network['right_arm_ip'])
                    if 'left_arm_ip' in network:
                        self.left_arm_ip.setText(network['left_arm_ip'])
                    if 'chassis_ip' in network:
                        self.chassis_ip.setText(network['chassis_ip'])
                    if 'chassis_port' in network:
                        self.chassis_port.setText(str(network['chassis_port']))
                
                # 加载新设备配置
                if 'devices' in config:
                    devices = config['devices']
                    if 'vision' in devices:
                        vision = devices['vision']
                        self.vision_ip.setText(vision.get('ip', '192.168.1.100'))
                        self.vision_port.setText(str(vision.get('port', 8080)))
                    if 'gripper' in devices:
                        gripper = devices['gripper']
                        self.gripper_ip.setText(gripper.get('ip', '192.168.1.101'))
                        self.gripper_port.setText(str(gripper.get('port', 9000)))
                        
        except Exception as e:
            self.log_message.emit(f"加载配置失败: {e}", "ERROR")
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            'network': {
                'right_arm_ip': self.right_arm_ip.text(),
                'left_arm_ip': self.left_arm_ip.text(),
                'chassis_ip': self.chassis_ip.text(),
                'chassis_port': int(self.chassis_port.text())
            },
            'devices': {
                'vision': {
                    'ip': self.vision_ip.text(),
                    'port': int(self.vision_port.text()),
                    'type': 'camera',
                    'enabled': True
                },
                'gripper': {
                    'ip': self.gripper_ip.text(),
                    'port': int(self.gripper_port.text()),
                    'type': 'gripper',
                    'enabled': True
                }
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
        # 停止所有正在运行的连接线程
        for device_key, worker in self.test_workers.items():
            if worker.isRunning():
                worker.quit()
                worker.wait(3000)  # 等待最多3秒
        
        event.accept()

class ConnectionTestWorker(QThread):
    """连接测试工作线程"""
    
    test_completed = pyqtSignal(str, bool, str)
    
    def __init__(self, device_key, config):
        super().__init__()
        self.device_key = device_key
        self.config = config
        self.finished.connect(self.deleteLater)  # 自动清理线程
    
    def run(self):
        """执行连接测试"""
        try:
            device_type = self.config.get('type', 'unknown')
            
            if device_type == 'fr3':
                success, message = self.test_fr3_connection()
            elif device_type == 'hermes':
                success, message = self.test_hermes_connection()
            elif device_type == 'camera':
                success, message = self.test_camera_connection()
            elif device_type == 'gripper':
                success, message = self.test_gripper_connection()
            else:
                success, message = False, f"未知设备类型: {device_type}"
            
            self.test_completed.emit(self.device_key, success, message)
            
        except Exception as e:
            self.test_completed.emit(self.device_key, False, str(e))
        finally:
            self.quit()  # 确保线程正确退出
    
    def test_fr3_connection(self):
        """测试FR3机械臂连接"""
        try:
            # 尝试导入FR3库并连接
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'fr3_control'))
            from fairino import Robot
            
            robot = Robot.RPC(self.config['ip'])
            
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
    
    def test_hermes_connection(self):
        """测试Hermes底盘连接"""
        try:
            # 使用正确的Hermes API端点
            url = f"http://{self.config['ip']}:{self.config['port']}/api/core/system/v1/power/status"
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
    
    def test_camera_connection(self):
        """测试视觉系统连接"""
        try:
            url = f"http://{self.config['ip']}:{self.config['port']}/api/camera/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return True, f"视觉系统连接成功"
            else:
                return False, f"HTTP错误: {response.status_code}"
        except Exception as e:
            return False, f"视觉系统连接失败: {str(e)}"
    
    def test_gripper_connection(self):
        """测试末端执行器连接"""
        try:
            url = f"http://{self.config['ip']}:{self.config['port']}/api/gripper/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return True, f"末端执行器连接成功"
            else:
                return False, f"HTTP错误: {response.status_code}"
        except Exception as e:
            return False, f"末端执行器连接失败: {str(e)}"
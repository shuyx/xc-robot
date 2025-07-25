#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
底盘控制组件 - 修正IP和端口版
用于控制思岚科技 Hermes 底盘
"""

import requests
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChassisWidget(QWidget):
    """底盘控制主界面"""
    
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        # 正确的IP和端口配置
        self.chassis_ip = "192.168.31.211"
        self.chassis_port = 1448
        self.is_connected = False
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 连接控制
        conn_group = QGroupBox("连接控制")
        conn_layout = QHBoxLayout()
        
        self.ip_edit = QLineEdit(self.chassis_ip)
        self.port_edit = QLineEdit(str(self.chassis_port))
        self.port_edit.setMaximumWidth(80)
        
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: red;")
        
        conn_layout.addWidget(QLabel("底盘IP:"))
        conn_layout.addWidget(self.ip_edit)
        conn_layout.addWidget(QLabel("端口:"))
        conn_layout.addWidget(self.port_edit)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.status_label)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # 状态显示
        status_group = QGroupBox("状态信息")
        status_layout = QGridLayout()
        
        self.pos_label = QLabel("位置: (0.0, 0.0, 0°)")
        self.battery_label = QLabel("电池: 0%")
        self.motion_label = QLabel("状态: 静止")
        
        status_layout.addWidget(self.pos_label, 0, 0)
        status_layout.addWidget(self.battery_label, 0, 1)
        status_layout.addWidget(self.motion_label, 0, 2)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 预设位置
        preset_group = QGroupBox("预设位置")
        preset_layout = QHBoxLayout()
        
        positions = [
            ("原点", {"x": 0.0, "y": 0.0, "theta": 0.0}),
            ("工作站1", {"x": 2.0, "y": 1.0, "theta": 90.0}),
            ("工作站2", {"x": -2.0, "y": 1.0, "theta": -90.0}),
            ("充电站", {"x": 0.0, "y": -3.0, "theta": 180.0})
        ]
        
        for name, pos in positions:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, p=pos: self.move_to_position(p))
            preset_layout.addWidget(btn)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # 手动控制
        manual_group = QGroupBox("手动控制")
        manual_layout = QVBoxLayout()
        
        # 方向按钮
        dir_widget = QWidget()
        dir_layout = QGridLayout(dir_widget)
        
        self.create_direction_buttons(dir_layout)
        manual_layout.addWidget(dir_widget)
        
        # 速度控制
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("速度:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(30)
        self.speed_label = QLabel("30%")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"{v}%"))
        
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        manual_layout.addLayout(speed_layout)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        # 坐标导航
        coord_group = QGroupBox("坐标导航")
        coord_layout = QGridLayout()
        
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-10.0, 10.0)
        self.x_spin.setSuffix(" m")
        
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-10.0, 10.0)
        self.y_spin.setSuffix(" m")
        
        self.theta_spin = QDoubleSpinBox()
        self.theta_spin.setRange(-180.0, 180.0)
        self.theta_spin.setSuffix("°")
        
        self.nav_btn = QPushButton("导航")
        self.nav_btn.clicked.connect(self.navigate_to_target)
        
        coord_layout.addWidget(QLabel("X:"), 0, 0)
        coord_layout.addWidget(self.x_spin, 0, 1)
        coord_layout.addWidget(QLabel("Y:"), 0, 2)
        coord_layout.addWidget(self.y_spin, 0, 3)
        coord_layout.addWidget(QLabel("θ:"), 1, 0)
        coord_layout.addWidget(self.theta_spin, 1, 1)
        coord_layout.addWidget(self.nav_btn, 1, 2, 1, 2)
        
        coord_group.setLayout(coord_layout)
        layout.addWidget(coord_group)
        
    def create_direction_buttons(self, layout):
        """创建方向控制按钮"""
        buttons = [
            ("↑", 0, 1, "forward"),
            ("↓", 2, 1, "backward"),
            ("←", 1, 0, "left"),
            ("→", 1, 2, "right"),
            ("↺", 0, 0, "rotate_left"),
            ("↻", 0, 2, "rotate_right"),
            ("停止", 1, 1, "stop")
        ]
        
        for text, row, col, cmd in buttons:
            btn = QPushButton(text)
            if cmd == "stop":
                btn.setStyleSheet("background-color: red; color: white;")
                btn.clicked.connect(self.stop_movement)
            else:
                btn.pressed.connect(lambda c=cmd: self.start_movement(c))
                btn.released.connect(self.stop_movement)
            layout.addWidget(btn, row, col)
    
    def get_base_url(self):
        """获取底盘基础URL"""
        ip = self.ip_edit.text()
        port = self.port_edit.text()
        return f"http://{ip}:{port}"
    
    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_connected:
            try:
                base_url = self.get_base_url()
                # 测试连接 - 使用Hermes API
                response = requests.get(f"{base_url}/api/core/system/v1/power/status", timeout=5)
                if response.status_code == 200:
                    self.is_connected = True
                    self.connect_btn.setText("断开")
                    self.status_label.setText("已连接")
                    self.status_label.setStyleSheet("color: green;")
                    self.log_message.emit(f"底盘连接成功 ({base_url})", "SUCCESS")
                else:
                    self.log_message.emit(f"底盘连接失败: HTTP {response.status_code}", "ERROR")
            except requests.exceptions.Timeout:
                self.log_message.emit("底盘连接超时", "ERROR")
            except requests.exceptions.ConnectionError:
                self.log_message.emit("底盘连接被拒绝，请检查IP和端口", "ERROR")
            except Exception as e:
                self.log_message.emit(f"底盘连接异常: {e}", "ERROR")
        else:
            self.is_connected = False
            self.connect_btn.setText("连接")
            self.status_label.setText("未连接")
            self.status_label.setStyleSheet("color: red;")
            self.log_message.emit("底盘已断开", "INFO")
    
    def move_to_position(self, position):
        """移动到预设位置"""
        if not self.is_connected:
            self.log_message.emit("请先连接底盘", "WARNING")
            return
        
        x, y, theta = position["x"], position["y"], position["theta"]
        self.log_message.emit(f"移动到位置: ({x}, {y}, {theta}°)", "INFO")
        
        try:
            base_url = self.get_base_url()
            # 使用Hermes运动控制API
            data = {
                "target": {
                    "x": x,
                    "y": y,
                    "theta": theta
                }
            }
            response = requests.post(f"{base_url}/api/core/motion/v1/actions", 
                                   json=data, timeout=5)
            if response.status_code == 200:
                self.log_message.emit("导航命令已发送", "SUCCESS")
            else:
                self.log_message.emit(f"导航失败: HTTP {response.status_code}", "ERROR")
        except Exception as e:
            self.log_message.emit(f"导航异常: {e}", "ERROR")
    
    def start_movement(self, direction):
        """开始移动"""
        if not self.is_connected:
            return
        
        speed = self.speed_slider.value()
        self.log_message.emit(f"开始{direction}移动，速度{speed}%", "INFO")
        
        try:
            base_url = self.get_base_url()
            # 实际的运动控制API调用
            data = {
                "command": direction,
                "speed": speed / 100.0  # 转换为0-1范围
            }
            # 这里可以根据实际的Hermes API文档调整
            response = requests.post(f"{base_url}/api/core/motion/v1/manual", 
                                   json=data, timeout=3)
        except Exception as e:
            self.log_message.emit(f"移动命令失败: {e}", "ERROR")
    
    def stop_movement(self):
        """停止移动"""
        if not self.is_connected:
            return
        
        self.log_message.emit("停止移动", "INFO")
        
        try:
            base_url = self.get_base_url()
            # 停止命令
            response = requests.post(f"{base_url}/api/core/motion/v1/stop", timeout=3)
        except Exception as e:
            self.log_message.emit(f"停止命令失败: {e}", "ERROR")
    
    def navigate_to_target(self):
        """导航到目标坐标"""
        if not self.is_connected:
            self.log_message.emit("请先连接底盘", "WARNING")
            return
        
        position = {
            "x": self.x_spin.value(),
            "y": self.y_spin.value(),
            "theta": self.theta_spin.value()
        }
        self.move_to_position(position)
    
    def emergency_stop(self):
        """紧急停止"""
        if not self.is_connected:
            return
        
        try:
            base_url = self.get_base_url()
            response = requests.post(f"{base_url}/api/core/motion/v1/emergency_stop", timeout=3)
            self.log_message.emit("底盘紧急停止", "WARNING")
        except Exception as e:
            self.log_message.emit(f"紧急停止失败: {e}", "ERROR")
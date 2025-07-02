#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
底盘控制控件
gui/widgets/chassis_widget.py
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChassisWidget(QWidget):
    """底盘控制控件"""
    
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.chassis_controller = None
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 连接控制
        connection_group = QGroupBox("连接控制")
        connection_layout = QHBoxLayout(connection_group)
        
        self.ip_edit = QLineEdit("192.168.1.100")
        self.connect_btn = QPushButton("🔗 连接底盘")
        self.connect_btn.clicked.connect(self.connect_chassis)
        
        self.disconnect_btn = QPushButton("❌ 断开连接")
        self.disconnect_btn.clicked.connect(self.disconnect_chassis)
        self.disconnect_btn.setEnabled(False)
        
        connection_layout.addWidget(QLabel("底盘IP:"))
        connection_layout.addWidget(self.ip_edit)
        connection_layout.addWidget(self.connect_btn)
        connection_layout.addWidget(self.disconnect_btn)
        
        layout.addWidget(connection_group)
        
        # 状态显示
        status_group = QGroupBox("底盘状态")
        status_layout = QGridLayout(status_group)
        
        status_items = [
            ("连接状态:", "connection"),
            ("当前位置:", "position"),
            ("目标位置:", "target"),
            ("运动状态:", "motion")
        ]
        
        self.status_labels = {}
        for i, (name, key) in enumerate(status_items):
            label = QLabel(name)
            status = QLabel("未知")
            status.setStyleSheet("color: gray;")
            self.status_labels[key] = status
            
            status_layout.addWidget(label, i, 0)
            status_layout.addWidget(status, i, 1)
        
        layout.addWidget(status_group)
        
        # 预定义位置控制
        position_group = QGroupBox("预定义位置")
        position_layout = QGridLayout(position_group)
        
        positions = [
            ("🏠 初始位置", "home"),
            ("🏭 工作站1", "work_station_1"),
            ("🏭 工作站2", "work_station_2"),
            ("🔋 充电站", "charging_station")
        ]
        
        for i, (name, key) in enumerate(positions):
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, k=key: self.move_to_position(k))
            position_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(position_group)
        
        # 手动控制
        manual_group = QGroupBox("手动控制")
        manual_layout = QVBoxLayout(manual_group)
        
        # 方向控制
        direction_widget = QWidget()
        direction_layout = QGridLayout(direction_widget)
        
        # 创建方向按钮
        self.forward_btn = QPushButton("⬆️")
        self.backward_btn = QPushButton("⬇️")
        self.left_btn = QPushButton("⬅️")
        self.right_btn = QPushButton("➡️")
        self.stop_btn = QPushButton("⏹️ 停止")
        
        # 旋转按钮
        self.rotate_left_btn = QPushButton("↶")
        self.rotate_right_btn = QPushButton("↷")
        
        # 布局方向按钮
        direction_layout.addWidget(self.forward_btn, 0, 1)
        direction_layout.addWidget(self.left_btn, 1, 0)
        direction_layout.addWidget(self.stop_btn, 1, 1)
        direction_layout.addWidget(self.right_btn, 1, 2)
        direction_layout.addWidget(self.backward_btn, 2, 1)
        direction_layout.addWidget(self.rotate_left_btn, 0, 0)
        direction_layout.addWidget(self.rotate_right_btn, 0, 2)
        
        manual_layout.addWidget(direction_widget)
        
        # 速度控制
        speed_layout = QHBoxLayout()
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(30)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        
        self.speed_label = QLabel("30%")
        
        speed_layout.addWidget(QLabel("移动速度:"))
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        
        manual_layout.addLayout(speed_layout)
        
        layout.addWidget(manual_group)
        
        # 坐标控制
        coord_group = QGroupBox("坐标控制")
        coord_layout = QFormLayout(coord_group)
        
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-10.0, 10.0)
        self.x_spin.setSingleStep(0.1)
        self.x_spin.setSuffix(" m")
        
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-10.0, 10.0)
        self.y_spin.setSingleStep(0.1)
        self.y_spin.setSuffix(" m")
        
        self.theta_spin = QDoubleSpinBox()
        self.theta_spin.setRange(-180.0, 180.0)
        self.theta_spin.setSingleStep(1.0)
        self.theta_spin.setSuffix(" °")
        
        self.move_to_coord_btn = QPushButton("📍 移动到坐标")
        self.move_to_coord_btn.clicked.connect(self.move_to_coordinate)
        
        coord_layout.addRow("X坐标:", self.x_spin)
        coord_layout.addRow("Y坐标:", self.y_spin)
        coord_layout.addRow("角度:", self.theta_spin)
        coord_layout.addRow(self.move_to_coord_btn)
        
        layout.addWidget(coord_group)
        
        # 连接方向按钮信号
        self.forward_btn.pressed.connect(lambda: self.start_manual_move("forward"))
        self.forward_btn.released.connect(self.stop_manual_move)
        
        self.backward_btn.pressed.connect(lambda: self.start_manual_move("backward"))
        self.backward_btn.released.connect(self.stop_manual_move)
        
        self.left_btn.pressed.connect(lambda: self.start_manual_move("left"))
        self.left_btn.released.connect(self.stop_manual_move)
        
        self.right_btn.pressed.connect(lambda: self.start_manual_move("right"))
        self.right_btn.released.connect(self.stop_manual_move)
        
        self.rotate_left_btn.pressed.connect(lambda: self.start_manual_move("rotate_left"))
        self.rotate_left_btn.released.connect(self.stop_manual_move)
        
        self.rotate_right_btn.pressed.connect(lambda: self.start_manual_move("rotate_right"))
        self.rotate_right_btn.released.connect(self.stop_manual_move)
        
        self.stop_btn.clicked.connect(self.emergency_stop)
    
    def connect_chassis(self):
        """连接底盘"""
        ip = self.ip_edit.text()
        self.log_message.emit(f"正在连接底盘 ({ip})...", "INFO")
        
        try:
            # 这里集成实际的底盘连接代码
            # sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'main_control'))
            # from integrated_controller import HermesController
            # self.chassis_controller = HermesController(f"http://{ip}")
            # success = self.chassis_controller.test_connection()
            
            # 模拟连接成功
            success = True
            
            if success:
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.update_status("connection", "已连接", "green")
                self.log_message.emit("底盘连接成功", "SUCCESS")
            else:
                self.log_message.emit("底盘连接失败", "ERROR")
                
        except Exception as e:
            self.log_message.emit(f"底盘连接异常: {e}", "ERROR")
    
    def disconnect_chassis(self):
        """断开底盘连接"""
        self.log_message.emit("断开底盘连接", "INFO")
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.update_status("connection", "未连接", "red")
    
    def update_status(self, key: str, text: str, color: str = "black"):
        """更新状态显示"""
        if key in self.status_labels:
            self.status_labels[key].setText(text)
            self.status_labels[key].setStyleSheet(f"color: {color};")
    
    def move_to_position(self, position: str):
        """移动到预定义位置"""
        self.log_message.emit(f"移动到预定义位置: {position}", "INFO")
        self.update_status("target", position, "blue")
        self.update_status("motion", "移动中", "orange")
        
        # 模拟移动完成
        QTimer.singleShot(3000, lambda: self.update_status("motion", "到达目标", "green"))
    
    def move_to_coordinate(self):
        """移动到指定坐标"""
        x = self.x_spin.value()
        y = self.y_spin.value()
        theta = self.theta_spin.value()
        
        self.log_message.emit(f"移动到坐标: X={x:.1f}m, Y={y:.1f}m, θ={theta:.1f}°", "INFO")
        self.update_status("target", f"({x:.1f}, {y:.1f}, {theta:.1f}°)", "blue")
        self.update_status("motion", "移动中", "orange")
    
    def start_manual_move(self, direction: str):
        """开始手动移动"""
        speed = self.speed_slider.value()
        self.log_message.emit(f"开始{direction}移动 (速度: {speed}%)", "INFO")
        self.update_status("motion", f"{direction}移动中", "orange")
    
    def stop_manual_move(self):
        """停止手动移动"""
        self.log_message.emit("停止手动移动", "INFO")
        self.update_status("motion", "停止", "gray")
    
    def emergency_stop(self):
        """紧急停止"""
        self.log_message.emit("底盘紧急停止", "WARNING")
        self.update_status("motion", "紧急停止", "red")
    
    def on_speed_changed(self, value: int):
        """速度改变"""
        self.speed_label.setText(f"{value}%")
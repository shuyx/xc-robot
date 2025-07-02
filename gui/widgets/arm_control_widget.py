#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂控制控件 - 精简版
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ArmControlWidget(QWidget):
    """机械臂控制控件"""
    
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.current_arm = None
        self.is_connected = False
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 机械臂选择和连接
        conn_group = QGroupBox("连接控制")
        conn_layout = QHBoxLayout()
        
        self.arm_combo = QComboBox()
        self.arm_combo.addItems(["右臂 (192.168.58.2)", "左臂 (192.168.58.3)", "双臂协调"])
        self.arm_combo.currentTextChanged.connect(self.on_arm_changed)
        
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: red;")
        
        conn_layout.addWidget(QLabel("选择机械臂:"))
        conn_layout.addWidget(self.arm_combo)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.status_label)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # 基本控制
        control_group = QGroupBox("基本控制")
        control_layout = QGridLayout()
        
        self.enable_btn = QPushButton("上使能")
        self.disable_btn = QPushButton("去使能")
        self.home_btn = QPushButton("回零")
        self.stop_btn = QPushButton("紧急停止")
        
        self.enable_btn.clicked.connect(lambda: self.set_enable(True))
        self.disable_btn.clicked.connect(lambda: self.set_enable(False))
        self.home_btn.clicked.connect(self.go_home)
        self.stop_btn.clicked.connect(self.emergency_stop)
        
        # 设置停止按钮样式
        self.stop_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        
        control_layout.addWidget(self.enable_btn, 0, 0)
        control_layout.addWidget(self.disable_btn, 0, 1)
        control_layout.addWidget(self.home_btn, 1, 0)
        control_layout.addWidget(self.stop_btn, 1, 1)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 预定义动作
        action_group = QGroupBox("预定义动作")
        action_layout = QVBoxLayout()
        
        # 动作选择
        action_select_layout = QHBoxLayout()
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "抓取准备", "放置准备", "挥手动作", "安全位置"
        ])
        
        self.execute_btn = QPushButton("执行动作")
        self.execute_btn.clicked.connect(self.execute_action)
        
        action_select_layout.addWidget(QLabel("动作:"))
        action_select_layout.addWidget(self.action_combo)
        action_select_layout.addWidget(self.execute_btn)
        action_layout.addLayout(action_select_layout)
        
        # 速度控制
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("速度:"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(20)
        self.speed_label = QLabel("20%")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"{v}%"))
        
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        action_layout.addLayout(speed_layout)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # 手动点动控制
        jog_group = QGroupBox("关节点动")
        jog_layout = QGridLayout()
        
        # 关节控制
        self.joint_controls = []
        for i in range(6):
            # 关节标签
            label = QLabel(f"J{i+1}")
            jog_layout.addWidget(label, i, 0)
            
            # 负方向按钮
            neg_btn = QPushButton("◀")
            neg_btn.pressed.connect(lambda j=i: self.start_jog(j, -1))
            neg_btn.released.connect(self.stop_jog)
            jog_layout.addWidget(neg_btn, i, 1)
            
            # 位置显示
            pos_label = QLabel("0.0°")
            pos_label.setAlignment(Qt.AlignCenter)
            jog_layout.addWidget(pos_label, i, 2)
            
            # 正方向按钮
            pos_btn = QPushButton("▶")
            pos_btn.pressed.connect(lambda j=i: self.start_jog(j, 1))
            pos_btn.released.connect(self.stop_jog)
            jog_layout.addWidget(pos_btn, i, 3)
            
            self.joint_controls.append(pos_label)
        
        # 点动速度
        jog_speed_layout = QHBoxLayout()
        jog_speed_layout.addWidget(QLabel("点动速度:"))
        
        self.jog_speed_slider = QSlider(Qt.Horizontal)
        self.jog_speed_slider.setRange(1, 50)
        self.jog_speed_slider.setValue(10)
        self.jog_speed_label = QLabel("10%")
        self.jog_speed_slider.valueChanged.connect(lambda v: self.jog_speed_label.setText(f"{v}%"))
        
        jog_speed_layout.addWidget(self.jog_speed_slider)
        jog_speed_layout.addWidget(self.jog_speed_label)
        
        jog_layout.addLayout(jog_speed_layout, 6, 0, 1, 4)
        
        jog_group.setLayout(jog_layout)
        layout.addWidget(jog_group)
        
        # 双臂协调控制（默认隐藏）
        self.dual_arm_group = QGroupBox("双臂协调控制")
        dual_layout = QHBoxLayout()
        
        self.coord_combo = QComboBox()
        self.coord_combo.addItems(["双臂回零", "双臂挥手", "协调抓取", "镜像运动"])
        
        self.coord_btn = QPushButton("执行协调动作")
        self.coord_btn.clicked.connect(self.execute_coordination)
        
        dual_layout.addWidget(self.coord_combo)
        dual_layout.addWidget(self.coord_btn)
        
        self.dual_arm_group.setLayout(dual_layout)
        self.dual_arm_group.setVisible(False)
        layout.addWidget(self.dual_arm_group)
        
    def on_arm_changed(self, text):
        """机械臂选择改变"""
        if "双臂协调" in text:
            self.dual_arm_group.setVisible(True)
            self.current_arm = "dual"
        else:
            self.dual_arm_group.setVisible(False)
            if "右臂" in text:
                self.current_arm = "right"
            elif "左臂" in text:
                self.current_arm = "left"
    
    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_connected:
            try:
                # 这里添加实际的连接逻辑
                # sys.path.append('../../fr3_control')
                # from fairino import Robot
                # if self.current_arm == "right":
                #     self.robot = Robot.RPC('192.168.58.2')
                # elif self.current_arm == "left":
                #     self.robot = Robot.RPC('192.168.58.3')
                
                # 模拟连接成功
                self.is_connected = True
                self.connect_btn.setText("断开")
                self.status_label.setText("已连接")
                self.status_label.setStyleSheet("color: green;")
                self.log_message.emit(f"{self.current_arm}臂连接成功", "SUCCESS")
                
            except Exception as e:
                self.log_message.emit(f"连接失败: {e}", "ERROR")
        else:
            self.is_connected = False
            self.connect_btn.setText("连接")
            self.status_label.setText("未连接")
            self.status_label.setStyleSheet("color: red;")
            self.log_message.emit("机械臂已断开", "INFO")
    
    def set_enable(self, enable):
        """设置使能状态"""
        if not self.is_connected:
            self.log_message.emit("请先连接机械臂", "WARNING")
            return
        
        status = "上使能" if enable else "去使能"
        self.log_message.emit(f"机械臂{status}", "INFO")
        
        # 这里添加实际的使能控制逻辑
        # self.robot.RobotEnable(1 if enable else 0)
    
    def go_home(self):
        """回零"""
        if not self.is_connected:
            self.log_message.emit("请先连接机械臂", "WARNING")
            return
        
        self.log_message.emit("机械臂回零中...", "INFO")
        
        # 这里添加实际的回零逻辑
        # home_pos = [0, -20, -90, -90, 90, 0]
        # self.robot.MoveJ(home_pos, self.speed_slider.value())
    
    def emergency_stop(self):
        """紧急停止"""
        reply = QMessageBox.question(
            self, "紧急停止", "确定要紧急停止机械臂吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_message.emit("机械臂紧急停止", "WARNING")
            # 这里添加紧急停止逻辑
    
    def execute_action(self):
        """执行预定义动作"""
        if not self.is_connected:
            self.log_message.emit("请先连接机械臂", "WARNING")
            return
        
        action = self.action_combo.currentText()
        speed = self.speed_slider.value()
        
        self.log_message.emit(f"执行动作: {action} (速度: {speed}%)", "INFO")
        
        # 这里添加实际的动作执行逻辑
        # action_positions = {
        #     "抓取准备": [0, -45, -90, -45, 90, 0],
        #     "放置准备": [0, -30, -60, -90, 90, 0],
        #     "挥手动作": [0, -20, -45, -90, 45, 0],
        #     "安全位置": [0, -90, -90, -90, 90, 0]
        # }
        # if action in action_positions:
        #     self.robot.MoveJ(action_positions[action], speed)
    
    def start_jog(self, joint, direction):
        """开始关节点动"""
        if not self.is_connected:
            return
        
        speed = self.jog_speed_slider.value()
        dir_text = "正向" if direction > 0 else "负向"
        self.log_message.emit(f"J{joint+1} {dir_text}点动 (速度: {speed}%)", "INFO")
        
        # 这里添加实际的点动逻辑
    
    def stop_jog(self):
        """停止点动"""
        if not self.is_connected:
            return
        
        self.log_message.emit("停止点动", "INFO")
        # 这里添加停止点动逻辑
    
    def execute_coordination(self):
        """执行双臂协调动作"""
        if not self.is_connected:
            self.log_message.emit("请先连接双臂", "WARNING")
            return
        
        action = self.coord_combo.currentText()
        self.log_message.emit(f"执行双臂协调动作: {action}", "INFO")
        
        # 这里添加双臂协调控制逻辑
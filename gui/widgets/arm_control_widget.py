#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂控制控件
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ArmControlWidget(QWidget):
    """机械臂控制控件"""
    
    # 信号定义
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.arm_controllers = {}
        self.current_arm = None
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 机械臂选择
        selection_group = QGroupBox("机械臂选择")
        selection_layout = QHBoxLayout(selection_group)
        
        self.arm_combo = QComboBox()
        self.arm_combo.addItems(["右臂 (192.168.58.2)", "左臂 (192.168.58.3)", "双臂协调"])
        self.arm_combo.currentTextChanged.connect(self.on_arm_changed)
        
        self.connect_btn = QPushButton("🔗 连接")
        self.connect_btn.clicked.connect(self.connect_arm)
        
        self.disconnect_btn = QPushButton("❌ 断开")
        self.disconnect_btn.clicked.connect(self.disconnect_arm)
        self.disconnect_btn.setEnabled(False)
        
        selection_layout.addWidget(QLabel("选择机械臂:"))
        selection_layout.addWidget(self.arm_combo)
        selection_layout.addWidget(self.connect_btn)
        selection_layout.addWidget(self.disconnect_btn)
        selection_layout.addStretch()
        
        layout.addWidget(selection_group)
        
        # 状态显示
        status_group = QGroupBox("机械臂状态")
        status_layout = QGridLayout(status_group)
        
        status_items = [
            ("连接状态:", "connection_status"),
            ("运动状态:", "motion_status"),
            ("模式:", "mode_status"),
            ("使能状态:", "enable_status")
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
        
        # 控制面板
        control_group = QGroupBox("控制面板")
        control_layout = QVBoxLayout(control_group)
        
        # 基本控制
        basic_control = self.create_basic_control()
        control_layout.addWidget(basic_control)
        
        # 预定义动作
        action_control = self.create_action_control()
        control_layout.addWidget(action_control)
        
        # 手动控制
        manual_control = self.create_manual_control()
        control_layout.addWidget(manual_control)
        
        layout.addWidget(control_group)
        
        # 双臂协调控制
        dual_arm_group = QGroupBox("双臂协调控制")
        dual_arm_layout = QVBoxLayout(dual_arm_group)
        
        coord_control = self.create_coordination_control()
        dual_arm_layout.addWidget(coord_control)
        
        layout.addWidget(dual_arm_group)
        
        # 默认隐藏双臂控制
        dual_arm_group.setVisible(False)
        self.dual_arm_group = dual_arm_group
        
    def create_basic_control(self):
        """创建基本控制面板"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # 模式切换
        self.auto_mode_btn = QPushButton("🤖 自动模式")
        self.auto_mode_btn.clicked.connect(lambda: self.set_mode(0))
        
        self.manual_mode_btn = QPushButton("✋ 手动模式")
        self.manual_mode_btn.clicked.connect(lambda: self.set_mode(1))
        
        # 使能控制
        self.enable_btn = QPushButton("⚡ 上使能")
        self.enable_btn.clicked.connect(lambda: self.set_enable(True))
        
        self.disable_btn = QPushButton("🔌 去使能")
        self.disable_btn.clicked.connect(lambda: self.set_enable(False))
        
        # 紧急停止
        self.emergency_stop_btn = QPushButton("🛑 紧急停止")
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        self.emergency_stop_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        
        layout.addWidget(self.auto_mode_btn, 0, 0)
        layout.addWidget(self.manual_mode_btn, 0, 1)
        layout.addWidget(self.enable_btn, 1, 0)
        layout.addWidget(self.disable_btn, 1, 1)
        layout.addWidget(self.emergency_stop_btn, 2, 0, 1, 2)
        
        return widget
    
    def create_action_control(self):
        """创建预定义动作控制"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 动作选择
        action_layout = QHBoxLayout()
        
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "home - 初始位置",
            "pick_ready - 抓取准备",
            "place_ready - 放置准备", 
            "wave - 挥手动作",
            "safe - 安全位置"
        ])
        
        self.execute_action_btn = QPushButton("▶️ 执行动作")
        self.execute_action_btn.clicked.connect(self.execute_predefined_action)
        
        action_layout.addWidget(QLabel("预定义动作:"))
        action_layout.addWidget(self.action_combo)
        action_layout.addWidget(self.execute_action_btn)
        
        layout.addLayout(action_layout)
        
        # 速度设置
        speed_layout = QHBoxLayout()
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(20)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        
        self.speed_label = QLabel("20%")
        
        speed_layout.addWidget(QLabel("运动速度:"))
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        
        layout.addLayout(speed_layout)
        
        return widget
    
    def create_manual_control(self):
        """创建手动控制面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 关节控制
        joint_group = QGroupBox("关节控制")
        joint_layout = QGridLayout(joint_group)
        
        self.joint_controls = []
        joint_names = ["J1", "J2", "J3", "J4", "J5", "J6"]
        
        for i, name in enumerate(joint_names):
            # 关节标签
            label = QLabel(name)
            joint_layout.addWidget(label, i, 0)
            
            # 负方向按钮
            neg_btn = QPushButton("◀")
            neg_btn.pressed.connect(lambda j=i: self.start_jog(j, -1))
            neg_btn.released.connect(self.stop_jog)
            joint_layout.addWidget(neg_btn, i, 1)
            
            # 位置显示
            pos_label = QLabel("0.0°")
            pos_label.setAlignment(Qt.AlignCenter)
            joint_layout.addWidget(pos_label, i, 2)
            
            # 正方向按钮
            pos_btn = QPushButton("▶")
            pos_btn.pressed.connect(lambda j=i: self.start_jog(j, 1))
            pos_btn.released.connect(self.stop_jog)
            joint_layout.addWidget(pos_btn, i, 3)
            
            self.joint_controls.append({
                'neg_btn': neg_btn,
                'pos_btn': pos_btn,
                'pos_label': pos_label
            })
        
        layout.addWidget(joint_group)
        
        # 点动参数
        jog_params_layout = QHBoxLayout()
        
        self.jog_speed_slider = QSlider(Qt.Horizontal)
        self.jog_speed_slider.setRange(1, 50)
        self.jog_speed_slider.setValue(10)
        
        self.jog_speed_label = QLabel("10%")
        self.jog_speed_slider.valueChanged.connect(
            lambda v: self.jog_speed_label.setText(f"{v}%")
        )
        
        jog_params_layout.addWidget(QLabel("点动速度:"))
        jog_params_layout.addWidget(self.jog_speed_slider)
        jog_params_layout.addWidget(self.jog_speed_label)
        
        layout.addLayout(jog_params_layout)
        
        return widget
    
    def create_coordination_control(self):
        """创建双臂协调控制"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 协调动作选择
        coord_layout = QHBoxLayout()
        
        self.coord_combo = QComboBox()
        self.coord_combo.addItems([
            "双臂回零",
            "双臂挥手",
            "协调抓取",
            "协调放置",
            "镜像运动"
        ])
        
        self.execute_coord_btn = QPushButton("🤝 执行协调动作")
        self.execute_coord_btn.clicked.connect(self.execute_coordination_action)
        
        coord_layout.addWidget(QLabel("协调动作:"))
        coord_layout.addWidget(self.coord_combo)
        coord_layout.addWidget(self.execute_coord_btn)
        
        layout.addLayout(coord_layout)
        
        # 单独动作设置
        individual_group = QGroupBox("分别设置动作")
        individual_layout = QGridLayout(individual_group)
        
        # 右臂动作
        self.right_action_combo = QComboBox()
        self.right_action_combo.addItems([
            "home", "pick_ready", "place_ready", "wave"
        ])
        
        # 左臂动作
        self.left_action_combo = QComboBox()
        self.left_action_combo.addItems([
            "home", "pick_ready", "place_ready", "wave"
        ])
        
        self.execute_separate_btn = QPushButton("🎭 执行分别动作")
        self.execute_separate_btn.clicked.connect(self.execute_separate_actions)
        
        individual_layout.addWidget(QLabel("右臂动作:"), 0, 0)
        individual_layout.addWidget(self.right_action_combo, 0, 1)
        individual_layout.addWidget(QLabel("左臂动作:"), 1, 0)
        individual_layout.addWidget(self.left_action_combo, 1, 1)
        individual_layout.addWidget(self.execute_separate_btn, 2, 0, 1, 2)
        
        layout.addWidget(individual_group)
        
        return widget
    
    def on_arm_changed(self, text: str):
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
    
    def connect_arm(self):
        """连接机械臂"""
        if self.current_arm == "dual":
            success = self.connect_dual_arms()
        else:
            success = self.connect_single_arm()
        
        if success:
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.update_status("connection_status", "已连接", "green")
            self.log_message.emit("机械臂连接成功", "SUCCESS")
        else:
            self.log_message.emit("机械臂连接失败", "ERROR")
    
    def connect_single_arm(self) -> bool:
        """连接单个机械臂"""
        try:
            # 导入FR3控制器
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'main_control'))
            from integrated_controller import IntegratedRobotController
            
            # 获取IP地址
            if self.current_arm == "right":
                ip = "192.168.58.2"
            else:
                ip = "192.168.58.3"
            
            # 创建控制器并连接
            # 这里需要根据实际的integrated_controller实现来调整
            self.log_message.emit(f"正在连接{self.current_arm}臂 ({ip})...", "INFO")
            
            # 模拟连接成功（实际实现时需要替换）
            return True
            
        except Exception as e:
            self.log_message.emit(f"连接异常: {e}", "ERROR")
            return False
    
    def connect_dual_arms(self) -> bool:
        """连接双臂"""
        try:
            self.log_message.emit("正在连接双臂系统...", "INFO")
            # 实际连接双臂的代码
            return True
        except Exception as e:
            self.log_message.emit(f"双臂连接异常: {e}", "ERROR")
            return False
    
    def disconnect_arm(self):
        """断开机械臂连接"""
        self.log_message.emit("断开机械臂连接", "INFO")
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.update_status("connection_status", "未连接", "red")
    
    def update_status(self, key: str, text: str, color: str = "black"):
        """更新状态显示"""
        if key in self.status_labels:
            self.status_labels[key].setText(text)
            self.status_labels[key].setStyleSheet(f"color: {color};")
    
    def set_mode(self, mode: int):
        """设置机械臂模式"""
        mode_name = "自动" if mode == 0 else "手动"
        self.log_message.emit(f"切换到{mode_name}模式", "INFO")
        self.update_status("mode_status", f"{mode_name}模式", "blue")
    
    def set_enable(self, enable: bool):
        """设置使能状态"""
        status = "已使能" if enable else "未使能"
        color = "green" if enable else "red"
        self.log_message.emit(f"机械臂{status}", "INFO")
        self.update_status("enable_status", status, color)
    
    def emergency_stop(self):
        """紧急停止"""
        reply = QMessageBox.question(
            self, "紧急停止确认", 
            "确定要执行紧急停止吗？\n这将立即停止所有机械臂运动！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_message.emit("执行紧急停止", "WARNING")
            self.update_status("motion_status", "紧急停止", "red")
    
    def execute_predefined_action(self):
        """执行预定义动作"""
        action_text = self.action_combo.currentText()
        action_name = action_text.split(" - ")[0]
        speed = self.speed_slider.value()
        
        self.log_message.emit(f"执行动作: {action_name} (速度: {speed}%)", "INFO")
        self.update_status("motion_status", f"执行{action_name}", "orange")
        
        # 模拟动作执行
        QTimer.singleShot(3000, lambda: self.update_status("motion_status", "运动完成", "green"))
    
    def on_speed_changed(self, value: int):
        """速度改变"""
        self.speed_label.setText(f"{value}%")
    
    def start_jog(self, joint: int, direction: int):
        """开始点动"""
        dir_text = "正向" if direction > 0 else "负向"
        speed = self.jog_speed_slider.value()
        self.log_message.emit(f"J{joint+1} {dir_text}点动 (速度: {speed}%)", "INFO")
    
    def stop_jog(self):
        """停止点动"""
        self.log_message.emit("停止点动", "INFO")
    
    def execute_coordination_action(self):
        """执行协调动作"""
        action = self.coord_combo.currentText()
        self.log_message.emit(f"执行双臂协调动作: {action}", "INFO")
    
    def execute_separate_actions(self):
        """执行分别动作"""
        right_action = self.right_action_combo.currentText()
        left_action = self.left_action_combo.currentText()
        self.log_message.emit(f"执行分别动作: 右臂-{right_action}, 左臂-{left_action}", "INFO")
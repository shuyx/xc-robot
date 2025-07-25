#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人仿真模块 - RobotSim选项卡
基于VTK+PyQt5的3D机器人仿真界面
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 导入运动学模型
from fr3_kinematics import FR3Kinematics

# VTK导入
try:
    import vtk
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    print("Warning: VTK not available. VTK是可选依赖，如需3D仿真功能:")
    print("pip install -r requirements/simulation_vtk.txt 或使用Web端Three.js方案")

class RobotSimWidget(QWidget):
    """机器人仿真控制界面"""
    
    # 信号定义
    log_message = pyqtSignal(str, str)  # 消息内容, 消息类型
    
    def __init__(self):
        super().__init__()
        self.robot_actors = []  # 存储机器人各部件的VTK actor
        self.joint_angles = [0.0] * 6  # FR3机械臂6个关节角度
        self.model_path = ""
        
        # 初始化运动学模型
        self.kinematics = FR3Kinematics()
        
        # 设定默认初始位姿
        self.default_joint_angles = [0.0, -30.0, 90.0, 0.0, 60.0, 0.0]  # FR3机械臂默认初始位姿
        self.initial_camera_position = None  # 初始相机位置
        self.initial_camera_focal_point = None  # 初始相机焦点
        self.initial_camera_view_up = None  # 初始相机朝向
        
        # 平滑运动控制参数
        self.smooth_motion_enabled = False
        self.target_joint_angles = [0.0] * 6
        self.current_joint_angles = [0.0] * 6
        self.motion_speed = 0.1
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_end_effector_display)
        # 延迟启动定时器，避免在初始化时就开始更新
        
        self.setup_ui()
        
        # 在界面设置完成后再启动定时器
        QTimer.singleShot(1000, lambda: self.update_timer.start(100))
        
    def setup_ui(self):
        """设置界面布局"""
        layout = QHBoxLayout(self)
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel, 1)
        
        # 右侧3D显示区域
        if VTK_AVAILABLE:
            vtk_container = self.create_vtk_container()
            layout.addWidget(vtk_container, 2)
        else:
            placeholder = QLabel("VTK未安装\n请运行: pip install vtk")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("font-size: 16px; color: red;")
            layout.addWidget(placeholder, 2)
    
    def create_control_panel(self):
        """创建左侧控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题
        title = QLabel("🤖 机器人仿真控制")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # 模型加载区域
        model_group = QGroupBox("模型加载")
        model_layout = QVBoxLayout(model_group)
        
        # 模型文件选择
        file_layout = QHBoxLayout()
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("选择STL模型文件...")
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_model_file)
        file_layout.addWidget(self.model_path_edit)
        file_layout.addWidget(browse_btn)
        model_layout.addLayout(file_layout)
        
        # 加载模型按钮
        load_btn = QPushButton("加载模型")
        load_btn.clicked.connect(self.load_model)
        load_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        model_layout.addWidget(load_btn)
        
        layout.addWidget(model_group)
        
        # 关节控制区域
        joint_group = QGroupBox("关节角度控制")
        joint_layout = QVBoxLayout(joint_group)
        
        # 创建6个关节控制滑块
        self.joint_sliders = []
        self.joint_labels = []
        
        for i in range(6):
            # 关节标签和数值显示
            joint_layout_row = QHBoxLayout()
            label = QLabel(f"关节 {i+1}:")
            value_label = QLabel("0.0°")
            joint_layout_row.addWidget(label)
            joint_layout_row.addStretch()
            joint_layout_row.addWidget(value_label)
            joint_layout.addLayout(joint_layout_row)
            
            # 关节角度滑块 (使用运动学模型的限制)
            slider = QSlider(Qt.Horizontal)
            joint_min, joint_max = self.kinematics.joint_limits[i]
            slider.setRange(int(joint_min), int(joint_max))
            slider.setValue(0)
            slider.valueChanged.connect(lambda v, idx=i: self.on_joint_changed(idx, v))
            
            joint_layout.addWidget(slider)
            
            self.joint_sliders.append(slider)
            self.joint_labels.append(value_label)
        
        layout.addWidget(joint_group)
        
        # 预设动作区域
        preset_group = QGroupBox("预设动作")
        preset_layout = QVBoxLayout(preset_group)
        
        # 预设动作按钮
        home_btn = QPushButton("回到原点")
        home_btn.clicked.connect(self.move_to_home)
        preset_layout.addWidget(home_btn)
        
        wave_btn = QPushButton("挥手动作")
        wave_btn.clicked.connect(self.wave_motion)
        preset_layout.addWidget(wave_btn)
        
        layout.addWidget(preset_group)
        
        # 末端位姿控制区域
        endeff_group = QGroupBox("末端位姿控制")
        endeff_layout = QVBoxLayout(endeff_group)
        
        # 当前位姿显示
        current_pose_layout = QGridLayout()
        current_pose_layout.addWidget(QLabel("当前位姿:"), 0, 0, 1, 2)
        
        self.current_pos_labels = []
        for i, axis in enumerate(['X', 'Y', 'Z']):
            label = QLabel(f"{axis}: 0.0 mm")
            current_pose_layout.addWidget(label, 1, i)
            self.current_pos_labels.append(label)
        
        self.current_orient_labels = []
        for i, axis in enumerate(['Roll', 'Pitch', 'Yaw']):
            label = QLabel(f"{axis}: 0.0°")
            current_pose_layout.addWidget(label, 2, i)
            self.current_orient_labels.append(label)
        
        endeff_layout.addLayout(current_pose_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        endeff_layout.addWidget(line)
        
        # 目标位置控制 (X, Y, Z)
        pos_layout = QGridLayout()
        pos_layout.addWidget(QLabel("目标位置 (mm):"), 0, 0)
        
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-1000, 1000)
        self.pos_x_spin.setValue(0)
        self.pos_x_spin.setSuffix(" mm")
        pos_layout.addWidget(QLabel("X:"), 1, 0)
        pos_layout.addWidget(self.pos_x_spin, 1, 1)
        
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-1000, 1000)
        self.pos_y_spin.setValue(0)
        self.pos_y_spin.setSuffix(" mm")
        pos_layout.addWidget(QLabel("Y:"), 2, 0)
        pos_layout.addWidget(self.pos_y_spin, 2, 1)
        
        self.pos_z_spin = QDoubleSpinBox()
        self.pos_z_spin.setRange(-1000, 1000)
        self.pos_z_spin.setValue(400)
        self.pos_z_spin.setSuffix(" mm")
        pos_layout.addWidget(QLabel("Z:"), 3, 0)
        pos_layout.addWidget(self.pos_z_spin, 3, 1)
        
        endeff_layout.addLayout(pos_layout)
        
        # 目标姿态控制 (Roll, Pitch, Yaw)
        orient_layout = QGridLayout()
        orient_layout.addWidget(QLabel("目标姿态 (度):"), 0, 0)
        
        self.roll_spin = QDoubleSpinBox()
        self.roll_spin.setRange(-180, 180)
        self.roll_spin.setValue(0)
        self.roll_spin.setSuffix("°")
        orient_layout.addWidget(QLabel("Roll:"), 1, 0)
        orient_layout.addWidget(self.roll_spin, 1, 1)
        
        self.pitch_spin = QDoubleSpinBox()
        self.pitch_spin.setRange(-180, 180)
        self.pitch_spin.setValue(0)
        self.pitch_spin.setSuffix("°")
        orient_layout.addWidget(QLabel("Pitch:"), 2, 0)
        orient_layout.addWidget(self.pitch_spin, 2, 1)
        
        self.yaw_spin = QDoubleSpinBox()
        self.yaw_spin.setRange(-180, 180)
        self.yaw_spin.setValue(0)
        self.yaw_spin.setSuffix("°")
        orient_layout.addWidget(QLabel("Yaw:"), 3, 0)
        orient_layout.addWidget(self.yaw_spin, 3, 1)
        
        endeff_layout.addLayout(orient_layout)
        
        # 末端位姿控制按钮
        move_endeff_btn = QPushButton("移动到目标位姿")
        move_endeff_btn.clicked.connect(self.move_to_pose)
        move_endeff_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; }")
        endeff_layout.addWidget(move_endeff_btn)
        
        layout.addWidget(endeff_group)
        
        # 弹簧撑开
        layout.addStretch()
        
        return panel
    
    def create_vtk_container(self):
        """创建VTK容器，包含按钮和3D显示区域"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(5, 2, 5, 2)
        
        # 回到初始位姿按钮
        reset_view_btn = QPushButton("回到初始位姿")
        reset_view_btn.setFlat(True)
        reset_view_btn.setMaximumHeight(25)
        reset_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        reset_view_btn.clicked.connect(self.reset_to_initial_pose)
        
        button_layout.addWidget(reset_view_btn)
        button_layout.addStretch()
        
        # 添加按钮布局
        layout.addLayout(button_layout)
        
        # 创建3D显示区域
        self.vtk_widget = self.create_vtk_widget()
        layout.addWidget(self.vtk_widget)
        
        return container
    
    def create_vtk_widget(self):
        """创建VTK 3D显示区域"""
        if not VTK_AVAILABLE:
            return QLabel("VTK不可用")
        
        # 创建VTK交互窗口
        vtk_widget = QVTKRenderWindowInteractor(self)
        
        # 创建渲染器
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.9, 0.9, 0.95)  # 浅灰蓝色背景
        
        # 创建渲染窗口
        self.render_window = vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        
        # 创建交互器
        self.interactor = vtk_widget.GetRenderWindow().GetInteractor()
        
        # 添加坐标轴
        self.add_coordinate_axes()
        
        # 添加网格
        self.add_grid()
        
        # 初始化交互器
        self.interactor.Initialize()
        
        # 设置初始相机位姿
        self.set_initial_camera_pose()
        
        return vtk_widget
    
    def add_coordinate_axes(self):
        """添加带标注的坐标轴指示器到右上角"""
        if not VTK_AVAILABLE:
            return
        
        # 创建自定义的坐标轴组装体
        axes_assembly = vtk.vtkAssembly()
        
        # 创建三个轴线
        # X轴 (红色)
        x_source = vtk.vtkLineSource()
        x_source.SetPoint1(0, 0, 0)
        x_source.SetPoint2(1.2, 0, 0)  # 稍微长一些为标签留空间
        x_mapper = vtk.vtkPolyDataMapper()
        x_mapper.SetInputConnection(x_source.GetOutputPort())
        x_actor = vtk.vtkActor()
        x_actor.SetMapper(x_mapper)
        x_actor.GetProperty().SetColor(0.8, 0.2, 0.2)  # 红色
        x_actor.GetProperty().SetLineWidth(4)
        
        # Y轴 (绿色)
        y_source = vtk.vtkLineSource()
        y_source.SetPoint1(0, 0, 0)
        y_source.SetPoint2(0, 1.2, 0)
        y_mapper = vtk.vtkPolyDataMapper()
        y_mapper.SetInputConnection(y_source.GetOutputPort())
        y_actor = vtk.vtkActor()
        y_actor.SetMapper(y_mapper)
        y_actor.GetProperty().SetColor(0.2, 0.8, 0.2)  # 绿色
        y_actor.GetProperty().SetLineWidth(4)
        
        # Z轴 (蓝色)
        z_source = vtk.vtkLineSource()
        z_source.SetPoint1(0, 0, 0)
        z_source.SetPoint2(0, 0, 1.2)
        z_mapper = vtk.vtkPolyDataMapper()
        z_mapper.SetInputConnection(z_source.GetOutputPort())
        z_actor = vtk.vtkActor()
        z_actor.SetMapper(z_mapper)
        z_actor.GetProperty().SetColor(0.2, 0.2, 0.8)  # 蓝色
        z_actor.GetProperty().SetLineWidth(4)
        
        # 创建文字标注
        # X标签
        x_text = vtk.vtkVectorText()
        x_text.SetText("X")
        x_text_mapper = vtk.vtkPolyDataMapper()
        x_text_mapper.SetInputConnection(x_text.GetOutputPort())
        x_text_actor = vtk.vtkActor()
        x_text_actor.SetMapper(x_text_mapper)
        x_text_actor.SetPosition(1.3, 0, 0)
        x_text_actor.SetScale(0.15, 0.15, 0.15)
        x_text_actor.GetProperty().SetColor(0.8, 0.2, 0.2)
        
        # Y标签
        y_text = vtk.vtkVectorText()
        y_text.SetText("Y")
        y_text_mapper = vtk.vtkPolyDataMapper()
        y_text_mapper.SetInputConnection(y_text.GetOutputPort())
        y_text_actor = vtk.vtkActor()
        y_text_actor.SetMapper(y_text_mapper)
        y_text_actor.SetPosition(0, 1.3, 0)
        y_text_actor.SetScale(0.15, 0.15, 0.15)
        y_text_actor.GetProperty().SetColor(0.2, 0.8, 0.2)
        
        # Z标签
        z_text = vtk.vtkVectorText()
        z_text.SetText("Z")
        z_text_mapper = vtk.vtkPolyDataMapper()
        z_text_mapper.SetInputConnection(z_text.GetOutputPort())
        z_text_actor = vtk.vtkActor()
        z_text_actor.SetMapper(z_text_mapper)
        z_text_actor.SetPosition(0, 0, 1.3)
        z_text_actor.SetScale(0.15, 0.15, 0.15)
        z_text_actor.GetProperty().SetColor(0.2, 0.2, 0.8)
        
        # 添加所有元素到组装体
        axes_assembly.AddPart(x_actor)
        axes_assembly.AddPart(y_actor)
        axes_assembly.AddPart(z_actor)
        axes_assembly.AddPart(x_text_actor)
        axes_assembly.AddPart(y_text_actor)
        axes_assembly.AddPart(z_text_actor)
        
        # 创建方向标记小部件
        self.orientation_marker = vtk.vtkOrientationMarkerWidget()
        self.orientation_marker.SetOrientationMarker(axes_assembly)
        self.orientation_marker.SetInteractor(self.interactor)
        
        # 设置位置到右上角
        self.orientation_marker.SetViewport(0.75, 0.75, 1.0, 1.0)  # 右上角 25% 区域
        self.orientation_marker.SetEnabled(True)
        self.orientation_marker.InteractiveOff()  # 禁用交互，只作为指示器
    
    def add_grid(self):
        """添加网格"""
        if not VTK_AVAILABLE:
            return
        
        # 创建网格平面
        plane = vtk.vtkPlaneSource()
        plane.SetResolution(10, 10)
        plane.SetOrigin(-500, -500, 0)
        plane.SetPoint1(500, -500, 0)
        plane.SetPoint2(-500, 500, 0)
        
        # 创建网格映射器
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())
        
        # 创建网格演员
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor.GetProperty().SetOpacity(0.3)
        
        # 添加到渲染器
        self.renderer.AddActor(actor)
    
    def browse_model_file(self):
        """浏览模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择STL模型文件", 
            "/Users/shushu/Library/CloudStorage/Dropbox/xc-robot/models", 
            "STL Files (*.stl);;All Files (*)"
        )
        if file_path:
            self.model_path_edit.setText(file_path)
            self.model_path = file_path
    
    def load_model(self):
        """加载STL模型"""
        if not VTK_AVAILABLE:
            self.log_message.emit("VTK未安装，无法加载模型", "ERROR")
            return
        
        model_path = self.model_path_edit.text()
        if not model_path or not os.path.exists(model_path):
            self.log_message.emit("请选择有效的STL模型文件", "ERROR")
            return
        
        try:
            # 读取STL文件
            reader = vtk.vtkSTLReader()
            reader.SetFileName(model_path)
            reader.Update()
            
            # 创建映射器
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            
            # 创建演员
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0.8, 0.8, 0.8)  # 灰色
            actor.GetProperty().SetSpecular(0.3)
            actor.GetProperty().SetSpecularPower(60)
            
            # 清除之前的模型
            for old_actor in self.robot_actors:
                self.renderer.RemoveActor(old_actor)
            self.robot_actors.clear()
            
            # 添加新模型
            self.robot_actors.append(actor)
            self.renderer.AddActor(actor)
            
            # 调整视角
            self.renderer.ResetCamera()
            self.render_window.Render()
            
            self.log_message.emit(f"成功加载模型: {os.path.basename(model_path)}", "SUCCESS")
            
        except Exception as e:
            self.log_message.emit(f"加载模型失败: {str(e)}", "ERROR")
    
    def on_joint_changed(self, joint_index, value):
        """关节角度改变处理"""
        angle = value  # 角度值
        self.joint_angles[joint_index] = angle
        
        # 更新运动学模型
        self.kinematics.set_joint_angles(self.joint_angles)
        
        # 更新标签显示
        self.joint_labels[joint_index].setText(f"{angle:.1f}°")
        
        # 更新3D模型 (这里需要实现关节变换)
        self.update_robot_pose()
        
        self.log_message.emit(f"关节{joint_index+1}角度: {angle:.1f}°", "INFO")
    
    def update_robot_pose(self):
        """更新机器人姿态"""
        if not VTK_AVAILABLE or not self.robot_actors:
            return
        
        # 这里需要实现运动学变换
        # 暂时只是简单的旋转示例
        for i, actor in enumerate(self.robot_actors):
            if i < len(self.joint_angles):
                transform = vtk.vtkTransform()
                transform.RotateZ(self.joint_angles[i])
                actor.SetUserTransform(transform)
        
        self.render_window.Render()
    
    def move_to_home(self):
        """移动到原点位置"""
        for i, slider in enumerate(self.joint_sliders):
            slider.setValue(0)
        
        self.log_message.emit("机械臂回到原点位置", "INFO")
    
    def wave_motion(self):
        """挥手动作"""
        # 简单的挥手动作序列
        wave_sequence = [
            [0, -30, 90, 0, 90, 0],   # 抬起手臂
            [0, -30, 90, 0, 45, 0],   # 挥手1
            [0, -30, 90, 0, 90, 0],   # 挥手2
            [0, -30, 90, 0, 45, 0],   # 挥手3
            [0, 0, 0, 0, 0, 0]        # 回到原点
        ]
        
        # 创建动作定时器
        self.motion_timer = QTimer()
        self.motion_step = 0
        self.motion_sequence = wave_sequence
        
        def execute_motion():
            if self.motion_step < len(self.motion_sequence):
                angles = self.motion_sequence[self.motion_step]
                for i, angle in enumerate(angles):
                    self.joint_sliders[i].setValue(angle)
                self.motion_step += 1
            else:
                self.motion_timer.stop()
                self.log_message.emit("挥手动作完成", "SUCCESS")
        
        self.motion_timer.timeout.connect(execute_motion)
        self.motion_timer.start(1000)  # 1秒间隔
        
        self.log_message.emit("开始执行挥手动作", "INFO")
    
    def move_to_pose(self):
        """移动到目标位姿"""
        # 获取目标位姿
        target_pos = [
            self.pos_x_spin.value(),
            self.pos_y_spin.value(),
            self.pos_z_spin.value()
        ]
        target_orient = [
            self.roll_spin.value(),
            self.pitch_spin.value(),
            self.yaw_spin.value()
        ]
        
        self.log_message.emit(
            f"目标位置: ({target_pos[0]:.1f}, {target_pos[1]:.1f}, {target_pos[2]:.1f})", 
            "INFO"
        )
        self.log_message.emit(
            f"目标姿态: ({target_orient[0]:.1f}°, {target_orient[1]:.1f}°, {target_orient[2]:.1f}°)", 
            "INFO"
        )
        
        try:
            # 调用逆运动学求解器
            joint_angles = self.kinematics.inverse_kinematics(target_pos, target_orient)
            
            # 更新滑块位置
            for i, angle in enumerate(joint_angles):
                self.joint_sliders[i].setValue(int(angle))
            
            self.log_message.emit("逆运动学求解完成", "SUCCESS")
            
        except Exception as e:
            self.log_message.emit(f"逆运动学求解失败: {str(e)}", "ERROR")
    
    def update_end_effector_display(self):
        """更新末端执行器位姿显示"""
        try:
            # 检查必要的属性是否存在
            if not hasattr(self, 'kinematics') or not hasattr(self, 'current_pos_labels'):
                return
                
            # 获取当前末端位姿
            current_pose = self.kinematics.get_end_effector_pose()
            
            # 更新位置显示
            pos = current_pose['position']
            for i, axis in enumerate(['X', 'Y', 'Z']):
                if i < len(self.current_pos_labels):
                    self.current_pos_labels[i].setText(f"{axis}: {pos[i]:.1f} mm")
            
            # 更新姿态显示
            orient = current_pose['orientation']
            for i, axis in enumerate(['Roll', 'Pitch', 'Yaw']):
                if i < len(self.current_orient_labels):
                    self.current_orient_labels[i].setText(f"{axis}: {orient[i]:.1f}°")
                
        except Exception as e:
            # 静默处理，避免过多错误信息
            pass
    
    def set_initial_camera_pose(self):
        """设置初始相机位姿"""
        if not VTK_AVAILABLE or not hasattr(self, 'renderer'):
            return
        
        camera = self.renderer.GetActiveCamera()
        
        # 设置初始相机位置和角度，适合观察机械臂
        camera.SetPosition(500, -800, 400)  # 相机位置
        camera.SetFocalPoint(0, 0, 200)     # 焦点位置
        camera.SetViewUp(0, 0, 1)           # 上方向
        
        # 保存初始位姿
        self.initial_camera_position = camera.GetPosition()
        self.initial_camera_focal_point = camera.GetFocalPoint()
        self.initial_camera_view_up = camera.GetViewUp()
        
        self.renderer.ResetCameraClippingRange()
    
    def reset_to_initial_pose(self):
        """回到初始位姿"""
        if not VTK_AVAILABLE:
            return
        
        # 重置关节角度到默认位姿
        for i, angle in enumerate(self.default_joint_angles):
            if i < len(self.joint_sliders):
                self.joint_sliders[i].setValue(int(angle))
        
        # 重置相机位姿
        if (self.initial_camera_position and 
            self.initial_camera_focal_point and 
            self.initial_camera_view_up):
            
            camera = self.renderer.GetActiveCamera()
            camera.SetPosition(self.initial_camera_position)
            camera.SetFocalPoint(self.initial_camera_focal_point)
            camera.SetViewUp(self.initial_camera_view_up)
            
            self.renderer.ResetCameraClippingRange()
            self.render_window.Render()
        
        self.log_message.emit("已回到初始位姿", "SUCCESS")
    
    def emergency_stop(self):
        """紧急停止"""
        # 停止所有运动
        if hasattr(self, 'motion_timer'):
            self.motion_timer.stop()
        
        self.log_message.emit("仿真系统紧急停止", "WARNING")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止更新定时器
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            
            # 停止动作定时器
            if hasattr(self, 'motion_timer'):
                self.motion_timer.stop()
            
            # 清理VTK资源
            if VTK_AVAILABLE and hasattr(self, 'orientation_marker'):
                self.orientation_marker.SetEnabled(False)
            
            if VTK_AVAILABLE and hasattr(self, 'interactor'):
                try:
                    self.interactor.TerminateApp()
                except:
                    pass
            
            if VTK_AVAILABLE and hasattr(self, 'render_window'):
                try:
                    self.render_window.Finalize()
                except:
                    pass
                    
        except Exception as e:
            print(f"清理资源时出错: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.cleanup()
        super().closeEvent(event)
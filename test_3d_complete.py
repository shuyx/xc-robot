#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的3D显示和运动学测试
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui', 'widgets'))

from robot_3d_widget import Robot3DWidget
from fr3_kinematics_3d import FR3RobotModel, integrate_fr3_kinematics

class Complete3DTestWindow(QMainWindow):
    """完整的3D测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FR3机器人3D仿真测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # 左侧：3D显示
        self.robot_3d = Robot3DWidget()
        layout.addWidget(self.robot_3d, 3)
        
        # 右侧：控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel, 1)
        
        # 创建示例机器人
        if hasattr(self.robot_3d, 'vtk_widget'):
            self.robot_3d.create_example_robot()
            
        # 集成运动学
        self.update_display, self.fr3_model = integrate_fr3_kinematics(self.robot_3d)
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_time = 0
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = QGroupBox("控制面板")
        layout = QVBoxLayout(panel)
        
        # 标题
        title = QLabel("关节角度控制")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # 关节滑块
        self.joint_sliders = []
        for i in range(6):
            joint_group = QGroupBox(f"关节 {i+1}")
            joint_layout = QHBoxLayout(joint_group)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-180, 180)
            slider.setValue(0)
            slider.valueChanged.connect(self.update_joint_angles)
            
            label = QLabel("0°")
            label.setMinimumWidth(40)
            
            joint_layout.addWidget(slider)
            joint_layout.addWidget(label)
            
            self.joint_sliders.append((slider, label))
            layout.addWidget(joint_group)
            
        # 设置默认姿态
        default_angles = [0, -30, -60, -90, 0, 0]
        for i, angle in enumerate(default_angles):
            self.joint_sliders[i][0].setValue(angle)
            
        # 动画控制
        animation_group = QGroupBox("动画控制")
        animation_layout = QVBoxLayout(animation_group)
        
        self.play_button = QPushButton("播放动画")
        self.play_button.clicked.connect(self.toggle_animation)
        animation_layout.addWidget(self.play_button)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        speed_label = QLabel("速度: 50%")
        self.speed_slider.valueChanged.connect(
            lambda v: speed_label.setText(f"速度: {v}%")
        )
        animation_layout.addWidget(speed_label)
        animation_layout.addWidget(self.speed_slider)
        
        layout.addWidget(animation_group)
        
        # 信息显示
        info_group = QGroupBox("末端执行器信息")
        info_layout = QVBoxLayout(info_group)
        
        self.pos_label = QLabel("位置: X=0, Y=0, Z=0")
        self.rot_label = QLabel("姿态: RX=0°, RY=0°, RZ=0°")
        
        info_layout.addWidget(self.pos_label)
        info_layout.addWidget(self.rot_label)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        return panel
        
    def update_joint_angles(self):
        """更新关节角度"""
        angles = []
        for slider, label in self.joint_sliders:
            angle = slider.value()
            angles.append(angle)
            label.setText(f"{angle}°")
            
        # 更新3D显示
        self.robot_3d.update_joint_angles(angles)
        
        # 更新运动学模型
        if hasattr(self, 'fr3_model'):
            self.fr3_model.update_joints(angles)
            
            # 获取末端执行器位姿
            try:
                pos, rot = self.fr3_model.get_end_effector_pose()
                self.pos_label.setText(f"位置: X={pos[0]:.1f}, Y={pos[1]:.1f}, Z={pos[2]:.1f}")
                self.rot_label.setText(f"姿态: RX={rot[0]:.1f}°, RY={rot[1]:.1f}°, RZ={rot[2]:.1f}°")
            except:
                pass
                
    def toggle_animation(self):
        """切换动画播放"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.play_button.setText("播放动画")
        else:
            self.animation_timer.start(50)  # 20 FPS
            self.play_button.setText("停止动画")
            
    def update_animation(self):
        """更新动画"""
        speed = self.speed_slider.value() / 100.0
        self.animation_time += 0.05 * speed
        
        # 生成动画轨迹
        angles = []
        for i in range(6):
            if i == 0:  # 基座旋转
                angle = 30 * np.sin(self.animation_time)
            elif i == 1:  # 肩部
                angle = -30 + 20 * np.sin(self.animation_time * 0.8)
            elif i == 2:  # 肘部
                angle = -60 + 30 * np.sin(self.animation_time * 0.6)
            else:
                angle = 0
                
            angles.append(angle)
            self.joint_sliders[i][0].setValue(int(angle))
            
            
class SimpleVTKTest(QMainWindow):
    """简单的VTK测试"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VTK简单测试")
        self.setGeometry(100, 100, 800, 600)
        
        try:
            import vtk
            from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
            
            # 创建VTK控件
            vtk_widget = QVTKRenderWindowInteractor(self)
            self.setCentralWidget(vtk_widget)
            
            # 创建渲染器
            renderer = vtk.vtkRenderer()
            renderer.SetBackground(0.1, 0.2, 0.3)
            vtk_widget.GetRenderWindow().AddRenderer(renderer)
            
            # 创建一个立方体
            cube = vtk.vtkCubeSource()
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(cube.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1, 0.5, 0)
            
            renderer.AddActor(actor)
            
            # 重置相机
            renderer.ResetCamera()
            
            # 启动交互
            vtk_widget.GetRenderWindow().Render()
            vtk_widget.GetRenderWindow().GetInteractor().Start()
            
            self.statusBar().showMessage("VTK测试成功！")
            
        except Exception as e:
            label = QLabel(f"VTK测试失败:\n{str(e)}")
            label.setAlignment(Qt.AlignCenter)
            self.setCentralWidget(label)


def test_kinematics():
    """测试运动学计算"""
    print("=" * 50)
    print("FR3运动学测试")
    print("=" * 50)
    
    from fr3_kinematics_3d import FR3RobotModel
    
    # 创建模型
    model = FR3RobotModel()
    
    # 测试正向运动学
    test_angles = [0, -30, -60, -90, 0, 0]
    print(f"\n测试关节角度: {test_angles}")
    
    model.update_joints(test_angles)
    positions = model.get_joint_positions()
    
    print("\n各关节位置:")
    for i, pos in enumerate(positions):
        print(f"  关节{i}: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}] mm")
        
    # 获取末端位姿
    pos, rot = model.get_end_effector_pose()
    print(f"\n末端执行器:")
    print(f"  位置: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}] mm")
    print(f"  姿态: [{rot[0]:.1f}, {rot[1]:.1f}, {rot[2]:.1f}] 度")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="3D显示测试")
    parser.add_argument('--mode', choices=['simple', 'complete', 'kinematics'], 
                       default='complete', help='测试模式')
    args = parser.parse_args()
    
    if args.mode == 'kinematics':
        # 纯运动学测试
        test_kinematics()
    else:
        # GUI测试
        app = QApplication(sys.argv)
        
        if args.mode == 'simple':
            window = SimpleVTKTest()
        else:
            window = Complete3DTestWindow()
            
        window.show()
        sys.exit(app.exec_())
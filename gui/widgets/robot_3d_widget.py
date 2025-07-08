#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D机器人模型显示控件 - 基于VTK
"""

import sys
import os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

try:
    import vtk
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    print("VTK未安装，请运行: pip install vtk")

class Robot3DWidget(QWidget):
    """3D机器人模型显示控件"""
    
    log_message = pyqtSignal(str, str)  # 日志信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.robot_parts = {}  # 存储机器人各部件
        self.joint_transforms = {}  # 存储关节变换
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        if not VTK_AVAILABLE:
            # VTK未安装时显示提示
            info_label = QLabel("VTK未安装\n请运行: pip install vtk")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #666;
                    padding: 20px;
                    background-color: #f0f0f0;
                    border-radius: 5px;
                }
            """)
            layout.addWidget(info_label)
            return
        
        # 创建VTK渲染窗口
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)
        
        # 设置渲染器
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.9, 0.9, 0.9)  # 浅灰色背景
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # 设置相机
        self.setup_camera()
        
        # 设置灯光
        self.setup_lights()
        
        # 添加坐标轴
        self.add_coordinate_axes()
        
        # 启动交互器
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        
    def setup_camera(self):
        """设置相机"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(1000, -1000, 800)
        camera.SetFocalPoint(0, 0, 300)
        camera.SetViewUp(0, 0, 1)
        
    def setup_lights(self):
        """设置灯光"""
        # 主光源
        light1 = vtk.vtkLight()
        light1.SetPosition(1000, 1000, 1000)
        light1.SetFocalPoint(0, 0, 0)
        light1.SetColor(1, 1, 1)
        light1.SetIntensity(0.8)
        self.renderer.AddLight(light1)
        
        # 辅助光源
        light2 = vtk.vtkLight()
        light2.SetPosition(-1000, -1000, 500)
        light2.SetFocalPoint(0, 0, 0)
        light2.SetColor(0.8, 0.8, 0.8)
        light2.SetIntensity(0.5)
        self.renderer.AddLight(light2)
        
    def add_coordinate_axes(self):
        """添加坐标轴"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(200, 200, 200)
        axes.SetShaftType(0)
        axes.SetCylinderRadius(0.02)
        axes.SetConeRadius(0.05)
        
        # 设置标签
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        
        self.renderer.AddActor(axes)
        
    def load_stl_model(self, filename, part_name):
        """加载STL模型文件"""
        if not os.path.exists(filename):
            self.log_message.emit(f"文件不存在: {filename}", "ERROR")
            return None
            
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        
        # 创建mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        # 创建actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        # 存储部件
        self.robot_parts[part_name] = {
            'actor': actor,
            'transform': vtk.vtkTransform()
        }
        
        actor.SetUserTransform(self.robot_parts[part_name]['transform'])
        self.renderer.AddActor(actor)
        
        self.log_message.emit(f"加载模型: {part_name}", "SUCCESS")
        return actor
        
    def create_robot_structure(self):
        """创建机器人结构（示例）"""
        # 这里可以加载各个部件的STL文件
        # 例如：
        # self.load_stl_model("models/base.stl", "base")
        # self.load_stl_model("models/link1.stl", "link1")
        # self.load_stl_model("models/link2.stl", "link2")
        # ...
        
        # 创建简单的示例几何体
        self.create_example_robot()
        
    def create_example_robot(self):
        """创建示例机器人（使用基本几何体）"""
        # 基座
        base = self.create_cylinder(100, 50, "base")
        base.GetProperty().SetColor(0.5, 0.5, 0.5)
        
        # 连杆1
        link1 = self.create_box(40, 40, 200, "link1")
        link1.GetProperty().SetColor(0.6, 0.6, 0.8)
        self.robot_parts["link1"]['transform'].Translate(0, 0, 50)
        
        # 连杆2
        link2 = self.create_box(30, 30, 150, "link2")
        link2.GetProperty().SetColor(0.8, 0.6, 0.6)
        self.robot_parts["link2"]['transform'].Translate(0, 0, 250)
        
        self.vtk_widget.GetRenderWindow().Render()
        
    def create_box(self, x, y, z, name):
        """创建长方体"""
        cube = vtk.vtkCubeSource()
        cube.SetXLength(x)
        cube.SetYLength(y)
        cube.SetZLength(z)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        self.robot_parts[name] = {
            'actor': actor,
            'transform': vtk.vtkTransform()
        }
        
        actor.SetUserTransform(self.robot_parts[name]['transform'])
        self.renderer.AddActor(actor)
        
        return actor
        
    def create_cylinder(self, radius, height, name):
        """创建圆柱体"""
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetRadius(radius)
        cylinder.SetHeight(height)
        cylinder.SetResolution(32)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cylinder.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        self.robot_parts[name] = {
            'actor': actor,
            'transform': vtk.vtkTransform()
        }
        
        actor.SetUserTransform(self.robot_parts[name]['transform'])
        self.renderer.AddActor(actor)
        
        return actor
        
    def update_joint_angles(self, joint_angles):
        """更新关节角度"""
        # 这里实现关节角度到变换矩阵的转换
        # 结合FR3的运动学模型
        
        # 示例：更新第一个关节
        if "link1" in self.robot_parts and len(joint_angles) > 0:
            transform = self.robot_parts["link1"]['transform']
            transform.Identity()
            transform.Translate(0, 0, 50)
            transform.RotateZ(joint_angles[0])
            
        # 更新第二个关节
        if "link2" in self.robot_parts and len(joint_angles) > 1:
            transform = self.robot_parts["link2"]['transform']
            transform.Identity()
            transform.Translate(0, 0, 250)
            transform.RotateY(joint_angles[1])
            
        self.vtk_widget.GetRenderWindow().Render()
        
    def reset_camera(self):
        """重置相机视角"""
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def set_background_color(self, r, g, b):
        """设置背景颜色"""
        self.renderer.SetBackground(r, g, b)
        self.vtk_widget.GetRenderWindow().Render()


# 测试窗口
class Test3DWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D机器人模型测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建3D控件
        self.robot_3d = Robot3DWidget()
        self.setCentralWidget(self.robot_3d)
        
        # 创建菜单
        self.create_menus()
        
        # 创建示例机器人
        if VTK_AVAILABLE:
            self.robot_3d.create_example_robot()
            
    def create_menus(self):
        """创建菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        load_action = QAction('加载STL模型', self)
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        reset_action = QAction('重置视角', self)
        reset_action.triggered.connect(self.robot_3d.reset_camera)
        view_menu.addAction(reset_action)
        
    def load_model(self):
        """加载模型文件"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择STL文件", "", "STL Files (*.stl);;All Files (*)"
        )
        if filename:
            self.robot_3d.load_stl_model(filename, "imported_model")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Test3DWindow()
    window.show()
    sys.exit(app.exec_())
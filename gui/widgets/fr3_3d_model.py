#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR3机械臂3D模型 - 简化版本
"""

import vtk
import numpy as np
from PyQt5.QtCore import pyqtSignal

class FR3Arm3D:
    """FR3机械臂3D模型"""
    
    def __init__(self, renderer, side="left"):
        self.renderer = renderer
        self.side = side
        self.parts = {}
        self.transforms = {}
        self.joint_angles = [0, 0, 0, 0, 0, 0]
        
        # FR3尺寸参数（mm）
        self.dimensions = {
            'base_radius': 60,
            'base_height': 100,
            'link1_size': [80, 80, 140],
            'link2_size': [60, 60, 280],
            'link3_size': [50, 50, 60],
            'link4_size': [40, 40, 240],
            'link5_size': [35, 35, 60],
            'link6_size': [30, 30, 100],
            'gripper_size': [60, 40, 80]
        }
        
        # 关节偏移
        self.joint_offsets = {
            'joint1': [0, 0, 50],        # 基座顶部
            'joint2': [0, 0, 70],        # Link1顶部
            'joint3': [0, 0, 140],       # Link2中部
            'joint4': [0, 0, 30],        # Link3顶部
            'joint5': [0, 0, 120],       # Link4中部
            'joint6': [0, 0, 30],        # Link5顶部
            'gripper': [0, 0, 50]        # Link6顶部
        }
        
        # 颜色设置
        if side == "left":
            self.base_color = [0.3, 0.5, 0.8]    # 蓝色系
            self.link_color = [0.4, 0.6, 0.9]
        else:
            self.base_color = [0.8, 0.3, 0.3]    # 红色系
            self.link_color = [0.9, 0.4, 0.4]
            
        self.create_robot()
        
    def create_cylinder(self, radius, height, name):
        """创建圆柱体"""
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetRadius(radius)
        cylinder.SetHeight(height)
        cylinder.SetResolution(32)
        
        # 创建变换使圆柱体垂直
        transform = vtk.vtkTransform()
        transform.RotateX(90)  # 默认圆柱体是水平的，旋转90度使其垂直
        
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(cylinder.GetOutputPort())
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transformFilter.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        return actor
        
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
        
        return actor
        
    def create_robot(self):
        """创建机器人模型"""
        # 基座
        base = self.create_cylinder(
            self.dimensions['base_radius'],
            self.dimensions['base_height'],
            "base"
        )
        base.GetProperty().SetColor(*self.base_color)
        self.parts['base'] = base
        self.transforms['base'] = vtk.vtkTransform()
        base.SetUserTransform(self.transforms['base'])
        self.renderer.AddActor(base)
        
        # Link1
        link1 = self.create_box(*self.dimensions['link1_size'], "link1")
        link1.GetProperty().SetColor(*self.link_color)
        self.parts['link1'] = link1
        self.transforms['link1'] = vtk.vtkTransform()
        link1.SetUserTransform(self.transforms['link1'])
        self.renderer.AddActor(link1)
        
        # Link2
        link2 = self.create_box(*self.dimensions['link2_size'], "link2")
        link2.GetProperty().SetColor(*[c * 0.9 for c in self.link_color])
        self.parts['link2'] = link2
        self.transforms['link2'] = vtk.vtkTransform()
        link2.SetUserTransform(self.transforms['link2'])
        self.renderer.AddActor(link2)
        
        # Link3
        link3 = self.create_box(*self.dimensions['link3_size'], "link3")
        link3.GetProperty().SetColor(*self.link_color)
        self.parts['link3'] = link3
        self.transforms['link3'] = vtk.vtkTransform()
        link3.SetUserTransform(self.transforms['link3'])
        self.renderer.AddActor(link3)
        
        # Link4
        link4 = self.create_box(*self.dimensions['link4_size'], "link4")
        link4.GetProperty().SetColor(*[c * 0.9 for c in self.link_color])
        self.parts['link4'] = link4
        self.transforms['link4'] = vtk.vtkTransform()
        link4.SetUserTransform(self.transforms['link4'])
        self.renderer.AddActor(link4)
        
        # Link5
        link5 = self.create_box(*self.dimensions['link5_size'], "link5")
        link5.GetProperty().SetColor(*self.link_color)
        self.parts['link5'] = link5
        self.transforms['link5'] = vtk.vtkTransform()
        link5.SetUserTransform(self.transforms['link5'])
        self.renderer.AddActor(link5)
        
        # Link6
        link6 = self.create_box(*self.dimensions['link6_size'], "link6")
        link6.GetProperty().SetColor(*[c * 0.9 for c in self.link_color])
        self.parts['link6'] = link6
        self.transforms['link6'] = vtk.vtkTransform()
        link6.SetUserTransform(self.transforms['link6'])
        self.renderer.AddActor(link6)
        
        # 夹爪
        gripper = self.create_box(*self.dimensions['gripper_size'], "gripper")
        gripper.GetProperty().SetColor(0.8, 0.8, 0.2)  # 黄色
        self.parts['gripper'] = gripper
        self.transforms['gripper'] = vtk.vtkTransform()
        gripper.SetUserTransform(self.transforms['gripper'])
        self.renderer.AddActor(gripper)
        
        # 添加关节球（可视化关节位置）
        self.create_joint_markers()
        
    def create_joint_markers(self):
        """创建关节标记球"""
        for i in range(6):
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(10)
            sphere.SetPhiResolution(16)
            sphere.SetThetaResolution(16)
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1, 1, 0)  # 黄色
            
            self.parts[f'joint{i+1}_marker'] = actor
            self.transforms[f'joint{i+1}_marker'] = vtk.vtkTransform()
            actor.SetUserTransform(self.transforms[f'joint{i+1}_marker'])
            self.renderer.AddActor(actor)
            
    def update_joints(self, angles):
        """更新关节角度（度）"""
        self.joint_angles = angles
        
        # 基座位置（如果是左臂在左边，右臂在右边）
        base_x = -190 if self.side == "left" else 190
        
        # 基座变换
        self.transforms['base'].Identity()
        self.transforms['base'].Translate(base_x, 0, 0)
        
        # Joint1 - 基座旋转（绕Z轴）
        t1 = vtk.vtkTransform()
        t1.SetInput(self.transforms['base'])
        t1.Translate(*self.joint_offsets['joint1'])
        t1.RotateZ(angles[0])
        self.transforms['link1'] = t1
        self.parts['link1'].SetUserTransform(t1)
        
        # Joint1标记
        if 'joint1_marker' in self.transforms:
            self.transforms['joint1_marker'].SetInput(self.transforms['base'])
            self.transforms['joint1_marker'].Translate(*self.joint_offsets['joint1'])
        
        # Joint2 - 肩部俯仰（绕Y轴）
        t2 = vtk.vtkTransform()
        t2.SetInput(t1)
        t2.Translate(*self.joint_offsets['joint2'])
        t2.RotateY(angles[1])
        self.transforms['link2'] = t2
        self.parts['link2'].SetUserTransform(t2)
        
        # Joint2标记
        if 'joint2_marker' in self.transforms:
            self.transforms['joint2_marker'].SetInput(t1)
            self.transforms['joint2_marker'].Translate(*self.joint_offsets['joint2'])
        
        # Joint3 - 肘部（绕Y轴）
        t3 = vtk.vtkTransform()
        t3.SetInput(t2)
        t3.Translate(*self.joint_offsets['joint3'])
        t3.RotateY(angles[2])
        self.transforms['link3'] = t3
        self.parts['link3'].SetUserTransform(t3)
        
        # Joint4 - 腕部旋转（绕Z轴）
        t4 = vtk.vtkTransform()
        t4.SetInput(t3)
        t4.Translate(*self.joint_offsets['joint4'])
        t4.RotateZ(angles[3])
        self.transforms['link4'] = t4
        self.parts['link4'].SetUserTransform(t4)
        
        # Joint5 - 腕部俯仰（绕Y轴）
        t5 = vtk.vtkTransform()
        t5.SetInput(t4)
        t5.Translate(*self.joint_offsets['joint5'])
        t5.RotateY(angles[4])
        self.transforms['link5'] = t5
        self.parts['link5'].SetUserTransform(t5)
        
        # Joint6 - 腕部旋转（绕Z轴）
        t6 = vtk.vtkTransform()
        t6.SetInput(t5)
        t6.Translate(*self.joint_offsets['joint6'])
        t6.RotateZ(angles[5])
        self.transforms['link6'] = t6
        self.parts['link6'].SetUserTransform(t6)
        
        # 夹爪
        tg = vtk.vtkTransform()
        tg.SetInput(t6)
        tg.Translate(*self.joint_offsets['gripper'])
        self.transforms['gripper'] = tg
        self.parts['gripper'].SetUserTransform(tg)
        
    def set_visibility(self, visible):
        """设置可见性"""
        for actor in self.parts.values():
            actor.SetVisibility(visible)
            
    def highlight_joint(self, joint_index, highlight=True):
        """高亮显示指定关节"""
        if 0 <= joint_index < 6:
            link_name = f"link{joint_index + 1}"
            if link_name in self.parts:
                if highlight:
                    self.parts[link_name].GetProperty().SetColor(1, 1, 0)  # 黄色高亮
                else:
                    # 恢复原色
                    color = self.link_color if joint_index % 2 == 0 else [c * 0.9 for c in self.link_color]
                    self.parts[link_name].GetProperty().SetColor(*color)
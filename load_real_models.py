#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加载真实STL模型的示例脚本
"""

import sys
import os
import glob
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui', 'widgets'))

from robot_3d_widget import Robot3DWidget

class RealModelLoader:
    """真实模型加载器"""
    
    def __init__(self, robot_3d_widget):
        self.widget = robot_3d_widget
        self.model_parts = {}
        
    def load_fr3_models(self, models_dir):
        """加载FR3模型文件"""
        print(f"正在搜索模型文件: {models_dir}")
        
        # 定义部件映射
        part_mapping = {
            # 主体结构
            'chest': 'fr3_chest.stl',
            'support': 'fr3_support.stl',
            
            # 左臂
            'left_base': 'fr3_left_base.stl',
            'left_link1': 'fr3_left_link1.stl',
            'left_link2': 'fr3_left_link2.stl',
            'left_link3': 'fr3_left_link3.stl',
            'left_link4': 'fr3_left_link4.stl',
            'left_link5': 'fr3_left_link5.stl',
            'left_link6': 'fr3_left_link6.stl',
            'left_gripper': 'fr3_left_gripper.stl',
            
            # 右臂
            'right_base': 'fr3_right_base.stl',
            'right_link1': 'fr3_right_link1.stl',
            'right_link2': 'fr3_right_link2.stl',
            'right_link3': 'fr3_right_link3.stl',
            'right_link4': 'fr3_right_link4.stl',
            'right_link5': 'fr3_right_link5.stl',
            'right_link6': 'fr3_right_link6.stl',
            'right_gripper': 'fr3_right_gripper.stl',
        }
        
        # 扫描可用的模型文件
        available_files = glob.glob(os.path.join(models_dir, "*.stl"))
        print(f"找到 {len(available_files)} 个STL文件")
        
        loaded_count = 0
        
        # 尝试加载每个部件
        for part_name, filename in part_mapping.items():
            file_path = os.path.join(models_dir, filename)
            
            if os.path.exists(file_path):
                print(f"✓ 加载 {part_name}: {filename}")
                actor = self.widget.load_stl_model(file_path, part_name)
                if actor:
                    self.model_parts[part_name] = actor
                    loaded_count += 1
                    
                    # 设置部件颜色
                    self.set_part_color(actor, part_name)
            else:
                print(f"✗ 未找到 {part_name}: {filename}")
        
        print(f"\n总共加载了 {loaded_count} 个部件")
        
        # 如果没有找到任何模型，创建占位符
        if loaded_count == 0:
            print("未找到任何STL文件，创建占位符模型")
            self.create_placeholder_models()
        
        return loaded_count > 0
    
    def set_part_color(self, actor, part_name):
        """设置部件颜色"""
        if 'chest' in part_name or 'support' in part_name:
            actor.GetProperty().SetColor(0.7, 0.7, 0.7)  # 灰色主体
        elif 'left' in part_name:
            if 'base' in part_name:
                actor.GetProperty().SetColor(0.3, 0.5, 0.8)  # 蓝色基座
            elif 'gripper' in part_name:
                actor.GetProperty().SetColor(0.8, 0.8, 0.2)  # 黄色夹爪
            else:
                actor.GetProperty().SetColor(0.4, 0.6, 0.9)  # 蓝色连杆
        elif 'right' in part_name:
            if 'base' in part_name:
                actor.GetProperty().SetColor(0.8, 0.3, 0.3)  # 红色基座
            elif 'gripper' in part_name:
                actor.GetProperty().SetColor(0.8, 0.8, 0.2)  # 黄色夹爪
            else:
                actor.GetProperty().SetColor(0.9, 0.4, 0.4)  # 红色连杆
    
    def create_placeholder_models(self):
        """创建占位符模型"""
        print("创建占位符几何体...")
        
        # 主体结构
        chest = self.widget.create_box(380, 200, 320, "chest")
        chest.GetProperty().SetColor(0.7, 0.7, 0.7)
        
        support = self.widget.create_box(160, 200, 1200, "support")
        support.GetProperty().SetColor(0.6, 0.6, 0.6)
        
        # 左臂简化模型
        left_base = self.widget.create_cylinder(60, 100, "left_base")
        left_base.GetProperty().SetColor(0.3, 0.5, 0.8)
        
        # 右臂简化模型
        right_base = self.widget.create_cylinder(60, 100, "right_base")
        right_base.GetProperty().SetColor(0.8, 0.3, 0.3)
        
        print("占位符模型创建完成")
    
    def setup_joint_hierarchy(self):
        """设置关节层次结构"""
        # 这里定义各个部件的父子关系和相对位置
        
        # 主体结构不动
        if 'chest' in self.model_parts:
            chest_transform = self.widget.robot_parts['chest']['transform']
            chest_transform.Translate(0, 0, 600)  # 胸部高度
        
        if 'support' in self.model_parts:
            support_transform = self.widget.robot_parts['support']['transform']
            support_transform.Translate(0, 0, 0)  # 支撑在底部
        
        # 左臂基座位置
        if 'left_base' in self.model_parts:
            base_transform = self.widget.robot_parts['left_base']['transform']
            base_transform.Translate(-190, 0, 650)  # 左侧，胸部高度
        
        # 右臂基座位置
        if 'right_base' in self.model_parts:
            base_transform = self.widget.robot_parts['right_base']['transform']
            base_transform.Translate(190, 0, 650)  # 右侧，胸部高度


class RealModelTestWindow(QMainWindow):
    """真实模型测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FR3真实模型测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建界面
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("加载STL模型")
        self.load_button.clicked.connect(self.load_models)
        button_layout.addWidget(self.load_button)
        
        self.reset_button = QPushButton("重置视角")
        self.reset_button.clicked.connect(self.reset_view)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 3D显示区域
        self.robot_3d = Robot3DWidget()
        layout.addWidget(self.robot_3d)
        
        # 状态栏
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)
        
        # 模型加载器
        self.loader = RealModelLoader(self.robot_3d)
        
        # 连接日志信号
        self.robot_3d.log_message.connect(self.show_log)
        
    def load_models(self):
        """加载模型"""
        models_dir = QFileDialog.getExistingDirectory(
            self, "选择模型文件夹", "models"
        )
        
        if models_dir:
            self.status_label.setText(f"正在加载: {models_dir}")
            QApplication.processEvents()
            
            success = self.loader.load_fr3_models(models_dir)
            
            if success:
                self.loader.setup_joint_hierarchy()
                self.status_label.setText(f"加载成功: {models_dir}")
                self.robot_3d.reset_camera()
            else:
                self.status_label.setText("未找到模型文件，使用占位符")
    
    def reset_view(self):
        """重置视角"""
        self.robot_3d.reset_camera()
        
    def show_log(self, message, level):
        """显示日志"""
        color = {
            'INFO': 'black',
            'SUCCESS': 'green',
            'ERROR': 'red',
            'WARNING': 'orange'
        }.get(level, 'black')
        
        self.status_label.setText(f"<font color='{color}'>{message}</font>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealModelTestWindow()
    window.show()
    sys.exit(app.exec_())
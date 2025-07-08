#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个STL文件加载
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui', 'widgets'))

from robot_3d_widget import Robot3DWidget

class SingleSTLTest(QMainWindow):
    """单个STL文件测试"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("单个STL文件测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建界面
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("选择STL文件")
        self.load_button.clicked.connect(self.load_stl_file)
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
        self.status_label = QLabel("请选择一个STL文件进行测试")
        layout.addWidget(self.status_label)
        
        # 连接日志信号
        self.robot_3d.log_message.connect(self.show_log)
        
    def load_stl_file(self):
        """加载STL文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择STL文件", 
            "", 
            "STL Files (*.stl);;All Files (*)"
        )
        
        if file_path:
            self.status_label.setText(f"正在加载: {os.path.basename(file_path)}")
            QApplication.processEvents()
            
            # 清除之前的模型
            if hasattr(self.robot_3d, 'renderer'):
                self.robot_3d.renderer.RemoveAllViewProps()
                self.robot_3d.add_coordinate_axes()
            
            # 加载新模型
            actor = self.robot_3d.load_stl_model(file_path, "test_model")
            
            if actor:
                # 设置颜色
                actor.GetProperty().SetColor(0.6, 0.8, 0.9)
                
                # 重置视角
                self.robot_3d.reset_camera()
                
                # 显示文件信息
                file_size = os.path.getsize(file_path)
                self.status_label.setText(
                    f"加载成功: {os.path.basename(file_path)} ({file_size} bytes)"
                )
            else:
                self.status_label.setText("加载失败")
    
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
    window = SingleSTLTest()
    window.show()
    sys.exit(app.exec_())
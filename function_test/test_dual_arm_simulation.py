#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双臂机械臂仿真界面集成测试
将生成的轨迹数据载入仿真界面进行可视化测试
"""

import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import QTimer

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'gui', 'widgets'))

try:
    from simulation_widget import ArmSimulationWidget
    from dual_arm_simulation_trajectory import DualArmTrajectoryGenerator
except ImportError as e:
    print(f"导入失败: {e}")

class DualArmSimulationTester(QMainWindow):
    """双臂仿真测试界面"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("双臂机械臂仿真测试 - FR3双臂协调动作")
        self.setGeometry(100, 100, 1000, 700)
        
        # 轨迹生成器
        self.trajectory_generator = None
        self.current_trajectory_index = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("🤖 FR3双臂机械臂仿真测试系统")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 状态信息
        self.status_label = QLabel("状态: 等待加载轨迹数据")
        self.status_label.setStyleSheet("color: #666; margin: 5px;")
        layout.addWidget(self.status_label)
        
        # 机械臂仿真控件
        self.arm_sim = ArmSimulationWidget()
        layout.addWidget(self.arm_sim)
        
        # 控制按钮
        button_layout = QVBoxLayout()
        
        self.generate_button = QPushButton("🔧 生成内置测试轨迹")
        self.generate_button.clicked.connect(self.generate_trajectory)
        button_layout.addWidget(self.generate_button)
        
        self.load_button = QPushButton("📁 加载轨迹文件")
        self.load_button.clicked.connect(self.load_trajectory_file)
        button_layout.addWidget(self.load_button)
        
        self.play_button = QPushButton("▶️ 播放动画")
        self.play_button.clicked.connect(self.play_animation)
        self.play_button.setEnabled(False)
        button_layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton("⏸️ 暂停")
        self.pause_button.clicked.connect(self.pause_animation)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("🔄 重置")
        self.reset_button.clicked.connect(self.reset_animation)
        self.reset_button.setEnabled(False)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
    
    def generate_trajectory(self):
        """生成内置测试轨迹"""
        try:
            self.status_label.setText("状态: 正在生成轨迹...")
            self.trajectory_generator = DualArmTrajectoryGenerator()
            
            # 连接机器人 (模拟)
            self.trajectory_generator.connect_robots()
            
            # 生成轨迹
            left_traj, right_traj = self.trajectory_generator.generate_complete_trajectory()
            
            # 设置到仿真控件
            self.arm_sim.set_arm_trajectories(left_traj, right_traj)
            
            self.status_label.setText(f"状态: 轨迹生成完成 - 左臂{len(left_traj)}点，右臂{len(right_traj)}点")
            
            # 启用控制按钮
            self.play_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            
            print("✅ 内置轨迹生成并加载到仿真界面成功")
            
        except Exception as e:
            self.status_label.setText(f"状态: 轨迹生成失败 - {str(e)}")
            print(f"❌ 轨迹生成失败: {e}")
    
    def load_trajectory_file(self):
        """加载轨迹文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择轨迹数据文件", 
            current_dir, 
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                left_traj = data.get('left_arm_trajectory', [])
                right_traj = data.get('right_arm_trajectory', [])
                
                if left_traj and right_traj:
                    self.arm_sim.set_arm_trajectories(left_traj, right_traj)
                    self.status_label.setText(f"状态: 轨迹文件加载成功 - 左臂{len(left_traj)}点，右臂{len(right_traj)}点")
                    
                    # 启用控制按钮
                    self.play_button.setEnabled(True)
                    self.reset_button.setEnabled(True)
                    
                    print(f"✅ 轨迹文件加载成功: {file_path}")
                else:
                    self.status_label.setText("状态: 轨迹文件格式错误")
                    print("❌ 轨迹文件格式错误")
                    
            except Exception as e:
                self.status_label.setText(f"状态: 文件加载失败 - {str(e)}")
                print(f"❌ 文件加载失败: {e}")
    
    def play_animation(self):
        """播放动画"""
        if self.arm_sim.get_trajectory_length() > 0:
            self.animation_timer.start(100)  # 100ms间隔
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.status_label.setText("状态: 动画播放中...")
            print("▶️ 开始播放双臂协调动画")
    
    def pause_animation(self):
        """暂停动画"""
        self.animation_timer.stop()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.status_label.setText("状态: 动画已暂停")
        print("⏸️ 动画暂停")
    
    def reset_animation(self):
        """重置动画"""
        self.animation_timer.stop()
        self.current_trajectory_index = 0
        self.arm_sim.update_trajectory_position(0)
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.status_label.setText("状态: 动画已重置")
        print("🔄 动画重置到起始位置")
    
    def update_animation(self):
        """更新动画帧"""
        trajectory_length = self.arm_sim.get_trajectory_length()
        
        if self.current_trajectory_index < trajectory_length:
            self.arm_sim.update_trajectory_position(self.current_trajectory_index)
            self.current_trajectory_index += 1
            
            # 更新进度
            progress = int(self.current_trajectory_index * 100 / trajectory_length)
            self.status_label.setText(f"状态: 动画播放中... ({progress}%)")
        else:
            # 动画完成
            self.animation_timer.stop()
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.status_label.setText("状态: 动画播放完成")
            print("✅ 双臂协调动画播放完成")

def main():
    """主程序"""
    print("🎮 双臂机械臂仿真界面集成测试")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    app.setApplicationName("双臂仿真测试")
    
    # 创建测试窗口
    window = DualArmSimulationTester()
    window.show()
    
    print("✅ 仿真测试界面启动成功")
    print("💡 点击'生成内置测试轨迹'开始测试")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
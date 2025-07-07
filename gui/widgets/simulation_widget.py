#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仿真界面 - 机械臂和底盘运动仿真
"""

import sys
import os
import math
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 导入程序分析器
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(os.path.dirname(current_dir), 'utils')
sys.path.insert(0, utils_dir)

from program_analyzer import ProgramAnalyzer

class ChassisSimulationWidget(QWidget):
    """底盘仿真显示区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.grid_size = 20  # 网格大小(像素)
        self.grid_real_size = 250  # 单个网格实际物理尺寸(mm)
        self.scale_ratio = self.grid_size / self.grid_real_size  # 像素/mm比例
        
        # 底盘实际尺寸: 465mm x 545mm
        self.chassis_real_width = 465  # mm
        self.chassis_real_length = 545  # mm
        self.chassis_pixel_width = int(self.chassis_real_width * self.scale_ratio)
        self.chassis_pixel_length = int(self.chassis_real_length * self.scale_ratio)
        
        self.chassis_pos = [10, 5]  # 底盘位置(网格坐标)
        self.chassis_angle = 90  # 底盘角度(度) - 初始朝下
        self.path_points = []  # 路径点列表
        self.current_path_index = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_speed = 100  # 动画速度百分比
        self.is_manual_seeking = False  # 是否正在手动拖动进度
        
        # 坐标系状态
        self.x_inverted = False  # X轴是否反向
        self.y_inverted = False  # Y轴是否反向
        self.chassis_rotation_offset = 0  # 底盘额外旋转角度
        self.coordinate_origin = [30, 30]  # 坐标系原点位置
        
        # 交互式路径绘制状态
        self.drawing_mode = False  # 是否处于绘制模式
        self.drawing_path = []  # 正在绘制的路径点
        self.last_grid_pos = None  # 上一个网格位置
        self.start_grid_pos = None  # 起始网格位置
        
    def paintEvent(self, event):
        """绘制底盘仿真"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制网格
        self.draw_grid(painter)
        
        # 绘制路径
        self.draw_path(painter)
        
        # 绘制底盘
        self.draw_chassis(painter)
        
    def draw_grid(self, painter):
        """绘制网格"""
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        width = self.width()
        height = self.height()
        
        # 垂直线
        for x in range(0, width, self.grid_size):
            painter.drawLine(x, 0, x, height)
            
        # 水平线
        for y in range(0, height, self.grid_size):
            painter.drawLine(0, y, width, y)
        
        # 绘制坐标系
        self.draw_coordinate_system(painter)
        
        # 绘制比例尺
        self.draw_scale_ruler(painter)
    
    def draw_path(self, painter):
        """绘制路径"""
        # 绘制已确定的路径
        if len(self.path_points) >= 2:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
            
            # 绘制路径线
            for i in range(len(self.path_points) - 1):
                x1 = self.path_points[i][0] * self.grid_size
                y1 = self.path_points[i][1] * self.grid_size
                x2 = self.path_points[i + 1][0] * self.grid_size
                y2 = self.path_points[i + 1][1] * self.grid_size
                painter.drawLine(x1, y1, x2, y2)
                
            # 绘制路径点和方向
            for i, (x, y, angle) in enumerate(self.path_points):
                px = x * self.grid_size
                py = y * self.grid_size
                
                # 绘制路径点
                if i == self.current_path_index:
                    painter.setBrush(QBrush(QColor(255, 100, 100)))
                else:
                    painter.setBrush(QBrush(QColor(100, 150, 255)))
                painter.drawEllipse(px - 4, py - 4, 8, 8)
                
                # 绘制方向箭头
                self.draw_arrow(painter, px, py, angle)
        
        # 绘制正在绘制的路径（实时预览）
        if self.drawing_mode and len(self.drawing_path) >= 2:
            painter.setPen(QPen(QColor(255, 200, 100), 3))  # 橙色，更粗的线条
            
            # 绘制绘制中的路径线
            for i in range(len(self.drawing_path) - 1):
                x1 = self.drawing_path[i][0] * self.grid_size
                y1 = self.drawing_path[i][1] * self.grid_size
                x2 = self.drawing_path[i + 1][0] * self.grid_size
                y2 = self.drawing_path[i + 1][1] * self.grid_size
                painter.drawLine(x1, y1, x2, y2)
                
            # 绘制绘制中的路径点
            painter.setBrush(QBrush(QColor(255, 150, 50)))
            for i, (x, y, angle) in enumerate(self.drawing_path):
                px = x * self.grid_size
                py = y * self.grid_size
                painter.drawEllipse(px - 3, py - 3, 6, 6)
                
                # 为起点绘制特殊标记
                if i == 0:
                    painter.setPen(QPen(QColor(50, 200, 50), 2))
                    painter.drawEllipse(px - 6, py - 6, 12, 12)
                    painter.setPen(QPen(QColor(255, 200, 100), 3))
    
    def draw_coordinate_system(self, painter):
        """绘制坐标系"""
        painter.save()
        
        # 使用动态原点位置
        origin_x, origin_y = self.coordinate_origin
        axis_length = 40
        
        # X轴方向（根据反向状态决定）
        x_direction = -1 if self.x_inverted else 1
        x_end_x = origin_x + axis_length * x_direction
        
        # Y轴方向（根据反向状态决定）
        y_direction = -1 if self.y_inverted else 1
        y_end_y = origin_y + axis_length * y_direction
        
        # X轴（红色）
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        painter.drawLine(origin_x, origin_y, x_end_x, origin_y)
        
        # X轴箭头
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        if self.x_inverted:
            x_arrow = [
                QPoint(x_end_x, origin_y),
                QPoint(x_end_x + 8, origin_y - 4),
                QPoint(x_end_x + 8, origin_y + 4)
            ]
        else:
            x_arrow = [
                QPoint(x_end_x, origin_y),
                QPoint(x_end_x - 8, origin_y - 4),
                QPoint(x_end_x - 8, origin_y + 4)
            ]
        painter.drawPolygon(x_arrow)
        
        # Y轴（绿色）
        painter.setPen(QPen(QColor(0, 150, 0), 3))
        painter.drawLine(origin_x, origin_y, origin_x, y_end_y)
        
        # Y轴箭头
        painter.setBrush(QBrush(QColor(0, 150, 0)))
        if self.y_inverted:
            y_arrow = [
                QPoint(origin_x, y_end_y),
                QPoint(origin_x - 4, y_end_y + 8),
                QPoint(origin_x + 4, y_end_y + 8)
            ]
        else:
            y_arrow = [
                QPoint(origin_x, y_end_y),
                QPoint(origin_x - 4, y_end_y - 8),
                QPoint(origin_x + 4, y_end_y - 8)
            ]
        painter.drawPolygon(y_arrow)
        
        # 标签
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        x_label_x = x_end_x + (5 if not self.x_inverted else -15)
        y_label_y = y_end_y + (15 if not self.y_inverted else -5)
        painter.drawText(x_label_x, origin_y + 5, "X")
        painter.drawText(origin_x - 5, y_label_y, "Y")
        painter.drawText(origin_x - 15, origin_y - 5, "O")
        
        painter.restore()
    
    def draw_scale_ruler(self, painter):
        """绘制比例尺（右上角）"""
        painter.save()
        
        # 比例尺位置（右上角）
        margin = 15
        ruler_x = self.width() - 120 - margin
        ruler_y = margin + 10
        
        # 绘制比例尺标尺（以米为单位）
        scale_length_m = 0.5  # 0.5米标尺
        scale_length_pixels = int(scale_length_m * 1000 * self.scale_ratio)  # 转换为像素
        
        # 标尺线（加粗，黑色）
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawLine(ruler_x, ruler_y + 15, ruler_x + scale_length_pixels, ruler_y + 15)
        
        # 标尺刻度
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawLine(ruler_x, ruler_y + 10, ruler_x, ruler_y + 20)
        painter.drawLine(ruler_x + scale_length_pixels, ruler_y + 10, ruler_x + scale_length_pixels, ruler_y + 20)
        
        # 标尺文字（以米为单位）
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(ruler_x - 5, ruler_y + 8, "0")
        painter.drawText(ruler_x + scale_length_pixels - 10, ruler_y + 8, "0.5m")
        
        # 网格信息（简洁显示）
        painter.setFont(QFont("Arial", 8))
        grid_size_m = self.grid_real_size / 1000  # 转换为米
        painter.drawText(ruler_x, ruler_y + 30, f"网格: {grid_size_m}m")
        
        painter.restore()
    
    def draw_chassis(self, painter):
        """绘制底盘"""
        x = self.chassis_pos[0] * self.grid_size
        y = self.chassis_pos[1] * self.grid_size
        
        # 根据实际尺寸计算底盘矩形尺寸
        # 465mm x 545mm，按比例缩放
        half_width = self.chassis_pixel_width // 2
        half_length = self.chassis_pixel_length // 2
        
        # 1. 绘制底盘矩形（会受到rotation_offset影响）
        painter.save()
        painter.translate(x, y)
        painter.rotate(self.chassis_angle + self.chassis_rotation_offset)
        
        painter.setBrush(QBrush(QColor(255, 150, 50)))
        painter.setPen(QPen(QColor(200, 100, 0), 2))
        painter.drawRect(-half_width, -half_length, self.chassis_pixel_width, self.chassis_pixel_length)
        
        # 绘制底盘标识和尺寸信息（跟随矩形旋转）
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 6, QFont.Bold))
        text_y = -half_length + 8
        painter.drawText(-half_width + 2, text_y, "HERMES")
        painter.drawText(-half_width + 2, text_y + 10, f"{self.chassis_real_width}×{self.chassis_real_length}mm")
        
        painter.restore()
        
        # 2. 绘制方向箭头（不受rotation_offset影响，永远指向chassis_angle方向）
        painter.save()
        painter.translate(x, y)
        painter.rotate(self.chassis_angle)  # 只使用原始角度，不加rotation_offset
        
        painter.setBrush(QBrush(QColor(220, 50, 50)))
        painter.setPen(QPen(QColor(180, 30, 30), 2))
        
        # 箭头尺寸适应底盘大小
        arrow_length = min(half_width, half_length) * 0.8
        arrow_width = arrow_length * 0.4
        
        # 主箭头（指向前进方向）
        main_arrow = [
            QPoint(int(arrow_length), 0),                    # 箭头尖端
            QPoint(int(arrow_length * 0.6), int(-arrow_width)), # 左上
            QPoint(int(arrow_length * 0.6), int(-arrow_width * 0.4)), # 左上内
            QPoint(int(-arrow_length * 0.4), int(-arrow_width * 0.4)), # 箭头尾左上
            QPoint(int(-arrow_length * 0.4), int(arrow_width * 0.4)),  # 箭头尾左下
            QPoint(int(arrow_length * 0.6), int(arrow_width * 0.4)),   # 左下内
            QPoint(int(arrow_length * 0.6), int(arrow_width))           # 左下
        ]
        painter.drawPolygon(main_arrow)
        
        painter.restore()
    
    def draw_arrow(self, painter, x, y, angle):
        """绘制方向箭头"""
        painter.save()
        painter.translate(x, y)
        painter.rotate(angle)
        
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawLine(0, 0, 15, 0)
        
        # 箭头头部
        points = [QPoint(15, 0), QPoint(10, -3), QPoint(10, 3)]
        painter.drawPolygon(points)
        
        painter.restore()
    
    def set_chassis_position(self, x, y, angle):
        """设置底盘位置"""
        self.chassis_pos = [x, y]
        self.chassis_angle = angle
        self.update()
    
    def set_path_points(self, points):
        """设置路径点"""
        self.path_points = points
        self.current_path_index = 0
        self.update()
    
    def set_animation_speed(self, speed_percent):
        """设置动画速度"""
        self.animation_speed = speed_percent
        if self.animation_timer.isActive():
            # 根据速度调整定时器间隔
            interval = max(10, int(100 * 100 / speed_percent))  # 10ms到1000ms
            self.animation_timer.start(interval)
    
    def start_animation(self):
        """开始动画"""
        if self.path_points:
            interval = max(10, int(100 * 100 / self.animation_speed))
            self.animation_timer.start(interval)
    
    def stop_animation(self):
        """停止动画"""
        self.animation_timer.stop()
    
    def update_animation(self):
        """更新动画"""
        if not self.is_manual_seeking and self.current_path_index < len(self.path_points):
            point = self.path_points[self.current_path_index]
            self.set_chassis_position(point[0], point[1], point[2])
            self.current_path_index += 1
        elif self.current_path_index >= len(self.path_points):
            self.stop_animation()
            self.current_path_index = 0
    
    def seek_to_position(self, index):
        """跳转到指定位置"""
        if 0 <= index < len(self.path_points):
            self.current_path_index = index
            point = self.path_points[index]
            self.set_chassis_position(point[0], point[1], point[2])
    
    def get_current_progress(self):
        """获取当前进度"""
        if not self.path_points:
            return 0
        return int(self.current_path_index * 100 / len(self.path_points))
    
    def toggle_xy_direction(self):
        """切换X/Y轴方向"""
        # 计算当前坐标轴构成矩形的对角线角点
        axis_length = 40
        if not self.x_inverted and not self.y_inverted:
            # 从默认状态切换：原点(30,30)，对角线角点(70,70)
            self.coordinate_origin = [30 + axis_length, 30 + axis_length]
        elif self.x_inverted and self.y_inverted:
            # 从反转状态切换回默认：恢复到原始原点
            self.coordinate_origin = [30, 30]
        else:
            # 从部分反转状态切换：计算新的合适原点
            current_x, current_y = self.coordinate_origin
            if self.x_inverted != self.y_inverted:
                # 调整原点位置以保持显示在可见区域
                if not self.x_inverted:  # Y轴已反转
                    self.coordinate_origin = [current_x, 30 + axis_length]
                else:  # X轴已反转
                    self.coordinate_origin = [30 + axis_length, current_y]
        
        # 切换轴向
        self.x_inverted = not self.x_inverted
        self.y_inverted = not self.y_inverted
        self.update()
    
    def rotate_chassis_90(self):
        """底盘矩形旋转90度（不影响红色箭头）"""
        self.chassis_rotation_offset = (self.chassis_rotation_offset + 90) % 360
        self.update()
    
    def clear_path(self):
        """清除路径点和重置状态"""
        self.path_points = []
        self.current_path_index = 0
        self.stop_animation()
        self.update()
    
    def pixel_to_grid(self, x, y):
        """将像素坐标转换为网格坐标"""
        grid_x = round(x / self.grid_size)
        grid_y = round(y / self.grid_size)
        return grid_x, grid_y
    
    def grid_to_pixel(self, grid_x, grid_y):
        """将网格坐标转换为像素坐标"""
        x = grid_x * self.grid_size
        y = grid_y * self.grid_size
        return x, y
    
    def calculate_direction_angle(self, from_pos, to_pos):
        """计算从from_pos到to_pos的方向角度"""
        import math
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        if dx == 0 and dy == 0:
            return 0
        
        # 计算角度，0度为向右，90度为向下
        angle = math.degrees(math.atan2(dy, dx))
        # 转换为Qt的角度系统（0度向右，顺时针为正）
        return angle
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 开始绘制路径
            x, y = event.x(), event.y()
            grid_x, grid_y = self.pixel_to_grid(x, y)
            
            # 检查是否在有效网格范围内
            if 0 <= grid_x < self.width() // self.grid_size and 0 <= grid_y < self.height() // self.grid_size:
                self.drawing_mode = True
                self.drawing_path = []
                self.start_grid_pos = (grid_x, grid_y)
                self.last_grid_pos = (grid_x, grid_y)
                
                # 添加起始点（角度暂时为0，后面会根据移动方向调整）
                self.drawing_path.append([grid_x, grid_y, 0])
                self.update()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.drawing_mode:
            x, y = event.x(), event.y()
            grid_x, grid_y = self.pixel_to_grid(x, y)
            
            # 检查是否移动到新的网格位置
            if (grid_x, grid_y) != self.last_grid_pos:
                # 计算方向角度
                angle = self.calculate_direction_angle(self.last_grid_pos, (grid_x, grid_y))
                
                # 更新上一个点的角度
                if len(self.drawing_path) > 0:
                    self.drawing_path[-1][2] = angle
                
                # 添加新的路径点
                self.drawing_path.append([grid_x, grid_y, angle])
                self.last_grid_pos = (grid_x, grid_y)
                self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.drawing_mode:
            self.drawing_mode = False
            
            if len(self.drawing_path) > 1:
                # 完成路径绘制，将绘制的路径设置为当前路径
                self.path_points = self.drawing_path.copy()
                self.current_path_index = 0
                
                # 计算路径统计信息
                self.show_path_statistics()
            else:
                # 路径太短，清除
                self.drawing_path = []
            
            self.update()
    
    def show_path_statistics(self):
        """显示路径统计信息"""
        if len(self.path_points) < 2:
            return
        
        # 计算总距离和线段数
        total_distance = 0
        segment_count = len(self.path_points) - 1
        
        for i in range(len(self.path_points) - 1):
            x1, y1 = self.path_points[i][0], self.path_points[i][1]
            x2, y2 = self.path_points[i + 1][0], self.path_points[i + 1][1]
            
            # 计算实际距离（网格单位 * 实际尺寸）
            dx = abs(x2 - x1) * self.grid_real_size / 1000  # 转换为米
            dy = abs(y2 - y1) * self.grid_real_size / 1000  # 转换为米
            distance = (dx ** 2 + dy ** 2) ** 0.5
            total_distance += distance
        
        # 显示统计信息弹框
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("路径绘制完成")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"路径绘制完成！\n\n总距离: {total_distance:.2f} 米\n线段数量: {segment_count} 段")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

class ArmSimulationWidget(QWidget):
    """机械臂仿真显示区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 400)
        
        # FR3机械臂参数(mm)
        self.base_height = 140  # 底座到J2高度
        self.link1_length = 280  # J2到J3连杆长度
        self.link2_length = 240  # J3到J5连杆长度
        self.link3_length = 100  # J5到J6连杆长度
        self.chest_width = 380  # 胸部宽度
        self.chest_height = 320  # 胸部高度
        
        # 关节角度 (度)
        self.left_arm_joints = [0, 0, 0, 0, 0, 0]
        self.right_arm_joints = [0, 0, 0, 0, 0, 0]
        
        # 缩放比例
        self.scale = 0.5
        
    def paintEvent(self, event):
        """绘制机械臂仿真"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 分为上下两部分
        height = self.height()
        width = self.width()
        
        # 上半部分：正面视图
        painter.setViewport(0, 0, width, height // 2)
        self.draw_front_view(painter)
        
        # 下半部分：侧面视图
        painter.setViewport(0, height // 2, width, height // 2)
        self.draw_side_view(painter)
    
    def draw_front_view(self, painter):
        """绘制正面视图"""
        painter.save()
        
        # 设置坐标系原点到中心
        center_x = self.width() // 2
        center_y = self.height() // 4
        painter.translate(center_x, center_y)
        
        # 绘制胸部
        self.draw_chest(painter)
        
        # 绘制左臂（正面视图）
        left_x = -int(self.chest_width * self.scale) // 2
        self.draw_arm_front(painter, left_x, 0, self.left_arm_joints, True)
        
        # 绘制右臂（正面视图）
        right_x = int(self.chest_width * self.scale) // 2
        self.draw_arm_front(painter, right_x, 0, self.right_arm_joints, False)
        
        painter.restore()
    
    def draw_side_view(self, painter):
        """绘制侧面视图"""
        painter.save()
        
        # 设置坐标系原点到中心
        center_x = self.width() // 2
        center_y = self.height() // 4
        painter.translate(center_x, center_y)
        
        # 绘制胸部轮廓
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        chest_h = int(self.chest_height * self.scale)
        painter.drawRect(-20, -chest_h // 2, 40, chest_h)
        
        # 绘制左臂（侧面视图）
        self.draw_arm_side(painter, -100, 0, self.left_arm_joints, "左臂")
        
        # 绘制右臂（侧面视图）
        self.draw_arm_side(painter, 100, 0, self.right_arm_joints, "右臂")
        
        painter.restore()
    
    def draw_chest(self, painter):
        """绘制胸部"""
        painter.setPen(QPen(QColor(100, 100, 100), 3))
        painter.setBrush(QBrush(QColor(220, 220, 220)))
        
        w = int(self.chest_width * self.scale)
        h = int(self.chest_height * self.scale)
        painter.drawRect(-w // 2, -h // 2, w, h)
        
        # 绘制胸部标识
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.drawText(-20, 0, "胸部")
    
    def draw_arm_front(self, painter, base_x, base_y, joints, is_left):
        """绘制机械臂正面视图"""
        painter.save()
        painter.translate(base_x, base_y)
        
        # 绘制底座
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawEllipse(-10, -10, 20, 20)
        
        # 简化的正面视图，主要显示肩部和肘部运动
        # J1: 底座旋转 - 影响整个手臂的左右摆动
        # J2: 肩部摆动 - 影响大臂的上下摆动
        # J3: 肘部旋转 - 影响小臂的摆动
        
        arm_name = "左臂" if is_left else "右臂"
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.drawText(-20, 25, arm_name)
        
        # 绘制简化的关节位置
        y_offset = 40
        for i, angle in enumerate(joints[:3]):  # 只显示前3个关节
            painter.setPen(QPen(QColor(100, 100, 200), 2))
            painter.setBrush(QBrush(QColor(150, 150, 250)))
            painter.drawEllipse(-5, y_offset - 5, 10, 10)
            painter.drawText(15, y_offset + 5, f"J{i+1}: {angle:.1f}°")
            y_offset += 30
        
        painter.restore()
    
    def draw_arm_side(self, painter, base_x, base_y, joints, arm_name):
        """绘制机械臂侧面视图"""
        painter.save()
        painter.translate(base_x, base_y)
        
        # 根据关节角度计算各关节位置
        # 这里实现简化的运动学正解
        positions = self.calculate_arm_positions(joints)
        
        # 绘制连杆
        painter.setPen(QPen(QColor(100, 150, 200), 3))
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            painter.drawLine(x1, y1, x2, y2)
        
        # 绘制关节
        painter.setBrush(QBrush(QColor(200, 100, 100)))
        for i, (x, y) in enumerate(positions):
            painter.drawEllipse(x - 4, y - 4, 8, 8)
            if i < len(joints):
                painter.setPen(QPen(QColor(50, 50, 50)))
                painter.drawText(x + 8, y - 8, f"J{i+1}")
                painter.drawText(x + 8, y + 8, f"{joints[i]:.1f}°")
                painter.setPen(QPen(QColor(100, 150, 200), 3))
        
        # 绘制手臂名称
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.drawText(-30, -30, arm_name)
        
        painter.restore()
    
    def calculate_arm_positions(self, joints):
        """计算机械臂各关节位置（简化版运动学）"""
        positions = []
        
        # 底座位置
        x, y = 0, 0
        positions.append((x, y))
        
        # J1: 底座旋转（在侧面视图中不明显）
        # J2: 肩部摆动
        angle2 = math.radians(joints[1])
        x += 0
        y -= int(self.base_height * self.scale)
        positions.append((int(x), int(y)))
        
        # J3: 大臂
        angle3 = math.radians(joints[2])
        x += self.link1_length * self.scale * math.cos(angle2 + angle3)
        y -= self.link1_length * self.scale * math.sin(angle2 + angle3)
        positions.append((int(x), int(y)))
        
        # J4: 小臂
        angle4 = math.radians(joints[3])
        x += self.link2_length * self.scale * math.cos(angle2 + angle3 + angle4)
        y -= self.link2_length * self.scale * math.sin(angle2 + angle3 + angle4)
        positions.append((int(x), int(y)))
        
        # J5: 手腕
        angle5 = math.radians(joints[4])
        x += self.link3_length * self.scale * math.cos(angle2 + angle3 + angle4 + angle5)
        y -= self.link3_length * self.scale * math.sin(angle2 + angle3 + angle4 + angle5)
        positions.append((int(x), int(y)))
        
        # J6: 末端
        angle6 = math.radians(joints[5])
        x += 20 * self.scale * math.cos(angle2 + angle3 + angle4 + angle5 + angle6)
        y -= 20 * self.scale * math.sin(angle2 + angle3 + angle4 + angle5 + angle6)
        positions.append((int(x), int(y)))
        
        return positions
    
    def set_left_arm_joints(self, joints):
        """设置左臂关节角度"""
        self.left_arm_joints = joints[:]
        self.update()
    
    def set_right_arm_joints(self, joints):
        """设置右臂关节角度"""
        self.right_arm_joints = joints[:]
        self.update()

class SimulationWidget(QWidget):
    """仿真主界面"""
    
    log_message = pyqtSignal(str, str)  # 日志信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.chassis_animation_playing = False
        self.arm_animation_playing = False
        self.program_analyzer = ProgramAnalyzer()
        self.animation_sequence = []
        self.current_animation_index = 0
        self.progress_update_timer = QTimer()
        self.progress_update_timer.timeout.connect(self.update_progress_display)
        self.progress_update_timer.start(100)  # 每100ms更新一次进度显示
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("🎮 机器人仿真系统")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 主显示区域
        display_layout = QHBoxLayout()
        
        # 左侧：底盘仿真
        chassis_group = QGroupBox("底盘运动仿真")
        chassis_layout = QVBoxLayout(chassis_group)
        
        # 底盘仿真控制按钮（在标题旁边）
        chassis_title_layout = QHBoxLayout()
        chassis_title_layout.addWidget(QLabel(""))  # 占位
        chassis_title_layout.addStretch()
        
        # X/Y方向切换按钮
        self.xy_toggle_button = QPushButton("🔄 X/Y切换")
        self.xy_toggle_button.setToolTip("切换X轴和Y轴方向")
        self.xy_toggle_button.setMaximumWidth(100)
        
        # 90度旋转按钮
        self.rotate_90_button = QPushButton("🔄 90°旋转")
        self.rotate_90_button.setToolTip("底盘矩形围绕质心旋转90度")
        self.rotate_90_button.setMaximumWidth(100)
        
        # 清除路径按钮
        self.clear_path_button = QPushButton("🗑️ 清除路径")
        self.clear_path_button.setToolTip("一键清除底盘运动仿真中的蓝色路径线条")
        self.clear_path_button.setMaximumWidth(100)
        
        # 设置按钮字体
        button_font = QFont()
        button_font.setFamily("PingFang SC, Helvetica, Microsoft YaHei, Arial")
        button_font.setPointSize(8)
        self.xy_toggle_button.setFont(button_font)
        self.rotate_90_button.setFont(button_font)
        self.clear_path_button.setFont(button_font)
        
        chassis_title_layout.addWidget(self.xy_toggle_button)
        chassis_title_layout.addWidget(self.rotate_90_button)
        chassis_title_layout.addWidget(self.clear_path_button)
        
        # 添加交互式绘制说明
        drawing_help_layout = QHBoxLayout()
        help_label = QLabel("💡 提示：在网格上拖拽鼠标可以绘制底盘路径")
        help_label.setStyleSheet("color: #666; font-size: 10px; margin: 2px;")
        drawing_help_layout.addWidget(help_label)
        drawing_help_layout.addStretch()
        chassis_layout.addLayout(drawing_help_layout)
        
        chassis_layout.addLayout(chassis_title_layout)
        
        self.chassis_sim = ChassisSimulationWidget()
        chassis_layout.addWidget(self.chassis_sim)
        
        # 右侧：机械臂仿真
        arm_group = QGroupBox("机械臂运动仿真")
        arm_layout = QVBoxLayout(arm_group)
        self.arm_sim = ArmSimulationWidget()
        arm_layout.addWidget(self.arm_sim)
        
        display_layout.addWidget(chassis_group)
        display_layout.addWidget(arm_group)
        layout.addWidget(QWidget())  # 占位
        layout.addLayout(display_layout)
        
        # 控制面板 - 分为两个部分
        control_layout = QHBoxLayout()
        
        # 底盘控制面板
        chassis_control_group = QGroupBox("底盘仿真控制")
        chassis_control_layout = QVBoxLayout(chassis_control_group)
        
        # 底盘播放控制按钮
        chassis_button_layout = QHBoxLayout()
        self.chassis_play_button = QPushButton("播放底盘")
        self.chassis_pause_button = QPushButton("暂停")
        self.chassis_stop_button = QPushButton("停止")
        self.chassis_reset_button = QPushButton("重置")
        
        # 设置按钮字体（Mac优先）
        button_font = QFont()
        button_font.setFamily("PingFang SC, Helvetica, Microsoft YaHei, Arial")
        button_font.setPointSize(9)
        for btn in [self.chassis_play_button, self.chassis_pause_button, 
                   self.chassis_stop_button, self.chassis_reset_button]:
            btn.setFont(button_font)
        
        chassis_button_layout.addWidget(self.chassis_play_button)
        chassis_button_layout.addWidget(self.chassis_pause_button)
        chassis_button_layout.addWidget(self.chassis_stop_button)
        chassis_button_layout.addWidget(self.chassis_reset_button)
        
        chassis_control_layout.addLayout(chassis_button_layout)
        
        # 底盘进度条（大号滑块）
        chassis_progress_layout = QHBoxLayout()
        chassis_progress_layout.addWidget(QLabel("进度:"))
        self.chassis_progress_slider = QSlider(Qt.Horizontal)
        self.chassis_progress_slider.setRange(0, 100)
        self.chassis_progress_slider.setValue(0)
        self.chassis_progress_slider.setMinimumHeight(30)  # 增加高度
        self.chassis_progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e1e1e1, stop: 1 #c7c7c7);
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f4f4f4, stop: 1 #3573dc);
                border: 1px solid #5c5c5c;
                width: 20px;  /* 更大的滑块 */
                margin: -8px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #4584e6);
            }
        """)
        chassis_progress_layout.addWidget(self.chassis_progress_slider)
        self.chassis_progress_label = QLabel("0%")
        chassis_progress_layout.addWidget(self.chassis_progress_label)
        
        chassis_control_layout.addLayout(chassis_progress_layout)
        
        # 底盘速度控制
        chassis_speed_layout = QHBoxLayout()
        chassis_speed_layout.addWidget(QLabel("速度:"))
        self.chassis_speed_slider = QSlider(Qt.Horizontal)
        self.chassis_speed_slider.setRange(10, 200)
        self.chassis_speed_slider.setValue(100)
        chassis_speed_layout.addWidget(self.chassis_speed_slider)
        self.chassis_speed_label = QLabel("1.0x")
        chassis_speed_layout.addWidget(self.chassis_speed_label)
        
        chassis_control_layout.addLayout(chassis_speed_layout)
        
        # 机械臂控制面板
        arm_control_group = QGroupBox("机械臂仿真控制")
        arm_control_layout = QVBoxLayout(arm_control_group)
        
        # 机械臂播放控制按钮
        arm_button_layout = QHBoxLayout()
        self.arm_play_button = QPushButton("播放机械臂")
        self.arm_pause_button = QPushButton("暂停")
        self.arm_stop_button = QPushButton("停止")
        self.arm_reset_button = QPushButton("重置")
        
        # 设置机械臂按钮字体（Mac优先）
        for btn in [self.arm_play_button, self.arm_pause_button, 
                   self.arm_stop_button, self.arm_reset_button]:
            btn.setFont(button_font)
        
        arm_button_layout.addWidget(self.arm_play_button)
        arm_button_layout.addWidget(self.arm_pause_button)
        arm_button_layout.addWidget(self.arm_stop_button)
        arm_button_layout.addWidget(self.arm_reset_button)
        
        arm_control_layout.addLayout(arm_button_layout)
        
        # 机械臂进度条（大号滑块）
        arm_progress_layout = QHBoxLayout()
        arm_progress_layout.addWidget(QLabel("进度:"))
        self.arm_progress_slider = QSlider(Qt.Horizontal)
        self.arm_progress_slider.setRange(0, 100)
        self.arm_progress_slider.setValue(0)
        self.arm_progress_slider.setMinimumHeight(30)  # 增加高度
        self.arm_progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e1e1e1, stop: 1 #c7c7c7);
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f4f4f4, stop: 1 #dc5735);
                border: 1px solid #5c5c5c;
                width: 20px;
                margin: -8px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #e67055);
            }
        """)
        arm_progress_layout.addWidget(self.arm_progress_slider)
        self.arm_progress_label = QLabel("0%")
        arm_progress_layout.addWidget(self.arm_progress_label)
        
        arm_control_layout.addLayout(arm_progress_layout)
        
        # 机械臂速度控制
        arm_speed_layout = QHBoxLayout()
        arm_speed_layout.addWidget(QLabel("速度:"))
        self.arm_speed_slider = QSlider(Qt.Horizontal)
        self.arm_speed_slider.setRange(10, 200)
        self.arm_speed_slider.setValue(100)
        arm_speed_layout.addWidget(self.arm_speed_slider)
        self.arm_speed_label = QLabel("1.0x")
        arm_speed_layout.addWidget(self.arm_speed_label)
        
        arm_control_layout.addLayout(arm_speed_layout)
        
        # 添加两个控制面板到布局
        control_layout.addWidget(chassis_control_group)
        control_layout.addWidget(arm_control_group)
        
        # 文件加载（放在底部，跨越两列）
        file_group = QGroupBox("程序加载")
        file_layout = QHBoxLayout(file_group)
        self.load_button = QPushButton("📁 加载主控程序")
        self.file_label = QLabel("未选择文件")
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        
        layout.addWidget(QWidget())  # 占位
        layout.addLayout(display_layout)
        layout.addLayout(control_layout)
        layout.addWidget(file_group)
        
        # 测试数据
        self.load_test_data()
    
    def setup_connections(self):
        """设置信号连接"""
        # 底盘控制连接
        self.chassis_play_button.clicked.connect(self.play_chassis_animation)
        self.chassis_pause_button.clicked.connect(self.pause_chassis_animation)
        self.chassis_stop_button.clicked.connect(self.stop_chassis_animation)
        self.chassis_reset_button.clicked.connect(self.reset_chassis_animation)
        
        # 机械臂控制连接
        self.arm_play_button.clicked.connect(self.play_arm_animation)
        self.arm_pause_button.clicked.connect(self.pause_arm_animation)
        self.arm_stop_button.clicked.connect(self.stop_arm_animation)
        self.arm_reset_button.clicked.connect(self.reset_arm_animation)
        
        # 程序加载
        self.load_button.clicked.connect(self.load_program)
        
        # 底盘控制按钮
        self.xy_toggle_button.clicked.connect(self.toggle_xy_direction)
        self.rotate_90_button.clicked.connect(self.rotate_chassis_90)
        self.clear_path_button.clicked.connect(self.clear_chassis_path)
        
        # 速度和进度控制
        self.chassis_speed_slider.valueChanged.connect(self.update_chassis_speed)
        self.chassis_progress_slider.valueChanged.connect(self.update_chassis_progress)
        self.chassis_progress_slider.sliderPressed.connect(self.chassis_seek_start)
        self.chassis_progress_slider.sliderReleased.connect(self.chassis_seek_end)
        self.arm_speed_slider.valueChanged.connect(self.update_arm_speed)
        self.arm_progress_slider.valueChanged.connect(self.update_arm_progress)
    
    def load_test_data(self):
        """加载测试数据"""
        # 测试底盘路径（根据实际尺寸调整，考虑250mm网格）
        # 路径点以网格坐标表示，每个网格250mm
        test_path = [
            [8, 4, 90],    # 初始位置，箭头朝下 (2000mm, 1000mm)
            [8, 6, 90],    # 向下移动 (2000mm, 1500mm)
            [10, 6, 0],    # 向右移动，箭头朝右 (2500mm, 1500mm)
            [10, 8, 90],   # 向下移动，箭头朝下 (2500mm, 2000mm)
            [12, 8, 0],    # 向右移动，箭头朝右 (3000mm, 2000mm)
            [12, 10, 90],  # 向下移动，箭头朝下 (3000mm, 2500mm)
            [10, 10, 180], # 向左移动，箭头朝左 (2500mm, 2500mm)
            [8, 10, 180]   # 向左移动，箭头朝左 (2000mm, 2500mm)
        ]
        self.chassis_sim.set_path_points(test_path)
        # 设置初始位置
        self.chassis_sim.set_chassis_position(8, 4, 90)
        
        # 更新底盘进度条范围
        self.chassis_progress_slider.setRange(0, len(test_path) - 1)
        
        # 测试机械臂姿态
        test_left_joints = [0, -30, -60, -90, 0, 0]
        test_right_joints = [0, 30, 60, 90, 0, 0]
        self.arm_sim.set_left_arm_joints(test_left_joints)
        self.arm_sim.set_right_arm_joints(test_right_joints)
        
        self.log_message.emit("加载测试数据完成 - 网格尺寸: 250mm", "SUCCESS")
    
    def update_progress_display(self):
        """更新进度显示（自动同步）"""
        if self.chassis_animation_playing and not self.chassis_sim.is_manual_seeking:
            # 底盘动画播放时，自动更新进度条
            if self.chassis_sim.path_points:
                progress = self.chassis_sim.current_path_index
                max_progress = len(self.chassis_sim.path_points) - 1
                if max_progress > 0:
                    slider_value = int(progress * self.chassis_progress_slider.maximum() / max_progress)
                    self.chassis_progress_slider.blockSignals(True)  # 阻止信号，避免循环
                    self.chassis_progress_slider.setValue(slider_value)
                    self.chassis_progress_slider.blockSignals(False)
                    
                    # 更新百分比显示
                    percent = int(progress * 100 / max_progress) if max_progress > 0 else 0
                    self.chassis_progress_label.setText(f"{percent}%")
    
    # 底盘动画控制
    def play_chassis_animation(self):
        """播放底盘动画"""
        if not self.chassis_animation_playing:
            self.chassis_animation_playing = True
            self.chassis_sim.start_animation()
            self.chassis_play_button.setText("暂停 播放中...")
            self.log_message.emit("开始播放底盘仿真动画", "INFO")
    
    def pause_chassis_animation(self):
        """暂停底盘动画"""
        if self.chassis_animation_playing:
            self.chassis_animation_playing = False
            self.chassis_sim.stop_animation()
            self.chassis_play_button.setText("播放 播放底盘")
            self.log_message.emit("暂停底盘仿真动画", "INFO")
    
    def stop_chassis_animation(self):
        """停止底盘动画"""
        self.chassis_animation_playing = False
        self.chassis_sim.stop_animation()
        self.chassis_sim.current_path_index = 0
        self.chassis_play_button.setText("播放 播放底盘")
        self.chassis_progress_slider.setValue(0)
        self.log_message.emit("停止底盘仿真动画", "INFO")
    
    def reset_chassis_animation(self):
        """重置底盘动画"""
        self.stop_chassis_animation()
        self.load_test_data()
        self.log_message.emit("重置底盘仿真状态", "INFO")
    
    def update_chassis_speed(self, value):
        """更新底盘速度"""
        speed = value / 100.0
        self.chassis_speed_label.setText(f"{speed:.1f}x")
        # 实际更新底盘动画速度
        self.chassis_sim.set_animation_speed(value)
    
    def chassis_seek_start(self):
        """开始拖动底盘进度条"""
        self.chassis_sim.is_manual_seeking = True
    
    def chassis_seek_end(self):
        """结束拖动底盘进度条"""
        self.chassis_sim.is_manual_seeking = False
    
    def update_chassis_progress(self, value):
        """更新底盘进度"""
        if self.chassis_sim.path_points:
            # 将进度值转换为路径点索引
            max_index = len(self.chassis_sim.path_points) - 1
            index = int(value * max_index / self.chassis_progress_slider.maximum())
            
            # 更新显示
            progress_percent = int(value * 100 / self.chassis_progress_slider.maximum())
            self.chassis_progress_label.setText(f"{progress_percent}%")
            
            # 如果正在手动拖动，立即跳转到对应位置
            if self.chassis_sim.is_manual_seeking:
                self.chassis_sim.seek_to_position(index)
    
    # 机械臂动画控制
    def play_arm_animation(self):
        """播放机械臂动画"""
        if not self.arm_animation_playing:
            self.arm_animation_playing = True
            self.arm_play_button.setText("暂停 播放中...")
            self.log_message.emit("开始播放机械臂仿真动画", "INFO")
            # TODO: 实现机械臂动画播放逻辑
    
    def pause_arm_animation(self):
        """暂停机械臂动画"""
        if self.arm_animation_playing:
            self.arm_animation_playing = False
            self.arm_play_button.setText("播放 播放机械臂")
            self.log_message.emit("暂停机械臂仿真动画", "INFO")
    
    def stop_arm_animation(self):
        """停止机械臂动画"""
        self.arm_animation_playing = False
        self.arm_play_button.setText("播放 播放机械臂")
        self.arm_progress_slider.setValue(0)
        self.log_message.emit("停止机械臂仿真动画", "INFO")
    
    def reset_arm_animation(self):
        """重置机械臂动画"""
        self.stop_arm_animation()
        self.load_test_data()
        self.log_message.emit("重置机械臂仿真状态", "INFO")
    
    def update_arm_speed(self, value):
        """更新机械臂速度"""
        speed = value / 100.0
        self.arm_speed_label.setText(f"{speed:.1f}x")
        # TODO: 实际更新机械臂动画速度
    
    def update_arm_progress(self, value):
        """更新机械臂进度"""
        self.arm_progress_label.setText(f"{value}%")
        # TODO: 根据进度更新机械臂动画位置
    
    def load_program(self):
        """加载主控程序"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择主控程序文件", 
            "/mnt/c/xc robot/mvp-1/xc-robot/main_control",
            "Python文件 (*.py);;所有文件 (*)"
        )
        
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.log_message.emit(f"加载程序文件: {os.path.basename(file_path)}", "SUCCESS")
            
            # 分析程序文件
            try:
                result = self.program_analyzer.analyze_file(file_path)
                
                if result['success']:
                    # 获取动画序列
                    self.animation_sequence = self.program_analyzer.get_animation_sequence()
                    
                    # 更新底盘路径
                    chassis_path = self.program_analyzer.get_chassis_path()
                    if chassis_path:
                        # 转换为网格坐标（假设1个单位=1个网格）
                        grid_path = [(x/20, y/20, angle) for x, y, angle in chassis_path]
                        self.chassis_sim.set_path_points(grid_path)
                        self.log_message.emit(f"提取底盘路径点: {len(chassis_path)}个", "INFO")
                    
                    # 更新机械臂关节序列
                    left_joints = self.program_analyzer.get_arm_joint_sequence('left')
                    right_joints = self.program_analyzer.get_arm_joint_sequence('right')
                    
                    if left_joints:
                        self.arm_sim.set_left_arm_joints(left_joints[0])
                        self.log_message.emit(f"提取左臂动作: {len(left_joints)}个", "INFO")
                    
                    if right_joints:
                        self.arm_sim.set_right_arm_joints(right_joints[0])
                        self.log_message.emit(f"提取右臂动作: {len(right_joints)}个", "INFO")
                    
                    # 更新进度条范围
                    if self.animation_sequence:
                        self.chassis_progress_slider.setRange(0, len(chassis_path) - 1 if chassis_path else 0)
                        self.arm_progress_slider.setRange(0, max(len(left_joints), len(right_joints)) - 1 if (left_joints or right_joints) else 0)
                        self.log_message.emit(f"总动作数: {len(self.animation_sequence)}", "SUCCESS")
                    
                    self.log_message.emit("程序分析完成", "SUCCESS")
                    
                else:
                    self.log_message.emit(f"程序分析失败: {result.get('error', '未知错误')}", "ERROR")
                    
            except Exception as e:
                self.log_message.emit(f"程序分析异常: {str(e)}", "ERROR")
                
        else:
            self.log_message.emit("未选择程序文件", "WARNING")
    
    def toggle_xy_direction(self):
        """切换X/Y轴方向"""
        self.chassis_sim.toggle_xy_direction()
        self.log_message.emit("已切换X/Y轴方向", "INFO")
    
    def rotate_chassis_90(self):
        """底盘矩形旋转90度"""
        self.chassis_sim.rotate_chassis_90()
        self.log_message.emit("底盘矩形已旋转90度", "INFO")
    
    def clear_chassis_path(self):
        """清除底盘路径"""
        self.chassis_sim.clear_path()
        # 重置进度条
        self.chassis_progress_slider.setValue(0)
        self.chassis_progress_label.setText("0%")
        # 停止动画
        self.stop_chassis_animation()
        self.log_message.emit("已清除底盘路径", "INFO")
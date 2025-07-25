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
        self.setMinimumSize(400, 400)  # 增加最小高度，给网格更多空间
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
            # 先绘制包围矩形
            self.draw_path_bounding_box(painter)
            
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
    
    def draw_path_bounding_box(self, painter):
        """绘制路径的最小包围矩形"""
        bbox = self.calculate_path_bounding_box()
        if not bbox:
            return
            
        # 绘制包围矩形（虚线）
        painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        
        rect_x = bbox['min_x'] * self.grid_size
        rect_y = bbox['min_y'] * self.grid_size
        rect_w = bbox['width'] * self.grid_size
        rect_h = bbox['height'] * self.grid_size
        
        painter.drawRect(rect_x, rect_y, rect_w, rect_h)
        
        # 绘制尺寸标注
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Arial", 8))
        
        # 宽度标注（顶部）
        width_text = f"{bbox['width_mm']/1000:.2f}m"
        text_x = rect_x + rect_w // 2 - 20
        text_y = rect_y - 5
        painter.drawText(text_x, text_y, width_text)
        
        # 高度标注（右侧）
        height_text = f"{bbox['height_mm']/1000:.2f}m"
        text_x = rect_x + rect_w + 5
        text_y = rect_y + rect_h // 2
        painter.drawText(text_x, text_y, height_text)
        
        # 绘制尺寸线
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        
        # 宽度尺寸线
        painter.drawLine(rect_x, rect_y - 3, rect_x + rect_w, rect_y - 3)
        painter.drawLine(rect_x, rect_y - 6, rect_x, rect_y)
        painter.drawLine(rect_x + rect_w, rect_y - 6, rect_x + rect_w, rect_y)
        
        # 高度尺寸线
        painter.drawLine(rect_x + rect_w + 3, rect_y, rect_x + rect_w + 3, rect_y + rect_h)
        painter.drawLine(rect_x + rect_w, rect_y, rect_x + rect_w + 6, rect_y)
        painter.drawLine(rect_x + rect_w, rect_y + rect_h, rect_x + rect_w + 6, rect_y + rect_h)
    
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
    
    def calculate_path_bounding_box(self):
        """计算路径的最小包围矩形"""
        if len(self.path_points) < 2:
            return None
            
        # 获取所有路径点的坐标
        x_coords = [point[0] for point in self.path_points]
        y_coords = [point[1] for point in self.path_points]
        
        # 计算包围矩形
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)
        
        # 返回包围矩形的信息
        return {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'width': max_x - min_x,
            'height': max_y - min_y,
            'width_mm': (max_x - min_x) * self.grid_real_size,
            'height_mm': (max_y - min_y) * self.grid_real_size
        }
    
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
    """机械臂仿真显示区域 - 火柴人风格"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 500)
        
        # FR3机械臂精确尺寸参数 (基于参考图)
        self.arm_dimensions = {
            'base_to_j2': 140,      # 底座到J2摆动轴 (mm)
            'j2_to_j3': 280,        # J2摆动轴中心到J3旋转轴中心 (mm)  
            'j4_to_j6': 102,        # J4摆动轴中心线和J6旋转轴中轴线间距 (mm)
            'j3_offset': 240,       # J3到J4的偏移距离 (估算)
            'j5_offset': 100,       # J5到J6的偏移距离 (估算)
            'end_effector': 50,     # 末端执行器长度 (估算)
        }
        
        # 机器人整体结构配置 (基于参考图)
        self.robot_structure = {
            'chest_width': 380,     # 胸部宽度 (mm)
            'chest_length': 350,    # 胸部长度 (mm) 
            'chest_height': 200,    # 胸部高度 (mm)
            'base_separation': 380, # 两臂间距 (mm)
            'chassis_width': 455,   # 底盘宽度 (mm)
            'chassis_length': 550,  # 底盘长度 (mm)
            'lift_column_height': 800, # 升降轴高度 (mm)
            'lift_column_width': 150,  # 升降轴宽度 (mm)
        }
        
        # 关节角度 (度)
        self.left_arm_joints = [0, -30, -60, -90, 0, 0]   # 默认姿态
        self.right_arm_joints = [0, 30, 60, 90, 0, 0]     # 默认姿态
        
        # 运动轨迹
        self.left_arm_trajectory = []   # 左臂轨迹
        self.right_arm_trajectory = []  # 右臂轨迹
        self.trajectory_index = 0       # 当前轨迹索引
        
        # 显示设置
        self.scale = 0.5           # 缩放比例（调小以适应完整结构）
        self.view_angle_x = 25     # X轴视角
        self.view_angle_y = 30     # Y轴视角
        
        # 关节和连杆显示尺寸
        self.joint_size = 8        # 关节方块尺寸（调小以匹配缩放）
        self.link_thickness = 4    # 连杆粗细（调小以匹配缩放）
        
    def paintEvent(self, event):
        """绘制机械臂仿真 - 火柴人风格"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置背景
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        # 设置坐标系中心
        center_x = self.width() // 2
        center_y = self.height() // 2 + 100  # 下移更多以显示完整机器人
        painter.translate(center_x, center_y)
        
        # 绘制地面网格
        self.draw_ground_grid(painter)
        
        # 绘制胸部和基座
        self.draw_robot_base(painter)
        
        # 计算机械臂基座位置（在胸部顶部）
        arm_base_y = 100 - self.robot_structure['lift_column_height'] * self.scale - self.robot_structure['chest_height'] * self.scale
        
        # 绘制左臂（火柴人风格）
        left_base_pos = [-self.robot_structure['base_separation'] // 2 * self.scale, arm_base_y, 0]
        self.draw_arm_stick_figure(painter, left_base_pos, self.left_arm_joints, "左臂", QColor(50, 150, 255))
        
        # 绘制右臂（火柴人风格）
        right_base_pos = [self.robot_structure['base_separation'] // 2 * self.scale, arm_base_y, 0]
        self.draw_arm_stick_figure(painter, right_base_pos, self.right_arm_joints, "右臂", QColor(255, 100, 100))
        
        # 绘制信息面板
        self.draw_info_panel(painter)
    
    def project_3d_to_2d(self, x, y, z):
        """3D坐标投影到2D显示"""
        import math
        
        # 简化的等轴投影
        angle_x = math.radians(self.view_angle_x)
        angle_y = math.radians(self.view_angle_y)
        
        # 旋转投影
        x_2d = x * math.cos(angle_y) + z * math.sin(angle_y)
        y_2d = -y * math.cos(angle_x) - (x * math.sin(angle_y) - z * math.cos(angle_y)) * math.sin(angle_x)
        
        return int(x_2d), int(y_2d)
    
    def draw_ground_grid(self, painter):
        """绘制地面网格"""
        painter.save()
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        grid_size = 50
        grid_count = 10
        
        # 绘制网格线
        for i in range(-grid_count, grid_count + 1):
            x = i * grid_size
            # 水平线
            x1, y1 = self.project_3d_to_2d(-grid_count * grid_size, 100, x)
            x2, y2 = self.project_3d_to_2d(grid_count * grid_size, 100, x)
            painter.drawLine(x1, y1, x2, y2)
            
            # 垂直线
            x1, y1 = self.project_3d_to_2d(x, 100, -grid_count * grid_size)
            x2, y2 = self.project_3d_to_2d(x, 100, grid_count * grid_size)
            painter.drawLine(x1, y1, x2, y2)
        
        painter.restore()
    
    def draw_robot_base(self, painter):
        """绘制机器人基座和胸部 - 基于参考图优化"""
        painter.save()
        
        struct = self.robot_structure
        scale = self.scale
        
        # 1. 绘制底盘 (455mm x 550mm)
        self.draw_chassis_base(painter, struct, scale)
        
        # 2. 绘制升降轴
        self.draw_lift_column(painter, struct, scale)
        
        # 3. 绘制胸部结构 (380mm x 350mm)
        self.draw_chest_structure(painter, struct, scale)
        
        # 4. 绘制机械臂基座接口
        self.draw_arm_mounts(painter, struct, scale)
        
        painter.restore()
    
    def draw_chassis_base(self, painter, struct, scale):
        """绘制底盘基座"""
        chassis_w = int(struct['chassis_width'] * scale)
        chassis_l = int(struct['chassis_length'] * scale)
        
        # 底盘3D坐标
        base_y = 100  # 地面高度
        chassis_corners = [
            [-chassis_w//2, base_y, -chassis_l//2],  # 左前
            [chassis_w//2, base_y, -chassis_l//2],   # 右前
            [chassis_w//2, base_y, chassis_l//2],    # 右后
            [-chassis_w//2, base_y, chassis_l//2],   # 左后
        ]
        
        # 绘制底盘
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(180, 180, 190)))
        
        chassis_points = []
        for corner in chassis_corners:
            x, y = self.project_3d_to_2d(*corner)
            chassis_points.append(QPoint(x, y))
        painter.drawPolygon(chassis_points)
        
        # 底盘标识
        center_x, center_y = self.project_3d_to_2d(0, base_y, 0)
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(center_x - 30, center_y + 5, f"底盘: {struct['chassis_width']}×{struct['chassis_length']}mm")
    
    def draw_lift_column(self, painter, struct, scale):
        """绘制升降轴"""
        column_w = int(struct['lift_column_width'] * scale)
        column_h = int(struct['lift_column_height'] * scale)
        
        # 升降轴坐标
        column_corners = [
            [-column_w//2, 100, -column_w//2],          # 底部左前
            [column_w//2, 100, -column_w//2],           # 底部右前
            [column_w//2, 100-column_h, -column_w//2],  # 顶部右前
            [-column_w//2, 100-column_h, -column_w//2], # 顶部左前
            [-column_w//2, 100, column_w//2],           # 底部左后
            [column_w//2, 100-column_h, column_w//2],   # 顶部右后
        ]
        
        # 绘制升降轴主体
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.setBrush(QBrush(QColor(140, 140, 150)))
        
        # 前面
        front_points = []
        for corner in column_corners[:4]:
            x, y = self.project_3d_to_2d(*corner)
            front_points.append(QPoint(x, y))
        painter.drawPolygon(front_points)
        
        # 侧面
        painter.setBrush(QBrush(QColor(120, 120, 130)))
        side_points = [
            QPoint(*self.project_3d_to_2d(*column_corners[1])),
            QPoint(*self.project_3d_to_2d(*column_corners[2])),
            QPoint(*self.project_3d_to_2d(*column_corners[5])),
            QPoint(*self.project_3d_to_2d(column_corners[1][0], column_corners[1][1], column_corners[4][2]))
        ]
        painter.drawPolygon(side_points)
    
    def draw_chest_structure(self, painter, struct, scale):
        """绘制胸部结构"""
        chest_w = int(struct['chest_width'] * scale)
        chest_l = int(struct['chest_length'] * scale) 
        chest_h = int(struct['chest_height'] * scale)
        
        # 胸部位置（在升降轴顶部）
        chest_base_y = 100 - struct['lift_column_height'] * scale
        
        chest_corners = [
            [-chest_w//2, chest_base_y, -chest_l//2],          # 底部左前
            [chest_w//2, chest_base_y, -chest_l//2],           # 底部右前
            [chest_w//2, chest_base_y, chest_l//2],            # 底部右后
            [-chest_w//2, chest_base_y, chest_l//2],           # 底部左后
            [-chest_w//2, chest_base_y-chest_h, -chest_l//2],  # 顶部左前
            [chest_w//2, chest_base_y-chest_h, -chest_l//2],   # 顶部右前
            [chest_w//2, chest_base_y-chest_h, chest_l//2],    # 顶部右后
            [-chest_w//2, chest_base_y-chest_h, chest_l//2],   # 顶部左后
        ]
        
        # 绘制胸部主体
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(220, 220, 230)))
        
        # 前面
        front_points = []
        for corner in [chest_corners[0], chest_corners[1], chest_corners[5], chest_corners[4]]:
            x, y = self.project_3d_to_2d(*corner)
            front_points.append(QPoint(x, y))
        painter.drawPolygon(front_points)
        
        # 顶面
        painter.setBrush(QBrush(QColor(190, 190, 200)))
        top_points = []
        for corner in chest_corners[4:8]:
            x, y = self.project_3d_to_2d(*corner)
            top_points.append(QPoint(x, y))
        painter.drawPolygon(top_points)
        
        # 胸部标识
        center_x, center_y = self.project_3d_to_2d(0, chest_base_y - chest_h//2, 0)
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(center_x - 30, center_y + 5, "FR3 双臂系统")
    
    def draw_arm_mounts(self, painter, struct, scale):
        """绘制机械臂基座接口"""
        mount_size = int(30 * scale)
        mount_y = 100 - struct['lift_column_height'] * scale - struct['chest_height'] * scale
        
        # 左臂基座
        left_mount_x = -struct['base_separation'] * scale // 2
        left_center = self.project_3d_to_2d(left_mount_x, mount_y, 0)
        
        # 右臂基座
        right_mount_x = struct['base_separation'] * scale // 2
        right_center = self.project_3d_to_2d(right_mount_x, mount_y, 0)
        
        # 绘制基座接口
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        
        for center, label in [(left_center, "左臂"), (right_center, "右臂")]:
            # 确保坐标为整数
            cx, cy = int(center[0]), int(center[1])
            painter.drawEllipse(cx - mount_size//2, cy - mount_size//2, 
                               mount_size, mount_size)
            
            # 基座标签
            painter.setPen(QPen(QColor(50, 50, 50)))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(cx - 15, cy + 25, label + "基座")
    
    def draw_arm_stick_figure(self, painter, base_pos, joints, arm_name, color):
        """绘制火柴人风格机械臂"""
        painter.save()
        
        # 计算正向运动学
        positions = self.calculate_forward_kinematics(base_pos, joints)
        
        # 绘制连杆（火柴棍）
        painter.setPen(QPen(color, self.link_thickness))
        for i in range(len(positions) - 1):
            x1, y1 = self.project_3d_to_2d(*positions[i])
            x2, y2 = self.project_3d_to_2d(*positions[i + 1])
            painter.drawLine(x1, y1, x2, y2)
        
        # 绘制关节（方块）
        painter.setBrush(QBrush(color.darker(120)))
        painter.setPen(QPen(color.darker(150), 2))
        
        for i, pos in enumerate(positions):
            x, y = self.project_3d_to_2d(*pos)
            size = self.joint_size
            painter.drawRect(x - size//2, y - size//2, size, size)
            
            # 绘制关节标签
            if i < len(joints):
                painter.setPen(QPen(QColor(50, 50, 50)))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(x + size//2 + 3, y - size//2, f"J{i+1}")
                painter.drawText(x + size//2 + 3, y + size//2, f"{joints[i]:.0f}°")
                painter.setPen(QPen(color.darker(150), 2))
        
        # 绘制末端执行器
        if len(positions) > 0:
            end_pos = positions[-1]
            x, y = self.project_3d_to_2d(*end_pos)
            painter.setBrush(QBrush(QColor(255, 200, 50)))
            painter.drawEllipse(x - 8, y - 8, 16, 16)
        
        # 绘制机械臂名称
        if len(positions) > 0:
            base_x, base_y = self.project_3d_to_2d(*base_pos)
            painter.setPen(QPen(color))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(base_x - 20, base_y - 30, arm_name)
        
        painter.restore()
    
    def calculate_forward_kinematics(self, base_pos, joints):
        """计算正向运动学 - 基于精确FR3尺寸"""
        import math
        
        positions = []
        scale = self.scale
        dims = self.arm_dimensions
        
        # 起始位置
        x, y, z = base_pos[0], base_pos[1], base_pos[2]
        positions.append([x, y, z])
        
        # 关节角度转换
        theta1 = math.radians(joints[0])  # J1基座旋转
        theta2 = math.radians(joints[1])  # J2肩部摆动
        theta3 = math.radians(joints[2])  # J3肘部旋转
        theta4 = math.radians(joints[3])  # J4腕部摆动1
        theta5 = math.radians(joints[4])  # J5腕部旋转
        theta6 = math.radians(joints[5])  # J6腕部摆动2
        
        # J1位置 (基座旋转，位置不变)
        positions.append([x, y, z])
        
        # J2位置 (底座到J2摆动轴: 140mm)
        y2 = y - dims['base_to_j2'] * scale
        positions.append([x, y2, z])
        
        # J3位置 (J2摆动轴中心到J3旋转轴中心: 280mm)
        # 考虑J2的摆动角度
        j3_x = x + dims['j2_to_j3'] * scale * math.cos(theta1) * math.sin(theta2)
        j3_y = y2 - dims['j2_to_j3'] * scale * math.cos(theta2)
        j3_z = z + dims['j2_to_j3'] * scale * math.sin(theta1) * math.sin(theta2)
        positions.append([j3_x, j3_y, j3_z])
        
        # J4位置 (J3偏移)
        # 考虑J2和J3的累积角度
        cumulative_angle = theta2 + theta3
        j4_x = j3_x + dims['j3_offset'] * scale * math.cos(theta1) * math.sin(cumulative_angle)
        j4_y = j3_y - dims['j3_offset'] * scale * math.cos(cumulative_angle)
        j4_z = j3_z + dims['j3_offset'] * scale * math.sin(theta1) * math.sin(cumulative_angle)
        positions.append([j4_x, j4_y, j4_z])
        
        # J5位置 (考虑J4摆动)
        cumulative_angle = theta2 + theta3 + theta4
        j5_x = j4_x + dims['j5_offset'] * scale * math.cos(theta1) * math.sin(cumulative_angle)
        j5_y = j4_y - dims['j5_offset'] * scale * math.cos(cumulative_angle)
        j5_z = j4_z + dims['j5_offset'] * scale * math.sin(theta1) * math.sin(cumulative_angle)
        positions.append([j5_x, j5_y, j5_z])
        
        # J6位置 (J4摆动轴中心线和J6旋转轴中轴线间距: 102mm)
        j6_x = j5_x + dims['j4_to_j6'] * scale * math.cos(theta1) * math.sin(cumulative_angle + theta5)
        j6_y = j5_y - dims['j4_to_j6'] * scale * math.cos(cumulative_angle + theta5)
        j6_z = j5_z + dims['j4_to_j6'] * scale * math.sin(theta1) * math.sin(cumulative_angle + theta5)
        positions.append([j6_x, j6_y, j6_z])
        
        # 末端执行器位置
        end_x = j6_x + dims['end_effector'] * scale * math.cos(theta1) * math.sin(cumulative_angle + theta5 + theta6)
        end_y = j6_y - dims['end_effector'] * scale * math.cos(cumulative_angle + theta5 + theta6)
        end_z = j6_z + dims['end_effector'] * scale * math.sin(theta1) * math.sin(cumulative_angle + theta5 + theta6)
        positions.append([end_x, end_y, end_z])
        
        return positions
    
    def draw_info_panel(self, painter):
        """绘制信息面板"""
        painter.save()
        painter.resetTransform()
        
        # 准备信息文本内容
        info_texts = [
            "FR3 双臂机械臂仿真",
            f"基座间距: {self.robot_structure['base_separation']}mm",
            f"胸部: {self.robot_structure['chest_width']}×{self.robot_structure['chest_length']}mm", 
            f"底盘: {self.robot_structure['chassis_width']}×{self.robot_structure['chassis_length']}mm",
            f"视角: X={self.view_angle_x}° Y={self.view_angle_y}°",
            f"缩放: {self.scale:.1f}x"
        ]
        
        # 添加轨迹信息（如果有）
        if self.left_arm_trajectory or self.right_arm_trajectory:
            info_texts.extend([
                f"轨迹点: {max(len(self.left_arm_trajectory), len(self.right_arm_trajectory))}",
                f"当前: {self.trajectory_index}"
            ])
        
        # 设置字体并计算文本尺寸
        font = QFont("Arial", 9)
        painter.setFont(font)
        fm = painter.fontMetrics()
        
        # 计算最大文本宽度
        max_text_width = 0
        for text in info_texts:
            text_width = fm.width(text)
            max_text_width = max(max_text_width, text_width)
        
        # 计算面板尺寸（自适应文字）
        padding_horizontal = 20  # 左右各10px边距
        padding_vertical = 30    # 上下边距
        line_height = fm.height()
        line_spacing = 4  # 行间距
        
        panel_w = max_text_width + padding_horizontal
        panel_h = len(info_texts) * line_height + (len(info_texts) - 1) * line_spacing + padding_vertical
        
        panel_x = 10
        panel_y = 10
        
        # 绘制面板背景
        painter.setBrush(QBrush(QColor(250, 250, 250, 220)))
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawRect(panel_x, panel_y, panel_w, panel_h)
        
        # 绘制信息文本
        painter.setPen(QPen(QColor(50, 50, 50)))
        
        y_offset = panel_y + 15 + fm.ascent()  # 从顶部开始，加上边距和字体上升高度
        
        for text in info_texts:
            painter.drawText(panel_x + 10, y_offset, text)
            y_offset += line_height + line_spacing
        
        painter.restore()
    
    def set_left_arm_joints(self, joints):
        """设置左臂关节角度"""
        self.left_arm_joints = joints[:]
        self.update()
    
    def set_right_arm_joints(self, joints):
        """设置右臂关节角度"""
        self.right_arm_joints = joints[:]
        self.update()
    
    def set_arm_trajectories(self, left_trajectory, right_trajectory):
        """设置机械臂轨迹"""
        self.left_arm_trajectory = left_trajectory[:] if left_trajectory else []
        self.right_arm_trajectory = right_trajectory[:] if right_trajectory else []
        self.trajectory_index = 0
        self.update()
    
    def update_trajectory_position(self, index):
        """更新轨迹位置"""
        if 0 <= index < len(self.left_arm_trajectory):
            self.left_arm_joints = self.left_arm_trajectory[index][:]
        if 0 <= index < len(self.right_arm_trajectory):
            self.right_arm_joints = self.right_arm_trajectory[index][:]
        self.trajectory_index = index
        self.update()
    
    def get_trajectory_length(self):
        """获取轨迹长度"""
        return max(len(self.left_arm_trajectory), len(self.right_arm_trajectory))
    
    def load_trajectory_from_program(self, program_analyzer):
        """从程序分析器加载轨迹"""
        try:
            # 获取左臂和右臂轨迹
            left_trajectory = program_analyzer.get_arm_joint_sequence('left')
            right_trajectory = program_analyzer.get_arm_joint_sequence('right')
            
            if left_trajectory or right_trajectory:
                self.set_arm_trajectories(left_trajectory, right_trajectory)
                return True
        except Exception as e:
            print(f"加载轨迹失败: {e}")
        
        return False

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
        chassis_group.setStyleSheet("QGroupBox::title { font-size: 15px; font-weight: bold; }")
        chassis_layout = QVBoxLayout(chassis_group)
        
        # 底盘仿真控制按钮（紧凑布局）
        chassis_title_layout = QHBoxLayout()
        chassis_title_layout.setSpacing(5)  # 减少间距
        chassis_title_layout.setContentsMargins(0, 0, 0, 5)  # 减少边距
        
        # X/Y方向切换按钮
        self.xy_toggle_button = QPushButton("X/Y切换")
        self.xy_toggle_button.setToolTip("切换X轴和Y轴方向")
        self.xy_toggle_button.setMaximumWidth(70)
        self.xy_toggle_button.setMaximumHeight(25)
        
        # 90度旋转按钮
        self.rotate_90_button = QPushButton("90°旋转")
        self.rotate_90_button.setToolTip("底盘矩形围绕质心旋转90度")
        self.rotate_90_button.setMaximumWidth(70)
        self.rotate_90_button.setMaximumHeight(25)
        
        # 清除路径按钮
        self.clear_path_button = QPushButton("清除路径")
        self.clear_path_button.setToolTip("一键清除底盘运动仿真中的蓝色路径线条")
        self.clear_path_button.setMaximumWidth(70)
        self.clear_path_button.setMaximumHeight(25)
        
        # 设置按钮字体（更小更紧凑）
        button_font = QFont()
        # 使用默认字体避免警告
        button_font.setPointSize(9)
        self.xy_toggle_button.setFont(button_font)
        self.rotate_90_button.setFont(button_font)
        self.clear_path_button.setFont(button_font)
        
        chassis_title_layout.addWidget(self.xy_toggle_button)
        chassis_title_layout.addWidget(self.rotate_90_button)
        chassis_title_layout.addWidget(self.clear_path_button)
        
        # 添加紧凑的提示文字
        help_label = QLabel("拖拽鼠标绘制路径")
        help_label.setStyleSheet("color: #666; font-size: 9px; margin: 0px; padding: 2px; font-style: italic;")
        chassis_title_layout.addWidget(help_label)
        
        # 添加弹性空间，让按钮靠左
        chassis_title_layout.addStretch()
        
        chassis_layout.addLayout(chassis_title_layout)
        
        self.chassis_sim = ChassisSimulationWidget()
        chassis_layout.addWidget(self.chassis_sim)
        
        # 右侧：机械臂仿真
        arm_group = QGroupBox("机械臂运动仿真")
        arm_group.setStyleSheet("QGroupBox::title { font-size: 15px; font-weight: bold; }")
        arm_layout = QVBoxLayout(arm_group)
        self.arm_sim = ArmSimulationWidget()
        arm_layout.addWidget(self.arm_sim)
        
        display_layout.addWidget(chassis_group)
        display_layout.addWidget(arm_group)
        
        # 控制面板 - 分为两个部分
        control_layout = QHBoxLayout()
        
        # 底盘控制面板
        chassis_control_group = QGroupBox("底盘仿真控制")
        chassis_control_group.setStyleSheet("QGroupBox::title { font-size: 15px; font-weight: bold; }")
        chassis_control_layout = QVBoxLayout(chassis_control_group)
        
        # 底盘播放控制按钮
        chassis_button_layout = QHBoxLayout()
        self.chassis_play_button = QPushButton("播放底盘")
        self.chassis_pause_button = QPushButton("暂停")
        self.chassis_stop_button = QPushButton("停止")
        self.chassis_reset_button = QPushButton("重置")
        
        # 设置按钮字体（Mac优先）
        button_font = QFont()
        # 使用默认字体避免警告
        button_font.setPointSize(11)
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
        arm_control_group.setStyleSheet("QGroupBox::title { font-size: 15px; font-weight: bold; }")
        arm_control_layout = QVBoxLayout(arm_control_group)
        
        # 机械臂播放控制按钮
        arm_button_layout = QHBoxLayout()
        self.arm_play_button = QPushButton("播放机械臂")
        self.arm_pause_button = QPushButton("暂停")
        self.arm_stop_button = QPushButton("停止")
        self.arm_reset_button = QPushButton("重置")
        
        # 设置机械臂按钮字体（Mac优先）
        arm_button_font = QFont()
        # 使用默认字体避免警告
        arm_button_font.setPointSize(11)
        for btn in [self.arm_play_button, self.arm_pause_button, 
                   self.arm_stop_button, self.arm_reset_button]:
            btn.setFont(arm_button_font)
        
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
        
        # 设置文件加载按钮字体
        load_button_font = QFont()
        # 使用默认字体避免警告
        load_button_font.setPointSize(11)
        self.load_button.setFont(load_button_font)
        
        self.file_label = QLabel("未选择文件")
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        
        # 设置主布局的拉伸比例，让显示区域占更多空间
        layout.addLayout(display_layout, 4)  # 显示区域占4份
        layout.addLayout(control_layout, 1)  # 控制区域占1份
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
            trajectory_length = self.arm_sim.get_trajectory_length()
            if trajectory_length > 0:
                self.arm_animation_playing = True
                self.arm_play_button.setText("暂停 播放中...")
                self.log_message.emit("开始播放机械臂仿真动画", "INFO")
                
                # 启动机械臂动画定时器
                if not hasattr(self, 'arm_animation_timer'):
                    self.arm_animation_timer = QTimer()
                    self.arm_animation_timer.timeout.connect(self.update_arm_animation)
                
                interval = max(50, int(200 * 100 / self.arm_speed_slider.value()))
                self.arm_animation_timer.start(interval)
            else:
                self.log_message.emit("没有机械臂轨迹数据", "WARNING")
    
    def pause_arm_animation(self):
        """暂停机械臂动画"""
        if self.arm_animation_playing:
            self.arm_animation_playing = False
            self.arm_play_button.setText("播放 播放机械臂")
            if hasattr(self, 'arm_animation_timer'):
                self.arm_animation_timer.stop()
            self.log_message.emit("暂停机械臂仿真动画", "INFO")
    
    def stop_arm_animation(self):
        """停止机械臂动画"""
        self.arm_animation_playing = False
        self.arm_play_button.setText("播放 播放机械臂")
        if hasattr(self, 'arm_animation_timer'):
            self.arm_animation_timer.stop()
        self.arm_progress_slider.setValue(0)
        self.arm_sim.update_trajectory_position(0)
        self.log_message.emit("停止机械臂仿真动画", "INFO")
    
    def reset_arm_animation(self):
        """重置机械臂动画"""
        self.stop_arm_animation()
        # 重置到默认姿态
        self.arm_sim.set_left_arm_joints([0, -30, -60, -90, 0, 0])
        self.arm_sim.set_right_arm_joints([0, 30, 60, 90, 0, 0])
        self.log_message.emit("重置机械臂仿真状态", "INFO")
    
    def update_arm_animation(self):
        """更新机械臂动画"""
        trajectory_length = self.arm_sim.get_trajectory_length()
        if trajectory_length > 0:
            current_progress = self.arm_progress_slider.value()
            next_progress = current_progress + 1
            
            if next_progress <= 100:
                self.arm_progress_slider.setValue(next_progress)
                # update_arm_progress方法会自动更新轨迹位置
            else:
                # 动画结束
                self.stop_arm_animation()
    
    def update_arm_speed(self, value):
        """更新机械臂速度"""
        speed = value / 100.0
        self.arm_speed_label.setText(f"{speed:.1f}x")
        
        # 实际更新机械臂动画速度
        if hasattr(self, 'arm_animation_timer') and self.arm_animation_timer.isActive():
            interval = max(50, int(200 * 100 / value))
            self.arm_animation_timer.start(interval)
    
    def update_arm_progress(self, value):
        """更新机械臂进度"""
        self.arm_progress_label.setText(f"{value}%")
        
        # 根据进度更新机械臂轨迹位置
        trajectory_length = self.arm_sim.get_trajectory_length()
        if trajectory_length > 0:
            index = int(value * trajectory_length / 100)
            if 0 <= index < trajectory_length:
                self.arm_sim.update_trajectory_position(index)
    
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
                    
                    # 加载机械臂轨迹到新的仿真系统
                    if self.arm_sim.load_trajectory_from_program(self.program_analyzer):
                        trajectory_length = self.arm_sim.get_trajectory_length()
                        self.log_message.emit(f"加载机械臂轨迹: {trajectory_length}个动作点", "SUCCESS")
                        
                        # 更新进度条范围
                        self.arm_progress_slider.setRange(0, 100)
                        self.arm_progress_slider.setValue(0)
                    else:
                        # 使用默认轨迹进行演示
                        demo_left = [[0, -30, -60, -90, 0, 0], [15, -45, -75, -105, 15, 15]]
                        demo_right = [[0, 30, 60, 90, 0, 0], [-15, 45, 75, 105, -15, -15]]
                        self.arm_sim.set_arm_trajectories(demo_left, demo_right)
                        self.log_message.emit("使用默认演示轨迹", "INFO")
                    
                    # 更新底盘进度条范围
                    if self.animation_sequence and chassis_path:
                        self.chassis_progress_slider.setRange(0, len(chassis_path) - 1)
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
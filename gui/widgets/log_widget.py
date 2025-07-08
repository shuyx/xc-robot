#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志显示控件 - 精简版
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

class LogWidget(QWidget):
    """日志显示控件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        # 日志级别过滤
        self.level_combo = QComboBox()
        self.level_combo.addItems(["全部", "INFO", "SUCCESS", "WARNING", "ERROR"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        
        # 清空和保存按钮
        self.clear_btn = QPushButton("清空")
        self.save_btn = QPushButton("保存")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.save_btn.clicked.connect(self.save_logs)
        
        # 自动滚动
        self.auto_scroll_cb = QCheckBox("自动滚动")
        self.auto_scroll_cb.setChecked(True)
        
        toolbar.addWidget(QLabel("级别:"))
        toolbar.addWidget(self.level_combo)
        toolbar.addWidget(self.clear_btn)
        toolbar.addWidget(self.save_btn)
        toolbar.addWidget(self.auto_scroll_cb)
        toolbar.addStretch()
        
        # 行数统计
        self.count_label = QLabel("行数: 0")
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # 日志显示区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        # 使用系统默认字体，避免字体警告
        font = QFont()
        font.setPointSize(9)
        self.log_display.setFont(font)
        layout.addWidget(self.log_display)
        
        # 初始化行数统计
        self.line_count = 0
    
    def add_message(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 设置颜色
        color = self.get_level_color(level)
        self.log_display.setTextColor(QColor(color))
        
        # 添加消息
        log_line = f"[{timestamp}] [{level}] {message}"
        self.log_display.append(log_line)
        
        # 更新行数
        self.line_count += 1
        self.update_count()
        
        # 自动滚动到底部
        if self.auto_scroll_cb.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_display.setTextCursor(cursor)
    
    def get_level_color(self, level: str) -> str:
        """获取日志级别对应的颜色"""
        colors = {
            'INFO': 'black',
            'SUCCESS': 'green',
            'WARNING': 'orange',
            'ERROR': 'red',
            'DEBUG': 'gray'
        }
        return colors.get(level, 'black')
    
    def filter_logs(self):
        """过滤日志（简化版）"""
        # 这里可以添加更复杂的过滤逻辑
        # 当前版本只更新显示状态
        pass
    
    def update_count(self):
        """更新行数统计"""
        self.count_label.setText(f"行数: {self.line_count}")
    
    def clear_logs(self):
        """清空日志"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有日志吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_display.clear()
            self.line_count = 0
            self.update_count()
    
    def save_logs(self):
        """保存日志"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存日志", 
            f"xc_robot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("XC-ROBOT 日志导出\n")
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.log_display.toPlainText())
                
                QMessageBox.information(self, "保存成功", f"日志已保存到:\n{filename}")
                
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"保存日志时出错:\n{str(e)}")
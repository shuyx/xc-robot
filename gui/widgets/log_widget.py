#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志显示控件
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
        self.log_buffer = []
        self.max_lines = 1000  # 最大显示行数
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 日志级别过滤
        self.level_combo = QComboBox()
        self.level_combo.addItems(["全部", "INFO", "SUCCESS", "WARNING", "ERROR"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索日志...")
        self.search_edit.textChanged.connect(self.filter_logs)
        
        # 清空按钮
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_logs)
        
        # 保存按钮
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_logs)
        
        # 自动滚动复选框
        self.auto_scroll_cb = QCheckBox("自动滚动")
        self.auto_scroll_cb.setChecked(True)
        
        toolbar_layout.addWidget(QLabel("级别:"))
        toolbar_layout.addWidget(self.level_combo)
        toolbar_layout.addWidget(self.search_edit)
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.auto_scroll_cb)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 日志显示区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_display)
        
        # 状态显示
        status_layout = QHBoxLayout()
        
        self.line_count_label = QLabel("行数: 0")
        self.filter_count_label = QLabel("显示: 0")
        
        status_layout.addWidget(self.line_count_label)
        status_layout.addWidget(self.filter_count_label)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
    
    def add_message(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message,
            'full_text': f"[{timestamp}] [{level.upper()}] {message}"
        }
        
        self.log_buffer.append(log_entry)
        
        # 限制缓冲区大小
        if len(self.log_buffer) > self.max_lines:
            self.log_buffer.pop(0)
        
        # 更新显示
        self.update_display()
        
        # 更新统计
        self.update_stats()
    
    def update_display(self):
        """更新显示"""
        # 获取过滤后的日志
        filtered_logs = self.get_filtered_logs()
        
        # 清空并重新添加
        self.log_display.clear()
        
        for log_entry in filtered_logs:
            self.append_log_entry(log_entry)
        
        # 自动滚动到底部
        if self.auto_scroll_cb.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_display.setTextCursor(cursor)
    
    def append_log_entry(self, log_entry: dict):
        """添加单条日志到显示区域"""
        # 设置颜色
        color = self.get_level_color(log_entry['level'])
        
        # 格式化显示
        self.log_display.setTextColor(QColor(color))
        self.log_display.append(log_entry['full_text'])
    
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
    
    def get_filtered_logs(self) -> list:
        """获取过滤后的日志"""
        level_filter = self.level_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        filtered = []
        for log_entry in self.log_buffer:
            # 级别过滤
            if level_filter != "全部" and log_entry['level'] != level_filter:
                continue
            
            # 搜索过滤
            if search_text and search_text not in log_entry['full_text'].lower():
                continue
            
            filtered.append(log_entry)
        
        return filtered
    
    def filter_logs(self):
        """过滤日志"""
        self.update_display()
        self.update_stats()
    
    def update_stats(self):
        """更新统计信息"""
        total_lines = len(self.log_buffer)
        filtered_lines = len(self.get_filtered_logs())
        
        self.line_count_label.setText(f"总行数: {total_lines}")
        self.filter_count_label.setText(f"显示: {filtered_lines}")
    
    def clear_logs(self):
        """清空日志"""
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有日志吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_buffer.clear()
            self.log_display.clear()
            self.update_stats()
    
    def save_logs(self):
        """保存日志"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存日志", 
            f"xc_robot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if filename:
            self.save_to_file(filename)
    
    def save_to_file(self, filename: str):
        """保存到文件"""
        try:
            filtered_logs = self.get_filtered_logs()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"XC-ROBOT 日志导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总行数: {len(filtered_logs)}\n")
                f.write("=" * 50 + "\n\n")
                
                for log_entry in filtered_logs:
                    f.write(log_entry['full_text'] + '\n')
            
            QMessageBox.information(self, "保存成功", f"日志已保存到:\n{filename}")
            
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存日志时出错:\n{str(e)}")

class ChassisWidget(QWidget):
    """底盘控制控件"""
    
    log_message = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.chassis_controller = None
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 连接控制
        connection_group = QGroupBox("连接控制")
        connection_layout = QHBoxLayout(connection_group)
        
        self.ip_edit = QLineEdit("192.168.1.100")
        self.connect_btn = QPushButton("🔗 连接底盘")
        self.connect_btn.clicked.connect(self.connect_chassis)
        
        self.disconnect_btn = QPushButton("❌ 断开连接")
        self.disconnect_btn.clicked.connect(self.disconnect_chassis)
        self.disconnect_btn.setEnabled(False)
        
        connection_layout.addWidget(QLabel("底盘IP:"))
        connection_layout.addWidget(self.ip_edit)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的帮助文档查看器
使用QWebEngineView显示HTML格式的帮助文档
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

class HelpViewerWindow(QDialog):
    """帮助文档查看窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助文档")
        self.setGeometry(200, 200, 900, 700)
        self.setWindowFlags(Qt.Window)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建Web视图
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
    
    def load_html_file(self, file_path):
        """加载HTML文件"""
        if os.path.exists(file_path):
            url = QUrl.fromLocalFile(os.path.abspath(file_path))
            self.web_view.load(url)
            # 设置窗口标题为文件名
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"帮助文档 - {filename}")
        else:
            self.show_error(f"文件不存在: {file_path}")
    
    def show_error(self, message):
        """显示错误信息"""
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>错误</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 50px; 
                    background: #f8f9fa;
                }}
                .error-container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .error-icon {{ 
                    font-size: 48px; 
                    color: #e74c3c; 
                    margin-bottom: 20px; 
                }}
                .error-title {{ 
                    font-size: 24px; 
                    color: #2c3e50; 
                    margin-bottom: 15px; 
                }}
                .error-message {{ 
                    font-size: 16px; 
                    color: #7f8c8d; 
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <div class="error-title">文件加载失败</div>
                <div class="error-message">{message}</div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(error_html)
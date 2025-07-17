#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 桥接模块

用于在 Python 后端和 QWebEngineView 中的 JavaScript 前端之间进行通信。
"""

import os
from PyQt5.QtCore import QObject, pyqtSlot

class HelpBridge(QObject):
    """
    一个QObject派生的类，其实例将被注册到WebChannel中，
    以便JavaScript可以调用其@pyqtSlot装饰的函数。
    """

    def __init__(self, main_window, parent=None):
        """
        初始化桥接对象。

        Args:
            main_window: 主窗口的引用，用于调用其方法（如显示帮助窗口）。
        """
        super().__init__(parent)
        self._main_window = main_window

    @pyqtSlot(str, result=str)
    def show_document(self, doc_name: str) -> str:
        """
        一个可从JavaScript调用的槽函数，用于请求显示一个帮助文档。

        Args:
            doc_name (str): 请求的文档名称 (例如 'PROJECT_TECHNICAL_OVERVIEW.md')。

        Returns:
            str: 操作结果的反馈信息 (例如 'Success' 或 'Error: File not found')。
        """
        print(f"[Bridge] 接收到JS请求，显示文档: {doc_name}")
        try:
            # 将文档名 (e.g., 'README.md') 转换为HTML文件名 (e.g., 'README.html')
            html_filename = os.path.splitext(doc_name)[0] + '.html'

            # 构建HTML文件的绝对路径
            # __file__ -> web_bridge.py, dirname -> widgets, dirname -> gui, dirname -> project_root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            html_file_path = os.path.join(project_root, 'Md_files', html_filename)

            if os.path.exists(html_file_path):
                # 检查主窗口是否有 show_help_document 方法
                if hasattr(self._main_window, 'show_help_document'):
                    self._main_window.show_help_document(html_file_path)
                    return f"Success: Loaded {html_filename}"
                else:
                    return "Error: Backend is missing the 'show_help_document' method."
            else:
                print(f"[Bridge] 文件未找到: {html_file_path}")
                return f"Error: File not found: {html_filename}"

        except Exception as e:
            error_message = f"Error: An exception occurred in Python: {e}"
            print(f"[Bridge] {error_message}")
            return error_message

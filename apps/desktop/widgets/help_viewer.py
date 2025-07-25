#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帮助文档显示窗口
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

class HelpViewerWindow(QMainWindow):
    """用于显示HTML帮助文档的窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助文档查看器")
        self.setGeometry(200, 200, 800, 600)

        # 创建主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建 QWebEngineView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # 配置 WebEngine
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        # 允许加载本地文件
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

    def load_html_file(self, file_path: str):
        """
        加载并显示一个本地的HTML文件。

        Args:
            file_path (str): HTML文件的绝对路径。
        """
        if not file_path:
            self.web_view.setHtml("<h1>未提供文件路径</h1>")
            return

        # 使用 QUrl.fromLocalFile 来确保路径格式正确
        url = QUrl.fromLocalFile(file_path)
        self.web_view.load(url)
        self.show()
        self.raise_()
        self.activateWindow()

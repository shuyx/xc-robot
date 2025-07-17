#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帮助菜单动态构建器
根据Md_files目录结构自动生成帮助菜单
"""

import os
from PyQt5.QtWidgets import QAction, QMenu
from .help_viewer import HelpViewerWindow

class HelpMenuBuilder:
    """帮助菜单构建器"""
    
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.help_viewer = None
        self.docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Md_files")
    
    def build_help_menu(self, help_menu):
        """构建帮助菜单"""
        if not os.path.exists(self.docs_dir):
            return
        
        # 定义文档分类和对应的文件
        doc_categories = {
            "项目概述": ["README.html", "PROJECT_TECHNICAL_OVERVIEW.html"],
            "部署指南": ["DEPLOYMENT_GUIDE.html"],
            "用户界面": ["GUI_DESCRIPTION.html", "README_WEB_GUI.html", "XC_ROBOT_WEB_GUI_2.0_技术说明.html"],
            "机器人分析": ["FR3_ROBOT_ANALYSIS.html", "FR3_STL_DH_ANALYSIS.html", "STL_NAMING_GUIDE.html"],
            "仿真测试": ["ROBOTSIM_GUIDE.html", "ROBOT_TESTING_PLAN.html"]
        }
        
        # 为每个分类创建子菜单
        for category, files in doc_categories.items():
            category_menu = QMenu(category, help_menu)
            
            for file_name in files:
                file_path = os.path.join(self.docs_dir, file_name)
                if os.path.exists(file_path):
                    # 直接使用文件名作为菜单项名称（去掉.html后缀）
                    display_name = file_name.replace('.html', '')
                    action = QAction(display_name, category_menu)
                    action.triggered.connect(lambda checked, fname=file_name: self._open_help_doc_by_name(fname))
                    category_menu.addAction(action)
            
            # 只有当子菜单有内容时才添加到主菜单
            if category_menu.actions():
                help_menu.addMenu(category_menu)
        
        # 添加分隔符
        help_menu.addSeparator()
    
    def _get_display_name(self, file_name):
        """根据文件名生成显示名称"""
        name_map = {
            "README.html": "项目说明",
            "PROJECT_TECHNICAL_OVERVIEW.html": "技术概述",
            "DEPLOYMENT_GUIDE.html": "部署指南",
            "GUI_DESCRIPTION.html": "界面说明",
            "README_WEB_GUI.html": "Web界面说明",
            "XC_ROBOT_WEB_GUI_2.0_技术说明.html": "Web GUI 2.0技术说明",
            "FR3_ROBOT_ANALYSIS.html": "FR3机器人分析",
            "FR3_STL_DH_ANALYSIS.html": "FR3 STL DH参数分析",
            "STL_NAMING_GUIDE.html": "STL命名规范",
            "ROBOTSIM_GUIDE.html": "机器人仿真指南",
            "ROBOT_TESTING_PLAN.html": "机器人测试计划"
        }
        return name_map.get(file_name, file_name.replace('.html', '').replace('_', ' '))
    
    def _open_help_doc_by_name(self, file_name):
        """根据文件名打开帮助文档"""
        file_path = os.path.join(self.docs_dir, file_name)
        if not self.help_viewer:
            self.help_viewer = HelpViewerWindow(self.parent_window)
        
        self.help_viewer.load_html_file(file_path)
        self.help_viewer.show()
        self.help_viewer.raise_()
        self.help_viewer.activateWindow()
    
    def _open_help_doc(self, file_path):
        """打开帮助文档"""
        if not self.help_viewer:
            self.help_viewer = HelpViewerWindow(self.parent_window)
        
        self.help_viewer.load_html_file(file_path)
        self.help_viewer.show()
        self.help_viewer.raise_()
        self.help_viewer.activateWindow()
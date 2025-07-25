#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT GUI 包 - 延迟导入版本
"""

def get_main_window():
    """获取主窗口类（延迟导入）"""
    from .main_window import XCRobotMainWindow
    return XCRobotMainWindow

def get_web_main_window():
    """获取Web主窗口类（延迟导入）"""
    from .web_main_window import XCRobotWebMainWindow
    return XCRobotWebMainWindow

__all__ = ['get_main_window', 'get_web_main_window']
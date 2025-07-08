#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT GUI 包 - 延迟导入版本
"""

def get_main_window():
    """获取主窗口类（延迟导入）"""
    from .main_window import XCRobotMainWindow
    return XCRobotMainWindow

__all__ = ['get_main_window']
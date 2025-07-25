#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT 分析工具包
提供STL文件验证、DH参数分析和RoboDK转换等工具
"""

from .stl_validation import STLValidator
from .dh_parameter_analyzer import DHParameterAnalyzer  
from .robodk_converter import RoboDKConverter

__all__ = [
    'STLValidator',
    'DHParameterAnalyzer',
    'RoboDKConverter'
]

__version__ = "1.0.0"
__author__ = "Claude Code Assistant"
__description__ = "FR3机械臂分析和验证工具包"
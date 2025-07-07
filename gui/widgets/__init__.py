#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT GUI 控件包
"""

# 导入所有控件类
from .connection_widget import ConnectionWidget
from .arm_control_widget import ArmControlWidget  
from .chassis_widget import ChassisWidget
from .config_widget import ConfigWidget
from .log_widget import LogWidget

__all__ = [
    'ConnectionWidget',
    'ArmControlWidget', 
    'ChassisWidget',
    'ConfigWidget',
    'LogWidget'
]
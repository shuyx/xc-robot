#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XC-ROBOT GUI 控件包
"""

# 导入所有控件类
from .connection_widget import ConnectionWidget
from .arm_control_widget import ArmControlWidget  
from .chassis_widget import ChassisWidget
from .log_widget import LogWidget
from .simulation_widget import SimulationWidget
from .robot_sim_widget import RobotSimWidget

__all__ = [
    'ConnectionWidget',
    'ArmControlWidget', 
    'ChassisWidget',
    'LogWidget',
    'SimulationWidget',
    'RobotSimWidget'
]
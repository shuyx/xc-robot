#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仿真界面
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
gui_dir = os.path.join(current_dir, 'gui')
widgets_dir = os.path.join(gui_dir, 'widgets')
sys.path.insert(0, gui_dir)
sys.path.insert(0, widgets_dir)

from simulation_widget import SimulationWidget

def main():
    """测试仿真界面"""
    app = QApplication(sys.argv)
    app.setApplicationName("仿真测试")
    
    # 创建仿真界面
    widget = SimulationWidget()
    widget.setWindowTitle("机器人仿真系统测试")
    widget.resize(1200, 800)
    widget.show()
    
    # 连接日志信号到打印
    widget.log_message.connect(lambda msg, level: print(f"[{level}] {msg}"))
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
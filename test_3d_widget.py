#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试3D显示控件
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# 添加gui路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui', 'widgets'))

from robot_3d_widget import Test3DWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = Test3DWindow()
    window.show()
    
    sys.exit(app.exec_())
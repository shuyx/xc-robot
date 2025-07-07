# main.py
#!/usr/bin/env python3
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'fr3_control'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'main_control'))

from integrated_controller import IntegratedRobotController

def main():
    # 使用你现有的hermes_controller和robot_controller
    controller = IntegratedRobotController()
    controller.run()

if __name__ == "__main__":
    main()
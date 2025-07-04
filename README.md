# xc-robot
xc robot 的调试
尝试开发 xc-os system，用来调试mvp1.0的场景、功能等各种情况测试和验证

## Code Reviews

- fr3_control
    - fairino: sdk文件夹
    - Robot.py python版本的导入模块
- function_test
    - 功能测试用文件夹
    - 测试时，最好将py文件放到根目录
- gui
    - gui界面的weidget组件
- main_control
    - 主要控制程序，多为集成功能
- tests
    - 独立模块或设备的功能测试，可单独进行测试
- quick_start.py
    - 快速检查目前所有设备和连接
- requirements.txt
    - 依赖文件
- start_gui.py
    - 启动gui界面
- venv
    - 虚拟环境启动，里面安装依赖，python解释器
    - venv\Scripts\activate
    - deactivate（解除）
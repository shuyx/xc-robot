# FR3机械臂部署指南

## 1. 安装Python依赖

在VS Code终端中运行：

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 2. 验证网络连接

### 2.1 检查机械臂IP配置
- 右臂IP: 192.168.58.2
- 左臂IP: 192.168.58.3
- Hermes底盘: http://192.168.31.211:1448

### 2.2 测试网络连通性
在命令行中ping测试：
```bash
ping 192.168.58.2
ping 192.168.58.3
```

## 3. 运行测试程序

### 3.1 测试单个机械臂
```bash
# 测试右臂
python tests/fr3_simple_test.py 192.168.58.2

# 测试左臂
python tests/fr3_simple_test.py 192.168.58.3
```

### 3.2 测试双臂连接
```bash
python tests/dual_arm_connection.py
```

### 3.3 测试集成控制器（完整流程）
```bash
python main_control/integrated_controller.py
```

## 4. 使用指南

### 4.1 编程接口
```python
from fr3_control.fairino import Robot

# 连接机械臂
robot = Robot.RPC("192.168.58.2")

# 设置模式和使能
robot.Mode(0)  # 自动模式
robot.RobotEnable(1)  # 使能

# 执行运动
robot.MoveJ([0, -20, -90, -90, 90, 0], tool=0, user=0, vel=20)
```

### 4.2 运行模式
集成控制器支持三种模式：
1. **交互控制模式** - 手动选择任务
2. **标准任务模式** - 执行预定义流程
3. **状态测试模式** - 仅检查系统状态

## 5. 注意事项

1. **安全第一**
   - 首次运行请确保机械臂周围有足够空间
   - 使用较低速度（10-20%）进行测试
   - 准备好急停按钮

2. **网络配置**
   - 确保主机与机械臂在同一网段
   - 防火墙可能需要允许相关端口

3. **错误处理**
   - 如果连接失败，检查机械臂控制器是否开启
   - 确认机械臂处于远程控制模式

## 6. 常见问题

### Q: 提示"fairino模块导入失败"
A: 确保在项目根目录运行，fr3_control文件夹包含fairino模块

### Q: 连接超时
A: 检查网络连接和IP地址配置

### Q: 运动指令返回错误码
A: 查看fr3 pdf文件夹中的错误码对照表

## 7. 下一步

完成基础测试后，你可以：
- 修改`integrated_controller.py`中的动作序列
- 添加新的工作站位置
- 开发GUI界面（gui文件夹已有基础框架）
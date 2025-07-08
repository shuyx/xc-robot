# 3D显示模块测试指南

## 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装VTK（已安装）
pip install vtk
```

## 测试方法

### 1. 简单VTK测试
测试VTK是否正常工作：
```bash
python test_3d_complete.py --mode simple
```
应该看到一个带有橙色立方体的3D窗口。

### 2. 运动学计算测试
测试FR3运动学计算（无GUI）：
```bash
python test_3d_complete.py --mode kinematics
```
输出各关节位置和末端执行器位姿。

### 3. 完整3D机器人测试
测试完整的3D机器人显示和控制：
```bash
python test_3d_complete.py --mode complete
```
包含：
- 3D机器人模型显示
- 6个关节滑块控制
- 动画播放功能
- 末端执行器位姿显示

### 4. 原始测试脚本
```bash
python test_3d_widget.py
```
基本的3D控件测试。

## 集成到主程序

要将3D显示集成到主程序，可以：

1. 在 `simulation_widget.py` 中导入 `Robot3DWidget`
2. 替换或添加一个新的选项卡
3. 连接轨迹数据到3D显示

示例代码：
```python
from robot_3d_widget import Robot3DWidget

# 在SimulationWidget中添加
self.robot_3d = Robot3DWidget()
layout.addWidget(self.robot_3d)

# 更新显示
def update_3d_display(joint_angles):
    self.robot_3d.update_joint_angles(joint_angles)
```

## 加载真实模型

准备STL文件后，可以：
```python
# 加载基座
robot_3d.load_stl_model("models/fr3_base.stl", "base")

# 加载连杆
robot_3d.load_stl_model("models/fr3_link1.stl", "link1")
# ... 加载其他部件
```

## 故障排除

1. **ImportError: No module named 'vtk'**
   - 解决：`pip install vtk`

2. **Qt平台插件错误**
   - 解决：确保在虚拟环境中运行

3. **窗口不响应**
   - 正常现象，VTK窗口需要鼠标交互
   - 使用鼠标左键旋转，右键缩放，中键平移

## 下一步

1. 准备FR3机器人的CAD模型（STL格式）
2. 实现URDF加载器
3. 集成到主界面
4. 添加轨迹回放功能
5. 实现碰撞检测（可选）
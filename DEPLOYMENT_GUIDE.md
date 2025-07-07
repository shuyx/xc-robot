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

## 7. 底盘相对移动控制

*更新时间：2025-01-07 17:30*

### 7.1 功能说明
新增底盘相对移动控制程序，支持基于当前位置的相对运动控制。

### 7.2 使用方法
```bash
# 在项目根目录运行
python function_test/chassis_relative_move.py
```

### 7.3 控制选项
- **前进/后退** - 沿当前朝向移动指定距离(米)
- **左移/右移** - 垂直于当前朝向平移指定距离(米)  
- **左转/右转** - 原地旋转指定角度(度)

### 7.4 实现效果
1. 自动获取底盘当前坐标和朝向
2. 终端交互式选择运动方向
3. 输入移动距离或转向角度
4. 计算目标位置并执行移动
5. 实时反馈运动状态

### 7.5 故障排查工具

*更新时间：2025-01-07 18:00*

#### 7.5.1 Action类型检查
```bash
python function_test/check_action_factories.py
```
功能：查询底盘支持的所有action类型，验证API接口

#### 7.5.2 刹车状态复位
```bash
python function_test/chassis_reset_brake.py
```
功能：
- 检查底盘状态信息
- 尝试复位电机刹车
- 解决"motor brake released"错误（错误码：33621760）

常见错误处理：
- **CANNOT_REACH_TARGET**: 目标位置不可达，建议减小移动距离
- **motor brake released**: 电机刹车释放，需要复位或检查急停按钮

## 8. GUI界面优化

*更新时间：2025-01-07 20:15*

### 8.1 跨平台字体兼容性修复
修复了Mac系统下GUI按钮文字不显示的问题：

#### 8.1.1 问题描述
- Windows系统使用"Microsoft YaHei"字体正常显示
- Mac系统缺少该字体，导致按钮文字为空白
- 特别是仿真界面的"播放底盘"、"暂停"、"停止"等按钮

#### 8.1.2 解决方案
1. **设置字体回退机制**：
   ```python
   font = QFont()
   font.setFamily("PingFang SC, Helvetica, Microsoft YaHei, Arial")
   ```

2. **移除emoji字符**：
   - 替换`▶️ 播放底盘` → `播放底盘`
   - 替换`⏸️ 暂停` → `暂停`
   - 替换`⏹️ 停止` → `停止`
   - 替换`🔄 重置` → `重置`

3. **修改的文件**：
   - `start_gui.py`：全局字体设置
   - `gui/main_window.py`：主窗口字体设置
   - `gui/gui_main.py`：GUI主程序字体设置
   - `gui/widgets/simulation_widget.py`：仿真控件按钮字体设置

### 8.2 仿真界面标尺优化
改进了仿真界面右上角的标尺显示：

#### 8.2.1 优化内容
1. **单位标准化**：从毫米(mm)改为米(m)
2. **去除背景**：移除白色背景框，界面更简洁
3. **视觉优化**：使用黑色加粗线条，提高清晰度
4. **信息精简**：只显示关键的网格尺寸信息

#### 8.2.2 显示效果
- 标尺显示：`0` ━━━━━━━━━━ `0.5m`
- 网格信息：`网格: 0.25m`
- 位置：右上角，无背景干扰

### 8.3 依赖环境配置
#### 8.3.1 Python虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
pip install PyQt5  # GUI界面支持
```

#### 8.3.2 跨平台兼容性
现在GUI界面支持：
- ✅ Windows 10/11
- ✅ macOS (Intel/Apple Silicon)
- ✅ Linux (Ubuntu/Debian)

## 9. 底盘仿真界面控制增强

*更新时间：2025-01-07 23:00*

### 9.1 新增功能概述
在底盘运动仿真界面标题旁边新增三个控制按钮，提供更精细的仿真控制能力。

### 9.2 功能详细说明

#### 9.2.1 X/Y方向切换按钮 (`🔄 X/Y切换`)
**功能描述**：
- 一键切换X轴和Y轴的方向
- 坐标系箭头会相应反转方向
- 以坐标轴构成矩形的对角线角点为新坐标系原点

**技术实现**：
- 新增 `coordinate_origin` 变量跟踪坐标系原点位置
- 实现动态原点逻辑，确保轴向反转后坐标系仍在可见区域
- 修改 `draw_coordinate_system` 方法支持轴向反转显示

**使用效果**：
```
默认状态: 原点(30,30), X轴→, Y轴↓
切换后: 原点(70,70), X轴←, Y轴↑
再次切换: 恢复原状态
```

#### 9.2.2 90°旋转按钮 (`🔄 90°旋转`)
**功能描述**：
- 底盘矩形围绕当前质心旋转90°
- 红色方向箭头保持原方向不变
- 点击一次旋转90°，连续点击可实现180°、270°、360°旋转

**技术实现**：
- 新增 `chassis_rotation_offset` 变量控制额外旋转角度
- 分离底盘矩形和方向箭头的绘制逻辑
- 矩形应用 `chassis_angle + chassis_rotation_offset`
- 箭头仅应用原始 `chassis_angle`

**绘制分离**：
```python
# 1. 绘制底盘矩形（受rotation_offset影响）
painter.rotate(self.chassis_angle + self.chassis_rotation_offset)
painter.drawRect(...)  # 橘黄色矩形

# 2. 绘制方向箭头（不受rotation_offset影响）
painter.rotate(self.chassis_angle)  # 只使用原始角度
painter.drawPolygon(...)  # 红色箭头
```

### 9.3 代码修改内容

#### 9.3.1 新增状态变量
```python
# ChassisSimulationWidget类新增：
self.x_inverted = False  # X轴是否反向
self.y_inverted = False  # Y轴是否反向
self.chassis_rotation_offset = 0  # 底盘额外旋转角度
self.coordinate_origin = [30, 30]  # 坐标系原点位置
```

#### 9.3.2 新增控制方法
```python
def toggle_xy_direction(self):
    """切换X/Y轴方向，以对角线角点为新原点"""
    
def rotate_chassis_90(self):
    """底盘矩形旋转90度（不影响红色箭头）"""

def clear_chassis_path(self):
    """清除底盘路径"""
```

#### 9.3.3 修改的文件
- `gui/widgets/simulation_widget.py`：主要功能实现
- 新增三个UI按钮和信号连接
- 修改坐标系和底盘绘制方法
- 新增路径清除功能

### 9.4 使用指南

#### 9.4.1 启动仿真界面
```bash
# 运行GUI主程序
python start_gui.py

# 或直接测试仿真界面
python test_simulation.py
```

#### 9.4.2 操作步骤
1. 在GUI界面选择"仿真系统"标签页
2. 观察"底盘运动仿真"区域的橘黄色矩形和红色箭头
3. 点击 `🔄 X/Y切换` 按钮测试坐标轴反转
4. 点击 `🔄 90°旋转` 按钮测试矩形旋转（箭头方向不变）
5. 点击 `🗑️ 清除路径` 按钮测试路径清除功能

### 9.5 预期效果验证

#### 9.5.1 X/Y切换效果
- ✅ 坐标轴箭头方向反转
- ✅ 原点移动到对角线位置
- ✅ 显示内容保持在可见区域
- ✅ 日志显示"已切换X/Y轴方向"

#### 9.5.2 90°旋转效果
- ✅ 橘黄色底盘矩形围绕质心旋转
- ✅ 红色方向箭头保持原方向
- ✅ 矩形上的"HERMES"标识跟随旋转
- ✅ 日志显示"底盘矩形已旋转90度"

#### 9.5.3 清除路径功能 (`🗑️ 清除路径`)

*更新时间：2025-01-07 23:00*

**功能描述**：
- 一键清除底盘运动仿真中的所有蓝色路径线条
- 重置动画状态和进度条
- 保持底盘当前位置和朝向不变

**技术实现**：
```python
def clear_path(self):
    """清除路径点和重置状态"""
    self.path_points = []           # 清空路径点列表
    self.current_path_index = 0     # 重置当前索引
    self.stop_animation()           # 停止动画
    self.update()                   # 刷新显示
```

**清除内容**：
- ✅ 蓝色路径连接线
- ✅ 蓝色/红色路径点圆圈
- ✅ 路径点方向箭头
- ✅ 动画进度条重置为0%
- ✅ 停止正在播放的路径动画

**保留内容**：
- ✅ 底盘矩形和红色方向箭头（当前位置）
- ✅ 网格线和坐标系显示
- ✅ 比例尺和标识信息

**使用场景**：
- 加载新的路径数据前清除旧路径
- 重新开始路径规划时清空显示
- 调试时快速清除测试路径
- 演示时重置仿真状态

**操作效果验证**：
- ✅ 点击按钮后蓝色路径立即消失
- ✅ 进度条显示"0%"
- ✅ 动画停止播放
- ✅ 日志显示"已清除底盘路径"
- ✅ 底盘位置和方向保持不变

## 10. 下一步

完成基础测试后，你可以：
- 修改`integrated_controller.py`中的动作序列
- 添加新的工作站位置
- 使用优化后的GUI界面进行仿真测试
- 使用底盘相对移动功能进行路径规划
- 利用新增的仿真控制功能验证底盘运动逻辑
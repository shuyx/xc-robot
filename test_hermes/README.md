# Hermes底盘测试程序

这个目录包含了用于测试Hermes底盘的各种Python脚本。

## 文件说明

### 1. `hermes_control_example.py`
**完整的底盘控制示例**
- 演示连接、状态查询、移动、停止、断开的完整流程
- 适合初学者了解底盘控制的基本操作

**运行方式**:
```bash
python test_hermes/hermes_control_example.py
```

### 2. `simple_movement_test.py`
**简单移动测试**
- 测试底盘移动到多个预设位置
- 显示目标位置与实际位置的对比
- 适合测试底盘的移动精度

**运行方式**:
```bash
python test_hermes/simple_movement_test.py
```

### 3. `status_monitor.py`
**底盘状态监控**
- 持续监控底盘的实时状态
- 显示位置、角度、运动状态、电量等信息
- 可以自定义监控时长和间隔

**运行方式**:
```bash
# 默认监控10秒，间隔1秒
python test_hermes/status_monitor.py

# 自定义监控20秒，间隔0.5秒
python test_hermes/status_monitor.py 20 0.5
```

### 4. `map_navigation_control.py` 🗺️ **最新推荐**
**基于SLAM地图的精确导航控制**
- 🎯 **基于真实地图数据** - 使用RoboStudio建立的SLAM地图
- 📏 **精确10cm步长** - 每次移动精确10厘米
- 🧭 **智能位姿计算** - 基于当前位姿计算目标位置
- 📊 **实时误差显示** - 显示目标位置与实际位置的误差
- 🗺️ **地图坐标转换** - 同时显示世界坐标和地图像素坐标
- ⚡ **高精度控制** - 误差通常控制在1-2厘米内

**运行方式**:
```bash
python test_hermes/map_navigation_control.py
```

**控制指令**:
- `W` - 沿当前朝向前进10cm
- `S` - 沿当前朝向后退10cm  
- `A` - 向左侧移动10cm (相对于当前朝向)
- `D` - 向右侧移动10cm (相对于当前朝向)
- `Q` - 原地左转15°
- `E` - 原地右转15°
- `P` - 显示详细位姿信息(世界坐标+地图坐标)
- `X` - 退出程序

**地图信息**:
- 地图文件: `slam_map/吸管_纸杯.stcm`
- 地图尺寸: 536×563像素
- 分辨率: 5厘米/像素
- 原点坐标: (-12.8, -15.5)米

### 5. `simple_wasd_control.py` ⭐️ **基础推荐**
**简化版WASD键盘控制**
- 使用键盘输入控制底盘移动
- 支持前后左右移动、左右转向
- 交互式命令界面，操作简单直观
- **最适合手动测试和学习使用**

**运行方式**:
```bash
python test_hermes/simple_wasd_control.py
```

**控制指令**:
- `W` - 前进0.5m
- `S` - 后退0.5m  
- `A` - 左移0.5m
- `D` - 右移0.5m
- `Q` - 左转30°
- `E` - 右转30°
- `P` - 显示当前位置
- `X` - 退出程序

### 6. `real_api_control.py` 🔥 **真实底盘控制**
**使用真实API的底盘控制**
- 🌐 **直接HTTP API调用** - 绕过仿真，直接控制真实底盘
- 🎮 **多种控制模式** - 相对移动、绝对定位、手动速度控制
- 📊 **完整状态监控** - 电池、位姿、运动状态
- 🔧 **基于官方API** - 使用Slamware官方RESTful API

**运行方式**:
```bash
# 使用默认IP地址 192.168.31.211
python test_hermes/real_api_control.py

# 指定底盘IP地址
python test_hermes/real_api_control.py 192.168.11.1
```

**控制模式**:
- **相对移动**: W/S/A/D (10cm步长), Q/E (15°转向)
- **绝对定位**: G - 移动到指定坐标
- **手动控制**: I/K/J/L (连续速度控制)
- **状态查询**: P (位姿), B (电池)

### 7. `test_chassis_connection.py` 🔍 **连接诊断工具**
**底盘连接测试和诊断**
- 🔌 **TCP连接测试** - 检查网络连通性
- 🌐 **HTTP服务测试** - 验证Web服务状态
- 📡 **API端点测试** - 逐个测试所有API接口
- 💡 **故障诊断建议** - 提供详细的故障排除指导

**运行方式**:
```bash
# 测试默认IP地址
python test_hermes/test_chassis_connection.py

# 测试指定IP地址
python test_hermes/test_chassis_connection.py 192.168.11.1
```

### 8. `wasd_control.py`
**高级WASD键盘控制**
- 连续速度控制模式
- 多线程键盘监听
- 适合需要连续控制的场景

**运行方式**:
```bash
python test_hermes/wasd_control.py
```

## 使用说明

### 前置条件
1. 确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 确保httpx库已安装：
   ```bash
   pip install httpx
   ```

### 仿真模式
- 当前所有程序都运行在仿真模式下
- 仿真模式可以在没有真实硬件的情况下测试代码逻辑
- 仿真数据包括随机的位置误差，模拟真实情况

### 真实硬件模式
要连接真实的Hermes底盘：
1. 确保底盘已连接到网络
2. 修改 `services/robot/hermes_service.py` 中的 `SIMULATION_MODE = False`
3. 确认底盘IP地址是否为 `192.168.31.211:1448`

## API功能对照

| 功能 | API端点 | 对应方法 |
|------|---------|----------|
| 连接底盘 | - | `hermes_service.connect_hermes_chassis()` |
| 获取状态 | `/api/core/system/v1/power/status` | `hermes_service.get_chassis_status()` |
| 移动到位置 | `/api/core/motion/v1/actions` | `hermes_service.move_chassis()` |
| 停止移动 | `/api/core/motion/v1/stop` | `hermes_service.stop_chassis()` |
| 断开连接 | - | `hermes_service.disconnect_hermes_chassis()` |

## 故障排除

### ❗ 底盘不移动问题
**如果底盘连接成功但不移动**，按以下步骤检查：

1. **首先运行连接测试**:
   ```bash
   python test_hermes/test_chassis_connection.py
   ```

2. **检查底盘状态**:
   - 底盘是否完成开机初始化（通常需要1-2分钟）
   - 底盘是否在建图模式或导航模式
   - 急停按钮是否处于正常状态

3. **使用浏览器验证API**:
   - 打开浏览器访问: `http://192.168.31.211:1448`
   - 查看是否有Swagger API文档界面
   - 手动测试API接口是否响应

4. **使用真实API控制脚本**:
   ```bash
   python test_hermes/real_api_control.py
   ```

### 🔌 网络连接问题
**如果无法连接到底盘**：

1. **检查网络连接**:
   ```bash
   ping 192.168.31.211
   ```

2. **确认IP地址**:
   - 使用RoboStudio查看底盘实际IP地址
   - 确保电脑和底盘在同一网段

3. **检查端口访问**:
   ```bash
   telnet 192.168.31.211 1448
   ```

4. **防火墙设置**:
   - Windows防火墙可能阻止连接
   - 尝试临时关闭防火墙测试

### 📦 导入错误
如果出现 `ModuleNotFoundError: No module named 'services'`：
- 确保在项目根目录下运行脚本
- 检查脚本中的路径设置是否正确

### 🖥️ 中文显示问题
Windows控制台可能显示中文乱码，这是正常现象，不影响程序功能。

### 🚀 推荐的测试流程
1. **连接测试**: `test_chassis_connection.py` - 验证网络和API
2. **浏览器测试**: 访问 `http://IP:1448` - 查看API文档
3. **真实控制**: `real_api_control.py` - 进行实际控制测试
4. **精确导航**: `map_navigation_control.py` - 基于地图的精确控制
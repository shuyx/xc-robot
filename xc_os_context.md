# XC-OS Context 项目背景

**作者**: Kevin Yuan  
**创建时间**: 2025年7月1日  
**最后更新**: 2025年7月17日  
**版本**: v1.0

---

## Claude AI助手须知
我是一个轮式双臂类人形机器人的项目负责人，正在开发这套机器人及其上位控制系统。我希望该系统能够控制机器人，实现本地、远程控制与运维，能实现基于AI及大模型的智能交互控制、数据智能运维与调度、基于AI的多场景多传感融合自适应部署等功能。

**当前开发阶段**：MVP1.0版本硬件的XC-OS System
**开发原则**：以实现功能为目标，精简代码，提高可靠性
**重要约束**：任何非我设计的、描述的、讨论的功能都尽量不要增加，以降低Claude的思考和撰写代码的tokens消耗为标准

---

# XC-ROBOT 项目概述

## 项目定义
XC-ROBOT是轮式双臂类人形机器人控制系统，基于XC-OS模块化架构，专为机器人预研和功能测试设计。

## 硬件平台
- **移动底盘**: 思岚科技 Hermes 轮式底盘 (192.168.31.211:1448)
- **机械臂**: 法奥意威 FR3 双机械臂系统 (右臂:192.168.58.2, 左臂:192.168.58.3)
- **视觉系统**: Gemini 335系列相机
- **控制器**: 多平台控制计算机 (192.168.58.1)

## 技术栈
- **开发语言**: Python 3.x
- **GUI框架**: PyQt5 + QWebEngineView (Web混合界面)
- **机械臂控制**: FR3 API (法奥意威SDK)
- **底盘控制**: Hermes RESTful API
- **3D可视化**: VTK
- **运动学**: Modified DH Convention
- **前端技术**: HTML5 + CSS3 + JavaScript
- **通信机制**: QWebChannel (Python-JS桥接)
- **开发环境**: 虚拟环境 (venv)

## 双GUI架构设计

### 1. 传统PyQt5 GUI (start_gui.py)
- **主窗口**: `gui/main_window.py` - 传统PyQt5选项卡界面
- **控件模块**: `gui/widgets/` - 各功能模块的PyQt5控件
- **特点**: 稳定可靠，功能完整，适合开发调试

### 2. Web混合GUI (start_web_gui.py)
- **主窗口**: `gui/web_main_window.py` - QWebEngineView嵌入HTML界面
- **桥接模块**: `gui/web_bridge.py` - Python与JavaScript通信
- **特点**: 现代化界面，易于定制，适合展示和远程控制

## 核心功能模块

### 1. 硬件控制
- **FR3双机械臂**: 6DOF×2，支持单臂/双臂协调控制
- **Hermes移动底盘**: 全向移动，路径规划，预设位置导航
- **集成控制**: `main_control/integrated_controller.py` - 完整工作流程控制

### 2. 仿真系统
- **2D底盘仿真**: 路径绘制，轨迹预览
- **3D机械臂仿真**: VTK渲染，STL模型加载
- **运动学求解**: 正向/逆向运动学，雅可比矩阵
- **RobotSim**: 高级3D仿真环境

### 3. 网络通信
- **连接测试**: 多线程网络连通性检测
- **设备状态**: 实时状态监控和反馈
- **API接口**: RESTful API调用和响应处理

### 4. 日志系统
- **实时日志**: 分级显示(INFO/SUCCESS/WARNING/ERROR)
- **日志过滤**: 按级别过滤显示
- **日志导出**: 保存为文本文件

## 详细项目结构
```
xc-robot/
├── 启动脚本
│   ├── start_gui.py              # 传统PyQt5界面启动
│   ├── start_web_gui.py          # Web混合界面启动
│   ├── gui/gui_main.py           # GUI主程序
│   └── platform_config.py        # 跨平台配置适配
│
├── fr3_control/                  # FR3机械臂控制
│   ├── fairino/Robot.py          # FR3 SDK核心模块
│   └── example/                  # FR3控制示例代码
│
├── gui/                          # GUI界面模块
│   ├── __init__.py              # 延迟导入机制
│   ├── main_window.py           # 传统PyQt5主窗口
│   ├── web_main_window.py       # Web混合主窗口
│   ├── web_bridge.py            # Python-JS通信桥接
│   ├── help_menu_builder.py     # 帮助菜单构建器
│   ├── help_viewer.py           # 帮助文档查看器
│   └── widgets/                 # 功能控件模块
│       ├── connection_widget.py  # 连接测试控件
│       ├── arm_control_widget.py # 机械臂控制控件
│       ├── chassis_widget.py     # 底盘控制控件
│       ├── simulation_widget.py  # 仿真系统控件
│       ├── robot_sim_widget.py   # RobotSim 3D控件
│       ├── log_widget.py         # 日志显示控件
│       └── fr3_kinematics.py     # FR3运动学模型
│
├── main_control/                 # 主控制程序
│   ├── integrated_controller.py  # 集成控制器(完整工作流程)
│   ├── dual_arm_controller.py    # 双臂协调控制器
│   ├── robot_controller.py       # 机器人控制器
│   ├── hermer_controller.py      # Hermes底盘控制器
│   └── utils/                    # 控制工具模块
│       ├── config_loader.py      # 配置加载器
│       └── logger.py             # 日志工具
│
├── tests/                        # 设备功能测试
│   ├── fr3_simple_test.py        # FR3基础测试
│   ├── dual_arm_connection.py    # 双臂连接测试
│   ├── hermes_test_connection.py # Hermes连接测试
│   └── integrated_test.py        # 集成测试
│
├── function_test/                # 功能验证测试
│   ├── dual_arm_realtime_monitor.py    # 双臂实时监控
│   ├── dual_arm_simulation_trajectory.py # 双臂仿真轨迹
│   └── fr3_diagnostic.py               # FR3诊断工具
│
├── models/                       # 3D模型文件
│   ├── fr3_robot.urdf           # FR3机器人URDF模型
│   └── fr3_base.stl             # FR3底座STL模型
│
├── config/                       # 配置文件
│   ├── robot_config.json        # 机器人配置
│   ├── platform_configs.json    # 平台配置
│   ├── gui_config_darwin.json   # macOS GUI配置
│   └── network_config_darwin.json # macOS网络配置
│
├── tools/                        # 工具脚本
│   ├── dh_parameter_analyzer.py  # DH参数分析器
│   ├── stl_validation.py        # STL文件验证
│   └── robodk_converter.py      # RoboDK转换器
│
├── Md_files/                     # 项目文档
│   ├── README.md                # 项目说明
│   ├── PROJECT_TECHNICAL_OVERVIEW.md # 技术概览
│   ├── GUI_DESCRIPTION.md       # GUI界面说明
│   ├── FR3_ROBOT_ANALYSIS.md    # FR3机械臂分析
│   └── DEPLOYMENT_GUIDE.md      # 部署指南
│
├── 配置文件
│   ├── robot_config.yaml        # 机器人主配置
│   ├── requirements.txt         # Python依赖
│   └── requirements_platform.txt # 平台特定依赖
│
└── 其他目录
    ├── hermes_datas/            # Hermes底盘文档
    ├── fr3_datas/               # FR3机械臂文档
    ├── vision_datas/            # 视觉系统文档
    └── UI/                      # UI设计文档
```

## 核心代码架构

### 1. Web桥接通信 (WebBridge类)
```python
# gui/web_main_window.py - WebBridge类
@pyqtSlot(str, result=str)
def test_connection(self, device_type):
    """测试设备连接，返回JSON格式结果"""

@pyqtSlot(str, str)
def control_arm(self, arm_type, action):
    """控制机械臂(right/left/both)"""

@pyqtSlot(str)
def control_chassis(self, action):
    """控制底盘移动"""

@pyqtSlot()
def emergency_stop(self):
    """全系统紧急停止"""
```

### 2. 集成控制器 (IntegratedController类)
```python
# main_control/integrated_controller.py
class IntegratedController:
    """完整工作流程控制器"""
    - HermesController: 底盘控制
    - FR3Controller: 双臂控制  
    - 工作流程: 移动→操作→返回
```

### 3. 控件模块架构
```python
# gui/widgets/ - 各控件都继承QWidget
- ConnectionWidget: 网络连接测试
- ArmControlWidget: 机械臂控制
- ChassisWidget: 底盘控制
- SimulationWidget: 仿真系统
- RobotSimWidget: VTK 3D仿真
- LogWidget: 日志显示
```

## 已实现功能
1. ✅ FR3双机械臂基础控制 (连接、使能、运动、关节点动)
2. ✅ Hermes底盘基础控制 (移动、导航、预设位置)
3. ✅ 双GUI架构 (传统PyQt5 + Web混合界面)
4. ✅ Python-JavaScript桥接通信
5. ✅ VTK 3D仿真系统 (STL模型加载、运动学可视化)
6. ✅ 运动学正逆解算法 (Modified DH Convention)
7. ✅ 多线程网络连接测试
8. ✅ 分级日志系统 (实时显示、过滤、导出)
9. ✅ 配置管理系统 (YAML配置、平台适配)
10. ✅ 集成控制器 (完整工作流程控制)

## 技术特点
- **双GUI架构**: 传统PyQt5界面 + 现代Web混合界面
- **模块化设计**: 独立的控制模块，便于维护扩展
- **延迟加载**: 解决VTK与PyQt5初始化冲突
- **多线程**: 网络测试和控制操作不阻塞GUI
- **信号槽机制**: PyQt信号槽实现模块间通信
- **桥接通信**: QWebChannel实现Python-JavaScript双向通信
- **配置驱动**: YAML配置文件管理设备参数
- **跨平台支持**: Mac/Windows/Linux平台适配

## FR3机械臂技术细节
- **自由度**: 6DOF全旋转关节
- **工作半径**: 630mm，负载3kg
- **DH参数**: Modified DH Convention
- **关节范围**: J1-J6分别为±170°,±120°,±170°,±170°,±120°,±175°
- **零位配置**: 垂直向上姿态 [0,-90,90,0,0,0]
- **控制模式**: 位置控制、速度控制、力控制
- **SDK接口**: fairino.Robot.RPC() 网络连接

## 开发状态
- **当前版本**: v2.6.3 (Web GUI), v2.3.2 (传统GUI)
- **开发阶段**: MVP1.0硬件验证
- **测试状态**: 基础功能已验证，集成控制器已实现
- **下一步**: AI功能接入准备，智能交互控制开发

## Git开发历史 (近期重要更新)

### 主要分支架构
```
├── main (主分支)
├── mac-dev (macOS开发分支) ⭐ 当前活跃
├── win-dev (Windows开发分支)
└── robot-dev (机器人功能测试分支)
```

### 重要里程碑版本

#### v2.6.x 系列 - Web GUI完善期 (2025.07)
- **v2.6.3** `65baa1a` - 统一所有平台使用Web界面，提供一致的UI/UX体验
- **v2.6.2** `62e8d0b` - 新UI说明文档更新为HTML格式
- **v2.6.1** `4392eb6` - 设备连接功能完整实现 (+772行代码)
- **v2.6.0** `efddca4` - Connection连接测试功能核心实现 (+855行代码)

#### v2.5.x 系列 - UI界面重构期 (2025.06-07)
- **v2.5.14** `d72bd8e` - 界面细节调整优化
- **v2.5.13** `431fdc3` - 菜单栏功能丰富
- **v2.5.12** `70854c7` - Quick Start快速启动功能
- **v2.5.11** `4c2da20` - 帮助系统功能完成
- **v2.5.0** `d0806f0` - 全新软件UI界面架构

### 关键技术突破

#### 🚀 跨平台开发解决方案 `726f76f` (2025.07.17)
**重大功能实现**:
1. **跨平台自动适配系统**
   - 平台检测和自动配置 (Mac/Windows/Linux)
   - 自动路径分隔符处理 (/ vs \)
   - 平台特定启动脚本生成 (.sh/.bat)
   - 字体和DPI缩放优化
   - 平台特定依赖管理

2. **网络配置与连接测试**
   - 完整设备网络配置界面
   - 16个机器人设备一键连接测试
   - 实时状态指示器和日志记录
   - macOS网络设置集成

3. **连接状态仪表板**
   - 实时监控数据面板设计
   - 设备统计和性能指标系统概览
   - 硬件组件监控网格
   - 任务执行跟踪和队列管理
   - 系统资源监控 (CPU、内存、温度、网络)

**新增核心文件**:
- `platform_config.py` - 平台适配引擎
- `auto_platform_setup.py` - 一键环境设置
- `sync_branches.py` - 智能分支同步
- `CROSS_PLATFORM_SOLUTION.md` - 完整解决方案文档

#### 🔧 分支合并与同步 `42ff603` (2025.07.17)
- 将robot-dev分支合并到mac-dev，实现完整技术文档访问
- 智能冲突解决和文件重命名处理
- 自动化分支同步工具

#### 🐛 JavaScript错误修复 `ec059d8` (2025.07.17)
- 修复连接状态仪表板中的JavaScript错误
- 解决localStorage在data: URL环境中的访问问题
- 增强错误处理和回退机制

### 测试功能开发 (robot-dev分支)
- **SAT003** `384722a` - 安全检查条件变更
- **SAT002** `6ee67a4` - 确认单臂基础运动测试
- **SAT001** `38b9d4e` - 所有测试代码文件完成

### 开发效率提升
- ✅ **零手动平台适配**: 自动化处理所有平台差异
- ✅ **一键环境设置**: 新开发者快速上手
- ✅ **智能分支同步**: 自动冲突解决
- ✅ **平台特定优化**: 自动应用最佳配置

### 代码统计 (近期主要提交)
```
726f76f: +1611行, -31行  (跨平台解决方案)
4392eb6: +772行, -9行   (设备连接功能)
efddca4: +855行, +0行   (连接测试功能)
```

### 当前开发重点
1. **Web GUI界面优化** - 现代化HTML5界面完善
2. **跨平台兼容性** - Mac/Windows/Linux全平台支持
3. **设备连接稳定性** - 16设备实时监控
4. **自动化工具链** - 减少手动操作，提高开发效率

## 安全机制
- 紧急停止功能 (Ctrl+E，全系统停止)
- 关节限位保护 (软件限位检查)
- 奇异性配置避免 (运动学检查)
- 碰撞检测预警 (仿真环境)
- 网络连接状态监控 (实时检测)
- 多线程安全 (避免界面冻结)
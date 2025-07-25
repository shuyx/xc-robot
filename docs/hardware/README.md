# 硬件系统文档模块

> XC-ROBOT 硬件系统完整技术文档

## 🤖 硬件系统概述

XC-ROBOT采用模块化硬件架构，由以下核心硬件组成：
- **FR3 机械臂** - 7自由度协作机械臂（双臂配置）
- **Hermes 底盘** - 激光导航移动底盘
- **Gemini 视觉** - 深度相机和视觉处理系统
- **仿真系统** - 高保真度机器人仿真环境

## 🏗️ 硬件架构图
```
           XC-ROBOT 硬件系统架构
    ┌─────────────────────────────────────┐
    │              控制中心                │
    │        (主控制器 + GUI)              │
    └──────────────┬──────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
   │ FR3   │   │Hermes │   │Gemini │
   │双机械臂│   │底盘   │   │视觉   │
   └───────┘   └───────┘   └───────┘
```

## 📁 硬件模块文档

### 🦾 FR3 机械臂系统 (`fr3_mechanical_arm/`)

#### 技术分析 (`analysis/`)
- [🔬 **FR3_ROBOT_ANALYSIS.md**](./fr3_mechanical_arm/analysis/FR3_ROBOT_ANALYSIS.md) - FR3机械臂运动学分析
- [📐 **FR3_STL_DH_ANALYSIS.md**](./fr3_mechanical_arm/analysis/FR3_STL_DH_ANALYSIS.md) - STL文件与DH参数深度分析

#### 使用指南 (`guides/`)
- [📝 **STL_NAMING_GUIDE.md**](./fr3_mechanical_arm/guides/STL_NAMING_GUIDE.md) - FR3机械臂STL文件命名规则

#### 用户手册 (`user_manual/`)
- [📚 机器人基础操作](./fr3_mechanical_arm/user_manual/【FR3】1.%20机器人基础%20—%20法奥意威协作机器人用户手册%203.8.2%20文档.html)
- [🎮 机器人运动控制](./fr3_mechanical_arm/user_manual/【FR3】2.%20机器人运动%20—%20法奥意威协作机器人用户手册%203.8.2%20文档.html)
- [🔌 机器人IO操作](./fr3_mechanical_arm/user_manual/【FR3】3.%20机器人IO%20—%20法奥意威协作机器人用户手册%203.8.2%20文档.html)
- [⚙️ 更多官方文档...](./fr3_mechanical_arm/user_manual/)

#### API协议 (`api_protocol/`)
- [📡 通讯指令协议](./fr3_mechanical_arm/api_protocol/协作机器人控制器通讯指令协议用户手册.html)
- [📊 状态反馈协议](./fr3_mechanical_arm/api_protocol/机器人控制器8083端口状态反馈用户手册.html)

#### SDK参考 (`sdk_reference/`)
- [📋 SDK错误码对照表](./fr3_mechanical_arm/sdk_reference/SDK%20错误码对照表%20—%20法奥意威协作机器人用户手册%203.8.2%20文档.html)

**技术规格**:
- 负载: 3kg
- 工作半径: 630mm  
- 重复定位精度: ±0.1mm
- 关节数: 7个
- 控制频率: 1kHz

### 🚚 Hermes 移动底盘 (`hermes_chassis/`)

#### 用户手册 (`user_manual/`)
- [📖 **赫尔墨斯用户手册**](./hermes_chassis/user_manual/赫尔墨斯%20Hermes%20用户手册.html) - 完整用户操作指南

#### RESTful API (`restful_api/`)
- [🌐 **Slamware RESTful API开发手册**](./hermes_chassis/restful_api/Slamware%20RESTful%20API开发手册%20-%20飞书云文档.html)
- [🔧 **Swagger UI接口**](./hermes_chassis/restful_api/swagger/Swagger%20Restful%20UI.html)

#### 配置指南 (`configuration/`)
- [⚙️ **Hermes底盘其他知识**](./hermes_chassis/configuration/Hermes%20底盘其他知识.html)

**技术规格**:
- 最大速度: 1.5 m/s
- 负载能力: 50kg
- 导航方式: 激光SLAM
- 定位精度: ±5cm
- 电池续航: 8小时

### 👁️ Gemini 视觉系统 (`gemini_vision/`)

#### 产品规格 (`product_specs/`)
- [📊 **Gemini 335相机功能矩阵**](./gemini_vision/product_specs/Gemini%20335%20相机功能矩阵.html)
- [📋 **USB设备产品规格书**](./gemini_vision/product_specs/Gemini%20335系列-USB设备产品规格书.html)

#### 快速开始 (`quick_start/`)
- [⚡ **Gemini 335Lg快速启动指南**](./gemini_vision/quick_start/Gemini%20335Lg快速启动指南.html)

#### 系统要求 (`system_requirements/`)
- [💻 **系统要求和支持**](./gemini_vision/system_requirements/Gemini335支持的上位机和对系统要求.html)

#### 使用指南 (`user_guide/`)
- [📖 **相机使用指南**](./gemini_vision/user_guide/Gemini%20335系列相机简易使用指南.html)

**技术规格**:
- 分辨率: 1280×720 (RGB) + 1280×720 (深度)
- 帧率: 30fps
- 深度范围: 0.3-10m
- 接口: USB 3.0
- SDK: 跨平台支持

### 🎮 仿真系统 (`simulation/`)
- [🎯 **ROBOTSIM_GUIDE.md**](./simulation/ROBOTSIM_GUIDE.md) - 机器人仿真模块使用指南

**仿真特性**:
- 高保真度物理仿真
- 实时运动学计算
- 碰撞检测
- 3D可视化界面

## 🔗 硬件集成

### 系统连接
```
控制网络拓扑 (192.168.58.x):
├── FR3 右臂: 192.168.58.2
├── FR3 左臂: 192.168.58.3
├── Hermes 底盘: 192.168.31.211:1448
└── 主控制器: 192.168.58.1
```

### 通信协议
- **FR3**: TCP/IP + fairino SDK
- **Hermes**: HTTP RESTful API
- **Gemini**: USB 3.0 + OpenCV
- **仿真**: 本地VTK渲染

## 🚀 快速开始指南

### 1. 硬件连接
1. 确保所有设备在同一网络
2. 检查IP地址配置
3. 验证硬件连接状态

### 2. 系统初始化
1. 启动Hermes底盘
2. 上电FR3机械臂
3. 连接Gemini相机
4. 运行连接测试

### 3. 功能验证
1. 测试机械臂基本运动
2. 验证底盘导航功能
3. 检查视觉系统数据
4. 运行综合演示

## 🔧 故障排除

### 常见问题
- **连接超时**: 检查网络配置和IP地址
- **运动异常**: 验证机械臂标定和限位
- **视觉数据异常**: 检查相机驱动和USB连接
- **仿真卡顿**: 调整渲染质量和更新频率

### 联系支持
- FR3技术支持: 法奥意威官方文档
- Hermes支持: 思岚科技技术支持
- Gemini支持: 奥比中光技术文档

## 🔗 相关链接

- **⬅️ 返回文档中心**: [../README.md](../README.md)
- **📋 项目文档**: [../project/](../project/)
- **💻 界面系统**: [../interfaces/](../interfaces/)
- **🚀 部署指南**: [../deployment/](../deployment/)
- **🧪 测试文档**: [../testing/](../testing/)

---

**📝 维护信息**  
**更新时间**: 2025-07-25  
**硬件文档数量**: 24+ HTML技术文档  
**涵盖设备**: 4个主要硬件模块  
**状态**: 持续更新中
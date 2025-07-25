# XC-ROBOT 项目文档中心

> 轮式双臂类人形机器人控制系统完整技术文档

[![项目状态](https://img.shields.io/badge/状态-开发中-green.svg)]()
[![文档版本](https://img.shields.io/badge/文档版本-v2.3.2-blue.svg)]()
[![Python版本](https://img.shields.io/badge/Python-3.8+-yellow.svg)]()

## 📋 快速导航

### 🎯 项目概述
- [📖 项目简介](./project/overview/README.md) - 项目基本介绍和架构概览
- [📊 技术全览](./project/overview/PROJECT_TECHNICAL_OVERVIEW.md) - 完整技术架构说明
- [📝 项目背景](./project/overview/xc_os_context.md) - 项目发展历程和背景信息
- [📋 项目评估](./project/overview/Project_Review.md) - 项目评估和分析报告

### 🚀 快速开始
- [⚡ 部署指南](./deployment/installation/DEPLOYMENT_GUIDE.md) - FR3机械臂系统部署
- [🔧 跨平台解决方案](./deployment/configuration/CROSS_PLATFORM_SOLUTION.md) - Mac/Windows/Linux适配
- [📋 依赖配置](./deployment/installation/requirements_basic.txt) - 基础依赖说明

### 💻 界面系统
- [🖥️ Web GUI 2.0](./interfaces/web_gui/XC_ROBOT_WEB_GUI_2.0_技术说明.md) - 现代化Web界面技术说明
- [📱 GUI功能说明](./interfaces/web_gui/GUI_DESCRIPTION.md) - 用户界面功能详述
- [📖 Web GUI使用手册](./interfaces/web_gui/README_WEB_GUI.md) - Web界面使用指南

### 🤖 硬件系统

#### FR3 机械臂
- [🔬 技术分析](./hardware/fr3_mechanical_arm/analysis/FR3_ROBOT_ANALYSIS.md) - 运动学和控制分析
- [📐 STL/DH分析](./hardware/fr3_mechanical_arm/analysis/FR3_STL_DH_ANALYSIS.md) - 3D模型和参数深度分析
- [📝 STL命名规则](./hardware/fr3_mechanical_arm/guides/STL_NAMING_GUIDE.md) - 3D模型文件规范
- [📚 用户手册](./hardware/fr3_mechanical_arm/user_manual/) - 官方技术文档集合
- [🔌 API协议](./hardware/fr3_mechanical_arm/api_protocol/) - 通信协议文档

#### Hermes 移动底盘
- [📖 用户手册](./hardware/hermes_chassis/user_manual/赫尔墨斯%20Hermes%20用户手册.html) - 底盘使用说明
- [🌐 RESTful API](./hardware/hermes_chassis/restful_api/) - HTTP接口文档
- [⚙️ 配置指南](./hardware/hermes_chassis/configuration/) - 底盘配置说明

#### Gemini 视觉系统
- [🎥 产品规格](./hardware/gemini_vision/product_specs/) - 相机技术规格
- [⚡ 快速开始](./hardware/gemini_vision/quick_start/) - 快速启动指南
- [💻 系统要求](./hardware/gemini_vision/system_requirements/) - 硬件和软件要求
- [📖 使用指南](./hardware/gemini_vision/user_guide/) - 详细使用说明

#### 仿真系统
- [🎮 RobotSim指南](./hardware/simulation/ROBOTSIM_GUIDE.md) - 机器人仿真系统使用

### 🧪 测试与质量
- [📋 测试计划](./testing/plans/ROBOT_TESTING_PLAN.md) - 系统综合测试规划

### 📚 开发指南
- [🔧 开发调试日志](./project/development/development_log.md) - 开发过程记录
- [📝 开发指导](./development/guides/CLAUDE_CODE_INSTRUCTIONS.md) - Claude Code使用指南
- [🔗 API文档](./api/) - 接口文档集合

### 📖 参考资料
- [🎛️ 控制文档](./reference/control_docs/) - 设备控制技术文档
- [🏗️ 系统文档](./reference/system_docs/) - 系统架构和设计文档

## 🗂️ 文档结构概览

```
docs/
├── 📁 api/                     # API接口文档
├── 📁 deployment/              # 部署和配置
│   ├── configuration/          # 配置文件和说明
│   ├── installation/           # 安装部署指南
│   └── scripts/               # 部署脚本
├── 📁 development/             # 开发指南
│   ├── api_guides/            # API开发指南
│   ├── examples/              # 代码示例
│   ├── guides/               # 开发指导
│   └── tutorials/            # 教程文档
├── 📁 hardware/               # 硬件系统文档
│   ├── fr3_mechanical_arm/    # FR3机械臂
│   ├── hermes_chassis/        # Hermes底盘
│   ├── gemini_vision/         # Gemini视觉
│   └── simulation/           # 仿真系统
├── 📁 interfaces/             # 用户界面
│   └── web_gui/              # Web图形界面
├── 📁 project/                # 项目文档
│   ├── overview/             # 项目概述
│   ├── development/          # 开发记录
│   └── analysis/            # 分析报告
├── 📁 reference/              # 参考资料
│   ├── control_docs/         # 控制文档
│   └── system_docs/         # 系统文档
└── 📁 testing/               # 测试文档
    └── plans/               # 测试计划
```

## 🔍 快速查找

### 按功能分类
- **🎮 控制系统**: [FR3控制](./reference/control_docs/fr3_control_doc.md) | [Hermes控制](./reference/control_docs/hermes_control_doc.md) | [双臂集成](./reference/control_docs/dual_arm_integration_guide.md)
- **👁️ 视觉系统**: [Gemini控制](./reference/control_docs/gemini335_control_doc.md) | [视觉重建](./reference/system_docs/xc_recon_system.md)
- **🖥️ 用户界面**: [Web GUI](./interfaces/web_gui/) | [系统设计](./project/design/XC_OS_SYSTEM_DESIGN.md)
- **🔧 开发工具**: [开发指南](./development/guides/) | [API文档](./api/) | [测试框架](./testing/)

### 按用户角色
- **👨‍💻 开发者** → [开发指南](./development/) | [API文档](./api/) | [代码示例](./development/examples/)
- **🔧 部署人员** → [部署指南](./deployment/) | [配置说明](./deployment/configuration/) | [脚本工具](./deployment/scripts/)
- **🧪 测试人员** → [测试计划](./testing/plans/) | [测试指南](./development/guides/)
- **📚 研究人员** → [技术分析](./hardware/fr3_mechanical_arm/analysis/) | [系统文档](./reference/system_docs/)

### 按紧急程度
- **🚨 紧急问题** → [故障排除](./hardware/fr3_mechanical_arm/troubleshooting/) | [开发日志](./project/development/development_log.md)
- **⚡ 快速上手** → [快速开始](./deployment/installation/) | [Web GUI手册](./interfaces/web_gui/README_WEB_GUI.md)
- **📋 详细了解** → [技术全览](./project/overview/PROJECT_TECHNICAL_OVERVIEW.md) | [项目背景](./project/overview/xc_os_context.md)

## 🏷️ 文档标签

| 标签 | 说明 | 示例文档 |
|------|------|----------|
| 🚀 入门 | 快速开始和基础指南 | [部署指南](./deployment/installation/DEPLOYMENT_GUIDE.md) |
| 🔧 配置 | 系统配置和设置 | [跨平台方案](./deployment/configuration/CROSS_PLATFORM_SOLUTION.md) |
| 📊 分析 | 深度技术分析 | [FR3分析](./hardware/fr3_mechanical_arm/analysis/FR3_ROBOT_ANALYSIS.md) |
| 🎮 控制 | 设备控制相关 | [控制文档](./reference/control_docs/) |
| 👁️ 视觉 | 视觉系统相关 | [Gemini文档](./hardware/gemini_vision/) |
| 🌐 网络 | 网络通信相关 | [RESTful API](./hardware/hermes_chassis/restful_api/) |
| 🧪 测试 | 测试和验证 | [测试计划](./testing/plans/) |

## 📞 获取帮助

- **项目问题**: 查看 [开发日志](./project/development/development_log.md) 获取常见问题解决方案
- **技术支持**: 参考 [技术全览](./project/overview/PROJECT_TECHNICAL_OVERVIEW.md) 了解系统架构
- **部署问题**: 查看 [部署指南](./deployment/installation/DEPLOYMENT_GUIDE.md) 和 [跨平台方案](./deployment/configuration/CROSS_PLATFORM_SOLUTION.md)

## 📈 文档统计

- **总文档数**: 33+ Markdown文档 + 24+ HTML技术文档
- **覆盖模块**: 7个主要功能模块
- **支持平台**: Windows 11 / macOS / Linux
- **更新频率**: 持续更新中

---

**📝 文档维护**: 本文档集合由 XC-ROBOT 开发团队维护  
**🔄 最后更新**: 2025-07-25  
**📧 联系方式**: 技术问题请参考各模块的具体文档

*🤖 部分文档使用 Claude Code 协助生成和整理*
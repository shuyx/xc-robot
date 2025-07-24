# XC-RECON-V2 项目文档索引

**最后更新**: 2025-07-19  
**文档版本**: v1.0  
**维护者**: Kevin Yuan

> 🤖 **Claude AI协作**: 请优先阅读 [CLAUDE.md](../CLAUDE.md) 获取项目核心记忆和工作指南

---

## 📖 文档概述

本文档库包含XC-RECON-V2项目重构所需的所有背景资料、技术文档、设计规范和测试指南。这些文档是从原始xc-robot项目中精选和整理的核心资料，为开发团队提供全面的技术参考。

## 🗂️ 文档结构

### 📁 [technical/](./technical/) - 技术文档
系统架构、技术栈和核心概念的详细说明

| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [xc_os_context.md](./technical/xc_os_context.md) | **项目核心背景** | ⭐⭐⭐⭐⭐ | 了解项目定位、硬件配置、技术栈 |
| [PROJECT_TECHNICAL_OVERVIEW.md](./technical/PROJECT_TECHNICAL_OVERVIEW.md) | **技术全览** | ⭐⭐⭐⭐⭐ | 系统架构、目录结构、模块功能 |
| [GUI_DESCRIPTION.md](./technical/GUI_DESCRIPTION.md) | **GUI界面功能说明** | ⭐⭐⭐⭐ | PyQt5界面布局和功能详解 |

### 📁 [hardware/](./hardware/) - 硬件文档
机器人硬件、控制协议和配置说明

#### 基础硬件文档
| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [FR3_ROBOT_ANALYSIS.md](./hardware/FR3_ROBOT_ANALYSIS.md) | **FR3机械臂分析** | ⭐⭐⭐⭐⭐ | 运动学模型、DH参数、控制接口 |
| [fr3_control_doc.md](./hardware/fr3_control_doc.md) | **FR3控制文档** | ⭐⭐⭐⭐ | 机械臂控制API和编程接口 |
| [hermes_control_doc.md](./hardware/hermes_control_doc.md) | **Hermes底盘控制** | ⭐⭐⭐⭐ | 移动底盘控制和导航API |
| [gemini335_control_doc.md](./hardware/gemini335_control_doc.md) | **视觉系统文档** | ⭐⭐⭐ | 相机集成和视觉处理 |
| [robot_config_reference.json](./hardware/robot_config_reference.json) | **配置参考** | ⭐⭐⭐ | 硬件配置参数和网络设置 |

#### 🆕 完整API文档集合 (2025-07-19新增)
| 目录/文件 | 描述 | 重要程度 | 用途 |
|-----------|------|----------|------|
| **[fr3_sdk/](./hardware/fr3_sdk/)** | **FR3 Python SDK完整文档** | ⭐⭐⭐⭐⭐ | 法奥意威FR3协作机器人完整开发手册 |
| [fr3_sdk/【FR3】1. 机器人基础.html](./hardware/fr3_sdk/) | FR3基础功能 | ⭐⭐⭐⭐⭐ | 机器人连接、初始化、基本操作 |
| [fr3_sdk/【FR3】2. 机器人运动.html](./hardware/fr3_sdk/) | FR3运动控制 | ⭐⭐⭐⭐⭐ | 轨迹规划、运动控制、坐标系 |
| [fr3_sdk/【FR10】10. 机器人力控.html](./hardware/fr3_sdk/) | FR3力控功能 | ⭐⭐⭐⭐ | 力反馈控制、碰撞检测、安全功能 |
| [fr3_sdk/SDK 错误码对照表.html](./hardware/fr3_sdk/) | FR3错误码参考 | ⭐⭐⭐⭐ | 错误诊断和故障排除 |
| **[hermes_api/](./hardware/hermes_api/)** | **Hermes底盘RESTful API文档** | ⭐⭐⭐⭐⭐ | 思岚科技Hermes底盘完整开发文档 |
| [hermes_api/赫尔墨斯 Hermes 用户手册.html](./hardware/hermes_api/) | Hermes用户手册 | ⭐⭐⭐⭐⭐ | 底盘控制、导航、定位功能 |
| [hermes_api/Slamware RESTful API开发手册.html](./hardware/hermes_api/) | RESTful API开发 | ⭐⭐⭐⭐⭐ | HTTP API接口、数据格式、调用示例 |
| [hermes_api/Swagger Restful UI.html](./hardware/hermes_api/) | API接口文档 | ⭐⭐⭐⭐ | 交互式API文档和测试界面 |
| **[gemini335/](./hardware/gemini335/)** | **Gemini335视觉系统文档** | ⭐⭐⭐⭐ | TOF深度相机完整开发文档 |
| [gemini335/Gemini 335系列相机简易使用指南.html](./hardware/gemini335/) | 相机使用指南 | ⭐⭐⭐⭐ | 快速入门、基本配置、软件安装 |
| [gemini335/Gemini 335 相机功能矩阵.html](./hardware/gemini335/) | 功能规格参考 | ⭐⭐⭐ | 技术参数、支持功能、兼容性 |
| [gemini335/Gemini 335系列-USB设备产品规格书.html](./hardware/gemini335/) | 硬件规格书 | ⭐⭐⭐ | 物理参数、接口规格、环境要求 |

### 📁 [design/](./design/) - 设计文档
UI设计、组件规范和用户体验指南

| 文件/目录 | 描述 | 重要程度 | 用途 |
|-----------|------|----------|------|
| [design_reference/](./design/design_reference/) | **完整设计参考** | ⭐⭐⭐⭐⭐ | UI/UX设计规范和实现指南 |
| [component_specs.md](./design/design_reference/component_specs.md) | **组件规范** | ⭐⭐⭐⭐ | PyQt5组件实现规格 |
| [style_guide.md](./design/design_reference/style_guide.md) | **样式指南** | ⭐⭐⭐⭐ | 视觉设计和交互规范 |
| [ui_mockups/](./design/design_reference/ui_mockups/) | **UI原型** | ⭐⭐⭐⭐⭐ | HTML界面原型和设计参考 |
| [Smartinterface_Planning_doc.md](./design/Smartinterface_Planning_doc.md) | **智能交互模块设计** | ⭐⭐⭐⭐ | AI交互界面设计方案 |

### 📁 [testing/](./testing/) - 测试文档
测试计划、测试程序和质量保证指南

| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [Testing_Plan.md](./testing/Testing_Plan.md) | **综合测试规划** | ⭐⭐⭐⭐⭐ | 系统测试策略和安全规范 |
| [Testing_Programs_Guide.md](./testing/Testing_Programs_Guide.md) | **测试程序指南** | ⭐⭐⭐⭐ | 测试代码编写和执行规范 |

### 📁 [development/](./development/) - 开发文档
开发指南、部署说明和集成文档

| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [DEPLOYMENT_GUIDE.md](./development/DEPLOYMENT_GUIDE.md) | **部署指南** | ⭐⭐⭐⭐ | 环境配置和问题解决 |
| [dual_arm_integration_guide.md](./development/dual_arm_integration_guide.md) | **双臂集成指南** | ⭐⭐⭐⭐ | 双机械臂协调控制实现 |
| [CROSS_PLATFORM_SOLUTION.md](./development/CROSS_PLATFORM_SOLUTION.md) | **跨平台开发方案** | ⭐⭐⭐ | Mac/Windows协作开发解决方案 |

---

## 🎯 快速导航

### 新团队成员必读 📚
1. **[xc_os_context.md](./technical/xc_os_context.md)** - 了解项目背景和目标
2. **[PROJECT_TECHNICAL_OVERVIEW.md](./technical/PROJECT_TECHNICAL_OVERVIEW.md)** - 掌握技术架构
3. **[FR3_ROBOT_ANALYSIS.md](./hardware/FR3_ROBOT_ANALYSIS.md)** - 理解硬件平台

### 前端开发者关注 🎨
1. **[design_reference/](./design/design_reference/)** - UI/UX设计规范
2. **[component_specs.md](./design/design_reference/component_specs.md)** - 组件实现规格
3. **[ui_mockups/](./design/design_reference/ui_mockups/)** - 界面原型参考

### 后端开发者关注 ⚙️
1. **[FR3_ROBOT_ANALYSIS.md](./hardware/FR3_ROBOT_ANALYSIS.md)** - 机械臂控制接口
2. **[dual_arm_integration_guide.md](./development/dual_arm_integration_guide.md)** - 双臂集成
3. **[Testing_Plan.md](./testing/Testing_Plan.md)** - 测试和验证策略

### 🆕 硬件集成开发者关注 🔧 (新增)
1. **[fr3_sdk/](./hardware/fr3_sdk/)** - FR3 Python SDK完整API文档
2. **[hermes_api/](./hardware/hermes_api/)** - Hermes底盘RESTful API文档
3. **[gemini335/](./hardware/gemini335/)** - Gemini335视觉系统完整文档

### 系统集成者关注 🔧
1. **[DEPLOYMENT_GUIDE.md](./development/DEPLOYMENT_GUIDE.md)** - 部署和配置
2. **[robot_config_reference.json](./hardware/robot_config_reference.json)** - 配置参数
3. **[Testing_Programs_Guide.md](./testing/Testing_Programs_Guide.md)** - 测试执行

---

## 📋 使用指南

### 如何使用这些文档

#### 📖 阅读顺序建议
1. **理解背景** → `xc_os_context.md`
2. **掌握架构** → `PROJECT_TECHNICAL_OVERVIEW.md`
3. **选择专业领域** → 根据角色选择相关文档
4. **深入细节** → 阅读具体实现文档

#### 🔍 AI助手参考指南
当您需要AI助手帮助时，请按以下顺序引用：

```bash
# 1. 首先阅读项目记忆 (必读)
@CLAUDE.md - 🤖 Claude项目记忆和工作指南

# 2. 根据任务类型选择相关文档
@docs/technical/xc_os_context.md - 了解项目背景和约束
@docs/hardware/FR3_ROBOT_ANALYSIS.md - 获取机械臂技术细节  
@docs/design/design_reference/ - 参考UI/UX设计规范
@docs/testing/Testing_Plan.md - 了解测试要求和安全规范
@xc_recon_8.md - 查看最新开发状态

# 3. 硬件开发专项文档 (新增)
@docs/hardware/fr3_sdk/ - FR3机械臂Python SDK完整API参考
@docs/hardware/hermes_api/ - Hermes底盘RESTful API和开发手册
@docs/hardware/gemini335/ - Gemini335视觉系统完整技术文档

# 4. 原项目遗留文档参考 (Legacy Documents)
@docs/technical/project_overview_legacy.md - 原项目v2.3.2完整技术架构
@docs/development/robotsim_guide.md - VTK 3D仿真系统实现指南
@docs/hardware/fr3_stl_dh_analysis.md - FR3 STL模型与DH参数分析

# 5. 根目录核心文档参考 (Root Directory Core Documents)
@docs/technical/xc_os_system_design.md - XC-OS系统设计规划和架构愿景
@docs/technical/xc_recon_system_design.md - XC-RECON重构设计方案
@docs/design/smartinterface_planning_root_version.md - 智能交互模块设计
@docs/development/claude_code_instructions.md - Claude AI开发协作指令
```

#### 📝 文档维护
- **更新频率**: 每个开发阶段结束后更新
- **版本控制**: 重要变更记录在git commit中
- **责任分工**: 各模块负责人维护相关文档

---

## 🔄 项目背景说明

### 原始项目概况
- **项目名称**: XC-ROBOT 轮式双臂类人形机器人控制系统
- **技术栈**: Python + PyQt5 + VTK + FR3 API
- **硬件平台**: FR3双机械臂 + Hermes移动底盘
- **开发阶段**: MVP1.0版本，功能完整

### 重构项目目标
- **项目名称**: XC-RECON-V2 现代化重构
- **技术栈**: FastAPI + Vue 3 + TypeScript + Element Plus
- **架构模式**: 前后端分离，微服务架构
- **开发目标**: 企业级应用，可扩展性和维护性

### 文档价值
这些文档为重构项目提供：
1. **需求理解**: 完整的功能需求和技术约束
2. **技术参考**: 硬件接口、协议规范、算法实现
3. **设计指导**: UI/UX设计原则和实现方案
4. **质量标准**: 测试规范和安全要求

---

## 📚 原项目遗留文档 (Legacy Documents)

**说明**: 以下文档来自原始xc-robot项目的Md_files文件夹，提供原项目的完整技术背景和实现经验。

### 📁 [technical/] - 原项目技术文档
| 文件名 | 格式 | 描述 | 重要程度 | 用途 |
|--------|------|------|----------|------|
| [project_overview_legacy.md](./technical/project_overview_legacy.md) | MD/HTML | **原项目技术全览** | ⭐⭐⭐⭐⭐ | 完整的v2.3.2技术架构和实现细节 |
| [original_project_readme.md](./technical/original_project_readme.md) | MD/HTML | **原项目README** | ⭐⭐⭐⭐ | 项目基础信息和代码结构 |
| [web_gui_legacy.md](./technical/web_gui_legacy.md) | MD/HTML | **Web GUI遗留说明** | ⭐⭐⭐ | 早期Web GUI设计思路 |
| [web_gui_v2_tech_spec.md](./technical/web_gui_v2_tech_spec.md) | MD/HTML | **Web GUI 2.0技术规范** | ⭐⭐⭐⭐ | Web GUI详细技术说明 |
| [gui_description_legacy.html](./technical/gui_description_legacy.html) | HTML | **GUI界面功能说明** | ⭐⭐⭐⭐ | PyQt5界面详细功能描述 |

### 📁 [hardware/] - 硬件遗留文档  
| 文件名 | 格式 | 描述 | 重要程度 | 用途 |
|--------|------|------|----------|------|
| [fr3_robot_analysis_legacy.html](./hardware/fr3_robot_analysis_legacy.html) | HTML | **FR3机械臂分析遗留版** | ⭐⭐⭐⭐⭐ | 原项目FR3运动学分析对比参考 |
| [fr3_stl_dh_analysis.md](./hardware/fr3_stl_dh_analysis.md) | MD/HTML | **FR3 STL模型DH分析** | ⭐⭐⭐⭐ | 3D模型与DH参数对应关系 |

### 📁 [development/] - 开发遗留文档
| 文件名 | 格式 | 描述 | 重要程度 | 用途 |
|--------|------|------|----------|------|
| [deployment_guide_legacy.html](./development/deployment_guide_legacy.html) | HTML | **部署指南遗留版** | ⭐⭐⭐⭐ | 原项目完整部署指南对比参考 |
| [robotsim_guide.md](./development/robotsim_guide.md) | MD/HTML | **机器人仿真指南** | ⭐⭐⭐⭐ | VTK 3D仿真系统实现指南 |
| [stl_naming_guide.md](./development/stl_naming_guide.md) | MD/HTML | **STL模型命名指南** | ⭐⭐⭐ | 3D模型文件命名规范 |

### 📁 [testing/] - 测试遗留文档
| 文件名 | 格式 | 描述 | 重要程度 | 用途 |
|--------|------|------|----------|------|
| [robot_testing_plan_legacy.html](./testing/robot_testing_plan_legacy.html) | HTML | **机器人测试计划遗留版** | ⭐⭐⭐⭐ | 原项目测试策略对比参考 |
| [development_log_legacy.md](./testing/development_log_legacy.md) | MD | **开发日志遗留版** | ⭐⭐⭐ | 原项目开发过程记录 |

### 📁 Supporting Files
| 文件/目录 | 描述 | 用途 |
|-----------|------|------|
| [images/](./images/) | **完整图片资源库** | 原项目所有文档配图和截图 |
| [css/](./css/) | **HTML文档样式** | 支持HTML文档的样式渲染 |

---

## 📋 根目录核心文档 (Root Directory Documents)

**说明**: 以下文档来自原始xc-robot项目根目录，包含项目核心设计、规划和开发指导文档。

### 📁 [technical/] - 项目核心技术文档
| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [xc_os_system_design.md](./technical/xc_os_system_design.md) | **XC-OS系统设计规划** | ⭐⭐⭐⭐⭐ | XC-OS模块化架构和系统设计愿景 |
| [xc_recon_system_design.md](./technical/xc_recon_system_design.md) | **XC-RECON重构设计方案** | ⭐⭐⭐⭐⭐ | 重构架构设计和技术栈选择 |
| [xc_os_context_root_version.md](./technical/xc_os_context_root_version.md) | **项目背景根目录版本** | ⭐⭐⭐⭐ | 根目录版本的项目背景对比参考 |
| [project_review.md](./technical/project_review.md) | **项目评审文档** | ⭐⭐⭐⭐ | 项目阶段评审和改进建议 |
| [project_context.md](./technical/project_context.md) | **项目上下文** | ⭐⭐⭐ | 项目开发背景和上下文信息 |
| [xc_recon_v1_notes.md](./technical/xc_recon_v1_notes.md) | **重构V1笔记** | ⭐⭐⭐ | 早期重构思路和记录 |

### 📁 [hardware/] - 硬件系统扩展文档
| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [xc_gemini_system.md](./hardware/xc_gemini_system.md) | **XC Gemini系统文档** | ⭐⭐⭐⭐ | Gemini视觉系统集成方案 |

### 📁 [design/] - 系统设计和规划文档
| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [smartinterface_planning_root_version.md](./design/smartinterface_planning_root_version.md) | **智能交互规划根目录版** | ⭐⭐⭐⭐⭐ | 根目录版本的智能交互设计 |
| [scenario_planning.md](./design/scenario_planning.md) | **场景规划文档** | ⭐⭐⭐⭐ | 机器人应用场景规划 |
| [simulation_planning.md](./design/simulation_planning.md) | **仿真规划文档** | ⭐⭐⭐⭐ | 仿真系统设计规划 |
| [monitor_planning.md](./design/monitor_planning.md) | **监控规划文档** | ⭐⭐⭐ | 系统监控设计规划 |

### 📁 [development/] - 开发工具和指导文档
| 文件名 | 描述 | 重要程度 | 用途 |
|--------|------|----------|------|
| [claude_code_instructions.md](./development/claude_code_instructions.md) | **Claude Code指令文档** | ⭐⭐⭐⭐ | Claude AI开发协作指令 |
| [claude_ai_guide_legacy.md](./development/claude_ai_guide_legacy.md) | **Claude AI指南遗留版** | ⭐⭐⭐ | 原项目Claude协作指南 |

---

## 📞 联系方式

如有文档相关问题，请联系：
- **项目负责人**: Kevin Yuan
- **技术讨论**: 通过git issues或项目群组
- **文档更新**: 提交PR到docs目录

---

**文档说明**: 本文档库是XC-RECON-V2项目的技术知识库，包含了从原始xc-robot项目继承的核心技术资料。请根据您的角色和需求选择相关文档进行阅读。
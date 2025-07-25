# 设计文档中心

> XC-ROBOT 系统设计资源和UI/UX设计文档

## 📁 设计文档结构

```
design/
├── ui_mockups/           # HTML界面原型
│   ├── smart_interface_chat.html    # 对话式任务界面
│   ├── smart_interface_elivate.html # 智能提升界面
│   └── smart_interface_face.html    # 人脸识别界面
├── component_specs.md    # PyQt5组件实现规格
├── style_guide.md        # 界面设计规格和样式指南
├── ui_file_management.md # UI文件管理和开发指南
├── use_method.md         # Claude Code开发指令模板
├── ui/                   # 历史UI设计文档
│   ├── *.docx           # Word设计文档
│   ├── *.html           # HTML设计原型
│   └── xc_os_newui files/ # 新UI设计资源
└── assets/              # 设计资源
    ├── UI_ck_image/     # UI检查图片
    ├── old_gui/         # 旧版界面截图
    ├── *.png            # 图标和界面图片
    └── *.jpg            # 背景图和logos
```

## 🎨 UI开发框架

### 核心设计文档
- **📋 component_specs.md** - PyQt5组件实现技术规格
  - HTML到PyQt5的精确映射关系
  - 完整的样式表配置模板
  - JavaScript-Python通信接口规范
  
- **🎯 style_guide.md** - 界面设计规格和样式指南
  - 完整的界面设计规格（基于smart_interface_chat.html）
  - 详细的尺寸、布局、颜色、字体规范
  - PyQt5实现要点和技术指导

- **📖 ui_file_management.md** - UI文件管理和开发指南
  - 界面文件组织结构说明
  - 命名规范和开发流程指导
  - Claude Code指令模板

### HTML界面原型
- **💬 smart_interface_chat.html** - 对话式任务界面
  - 侧边栏导航、实时对话、任务监控
- **⬆️ smart_interface_elivate.html** - 智能提升界面
- **👤 smart_interface_face.html** - 人脸识别界面

### 历史设计文档
- **XC-ROBOT+侧边栏树形导航设计方案.docx** - 侧边栏导航设计方案
- **xc-os+system+规划介绍.html** - 系统规划介绍
- **xc-os+system新增+UI&功能.docx** - 新增UI和功能设计
- **xc_os_newui.html** - 新UI界面原型
- **xc_os_newui files/** - 完整的新UI设计资源包

## 🖼️ 设计资源

### 图标和界面元素
- **background.png** - 背景图片
- **info.png** - 信息图标
- **xc logo.jpg** - XC品牌Logo

### 界面截图
- **old_gui/** - 包含旧版GUI的5张界面截图
- **UI_ck_image/** - UI检查和验证图片

## 🚀 快速开发指南

### Claude Code开发指令
```bash
# 基于HTML原型开发PyQt5界面的标准指令：
"请严格按照design_reference/ui_mockups/[具体文件名].html设计实现界面布局，
但配色必须使用项目现有配色系统。参考color_mapping.md中的配色映射关系，
保持HTML设计的所有布局、尺寸、间距、圆角等视觉规格，只替换配色方案。"
```

### 开发流程
1. **选择界面模板** - 从ui_mockups/选择合适的HTML原型
2. **阅读技术规格** - 参考component_specs.md了解实现要求
3. **使用开发指令** - 按照use_method.md中的模板开发
4. **验证界面质量** - 对照style_guide.md检查规格一致性

## 🎯 设计原则

### 界面设计理念
1. **现代化**: 采用现代化的界面设计语言
2. **直观性**: 清晰的信息层次和操作流程
3. **一致性**: 统一的视觉风格和交互模式
4. **响应式**: 适配不同屏幕尺寸和设备

### 用户体验
1. **易用性**: 简化操作流程，降低学习成本
2. **安全性**: 明确的安全提示和操作确认
3. **效率性**: 快速访问常用功能
4. **可访问性**: 支持不同用户需求

### 技术实现
1. **PyQt5集成**: 优先使用QWebEngineView加载HTML内容
2. **配色统一**: 使用项目现有配色系统替代HTML原色
3. **通信桥梁**: JavaScript-Python通信确保功能完整
4. **性能优化**: 合理使用组件和资源管理

## 🔗 相关链接

- **⬅️ 返回文档中心**: [../README.md](../README.md)
- **💻 界面系统文档**: [../interfaces/](../interfaces/)
- **🚀 快速开始**: [../QUICKSTART.md](../QUICKSTART.md)
- **📋 项目文档**: [../project/](../project/)

---

**📝 维护信息**  
**更新时间**: 2025-07-25  
**设计版本**: XC-OS System 新UI设计  
**状态**: 设计资源已整理完成
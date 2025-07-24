# Vue 3 + TypeScript 界面实现指导手册

## 核心指导原则

**严格按照design_reference目录中的HTML设计实现Vue 3组件，配色系统与现有前端架构保持一致。**

### 技术实现要求
1. `design_reference/ui_mockups/[具体UI文件名].html` - **主要UI参考**
2. `design_reference/style_guide.md` - **样式规格标准**  
3. `design_reference/component_specs.md` - **Vue 3组件实现映射**

⚠️ **核心要求**: **严格按照HTML中的所有设计，包括布局、配色、尺寸等一切视觉规格，但使用Vue 3 + Element Plus技术栈实现**

## 标准开发指令模板

```bash
"请分析并严格按照design_reference/ui_mockups/[具体文件名].html的设计实现Vue 3 + TypeScript组件：

第一步 - 分析HTML设计：
- 仔细分析HTML文件中的布局结构、组件层次
- 提取HTML中实际使用的所有颜色值（无论是什么配色主题）
- 理解所有交互逻辑和状态变化

第二步 - Vue 3实现要求：
- 使用Vue 3 + TypeScript + Element Plus技术栈
- 完全复制HTML的布局结构和组件层次
- 精确复制所有尺寸比例、间距、圆角、字体大小
- 严格使用HTML中的具体颜色值（动态适配不同配色主题）
- 保持HTML中的信息层次和组织结构
- 实现HTML中展示的所有交互功能

第三步 - 技术实现：
- 使用Vue 3 Composition API + TypeScript
- Element Plus UI组件库作为基础
- Pinia状态管理
- Vue Router路由管理
- 与FastAPI后端通过HTTP/WebSocket通信

约束条件：不得偏离HTML设计的任何视觉规格，但必须使用现代Web技术栈实现"
```

## 重构技术栈映射

### 原PyQt5 → 新Vue 3架构
- **PyQt5窗口** → Vue 3页面组件(.vue)
- **QWidget** → Element Plus组件 + 自定义Vue组件
- **Qt信号槽** → Vue事件系统 + Pinia状态管理
- **QWebEngine** → 原生Web应用，无需嵌入
- **Python后端** → FastAPI RESTful API + WebSocket

### 开发优势
- **热重载**: Vite提供极速开发体验
- **类型安全**: TypeScript确保代码质量
- **组件化**: Vue 3组件化开发，提高可维护性
- **响应式**: 原生响应式设计，支持多设备
- **部署灵活**: Web应用 + 可选Electron桌面端
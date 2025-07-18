# Claude Code 开发指令

## 项目概述
基于PyQt5 + QWebEngine架构的机器人用户识别界面开发

## 设计参考要求
**严格按照以下文件中的设计实现界面：**
1. `design_reference/ui_mockups/[具体UI文件名].html` - **主要UI参考**
2. `design_reference/style_guide.md` - **样式规格标准**  
3. `design_reference/component_specs.md` - **PyQt5实现映射**
4. `design_reference/color_mapping.md` - **配色映射指南**

⚠️ **特别注意**: **配色方案使用项目现有配色系统，不使用HTML中的颜色值**

### 当前支持的UI文件：
- `user_recognition_interface.html` - 用户识别界面
- 其他界面文件请按功能命名，如：`robot_control_panel.html`、`task_dashboard.html`等

## 开发约束条件
### 必须遵守的设计原则：
- ✅ **布局结构**: 严格按照HTML的左右分栏布局（1:3比例）
- ✅ **尺寸规格**: 精确复制HTML中的组件尺寸（高度、宽度、间距）
- ✅ **字体样式**: 保持字体大小、粗细的一致性（颜色使用项目配色）
- ✅ **圆角边框**: 复制所有圆角(rounded-lg)和边框样式
- ✅ **图标使用**: 相同位置使用相同风格的图标
- ✅ **组件层次**: 保持HTML中的信息层次和组织结构

### 配色要求：
- ❌ **禁止使用**HTML中的具体颜色值 (如#f9fafb, #111827等)
- ✅ **必须使用**项目现有的配色系统和主题
- ✅ **保持配色语义**：主背景、次背景、边框、文字、按钮等配色层次关系
- ✅ **自动适配**项目的明暗主题（如果有的话）

### 技术实现要求：
```python
# 主窗口固定尺寸
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# 左右面板比例
LEFT_PANEL_WIDTH = WINDOW_WIDTH // 3    # 400px
RIGHT_PANEL_WIDTH = WINDOW_WIDTH * 2 // 3  # 800px

# 配色系统集成（使用项目现有配色）
PROJECT_COLORS = {
    # 请从项目配色系统中获取以下配色
    'background_primary': '',    # 主背景色
    'background_secondary': '',  # 卡片/组件背景色  
    'border_light': '',         # 边框色
    'text_primary': '',         # 主文字色
    'text_secondary': '',       # 次要文字色
    'button_primary': '',       # 主按钮背景色
    'button_text': '',          # 按钮文字色
    'button_hover': '',         # 按钮悬停色
    'status_inactive': '',      # 状态指示器色
}
```

## 功能实现优先级
### Phase 1 - 基础布局 (必须完成)
- [ ] 主窗口框架搭建
- [ ] 左右面板布局实现 
- [ ] 相机显示区域占位
- [ ] 扫描按钮样式实现
- [ ] 用户信息卡片布局

### Phase 2 - 样式精确化 (严格要求)
- [ ] 所有组件的精确配色
- [ ] 字体大小和间距调整
- [ ] 圆角和边框效果
- [ ] 悬停状态样式

### Phase 3 - 交互功能
- [ ] 按钮点击事件
- [ ] 用户数据显示更新
- [ ] 任务历史滚动列表
- [ ] 状态指示器动态更新

## 开发禁止事项
❌ **不得随意修改**HTML设计中的：
- 布局比例和组件位置
- 组件尺寸和间距规格
- 字体大小和文本层次
- 圆角大小和边框样式
- 组件间距和内边距

❌ **不得使用**不同于HTML设计的：
- 其他UI框架的默认样式
- 不同的布局方式
- 不一致的组件层次结构

⚠️ **配色特殊要求**：
- ❌ 不得使用HTML中的具体颜色值
- ✅ 必须集成项目现有配色系统
- ✅ 保持配色的语义层次关系

## 验收标准
界面实现必须达到：
1. **布局一致性**: 与HTML设计文件的布局结构90%以上相似度
2. **配色协调性**: 完美集成项目现有配色，保持视觉协调
3. **功能完整性**: 所有HTML中展示的信息都能正确显示
4. **交互响应**: 按钮和状态更新能正常工作
5. **性能要求**: 界面响应流畅，无卡顿现象

## 如何使用Claude Code
当您需要Claude Code开发时，请：
1. 在项目根目录运行 `claude code`
2. **明确告诉Claude Code当前要开发的界面**：
   ```bash
   # 示例指令模板：
   "请严格按照design_reference/ui_mockups/[具体文件名].html的设计实现界面布局和结构，
   配色方案必须使用项目现有配色系统，不要使用HTML中的具体颜色值，
   保持HTML设计的所有布局、尺寸、间距等视觉规格。"
   
   # 具体示例：
   "请严格按照design_reference/ui_mockups/user_recognition_interface.html的设计实现界面..."
   "请严格按照design_reference/ui_mockups/robot_control_panel.html的设计实现界面..."
   ```
3. 强调: "除配色外，不得偏离HTML设计文件中的布局和样式"
4. 如有疑问，要求Claude Code先查看对应的设计参考文件再开始编码
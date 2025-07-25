# UI文件管理指南

## 文件组织结构

```
design_reference/ui_mockups/
├── smart_interface_chat.html           # ✅ 智能对话界面（对话式任务）
├── smart_interface_elivate.html        # ✅ 智能提升界面
├── smart_interface_face.html           # ✅ 人脸识别界面  
└── user_recognition_interface.html     # 用户识别界面（旧模板）
```

## 当前界面功能说明

### 已有界面分析：
1. **smart_interface_chat.html** - 对话式任务界面
   - 侧边栏导航（首页、对话、位置、设置）
   - 配置与连接区（移动端接入、系统状态）
   - 实时对话记录（用户与机器人对话）
   - 解析任务详情（任务监控、进度追踪）

2. **smart_interface_elivate.html** - 智能提升界面
   - 需要分析具体内容来更新文档

3. **smart_interface_face.html** - 人脸识别界面
   - 需要分析具体内容来更新文档

## 文件命名规范

### 推荐命名格式：
```
[功能模块]_[界面类型].html

示例：
- user_recognition_interface.html        # 用户_识别_界面
- robot_control_panel.html              # 机器人_控制_面板
- sensor_monitoring_dashboard.html       # 传感器_监控_仪表板
- arm_calibration_wizard.html           # 机械臂_校准_向导
- safety_emergency_panel.html           # 安全_紧急_面板
```

### 界面类型后缀建议：
- `_interface` - 综合性交互界面
- `_panel` - 控制面板类
- `_dashboard` - 仪表板/监控类  
- `_wizard` - 步骤向导类
- `_dialog` - 对话框类
- `_screen` - 全屏展示类

## 开发新界面的步骤

### 1. 添加新的UI设计文件
```bash
# 将新的HTML设计保存到mockups目录
cp your_new_design.html design_reference/ui_mockups/robot_control_panel.html
```

### 2. 使用Claude Code开发
```bash
claude code

# 然后使用具体文件名的指令：
"请严格按照design_reference/ui_mockups/robot_control_panel.html的设计实现界面布局和结构，
配色方案必须使用项目现有配色系统，保持HTML设计的所有布局、尺寸、间距等视觉规格。"
```

### 3. 验证开发结果
- [ ] 布局结构与HTML设计一致
- [ ] 配色使用项目现有配色系统
- [ ] 组件尺寸和间距准确复制
- [ ] 功能交互正常工作

## 多界面项目管理

### 当前界面文件映射：
| 文件名 | 界面功能 | 开发状态 | 备注 |
|--------|---------|---------|------|
| `smart_interface_chat.html` | 对话式任务界面 | ✅ 设计完成 | 侧边栏导航、实时对话、任务监控 |
| `smart_interface_elivate.html` | 智能提升界面 | ✅ 设计完成 | 待开发 |
| `smart_interface_face.html` | 人脸识别界面 | ✅ 设计完成 | 待开发 |
| `user_recognition_interface.html` | 用户识别界面 | ✅ 设计完成 | 旧版模板参考 |
| `...` | 其他界面 | - | 根据需要添加 |

### 管理建议
- **无需预定义所有界面**：只需要在实际开发时添加对应的HTML文件即可
- **保持命名一致性**：建议使用`[功能模块]_[界面类型].html`的命名格式
- **灵活扩展**：新界面直接加入ui_mockups目录，使用通用Claude Code指令开发

### 配置文件更新
每次添加新界面时，可选择性更新以下文件：
- `component_specs.md` - 如果有新的组件类型
- `color_mapping.md` - 如果有新的配色语义
- `style_guide.md` - 如果有新的尺寸规格

## 最佳实践建议

### ✅ 推荐做法：
1. **按功能命名UI文件**，便于管理和查找
2. **保留所有历史UI文件**，便于对比和复用
3. **每个界面使用独立的开发分支**
4. **及时更新界面开发状态**

### ❌ 避免做法：
1. 不要覆盖现有的UI文件
2. 不要使用过于简单的文件名（如ui1.html, ui2.html）
3. 不要混合不同功能的界面设计在同一文件中

## Claude Code指令模板

```bash
# 通用开发指令（适用于所有界面）：
"请严格按照design_reference/ui_mockups/[具体文件名].html的设计实现PyQt5界面：

核心要求：
- 完全复制HTML的布局结构和组件层次  
- 精确复制所有尺寸比例、间距、圆角、字体大小
- 保持HTML中的信息层次和组织结构
- 实现HTML中展示的所有交互功能

配色要求：
- 使用项目现有配色系统，不使用HTML中的具体颜色值
- 参考design_reference/color_mapping.md中的配色映射关系
- 保持配色的语义层次关系"

# 使用时只需替换[具体文件名]为实际的HTML文件名即可
```
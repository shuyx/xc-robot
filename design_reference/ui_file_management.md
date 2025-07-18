# UI文件管理指南

## 文件组织结构

```
design_reference/ui_mockups/
├── user_recognition_interface.html      # 用户识别界面
├── robot_control_panel.html            # 机器人控制面板  
├── task_management_dashboard.html       # 任务管理仪表板
├── system_settings_panel.html          # 系统设置面板
├── data_visualization_screen.html       # 数据可视化界面
└── emergency_control_interface.html     # 紧急控制界面
```

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
| `user_recognition_interface.html` | 用户识别界面 | ✅ 已完成 | 基础模板 |
| `robot_control_panel.html` | 机器人控制面板 | 🚧 开发中 | - |
| `task_management_dashboard.html` | 任务管理仪表板 | ⏳ 待开发 | - |

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
# 开发新界面的标准指令：
"请严格按照design_reference/ui_mockups/[具体文件名].html的设计实现界面布局和结构，
配色方案必须使用项目现有配色系统，不要使用HTML中的具体颜色值，
保持HTML设计的所有布局、尺寸、间距、圆角等视觉规格。
参考design_reference/color_mapping.md中的配色映射关系。"

# 替换[具体文件名]为实际的HTML文件名即可
```
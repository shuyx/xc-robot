# Claude Code 开发指令

## 项目概述
基于PyQt5 + QWebEngine架构的机器人用户识别界面开发

## 设计参考要求
**严格按照以下文件中的设计实现界面：**
1. `design_reference/ui_mockups/[具体UI文件名].html` - **主要UI参考**
2. `design_reference/style_guide.md` - **样式规格标准**  
3. `design_reference/component_specs.md` - **PyQt5实现映射**
4. `design_reference/ui_file_management.md` - **文件管理指南**

⚠️ **核心要求**: **严格按照HTML中的所有设计，包括布局、配色、尺寸等一切视觉规格**

### 当前支持的UI文件：
- `smart_interface_chat.html` - 智能对话界面
- `smart_interface_elivate.html` - 智能提升界面  
- `smart_interface_face.html` - 人脸识别界面
- `user_recognition_interface.html` - 用户识别界面（旧模板）

## 开发约束条件
### 必须遵守的设计原则：
- ✅ **布局结构**: 严格按照HTML的布局结构和组件层次
- ✅ **配色方案**: 严格使用HTML中的所有颜色值，不得修改任何配色
- ✅ **尺寸规格**: 精确复制HTML中的组件尺寸（高度、宽度、间距）
- ✅ **字体样式**: 保持字体大小、粗细、颜色的完全一致性
- ✅ **圆角边框**: 复制所有圆角、边框、阴影等视觉效果
- ✅ **图标使用**: 相同位置使用相同风格的图标
- ✅ **组件层次**: 保持HTML中的信息层次和组织结构

### 严格要求：
- ✅ **100%复制**HTML中的所有视觉设计
- ✅ **精确使用**HTML中的具体颜色值 (如#f3f4f6, #0ea5e9等)
- ✅ **完全保持**HTML的配色方案和视觉层次
- ✅ **不得修改**任何设计元素

### 技术实现要求：
```python
# 动态适配不同HTML设计的配色方案
def load_html_design_colors(html_file):
    """
    从指定的HTML文件中提取实际使用的颜色值
    支持不同的配色方案（蓝色、紫色、绿色等主题）
    """
    # 解析HTML和CSS，提取实际颜色值
    # 例如：
    # - 如果HTML使用primary-blue主题 → primary_color = '#0ea5e9'  
    # - 如果HTML使用primary-purple主题 → primary_color = '#8b5cf6'
    # - 如果HTML使用primary-green主题 → primary_color = '#10b981'
    
    return extracted_colors

# 使用示例：
colors = load_html_design_colors("design_reference/ui_mockups/smart_interface_chat.html")
# 或
colors = load_html_design_colors("design_reference/ui_mockups/purple_theme_interface.html")
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
- 配色方案和具体颜色值
- 组件尺寸和间距规格
- 字体大小和文本层次
- 圆角大小和边框样式
- 组件间距和内边距

❌ **不得使用**不同于HTML设计的：
- 其他配色方案或颜色值
- 其他UI框架的默认样式
- 不同的布局方式
- 不一致的组件层次结构

⚠️ **严格要求**：
- ✅ 必须使用HTML中的具体颜色值
- ✅ 必须保持HTML的完整视觉效果
- ✅ 禁止任何形式的设计修改或"优化"

## 验收标准
界面实现必须达到：
1. **视觉一致性**: 与HTML设计文件100%一致（包括配色）
2. **布局精确性**: 完美复制HTML的布局结构和组件层次
3. **配色准确性**: 严格使用HTML中的所有颜色值
4. **功能完整性**: 所有HTML中展示的信息都能正确显示
5. **交互响应**: 按钮和状态更新能正常工作
6. **性能要求**: 界面响应流畅，无卡顿现象

## 如何使用Claude Code
当您需要Claude Code开发时，请：
1. 在项目根目录运行 `claude code`
2. **使用以下通用指令模板**：
   ```bash
   "请分析并严格按照design_reference/ui_mockups/[具体文件名].html的设计实现PyQt5界面：

   第一步 - 分析HTML设计：
   - 仔细分析HTML文件中的布局结构、组件层次
   - 提取HTML中实际使用的所有颜色值（无论是什么配色主题）
   - 理解所有交互逻辑和状态变化

   第二步 - 实现要求：
   - 完全复制HTML的布局结构和组件层次
   - 精确复制所有尺寸比例、间距、圆角、字体大小
   - 严格使用HTML中的具体颜色值（动态适配不同配色主题）
   - 保持HTML中的信息层次和组织结构
   - 实现HTML中展示的所有交互功能

   第三步 - 技术实现：
   - 推荐使用QWebEngineView集成HTML + Python-JS通信桥梁
   - 或纯PyQt5组件，动态提取HTML颜色值后精确复制
   
   约束条件：不得偏离HTML设计的任何视觉规格，包括布局和配色"
   ```
3. **关键优势**: 这个指令适用于任何配色主题的HTML设计
4. **自动适配**: Claude Code会自动分析和提取每个HTML的具体配色方案

## 多界面开发流程
1. **添加新HTML设计** → 保存到`design_reference/ui_mockups/`目录
2. **使用通用指令** → 替换`[具体文件名].html`为实际文件名
3. **验证实现效果** → 确保布局一致性和配色协调性
4. **记录开发状态** → 可选择性更新`ui_file_management.md`中的进度表
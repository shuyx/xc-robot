  📋 专业Prompt：严格按照UI设计文档实现Vue3界面组件

  🎯 核心目标

  基于 @docs/design/ui_mockups/
  文件夹中的HTML设计文档，严格实现Vue3界面组件，确保100%视觉一致性和功能完整性。

  📁 设计文档体系理解

  - 来源: 基于 @xc_recon_uxpilot.md 使用UX Pilot专业设计
  - 总计: 9个功能模块，35个HTML设计文档
  - 技术栈: Tailwind CSS + Font Awesome 6.4.0 + Inter字体 + 统一配色系统
  - 特征: 企业级UI设计，完整响应式系统，专业交互逻辑

  🎨 技术规范标准

  配色系统严格遵循

  :root {
    --primary-color: #409EFF;
    --secondary-color: #2c3e50;
    --success-color: #00A870;
    --warning-color: #E6A23C;
    --danger-color: #F56C6C;
    --info-color: #909399;
  }

  组件实现标准

  1. Vue3 Composition API + TypeScript
  2. Element Plus UI库集成
  3. Font Awesome 6.4.0图标系统
  4. 响应式设计(桌面端+移动端)
  5. Mock数据框架集成

  🔧 实施流程规范

  第一步：设计文档深度分析

  1. 完整读取对应的HTML设计文档
  2. 分析页面结构、布局、交互逻辑
  3. 识别可复用组件和页面特定功能
  4. 理解业务逻辑和用户体验设计

  第二步：Vue3组件结构规划

  1. Template结构：严格按照HTML DOM结构
  2. Script逻辑：复现所有JavaScript交互功能
  3. Style样式：转换Tailwind CSS为Vue scoped样式
  4. 集成方案：与Layout系统和Mock数据集成

  第三步：完整功能实现

  1. 视觉效果：100%匹配原设计的视觉规格
  2. 交互逻辑：键盘快捷键、悬停效果、状态切换
  3. 数据集成：使用Mock数据框架提供真实数据
  4. 响应式：确保移动端和桌面端完美适配

  第四步：质量验证标准

  1. 设计一致性：每个像素都要与原设计匹配
  2. 功能完整性：所有交互和动效必须正常工作
  3. 代码质量：TypeScript类型安全，Vue3最佳实践
  4. 性能优化：组件加载性能和响应速度

  📊 当前项目状态

  已完成 (100%正确)

  - ✅ Layout系统: Header.vue、Sidebar.vue、MainLayout.vue 严格按照设计文档实现
  - ✅ Mock数据框架: 5个核心模块，完整业务数据支撑
  - ✅ 路由系统: 动态路由生成，占位符页面系统

  需要修正

  - ❌ QuickLaunch.vue: 完全自创，需按照 quickstart/main.html 重新实现
  - ⏳ 其他页面组件: 按照Todo顺序，严格参考对应HTML文档实现

  🎯 具体实施指令

  对于每个组件实现，请严格执行：

  1. 必须先阅读对应的HTML设计文档
  例如：实现快速启动页面时，必须先阅读
  @docs/design/ui_mockups/quickstart/main.html
  2. 完全按照HTML结构转换为Vue3
  <!-- 保持与HTML相同的DOM结构 -->
  <!-- 保持所有CSS类名和样式 -->
  <!-- 复现所有JavaScript交互逻辑 -->
  3. 集成项目技术栈
  // 使用Mock数据框架
  import { MockService } from '@/mock'

  // 使用Element Plus组件
  import { ElButton, ElMessage } from 'element-plus'

  // 严格类型定义
  interface PageData { ... }
  4. 确保100%功能完整性
  - 所有按钮点击事件
  - 所有悬停效果和状态切换
  - 所有键盘快捷键
  - 所有图表和数据展示
  - 所有响应式断点

  ⚠️ 严格禁止事项

  1. 禁止自创UI结构 - 必须严格按照HTML设计文档
  2. 禁止忽略交互逻辑 - 所有JavaScript功能必须实现
  3. 禁止改变视觉设计 - 保持与原设计100%一致
  4. 禁止跳过设计文档 - 每个组件都有对应的HTML参考

  🚀 质量检查清单

  完成每个组件后，必须验证：
  - 是否严格按照对应HTML设计文档实现？
  - 视觉效果是否与原设计100%匹配？
  - 所有交互功能是否正常工作？
  - 是否正确集成Mock数据？
  - 响应式设计是否完整？
  - TypeScript类型是否安全？
  - 是否遵循Vue3最佳实践？






----------------------------------------------


⏺ 🎯 如何使用这份Prompt

  这份prompt是一个工作指导规范，用于指导我（Claude）严格按照您的UI设计文档来实现Vue组件。以
  下是具体的使用方法：

  📋 使用方式

  方式1：直接指令使用

  您可以直接给我发送指令，例如：
  请按照刚才的专业prompt规范，严格参照 @docs/design/ui_mockups/quickstart/main.html 重新实现
   QuickLaunch.vue 组件

  方式2：引用prompt执行

  按照刚才记录的UI实现规范，继续完成当前的简单页面组件任务

  方式3：检查现有实现

  请用刚才的质量检查清单，验证当前的Header.vue组件是否符合标准

  🔧 实际应用场景

  场景1：修正错误实现

  当发现组件实现偏离设计文档时：
  发现QuickLaunch.vue没有按照设计文档实现，请按照prompt规范重新实现

  场景2：新组件开发

  开始实现新的页面组件时：
  现在开始实现设备连接页面，请按照prompt规范，参照对应的HTML设计文档

  场景3：质量验证

  检查已完成的组件质量：
  请按照prompt中的质量检查清单，验证刚完成的组件是否达标

  📊 prompt的核心价值

  这份prompt为我提供了：

  1. 明确的工作标准 - 100%按照HTML设计文档实现
  2. 技术规范指导 - Vue3 + TypeScript + Element Plus
  3. 质量检查标准 - 确保实现质量的具体清单
  4. 禁止事项清单 - 避免偏离设计文档的错误做法

  🚀 立即行动建议

  现在您可以说：
  好的，现在请按照这个专业prompt规范，重新实现QuickLaunch.vue组件，严格参照
  quickstart/main.html 设计文档

  或者：
  按照刚才的prompt规范，继续当前的Todo任务：实现简单页面组件

  这样我就会严格按照规范来执行，确保每个组件都是对应HTML设计文档的完美复现！
## 代码风格

- You MUST 遵守如下要求：
  - 请记住,你在代码开发时,力求代码简洁高效
  - 代码开发要求:请阅读 xc_os_context.md 文档，并关注### v2.9.2 - 仿真页面路由问题修复 (2025-07-18)描述的你经常会出现的错误，在开发过程中注意规避。代码简洁高效，不涉及的功能不需要考虑和开发
  - 请先理解任务要求，然后进行规划和子任务分解，然后再发给我进行确认，最后再开始执行

## 工作流程

- 探索 - 规划（不编码） -- 实现 -- 提交
- 提前规划请求显著提高成功率

## TDO强化版

- 让 claude 编写失败的测试，提交它们，然后迭代代码直到通过
- 用第二个 claude 从零开始审查实现

## 文件定位能力

- 使用@、@/寻找文件，引用上下文
- 使用 tab 补全文件名，节省上下文计算

## 使用Git Worktrees并行开发

- 生成多个 worktrees，每个终端一个 claude，在单独的分支上
- 没有合并冲突

## 项目介绍

YOU MUST 记住这些内容

- xc_os_context.md，为项目的基本情况介绍
- start_web_gui.py，为当前 webgui 的启动文件

## 使用 zen mcp

- 我可以在 claude 里面，直接输入：使用 zen，调用 gemini pro 或者 gemini flash进行xxx 任务

## 提示词

请阅读项目根目录 CLAUDE_CODE_INSTRUCTIONS.md文档。请阅读 design_reference 文件夹内的 component_specs.md 和 style_guide.md 的内容。然后，请严格按照design_reference文件夹下 ui_mockups文件夹中的 smart_interface_chat.html设计实现界面布局，但配色必须使用项目现有配色系统。参考color_mapping.md中的配色映射关系，保持HTML设计的所有布局、尺寸、间距、圆角等视觉规格，只替换配色方案。


##  常用的深度思考提示词

  - think harder - 要求更深入思考
  - think step by step - 要求逐步分析
  - think carefully - 要求仔细思考
  - analyze deeply - 要求深度分析
  - 考虑所有可能性 - 全面思考
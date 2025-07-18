## 局部上下文管理

- @，调用文件
- @/，调用文件夹
- claude可以使用，think，think hard，think harder，ultrathink，解锁更大的思考深度
- Escape，可以中断，而不丢失上下文
- /clear，用这个可以清理上下文
- claude --dangerously-skip-permissions，这是无人值守的 mode，无视任何权限即可使用，谨慎使用

## 为复杂流程使用清单和草稿

- 多写 md，文档，记录 log 等

## UI设计的使用方式

请阅读项目根目录 CLAUDE_CODE_INSTRUCTIONS.md文档。请阅读 design_reference 文件夹内的 component_specs.md 和 style_guide.md 的内容。然后，请严格按照design_reference文件夹下 ui_mockups文件夹中的smart_interface_face.html设计实现界面布局，但配色必须使用项目现有配色系统。参考color_mapping.md中的配色映射关系，保持HTML设计的所有布局、尺寸、间距、圆角等视觉规格，只替换配色方案。

文件放在：

design_reference/ui_mockups/文件夹里

## 多claude 工作流

- gemini cli，用来规划
- 一个 claude 用来开发，一个 claude 用来 review，阅读代码和审查反馈
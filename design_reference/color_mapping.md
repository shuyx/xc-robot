# 配色映射指南

## HTML配色到项目配色的映射关系

### 配色语义映射表

| HTML原始配色 | 语义用途 | 项目配色变量 | 说明 |
|-------------|---------|-------------|------|
| `#f9fafb` (neutral-50) | 主面板背景 | `PROJECT_COLORS['panel_bg']` | 左侧面板背景色 |
| `#ffffff` (white) | 卡片背景 | `PROJECT_COLORS['card_bg']` | 用户信息卡片、任务卡片背景 |
| `#e5e7eb` (neutral-200) | 边框颜色 | `PROJECT_COLORS['border_light']` | 卡片边框、分割线 |
| `#111827` (neutral-900) | 主按钮背景 | `PROJECT_COLORS['button_primary']` | 扫描按钮背景色 |
| `#1f2937` (neutral-800) | 按钮悬停 | `PROJECT_COLORS['button_hover']` | 按钮悬停状态 |
| `#4b5563` (neutral-600) | 相机背景 | `PROJECT_COLORS['camera_bg']` | 相机显示区域背景 |
| `#111827` (neutral-900) | 主文字 | `PROJECT_COLORS['text_primary']` | 标题、用户名等主要文字 |
| `#6b7280` (neutral-500) | 次要文字 | `PROJECT_COLORS['text_secondary']` | 描述、时间戳等次要文字 |
| `#374151` (neutral-700) | 小标题 | `PROJECT_COLORS['text_subtitle']` | 区块小标题 |
| `white` | 按钮文字 | `PROJECT_COLORS['button_text']` | 按钮内文字颜色 |
| `#6b7280` (neutral-500) | 状态指示器 | `PROJECT_COLORS['status_inactive']` | 待命状态圆点 |

## PyQt5样式表模板

```python
def get_project_colors():
    """
    返回项目配色字典，需要根据实际项目配色系统填充
    """
    return {
        # 背景色系
        'panel_bg': '#{YOUR_PANEL_BG_COLOR}',        # 替换neutral-50
        'card_bg': '#{YOUR_CARD_BG_COLOR}',          # 替换white
        'camera_bg': '#{YOUR_CAMERA_BG_COLOR}',      # 替换neutral-600
        
        # 边框色系  
        'border_light': '#{YOUR_BORDER_COLOR}',      # 替换neutral-200
        
        # 按钮色系
        'button_primary': '#{YOUR_BTN_PRIMARY}',     # 替换neutral-900
        'button_hover': '#{YOUR_BTN_HOVER}',         # 替换neutral-800
        'button_text': '#{YOUR_BTN_TEXT}',           # 替换white
        
        # 文字色系
        'text_primary': '#{YOUR_TEXT_PRIMARY}',      # 替换neutral-900
        'text_secondary': '#{YOUR_TEXT_SECONDARY}',  # 替换neutral-500
        'text_subtitle': '#{YOUR_TEXT_SUBTITLE}',    # 替换neutral-700
        
        # 状态色系
        'status_inactive': '#{YOUR_STATUS_COLOR}',   # 替换neutral-500
    }

def apply_project_styling(widget_class, colors):
    """
    应用项目配色的样式表生成器
    """
    if widget_class == 'LeftPanel':
        return f"""
            QWidget {{
                background-color: {colors['panel_bg']};
                border-right: 1px solid {colors['border_light']};
            }}
        """
    
    elif widget_class == 'UserCard':
        return f"""
            QFrame {{
                background-color: {colors['card_bg']};
                border: 1px solid {colors['border_light']};
                border-radius: 8px;
            }}
        """
    
    elif widget_class == 'ScanButton':
        return f"""
            QPushButton {{
                background-color: {colors['button_primary']};
                color: {colors['button_text']};
                border-radius: 8px;
                padding: 12px 16px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
            }}
        """
    
    # 更多组件样式...
```

## 实际使用示例

```python
# 1. 获取项目配色
project_colors = get_project_colors()

# 2. 应用到具体组件
class CameraWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 256)
        style = f"""
            QLabel {{
                background-color: {project_colors['camera_bg']};
                border-radius: 8px;
                color: {project_colors['button_text']};
                text-align: center;
            }}
        """
        self.setStyleSheet(style)

class UserInfoCard(QFrame):
    def __init__(self):
        super().__init__()
        style = f"""
            QFrame {{
                background-color: {project_colors['card_bg']};
                border: 1px solid {project_colors['border_light']};
                border-radius: 8px;
                padding: 24px;
            }}
        """
        self.setStyleSheet(style)
```

## 配色适配检查清单

在实现时，请确保：
- [ ] 不直接使用HTML中的hex颜色值
- [ ] 所有颜色都从项目配色系统获取
- [ ] 保持配色的语义层次关系
- [ ] 支持项目的主题切换（如有）
- [ ] 确保颜色对比度满足可读性要求

## Claude Code指令模板

```bash
# 在Claude Code中使用以下指令：
"请按照design_reference/ui_mockups/user_recognition_interface.html的布局实现界面，
但配色必须使用项目现有配色系统。参考design_reference/color_mapping.md中的
配色映射关系，将HTML中的neutral色系映射到项目配色。保持所有布局、尺寸、
间距、圆角等视觉规格不变。"
```
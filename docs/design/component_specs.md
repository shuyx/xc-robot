# PyQt5 组件实现规格

## 主窗口结构（基于smart_interface系列）
```python
class SmartInterfaceMainWindow(QMainWindow):
    def __init__(self):
        # 主窗口尺寸: 全屏自适应或固定尺寸
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("智能机器人交互系统")
        
class ChatInterface(QMainWindow):  # smart_interface_chat.html
    def __init__(self):
        # 对话式任务界面
        self.setWindowTitle("对话式任务 - 监控与配置")

class ElivateInterface(QMainWindow):  # smart_interface_elivate.html  
    def __init__(self):
        # 智能提升界面
        pass

class FaceInterface(QMainWindow):  # smart_interface_face.html
    def __init__(self):
        # 人脸识别界面
        pass
```

## HTML集成方案
```python
# 推荐方案: QWebEngineView集成HTML (最佳选择)
class SmartWebInterface(QWidget):
    def __init__(self, html_file):
        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = PythonJSBridge()  # Python-JS通信桥梁
        
        # 加载对应的HTML文件
        html_path = f"design_reference/ui_mockups/{html_file}"
        self.web_view.load(QUrl.fromLocalFile(html_path))

# 方案2: 纯PyQt5控件复制HTML布局 (复杂但控制精确)
class SidebarWidget(QWidget):      # 对应HTML的sidebar
class HeaderWidget(QWidget):       # 对应HTML的header  
class MainContentWidget(QWidget):  # 对应HTML的main-content
class ChatHistoryWidget(QWidget):  # 对应HTML的chat-history
class TaskDetailsWidget(QWidget):  # 对应HTML的task-details
```

## 关键组件映射

### 1. 侧边栏组件
```python
# HTML: <div class="fixed left-0 top-0 bottom-0 w-16 bg-white border-r border-gray-200">
class SidebarWidget(QWidget):
    def __init__(self):
        self.setFixedWidth(64)  # w-16 = 64px
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;      /* 严格使用HTML中的white */
                border-right: 1px solid #e5e7eb;  /* 严格使用HTML中的gray-200 */
            }
        """)
```

### 2. 主按钮
```python
# HTML: <button class="bg-primary-50 hover:bg-primary-100 text-primary-700">
class PrimaryButton(QPushButton):
    def __init__(self):
        self.setText("🔍 生成二维码")
        self.setStyleSheet("""
            QPushButton {
                background-color: #e0f2fe;      /* 严格使用HTML中的primary-50 */
                color: #0369a1;                 /* 严格使用HTML中的primary-700 */
                border: 1px solid #bae6fd;      /* 严格使用HTML中的primary-200 */
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f0f9ff;      /* 严格使用HTML中的primary-100 */
            }
        """)
```

### 3. 状态指示器
```python
# HTML: <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse">
class StatusIndicator(QLabel):
    def __init__(self):
        self.setFixedSize(8, 8)  # w-2 h-2 = 8px
        self.setStyleSheet("""
            QLabel {
                background-color: #10b981;      /* 严格使用HTML中的green-500 */
                border-radius: 4px;             /* rounded-full */
            }
        """)
        # 添加脉动动画效果
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.3)
        self.animation.setLoopCount(-1)
        self.animation.start()
```
```

### 3. 用户信息卡片
```python
# HTML: <div class="bg-white border border-neutral-200 rounded-lg p-6">
class UserInfoCard(QFrame):
    def __init__(self):
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;  /* border-neutral-200 */
                border-radius: 8px;         /* rounded-lg */
                padding: 24px;              /* p-6 */
            }
        """)
        
        # 用户头像
        self.avatar = QLabel()
        self.avatar.setFixedSize(64, 64)  # w-16 h-16
        self.avatar.setStyleSheet("border-radius: 32px;")  # rounded-full
        
        # 用户名
        self.username = QLabel("Kevin Yuan")
        self.username.setStyleSheet("""
            font-size: 20px;           /* text-xl */
            color: #111827;            /* text-neutral-900 */
            font-weight: 600;
        """)
```

### 4. 任务历史列表
```python
# HTML: <div class="space-y-3 max-h-64 overflow-y-auto">
class TaskHistoryList(QScrollArea):
    def __init__(self):
        self.setMaximumHeight(256)  # max-h-64
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background-color: #f3f4f6;
                border-radius: 3px;
            }
        """)

class TaskItem(QWidget):
    def __init__(self, timestamp, status, description):
        # HTML: <div class="border-l-4 border-neutral-500 pl-4 py-2">
        self.setStyleSheet("""
            QWidget {
                border-left: 4px solid #6b7280;  /* border-l-4 border-neutral-500 */
                padding-left: 16px;              /* pl-4 */
                padding-top: 8px;                /* py-2 */
                padding-bottom: 8px;
                margin-bottom: 12px;             /* space-y-3 */
            }
        """)
```

## 样式表全局配置
```python
# 通用方法：从HTML文件中动态提取颜色值
def extract_colors_from_html(html_file_path):
    """
    从HTML文件中提取所有使用的颜色值
    根据具体HTML设计动态生成配色字典
    """
    # 示例：解析HTML和CSS，提取实际使用的颜色
    colors = {}
    
    # 根据HTML内容动态填充，例如：
    # 如果HTML使用 bg-blue-500，则 colors['primary'] = '#3b82f6'
    # 如果HTML使用 bg-purple-500，则 colors['primary'] = '#8b5cf6'
    # 如果HTML使用 bg-green-500，则 colors['primary'] = '#10b981'
    
    return colors

# 使用方法：
html_colors = extract_colors_from_html("design_reference/ui_mockups/your_interface.html")

# 通用配色模板（根据HTML实际内容调整）
GLOBAL_STYLESHEET = f"""
    QMainWindow {{
        background-color: {html_colors.get('app_background', '#ffffff')};
        font-family: 'Inter', 'Microsoft YaHei', sans-serif;
    }}
"""
```

## 通用组件实现模板
```python
class UniversalButton(QPushButton):
    def __init__(self, html_colors, button_type="primary"):
        super().__init__()
        
        # 根据HTML设计动态设置样式
        if button_type == "primary":
            bg_color = html_colors.get('primary_bg', '#0ea5e9')
            text_color = html_colors.get('primary_text', '#ffffff') 
            hover_color = html_colors.get('primary_hover', '#0284c7')
        elif button_type == "secondary":
            bg_color = html_colors.get('secondary_bg', '#f3f4f6')
            text_color = html_colors.get('secondary_text', '#374151')
            hover_color = html_colors.get('secondary_hover', '#e5e7eb')
            
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 6px;
                padding: 8px 16px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

class UniversalCard(QFrame):
    def __init__(self, html_colors):
        super().__init__()
        
        # 根据HTML设计动态设置卡片样式
        card_bg = html_colors.get('card_background', '#ffffff')
        border_color = html_colors.get('border_light', '#e5e7eb')
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {card_bg};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
```

## JavaScript-Python通信接口
```python
class PythonJSBridge(QObject):
    # 信号定义
    user_scanned = pyqtSignal(dict)  # 用户扫描结果
    status_changed = pyqtSignal(str)  # 状态更新
    
    @pyqtSlot()
    def scan_user(self):
        """对应HTML按钮的点击事件"""
        # 执行用户扫描逻辑
        user_data = self.camera_manager.scan_user()
        self.user_scanned.emit(user_data)
    
    @pyqtSlot(str)
    def update_status(self, status):
        """更新系统状态"""
        self.status_changed.emit(status)
```

## 实现优先级
1. **高优先级**: 保持HTML的视觉布局和配色方案
2. **中优先级**: 实现相同的交互逻辑和状态管理
3. **低优先级**: 完全一致的动画效果和细节
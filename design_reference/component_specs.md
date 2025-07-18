# PyQt5 组件实现规格

## 主窗口结构
```python
class UserRecognitionInterface(QMainWindow):
    def __init__(self):
        # 主窗口尺寸: 1200x800
        self.setFixedSize(1200, 800)
        self.setWindowTitle("机器人用户识别系统")
```

## HTML集成方案
```python
# 方案1: 纯PyQt5控件复制HTML布局
class LeftPanel(QWidget):  # 对应HTML的left-panel
    def __init__(self):
        self.camera_widget = CameraWidget()      # 相机显示区域
        self.scan_button = QPushButton("扫描并识别用户")  # 扫描按钮
        self.status_widget = StatusWidget()     # 状态指示器

class RightPanel(QWidget):  # 对应HTML的right-panel
    def __init__(self):
        self.user_card = UserInfoCard()         # 用户信息卡片
        self.history_card = TaskHistoryCard()   # 任务历史卡片

# 方案2: QWebEngineView集成HTML (推荐)
class WebInterface(QWidget):
    def __init__(self):
        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = PythonJSBridge()  # Python-JS通信桥梁
```

## 关键组件映射

### 1. 相机显示区域
```python
# HTML: <div class="bg-neutral-600 rounded-lg h-64">
class CameraWidget(QLabel):
    def __init__(self):
        self.setFixedSize(300, 256)  # h-64 = 256px
        self.setStyleSheet("""
            QLabel {
                background-color: {camera_bg_color};  /* 使用项目配色替代neutral-600 */
                border-radius: 8px;                   /* rounded-lg */
                color: {camera_text_color};           /* 使用项目文字配色 */
                text-align: center;
            }
        """.format(
            camera_bg_color=PROJECT_COLORS['camera_background'],
            camera_text_color=PROJECT_COLORS['camera_text']
        ))
```

### 2. 扫描按钮
```python
# HTML: <button class="w-full bg-neutral-900 text-white py-3 px-4 rounded-lg">
class ScanButton(QPushButton):
    def __init__(self):
        self.setText("🔍 扫描并识别用户")  # fa-scan-face图标用emoji替代
        self.setStyleSheet("""
            QPushButton {
                background-color: {btn_primary};     /* 使用项目主按钮色 */
                color: {btn_text};                   /* 使用项目按钮文字色 */
                padding: 12px 16px;                  /* py-3 px-4 */
                border-radius: 8px;                  /* rounded-lg */
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: {btn_hover};       /* 使用项目按钮悬停色 */
            }
        """.format(
            btn_primary=PROJECT_COLORS['button_primary'],
            btn_text=PROJECT_COLORS['button_text'],
            btn_hover=PROJECT_COLORS['button_hover']
        ))
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
# ⚠️ 配色方案使用项目现有配色系统，以下仅为结构参考
GLOBAL_STYLESHEET = """
    QMainWindow {
        background-color: {background_primary};  /* 使用项目主背景色 */
        font-family: 'Microsoft YaHei', sans-serif;
    }
    
    /* 配色映射 - 请替换为项目实际配色 */
    .bg-primary { background-color: {background_primary}; }
    .bg-secondary { background-color: {background_secondary}; }
    .border-light { border-color: {border_light}; }
    .text-primary { color: {text_primary}; }
    .text-secondary { color: {text_secondary}; }
    .btn-primary { background-color: {button_primary}; }
    .btn-hover { background-color: {button_hover}; }
"""

# 配色变量需要从项目配色系统中获取
def get_project_colors():
    """获取项目现有配色方案"""
    return {
        'background_primary': '#{项目主背景色}',
        'background_secondary': '#{项目次背景色}',
        'border_light': '#{项目浅边框色}',
        'text_primary': '#{项目主文字色}',
        'text_secondary': '#{项目次文字色}',
        'button_primary': '#{项目主按钮色}',
        'button_hover': '#{项目按钮悬停色}',
    }
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
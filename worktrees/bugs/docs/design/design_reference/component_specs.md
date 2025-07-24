# Vue 3 + TypeScript 组件实现规格

## 重构技术栈架构（基于smart_interface系列）
```typescript
// 主应用结构 - Vue 3 + Element Plus
// 前端: Vue 3 + TypeScript + Element Plus + Vite
// 后端: FastAPI + Python 3.9+
// 部署: Web应用 + Electron桌面端（可选）

interface SmartInterfaceConfig {
  framework: 'Vue 3 + TypeScript'
  uiLibrary: 'Element Plus'
  buildTool: 'Vite'
  stateManagement: 'Pinia'
  backend: 'FastAPI'
}

// 主要界面组件
interface ChatInterface {  // smart_interface_chat.html → Vue组件
  component: 'ConversationalTaskPage.vue'
  features: ['real-time-chat', 'task-monitoring', 'qr-generation']
}

interface ElevateInterface {  // smart_interface_elivate.html → Vue组件
  component: 'ElevatorControlPage.vue'  
  features: ['elevator-control', 'floor-selection', 'status-monitoring']
}

interface FaceInterface {  // smart_interface_face.html → Vue组件
  component: 'FaceRecognitionPage.vue'
  features: ['face-scanning', 'user-identification', 'permission-management']
}
```

## Vue 3组件实现方案
```typescript
// 推荐方案: Vue 3组件 + Element Plus UI库
// 基于HTML mockup设计实现对应的Vue组件

// 主布局组件
interface LayoutComponents {
  AppLayout: 'components/layout/AppLayout.vue'     // 应用主框架
  Sidebar: 'components/layout/Sidebar.vue'        // 侧边栏导航
  Header: 'components/layout/Header.vue'          // 头部区域
  MainContent: 'components/layout/MainContent.vue' // 主内容区
}

// 功能页面组件
interface PageComponents {
  ConversationalTask: 'pages/ConversationalTaskPage.vue'  // 对话式任务
  FaceRecognition: 'pages/FaceRecognitionPage.vue'       // 人脸识别
  ElevatorControl: 'pages/ElevatorControlPage.vue'       // 梯控系统
}

// 通用UI组件
interface UIComponents {
  ChatHistory: 'components/ui/ChatHistory.vue'      // 聊天记录
  TaskDetails: 'components/ui/TaskDetails.vue'      // 任务详情
  StatusIndicator: 'components/ui/StatusIndicator.vue' // 状态指示器
  UserInfoCard: 'components/ui/UserInfoCard.vue'    // 用户信息卡片
  QRCodeGenerator: 'components/ui/QRCodeGenerator.vue' // 二维码生成
}
```

## 关键组件映射

### 1. 侧边栏组件 (Sidebar.vue)
```vue
<!-- HTML模板设计: <div class="fixed left-0 top-0 bottom-0 w-16 bg-white border-r border-gray-200"> -->
<template>
  <el-aside 
    width="64px" 
    class="sidebar-container"
    :style="sidebarStyles"
  >
    <nav class="sidebar-nav">
      <div class="logo-section">
        <el-avatar 
          :size="40" 
          :style="{ backgroundColor: primaryColor }"
          icon="Robot"
        />
      </div>
      
      <div class="nav-items">
        <el-button
          v-for="item in navItems"
          :key="item.path"
          :icon="item.icon"
          circle
          :type="isActive(item.path) ? 'primary' : 'default'"
          @click="navigateTo(item.path)"
          class="nav-button"
        />
      </div>
    </nav>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'

// 从HTML设计中提取的颜色值
const sidebarStyles = computed(() => ({
  backgroundColor: '#ffffff',        // 严格使用HTML中的white
  borderRight: '1px solid #e5e7eb', // 严格使用HTML中的gray-200
  position: 'fixed',
  left: 0,
  top: 0,
  bottom: 0,
  width: '64px'                      // w-16 = 64px
}))
</script>
```

### 2. 主按钮组件 (PrimaryButton.vue)
```vue
<!-- HTML模板设计: <button class="bg-primary-50 hover:bg-primary-100 text-primary-700"> -->
<template>
  <el-button
    :type="buttonType"
    :size="size"
    :icon="icon"
    :loading="loading"
    :disabled="disabled"
    @click="handleClick"
    :style="buttonStyles"
    class="primary-button"
  >
    <slot>{{ text }}</slot>
  </el-button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  icon?: string
  size?: 'large' | 'default' | 'small'
  loading?: boolean
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

const props = withDefaults(defineProps<Props>(), {
  text: '🔍 生成二维码',
  size: 'default',
  variant: 'primary'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 从HTML设计中严格提取的样式
const buttonStyles = computed(() => {
  const baseStyles = {
    borderRadius: '6px',
    padding: '8px 16px',
    fontWeight: '500',
    transition: 'all 0.3s ease'
  }
  
  if (props.variant === 'primary') {
    return {
      ...baseStyles,
      backgroundColor: '#e0f2fe',    // HTML中的primary-50
      color: '#0369a1',             // HTML中的primary-700
      border: '1px solid #bae6fd'   // HTML中的primary-200
    }
  }
  
  return baseStyles
})

const buttonType = computed(() => {
  return props.variant === 'primary' ? 'primary' : 'default'
})

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style scoped>
.primary-button:hover {
  background-color: #f0f9ff !important;  /* HTML中的primary-100 */
}
</style>
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
# XC-RECON Kevin 开发执行指南

**项目负责人**: Kevin Yuan  
**创建日期**: 2025-07-19  
**更新状态**: UI优先策略执行方案  
**当前阶段**: Phase 0 - UI优先开发  

---

## 🎯 开发策略总览

基于Q&A、system和steps文档深度分析，确定采用**UI优先策略**：

### 📋 核心策略
1. **UI先行** → Mock数据驱动 → API集成 → 硬件连接
2. **Mac开发**(仿真) → **Win测试**(真实硬件)
3. **前端独立开发** → 避免硬件依赖阻塞
4. **设计验证优先** → 建立数据需求标准

### 🔄 工作流程参考
**简化版流程**:
1. **UX Pilot设计** (配色约束) → 导出HTML → 放入ui_mockups/
2. **Vue 3组件实现** → Mock数据驱动 → 测试集成 → 部署
3. **后端API对接** → 真实硬件连接 → Win环境验证

### 📖 关键决策依据
- **Q&A分析**: UI优先策略基于Mac/Win跨平台约束和Mock数据可行性
- **系统分析**: 从14307行HTML巨无霸重构为微服务架构
- **步骤分析**: Phase 0新增，UI优先验证设计可行性后再进行后端集成

---

## 📋 任务分解与操作指南

### 🎯 总体任务规划
基于文档分析，将开发任务分解为5个主要阶段：

| 任务 | 优先级 | 预估时间 | 依赖关系 | Kevin操作要点 |
|------|--------|----------|----------|---------------|
| 1. Vue3菜单框架 | P0-最高 | 1-2天 | 无 | 基于xc_recon_oldgui.md实现9分组菜单 |
| 2. 智能交互模块 | P0-最高 | 2-3天 | 任务1 | 参考smart_interface_*.html设计 |
| 3. Mock数据框架 | P1-重要 | 1-2天 | 任务1,2 | 为UI提供完整仿真数据支撑 |
| 4. 后端API集成 | P2-中等 | 1-2周 | 任务3 | 替换Mock为真实硬件连接 |
| 5. 硬件连接测试 | P3-低 | 3-5天 | 任务4 | Win环境真实设备验证 |

### 🔄 Kevin执行工作流
每个任务的标准执行流程：

**阶段1: 准备阶段**
```bash
# 检查环境和依赖
cd /Users/shushu/xc-robot/xc-recon-v2/frontend/xc-recon-frontend
npm run dev  # 验证前端环境
git status   # 检查当前状态
```

**阶段2: 开发阶段**
- 创建必要的目录和文件
- 实现核心功能组件
- 使用Mock数据进行本地测试

**阶段3: 验证阶段**  
```bash
npm run dev  # 启动开发服务器
# 浏览器访问 http://localhost:3000
# 验证功能正常运行
```

**阶段4: 提交阶段**
```bash
git add .
git commit -m "feat: 完成[任务名称] - Author: kevin yuan"
git push
```

---

## 🚀 Phase 0: UI优先开发 (立即执行)

### 任务 1: Vue3导航菜单框架建立
**优先级**: 🔥 最高  
**预估时间**: 1-2天  
**参考文档**: `xc_recon_oldgui.md`

#### Kevin的具体操作步骤：

**1.1 检查前端环境**
```bash
cd /Users/shushu/xc-robot/xc-recon-v2/frontend/xc-recon-frontend

# 检查当前Vue3项目状态
npm run dev

# 验证当前依赖
ls src/
cat package.json
```

**1.2 创建菜单配置文件**
```bash
# 创建菜单配置目录
mkdir -p src/config
touch src/config/menu.ts
```

**1.3 实现9分组菜单结构**
```typescript
// src/config/menu.ts
export const menuConfig = [
  {
    id: 'quickstart',
    icon: '⚡',
    title: '快速启动',
    path: '/quickstart',
    children: [
      { id: 'favorites', icon: '⭐', title: '收藏夹', path: '/quickstart/favorites' },
      { id: 'recent', icon: '📜', title: '最近使用', path: '/quickstart/recent' }
    ]
  },
  {
    id: 'device',
    icon: '📡',
    title: '设备连接',
    path: '/device',
    children: [
      { id: 'connection-test', icon: '🔗', title: '连接测试', path: '/device/connection' },
      { id: 'network-config', icon: '🌐', title: '网络配置', path: '/device/network' }
    ]
  },
  {
    id: 'control',
    icon: '🤖',
    title: '机器人控制',
    path: '/control',
    children: [
      { id: 'arm-control', icon: '🦾', title: '机械臂控制', path: '/control/arm' },
      { id: 'chassis-control', icon: '🚛', title: '底盘控制', path: '/control/chassis' },
      { id: 'coord-control', icon: '🔄', title: '联动控制', path: '/control/coord' }
    ]
  },
  {
    id: 'testing',
    icon: '🧪',
    title: '场景测试',
    path: '/testing',
    children: [
      { id: 'component-testing', icon: '🔧', title: '组件测试', path: '/testing/component' },
      { id: 'integration-testing', icon: '🔗', title: '集成测试', path: '/testing/integration' },
      { id: 'vision-testing', icon: '👁️', title: '视觉引导测试', path: '/testing/vision' },
      { id: 'e2e-testing', icon: '🎯', title: '端到端场景', path: '/testing/e2e' }
    ]
  },
  {
    id: 'simulation',
    icon: '🎯',
    title: '仿真规划',
    path: '/simulation',
    children: [
      { id: 'robot-sim', icon: '🎮', title: '仿真模拟', path: '/simulation/robot' },
      { id: 'path-planning', icon: '🏗️', title: '路径规划', path: '/simulation/path' },
      { id: 'task-orchestration', icon: '📋', title: '任务编排', path: '/simulation/task' }
    ]
  },
  {
    id: 'vision',
    icon: '👁️',
    title: '视觉感知',
    path: '/vision',
    children: [
      { id: 'vision-system', icon: '📷', title: '视觉系统', path: '/vision/system' },
      { id: 'camera-calibration', icon: '🎯', title: '相机标定', path: '/vision/calibration' },
      { id: 'pointcloud', icon: '☁️', title: '点云处理', path: '/vision/pointcloud' },
      { id: 'image-processing', icon: '🔍', title: '图像处理', path: '/vision/image' }
    ]
  },
  {
    id: 'interaction',
    icon: '🤝',
    title: '智能交互', // 重点模块
    path: '/interaction',
    children: [
      { id: 'face-recognition', icon: '👤', title: '人脸识别', path: '/interaction/face' },
      { id: 'conversational-task', icon: '🎤', title: '智能交互', path: '/interaction/chat' },
      { id: 'elevator-control', icon: '🏢', title: '梯控系统', path: '/interaction/elevator' }
    ]
  },
  {
    id: 'monitoring',
    icon: '📊',
    title: '数据监控',
    path: '/monitoring',
    children: [
      { id: 'system-monitor', icon: '📈', title: '系统监控', path: '/monitoring/system' },
      { id: 'data-analytics', icon: '📋', title: '数据分析', path: '/monitoring/analytics' },
      { id: 'performance-stats', icon: '📊', title: '性能统计', path: '/monitoring/performance' }
    ]
  },
  {
    id: 'management',
    icon: '⚙️',
    title: '系统管理',
    path: '/management',
    children: [
      { id: 'parameter-config', icon: '🔧', title: '参数配置', path: '/management/config' },
      { id: 'maintenance', icon: '🛠️', title: '维护管理', path: '/management/maintenance' },
      { id: 'system-settings', icon: '⚙️', title: '系统设置', path: '/management/settings' }
    ]
  }
]
```

**1.4 更新路由配置**
```bash
# 编辑路由文件
vim src/router/index.ts
```

**1.5 创建侧边栏菜单组件**
```bash
# 更新侧边栏组件
vim src/components/layout/Sidebar.vue
```

---

### 任务 2: 智能交互模块优先实现
**优先级**: 🔥 最高  
**预估时间**: 2-3天  
**参考文档**: `docs/design/ui_mockups/smart_interface_*.html`

#### Kevin的具体操作步骤：

**2.1 创建智能交互页面目录**
```bash
mkdir -p src/views/interaction
touch src/views/interaction/FaceRecognitionPage.vue
touch src/views/interaction/ConversationalTaskPage.vue
touch src/views/interaction/ElevatorControlPage.vue
```

**2.2 分析现有HTML设计**
```bash
# 读取现有设计文件，理解布局和功能
cat docs/design/ui_mockups/smart_interface_face.html
cat docs/design/ui_mockups/smart_interface_chat.html
cat docs/design/ui_mockups/smart_interface_elivate.html
```

**2.3 实现人脸识别页面**
```typescript
// src/views/interaction/FaceRecognitionPage.vue
<template>
  <div class="face-recognition-page">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>👤 人脸识别系统</span>
          <el-button type="primary" @click="startRecognition">开始识别</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="camera-preview">
            <div class="video-container">
              <video ref="videoRef" autoplay muted></video>
              <canvas ref="canvasRef" class="detection-overlay"></canvas>
            </div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="recognition-results">
            <h3>识别结果</h3>
            <el-table :data="recognitionResults" style="width: 100%">
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="confidence" label="置信度" />
              <el-table-column prop="timestamp" label="时间" />
            </el-table>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Mock数据
const recognitionResults = ref([
  { name: 'Kevin Yuan', confidence: '95%', timestamp: '2025-07-19 14:30:00' },
  { name: '未知人员', confidence: '65%', timestamp: '2025-07-19 14:25:00' }
])

const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()

const startRecognition = () => {
  // Mock功能 - 实际会调用后端API
  console.log('开始人脸识别...')
}

onMounted(() => {
  // Mock摄像头初始化
  console.log('摄像头组件已加载')
})
</script>
```

**2.4 实现智能对话页面**
```typescript
// src/views/interaction/ConversationalTaskPage.vue
<template>
  <div class="conversational-task-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="chat-area">
          <div class="chat-messages" ref="chatContainer">
            <div v-for="message in messages" :key="message.id" 
                 :class="['message', message.type]">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">{{ message.timestamp }}</div>
            </div>
          </div>
          
          <div class="chat-input">
            <el-input
              v-model="currentMessage"
              placeholder="请输入指令或问题..."
              @keyup.enter="sendMessage"
            >
              <template #append>
                <el-button type="primary" @click="sendMessage">发送</el-button>
              </template>
            </el-input>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="task-status">
          <template #header>
            <span>🤖 任务状态</span>
          </template>
          
          <div class="current-task">
            <h4>当前任务</h4>
            <p>{{ currentTask.name || '无任务' }}</p>
            <el-progress :percentage="currentTask.progress" />
          </div>
          
          <div class="task-history">
            <h4>任务历史</h4>
            <el-timeline>
              <el-timeline-item
                v-for="task in taskHistory"
                :key="task.id"
                :timestamp="task.timestamp"
              >
                {{ task.description }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Mock数据
const messages = ref([
  {
    id: 1,
    type: 'user',
    content: '请移动机械臂到指定位置',
    timestamp: '14:30:00'
  },
  {
    id: 2,
    type: 'assistant',
    content: '收到指令，正在规划机械臂运动路径...',
    timestamp: '14:30:05'
  }
])

const currentMessage = ref('')
const currentTask = ref({
  name: '机械臂位置调整',
  progress: 75
})

const taskHistory = ref([
  {
    id: 1,
    description: '完成机械臂校准',
    timestamp: '2025-07-19 14:25:00'
  },
  {
    id: 2,
    description: '执行抓取任务',
    timestamp: '2025-07-19 14:20:00'
  }
])

const sendMessage = () => {
  if (currentMessage.value.trim()) {
    messages.value.push({
      id: Date.now(),
      type: 'user',
      content: currentMessage.value,
      timestamp: new Date().toLocaleTimeString()
    })
    
    // Mock AI回复
    setTimeout(() => {
      messages.value.push({
        id: Date.now(),
        type: 'assistant',
        content: '正在处理您的请求...',
        timestamp: new Date().toLocaleTimeString()
      })
    }, 1000)
    
    currentMessage.value = ''
  }
}
</script>
```

**2.5 实现梯控系统页面**
```typescript
// src/views/interaction/ElevatorControlPage.vue  
<template>
  <div class="elevator-control-page">
    <el-card class="elevator-panel">
      <template #header>
        <span>🏢 梯控系统</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="elevator-status">
            <h3>电梯状态</h3>
            <div class="elevator-display">
              <div class="floor-indicator">
                当前楼层: <span class="current-floor">{{ currentFloor }}</span>
              </div>
              <div class="status-indicator">
                状态: <el-tag :type="elevatorStatus.type">{{ elevatorStatus.text }}</el-tag>
              </div>
            </div>
            
            <div class="floor-buttons">
              <el-button
                v-for="floor in floors"
                :key="floor"
                :type="floor === targetFloor ? 'primary' : 'default'"
                @click="callElevator(floor)"
                class="floor-btn"
              >
                {{ floor }}F
              </el-button>
            </div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="control-history">
            <h3>操作记录</h3>
            <el-table :data="operationHistory" style="width: 100%">
              <el-table-column prop="action" label="操作" />
              <el-table-column prop="floor" label="楼层" />
              <el-table-column prop="timestamp" label="时间" />
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.statusType">{{ scope.row.status }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Mock数据
const currentFloor = ref(1)
const targetFloor = ref(1)
const floors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

const elevatorStatus = ref({
  text: '停止',
  type: 'info'
})

const operationHistory = ref([
  {
    action: '呼叫电梯',
    floor: '3F',
    timestamp: '14:30:00',
    status: '完成',
    statusType: 'success'
  },
  {
    action: '呼叫电梯',
    floor: '1F',
    timestamp: '14:25:00',
    status: '完成',
    statusType: 'success'
  }
])

const callElevator = (floor: number) => {
  targetFloor.value = floor
  elevatorStatus.value = {
    text: '运行中',
    type: 'warning'
  }
  
  // Mock电梯运行
  setTimeout(() => {
    currentFloor.value = floor
    elevatorStatus.value = {
      text: '到达',
      type: 'success'
    }
    
    operationHistory.value.unshift({
      action: '呼叫电梯',
      floor: `${floor}F`,
      timestamp: new Date().toLocaleTimeString(),
      status: '完成',
      statusType: 'success'
    })
    
    setTimeout(() => {
      elevatorStatus.value = {
        text: '停止',
        type: 'info'
      }
    }, 3000)
  }, 2000)
}
</script>
```

---

### 任务 3: Mock数据框架设计
**优先级**: 🟡 中等  
**预估时间**: 1-2天

#### Kevin的具体操作步骤：

**3.1 创建Mock数据目录**
```bash
mkdir -p src/mock
touch src/mock/devices.ts
touch src/mock/tasks.ts
touch src/mock/users.ts
```

**3.2 实现设备Mock数据**
```typescript
// src/mock/devices.ts
export const mockDevices = [
  {
    id: 'fr3_right_arm',
    name: 'FR3右臂',
    type: 'robotic_arm',
    ip: '192.168.58.2',
    port: 20003,
    status: 'online',
    position: [0, -1.57, 1.57, 0, 1.57, 0],
    realtime_data: {
      joint_angles: [0, -90, 90, 0, 90, 0],
      tcp_position: [400, 0, 300, 0, 0, 0],
      force: [0.1, 0.2, 0.3, 0.01, 0.02, 0.03]
    }
  },
  {
    id: 'fr3_left_arm',
    name: 'FR3左臂',
    type: 'robotic_arm',
    ip: '192.168.58.3',
    port: 20003,
    status: 'online',
    position: [0, -1.57, 1.57, 0, 1.57, 0],
    realtime_data: {
      joint_angles: [0, -90, 90, 0, 90, 0],
      tcp_position: [400, 0, 300, 0, 0, 0],
      force: [0.1, 0.2, 0.3, 0.01, 0.02, 0.03]
    }
  },
  {
    id: 'hermes_chassis',
    name: 'Hermes底盘',
    type: 'mobile_base',
    ip: '192.168.31.211',
    port: 1448,
    status: 'online',
    position: [0, 0, 0],
    realtime_data: {
      pose: { x: 0, y: 0, theta: 0 },
      velocity: { linear: 0, angular: 0 },
      battery: 85,
      sensors: {
        lidar: 'active',
        imu: 'active',
        odometry: 'active'
      }
    }
  }
]
```

**3.3 创建API服务文件**
```bash
mkdir -p src/services
touch src/services/api.ts
touch src/services/devices.ts
touch src/services/tasks.ts
```

**3.4 实现设备API服务**
```typescript
// src/services/devices.ts
import { mockDevices } from '@/mock/devices'
import type { Device } from '@/types/device'

export const deviceApi = {
  async getDevices(): Promise<{ data: Device[] }> {
    // Mock API调用延迟
    await new Promise(resolve => setTimeout(resolve, 300))
    return { data: mockDevices }
  },
  
  async connectDevice(deviceId: string): Promise<{ success: boolean }> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    const device = mockDevices.find(d => d.id === deviceId)
    if (device) {
      device.status = 'online'
      return { success: true }
    }
    return { success: false }
  },
  
  async disconnectDevice(deviceId: string): Promise<{ success: boolean }> {
    await new Promise(resolve => setTimeout(resolve, 500))
    const device = mockDevices.find(d => d.id === deviceId)
    if (device) {
      device.status = 'offline'
      return { success: true }
    }
    return { success: false }
  }
}
```

**3.5 创建类型定义文件**
```bash
mkdir -p src/types
touch src/types/device.ts
touch src/types/task.ts
touch src/types/common.ts
```

**3.6 验证Mock数据框架**
```bash
# 启动开发服务器测试Mock数据
npm run dev
# 检查浏览器控制台确认Mock数据加载正常
```

---

## 🔄 Phase 1-2: 后端API集成 (后续执行)

### 任务 4: 后端API集成
**优先级**: 🟡 中等  
**预估时间**: 1-2周

#### Kevin的具体操作步骤：

**4.1 激活后端真实连接**
```bash
cd /Users/shushu/xc-robot/xc-recon-v2/backend

# 激活PostgreSQL依赖
sed -i 's/# psycopg2-binary==2.9.9/psycopg2-binary==2.9.9/' requirements.txt
pip install psycopg2-binary

# 运行数据库迁移
python -m alembic upgrade head
```

**4.2 替换设备连接逻辑**
```bash
# 编辑设备服务文件
vim backend/services/device_manager.py
vim backend/services/fr3_service.py  
vim backend/services/hermes_service.py
```

**4.3 集成前后端**
```bash
# 更新前端API调用
vim src/services/devices.ts

# 将Mock API替换为真实后端调用
const API_BASE_URL = 'http://localhost:8000'
```

---

### 任务 5: 硬件连接测试
**优先级**: 🟢 低  
**预估时间**: 3-5天

#### Kevin的具体操作步骤：

**5.1 准备Win环境**
```bash
# 在Windows机器上
git clone <repository>
cd xc-recon-v2

# 运行Windows启动脚本
./scripts/start_win.bat
```

**5.2 硬件连接验证**
```bash
# 验证FR3机械臂连接
ping 192.168.58.2
ping 192.168.58.3

# 验证Hermes底盘连接  
ping 192.168.31.211
curl http://192.168.31.211:1448/api/status
```

**5.3 功能测试**
```bash
# 测试机械臂连接和控制
python -m backend.services.fr3_service test_connection
python -m backend.services.fr3_service test_movement

# 测试底盘导航功能
python -m backend.services.hermes_service test_navigation
python -m backend.services.hermes_service test_slam

# 测试视觉相机采集
python -m backend.services.vision_service test_cameras
python -m backend.services.vision_service test_recognition

# 完整工作流程测试
npm run e2e:test
```

**5.4 集成测试验证**
```bash
# 运行完整集成测试套件
npm run test:integration
python -m pytest backend/tests/test_integration.py

# 生成测试报告
npm run test:report
```

---

## 📊 进度跟踪

### 当前状态
- ✅ **策略制定**: UI优先策略确定
- ✅ **文档准备**: xc_recon_oldgui.md + Q&A完整
- ✅ **后端就绪**: 仿真模式可用，API框架完整
- 🎯 **当前任务**: Vue3菜单框架建立

### 下一步行动
1. **立即开始**: 任务1 - Vue3导航菜单框架
2. **重点实现**: 任务2 - 智能交互模块
3. **支撑开发**: 任务3 - Mock数据框架
4. **最终集成**: 任务4-5 - API和硬件连接

### 成功标准
- [ ] 9分组菜单结构完整显示
- [ ] 智能交互3个页面可正常操作
- [ ] Mock数据驱动所有UI功能
- [ ] 前后端API成功对接
- [ ] Win环境硬件测试通过

---

## 📋 质量检查清单

### 任务1完成标准
- [ ] 菜单配置文件正确创建并导出
- [ ] 路由配置包含所有25个子功能路径
- [ ] 侧边栏组件正确显示9个主分组
- [ ] 所有菜单项点击可正常跳转
- [ ] 移动端响应式布局正常

### 任务2完成标准
- [ ] 人脸识别页面Mock摄像头界面显示
- [ ] 智能对话页面聊天功能可用
- [ ] 梯控系统页面电梯操作面板正常
- [ ] 所有页面Mock数据正确加载
- [ ] 页面样式符合项目配色规范

### 任务3完成标准
- [ ] Mock数据结构完整覆盖所有设备类型
- [ ] API服务封装完整且类型安全
- [ ] 所有Mock API响应延迟模拟真实环境
- [ ] 错误处理和状态管理正确实现
- [ ] TypeScript类型定义完整无误

### 任务4完成标准
- [ ] 后端PostgreSQL连接正常
- [ ] 所有设备服务真实硬件连接成功
- [ ] 前端API调用完全替换Mock数据
- [ ] 错误处理和重连机制稳定
- [ ] 数据流完整性验证通过

### 任务5完成标准
- [ ] Win环境所有硬件设备连接正常
- [ ] 前后端完整功能流程测试通过
- [ ] 性能和稳定性指标达标
- [ ] 安全测试和边界条件验证
- [ ] 用户体验测试满足要求

---

## 🛠️ 常见问题排查

### 前端开发问题

**问题1: npm run dev启动失败**
```bash
# 解决方案
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm run dev
```

**问题2: 路由跳转404错误**
```bash
# 检查路由配置
cat src/router/index.ts | grep -A 5 "path.*interaction"
# 确认组件文件是否存在
ls -la src/views/interaction/
```

**问题3: TypeScript类型错误**
```bash
# 检查类型定义
npm run type-check
# 更新类型定义
touch src/types/global.d.ts
```

### 后端集成问题

**问题4: PostgreSQL连接失败**
```bash
# 检查数据库状态
sudo systemctl status postgresql
# 检查连接配置
cat backend/.env | grep DATABASE
```

**问题5: 硬件设备连接超时**
```bash
# 网络连通性测试
ping 192.168.58.2
ping 192.168.58.3
ping 192.168.31.211

# 端口占用检查
netstat -tulpn | grep -E "(20003|1448)"
```

**问题6: API响应慢或超时**
```bash
# 检查后端日志
tail -f backend/logs/app.log
# 性能监控
top -p $(pgrep -f "uvicorn")
```

### Mock数据问题

**问题7: Mock数据不更新**
```bash
# 清除缓存重启
npm run dev -- --force
# 检查数据导入
console.log("Mock data loaded:", mockDevices.length)
```

**问题8: TypeScript导入错误**
```bash
# 检查模块路径
npm run type-check
# 更新tsconfig路径映射
cat tsconfig.json | grep -A 10 "paths"
```

---

## 🚨 注意事项

### 开发环境
- **Mac开发**: 使用Mock数据，无需真实硬件
- **依赖管理**: 确保Node.js 18+, Python 3.11.10
- **端口配置**: 前端3000，后端8000
- **热重载**: 确保开发时自动刷新

### 代码规范
- **Vue3**: 使用Composition API + TypeScript
- **Element Plus**: 统一UI组件库
- **配色系统**: 参考现有项目配色
- **命名规范**: kebab-case文件名，camelCase变量名

### 测试策略
- **每个页面**: 先Mock数据运行测试
- **API集成**: 逐步替换Mock为真实调用
- **硬件测试**: 最终在Win环境验证

---

## 🎯 Kevin执行工作流总结

### 标准化操作流程
每个任务都遵循以下4阶段工作流：

**阶段1: 准备 (Prepare)**
- ✅ 检查开发环境状态
- ✅ 验证依赖和工具可用性  
- ✅ 确认当前Git状态和分支

**阶段2: 实现 (Implement)**
- 🔧 创建必要目录和文件结构
- 💻 编写核心功能代码
- 🔗 集成Mock数据或API连接

**阶段3: 验证 (Validate)**
- 🧪 本地功能测试
- 📊 质量检查清单验证
- 🐛 问题排查和修复

**阶段4: 提交 (Commit)**
- 📝 Git提交和推送
- 📋 更新进度状态
- 📖 文档同步更新

### 快速开始指令

```bash
# 立即开始任务1
cd /Users/shushu/xc-robot/xc-recon-v2/frontend/xc-recon-frontend
npm run dev  # 验证环境
mkdir -p src/config && touch src/config/menu.ts  # 创建菜单配置
```

### 优先级提醒
- 🔥 **P0 - 立即执行**: 任务1 Vue3菜单框架 + 任务2 智能交互模块
- 🟡 **P1 - 重要**: 任务3 Mock数据框架
- 🟢 **P2-P3 - 后续**: 任务4-5 API集成和硬件测试

### 关键约束记住
- 📱 **响应式设计**: 支持移动端、平板、桌面端
- 🎨 **配色系统**: 严格遵循项目现有配色规范
- 🔧 **TypeScript**: 所有代码必须类型安全
- 🎯 **UI优先**: Mac开发用Mock数据，Win测试连硬件

---

**状态**: 📋 任务分解和操作指南已完成，Kevin可立即按照标准化工作流开始执行任务1 - Vue3导航菜单框架建立 🚀

**下一步**: 运行 `npm run dev` 验证环境，然后创建 `src/config/menu.ts` 菜单配置文件
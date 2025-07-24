<template>
  <div id="main-content" class="w-full h-[calc(100vh-100px)] overflow-auto p-6">
    <!-- Page Header -->
    <div id="page-header" class="mb-6">
      <div class="flex items-center text-sm text-gray-500 mb-2">
        <span>主菜单</span>
        <i class="fa-solid fa-chevron-right mx-2 text-xs"></i>
        <span>仿真规划</span>
        <i class="fa-solid fa-chevron-right mx-2 text-xs"></i>
        <span class="text-primary">任务编排</span>
      </div>
      <h1 class="text-2xl font-bold text-secondary">任务编排系统</h1>
      <p class="text-gray-600">复杂任务流程的编排与执行管理</p>
    </div>
    
    <!-- Main Content Grid -->
    <div class="grid grid-cols-12 gap-4">
      <!-- Task Designer - Full width on mobile, spans 12 columns -->
      <div id="task-designer-container" class="col-span-12 bg-white rounded-lg shadow-md">
        <div class="p-3 border-b border-gray-200 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-palette text-primary mr-2"></i>
            <h2 class="font-semibold">任务设计器</h2>
          </div>
          <div class="flex space-x-2">
            <button 
              @click="saveTask"
              class="px-2 py-1 bg-primary text-white rounded-md text-sm flex items-center hover:bg-blue-600 transition-colors"
            >
              <i class="fa-solid fa-save mr-1"></i> 保存
            </button>
            <button 
              @click="executeTask"
              class="px-2 py-1 bg-success text-white rounded-md text-sm flex items-center hover:bg-green-700 transition-colors"
            >
              <i class="fa-solid fa-play mr-1"></i> 执行
            </button>
          </div>
        </div>
        <div class="p-4 bg-secondary h-[360px] overflow-auto relative" id="designer-canvas">
          <!-- Task Flow Diagram -->
          <svg width="100%" height="100%" class="absolute top-0 left-0 pointer-events-none">
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#409EFF"></polygon>
              </marker>
              <marker id="arrowhead-success" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#00A870"></polygon>
              </marker>
              <marker id="arrowhead-error" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#F56C6C"></polygon>
              </marker>
            </defs>
            <!-- Connection Lines -->
            <!-- Start to Init -->
            <path d="M100,50 L100,90" class="connector"></path>
            <!-- Init to Vision -->
            <path d="M100,130 L100,170" class="connector"></path>
            <!-- Vision to Condition -->
            <path d="M100,210 L100,250" class="connector"></path>
            <!-- Condition to Error -->
            <path d="M170,270 L280,270" class="connector connector-error"></path>
            <!-- Error to Notify -->
            <path d="M320,290 L320,330" class="connector connector-error"></path>
            <!-- Notify to End -->
            <path d="M320,370 L320,410" class="connector connector-error"></path>
            <!-- Condition to Path Planning -->
            <path d="M100,290 L100,330" class="connector connector-success"></path>
            <!-- Path Planning to Grab -->
            <path d="M100,370 L100,410" class="connector"></path>
            <!-- Grab to Confirm -->
            <path d="M100,450 L100,490" class="connector"></path>
            <!-- Confirm to Complete -->
            <path d="M100,530 L100,570" class="connector"></path>
          </svg>

          <!-- Task Nodes -->
          <div 
            v-for="node in taskNodes" 
            :key="node.id"
            :ref="el => setNodeRef(node.id, el)"
            @mousedown="startDrag($event, node.id)"
            :class="[
              'node bg-white p-2 rounded-md shadow-md mb-4 border-l-4 cursor-move transition-all duration-200',
              getNodeBorderClass(node.type),
              node.status === 'active' ? 'active-node' : '',
              'absolute'
            ]"
            :style="{ left: node.x + 'px', top: node.y + 'px', width: node.width + 'px' }"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <i :class="[node.icon, getNodeIconClass(node.type), 'mr-1']"></i>
                <span class="font-medium">{{ node.title }}</span>
              </div>
              <span 
                v-if="node.duration"
                class="text-xs bg-gray-100 px-1 rounded"
              >⏱️ {{ node.duration }}</span>
            </div>
          </div>
        </div>
        <div class="p-2 border-t border-gray-200 bg-white flex space-x-2">
          <button 
            @click="addStep"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center transition-colors"
          >
            <i class="fa-solid fa-plus mr-1"></i> 添加步骤
          </button>
          <button 
            @click="addConnection"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center transition-colors"
          >
            <i class="fa-solid fa-link mr-1"></i> 连接线
          </button>
          <button 
            @click="addCondition"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center transition-colors"
          >
            <i class="fa-solid fa-code-branch mr-1"></i> 条件判断
          </button>
          <button 
            @click="addLoop"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center transition-colors"
          >
            <i class="fa-solid fa-redo mr-1"></i> 循环
          </button>
          <button 
            @click="addErrorHandler"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center transition-colors"
          >
            <i class="fa-solid fa-exclamation-triangle mr-1"></i> 异常处理
          </button>
        </div>
      </div>
      
      <!-- Component Library -->
      <div id="component-library" class="col-span-12 md:col-span-4 bg-white rounded-lg shadow-md">
        <div class="p-3 border-b border-gray-200 flex items-center">
          <i class="fa-solid fa-puzzle-piece text-primary mr-2"></i>
          <h2 class="font-semibold">组件库</h2>
        </div>
        <div class="p-3 h-[260px] overflow-y-auto">
          <div class="mb-4" v-for="category in componentCategories" :key="category.id">
            <h3 class="text-sm font-semibold mb-2 flex items-center">
              <i :class="[category.icon, category.color, 'mr-1']"></i> {{ category.title }}:
            </h3>
            <div class="space-y-2">
              <div 
                v-for="component in category.components" 
                :key="component.id"
                @mousedown="startComponentDrag($event, component)"
                class="component-library-item p-2 rounded-md border border-gray-200 flex items-center cursor-grab hover:bg-purple-50 hover:transform hover:-translate-y-0.5 transition-all duration-200"
              >
                <i :class="[component.icon, category.color, 'mr-2']"></i>
                <span>{{ component.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Execution Monitor -->
      <div id="execution-monitor" class="col-span-12 md:col-span-4 bg-white rounded-lg shadow-md">
        <div class="p-3 border-b border-gray-200 flex items-center">
          <i class="fa-solid fa-chart-line text-primary mr-2"></i>
          <h2 class="font-semibold">执行监控</h2>
        </div>
        <div class="p-3 h-[260px] overflow-y-auto">
          <div class="mb-4">
            <div class="mb-2 flex justify-between items-center">
              <span class="text-sm font-medium">📈 当前进度:</span>
              <span class="text-sm">{{ executionData.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-primary h-2 rounded-full transition-all duration-500 ease-in-out" 
                :style="{ width: executionData.progress + '%' }"
              ></div>
            </div>
          </div>
          
          <div class="mb-4">
            <div class="flex justify-between mb-1">
              <span class="text-sm">⏱️ 已用时间:</span>
              <span class="text-sm">{{ executionData.elapsedTime }}秒</span>
            </div>
            <div class="flex justify-between mb-1">
              <span class="text-sm">⏳ 预计剩余:</span>
              <span class="text-sm">{{ executionData.remainingTime }}秒</span>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2">🎯 当前步骤:</h3>
            <div class="p-2 bg-secondary rounded-md border-l-4 border-primary">
              <div class="flex items-center">
                <i :class="[executionData.currentStep.icon, 'text-primary mr-2']"></i>
                <span>{{ executionData.currentStep.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2">📊 步骤状态:</h3>
            <div class="space-y-1">
              <div class="flex justify-between">
                <span class="text-sm flex items-center">
                  <i class="fa-solid fa-check-circle text-success mr-1"></i> 已完成:
                </span>
                <span class="text-sm">{{ executionData.stepStats.completed }}步</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm flex items-center">
                  <i class="fa-solid fa-sync text-primary mr-1"></i> 进行中:
                </span>
                <span class="text-sm">{{ executionData.stepStats.inProgress }}步</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm flex items-center">
                  <i class="fa-solid fa-hourglass-half text-gray-400 mr-1"></i> 待执行:
                </span>
                <span class="text-sm">{{ executionData.stepStats.pending }}步</span>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2">
            <button 
              @click="pauseExecution"
              :disabled="!isExecuting"
              class="flex-1 px-2 py-1 bg-warning text-white rounded text-sm hover:bg-yellow-600 transition-colors disabled:opacity-50"
            >
              <i class="fa-solid fa-pause mr-1"></i> 暂停
            </button>
            <button 
              @click="skipStep"
              :disabled="!isExecuting"
              class="flex-1 px-2 py-1 bg-info text-white rounded text-sm hover:bg-cyan-600 transition-colors disabled:opacity-50"
            >
              <i class="fa-solid fa-step-forward mr-1"></i> 跳过
            </button>
            <button 
              @click="stopExecution"
              :disabled="!isExecuting"
              class="flex-1 px-2 py-1 bg-danger text-white rounded text-sm hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              <i class="fa-solid fa-stop mr-1"></i> 停止
            </button>
          </div>
        </div>
      </div>
      
      <!-- Task Configuration -->
      <div id="task-config" class="col-span-12 md:col-span-4 bg-white rounded-lg shadow-md">
        <div class="p-3 border-b border-gray-200 flex items-center">
          <i class="fa-solid fa-cog text-primary mr-2"></i>
          <h2 class="font-semibold">任务配置</h2>
        </div>
        <div class="p-3 h-[260px] overflow-y-auto">
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2">📛 任务名称:</h3>
            <input 
              type="text" 
              v-model="taskConfig.name"
              class="w-full p-2 border border-gray-300 rounded-md text-sm focus:border-primary focus:outline-none"
            >
          </div>
          
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2">🔄 执行模式:</h3>
            <div class="space-y-2">
              <div class="flex items-center">
                <input 
                  type="radio" 
                  id="mode-single" 
                  value="single"
                  v-model="taskConfig.executionMode"
                  class="mr-2"
                >
                <label for="mode-single" class="text-sm">单次执行</label>
              </div>
              <div class="flex items-center">
                <input 
                  type="radio" 
                  id="mode-loop" 
                  value="loop"
                  v-model="taskConfig.executionMode"
                  class="mr-2"
                >
                <label for="mode-loop" class="text-sm flex items-center">
                  循环执行
                  <input 
                    type="number" 
                    v-model.number="taskConfig.loopCount"
                    :disabled="taskConfig.executionMode !== 'loop'"
                    class="ml-2 w-12 p-1 border border-gray-300 rounded text-sm disabled:bg-gray-100"
                  >
                  次
                </label>
              </div>
              <div class="flex items-center">
                <input 
                  type="radio" 
                  id="mode-scheduled" 
                  value="scheduled"
                  v-model="taskConfig.executionMode"
                  class="mr-2"
                >
                <label for="mode-scheduled" class="text-sm">定时执行</label>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="text-sm font-medium mb-2">🚨 异常策略:</h3>
            <div class="space-y-2">
              <div class="flex items-center">
                <input 
                  type="radio" 
                  id="error-stop" 
                  value="stop"
                  v-model="taskConfig.errorStrategy"
                  class="mr-2"
                >
                <label for="error-stop" class="text-sm">停止执行</label>
              </div>
              <div class="flex items-center">
                <input 
                  type="radio" 
                  id="error-retry" 
                  value="retry"
                  v-model="taskConfig.errorStrategy"
                  class="mr-2"
                >
                <label for="error-retry" class="text-sm flex items-center">
                  重试
                  <input 
                    type="number" 
                    v-model.number="taskConfig.retryCount"
                    :disabled="taskConfig.errorStrategy !== 'retry'"
                    class="ml-2 w-12 p-1 border border-gray-300 rounded text-sm disabled:bg-gray-100"
                  >
                  次后停止
                </label>
              </div>
              <div class="flex items-center">
                <input 
                  type="radio" 
                  id="error-continue" 
                  value="continue"
                  v-model="taskConfig.errorStrategy"
                  class="mr-2"
                >
                <label for="error-continue" class="text-sm">跳过错误继续执行</label>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2">
            <button 
              @click="showAdvancedConfig"
              class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center transition-colors"
            >
              <i class="fa-solid fa-sliders-h mr-1"></i> 高级配置
            </button>
            <button 
              @click="validateTask"
              class="px-3 py-1 bg-primary text-white rounded text-sm flex items-center hover:bg-blue-600 transition-colors"
            >
              <i class="fa-solid fa-check mr-1"></i> 验证
            </button>
          </div>
        </div>
      </div>
      
      <!-- Execution Log -->
      <div id="execution-log" class="col-span-12 bg-white rounded-lg shadow-md">
        <div class="p-3 border-b border-gray-200 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>
            <h2 class="font-semibold">执行日志</h2>
          </div>
          <div class="flex space-x-2">
            <button 
              @click="viewAllLogs"
              class="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs transition-colors"
            >
              查看全部
            </button>
            <button 
              @click="clearLogs"
              class="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs transition-colors"
            >
              清空
            </button>
          </div>
        </div>
        <div class="p-3 h-[160px] overflow-y-auto">
          <div class="space-y-1 text-sm">
            <div 
              v-for="log in executionLogs" 
              :key="log.id"
              class="flex"
            >
              <span class="text-gray-500 mr-2">{{ log.timestamp }}</span>
              <span :class="log.status === 'current' ? 'text-primary font-medium' : ''">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 任务节点接口定义
interface TaskNode {
  id: string
  title: string
  type: 'start' | 'action' | 'condition' | 'error' | 'end'
  icon: string
  x: number
  y: number
  width: number
  duration?: string
  status?: 'active' | 'completed' | 'pending'
}

// 组件接口定义
interface Component {
  id: string
  name: string
  icon: string
  type: string
}

interface ComponentCategory {
  id: string
  title: string
  icon: string
  color: string
  components: Component[]
}

// 执行数据接口定义
interface ExecutionData {
  progress: number
  elapsedTime: number
  remainingTime: number
  currentStep: {
    name: string
    icon: string
  }
  stepStats: {
    completed: number
    inProgress: number
    pending: number
  }
}

// 任务配置接口定义
interface TaskConfig {
  name: string
  executionMode: 'single' | 'loop' | 'scheduled'
  loopCount: number
  errorStrategy: 'stop' | 'retry' | 'continue'
  retryCount: number
}

// 执行日志接口定义
interface ExecutionLog {
  id: string
  timestamp: string
  message: string
  status?: 'current' | 'normal'
}

// 响应式数据
const isExecuting = ref(false)
const nodeRefs = ref<{ [key: string]: HTMLElement }>({})

// 拖拽相关状态
const dragState = reactive({
  isDragging: false,
  activeNodeId: '',
  offsetX: 0,
  offsetY: 0
})

// 任务节点数据
const taskNodes = ref<TaskNode[]>([
  { id: 'start', title: '开始', type: 'start', icon: 'fa-solid fa-share-from-square', x: 80, y: 20, width: 160 },
  { id: 'init', title: '机械臂初始化', type: 'action', icon: 'fa-solid fa-robot', x: 80, y: 90, width: 256, duration: '5秒' },
  { id: 'vision', title: '视觉检测目标', type: 'action', icon: 'fa-solid fa-eye', x: 80, y: 170, width: 256, duration: '3秒' },
  { id: 'condition', title: '目标检测成功?', type: 'condition', icon: 'fa-solid fa-question-circle', x: 80, y: 250, width: 256 },
  { id: 'error', title: '报错处理', type: 'error', icon: 'fa-solid fa-times-circle', x: 280, y: 250, width: 256 },
  { id: 'notify', title: '通知用户', type: 'error', icon: 'fa-solid fa-phone', x: 280, y: 330, width: 256 },
  { id: 'end-error', title: '结束', type: 'end', icon: 'fa-solid fa-share-from-square', x: 280, y: 410, width: 160 },
  { id: 'path-planning', title: '规划抓取路径', type: 'action', icon: 'fa-solid fa-bullseye', x: 80, y: 330, width: 256, duration: '2秒', status: 'active' },
  { id: 'grab', title: '双臂协调抓取', type: 'action', icon: 'fa-solid fa-hands-helping', x: 80, y: 410, width: 256, duration: '8秒' },
  { id: 'confirm', title: '物品放置确认', type: 'action', icon: 'fa-solid fa-box', x: 80, y: 490, width: 256, duration: '2秒' },
  { id: 'complete', title: '任务完成', type: 'end', icon: 'fa-solid fa-check-circle', x: 80, y: 570, width: 160 }
])

// 组件库数据
const componentCategories = ref<ComponentCategory[]>([
  {
    id: 'basic',
    title: '基础动作',
    icon: 'fa-solid fa-bullseye',
    color: 'text-success',
    components: [
      { id: 'arm-control', name: '机械臂控制', icon: 'fa-solid fa-robot', type: 'action' },
      { id: 'chassis-move', name: '底盘移动', icon: 'fa-solid fa-truck', type: 'action' },
      { id: 'vision-detect', name: '视觉检测', icon: 'fa-solid fa-eye', type: 'action' },
      { id: 'camera-capture', name: '拍照记录', icon: 'fa-solid fa-camera', type: 'action' }
    ]
  },
  {
    id: 'control',
    title: '控制结构',
    icon: 'fa-solid fa-sync',
    color: 'text-primary',
    components: [
      { id: 'condition', name: '条件判断', icon: 'fa-solid fa-question-circle', type: 'condition' },
      { id: 'loop', name: '循环执行', icon: 'fa-solid fa-redo', type: 'control' },
      { id: 'delay', name: '等待延时', icon: 'fa-solid fa-pause', type: 'control' },
      { id: 'error-handler', name: '异常处理', icon: 'fa-solid fa-exclamation-triangle', type: 'error' }
    ]
  },
  {
    id: 'advanced',
    title: '高级功能',
    icon: 'fa-solid fa-gamepad',
    color: 'text-warning',
    components: [
      { id: 'coordination', name: '设备协调', icon: 'fa-solid fa-hands-helping', type: 'advanced' },
      { id: 'notification', name: '消息通知', icon: 'fa-solid fa-phone', type: 'advanced' },
      { id: 'logging', name: '日志记录', icon: 'fa-solid fa-clipboard-list', type: 'advanced' },
      { id: 'config', name: '参数配置', icon: 'fa-solid fa-wrench', type: 'advanced' }
    ]
  }
])

// 执行监控数据
const executionData = reactive<ExecutionData>({
  progress: 60,
  elapsedTime: 18,
  remainingTime: 12,
  currentStep: {
    name: '双臂协调抓取',
    icon: 'fa-solid fa-hands-helping'
  },
  stepStats: {
    completed: 4,
    inProgress: 1,
    pending: 3
  }
})

// 任务配置数据
const taskConfig = reactive<TaskConfig>({
  name: '物品抓取任务_v1.2',
  executionMode: 'single',
  loopCount: 3,
  errorStrategy: 'stop',
  retryCount: 3
})

// 执行日志数据
const executionLogs = ref<ExecutionLog[]>([
  { id: '1', timestamp: '14:30:15', message: '开始任务' },
  { id: '2', timestamp: '14:30:20', message: '机械臂就位' },
  { id: '3', timestamp: '14:30:23', message: '视觉检测中' },
  { id: '4', timestamp: '14:30:26', message: '检测到目标' },
  { id: '5', timestamp: '14:30:28', message: '开始路径规划' },
  { id: '6', timestamp: '14:30:30', message: '路径规划完成' },
  { id: '7', timestamp: '14:30:33', message: '双臂协调中', status: 'current' }
])

// 设置节点引用
const setNodeRef = (nodeId: string, el: HTMLElement | null) => {
  if (el) {
    nodeRefs.value[nodeId] = el
  }
}

// 获取节点边框样式类
const getNodeBorderClass = (type: string) => {
  const classMap = {
    'start': 'border-primary',
    'action': 'border-success',
    'condition': 'border-warning',
    'error': 'border-danger',
    'end': 'border-primary'
  }
  return classMap[type as keyof typeof classMap] || 'border-gray-300'
}

// 获取节点图标颜色类
const getNodeIconClass = (type: string) => {
  const classMap = {
    'start': 'text-primary',
    'action': 'text-success',
    'condition': 'text-warning',
    'error': 'text-danger',
    'end': 'text-primary'
  }
  return classMap[type as keyof typeof classMap] || 'text-gray-500'
}

// 开始拖拽节点
const startDrag = (event: MouseEvent, nodeId: string) => {
  const node = nodeRefs.value[nodeId]
  if (!node) return

  dragState.isDragging = true
  dragState.activeNodeId = nodeId

  const rect = node.getBoundingClientRect()
  dragState.offsetX = event.clientX - rect.left
  dragState.offsetY = event.clientY - rect.top

  node.classList.add('z-50')
  event.preventDefault()
}

// 处理鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  if (!dragState.isDragging || !dragState.activeNodeId) return

  const canvas = document.getElementById('designer-canvas')
  if (!canvas) return

  const canvasRect = canvas.getBoundingClientRect()
  const node = nodeRefs.value[dragState.activeNodeId]
  if (!node) return

  // 计算新位置
  let newX = event.clientX - canvasRect.left - dragState.offsetX
  let newY = event.clientY - canvasRect.top - dragState.offsetY

  // 限制在画布范围内
  newX = Math.max(0, Math.min(newX, canvasRect.width - node.offsetWidth))
  newY = Math.max(0, Math.min(newY, canvasRect.height - node.offsetHeight))

  // 更新节点位置
  const nodeData = taskNodes.value.find(n => n.id === dragState.activeNodeId)
  if (nodeData) {
    nodeData.x = newX
    nodeData.y = newY
  }
}

// 结束拖拽
const endDrag = () => {
  if (dragState.activeNodeId) {
    const node = nodeRefs.value[dragState.activeNodeId]
    if (node) {
      node.classList.remove('z-50')
    }
  }
  
  dragState.isDragging = false
  dragState.activeNodeId = ''
  dragState.offsetX = 0
  dragState.offsetY = 0
}

// 开始拖拽组件
const startComponentDrag = (event: MouseEvent, component: Component) => {
  event.preventDefault()
  
  // 创建提示消息
  ElMessage.info(`拖放功能已触发：${component.name}，在实际系统中将创建新节点`)
}

// 任务操作函数
const saveTask = () => {
  ElMessage.success('任务流程已保存')
}

const executeTask = () => {
  isExecuting.value = true
  ElMessage.success('开始执行任务流程')
  
  // 模拟执行过程
  simulateExecution()
}

const pauseExecution = () => {
  ElMessage.warning('任务执行已暂停')
}

const skipStep = () => {
  ElMessage.info('已跳过当前步骤')
}

const stopExecution = () => {
  isExecuting.value = false
  ElMessage.error('任务执行已停止')
}

// 设计器操作函数
const addStep = () => {
  ElMessage.info('添加新的任务步骤')
}

const addConnection = () => {
  ElMessage.info('添加连接线')
}

const addCondition = () => {
  ElMessage.info('添加条件判断节点')
}

const addLoop = () => {
  ElMessage.info('添加循环控制节点')
}

const addErrorHandler = () => {
  ElMessage.info('添加异常处理节点')
}

// 配置操作函数
const showAdvancedConfig = () => {
  ElMessage.info('打开高级配置面板')
}

const validateTask = () => {
  ElMessage.success('任务配置验证通过')
}

// 日志操作函数
const viewAllLogs = () => {
  ElMessage.info('查看完整执行日志')
}

const clearLogs = () => {
  executionLogs.value = []
  ElMessage.success('执行日志已清空')
}

// 模拟执行过程
const simulateExecution = () => {
  const interval = setInterval(() => {
    if (executionData.progress < 100) {
      executionData.progress += 2
      executionData.elapsedTime += 1
      executionData.remainingTime = Math.max(0, executionData.remainingTime - 1)
      
      // 添加新的日志条目
      if (Math.random() > 0.7) {
        const newLog: ExecutionLog = {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString(),
          message: `执行进度 ${executionData.progress}%`,
          status: 'current'
        }
        
        // 移除之前的current状态
        executionLogs.value.forEach(log => {
          if (log.status === 'current') {
            delete log.status
          }
        })
        
        executionLogs.value.push(newLog)
      }
    } else {
      clearInterval(interval)
      isExecuting.value = false
      ElMessage.success('任务执行完成')
    }
  }, 1000)
}

// 生命周期
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', endDrag)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', endDrag)
})
</script>

<style scoped>
/* 项目配色系统 */
.text-primary {
  color: #409EFF;
}

.text-secondary {
  color: #2c3e50;
}

.text-success {
  color: #00A870;
}

.text-warning {
  color: #E6A23C;
}

.text-danger {
  color: #F56C6C;
}

.text-info {
  color: #909399;
}

.bg-primary {
  background-color: #409EFF;
}

.bg-secondary {
  background-color: #F3F0FF;
}

.bg-success {
  background-color: #00A870;
}

.bg-warning {
  background-color: #E6A23C;
}

.bg-danger {
  background-color: #F56C6C;
}

.bg-info {
  background-color: #06B6D4;
}

/* 任务编排专用样式 */
.node {
  cursor: move;
  transition: all 0.2s;
  user-select: none;
}

.node:hover {
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.5);
  transform: translateY(-1px);
}

.active-node {
  box-shadow: 0 0 0 2px #409EFF;
}

.component-library-item {
  transition: all 0.2s;
  user-select: none;
}

.component-library-item:hover {
  background-color: #F3F0FF;
  transform: translateY(-2px);
}

.progress-bar {
  transition: width 0.5s ease-in-out;
}

/* SVG连接线样式 */
.connector {
  fill: none;
  stroke: #409EFF;
  stroke-width: 2;
  marker-end: url(#arrowhead);
}

.connector-error {
  stroke: #F56C6C;
  marker-end: url(#arrowhead-error);
}

.connector-success {
  stroke: #00A870;
  marker-end: url(#arrowhead-success);
}

/* 边框样式 */
.border-primary {
  border-left-color: #409EFF;
}

.border-success {
  border-left-color: #00A870;
}

.border-warning {
  border-left-color: #E6A23C;
}

.border-danger {
  border-left-color: #F56C6C;
}

/* 按钮禁用状态 */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid.md\\:grid-cols-4 {
    grid-template-columns: 1fr;
  }
  
  #designer-canvas {
    height: 300px;
  }
  
  .node {
    max-width: 200px;
    font-size: 0.8rem;
  }
  
  .flex.space-x-2 {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .flex.space-x-2 > button {
    min-width: fit-content;
  }
}

@media (max-width: 640px) {
  .text-xs {
    font-size: 0.75rem;
  }
  
  .p-3 {
    padding: 0.5rem;
  }
  
  .space-x-2 > * + * {
    margin-left: 0.25rem;
  }
}
</style>
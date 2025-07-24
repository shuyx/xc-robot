<template>
  <div class="w-full h-[calc(100vh-100px)] overflow-auto bg-gray-100 p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-secondary">端到端场景测试</h1>
          <p class="text-gray-600 mt-1">完整任务流程的端到端验证测试</p>
        </div>
        <div class="flex space-x-3">
          <button 
            @click="createNewScene"
            class="px-4 py-2 bg-white border border-gray-300 rounded-md flex items-center text-gray-700 hover:bg-gray-50"
          >
            <i class="fa-solid fa-plus mr-2"></i>
            新建场景
          </button>
          <button 
            @click="runTest"
            :disabled="!canRunTest"
            class="px-4 py-2 bg-scene text-white rounded-md flex items-center hover:bg-opacity-90 disabled:opacity-50"
          >
            <i class="fa-solid fa-play mr-2"></i>
            运行测试
          </button>
        </div>
      </div>
      
      <!-- Breadcrumb -->
      <div class="flex mt-4 text-sm">
        <span class="text-gray-500">主菜单</span>
        <i class="fa-solid fa-chevron-right mx-2 text-gray-400 text-xs mt-1"></i>
        <span class="text-gray-500">场景测试</span>
        <i class="fa-solid fa-chevron-right mx-2 text-gray-400 text-xs mt-1"></i>
        <span class="text-primary font-medium">端到端场景</span>
      </div>
    </div>

    <!-- Scene Library -->
    <div class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-theater-masks text-scene mr-2"></i>
        <h2 class="text-lg font-medium">场景库</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Scene Cards -->
        <div 
          v-for="scene in sceneLibrary" 
          :key="scene.id"
          :class="[
            'bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition',
            scene.status === 'running' ? 'border-scene border-opacity-30' : 
            scene.status === 'draft' ? 'border-dashed border-gray-300' : 
            'border-gray-200'
          ]"
        >
          <div class="flex justify-between items-center mb-3">
            <div class="flex items-center">
              <i 
                :class="[
                  'mr-2',
                  scene.status === 'passed' ? 'fa-solid fa-check-circle text-completed' :
                  scene.status === 'running' ? 'fa-solid fa-cog fa-spin text-sceneConfig' :
                  scene.status === 'failed' ? 'fa-solid fa-times-circle text-danger' :
                  'fa-solid fa-pencil-alt text-gray-500'
                ]"
              ></i>
              <h3 class="font-medium">{{ scene.name }}</h3>
            </div>
            <div class="flex space-x-1">
              <button 
                @click="toggleSceneMenu(scene.id)"
                class="p-1 text-gray-400 hover:text-primary"
              >
                <i class="fa-solid fa-ellipsis-vertical"></i>
              </button>
            </div>
          </div>
          
          <div class="mb-4">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">状态:</span>
              <span 
                :class="[
                  'font-medium',
                  scene.status === 'passed' ? 'text-completed' :
                  scene.status === 'running' ? 'text-sceneConfig' :
                  scene.status === 'failed' ? 'text-danger' :
                  'text-gray-500'
                ]"
              >
                {{ getStatusText(scene.status) }}
              </span>
            </div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">{{ scene.status === 'failed' ? '失败原因:' : '成功率:' }}</span>
              <span class="font-medium">{{ scene.status === 'failed' ? scene.failureReason : scene.successRate }}</span>
            </div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">{{ scene.status === 'draft' ? '复杂度:' : '平均时长:' }}</span>
              <span>{{ scene.status === 'draft' ? scene.complexity : scene.averageDuration }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">{{ getTimeLabel(scene.status) }}:</span>
              <span>{{ getTimeValue(scene) }}</span>
            </div>
          </div>
          
          <div class="flex justify-between mt-3">
            <button 
              @click="handleLeftAction(scene)"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded hover:bg-gray-50 text-gray-700"
            >
              {{ getLeftButtonText(scene.status) }}
            </button>
            <button 
              @click="handleRightAction(scene)"
              :class="[
                'px-3 py-1.5 text-sm rounded',
                scene.status === 'running' ? 'bg-danger text-white hover:bg-opacity-90' :
                'bg-scene text-white hover:bg-opacity-90'
              ]"
            >
              {{ getRightButtonText(scene.status) }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Current Scene -->
    <div class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-clipboard-list text-scene mr-2"></i>
        <h2 class="text-lg font-medium">当前场景: {{ currentScene.name }}</h2>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
        <div class="space-y-3">
          <!-- Test Phases -->
          <div 
            v-for="(phase, index) in testPhases" 
            :key="phase.id"
            class="flex items-center"
          >
            <div class="w-1/6">
              <span class="font-medium">阶段 {{ index + 1 }}:</span>
            </div>
            <div class="w-3/6 flex items-center">
              <i 
                :class="[
                  'mr-2',
                  phase.status === 'completed' ? 'fa-solid fa-check-circle text-completed' :
                  phase.status === 'running' ? 'fa-solid fa-sync fa-spin text-sceneConfig' :
                  'fa-solid fa-hourglass-half text-gray-400'
                ]"
              ></i>
              <span>{{ phase.name }}</span>
            </div>
            <div class="w-1/6">
              <span>{{ phase.status === 'running' ? `进度: ${phase.progress}%` : phase.duration || '--' }}</span>
            </div>
            <div class="w-1/6">
              <span 
                :class="[
                  'font-medium',
                  phase.status === 'completed' ? 'text-completed' :
                  phase.status === 'running' ? 'text-sceneConfig' :
                  'text-gray-500'
                ]"
              >
                {{ getPhaseStatusIcon(phase.status) }}{{ getPhaseStatusText(phase.status) }}
              </span>
            </div>
          </div>

          <!-- Sub-phases for Phase 3 (if running) -->
          <template v-if="currentPhaseIndex === 2">
            <div 
              v-for="(subPhase, subIndex) in subPhases" 
              :key="subPhase.id"
              class="flex items-center ml-10"
            >
              <div class="w-1/6">
                <span class="text-sm">{{ subPhase.id }} {{ subPhase.name }}</span>
              </div>
              <div class="w-3/6 flex items-center">
                <i 
                  :class="[
                    'mr-2 text-sm',
                    subPhase.status === 'completed' ? 'fa-solid fa-check-circle text-completed' :
                    subPhase.status === 'running' ? 'fa-solid fa-sync fa-spin text-sceneConfig' :
                    'fa-solid fa-hourglass-half text-gray-400'
                  ]"
                ></i>
              </div>
              <div class="w-1/6">
                <span class="text-sm">{{ subPhase.status === 'running' ? `进度: ${subPhase.progress}%` : subPhase.duration || '--' }}</span>
              </div>
              <div class="w-1/6">
                <span 
                  :class="[
                    'font-medium text-sm',
                    subPhase.status === 'completed' ? 'text-completed' :
                    subPhase.status === 'running' ? 'text-sceneConfig' :
                    'text-gray-500'
                  ]"
                >
                  {{ getPhaseStatusIcon(subPhase.status) }}{{ getSubPhaseStatusText(subPhase.status) }}
                </span>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Monitoring and Analysis -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <!-- Real-time Monitoring -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-chart-line text-scene mr-2"></i>
          <h2 class="text-lg font-medium">实时监控</h2>
        </div>
        <div class="space-y-4">
          <!-- Current Task Progress -->
          <div>
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-bullseye text-scene mr-2"></i>
              <h3 class="font-medium">当前任务进度</h3>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
              <div 
                class="bg-scene h-2.5 rounded-full transition-all duration-500" 
                :style="`width: ${monitoring.currentProgress}%`"
              ></div>
            </div>
            <div class="text-right text-sm text-gray-600">{{ monitoring.currentProgress }}% - 预计剩余: {{ monitoring.remainingTime }}</div>
          </div>

          <!-- Device Status -->
          <div>
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-robot text-scene mr-2"></i>
              <h3 class="font-medium">设备运行状态:</h3>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div 
                v-for="device in deviceStatus" 
                :key="device.id"
                class="flex items-center"
              >
                <span 
                  :class="[
                    'h-2.5 w-2.5 rounded-full mr-2',
                    device.status === 'normal' ? 'bg-completed' :
                    device.status === 'warning' ? 'bg-warning' :
                    'bg-danger'
                  ]"
                ></span>
                <span class="text-sm">{{ device.name }}: {{ device.emoji }} {{ device.statusText }}</span>
              </div>
            </div>
          </div>

          <!-- Resource Usage -->
          <div>
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-microchip text-scene mr-2"></i>
              <h3 class="font-medium">资源使用:</h3>
            </div>
            <div class="flex justify-between mb-1">
              <span class="text-sm">CPU:</span>
              <span class="text-sm">{{ monitoring.cpuUsage }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5 mb-3">
              <div 
                class="bg-primary h-1.5 rounded-full transition-all duration-300" 
                :style="`width: ${monitoring.cpuUsage}%`"
              ></div>
            </div>
            <div class="flex justify-between mb-1">
              <span class="text-sm">内存:</span>
              <span class="text-sm">{{ monitoring.memoryUsage }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-1.5 mb-3">
              <div 
                class="bg-primary h-1.5 rounded-full transition-all duration-300" 
                :style="`width: ${monitoring.memoryUsage}%`"
              ></div>
            </div>
          </div>

          <div class="flex space-x-3">
            <button 
              @click="viewDetailedMonitoring"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded hover:bg-gray-50 text-gray-700 flex-1"
            >
              详细监控
            </button>
            <button 
              @click="runDiagnostics"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded hover:bg-gray-50 text-gray-700 flex-1"
            >
              诊断
            </button>
          </div>
        </div>
      </div>

      <!-- Performance Analysis -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-chart-bar text-scene mr-2"></i>
          <h2 class="text-lg font-medium">性能分析</h2>
        </div>
        <div class="space-y-4">
          <!-- Historical Statistics -->
          <div>
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-chart-pie text-scene mr-2"></i>
              <h3 class="font-medium">历史统计</h3>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">总测试:</span>
                <span class="text-sm font-medium">{{ performanceStats.totalTests }}次</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">成功:</span>
                <span class="text-sm font-medium text-completed">{{ performanceStats.successfulTests }}次 ({{ performanceStats.successRate }}%)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">失败:</span>
                <span class="text-sm font-medium text-danger">{{ performanceStats.failedTests }}次 ({{ performanceStats.failureRate }}%)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600">平均时长:</span>
                <span class="text-sm font-medium">{{ performanceStats.averageDuration }}分钟</span>
              </div>
            </div>
          </div>

          <!-- Common Failure Reasons -->
          <div>
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-exclamation-triangle text-warning mr-2"></i>
              <h3 class="font-medium">常见失败原因:</h3>
            </div>
            <div class="space-y-2">
              <div 
                v-for="reason in failureReasons" 
                :key="reason.name"
                class="flex justify-between"
              >
                <span class="text-sm">• {{ reason.name }}:</span>
                <span class="text-sm font-medium">{{ reason.percentage }}%</span>
              </div>
            </div>
          </div>

          <div class="flex space-x-3">
            <button 
              @click="getOptimizationSuggestions"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded hover:bg-gray-50 text-gray-700 flex-1"
            >
              优化建议
            </button>
            <button 
              @click="generateReport"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded hover:bg-gray-50 text-gray-700 flex-1"
            >
              报告
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Control and Fault Injection -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Scene Control -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5 col-span-2">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-gamepad text-scene mr-2"></i>
          <h2 class="text-lg font-medium">场景控制</h2>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <button 
            @click="pauseScene"
            :disabled="!isSceneRunning"
            class="px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 flex items-center justify-center disabled:opacity-50"
          >
            <i class="fa-solid fa-pause mr-2"></i>
            暂停场景
          </button>
          <button 
            @click="skipPhase"
            :disabled="!isSceneRunning"
            class="px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 flex items-center justify-center disabled:opacity-50"
          >
            <i class="fa-solid fa-forward-step mr-2"></i>
            跳过阶段
          </button>
          <button 
            @click="restartScene"
            class="px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 flex items-center justify-center"
          >
            <i class="fa-solid fa-redo mr-2"></i>
            重启场景
          </button>
          <button 
            @click="saveState"
            class="px-4 py-3 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 flex items-center justify-center"
          >
            <i class="fa-solid fa-save mr-2"></i>
            保存状态
          </button>
        </div>
      </div>

      <!-- Fault Injection -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-wrench text-scene mr-2"></i>
          <h2 class="text-lg font-medium">故障注入</h2>
        </div>
        <div class="space-y-3">
          <div 
            v-for="fault in faultInjections" 
            :key="fault.id"
            class="flex items-center"
          >
            <input 
              :id="fault.id"
              v-model="fault.enabled"
              type="checkbox" 
              class="rounded border-gray-300 text-scene focus:ring-scene mr-2"
            >
            <label :for="fault.id" class="text-sm">{{ fault.name }}</label>
          </div>
          <div class="flex space-x-3 mt-4">
            <button 
              @click="injectFaults"
              :disabled="!hasEnabledFaults"
              class="px-3 py-1.5 text-sm bg-danger text-white rounded hover:bg-opacity-90 flex-1 disabled:opacity-50"
            >
              注入故障
            </button>
            <button 
              @click="recoverFaults"
              class="px-3 py-1.5 text-sm border border-gray-200 rounded hover:bg-gray-50 text-gray-700 flex-1"
            >
              恢复
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 场景接口定义
interface Scene {
  id: string
  name: string
  status: 'passed' | 'running' | 'failed' | 'draft'
  successRate?: string
  averageDuration?: string
  lastTest?: string
  failureReason?: string
  complexity?: string
  createdTime?: string
  startTime?: string
}

// 测试阶段接口定义
interface TestPhase {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed'
  progress?: number
  duration?: string
}

// 子阶段接口定义
interface SubPhase {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed'
  progress?: number
  duration?: string
}

// 设备状态接口定义
interface DeviceStatus {
  id: string
  name: string
  status: 'normal' | 'warning' | 'error'
  emoji: string
  statusText: string
}

// 监控数据接口定义
interface MonitoringData {
  currentProgress: number
  remainingTime: string
  cpuUsage: number
  memoryUsage: number
}

// 性能统计接口定义
interface PerformanceStats {
  totalTests: number
  successfulTests: number
  failedTests: number
  successRate: number
  failureRate: number
  averageDuration: number
}

// 失败原因接口定义
interface FailureReason {
  name: string
  percentage: number
}

// 故障注入接口定义
interface FaultInjection {
  id: string
  name: string
  enabled: boolean
}

// 当前场景数据
const currentScene = ref<Scene>({
  id: 'factory-assembly',
  name: '工厂零件装配',
  status: 'running'
})

// 场景库数据
const sceneLibrary = ref<Scene[]>([
  {
    id: 'office-coffee',
    name: '办公室咖啡配送',
    status: 'passed',
    successRate: '92%',
    averageDuration: '8.5分钟',
    lastTest: '2小时前'
  },
  {
    id: 'factory-assembly',
    name: '工厂零件装配',
    status: 'running',
    startTime: '刚刚'
  },
  {
    id: 'warehouse-sorting',
    name: '仓库货物分拣',
    status: 'failed',
    successRate: '65%',
    failureReason: '视觉识别',
    lastTest: '昨天'
  },
  {
    id: 'custom-test',
    name: '自定义测试场景',
    status: 'draft',
    complexity: '待定',
    createdTime: '今天'
  }
])

// 测试阶段数据
const testPhases = ref<TestPhase[]>([
  { id: 'phase1', name: '系统初始化', status: 'completed', duration: '耗时: 15秒' },
  { id: 'phase2', name: '工作台准备', status: 'completed', duration: '耗时: 8秒' },
  { id: 'phase3', name: '零件识别', status: 'running', progress: 45 },
  { id: 'phase4', name: '机械臂抓取', status: 'pending' },
  { id: 'phase5', name: '精密装配', status: 'pending' },
  { id: 'phase6', name: '质量检验', status: 'pending' }
])

// 子阶段数据
const subPhases = ref<SubPhase[]>([
  { id: '3.1', name: '图像采集', status: 'completed', duration: '耗时: 2秒' },
  { id: '3.2', name: '目标检测', status: 'running', progress: 80 },
  { id: '3.3', name: '位置估计', status: 'pending' }
])

// 设备状态数据
const deviceStatus = ref<DeviceStatus[]>([
  { id: 'dual-arm', name: '双臂', status: 'normal', emoji: '🟢', statusText: '协调工作' },
  { id: 'chassis', name: '底盘', status: 'normal', emoji: '🟢', statusText: '定位稳定' },
  { id: 'vision', name: '视觉', status: 'warning', emoji: '🟡', statusText: '处理中' },
  { id: 'sensors', name: '传感器', status: 'normal', emoji: '🟢', statusText: '正常' }
])

// 监控数据
const monitoring = reactive<MonitoringData>({
  currentProgress: 35,
  remainingTime: '12分钟',
  cpuUsage: 68,
  memoryUsage: 45
})

// 性能统计数据
const performanceStats = reactive<PerformanceStats>({
  totalTests: 47,
  successfulTests: 38,
  failedTests: 9,
  successRate: 81,
  failureRate: 19,
  averageDuration: 9.2
})

// 失败原因数据
const failureReasons = ref<FailureReason[]>([
  { name: '视觉识别', percentage: 45 },
  { name: '机械精度', percentage: 30 },
  { name: '通信超时', percentage: 15 },
  { name: '其他', percentage: 10 }
])

// 故障注入数据
const faultInjections = ref<FaultInjection[]>([
  { id: 'network-delay', name: '网络延迟', enabled: false },
  { id: 'camera-occlusion', name: '相机遮挡', enabled: false },
  { id: 'arm-stuck', name: '机械臂卡顿', enabled: false },
  { id: 'sensor-error', name: '传感器错误', enabled: false }
])

// 状态变量
const isSceneRunning = ref(true)
const currentPhaseIndex = ref(2) // Current phase is 零件识别 (index 2)

// 定时器
let progressTimer: NodeJS.Timeout | null = null
let monitoringTimer: NodeJS.Timeout | null = null

// 计算属性
const canRunTest = computed(() => {
  return !isSceneRunning.value
})

const hasEnabledFaults = computed(() => {
  return faultInjections.value.some(fault => fault.enabled)
})

// 方法：获取状态文本
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'passed': '已通过',
    'running': '测试中',
    'failed': '失败',
    'draft': '草稿'
  }
  return statusMap[status] || '未知'
}

// 方法：获取时间标签
const getTimeLabel = (status: string): string => {
  const labelMap: Record<string, string> = {
    'passed': '最后测试',
    'running': '开始时间',
    'failed': '最后测试',
    'draft': '创建时间'
  }
  return labelMap[status] || '时间'
}

// 方法：获取时间值
const getTimeValue = (scene: Scene): string => {
  switch (scene.status) {
    case 'passed':
    case 'failed':
      return scene.lastTest || '--'
    case 'running':
      return scene.startTime || '--'
    case 'draft':
      return scene.createdTime || '--'
    default:
      return '--'
  }
}

// 方法：获取左侧按钮文本
const getLeftButtonText = (status: string): string => {
  const buttonMap: Record<string, string> = {
    'passed': '查看结果',
    'running': '查看进度',
    'failed': '查看日志',
    'draft': '编辑'
  }
  return buttonMap[status] || '查看'
}

// 方法：获取右侧按钮文本
const getRightButtonText = (status: string): string => {
  const buttonMap: Record<string, string> = {
    'passed': '重测',
    'running': '停止',
    'failed': '调试',
    'draft': '测试'
  }
  return buttonMap[status] || '操作'
}

// 方法：获取阶段状态图标
const getPhaseStatusIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    'completed': '✅',
    'running': '🔄',
    'pending': '⏳'
  }
  return iconMap[status] || '⏳'
}

// 方法：获取阶段状态文本
const getPhaseStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    'completed': '完成',
    'running': '进行中',
    'pending': '等待'
  }
  return textMap[status] || '等待'
}

// 方法：获取子阶段状态文本
const getSubPhaseStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    'completed': '完成',
    'running': '处理',
    'pending': '等待'
  }
  return textMap[status] || '等待'
}

// 方法：切换场景菜单
const toggleSceneMenu = (sceneId: string) => {
  ElMessage.info(`场景菜单: ${sceneId}`)
}

// 方法：处理左侧操作
const handleLeftAction = (scene: Scene) => {
  const actionMap: Record<string, string> = {
    'passed': '查看测试结果',
    'running': '查看当前进度',
    'failed': '查看失败日志',
    'draft': '编辑场景配置'
  }
  ElMessage.info(actionMap[scene.status] || '执行操作')
}

// 方法：处理右侧操作
const handleRightAction = (scene: Scene) => {
  if (scene.status === 'running') {
    stopScene(scene)
  } else {
    const actionMap: Record<string, string> = {
      'passed': '重新测试',
      'failed': '调试场景',
      'draft': '开始测试'
    }
    ElMessage.success(actionMap[scene.status] || '执行操作')
  }
}

// 方法：停止场景
const stopScene = (scene: Scene) => {
  scene.status = 'failed'
  isSceneRunning.value = false
  ElMessage.warning('场景测试已停止')
}

// 方法：创建新场景
const createNewScene = () => {
  ElMessage.info('新建场景功能开发中')
}

// 方法：运行测试
const runTest = () => {
  if (!canRunTest.value) return
  
  isSceneRunning.value = true
  currentScene.value.status = 'running'
  ElMessage.success('开始运行端到端测试')
  
  // 重置测试状态
  resetTestPhases()
  startProgressSimulation()
}

// 方法：重置测试阶段
const resetTestPhases = () => {
  testPhases.value.forEach((phase, index) => {
    if (index < 2) {
      phase.status = 'completed'
      phase.duration = `耗时: ${Math.floor(Math.random() * 20 + 8)}秒`
    } else if (index === 2) {
      phase.status = 'running'
      phase.progress = 45
    } else {
      phase.status = 'pending'
      phase.duration = undefined
    }
  })
  
  // 重置子阶段
  subPhases.value.forEach((subPhase, index) => {
    if (index === 0) {
      subPhase.status = 'completed'
      subPhase.duration = '耗时: 2秒'
    } else if (index === 1) {
      subPhase.status = 'running'
      subPhase.progress = 80
    } else {
      subPhase.status = 'pending'
      subPhase.duration = undefined
    }
  })
}

// 方法：开始进度模拟
const startProgressSimulation = () => {
  if (progressTimer) clearInterval(progressTimer)
  
  progressTimer = setInterval(() => {
    // 更新主进度
    if (monitoring.currentProgress < 100) {
      monitoring.currentProgress += Math.random() * 2
      const remainingMinutes = Math.max(0, Math.floor(12 - (monitoring.currentProgress/100) * 12))
      monitoring.remainingTime = `${remainingMinutes}分钟`
    }
    
    // 更新子阶段进度
    const runningSubPhase = subPhases.value.find(sub => sub.status === 'running')
    if (runningSubPhase && runningSubPhase.progress !== undefined) {
      runningSubPhase.progress += Math.random() * 3
      
      if (runningSubPhase.progress >= 100) {
        runningSubPhase.progress = 100
        runningSubPhase.status = 'completed'
        runningSubPhase.duration = `耗时: ${Math.floor(Math.random() * 10 + 3)}秒`
        
        // 开始下一个子阶段
        const currentIndex = subPhases.value.findIndex(sub => sub.id === runningSubPhase.id)
        if (currentIndex < subPhases.value.length - 1) {
          const nextSubPhase = subPhases.value[currentIndex + 1]
          nextSubPhase.status = 'running'
          nextSubPhase.progress = 0
        } else {
          // 子阶段全部完成，完成当前主阶段
          const currentMainPhase = testPhases.value[currentPhaseIndex.value]
          currentMainPhase.status = 'completed'
          currentMainPhase.duration = `耗时: ${Math.floor(Math.random() * 60 + 30)}秒`
          
          // 开始下一个主阶段
          if (currentPhaseIndex.value < testPhases.value.length - 1) {
            currentPhaseIndex.value++
            const nextPhase = testPhases.value[currentPhaseIndex.value]
            nextPhase.status = 'running'
            nextPhase.progress = 0
          } else {
            // 所有阶段完成
            isSceneRunning.value = false
            currentScene.value.status = 'passed'
            ElMessage.success('端到端测试完成')
            clearInterval(progressTimer!)
          }
        }
      }
    }
  }, 2000)
}

// 方法：开始监控数据更新
const startMonitoringUpdate = () => {
  monitoringTimer = setInterval(() => {
    // 模拟CPU和内存使用率变化
    monitoring.cpuUsage = Math.min(95, Math.max(50, monitoring.cpuUsage + (Math.random() > 0.5 ? 2 : -2)))
    monitoring.memoryUsage = Math.min(80, Math.max(40, monitoring.memoryUsage + (Math.random() > 0.5 ? 1 : -1)))
    
    // 模拟设备状态变化
    deviceStatus.value.forEach(device => {
      if (Math.random() < 0.05) { // 5%概率状态变化
        const statuses: Array<'normal' | 'warning' | 'error'> = ['normal', 'warning', 'error']
        const newStatus = statuses[Math.floor(Math.random() * statuses.length)]
        device.status = newStatus
        
        const statusTexts: Record<string, { emoji: string; text: string }> = {
          'normal': { emoji: '🟢', text: '正常' },
          'warning': { emoji: '🟡', text: '警告' },
          'error': { emoji: '🔴', text: '错误' }
        }
        
        const statusInfo = statusTexts[newStatus]
        device.emoji = statusInfo.emoji
        device.statusText = statusInfo.text
      }
    })
  }, 3000)
}

// 方法：暂停场景
const pauseScene = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  isSceneRunning.value = false
  ElMessage.warning('场景已暂停')
}

// 方法：跳过阶段
const skipPhase = () => {
  const currentPhase = testPhases.value[currentPhaseIndex.value]
  if (currentPhase && currentPhase.status === 'running') {
    currentPhase.status = 'completed'
    currentPhase.duration = '跳过'
    
    if (currentPhaseIndex.value < testPhases.value.length - 1) {
      currentPhaseIndex.value++
      const nextPhase = testPhases.value[currentPhaseIndex.value]
      nextPhase.status = 'running'
      nextPhase.progress = 0
    }
    
    ElMessage.success('阶段已跳过')
  }
}

// 方法：重启场景
const restartScene = () => {
  if (progressTimer) clearInterval(progressTimer)
  
  resetTestPhases()
  currentPhaseIndex.value = 2
  monitoring.currentProgress = 35
  monitoring.remainingTime = '12分钟'
  
  isSceneRunning.value = true
  startProgressSimulation()
  
  ElMessage.success('场景已重启')
}

// 方法：保存状态
const saveState = () => {
  ElMessage.success('场景状态已保存')
}

// 方法：注入故障
const injectFaults = () => {
  const enabledFaults = faultInjections.value.filter(fault => fault.enabled)
  ElMessage.warning(`已注入${enabledFaults.length}个故障`)
}

// 方法：恢复故障
const recoverFaults = () => {
  faultInjections.value.forEach(fault => {
    fault.enabled = false
  })
  ElMessage.success('所有故障已恢复')
}

// 方法：查看详细监控
const viewDetailedMonitoring = () => {
  ElMessage.info('详细监控功能开发中')
}

// 方法：运行诊断
const runDiagnostics = () => {
  ElMessage.info('系统诊断功能开发中')
}

// 方法：获取优化建议
const getOptimizationSuggestions = () => {
  ElMessage.info('优化建议功能开发中')
}

// 方法：生成报告
const generateReport = () => {
  ElMessage.success('性能报告生成成功')
}

// 生命周期
onMounted(() => {
  startProgressSimulation()
  startMonitoringUpdate()
})

onUnmounted(() => {
  if (progressTimer) clearInterval(progressTimer)
  if (monitoringTimer) clearInterval(monitoringTimer)
})
</script>

<style scoped>
/* 场景配色系统 */
.text-scene {
  color: #7C3AED;
}

.bg-scene {
  background-color: #7C3AED;
}

.text-sceneConfig {
  color: #409EFF;
}

.bg-sceneLight {
  background-color: #EDE9FE;
}

.text-completed {
  color: #67C23A;
}

.bg-completed {
  background-color: #67C23A;
}

.text-danger {
  color: #F56C6C;
}

.bg-danger {
  background-color: #F56C6C;
}

.text-warning {
  color: #E6A23C;
}

.bg-warning {
  background-color: #E6A23C;
}

.text-primary {
  color: #409EFF;
}

.bg-primary {
  background-color: #409EFF;
}

.text-secondary {
  color: #2c3e50;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  display: none;
}

html, body {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
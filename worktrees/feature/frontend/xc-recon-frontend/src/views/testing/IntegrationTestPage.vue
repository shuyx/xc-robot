<template>
  <div class="w-full h-[calc(100vh-100px)] overflow-auto bg-gray-50 p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">系统集成测试</h1>
      <p class="text-gray-600 mt-1">多设备协同功能的集成测试验证</p>
    </div>

    <!-- Test Scenarios Section -->
    <div class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-theater-masks text-purple-primary mr-2"></i>
        <h2 class="text-lg font-semibold">测试场景选择</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Scenario 1 -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
          <div class="p-4 bg-purple-light border-b border-gray-200">
            <div class="flex justify-between items-center">
              <div class="flex items-center">
                <i class="fa-solid fa-check-circle text-success mr-2"></i>
                <h3 class="font-medium">双臂协调抓取</h3>
              </div>
              <span class="text-xs px-2 py-1 bg-purple-primary text-white rounded-full">活跃</span>
            </div>
          </div>
          <div class="p-4">
            <div class="mb-3">
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-robot text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">设备: 双臂+底盘</span>
              </div>
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-chart-network text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">复杂度: 
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                </span>
              </div>
              <div class="flex items-center">
                <i class="fa-regular fa-clock text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">预估时间: 5分钟</span>
              </div>
            </div>
            <button 
              @click="startScenario('dual-arm')"
              :disabled="currentScenario.id === 'dual-arm'"
              class="w-full py-2 bg-purple-primary text-white rounded-md hover:bg-purple-700 transition disabled:opacity-50"
            >
              {{ currentScenario.id === 'dual-arm' ? '测试中' : '开始测试' }}
            </button>
          </div>
        </div>

        <!-- Scenario 2 -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
          <div class="p-4 bg-purple-light border-b border-gray-200">
            <div class="flex justify-between items-center">
              <h3 class="font-medium">移动抓取任务</h3>
            </div>
          </div>
          <div class="p-4">
            <div class="mb-3">
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-robot text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">设备: 双臂+底盘+视觉</span>
              </div>
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-chart-network text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">复杂度: 
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                </span>
              </div>
              <div class="flex items-center">
                <i class="fa-regular fa-clock text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">预估时间: 12分钟</span>
              </div>
            </div>
            <button 
              @click="startScenario('mobile-grasp')"
              :disabled="currentScenario.id === 'mobile-grasp'"
              class="w-full py-2 bg-purple-primary text-white rounded-md hover:bg-purple-700 transition disabled:opacity-50"
            >
              {{ currentScenario.id === 'mobile-grasp' ? '测试中' : '开始测试' }}
            </button>
          </div>
        </div>

        <!-- Scenario 3 -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
          <div class="p-4 bg-purple-light border-b border-gray-200">
            <div class="flex justify-between items-center">
              <h3 class="font-medium">视觉引导定位</h3>
            </div>
          </div>
          <div class="p-4">
            <div class="mb-3">
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-camera text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">设备: 相机+底盘</span>
              </div>
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-chart-network text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">复杂度: 
                  <i class="fa-solid fa-star text-yellow-400"></i>
                  <i class="fa-solid fa-star text-yellow-400"></i>
                </span>
              </div>
              <div class="flex items-center">
                <i class="fa-regular fa-clock text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">预估时间: 8分钟</span>
              </div>
            </div>
            <button 
              @click="startScenario('vision-guided')"
              :disabled="currentScenario.id === 'vision-guided'"
              class="w-full py-2 bg-purple-primary text-white rounded-md hover:bg-purple-700 transition disabled:opacity-50"
            >
              {{ currentScenario.id === 'vision-guided' ? '测试中' : '开始测试' }}
            </button>
          </div>
        </div>

        <!-- Scenario 4 -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
          <div class="p-4 bg-purple-light border-b border-gray-200">
            <div class="flex justify-between items-center">
              <h3 class="font-medium">自定义测试场景</h3>
            </div>
          </div>
          <div class="p-4">
            <div class="mb-3">
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-cog text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">设备: 可选配置</span>
              </div>
              <div class="flex items-center mb-1">
                <i class="fa-solid fa-sliders-h text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">复杂度: 可调节</span>
              </div>
              <div class="flex items-center">
                <i class="fa-regular fa-clock text-gray-500 mr-2 w-5"></i>
                <span class="text-sm">预估时间: 待计算</span>
              </div>
            </div>
            <button 
              @click="createCustomScenario"
              class="w-full py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition"
            >
              创建场景
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Current Test Section -->
    <div class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>
        <h2 class="text-lg font-semibold">当前测试: {{ currentScenario.name }}</h2>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
        <div class="space-y-3">
          <!-- Test Steps -->
          <div 
            v-for="(step, index) in testSteps" 
            :key="step.id"
            class="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0"
          >
            <div class="flex items-center">
              <span class="w-16 text-sm font-medium">步骤 {{ index + 1 }}:</span>
              <div class="flex items-center">
                <i 
                  :class="[
                    'mr-2',
                    step.status === 'completed' ? 'fa-solid fa-check-circle text-success' :
                    step.status === 'running' ? 'fa-solid fa-sync fa-spin text-primary' :
                    'fa-regular fa-clock text-gray-400'
                  ]"
                ></i>
                <span>{{ step.name }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="flex items-center" v-if="step.status === 'running' && step.progress !== undefined">
                <span class="text-sm text-gray-600 mr-2">进度:</span>
                <div class="w-24 bg-gray-200 rounded-full h-2.5 mr-2">
                  <div 
                    class="bg-primary h-2.5 rounded-full transition-all duration-300" 
                    :style="`width: ${step.progress}%`"
                  ></div>
                </div>
                <span class="text-sm font-medium">{{ step.progress }}%</span>
              </div>
              <div class="flex items-center" v-else-if="step.status === 'completed'">
                <span class="text-sm text-gray-600 mr-2">耗时:</span>
                <span class="text-sm font-medium">{{ step.duration }}</span>
              </div>
              <div class="flex items-center" v-else>
                <span class="text-sm text-gray-600 mr-2">进度:</span>
                <span class="text-sm font-medium">--</span>
              </div>
              <div class="flex items-center">
                <span class="text-sm text-gray-600 mr-2">状态:</span>
                <span 
                  :class="[
                    'text-sm font-medium',
                    step.status === 'completed' ? 'text-success' :
                    step.status === 'running' ? 'text-primary' :
                    'text-gray-400'
                  ]"
                >
                  {{ 
                    step.status === 'completed' ? '完成' :
                    step.status === 'running' ? '执行中' :
                    '等待'
                  }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Monitoring and Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <!-- Device Monitoring -->
      <div>
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-chart-line text-primary mr-2"></i>
          <h2 class="text-lg font-semibold">设备状态监控</h2>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm h-full">
          <div class="space-y-3 mb-4">
            <div 
              v-for="device in devices" 
              :key="device.id"
              class="flex items-center justify-between"
            >
              <div class="flex items-center">
                <i :class="`fa-solid ${device.icon} text-gray-600 mr-2`"></i>
                <span>{{ device.name }}:</span>
              </div>
              <div class="flex items-center">
                <span 
                  :class="[
                    'w-3 h-3 rounded-full mr-2',
                    device.status === 'normal' ? 'bg-success' :
                    device.status === 'warning' ? 'bg-warning' :
                    device.status === 'error' ? 'bg-danger' :
                    'bg-gray-400'
                  ]"
                ></span>
                <span 
                  :class="[
                    'text-sm font-medium',
                    device.status === 'normal' ? 'text-success' :
                    device.status === 'warning' ? 'text-warning' :
                    device.status === 'error' ? 'text-danger' :
                    'text-gray-400'
                  ]"
                >
                  {{ 
                    device.status === 'normal' ? '正常' :
                    device.status === 'warning' ? '警告' :
                    device.status === 'error' ? '错误' :
                    '未知'
                  }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="border-t border-gray-200 pt-3 mt-3">
            <h3 class="font-medium mb-2 flex items-center">
              <i class="fa-solid fa-satellite-dish text-gray-600 mr-2"></i>
              通信延迟:
            </h3>
            <ul class="space-y-1 pl-6">
              <li 
                v-for="latency in latencies" 
                :key="latency.name"
                class="text-sm flex items-center"
              >
                <span class="w-1.5 h-1.5 bg-gray-500 rounded-full mr-2"></span>
                {{ latency.name }}: {{ latency.value }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Test Statistics -->
      <div>
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-chart-pie text-primary mr-2"></i>
          <h2 class="text-lg font-semibold">测试统计</h2>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm h-full">
          <div class="grid grid-cols-2 gap-3 mb-4">
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">总测试场景</div>
              <div class="text-2xl font-semibold mt-1">{{ statistics.totalScenarios }}个</div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">通过场景</div>
              <div class="text-2xl font-semibold text-success mt-1">{{ statistics.passedScenarios }}个</div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">失败场景</div>
              <div class="text-2xl font-semibold text-danger mt-1">{{ statistics.failedScenarios }}个</div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-sm text-gray-600">进行中</div>
              <div class="text-2xl font-semibold text-primary mt-1">{{ statistics.runningScenarios }}个</div>
            </div>
          </div>
          
          <div class="space-y-3 mb-4">
            <div class="flex items-center justify-between">
              <span class="text-sm">平均成功率:</span>
              <span class="font-medium">{{ statistics.averageSuccessRate }}%</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm">平均耗时:</span>
              <span class="font-medium">{{ statistics.averageDuration }}分钟</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm">最长耗时:</span>
              <span class="font-medium">{{ statistics.maxDuration }}分钟</span>
            </div>
          </div>
          
          <button 
            @click="viewFailureLogs"
            class="w-full py-2 bg-danger text-white rounded-md hover:bg-red-500 transition flex items-center justify-center"
          >
            <i class="fa-solid fa-file-alt mr-2"></i>
            查看失败日志
          </button>
        </div>
      </div>
    </div>

    <!-- Control and Analysis Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Test Control -->
      <div>
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-gamepad text-primary mr-2"></i>
          <h2 class="text-lg font-semibold">测试控制</h2>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <button 
              @click="pauseTest"
              :disabled="!isTestRunning"
              class="py-3 bg-warning text-white rounded-md hover:bg-yellow-500 transition flex items-center justify-center disabled:opacity-50"
            >
              <i class="fa-solid fa-pause mr-2"></i>
              暂停测试
            </button>
            <button 
              @click="skipStep"
              :disabled="!isTestRunning"
              class="py-3 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition flex items-center justify-center disabled:opacity-50"
            >
              <i class="fa-solid fa-step-forward mr-2"></i>
              跳过步骤
            </button>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <button 
              @click="resetTest"
              class="py-3 bg-danger text-white rounded-md hover:bg-red-500 transition flex items-center justify-center"
            >
              <i class="fa-solid fa-redo-alt mr-2"></i>
              重置测试
            </button>
            <button 
              @click="saveLogs"
              class="py-3 bg-success text-white rounded-md hover:bg-green-600 transition flex items-center justify-center"
            >
              <i class="fa-solid fa-save mr-2"></i>
              保存日志
            </button>
          </div>
        </div>
      </div>

      <!-- Result Analysis -->
      <div>
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-clipboard-check text-primary mr-2"></i>
          <h2 class="text-lg font-semibold">结果分析</h2>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <h3 class="font-medium mb-3">性能瓶颈分析:</h3>
          <ul class="space-y-2 mb-4">
            <li 
              v-for="analysis in performanceAnalysis" 
              :key="analysis.item"
              class="flex items-center"
            >
              <span 
                :class="[
                  'w-1.5 h-1.5 rounded-full mr-2',
                  analysis.status === 'slow' ? 'bg-danger' :
                  analysis.status === 'good' ? 'bg-success' :
                  analysis.status === 'excellent' ? 'bg-success' :
                  'bg-warning'
                ]"
              ></span>
              <span class="text-sm">{{ analysis.item }}: </span>
              <span 
                :class="[
                  'text-sm font-medium ml-1',
                  analysis.status === 'slow' ? 'text-danger' :
                  analysis.status === 'good' ? 'text-success' :
                  analysis.status === 'excellent' ? 'text-success' :
                  'text-warning'
                ]"
              >
                {{ analysis.label }}
              </span>
            </li>
          </ul>
          <button 
            @click="viewDetailedReport"
            class="w-full py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition flex items-center justify-center"
          >
            <i class="fa-solid fa-chart-bar mr-2"></i>
            详细分析报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 测试场景接口定义
interface TestScenario {
  id: string
  name: string
  devices: string[]
  complexity: number
  estimatedTime: number
  status: 'idle' | 'running' | 'completed' | 'failed'
}

// 测试步骤接口定义
interface TestStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number
  duration?: string
}

// 设备状态接口定义
interface Device {
  id: string
  name: string
  icon: string
  status: 'normal' | 'warning' | 'error' | 'unknown'
}

// 通信延迟接口定义
interface Latency {
  name: string
  value: string
}

// 测试统计接口定义
interface TestStatistics {
  totalScenarios: number
  passedScenarios: number
  failedScenarios: number
  runningScenarios: number
  averageSuccessRate: number
  averageDuration: number
  maxDuration: number
}

// 性能分析接口定义
interface PerformanceAnalysis {
  item: string
  status: 'slow' | 'good' | 'excellent' | 'warning'
  label: string
}

// 当前测试场景
const currentScenario = ref<TestScenario>({
  id: 'dual-arm',
  name: '双臂协调抓取',
  devices: ['FR3右臂', 'FR3左臂', 'Hermes底盘'],
  complexity: 3,
  estimatedTime: 5,
  status: 'running'
})

// 测试步骤数据
const testSteps = ref<TestStep[]>([
  { id: 'step1', name: '设备初始化', status: 'completed', duration: '12秒' },
  { id: 'step2', name: '视觉目标检测', status: 'completed', duration: '8秒' },
  { id: 'step3', name: '左臂移动就位', status: 'running', progress: 70 },
  { id: 'step4', name: '右臂协调配合', status: 'pending' },
  { id: 'step5', name: '双臂协调抓取', status: 'pending' },
  { id: 'step6', name: '抓取结果验证', status: 'pending' }
])

// 设备状态数据
const devices = ref<Device[]>([
  { id: 'fr3-right', name: 'FR3右臂', icon: 'fa-robot', status: 'normal' },
  { id: 'fr3-left', name: 'FR3左臂', icon: 'fa-robot', status: 'normal' },
  { id: 'hermes', name: 'Hermes', icon: 'fa-truck', status: 'normal' },
  { id: 'vision', name: '视觉', icon: 'fa-eye', status: 'normal' }
])

// 通信延迟数据
const latencies = ref<Latency[]>([
  { name: '右臂-左臂', value: '5ms' },
  { name: '双臂-底盘', value: '8ms' },
  { name: '视觉-控制', value: '12ms' }
])

// 测试统计数据
const statistics = reactive<TestStatistics>({
  totalScenarios: 15,
  passedScenarios: 12,
  failedScenarios: 2,
  runningScenarios: 1,
  averageSuccessRate: 80,
  averageDuration: 8.5,
  maxDuration: 15
})

// 性能分析数据
const performanceAnalysis = ref<PerformanceAnalysis[]>([
  { item: '视觉处理', status: 'slow', label: '慢' },
  { item: '机械臂精度', status: 'good', label: '良好' },
  { item: '通信同步', status: 'excellent', label: '优秀' }
])

// 计算属性
const isTestRunning = ref(true)

// 定时器
let progressTimer: NodeJS.Timeout | null = null
let monitoringTimer: NodeJS.Timeout | null = null

// 方法：开始测试场景
const startScenario = (scenarioId: string) => {
  if (currentScenario.value.id === scenarioId) return
  
  // 重置测试状态
  resetTestSteps()
  
  // 更新当前场景
  const scenarioNames: Record<string, string> = {
    'dual-arm': '双臂协调抓取',
    'mobile-grasp': '移动抓取任务',
    'vision-guided': '视觉引导定位'
  }
  
  currentScenario.value = {
    id: scenarioId,
    name: scenarioNames[scenarioId] || '未知场景',
    devices: ['FR3右臂', 'FR3左臂', 'Hermes底盘'],
    complexity: scenarioId === 'mobile-grasp' ? 5 : scenarioId === 'vision-guided' ? 2 : 3,
    estimatedTime: scenarioId === 'mobile-grasp' ? 12 : scenarioId === 'vision-guided' ? 8 : 5,
    status: 'running'
  }
  
  isTestRunning.value = true
  ElMessage.success(`开始执行${currentScenario.value.name}测试`)
  
  // 开始进度模拟
  startProgressSimulation()
}

// 方法：重置测试步骤
const resetTestSteps = () => {
  testSteps.value.forEach((step, index) => {
    if (index < 2) {
      step.status = 'completed'
      step.duration = `${Math.floor(Math.random() * 20 + 8)}秒`
      step.progress = undefined
    } else if (index === 2) {
      step.status = 'running'
      step.progress = 70
      step.duration = undefined
    } else {
      step.status = 'pending'
      step.progress = undefined
      step.duration = undefined
    }
  })
}

// 方法：开始进度模拟
const startProgressSimulation = () => {
  if (progressTimer) clearInterval(progressTimer)
  
  progressTimer = setInterval(() => {
    const runningStep = testSteps.value.find(step => step.status === 'running')
    if (runningStep && runningStep.progress !== undefined) {
      runningStep.progress += Math.random() * 5
      
      if (runningStep.progress >= 100) {
        runningStep.progress = 100
        runningStep.status = 'completed'
        runningStep.duration = `${Math.floor(Math.random() * 30 + 15)}秒`
        
        // 开始下一步
        const currentIndex = testSteps.value.findIndex(step => step.id === runningStep.id)
        if (currentIndex < testSteps.value.length - 1) {
          const nextStep = testSteps.value[currentIndex + 1]
          nextStep.status = 'running'
          nextStep.progress = 0
        } else {
          // 所有步骤完成
          isTestRunning.value = false
          ElMessage.success('测试场景执行完成')
          clearInterval(progressTimer!)
        }
      }
    }
  }, 1000)
}

// 方法：创建自定义场景
const createCustomScenario = () => {
  ElMessage.info('自定义场景创建功能开发中')
}

// 方法：暂停测试
const pauseTest = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  isTestRunning.value = false
  ElMessage.warning('测试已暂停')
}

// 方法：跳过步骤
const skipStep = () => {
  const runningStep = testSteps.value.find(step => step.status === 'running')
  if (runningStep) {
    runningStep.status = 'completed'
    runningStep.duration = '跳过'
    runningStep.progress = undefined
    
    const currentIndex = testSteps.value.findIndex(step => step.id === runningStep.id)
    if (currentIndex < testSteps.value.length - 1) {
      const nextStep = testSteps.value[currentIndex + 1]
      nextStep.status = 'running'
      nextStep.progress = 0
    } else {
      isTestRunning.value = false
      ElMessage.success('测试场景执行完成')
    }
    
    ElMessage.success('步骤已跳过')
  }
}

// 方法：重置测试
const resetTest = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  
  resetTestSteps()
  isTestRunning.value = true
  startProgressSimulation()
  
  ElMessage.success('测试已重置')
}

// 方法：保存日志
const saveLogs = () => {
  ElMessage.success('测试日志已保存')
}

// 方法：查看失败日志
const viewFailureLogs = () => {
  ElMessage.info('查看失败日志功能开发中')
}

// 方法：查看详细报告
const viewDetailedReport = () => {
  ElMessage.info('详细分析报告功能开发中')
}

// 方法：开始监控数据更新
const startMonitoringUpdate = () => {
  monitoringTimer = setInterval(() => {
    // 模拟设备状态变化
    devices.value.forEach(device => {
      if (Math.random() < 0.1) { // 10%概率状态变化
        const statuses: Array<'normal' | 'warning' | 'error'> = ['normal', 'warning', 'error']
        device.status = statuses[Math.floor(Math.random() * statuses.length)]
      }
    })
    
    // 模拟延迟变化
    latencies.value.forEach(latency => {
      const baseLatency = parseInt(latency.value)
      const variation = Math.floor(Math.random() * 5) - 2
      latency.value = `${Math.max(1, baseLatency + variation)}ms`
    })
  }, 2000)
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
.text-purple-primary {
  color: #531DAB;
}

.bg-purple-primary {
  background-color: #531DAB;
}

.bg-purple-light {
  background-color: #F0E6FF;
}

.hover\:bg-purple-700:hover {
  background-color: #391085;
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
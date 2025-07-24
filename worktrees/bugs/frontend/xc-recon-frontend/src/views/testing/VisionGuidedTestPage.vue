<template>
  <div class="w-full h-[calc(100vh-100px)] bg-gray-100 p-4 overflow-auto">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">视觉引导功能测试</h1>
      <p class="text-gray-600">视觉感知与机器人动作协调测试</p>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-2 gap-4">
      <!-- Video Preview Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-video text-primary mr-2"></i>
            <span class="font-medium">视觉预览区</span>
          </div>
          <div class="flex items-center">
            <button 
              @click="switchCamera"
              class="btn btn-secondary text-sm"
            >
              <i class="fa-solid fa-camera mr-1"></i>
              {{ currentCamera.name }}
              <i class="fa-solid fa-chevron-down ml-1"></i>
            </button>
          </div>
        </div>
        <div class="card-body p-0 relative">
          <div class="bg-secondary h-[280px] w-full relative">
            <div class="absolute inset-0 flex items-center justify-center">
              <img 
                class="w-full h-full object-cover" 
                :src="visionFeed.imageUrl" 
                :alt="visionFeed.description"
              >
            </div>
            <!-- Target Box Overlay -->
            <div 
              v-for="target in detectedTargets.filter(t => t.visible)"
              :key="target.id"
              :style="{
                left: target.position.x + '%',
                top: target.position.y + '%',
                width: target.position.width + 'px',
                height: target.position.height + 'px'
              }"
              class="absolute border-2 border-primary rounded-md flex flex-col items-center justify-center"
            >
              <div class="bg-black bg-opacity-60 text-white px-2 py-1 rounded text-sm">
                <i class="fa-solid fa-cube mr-1"></i>
                {{ target.name }}
              </div>
              <div class="bg-black bg-opacity-60 text-white px-2 py-1 rounded text-sm mt-1">
                <i class="fa-solid fa-chart-simple mr-1"></i>
                置信度: {{ target.confidence }}%
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <button 
            @click="capturePhoto"
            class="btn btn-secondary"
          >
            <i class="fa-solid fa-camera mr-1"></i>
            拍照
          </button>
          <button 
            @click="toggleRecording"
            class="btn btn-secondary"
          >
            <i :class="isRecording ? 'fa-solid fa-stop' : 'fa-solid fa-record-vinyl'" class="mr-1"></i>
            {{ isRecording ? '停止' : '录制' }}
          </button>
          <button 
            @click="redetectTargets"
            class="btn btn-primary"
          >
            <i class="fa-solid fa-rotate mr-1"></i>
            重新检测
          </button>
        </div>
      </div>

      <!-- Target Information Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-bullseye text-primary mr-2"></i>
            <span class="font-medium">引导目标区</span>
          </div>
        </div>
        <div class="card-body h-[280px] overflow-y-auto">
          <h3 class="font-medium mb-3">
            <i class="fa-solid fa-bullseye text-primary mr-1"></i>
            当前目标
          </h3>
          
          <!-- Target Objects -->
          <div 
            v-for="target in targets"
            :key="target.id"
            :class="[
              'border rounded-md p-3 mb-3',
              target.status === 'locked' ? 'border-locked' :
              target.status === 'detecting' ? 'border-detecting' :
              'border-gray-200'
            ]"
          >
            <div class="flex justify-between items-center mb-2">
              <div class="font-medium">
                <i class="fa-solid fa-cube mr-1"></i>
                {{ target.name }}
              </div>
              <div>
                <span class="text-sm">
                  状态: 
                  <span 
                    :class="[
                      'status-dot',
                      target.status === 'locked' ? 'status-success' :
                      target.status === 'detecting' ? 'status-warning' :
                      'status-unknown'
                    ]"
                  ></span>
                  {{ 
                    target.status === 'locked' ? '已锁定' :
                    target.status === 'detecting' ? '检测中' :
                    '未检测'
                  }}
                </span>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>位置: {{ target.position || '--' }}</div>
              <div>角度: {{ target.angle || '--' }}</div>
              <div>深度: {{ target.depth || '--' }}</div>
              <div>尺寸: {{ target.size || '--' }}</div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <button 
            @click="selectTarget"
            class="btn btn-secondary"
          >
            <i class="fa-solid fa-list mr-1"></i>
            选择目标
          </button>
          <button 
            @click="addTarget"
            class="btn btn-primary"
          >
            <i class="fa-solid fa-plus mr-1"></i>
            添加目标
          </button>
        </div>
      </div>

      <!-- Test Items Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-flask text-primary mr-2"></i>
            <span class="font-medium">测试项目</span>
          </div>
        </div>
        <div class="card-body">
          <div class="space-y-3">
            <div 
              v-for="test in testItems"
              :key="test.id"
              class="flex justify-between items-center"
            >
              <div class="flex items-center">
                <i 
                  :class="[
                    'mr-2',
                    test.status === 'passed' ? 'fa-solid fa-check-circle text-locked' :
                    test.status === 'running' ? 'fa-solid fa-sync text-detecting animate-spin' :
                    'fa-solid fa-hourglass-half text-gray-400'
                  ]"
                ></i>
                <span>{{ test.name }}</span>
              </div>
              <div class="flex items-center">
                <span class="text-sm mr-2">
                  状态: {{ 
                    test.status === 'passed' ? '通过' :
                    test.status === 'running' ? '进行中' :
                    '待测试'
                  }}
                </span>
                <span 
                  :class="[
                    'text-sm',
                    test.status === 'passed' ? 'text-precision' :
                    test.status === 'running' ? 'text-detecting' :
                    'text-gray-400'
                  ]"
                >
                  {{ test.result || '--' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Robot Status Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-robot text-primary mr-2"></i>
            <span class="font-medium">机械臂状态</span>
          </div>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 gap-4">
            <!-- Target Position -->
            <div>
              <h3 class="font-medium mb-2">
                <i class="fa-solid fa-bullseye text-primary mr-1"></i>
                目标位置:
              </h3>
              <div class="grid grid-cols-3 gap-2 text-sm">
                <div>X: {{ robotStatus.targetPosition.x }}mm</div>
                <div>Y: {{ robotStatus.targetPosition.y }}mm</div>
                <div>Z: {{ robotStatus.targetPosition.z }}mm</div>
              </div>
            </div>
            
            <!-- Current Position -->
            <div>
              <h3 class="font-medium mb-2">
                <i class="fa-solid fa-robot text-primary mr-1"></i>
                当前位置:
              </h3>
              <div class="grid grid-cols-3 gap-2 text-sm">
                <div>X: {{ robotStatus.currentPosition.x }}mm</div>
                <div>Y: {{ robotStatus.currentPosition.y }}mm</div>
                <div>Z: {{ robotStatus.currentPosition.z }}mm</div>
              </div>
            </div>
            
            <!-- Position Error -->
            <div>
              <h3 class="font-medium mb-2">
                <i class="fa-solid fa-ruler-combined text-primary mr-1"></i>
                位置误差:
              </h3>
              <div class="grid grid-cols-3 gap-2 text-sm">
                <div>ΔX: {{ robotStatus.positionError.x }}mm</div>
                <div>ΔY: {{ robotStatus.positionError.y }}mm</div>
                <div>ΔZ: {{ robotStatus.positionError.z }}mm</div>
              </div>
            </div>
            
            <!-- Precision -->
            <div>
              <h3 class="font-medium mb-2">
                <i class="fa-solid fa-chart-pie text-primary mr-1"></i>
                精度: <span class="text-precision">{{ robotStatus.precision }}%</span>
              </h3>
              <div class="progress-bar mt-1 mb-3">
                <div 
                  class="progress-bar-fill bg-precision" 
                  :style="`width: ${robotStatus.precision}%`"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <button 
            @click="guideMovement"
            class="btn btn-secondary"
          >
            <i class="fa-solid fa-hand-pointer mr-1"></i>
            引导移动
          </button>
          <button 
            @click="verifyPosition"
            class="btn btn-primary"
          >
            <i class="fa-solid fa-check mr-1"></i>
            验证
          </button>
        </div>
      </div>

      <!-- Precision Analysis Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-line text-primary mr-2"></i>
            <span class="font-medium">引导精度分析</span>
          </div>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <h3 class="font-medium mb-2">
                <i class="fa-solid fa-ruler text-primary mr-1"></i>
                定位误差统计
              </h3>
              <div class="space-y-2 text-sm">
                <div 
                  v-for="error in precisionAnalysis.errors"
                  :key="error.axis"
                  class="flex justify-between"
                >
                  <span>{{ error.axis }}:</span>
                  <span>{{ error.value }}</span>
                </div>
              </div>
            </div>
            <div>
              <h3 class="font-medium mb-2">
                <i class="fa-solid fa-chart-bar text-primary mr-1"></i>
                平均精度: {{ precisionAnalysis.averagePrecision }}%
              </h3>
              <div ref="precisionChart" class="h-[120px]"></div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <button 
            @click="viewDetailedData"
            class="btn btn-secondary"
          >
            <i class="fa-solid fa-table mr-1"></i>
            详细数据
          </button>
          <button 
            @click="exportData"
            class="btn btn-primary"
          >
            <i class="fa-solid fa-file-export mr-1"></i>
            导出
          </button>
        </div>
      </div>

      <!-- Test Results Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-pie text-primary mr-2"></i>
            <span class="font-medium">测试结果</span>
          </div>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <div class="flex justify-between">
                <span>测试通过:</span>
                <span class="text-locked">{{ testResults.passed }}/{{ testResults.total }}</span>
              </div>
              <div class="flex justify-between">
                <span>平均精度:</span>
                <span class="text-precision">{{ testResults.averagePrecision }}%</span>
              </div>
              <div class="flex justify-between">
                <span>最佳精度:</span>
                <span class="text-precision">{{ testResults.bestPrecision }}%</span>
              </div>
              <div class="flex justify-between">
                <span>建议:</span>
                <span class="text-detecting">{{ testResults.recommendation }}</span>
              </div>
            </div>
            <div ref="resultsChart" class="h-[120px]"></div>
          </div>
        </div>
      </div>

      <!-- Test Controls Area -->
      <div class="card">
        <div class="card-header">
          <div class="flex items-center">
            <i class="fa-solid fa-gamepad text-primary mr-2"></i>
            <span class="font-medium">测试控制</span>
          </div>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-2 gap-4">
            <button 
              @click="startGuidance"
              :disabled="isGuidanceRunning"
              class="btn btn-primary h-12 disabled:opacity-50"
            >
              <i class="fa-solid fa-play mr-1"></i>
              {{ isGuidanceRunning ? '引导中...' : '开始引导' }}
            </button>
            <button 
              @click="redetectTargets"
              class="btn btn-secondary h-12"
            >
              <i class="fa-solid fa-rotate mr-1"></i>
              重新检测
            </button>
            <button 
              @click="saveResults"
              class="btn btn-secondary h-12"
            >
              <i class="fa-solid fa-save mr-1"></i>
              保存结果
            </button>
            <button 
              @click="generateReport"
              class="btn btn-secondary h-12"
            >
              <i class="fa-solid fa-file-pdf mr-1"></i>
              生成报告
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

// 相机设备接口定义
interface Camera {
  id: string
  name: string
  type: 'tof' | '2d' | 'fisheye'
}

// 视觉目标接口定义
interface Target {
  id: string
  name: string
  status: 'locked' | 'detecting' | 'undetected'
  position?: string
  angle?: string
  depth?: string
  size?: string
}

// 检测目标接口定义
interface DetectedTarget {
  id: string
  name: string
  confidence: number
  visible: boolean
  position: {
    x: number
    y: number
    width: number
    height: number
  }
}

// 测试项目接口定义
interface TestItem {
  id: string
  name: string
  status: 'passed' | 'running' | 'pending'
  result?: string
}

// 机器人状态接口定义
interface RobotStatus {
  targetPosition: { x: number; y: number; z: number }
  currentPosition: { x: number; y: number; z: number }
  positionError: { x: string; y: string; z: string }
  precision: number
}

// 精度分析接口定义
interface PrecisionAnalysis {
  errors: Array<{ axis: string; value: string }>
  averagePrecision: number
}

// 测试结果接口定义
interface TestResults {
  passed: number
  total: number
  averagePrecision: number
  bestPrecision: number
  recommendation: string
}

// 视觉图像数据接口定义
interface VisionFeed {
  imageUrl: string
  description: string
}

// 当前相机
const currentCamera = ref<Camera>({
  id: 'tof',
  name: 'TOF相机',
  type: 'tof'
})

// 可用相机列表
const cameras: Camera[] = [
  { id: 'tof', name: 'TOF相机', type: 'tof' },
  { id: '2d-1', name: '2D相机1', type: '2d' },
  { id: '2d-2', name: '2D相机2', type: '2d' },
  { id: 'fisheye', name: '鱼眼相机', type: 'fisheye' }
]

// 视觉图像数据
const visionFeed = ref<VisionFeed>({
  imageUrl: 'https://storage.googleapis.com/uxpilot-auth.appspot.com/bc76d3d038-3f212f6cf5f98fd80eea.png',
  description: 'robotic vision system camera feed showing objects with bounding boxes and detection confidence'
})

// 检测目标数据
const detectedTargets = ref<DetectedTarget[]>([
  {
    id: 'object-a',
    name: '物体A',
    confidence: 85,
    visible: true,
    position: { x: 25, y: 30, width: 150, height: 120 }
  }
])

// 目标数据
const targets = ref<Target[]>([
  {
    id: 'object-a',
    name: '物体A',
    status: 'locked',
    position: '(250, 180)',
    angle: '15°',
    depth: '0.65m',
    size: '120×85mm'
  },
  {
    id: 'object-b',
    name: '物体B',
    status: 'detecting',
    position: '(380, 220)',
    angle: '-8°',
    depth: '0.72m',
    size: '95×70mm'
  },
  {
    id: 'object-c',
    name: '物体C',
    status: 'undetected'
  }
])

// 测试项目数据
const testItems = ref<TestItem[]>([
  { id: 'calibration', name: '手眼标定验证', status: 'passed', result: '8.5mm' },
  { id: 'detection', name: '目标检测精度', status: 'passed', result: '95%' },
  { id: 'guidance', name: '定位引导测试', status: 'running', result: '3/5' },
  { id: 'grasping', name: '抓取精度验证', status: 'pending' },
  { id: 'multi-target', name: '多目标识别', status: 'pending' },
  { id: 'lighting', name: '光照适应测试', status: 'pending' }
])

// 机器人状态数据
const robotStatus = reactive<RobotStatus>({
  targetPosition: { x: 250, y: 180, z: 650 },
  currentPosition: { x: 248, y: 182, z: 648 },
  positionError: { x: '-2', y: '+2', z: '-2' },
  precision: 92
})

// 精度分析数据
const precisionAnalysis = reactive<PrecisionAnalysis>({
  errors: [
    { axis: 'X轴误差', value: '±2.3mm' },
    { axis: 'Y轴误差', value: '±1.8mm' },
    { axis: 'Z轴误差', value: '±3.1mm' },
    { axis: '角度误差', value: '±1.2°' }
  ],
  averagePrecision: 87
})

// 测试结果数据
const testResults = reactive<TestResults>({
  passed: 3,
  total: 6,
  averagePrecision: 89,
  bestPrecision: 96,
  recommendation: '光照优化'
})

// 状态变量
const isRecording = ref(false)
const isGuidanceRunning = ref(false)

// 图表引用
const precisionChart = ref<HTMLElement>()
const resultsChart = ref<HTMLElement>()

// 定时器
let statusUpdateTimer: NodeJS.Timeout | null = null

// 方法：切换相机
const switchCamera = () => {
  const currentIndex = cameras.findIndex(c => c.id === currentCamera.value.id)
  const nextIndex = (currentIndex + 1) % cameras.length
  currentCamera.value = cameras[nextIndex]
  ElMessage.success(`已切换到${currentCamera.value.name}`)
}

// 方法：拍照
const capturePhoto = () => {
  ElMessage.success('照片已保存')
}

// 方法：切换录制
const toggleRecording = () => {
  isRecording.value = !isRecording.value
  ElMessage.success(isRecording.value ? '开始录制' : '录制已停止')
}

// 方法：重新检测目标
const redetectTargets = () => {
  // 模拟检测过程
  targets.value.forEach(target => {
    if (target.status === 'undetected') {
      target.status = 'detecting'
    }
  })
  
  // 2秒后完成检测
  setTimeout(() => {
    targets.value.forEach(target => {
      if (target.status === 'detecting') {
        target.status = Math.random() > 0.5 ? 'locked' : 'undetected'
        if (target.status === 'locked') {
          target.position = `(${Math.floor(Math.random() * 400 + 100)}, ${Math.floor(Math.random() * 300 + 100)})`
          target.angle = `${Math.floor(Math.random() * 30 - 15)}°`
          target.depth = `${(Math.random() * 0.5 + 0.5).toFixed(2)}m`
          target.size = `${Math.floor(Math.random() * 50 + 80)}×${Math.floor(Math.random() * 40 + 60)}mm`
        }
      }
    })
    ElMessage.success('目标检测完成')
  }, 2000)
  
  ElMessage.info('正在重新检测目标...')
}

// 方法：选择目标
const selectTarget = () => {
  ElMessage.info('目标选择功能开发中')
}

// 方法：添加目标
const addTarget = () => {
  ElMessage.info('添加目标功能开发中')
}

// 方法：引导移动
const guideMovement = () => {
  isGuidanceRunning.value = true
  ElMessage.success('开始引导机械臂移动')
  
  // 模拟移动过程
  setTimeout(() => {
    robotStatus.currentPosition.x += Math.random() * 4 - 2
    robotStatus.currentPosition.y += Math.random() * 4 - 2
    robotStatus.currentPosition.z += Math.random() * 4 - 2
    
    // 重新计算误差
    robotStatus.positionError.x = (robotStatus.targetPosition.x - robotStatus.currentPosition.x).toFixed(0)
    robotStatus.positionError.y = (robotStatus.targetPosition.y - robotStatus.currentPosition.y).toFixed(0)
    robotStatus.positionError.z = (robotStatus.targetPosition.z - robotStatus.currentPosition.z).toFixed(0)
    
    // 更新精度
    const totalError = Math.abs(parseFloat(robotStatus.positionError.x)) + 
                      Math.abs(parseFloat(robotStatus.positionError.y)) + 
                      Math.abs(parseFloat(robotStatus.positionError.z))
    robotStatus.precision = Math.max(80, Math.floor(100 - totalError))
    
    isGuidanceRunning.value = false
    ElMessage.success('引导移动完成')
  }, 3000)
}

// 方法：验证位置
const verifyPosition = () => {
  ElMessage.success('位置验证通过')
}

// 方法：查看详细数据
const viewDetailedData = () => {
  ElMessage.info('详细数据功能开发中')
}

// 方法：导出数据
const exportData = () => {
  ElMessage.success('数据导出成功')
}

// 方法：开始引导
const startGuidance = () => {
  if (isGuidanceRunning.value) return
  
  isGuidanceRunning.value = true
  
  // 更新测试项目状态
  const guidanceTest = testItems.value.find(t => t.id === 'guidance')
  if (guidanceTest) {
    guidanceTest.status = 'running'
    guidanceTest.result = '0/5'
  }
  
  ElMessage.success('开始视觉引导测试')
  
  // 模拟引导过程
  let progress = 0
  const guidanceTimer = setInterval(() => {
    progress++
    if (guidanceTest) {
      guidanceTest.result = `${progress}/5`
    }
    
    if (progress >= 5) {
      clearInterval(guidanceTimer)
      if (guidanceTest) {
        guidanceTest.status = 'passed'
        guidanceTest.result = '5/5'
      }
      isGuidanceRunning.value = false
      ElMessage.success('视觉引导测试完成')
    }
  }, 1000)
}

// 方法：保存结果
const saveResults = () => {
  ElMessage.success('测试结果已保存')
}

// 方法：生成报告
const generateReport = () => {
  ElMessage.success('测试报告生成成功')
}

// 方法：创建精度分析图表
const createPrecisionChart = () => {
  if (!precisionChart.value) return
  
  // 使用简单的Canvas实现或者集成图表库
  const canvas = document.createElement('canvas')
  canvas.width = precisionChart.value.clientWidth
  canvas.height = 120
  precisionChart.value.appendChild(canvas)
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 绘制简单的柱状图
  const data = [90, 94, 82, 85]
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  const barWidth = canvas.width / data.length - 10
  
  data.forEach((value, index) => {
    const x = index * (barWidth + 10) + 5
    const height = (value / 100) * (canvas.height - 20)
    const y = canvas.height - height - 10
    
    ctx.fillStyle = colors[index]
    ctx.fillRect(x, y, barWidth, height)
  })
}

// 方法：创建结果图表
const createResultsChart = () => {
  if (!resultsChart.value) return
  
  const canvas = document.createElement('canvas')
  canvas.width = resultsChart.value.clientWidth
  canvas.height = 120
  resultsChart.value.appendChild(canvas)
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 绘制简单的饼图
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) - 10
  
  const data = [
    { value: 3, color: '#00A870', label: '通过' },
    { value: 1, color: '#E6A23C', label: '进行中' },
    { value: 2, color: '#909399', label: '待测试' }
  ]
  
  let currentAngle = 0
  const total = data.reduce((sum, item) => sum + item.value, 0)
  
  data.forEach(item => {
    const sliceAngle = (item.value / total) * 2 * Math.PI
    
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.closePath()
    ctx.fillStyle = item.color
    ctx.fill()
    
    currentAngle += sliceAngle
  })
}

// 方法：开始状态更新
const startStatusUpdate = () => {
  statusUpdateTimer = setInterval(() => {
    // 模拟数据变化
    if (Math.random() < 0.1) { // 10%概率更新
      robotStatus.precision += Math.random() * 2 - 1
      robotStatus.precision = Math.max(80, Math.min(98, robotStatus.precision))
    }
  }, 2000)
}

// 生命周期
onMounted(async () => {
  await nextTick()
  createPrecisionChart()
  createResultsChart()
  startStatusUpdate()
})

onUnmounted(() => {
  if (statusUpdateTimer) clearInterval(statusUpdateTimer)
})
</script>

<style scoped>
/* 自定义样式匹配设计文档 */
.text-primary {
  color: #9254DE;
}

.text-secondary {
  color: #2c3e50;
}

.text-locked {
  color: #00A870;
}

.text-detecting {
  color: #E6A23C;
}

.text-precision {
  color: #409EFF;
}

.border-locked {
  border-color: #00A870;
}

.border-detecting {
  border-color: #E6A23C;
}

.bg-secondary {
  background-color: #F4F0FF;
}

.bg-precision {
  background-color: #409EFF;
}

.progress-bar {
  height: 8px;
  border-radius: 4px;
  background-color: #E5E7EB;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: white;
}

.card-header {
  padding: 12px 16px;
  border-bottom: 1px solid #EBEEF5;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-body {
  padding: 16px;
}

.card-footer {
  padding: 12px 16px;
  border-top: 1px solid #EBEEF5;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn {
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: none;
}

.btn-primary {
  background-color: #9254DE;
  color: white;
}

.btn-primary:hover {
  background-color: #8048C8;
}

.btn-secondary {
  background-color: #F4F0FF;
  color: #9254DE;
  border: 1px solid #9254DE;
}

.btn-secondary:hover {
  background-color: #EAE0FF;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}

.status-success {
  background-color: #00A870;
}

.status-warning {
  background-color: #E6A23C;
}

.status-error {
  background-color: #F56C6C;
}

.status-info {
  background-color: #409EFF;
}

.status-unknown {
  background-color: #909399;
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
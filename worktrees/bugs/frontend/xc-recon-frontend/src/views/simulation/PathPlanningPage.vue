<template>
  <div id="main-content" class="w-full h-[calc(100vh-100px)] overflow-auto p-6">
    <!-- Page Header -->
    <div id="page-header" class="mb-6">
      <div class="flex items-center text-sm text-gray-500 mb-2">
        <span>主菜单</span>
        <i class="fa-solid fa-chevron-right mx-2 text-xs"></i>
        <span>仿真规划</span>
        <i class="fa-solid fa-chevron-right mx-2 text-xs"></i>
        <span class="text-primary">路径规划</span>
      </div>
      <h1 class="text-2xl font-bold text-secondary">智能路径规划</h1>
      <p class="text-gray-600">机器人运动轨迹规划与优化</p>
    </div>

    <!-- Planning Configuration Section -->
    <div id="planning-config" class="mb-6">
      <div class="flex items-center mb-3">
        <i class="fa-solid fa-bullseye text-primary mr-2"></i>
        <h2 class="text-lg font-semibold">规划配置</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Algorithm Selection Card -->
        <div id="algorithm-card" class="bg-white rounded-lg shadow-sm p-4">
          <div class="flex justify-between items-center mb-3">
            <div class="flex items-center">
              <i class="fa-solid fa-rocket text-primary mr-2"></i>
              <h3 class="font-medium">规划算法选择</h3>
            </div>
            <button 
              @click="showAlgorithmInfo"
              class="text-xs text-primary hover:text-blue-700 flex items-center"
            >
              <i class="fa-solid fa-info-circle mr-1"></i>
              算法说明
            </button>
          </div>
          <div class="space-y-2">
            <div 
              v-for="algorithm in algorithms" 
              :key="algorithm.id"
              @click="selectAlgorithm(algorithm.id)"
              class="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
            >
              <div :class="[
                'w-4 h-4 rounded-full mr-2 flex items-center justify-center',
                selectedAlgorithm === algorithm.id 
                  ? 'bg-primary' 
                  : 'border border-gray-300'
              ]">
                <div 
                  v-if="selectedAlgorithm === algorithm.id"
                  class="w-2 h-2 bg-white rounded-full"
                ></div>
              </div>
              <span>{{ algorithm.name }}</span>
              <span 
                v-if="algorithm.recommended" 
                class="text-xs text-success ml-1"
              >(推荐)</span>
            </div>
          </div>
        </div>

        <!-- Constraint Settings Card -->
        <div id="constraint-card" class="bg-white rounded-lg shadow-sm p-4">
          <div class="flex justify-between items-center mb-3">
            <div class="flex items-center">
              <i class="fa-solid fa-gear text-primary mr-2"></i>
              <h3 class="font-medium">约束条件设置</h3>
            </div>
            <button 
              @click="showAdvancedSettings"
              class="text-xs text-primary hover:text-blue-700 flex items-center"
            >
              <i class="fa-solid fa-sliders mr-1"></i>
              高级设置
            </button>
          </div>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label class="text-sm">最大速度:</label>
              <div class="flex items-center">
                <input 
                  type="number" 
                  v-model.number="constraints.maxVelocity"
                  step="0.1" 
                  min="0" 
                  max="10" 
                  class="w-16 text-center border border-gray-300 rounded px-2 py-1 text-sm"
                >
                <span class="ml-1 text-sm">m/s</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <label class="text-sm">最大加速度:</label>
              <div class="flex items-center">
                <input 
                  type="number" 
                  v-model.number="constraints.maxAcceleration"
                  step="0.1" 
                  min="0" 
                  max="10" 
                  class="w-16 text-center border border-gray-300 rounded px-2 py-1 text-sm"
                >
                <span class="ml-1 text-sm">m/s²</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <label class="text-sm">关节限位:</label>
              <div 
                @click="constraints.jointLimits = !constraints.jointLimits"
                class="flex items-center cursor-pointer"
              >
                <div :class="[
                  'w-4 h-4 border rounded flex items-center justify-center mr-1',
                  constraints.jointLimits 
                    ? 'border-primary bg-primary' 
                    : 'border-gray-300'
                ]">
                  <i 
                    v-if="constraints.jointLimits"
                    class="fa-solid fa-check text-white text-xs"
                  ></i>
                </div>
                <span class="text-sm">启用</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <label class="text-sm">碰撞距离:</label>
              <div class="flex items-center">
                <input 
                  type="number" 
                  v-model.number="constraints.collisionDistance"
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-16 text-center border border-gray-300 rounded px-2 py-1 text-sm"
                >
                <span class="ml-1 text-sm">m</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Path Planning Area Section -->
    <div id="planning-area" class="mb-6">
      <div class="flex items-center mb-3">
        <i class="fa-solid fa-map text-primary mr-2"></i>
        <h2 class="text-lg font-semibold">路径规划区域</h2>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4">
        <div class="text-center font-medium mb-2">工作空间俯视图</div>
        <div id="map-container" class="relative h-[300px] bg-mapBg rounded-lg mb-3">
          <!-- Start Point -->
          <div 
            :style="`left: ${startPoint.x}px; top: ${startPoint.y}px`"
            class="absolute flex flex-col items-center"
          >
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-primary">
              <i class="fa-solid fa-robot"></i>
            </div>
            <div class="text-xs mt-1 bg-white px-1 rounded shadow-sm">
              起点 ({{ Math.round(startPoint.x) }},{{ Math.round(startPoint.y) }})
            </div>
          </div>
          
          <!-- End Point -->
          <div 
            :style="`left: ${endPoint.x}px; top: ${endPoint.y}px`"
            class="absolute flex flex-col items-center"
          >
            <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center text-danger">
              <i class="fa-solid fa-bullseye"></i>
            </div>
            <div class="text-xs mt-1 bg-white px-1 rounded shadow-sm">
              终点 ({{ Math.round(endPoint.x) }},{{ Math.round(endPoint.y) }})
            </div>
          </div>
          
          <!-- Obstacles -->
          <div 
            v-for="obstacle in obstacles" 
            :key="obstacle.id"
            :style="`left: ${obstacle.x}px; top: ${obstacle.y}px`"
            class="absolute"
          >
            <div :style="`width: ${obstacle.width}px; height: ${obstacle.height}px`" 
                 class="bg-gray-300 rounded-md flex items-center justify-center">
              <span class="text-xs">{{ obstacle.name }}</span>
            </div>
          </div>
          
          <!-- Environment Objects -->
          <div class="absolute left-[100px] top-[150px]">
            <div class="text-2xl text-secondary">
              <i class="fa-solid fa-home"></i>
            </div>
          </div>
          
          <div class="absolute left-[200px] top-[150px]">
            <div class="text-xl text-secondary">
              <i class="fa-solid fa-box"></i>
            </div>
          </div>
          
          <div class="absolute left-[150px] top-[400px]">
            <div class="text-xl text-secondary">
              <i class="fa-solid fa-box"></i>
            </div>
          </div>
          
          <!-- Path Line -->
          <svg 
            v-if="pathPlanned"
            class="absolute top-0 left-0 w-full h-full" 
            style="z-index: 5;"
          >
            <path 
              :d="pathData" 
              stroke="#00A870" 
              stroke-width="3" 
              fill="none" 
              stroke-dasharray="5,5"
            ></path>
          </svg>
        </div>
        
        <div class="flex flex-wrap gap-2">
          <button 
            @click="setStartPoint"
            class="bg-white border border-primary text-primary hover:bg-primary hover:text-white px-3 py-1.5 rounded text-sm transition-colors flex items-center"
          >
            <i class="fa-solid fa-location-crosshairs mr-1"></i>
            设置起点
          </button>
          <button 
            @click="setEndPoint"
            class="bg-white border border-primary text-primary hover:bg-primary hover:text-white px-3 py-1.5 rounded text-sm transition-colors flex items-center"
          >
            <i class="fa-solid fa-flag-checkered mr-1"></i>
            设置终点
          </button>
          <button 
            @click="addObstacle"
            class="bg-white border border-primary text-primary hover:bg-primary hover:text-white px-3 py-1.5 rounded text-sm transition-colors flex items-center"
          >
            <i class="fa-solid fa-square mr-1"></i>
            添加障碍
          </button>
          <button 
            @click="planPath"
            :disabled="isPlanning"
            class="bg-primary text-white hover:bg-blue-600 px-3 py-1.5 rounded text-sm transition-colors flex items-center"
          >
            <i class="fa-solid fa-route mr-1"></i>
            {{ isPlanning ? '规划中...' : '规划路径' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Analysis and Control Section -->
    <div id="analysis-control" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <!-- Path Analysis Card -->
      <div id="path-analysis" class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-line text-primary mr-2"></i>
            <h3 class="font-medium">路径分析</h3>
          </div>
          <div>
            <button 
              @click="showDetailedReport"
              class="text-xs text-primary hover:text-blue-700 mr-2"
            >详细报告</button>
            <button 
              @click="show3DPreview"
              class="text-xs text-primary hover:text-blue-700"
            >3D预览</button>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="flex items-center">
            <i class="fa-solid fa-ruler text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">路径长度</div>
              <div class="font-medium">{{ pathAnalysis.length }}m</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-regular fa-clock text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">预计时间</div>
              <div class="font-medium">{{ pathAnalysis.estimatedTime }}秒</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-rotate text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">路径点数</div>
              <div class="font-medium">{{ pathAnalysis.pointCount }}个</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-chart-simple text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">平滑度</div>
              <div class="font-medium">{{ pathAnalysis.smoothness }}%</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-bolt text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">最大速度</div>
              <div class="font-medium">{{ pathAnalysis.maxVelocity }}m/s</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-ban text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">碰撞检测</div>
              <div :class="[
                'font-medium',
                pathAnalysis.collisionStatus === '通过' ? 'text-success' : 'text-danger'
              ]">{{ pathAnalysis.collisionStatus }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Planning Control Card -->
      <div id="planning-control" class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex items-center mb-3">
          <i class="fa-solid fa-gamepad text-primary mr-2"></i>
          <h3 class="font-medium">规划控制</h3>
        </div>
        <div class="mb-4">
          <div class="text-sm mb-1">规划状态:</div>
          <div class="flex items-center">
            <div :class="[
              'w-3 h-3 rounded-full mr-2',
              planningStatus.status === 'success' ? 'bg-success' :
              planningStatus.status === 'failed' ? 'bg-danger' : 'bg-warning'
            ]"></div>
            <span>{{ planningStatus.message }}</span>
          </div>
        </div>
        <div class="mb-4">
          <div class="text-sm mb-1">计算进度:</div>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mb-1">
            <div 
              class="bg-primary h-2.5 rounded-full transition-all duration-300" 
              :style="`width: ${planningProgress}%`"
            ></div>
          </div>
          <div class="text-right text-xs text-gray-500">{{ planningProgress }}%</div>
        </div>
        <div class="mb-4">
          <div class="flex items-center">
            <i class="fa-regular fa-clock text-gray-500 mr-2"></i>
            <div>
              <div class="text-xs text-gray-500">计算耗时</div>
              <div class="font-medium">{{ planningTime }}秒</div>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <button 
            @click="replan"
            :disabled="isPlanning"
            class="bg-white border border-primary text-primary hover:bg-primary hover:text-white px-3 py-1.5 rounded text-sm transition-colors flex items-center justify-center"
          >
            <i class="fa-solid fa-redo mr-1"></i>
            重新规划
          </button>
          <button 
            @click="optimizePath"
            :disabled="!pathPlanned || isPlanning"
            class="bg-white border border-primary text-primary hover:bg-primary hover:text-white px-3 py-1.5 rounded text-sm transition-colors flex items-center justify-center"
          >
            <i class="fa-solid fa-wand-magic-sparkles mr-1"></i>
            优化
          </button>
          <button 
            @click="simulateValidation"
            :disabled="!pathPlanned"
            class="bg-white border border-primary text-primary hover:bg-primary hover:text-white px-3 py-1.5 rounded text-sm transition-colors flex items-center justify-center"
          >
            <i class="fa-solid fa-vr-cardboard mr-1"></i>
            仿真验证
          </button>
          <button 
            @click="executePath"
            :disabled="!pathPlanned || planningStatus.status !== 'success'"
            class="bg-success text-white hover:bg-green-700 px-3 py-1.5 rounded text-sm transition-colors flex items-center justify-center"
          >
            <i class="fa-solid fa-play mr-1"></i>
            执行
          </button>
        </div>
      </div>
    </div>

    <!-- Path Adjustment and Performance Comparison -->
    <div id="adjustment-comparison" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <!-- Path Adjustment Card -->
      <div id="path-adjustment" class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-sliders text-primary mr-2"></i>
            <h3 class="font-medium">路径调整</h3>
          </div>
          <div>
            <button 
              @click="applyAdjustments"
              :disabled="!pathPlanned"
              class="text-xs text-primary hover:text-blue-700 mr-2"
            >应用调整</button>
            <button 
              @click="resetAdjustments"
              class="text-xs text-gray-500 hover:text-gray-700"
            >恢复</button>
          </div>
        </div>
        <div class="mb-4">
          <div class="text-sm font-medium mb-2">路径微调:</div>
          <div class="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label class="text-xs text-gray-500 block mb-1">起点偏移: X</label>
              <input 
                type="number" 
                v-model.number="adjustments.startOffset.x"
                class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              >
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-1">Y</label>
              <input 
                type="number" 
                v-model.number="adjustments.startOffset.y"
                class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              >
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-500 block mb-1">终点偏移: X</label>
              <input 
                type="number" 
                v-model.number="adjustments.endOffset.x"
                class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              >
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-1">Y</label>
              <input 
                type="number" 
                v-model.number="adjustments.endOffset.y"
                class="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              >
            </div>
          </div>
        </div>
        <div>
          <div class="text-sm font-medium mb-2">优化选项:</div>
          <div class="space-y-2">
            <div 
              v-for="option in optimizationOptions" 
              :key="option.id"
              @click="option.enabled = !option.enabled"
              class="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
            >
              <div :class="[
                'w-4 h-4 border rounded flex items-center justify-center mr-2',
                option.enabled 
                  ? 'border-primary bg-primary' 
                  : 'border-gray-300'
              ]">
                <i 
                  v-if="option.enabled"
                  class="fa-solid fa-check text-white text-xs"
                ></i>
              </div>
              <span class="text-sm">{{ option.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Comparison Card -->
      <div id="performance-comparison" class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-bar text-primary mr-2"></i>
            <h3 class="font-medium">性能对比</h3>
          </div>
          <div>
            <button 
              @click="switchAlgorithm"
              class="text-xs text-primary hover:text-blue-700 mr-2"
            >切换算法</button>
            <button 
              @click="compareAlgorithms"
              class="text-xs text-primary hover:text-blue-700"
            >对比</button>
          </div>
        </div>
        <div id="algorithm-comparison-chart" class="h-[180px] mb-4 bg-gray-50 rounded flex items-center justify-center">
          <div class="text-gray-500 text-sm">
            <i class="fa-solid fa-chart-bar mr-2"></i>
            算法性能对比图表
          </div>
        </div>
        <div class="text-sm">
          <div class="font-medium mb-2">算法性能对比:</div>
          <ul class="space-y-1">
            <li 
              v-for="(result, index) in algorithmResults" 
              :key="result.name"
              class="flex items-center"
            >
              <div :class="[
                'w-2 h-2 rounded-full mr-2',
                index === 0 ? 'bg-primary' :
                index === 1 ? 'bg-warning' : 'bg-danger'
              ]"></div>
              <span>{{ result.name }}: {{ result.time }}s {{ result.length }}m</span>
            </li>
          </ul>
          <div class="mt-3">
            <span class="text-sm">推荐: </span>
            <span class="text-primary font-medium">{{ recommendedAlgorithm }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 算法接口定义
interface Algorithm {
  id: string
  name: string
  recommended?: boolean
}

interface Point {
  x: number
  y: number
}

interface Obstacle {
  id: string
  name: string
  x: number
  y: number
  width: number
  height: number
}

interface Constraints {
  maxVelocity: number
  maxAcceleration: number
  jointLimits: boolean
  collisionDistance: number
}

interface PathAnalysis {
  length: string
  estimatedTime: string
  pointCount: string
  smoothness: string
  maxVelocity: string
  collisionStatus: string
}

interface PlanningStatus {
  status: 'idle' | 'planning' | 'success' | 'failed'
  message: string
}

interface Adjustments {
  startOffset: Point
  endOffset: Point
}

interface OptimizationOption {
  id: string
  name: string
  enabled: boolean
}

interface AlgorithmResult {
  name: string
  time: string
  length: string
}

// 响应式数据
const selectedAlgorithm = ref('astar')
const isPlanning = ref(false)
const pathPlanned = ref(false)
const planningProgress = ref(100)
const planningTime = ref('0.8')

// 算法选项
const algorithms = ref<Algorithm[]>([
  { id: 'astar', name: 'A*算法', recommended: true },
  { id: 'rrt', name: 'RRT算法' },
  { id: 'prm', name: 'PRM算法' },
  { id: 'potential', name: '人工势场法' }
])

// 约束条件
const constraints = reactive<Constraints>({
  maxVelocity: 2.0,
  maxAcceleration: 1.5,
  jointLimits: true,
  collisionDistance: 0.1
})

// 起点和终点
const startPoint = reactive<Point>({ x: 400, y: 200 })
const endPoint = reactive<Point>({ x: 600, y: 400 })

// 障碍物
const obstacles = ref<Obstacle[]>([
  { id: 'obs1', name: '障碍物', x: 350, y: 300, width: 80, height: 64 }
])

// 路径数据
const pathData = ref('M408,208 C450,220 480,280 500,320 C520,360 550,380 600,400')

// 路径分析
const pathAnalysis = reactive<PathAnalysis>({
  length: '1.85',
  estimatedTime: '3.2',
  pointCount: '156',
  smoothness: '92',
  maxVelocity: '1.8',
  collisionStatus: '通过'
})

// 规划状态
const planningStatus = reactive<PlanningStatus>({
  status: 'success',
  message: '规划成功'
})

// 路径调整
const adjustments = reactive<Adjustments>({
  startOffset: { x: 0, y: 0 },
  endOffset: { x: 0, y: 0 }
})

// 优化选项
const optimizationOptions = ref<OptimizationOption[]>([
  { id: 'smooth', name: '路径平滑', enabled: true },
  { id: 'velocity', name: '速度优化', enabled: true },
  { id: 'energy', name: '能耗最小', enabled: false }
])

// 算法结果对比
const algorithmResults = ref<AlgorithmResult[]>([
  { name: 'A*', time: '0.8', length: '1.85' },
  { name: 'RRT', time: '1.2', length: '2.1' },
  { name: 'PRM', time: '2.1', length: '1.92' }
])

// 推荐算法
const recommendedAlgorithm = computed(() => {
  const selected = algorithms.value.find(a => a.id === selectedAlgorithm.value)
  return selected?.name || 'A*算法'
})

// 算法选择
const selectAlgorithm = (algorithmId: string) => {
  selectedAlgorithm.value = algorithmId
  const algorithm = algorithms.value.find(a => a.id === algorithmId)
  ElMessage.info(`已选择${algorithm?.name}`)
}

// 显示算法信息
const showAlgorithmInfo = () => {
  ElMessage.info('显示算法详细说明')
}

// 显示高级设置
const showAdvancedSettings = () => {
  ElMessage.info('打开高级设置面板')
}

// 地图操作
const setStartPoint = () => {
  ElMessage.info('点击地图设置起点位置')
}

const setEndPoint = () => {
  ElMessage.info('点击地图设置终点位置')
}

const addObstacle = () => {
  const newObstacle: Obstacle = {
    id: `obs${obstacles.value.length + 1}`,
    name: `障碍物${obstacles.value.length + 1}`,
    x: Math.random() * 400 + 200,
    y: Math.random() * 200 + 150,
    width: 60,
    height: 50
  }
  obstacles.value.push(newObstacle)
  ElMessage.success('已添加新障碍物')
}

// 路径规划
const planPath = async () => {
  if (isPlanning.value) return
  
  isPlanning.value = true
  planningProgress.value = 0
  planningStatus.status = 'planning'
  planningStatus.message = '规划中...'
  
  // 模拟规划过程
  const interval = setInterval(() => {
    planningProgress.value += 10
    if (planningProgress.value >= 100) {
      clearInterval(interval)
      isPlanning.value = false
      pathPlanned.value = true
      planningStatus.status = 'success'
      planningStatus.message = '规划成功'
      planningTime.value = (Math.random() * 1 + 0.5).toFixed(1)
      ElMessage.success('路径规划完成')
    }
  }, 100)
}

// 重新规划
const replan = () => {
  planPath()
}

// 路径优化
const optimizePath = () => {
  if (!pathPlanned.value) return
  
  ElMessage.success('路径已优化')
  pathAnalysis.smoothness = '96'
  pathAnalysis.length = '1.76'
  pathAnalysis.estimatedTime = '3.0'
}

// 仿真验证
const simulateValidation = () => {
  ElMessage.info('启动仿真验证')
}

// 执行路径
const executePath = () => {
  ElMessage.success('开始执行路径')
}

// 路径分析操作
const showDetailedReport = () => {
  ElMessage.info('显示详细路径分析报告')
}

const show3DPreview = () => {
  ElMessage.info('打开3D路径预览')
}

// 路径调整
const applyAdjustments = () => {
  if (!pathPlanned.value) return
  
  // 应用偏移量
  startPoint.x += adjustments.startOffset.x
  startPoint.y += adjustments.startOffset.y
  endPoint.x += adjustments.endOffset.x
  endPoint.y += adjustments.endOffset.y
  
  ElMessage.success('路径调整已应用')
  
  // 重新规划
  planPath()
}

const resetAdjustments = () => {
  adjustments.startOffset.x = 0
  adjustments.startOffset.y = 0
  adjustments.endOffset.x = 0
  adjustments.endOffset.y = 0
  ElMessage.info('调整参数已重置')
}

// 性能对比
const switchAlgorithm = () => {
  ElMessage.info('切换对比算法')
}

const compareAlgorithms = () => {
  ElMessage.info('开始算法性能对比')
}
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

.bg-success {
  background-color: #00A870;
}

.bg-warning {
  background-color: #E6A23C;
}

.bg-danger {
  background-color: #F56C6C;
}

/* 路径规划专用配色 */
.text-pathColor {
  color: #00A870;
}

.bg-mapBg {
  background-color: #E0F8FF;
}

.text-planningColor {
  color: #0EA5E9;
}

/* 按钮禁用状态 */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 路径线条动画 */
svg path {
  animation: dash 2s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

/* 地图容器 */
#map-container {
  position: relative;
  overflow: hidden;
}

/* 悬停效果 */
.hover\\:bg-gray-50:hover {
  background-color: #f9fafb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid.md\\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  #map-container {
    height: 250px;
  }
  
  .flex.flex-wrap.gap-2 {
    flex-direction: column;
  }
  
  .flex.flex-wrap.gap-2 > button {
    width: 100%;
    justify-content: center;
  }
  
  .grid.grid-cols-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .text-xs {
    font-size: 0.75rem;
  }
  
  .absolute.flex.flex-col.items-center .text-xs {
    font-size: 0.625rem;
  }
}
</style>
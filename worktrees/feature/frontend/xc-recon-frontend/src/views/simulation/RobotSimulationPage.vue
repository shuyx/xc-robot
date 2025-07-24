<template>
  <div id="robot-simulation" class="w-full h-[calc(100vh-100px)] p-4">
    <!-- Page Header -->
    <div class="mb-4">
      <h1 class="text-2xl font-bold text-secondary">机器人仿真系统</h1>
      <p class="text-gray-600">3D虚拟环境下的机器人建模与仿真</p>
    </div>
    
    <!-- Main Content -->
    <div class="grid grid-cols-3 gap-4 h-[calc(100%-4rem)]">
      <!-- Left Column: 3D View + Target Setup -->
      <div class="col-span-2 flex flex-col gap-4">
        <!-- 3D Simulation Window -->
        <div id="simulation-window" class="card h-[60%]">
          <div class="card-header bg-info bg-opacity-10">
            <div class="flex items-center">
              <i class="fa-solid fa-cube text-info mr-2"></i>
              <h2 class="text-lg font-semibold">3D仿真视窗</h2>
            </div>
            <div>
              <button 
                @click="toggleFullscreen"
                class="btn-outline text-sm py-1 px-2"
              >
                <i class="fa-solid fa-expand mr-1"></i>全屏
              </button>
            </div>
          </div>
          <div class="card-body p-0 relative h-[calc(100%-4rem)]">
            <div id="3d-container" class="w-full h-full bg-light">
              <img 
                class="w-full h-full object-cover opacity-80" 
                src="https://storage.googleapis.com/uxpilot-auth.appspot.com/05f6c87c0f-1e9055fd717f4718ba8e.png" 
                alt="3D rendering of robotic arm in simulation environment with grid floor, blue background, showing joint positions and coordinate system"
              >
            </div>
            <div class="absolute bottom-4 left-4 bg-white bg-opacity-80 p-2 rounded-lg shadow-sm">
              <div class="text-sm font-medium mb-1">📐 视角控制:</div>
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="control in viewControls" 
                  :key="control.id"
                  @click="setViewControl(control.id)"
                  :class="[
                    'bg-gray-200 hover:bg-gray-300 text-secondary px-3 py-1 rounded text-xs',
                    activeViewControl === control.id ? 'bg-primary text-white' : ''
                  ]"
                >
                  <i :class="control.icon + ' mr-1'"></i>{{ control.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Target Setup -->
        <div id="target-setup" class="card h-[18%]">
          <div class="card-header">
            <div class="flex items-center">
              <i class="fa-solid fa-bullseye text-warning mr-2"></i>
              <h2 class="text-lg font-semibold">目标设置</h2>
            </div>
          </div>
          <div class="card-body grid grid-cols-2 gap-4">
            <div>
              <div class="mb-2 text-sm font-medium">🎯 目标位置 (mm):</div>
              <div class="grid grid-cols-3 gap-2">
                <div>
                  <label class="text-xs text-gray-600">X:</label>
                  <input 
                    type="number" 
                    v-model.number="targetPosition.x" 
                    class="input-control"
                  >
                </div>
                <div>
                  <label class="text-xs text-gray-600">Y:</label>
                  <input 
                    type="number" 
                    v-model.number="targetPosition.y" 
                    class="input-control"
                  >
                </div>
                <div>
                  <label class="text-xs text-gray-600">Z:</label>
                  <input 
                    type="number" 
                    v-model.number="targetPosition.z" 
                    class="input-control"
                  >
                </div>
              </div>
            </div>
            <div>
              <div class="mb-2 text-sm font-medium">📐 目标姿态 (度):</div>
              <div class="grid grid-cols-3 gap-2">
                <div>
                  <label class="text-xs text-gray-600">RX:</label>
                  <input 
                    type="number" 
                    v-model.number="targetOrientation.rx" 
                    class="input-control"
                  >
                </div>
                <div>
                  <label class="text-xs text-gray-600">RY:</label>
                  <input 
                    type="number" 
                    v-model.number="targetOrientation.ry" 
                    class="input-control"
                  >
                </div>
                <div>
                  <label class="text-xs text-gray-600">RZ:</label>
                  <input 
                    type="number" 
                    v-model.number="targetOrientation.rz" 
                    class="input-control"
                  >
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <button 
              @click="setTarget"
              class="btn-primary mr-2"
            >
              <i class="fa-solid fa-crosshairs mr-1"></i>设置目标
            </button>
            <button 
              @click="clearTarget"
              class="btn-outline"
            >
              <i class="fa-solid fa-eraser mr-1"></i>清除
            </button>
          </div>
        </div>
        
        <!-- Simulation Monitoring -->
        <div id="simulation-monitoring" class="card h-[22%]">
          <div class="card-header">
            <div class="flex items-center">
              <i class="fa-solid fa-chart-line text-primary mr-2"></i>
              <h2 class="text-lg font-semibold">仿真监控</h2>
            </div>
          </div>
          <div class="card-body grid grid-cols-2 gap-4">
            <div>
              <div class="mb-1 flex items-center">
                <i class="fa-regular fa-clock text-gray-500 mr-1"></i>
                <span class="text-sm font-medium">仿真时间: </span>
                <span class="ml-1 text-sm">{{ simulationData.time }}秒</span>
              </div>
              <div class="mb-1">
                <div class="text-sm font-medium mb-1">
                  <i class="fa-solid fa-rotate text-gray-500 mr-1"></i>关节角度:
                </div>
                <div class="grid grid-cols-3 gap-1 text-xs text-gray-600">
                  <div v-for="(angle, index) in simulationData.jointAngles" :key="index">
                    J{{ index + 1 }}: {{ angle }}°
                  </div>
                </div>
              </div>
              <div class="mb-1 flex items-center">
                <i class="fa-solid fa-location-dot text-gray-500 mr-1"></i>
                <span class="text-sm font-medium">TCP位置: </span>
                <span class="ml-1 text-sm">({{ simulationData.tcpPosition.x }}, {{ simulationData.tcpPosition.y }}, {{ simulationData.tcpPosition.z }})</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-ban text-gray-500 mr-1"></i>
                <span class="text-sm font-medium">碰撞状态: </span>
                <span class="ml-1 text-sm flex items-center">
                  <span :class="[
                    'inline-block w-2 h-2 rounded-full mr-1',
                    simulationData.collisionStatus === '无碰撞' ? 'bg-success' : 'bg-danger'
                  ]"></span>{{ simulationData.collisionStatus }}
                </span>
              </div>
            </div>
            <div class="flex items-center justify-center">
              <div class="text-center">
                <div class="w-24 h-24 mx-auto mb-2 relative">
                  <div class="absolute inset-0 rounded-full border-4 border-gray-200"></div>
                  <div 
                    class="absolute inset-0 rounded-full border-4 border-primary border-t-transparent transition-transform duration-500" 
                    :style="`transform: rotate(${simulationData.completion * 3.6}deg)`"
                  ></div>
                  <div class="absolute inset-0 flex items-center justify-center text-xl font-bold text-primary">
                    {{ simulationData.completion }}%
                  </div>
                </div>
                <div class="text-sm text-gray-600">完成度</div>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <button 
              @click="showDetailedData"
              class="btn-outline mr-2 text-sm"
            >
              <i class="fa-solid fa-table mr-1"></i>详细数据
            </button>
            <button 
              @click="showChart"
              class="btn-outline text-sm"
            >
              <i class="fa-solid fa-chart-simple mr-1"></i>图表
            </button>
          </div>
        </div>
      </div>
      
      <!-- Right Column: Control Panel + Environment Settings -->
      <div class="col-span-1 flex flex-col gap-4">
        <!-- Control Panel -->
        <div id="control-panel" class="card h-[48%]">
          <div class="card-header bg-success bg-opacity-10">
            <div class="flex items-center">
              <i class="fa-solid fa-sliders text-success mr-2"></i>
              <h2 class="text-lg font-semibold">控制面板</h2>
            </div>
          </div>
          <div class="card-body space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">🤖 仿真模型:</label>
              <select v-model="controlSettings.simulationModel" class="select-control">
                <option value="fr3-dual">FR3双臂+底盘</option>
                <option value="ur5">UR5机械臂</option>
                <option value="kuka-iiwa">KUKA LBR iiwa</option>
                <option value="abb-irb120">ABB IRB 120</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">🎯 仿真模式:</label>
              <div class="space-y-1">
                <div class="flex items-center">
                  <input 
                    type="radio" 
                    name="sim-mode" 
                    id="mode1" 
                    value="kinematics"
                    v-model="controlSettings.simulationMode"
                    class="mr-2"
                  >
                  <label for="mode1" class="text-sm">运动学仿真</label>
                </div>
                <div class="flex items-center">
                  <input 
                    type="radio" 
                    name="sim-mode" 
                    id="mode2" 
                    value="dynamics"
                    v-model="controlSettings.simulationMode"
                    class="mr-2"
                  >
                  <label for="mode2" class="text-sm">动力学仿真</label>
                </div>
                <div class="flex items-center">
                  <input 
                    type="radio" 
                    name="sim-mode" 
                    id="mode3" 
                    value="collision"
                    v-model="controlSettings.simulationMode"
                    class="mr-2"
                  >
                  <label for="mode3" class="text-sm">碰撞检测</label>
                </div>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">⚡ 仿真速度:</label>
              <div class="flex items-center">
                <input 
                  type="range" 
                  min="0.1" 
                  max="2" 
                  step="0.1" 
                  v-model.number="controlSettings.simulationSpeed"
                  class="slider flex-1 mr-2"
                >
                <span class="text-sm font-medium">{{ controlSettings.simulationSpeed }}x</span>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">📊 仿真精度:</label>
              <select v-model="controlSettings.accuracy" class="select-control">
                <option value="high">高精度</option>
                <option value="standard">标准精度</option>
                <option value="low">低精度(快速)</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">🎮 仿真控制:</label>
              <div class="grid grid-cols-2 gap-2">
                <button 
                  @click="startSimulation"
                  :disabled="simulationStatus === 'running'"
                  class="btn-success text-sm"
                >
                  <i class="fa-solid fa-play mr-1"></i>{{ simulationStatus === 'running' ? '运行中' : '开始' }}
                </button>
                <button 
                  @click="pauseSimulation"
                  :disabled="simulationStatus !== 'running'"
                  class="btn-warning text-sm"
                >
                  <i class="fa-solid fa-pause mr-1"></i>暂停
                </button>
                <button 
                  @click="stopSimulation"
                  :disabled="simulationStatus === 'stopped'"
                  class="btn-danger text-sm"
                >
                  <i class="fa-solid fa-stop mr-1"></i>停止
                </button>
                <button 
                  @click="resetSimulation"
                  class="btn-outline text-sm"
                >
                  <i class="fa-solid fa-rotate mr-1"></i>重置
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Environment Settings -->
        <div id="environment-settings" class="card h-[52%]">
          <div class="card-header bg-warning bg-opacity-10">
            <div class="flex items-center">
              <i class="fa-solid fa-screwdriver-wrench text-warning mr-2"></i>
              <h2 class="text-lg font-semibold">环境设置</h2>
            </div>
          </div>
          <div class="card-body space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">🏠 场景模板:</label>
              <select v-model="environmentSettings.sceneTemplate" class="select-control">
                <option value="office">办公室</option>
                <option value="factory">工厂</option>
                <option value="warehouse">仓库</option>
                <option value="laboratory">实验室</option>
                <option value="empty">空场景</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">📦 障碍物:</label>
              <div class="space-y-1 max-h-[120px] overflow-y-auto">
                <div 
                  v-for="obstacle in availableObstacles" 
                  :key="obstacle.id"
                  class="flex items-center"
                >
                  <input 
                    type="checkbox" 
                    :id="obstacle.id" 
                    v-model="obstacle.enabled"
                    class="mr-2"
                  >
                  <label :for="obstacle.id" class="text-sm">{{ obstacle.name }}</label>
                </div>
              </div>
              <div class="flex gap-2 mt-2">
                <button 
                  @click="addObstacle"
                  class="btn-outline text-xs py-1 flex-1"
                >
                  <i class="fa-solid fa-plus mr-1"></i>添加障碍
                </button>
                <button 
                  @click="clearObstacles"
                  class="btn-outline text-xs py-1 flex-1"
                >
                  <i class="fa-solid fa-trash mr-1"></i>清空
                </button>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">🌍 重力设置:</label>
              <select v-model="environmentSettings.gravity" class="select-control">
                <option value="9.8">9.8 m/s² (地球)</option>
                <option value="1.6">1.6 m/s² (月球)</option>
                <option value="3.7">3.7 m/s² (火星)</option>
                <option value="0.0">0.0 m/s² (零重力)</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">🔆 光照条件:</label>
              <div class="flex items-center">
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  v-model.number="environmentSettings.lighting"
                  class="slider flex-1 mr-2"
                >
                <span class="text-sm font-medium">{{ environmentSettings.lighting }}%</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <button 
              @click="applyEnvironment"
              class="btn-primary mr-2"
            >
              <i class="fa-solid fa-check mr-1"></i>应用环境
            </button>
            <button 
              @click="resetEnvironment"
              class="btn-outline"
            >
              <i class="fa-solid fa-rotate-left mr-1"></i>重置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 目标位置和姿态接口定义
interface TargetPosition {
  x: number
  y: number
  z: number
}

interface TargetOrientation {
  rx: number
  ry: number
  rz: number
}

interface ViewControl {
  id: string
  label: string
  icon: string
}

interface SimulationData {
  time: number
  jointAngles: number[]
  tcpPosition: TargetPosition
  collisionStatus: string
  completion: number
}

interface ControlSettings {
  simulationModel: string
  simulationMode: string
  simulationSpeed: number
  accuracy: string
}

interface EnvironmentSettings {
  sceneTemplate: string
  gravity: string
  lighting: number
}

interface Obstacle {
  id: string
  name: string
  enabled: boolean
}

// 响应式数据
const activeViewControl = ref('rotate')
const simulationStatus = ref<'stopped' | 'running' | 'paused'>('stopped')

// 目标设置
const targetPosition = reactive<TargetPosition>({
  x: 400,
  y: 0,
  z: 300
})

const targetOrientation = reactive<TargetOrientation>({
  rx: 0,
  ry: 0,
  rz: 0
})

// 视角控制
const viewControls = ref<ViewControl[]>([
  { id: 'rotate', label: '旋转', icon: 'fa-solid fa-rotate' },
  { id: 'zoom', label: '缩放', icon: 'fa-solid fa-magnifying-glass-plus' },
  { id: 'pan', label: '平移', icon: 'fa-solid fa-arrows-up-down-left-right' },
  { id: 'top', label: '俯视', icon: 'fa-solid fa-arrow-down' },
  { id: 'side', label: '侧视', icon: 'fa-solid fa-arrow-right' },
  { id: 'front', label: '正视', icon: 'fa-solid fa-arrow-up' }
])

// 仿真数据
const simulationData = reactive<SimulationData>({
  time: 45.6,
  jointAngles: [15, -30, 45, 0, 60, 0],
  tcpPosition: { x: 400, y: 0, z: 300 },
  collisionStatus: '无碰撞',
  completion: 86
})

// 控制设置
const controlSettings = reactive<ControlSettings>({
  simulationModel: 'fr3-dual',
  simulationMode: 'kinematics',
  simulationSpeed: 0.8,
  accuracy: 'high'
})

// 环境设置
const environmentSettings = reactive<EnvironmentSettings>({
  sceneTemplate: 'office',
  gravity: '9.8',
  lighting: 70
})

// 障碍物
const availableObstacles = ref<Obstacle[]>([
  { id: 'obj1', name: '桌子', enabled: true },
  { id: 'obj2', name: '椅子', enabled: true },
  { id: 'obj3', name: '柜子', enabled: false },
  { id: 'obj4', name: '墙壁', enabled: false },
  { id: 'obj5', name: '显示器', enabled: false },
  { id: 'obj6', name: '键盘', enabled: false }
])

let simulationInterval: number | null = null

// 视角控制
const setViewControl = (controlId: string) => {
  activeViewControl.value = controlId
  ElMessage.info(`已切换到${viewControls.value.find(c => c.id === controlId)?.label}模式`)
}

// 全屏切换
const toggleFullscreen = () => {
  ElMessage.success('全屏模式切换')
}

// 目标设置
const setTarget = () => {
  // 更新TCP位置到目标位置
  simulationData.tcpPosition.x = targetPosition.x
  simulationData.tcpPosition.y = targetPosition.y
  simulationData.tcpPosition.z = targetPosition.z
  ElMessage.success(`目标已设置: (${targetPosition.x}, ${targetPosition.y}, ${targetPosition.z})`)
}

const clearTarget = () => {
  targetPosition.x = 0
  targetPosition.y = 0
  targetPosition.z = 0
  targetOrientation.rx = 0
  targetOrientation.ry = 0
  targetOrientation.rz = 0
  ElMessage.info('目标已清除')
}

// 仿真控制
const startSimulation = () => {
  simulationStatus.value = 'running'
  ElMessage.success('仿真已开始')
  
  // 开始仿真时间更新
  simulationInterval = setInterval(() => {
    simulationData.time += 0.1
    simulationData.completion = Math.min(100, simulationData.completion + 0.5)
    
    // 模拟关节角度变化
    simulationData.jointAngles = simulationData.jointAngles.map(angle => 
      angle + (Math.random() - 0.5) * 2
    )
  }, 100)
}

const pauseSimulation = () => {
  simulationStatus.value = 'paused'
  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
  ElMessage.info('仿真已暂停')
}

const stopSimulation = () => {
  simulationStatus.value = 'stopped'
  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
  ElMessage.warning('仿真已停止')
}

const resetSimulation = () => {
  simulationStatus.value = 'stopped'
  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
  
  simulationData.time = 0
  simulationData.completion = 0
  simulationData.jointAngles = [0, 0, 0, 0, 0, 0]
  simulationData.collisionStatus = '无碰撞'
  
  ElMessage.success('仿真已重置')
}

// 监控功能
const showDetailedData = () => {
  ElMessage.info('显示详细数据表格')
}

const showChart = () => {
  ElMessage.info('显示数据图表')
}

// 环境管理
const addObstacle = () => {
  const newId = `obj${availableObstacles.value.length + 1}`
  availableObstacles.value.push({
    id: newId,
    name: `新障碍物${availableObstacles.value.length + 1}`,
    enabled: false
  })
  ElMessage.success('已添加新障碍物')
}

const clearObstacles = () => {
  availableObstacles.value.forEach(obstacle => {
    obstacle.enabled = false
  })
  ElMessage.warning('已清空所有障碍物')
}

const applyEnvironment = () => {
  const enabledObstacles = availableObstacles.value.filter(o => o.enabled)
  ElMessage.success(`环境已应用: ${environmentSettings.sceneTemplate}场景，包含${enabledObstacles.length}个障碍物`)
}

const resetEnvironment = () => {
  environmentSettings.sceneTemplate = 'office'
  environmentSettings.gravity = '9.8'
  environmentSettings.lighting = 70
  availableObstacles.value.forEach(obstacle => {
    obstacle.enabled = false
  })
  ElMessage.info('环境设置已重置')
}

onMounted(() => {
  console.log('机器人仿真页面已加载')
})

onUnmounted(() => {
  if (simulationInterval) {
    clearInterval(simulationInterval)
  }
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
  color: #06B6D4;
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

.bg-info {
  background-color: #06B6D4;
}

.bg-light {
  background-color: #E0F8FF;
}

/* 卡片样式 */
.card {
  @apply bg-white rounded-lg shadow-md overflow-hidden;
}

.card-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200;
}

.card-body {
  @apply p-4;
}

.card-footer {
  @apply flex justify-end p-4 border-t border-gray-200;
}

/* 按钮样式 */
.btn-primary {
  @apply bg-primary text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors;
}

.btn-success {
  @apply bg-success text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors;
}

.btn-warning {
  @apply bg-warning text-white px-4 py-2 rounded-md hover:bg-yellow-600 transition-colors;
}

.btn-danger {
  @apply bg-danger text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors;
}

.btn-info {
  @apply bg-info text-white px-4 py-2 rounded-md hover:bg-cyan-600 transition-colors;
}

.btn-outline {
  @apply border border-gray-300 text-secondary px-4 py-2 rounded-md hover:bg-gray-100 transition-colors;
}

/* 禁用状态 */
.btn-primary:disabled,
.btn-success:disabled,
.btn-warning:disabled,
.btn-danger:disabled {
  @apply opacity-50 cursor-not-allowed;
}

/* 输入控件样式 */
.input-control {
  @apply border border-gray-300 rounded-md px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-primary;
}

.select-control {
  @apply border border-gray-300 rounded-md px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-primary;
}

/* 滑块样式 */
.slider {
  @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer;
}

.slider::-webkit-slider-thumb {
  @apply appearance-none w-4 h-4 rounded-full bg-primary cursor-pointer;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid.grid-cols-3 {
    grid-template-columns: 1fr;
  }
  
  .col-span-2,
  .col-span-1 {
    grid-column: span 1;
  }
  
  .card {
    height: auto !important;
    min-height: 300px;
  }
  
  .grid.grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .grid.grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .grid.grid-cols-3 {
    grid-template-columns: 1fr;
  }
}
</style>
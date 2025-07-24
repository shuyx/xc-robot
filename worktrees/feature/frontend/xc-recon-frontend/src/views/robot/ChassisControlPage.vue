<template>
  <div class="w-full h-full bg-gray-50 p-4">
    <!-- Header -->
    <div class="mb-4">
      <h1 class="text-2xl font-bold text-secondary">Hermes移动底盘控制</h1>
      <p class="text-gray-600">移动机器人导航与运动控制</p>
    </div>
    
    <!-- Main Content Grid -->
    <div class="grid grid-cols-2 gap-4">
      <!-- Navigation Map Area -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-bold text-secondary flex items-center">
            <i class="fa-solid fa-map-location-dot mr-2 text-success"></i>导航地图区
          </h2>
          <div>
            <button 
              @click="toggleFullscreen"
              class="text-xs bg-success text-white px-2 py-1 rounded-md mr-1"
            >
              <i class="fa-solid fa-expand mr-1"></i>全屏
            </button>
            <button 
              @click="refreshMap"
              class="text-xs bg-gray-200 text-secondary px-2 py-1 rounded-md"
            >
              <i class="fa-solid fa-refresh mr-1"></i>刷新
            </button>
          </div>
        </div>
        <div class="map-container h-[300px] bg-light rounded-lg border border-gray-200">
          <div class="map-grid h-full w-full relative">
            <!-- Building markers -->
            <div class="building-marker absolute" style="top: 20%; left: 20%;">
              <i class="fa-solid fa-house text-gray-600 text-xl"></i>
            </div>
            <div class="building-marker absolute" style="top: 20%; right: 20%;">
              <i class="fa-solid fa-house text-gray-600 text-xl"></i>
            </div>
            
            <!-- Robot position -->
            <div class="robot-marker absolute" style="top: 50%; left: 30%; transform: translate(-50%, -50%); z-index: 10;">
              <div class="robot-icon">
                <i class="fa-solid fa-robot text-primary text-2xl"></i>
              </div>
              <div class="text-xs text-center mt-1 text-secondary font-medium">
                当前位置
              </div>
            </div>
            
            <!-- Target position -->
            <div class="target-marker absolute" style="top: 30%; left: 60%; transform: translate(-50%, -50%); z-index: 5;">
              <i class="fa-solid fa-location-crosshairs text-warning text-xl"></i>
              <div class="text-xs text-center mt-1 text-secondary">
                目标点
              </div>
            </div>
            
            <!-- Start position -->
            <div class="start-marker absolute" style="bottom: 20%; left: 20%; transform: translate(-50%, -50%); z-index: 5;">
              <i class="fa-solid fa-map-pin text-danger text-xl"></i>
              <div class="text-xs text-center mt-1 text-secondary">
                起点
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Manual Control Area -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-bold text-secondary flex items-center">
            <i class="fa-solid fa-gamepad mr-2 text-primary"></i>手动控制区
          </h2>
          <div class="text-xs text-gray-500">
            <i class="fa-solid fa-keyboard mr-1"></i>WASD键控制
          </div>
        </div>
        <div class="flex flex-col items-center justify-center h-[300px]">
          <!-- Forward button -->
          <button 
            @click="moveForward"
            @mousedown="startContinuousMove('forward')"
            @mouseup="stopContinuousMove"
            @mouseleave="stopContinuousMove"
            class="control-btn w-20 h-14 bg-success text-white rounded-t-lg mb-2 hover:bg-opacity-90"
          >
            <i class="fa-solid fa-chevron-up text-xl"></i>
            <div class="text-xs">前进</div>
          </button>
          
          <!-- Middle row buttons -->
          <div class="flex justify-center items-center space-x-2">
            <button 
              @click="turnLeft"
              @mousedown="startContinuousMove('left')"
              @mouseup="stopContinuousMove"
              @mouseleave="stopContinuousMove"
              class="control-btn w-14 h-14 bg-success text-white rounded-l-lg hover:bg-opacity-90"
            >
              <i class="fa-solid fa-chevron-left text-xl"></i>
              <div class="text-xs">左转</div>
            </button>
            
            <button 
              @click="stopMovement"
              class="control-btn w-14 h-14 bg-danger text-white rounded-lg hover:bg-opacity-90"
            >
              <i class="fa-solid fa-stop text-xl"></i>
              <div class="text-xs">停止</div>
            </button>
            
            <button 
              @click="turnRight"
              @mousedown="startContinuousMove('right')"
              @mouseup="stopContinuousMove"
              @mouseleave="stopContinuousMove"
              class="control-btn w-14 h-14 bg-success text-white rounded-r-lg hover:bg-opacity-90"
            >
              <i class="fa-solid fa-chevron-right text-xl"></i>
              <div class="text-xs">右转</div>
            </button>
          </div>
          
          <!-- Backward button -->
          <button 
            @click="moveBackward"
            @mousedown="startContinuousMove('backward')"
            @mouseup="stopContinuousMove"
            @mouseleave="stopContinuousMove"
            class="control-btn w-20 h-14 bg-success text-white rounded-b-lg mt-2 hover:bg-opacity-90"
          >
            <i class="fa-solid fa-chevron-down text-xl"></i>
            <div class="text-xs">后退</div>
          </button>
          
          <!-- Speed controls -->
          <div class="mt-6 w-full">
            <div class="mb-2">
              <div class="flex justify-between items-center">
                <label class="text-sm text-secondary">速度:</label>
                <span class="text-xs text-gray-600">{{ speedPercentage }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  class="bg-success h-2.5 rounded-full transition-all duration-300" 
                  :style="{ width: speedPercentage + '%' }"
                ></div>
              </div>
              <el-slider 
                v-model="speedPercentage" 
                :min="0" 
                :max="100" 
                :step="5"
                @change="updateSpeed"
                class="mt-2"
              ></el-slider>
            </div>
            
            <div class="flex justify-between text-sm">
              <div class="text-secondary">
                <i class="fa-solid fa-gauge-high mr-1 text-primary"></i>线速度: <span class="font-medium">{{ linearSpeed.toFixed(1) }} m/s</span>
              </div>
              <div class="text-secondary">
                <i class="fa-solid fa-rotate mr-1 text-warning"></i>角速度: <span class="font-medium">{{ angularSpeed.toFixed(1) }} rad/s</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Chassis Status -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-bold text-secondary flex items-center">
            <i class="fa-solid fa-chart-simple mr-2 text-primary"></i>底盘状态
          </h2>
          <span class="text-xs px-2 py-1 bg-green-100 text-success rounded-full">
            <i class="fa-solid fa-circle-check mr-1"></i>{{ chassisStatus }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="flex items-center">
            <i class="fa-solid fa-location-dot text-xl text-warning mr-3"></i>
            <div>
              <div class="text-xs text-gray-500">位置</div>
              <div class="font-medium text-secondary">({{ robotPosition.x }}, {{ robotPosition.y }})</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-compass text-xl text-warning mr-3"></i>
            <div>
              <div class="text-xs text-gray-500">朝向</div>
              <div class="font-medium text-secondary">{{ robotOrientation }}°</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-person-running text-xl text-primary mr-3"></i>
            <div>
              <div class="text-xs text-gray-500">速度</div>
              <div class="font-medium text-secondary">{{ currentLinearSpeed.toFixed(1) }} m/s</div>
            </div>
          </div>
          <div class="flex items-center">
            <i class="fa-solid fa-sync text-xl text-primary mr-3"></i>
            <div>
              <div class="text-xs text-gray-500">角速度</div>
              <div class="font-medium text-secondary">{{ currentAngularSpeed.toFixed(1) }} rad/s</div>
            </div>
          </div>
          <div class="flex items-center col-span-2">
            <i class="fa-solid fa-wifi text-xl text-success mr-3"></i>
            <div>
              <div class="text-xs text-gray-500">连接状态</div>
              <div class="font-medium text-success">
                <i class="fa-solid fa-circle text-xs mr-1"></i>{{ connectionStatus }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Sensor Status -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-bold text-secondary flex items-center">
            <i class="fa-solid fa-battery-three-quarters mr-2 text-success"></i>传感器状态
          </h2>
          <button 
            @click="refreshSensors"
            class="text-xs bg-gray-200 text-secondary px-2 py-1 rounded-md"
          >
            <i class="fa-solid fa-rotate mr-1"></i>刷新
          </button>
        </div>
        <div class="space-y-3">
          <div v-for="sensor in sensors" :key="sensor.name" class="flex items-center justify-between">
            <div class="flex items-center">
              <i :class="[sensor.icon, sensor.status === '正常' || sensor.status === '已校准' ? 'text-success' : 'text-warning']" class="mr-2"></i>
              <span class="text-secondary">{{ sensor.name }}</span>
            </div>
            <span :class="sensor.status === '正常' || sensor.status === '已校准' ? 'text-success' : 'text-warning'" class="font-medium">{{ sensor.status }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <i class="fa-solid fa-battery-three-quarters text-success mr-2"></i>
              <span class="text-secondary">电池</span>
            </div>
            <div class="flex items-center">
              <div class="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  class="bg-success h-2 rounded-full transition-all duration-300" 
                  :style="{ width: batteryLevel + '%' }"
                ></div>
              </div>
              <span class="text-success font-medium">{{ batteryLevel }}%</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <i class="fa-solid fa-temperature-half text-warning mr-2"></i>
              <span class="text-secondary">温度</span>
            </div>
            <span class="text-warning font-medium">{{ temperature }}°C</span>
          </div>
        </div>
      </div>
      
      <!-- Navigation Control -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-bold text-secondary flex items-center">
            <i class="fa-solid fa-location-crosshairs mr-2 text-warning"></i>导航控制
          </h2>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <button 
            @click="setTargetPoint"
            class="bg-white border border-success text-success rounded-md py-2 hover:bg-success hover:text-white transition-colors"
          >
            <i class="fa-solid fa-map-pin mr-1"></i>设置目标点
          </button>
          <button 
            @click="startNavigation"
            class="bg-success text-white rounded-md py-2 hover:bg-opacity-90 transition-colors"
          >
            <i class="fa-solid fa-play mr-1"></i>开始导航
          </button>
          <button 
            @click="saveMap"
            class="bg-white border border-primary text-primary rounded-md py-2 hover:bg-primary hover:text-white transition-colors"
          >
            <i class="fa-solid fa-floppy-disk mr-1"></i>保存地图
          </button>
          <button 
            @click="loadMap"
            class="bg-white border border-primary text-primary rounded-md py-2 hover:bg-primary hover:text-white transition-colors"
          >
            <i class="fa-solid fa-folder-open mr-1"></i>加载地图
          </button>
        </div>
        
        <div class="mt-4">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-sm font-medium text-secondary">导航参数</h3>
            <button 
              @click="openAdvancedSettings"
              class="text-xs text-primary"
            >
              <i class="fa-solid fa-sliders mr-1"></i>高级设置
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div class="flex items-center">
              <span class="text-gray-600 mr-2">最大速度:</span>
              <span class="text-secondary font-medium">{{ maxSpeed }} m/s</span>
            </div>
            <div class="flex items-center">
              <span class="text-gray-600 mr-2">最小避障距离:</span>
              <span class="text-secondary font-medium">{{ minObstacleDistance }} m</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Motion Record -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="font-bold text-secondary flex items-center">
            <i class="fa-solid fa-chart-line mr-2 text-primary"></i>运动记录
          </h2>
          <button 
            @click="exportData"
            class="text-xs bg-gray-200 text-secondary px-2 py-1 rounded-md"
          >
            <i class="fa-solid fa-download mr-1"></i>导出
          </button>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="record in motionRecords" :key="record.label" class="flex items-center">
            <div :class="`w-12 h-12 rounded-full ${record.bgColor} flex items-center justify-center mr-3`">
              <i :class="`${record.icon} ${record.iconColor} text-xl`"></i>
            </div>
            <div>
              <div class="text-xs text-gray-500">{{ record.label }}</div>
              <div class="font-medium text-secondary text-lg">{{ record.value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 类型定义
interface Position {
  x: number
  y: number
}

interface Sensor {
  name: string
  status: string
  icon: string
}

interface MotionRecord {
  label: string
  value: string
  icon: string
  iconColor: string
  bgColor: string
}

// 响应式数据
const speedPercentage = ref(50)
const linearSpeed = ref(0.5)
const angularSpeed = ref(0.3)
const currentLinearSpeed = ref(0.0)
const currentAngularSpeed = ref(0.0)
const robotPosition = reactive<Position>({ x: 2.5, y: 1.8 })
const robotOrientation = ref(45)
const batteryLevel = ref(85)
const temperature = ref(35)
const chassisStatus = ref('正常运行中')
const connectionStatus = ref('正常')
const maxSpeed = ref(0.8)
const minObstacleDistance = ref(0.5)

// 传感器状态
const sensors = ref<Sensor[]>([
  { name: '激光雷达', status: '正常', icon: 'fa-solid fa-circle' },
  { name: 'IMU', status: '已校准', icon: 'fa-solid fa-circle' },
  { name: '里程计', status: '正常', icon: 'fa-solid fa-circle' }
])

// 运动记录
const motionRecords = ref<MotionRecord[]>([
  { label: '总里程', value: '125.6 km', icon: 'fa-solid fa-road', iconColor: 'text-primary', bgColor: 'bg-blue-100' },
  { label: '运行时间', value: '8.5 h', icon: 'fa-regular fa-clock', iconColor: 'text-success', bgColor: 'bg-green-100' },
  { label: '避障次数', value: '15 次', icon: 'fa-solid fa-triangle-exclamation', iconColor: 'text-warning', bgColor: 'bg-yellow-100' },
  { label: '平均速度', value: '0.4 m/s', icon: 'fa-solid fa-gauge-high', iconColor: 'text-primary', bgColor: 'bg-blue-100' }
])

// 连续移动控制
let continuousMoveInterval: NodeJS.Timeout | null = null

// 计算属性
const isMoving = computed(() => currentLinearSpeed.value > 0 || Math.abs(currentAngularSpeed.value) > 0)

// 方法
const updateSpeed = () => {
  linearSpeed.value = (speedPercentage.value / 100) * maxSpeed.value
  angularSpeed.value = (speedPercentage.value / 100) * 0.6 // 最大角速度 0.6 rad/s
  console.log(`Speed updated: ${linearSpeed.value.toFixed(1)} m/s`)
}

const moveForward = () => {
  currentLinearSpeed.value = linearSpeed.value
  currentAngularSpeed.value = 0
  console.log('Moving forward')
  ElMessage({
    type: 'info',
    message: '机器人前进中',
    duration: 1000
  })
}

const moveBackward = () => {
  currentLinearSpeed.value = -linearSpeed.value
  currentAngularSpeed.value = 0
  console.log('Moving backward')
  ElMessage({
    type: 'info',
    message: '机器人后退中',
    duration: 1000
  })
}

const turnLeft = () => {
  currentLinearSpeed.value = 0
  currentAngularSpeed.value = angularSpeed.value
  console.log('Turning left')
  ElMessage({
    type: 'info',
    message: '机器人左转中',
    duration: 1000
  })
}

const turnRight = () => {
  currentLinearSpeed.value = 0
  currentAngularSpeed.value = -angularSpeed.value
  console.log('Turning right')
  ElMessage({
    type: 'info',
    message: '机器人右转中',
    duration: 1000
  })
}

const stopMovement = () => {
  currentLinearSpeed.value = 0
  currentAngularSpeed.value = 0
  if (continuousMoveInterval) {
    clearInterval(continuousMoveInterval)
    continuousMoveInterval = null
  }
  console.log('Stopping')
  ElMessage({
    type: 'warning',
    message: '机器人已停止',
    duration: 1000
  })
}

const startContinuousMove = (direction: string) => {
  if (continuousMoveInterval) {
    clearInterval(continuousMoveInterval)
  }
  
  continuousMoveInterval = setInterval(() => {
    switch (direction) {
      case 'forward':
        moveForward()
        break
      case 'backward':
        moveBackward()
        break
      case 'left':
        turnLeft()
        break
      case 'right':
        turnRight()
        break
    }
  }, 100)
}

const stopContinuousMove = () => {
  if (continuousMoveInterval) {
    clearInterval(continuousMoveInterval)
    continuousMoveInterval = null
  }
  // 延迟停止，让用户有时间感受到移动
  setTimeout(stopMovement, 100)
}

// 键盘控制
const handleKeyDown = (event: KeyboardEvent) => {
  switch (event.key.toLowerCase()) {
    case 'w':
      moveForward()
      break
    case 's':
      moveBackward()
      break
    case 'a':
      turnLeft()
      break
    case 'd':
      turnRight()
      break
    case ' ':
      event.preventDefault()
      stopMovement()
      break
  }
}

// 地图和导航功能
const toggleFullscreen = () => {
  ElMessage({
    type: 'info',
    message: '切换全屏模式',
    duration: 2000
  })
  console.log('Toggle fullscreen')
}

const refreshMap = () => {
  ElMessage({
    type: 'success',
    message: '地图已刷新',
    duration: 2000
  })
  console.log('Refresh map')
}

const refreshSensors = () => {
  ElMessage({
    type: 'success',
    message: '传感器状态已刷新',
    duration: 2000
  })
  console.log('Refresh sensors')
}

const setTargetPoint = () => {
  ElMessage({
    type: 'info',
    message: '请在地图上点击设置目标点',
    duration: 2000
  })
  console.log('Set target point')
}

const startNavigation = () => {
  ElMessage({
    type: 'success',
    message: '开始自主导航',
    duration: 2000
  })
  console.log('Start navigation')
}

const saveMap = () => {
  ElMessage({
    type: 'success',
    message: '地图已保存',
    duration: 2000
  })
  console.log('Save map')
}

const loadMap = () => {
  ElMessage({
    type: 'info',
    message: '正在加载地图...',
    duration: 2000
  })
  console.log('Load map')
}

const openAdvancedSettings = () => {
  ElMessage({
    type: 'info',
    message: '打开高级设置面板',
    duration: 2000
  })
  console.log('Open advanced settings')
}

const exportData = () => {
  ElMessage({
    type: 'success',
    message: '运动数据导出中...',
    duration: 2000
  })
  console.log('Export motion data')
}

// 生命周期
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  updateSpeed()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  if (continuousMoveInterval) {
    clearInterval(continuousMoveInterval)
  }
})
</script>

<style scoped>
.control-btn {
  transition: all 0.2s;
}

.control-btn:active {
  transform: scale(0.95);
}

.map-container {
  position: relative;
  overflow: hidden;
}

.map-grid {
  background-size: 20px 20px;
  background-image: 
    linear-gradient(to right, rgba(0, 168, 112, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 168, 112, 0.1) 1px, transparent 1px);
}

.robot-icon {
  position: relative;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.light-blue {
  background-color: #F0F9F5;
}

/* Element Plus Slider 样式覆盖 */
:deep(.el-slider__runway) {
  height: 6px;
}

:deep(.el-slider__bar) {
  height: 6px;
  background-color: #00A870;
}

:deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  border: 2px solid #00A870;
}
</style>
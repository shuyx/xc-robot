<template>
  <div class="bg-gray-100 w-full h-full p-4 overflow-auto">
    <!-- Header with Emergency Stop -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary">双臂FR3机械臂控制</h1>
        <p class="text-gray-600">实时控制双臂协作机器人的关节和末端执行器</p>
      </div>
      <div>
        <button 
          @click="emergencyStop"
          class="emergency-stop-btn rounded-full w-16 h-16 text-white font-bold flex items-center justify-center"
        >
          <div class="text-center">
            <i class="fa-solid fa-hand fa-lg mb-1"></i>
            <div class="text-xs">急停</div>
          </div>
        </button>
      </div>
    </div>

    <!-- 控制模式 -->
    <div id="control-mode-section" class="bg-white rounded-lg shadow p-4 mb-4">
      <h2 class="text-lg font-semibold mb-3 text-secondary flex items-center">
        <i class="fa-solid fa-sliders mr-2"></i> 控制模式
      </h2>
      <div class="flex flex-wrap gap-3">
        <div class="flex-1 min-w-[150px]">
          <div 
            :class="[
              'border rounded-md p-3 flex flex-col items-center',
              controlMode === 'manual' ? 'border-primary bg-light-blue' : 'border-gray-200'
            ]"
          >
            <div class="flex items-center justify-center mb-2">
              <i class="fa-solid fa-hand text-primary mr-2"></i>
              <span class="font-medium">手动模式</span>
            </div>
            <span 
              v-if="controlMode === 'manual'" 
              class="text-xs px-2 py-1 bg-success text-white rounded-full flex items-center"
            >
              <i class="fa-solid fa-check mr-1"></i> 当前模式
            </span>
            <button 
              v-else
              @click="switchMode('manual')"
              class="text-xs px-3 py-1 bg-primary text-white rounded-md hover:bg-blue-600 transition"
            >
              切换
            </button>
          </div>
        </div>
        <div class="flex-1 min-w-[150px]">
          <div 
            :class="[
              'border rounded-md p-3 flex flex-col items-center',
              controlMode === 'auto' ? 'border-primary bg-light-blue' : 'border-gray-200'
            ]"
          >
            <div class="flex items-center justify-center mb-2">
              <i class="fa-solid fa-robot text-gray-600 mr-2"></i>
              <span class="font-medium">自动模式</span>
            </div>
            <span 
              v-if="controlMode === 'auto'" 
              class="text-xs px-2 py-1 bg-success text-white rounded-full flex items-center"
            >
              <i class="fa-solid fa-check mr-1"></i> 当前模式
            </span>
            <button 
              v-else
              @click="switchMode('auto')"
              class="text-xs px-3 py-1 bg-primary text-white rounded-md hover:bg-blue-600 transition"
            >
              切换
            </button>
          </div>
        </div>
        <div class="flex-1 min-w-[150px]">
          <div 
            :class="[
              'border rounded-md p-3 flex flex-col items-center',
              controlMode === 'teach' ? 'border-primary bg-light-blue' : 'border-gray-200'
            ]"
          >
            <div class="flex items-center justify-center mb-2">
              <i class="fa-solid fa-chalkboard-user text-gray-600 mr-2"></i>
              <span class="font-medium">示教模式</span>
            </div>
            <span 
              v-if="controlMode === 'teach'" 
              class="text-xs px-2 py-1 bg-success text-white rounded-full flex items-center"
            >
              <i class="fa-solid fa-check mr-1"></i> 当前模式
            </span>
            <button 
              v-else
              @click="switchMode('teach')"
              class="text-xs px-3 py-1 bg-primary text-white rounded-md hover:bg-blue-600 transition"
            >
              切换
            </button>
          </div>
        </div>
        <div class="flex-1 min-w-[150px]">
          <div 
            :class="[
              'border rounded-md p-3 flex flex-col items-center',
              controlMode === 'force' ? 'border-primary bg-light-blue' : 'border-gray-200'
            ]"
          >
            <div class="flex items-center justify-center mb-2">
              <i class="fa-solid fa-hand-back-fist text-gray-600 mr-2"></i>
              <span class="font-medium">力控模式</span>
            </div>
            <span 
              v-if="controlMode === 'force'" 
              class="text-xs px-2 py-1 bg-success text-white rounded-full flex items-center"
            >
              <i class="fa-solid fa-check mr-1"></i> 当前模式
            </span>
            <button 
              v-else
              @click="switchMode('force')"
              class="text-xs px-3 py-1 bg-primary text-white rounded-md hover:bg-blue-600 transition"
            >
              切换
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 双臂状态监控 -->
    <div id="arm-status-section" class="bg-white rounded-lg shadow p-4 mb-4">
      <h2 class="text-lg font-semibold mb-3 text-secondary flex items-center">
        <i class="fa-solid fa-robot mr-2"></i> 双臂状态监控
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 右臂状态 -->
        <div class="border rounded-md p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center">
              <span class="inline-block w-3 h-3 rounded-full bg-success mr-2"></span>
              <h3 class="font-medium">右臂 (FR3-R)</h3>
            </div>
            <span class="text-xs px-2 py-1 bg-success text-white rounded-full">{{ rightArmStatus }}</span>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">位置 (mm)</span>
              <span class="font-medium">[{{ rightArm.position.x }}, {{ rightArm.position.y }}, {{ rightArm.position.z }}]</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">速度</span>
              <span class="font-medium">{{ rightArm.speed }} m/s</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">力 (N)</span>
              <span class="font-medium">[{{ rightArm.force.x }}, {{ rightArm.force.y }}, {{ rightArm.force.z }}]</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">温度</span>
              <span class="font-medium">{{ rightArm.temperature }}°C</span>
            </div>
          </div>
        </div>
        
        <!-- 左臂状态 -->
        <div class="border rounded-md p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center">
              <span class="inline-block w-3 h-3 rounded-full bg-success mr-2"></span>
              <h3 class="font-medium">左臂 (FR3-L)</h3>
            </div>
            <span class="text-xs px-2 py-1 bg-success text-white rounded-full">{{ leftArmStatus }}</span>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">位置 (mm)</span>
              <span class="font-medium">[{{ leftArm.position.x }}, {{ leftArm.position.y }}, {{ leftArm.position.z }}]</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">速度</span>
              <span class="font-medium">{{ leftArm.speed }} m/s</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">力 (N)</span>
              <span class="font-medium">[{{ leftArm.force.x }}, {{ leftArm.force.y }}, {{ leftArm.force.z }}]</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-gray-500">温度</span>
              <span class="font-medium">{{ leftArm.temperature }}°C</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关节控制 -->
    <div id="joint-control-section" class="bg-white rounded-lg shadow p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-lg font-semibold text-secondary flex items-center">
          <i class="fa-solid fa-bullseye mr-2"></i> 关节控制 ({{ currentArm === 'right' ? '右臂' : '左臂' }})
        </h2>
        <div class="flex items-center">
          <button 
            @click="switchArm"
            class="mr-2 px-3 py-1 bg-primary text-white text-sm rounded hover:bg-blue-600 transition"
          >
            切换到{{ currentArm === 'right' ? '左臂' : '右臂' }}
          </button>
          <button 
            @click="savePosition"
            class="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition flex items-center"
          >
            <i class="fa-solid fa-floppy-disk mr-1"></i> 保存位置
          </button>
        </div>
      </div>
      
      <div class="space-y-4">
        <div v-for="(joint, index) in joints" :key="`j${index + 1}`" class="flex flex-col">
          <div class="flex justify-between mb-1">
            <span class="text-sm font-medium">J{{ index + 1 }}:</span>
            <span class="text-sm">当前: {{ joint.current }}°</span>
          </div>
          <div class="flex items-center">
            <span class="text-xs text-gray-500 w-12">{{ joint.min }}°</span>
            <div class="flex-1 px-2">
              <el-slider 
                v-model="joint.target" 
                :min="joint.min" 
                :max="joint.max" 
                :step="1"
                @change="updateJoint(index, joint.target)"
              ></el-slider>
            </div>
            <span class="text-xs text-gray-500 w-12 text-right">+{{ joint.max }}°</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TCP控制 -->
    <div id="tcp-control-section" class="bg-white rounded-lg shadow p-4 mb-4">
      <h2 class="text-lg font-semibold mb-3 text-secondary flex items-center">
        <i class="fa-solid fa-bullseye mr-2"></i> TCP控制
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 位置控制 -->
        <div class="border rounded-md p-4">
          <h3 class="font-medium mb-3">位置控制 (mm)</h3>
          <div class="space-y-3">
            <div class="flex items-center">
              <label class="w-8 font-medium">X:</label>
              <div class="flex-1">
                <el-input-number 
                  v-model="tcpPosition.x" 
                  :min="-1000" 
                  :max="1000" 
                  :step="10" 
                  controls-position="right"
                  @change="updateTCPPosition"
                ></el-input-number>
              </div>
              <div class="ml-2 flex">
                <button 
                  @click="adjustTCPPosition('x', -10)"
                  class="w-8 h-8 bg-gray-200 rounded-l flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-minus"></i>
                </button>
                <button 
                  @click="adjustTCPPosition('x', 10)"
                  class="w-8 h-8 bg-gray-200 rounded-r flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>
            
            <div class="flex items-center">
              <label class="w-8 font-medium">Y:</label>
              <div class="flex-1">
                <el-input-number 
                  v-model="tcpPosition.y" 
                  :min="-1000" 
                  :max="1000" 
                  :step="10" 
                  controls-position="right"
                  @change="updateTCPPosition"
                ></el-input-number>
              </div>
              <div class="ml-2 flex">
                <button 
                  @click="adjustTCPPosition('y', -10)"
                  class="w-8 h-8 bg-gray-200 rounded-l flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-minus"></i>
                </button>
                <button 
                  @click="adjustTCPPosition('y', 10)"
                  class="w-8 h-8 bg-gray-200 rounded-r flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>
            
            <div class="flex items-center">
              <label class="w-8 font-medium">Z:</label>
              <div class="flex-1">
                <el-input-number 
                  v-model="tcpPosition.z" 
                  :min="0" 
                  :max="1000" 
                  :step="10" 
                  controls-position="right"
                  @change="updateTCPPosition"
                ></el-input-number>
              </div>
              <div class="ml-2 flex">
                <button 
                  @click="adjustTCPPosition('z', -10)"
                  class="w-8 h-8 bg-gray-200 rounded-l flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-minus"></i>
                </button>
                <button 
                  @click="adjustTCPPosition('z', 10)"
                  class="w-8 h-8 bg-gray-200 rounded-r flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 姿态控制 -->
        <div class="border rounded-md p-4">
          <h3 class="font-medium mb-3">姿态控制 (度)</h3>
          <div class="space-y-3">
            <div class="flex items-center">
              <label class="w-8 font-medium">RX:</label>
              <div class="flex-1">
                <el-input-number 
                  v-model="tcpOrientation.rx" 
                  :min="-180" 
                  :max="180" 
                  :step="5" 
                  controls-position="right"
                  @change="updateTCPOrientation"
                ></el-input-number>
              </div>
              <div class="ml-2 flex">
                <button 
                  @click="adjustTCPOrientation('rx', -5)"
                  class="w-8 h-8 bg-gray-200 rounded-l flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-minus"></i>
                </button>
                <button 
                  @click="adjustTCPOrientation('rx', 5)"
                  class="w-8 h-8 bg-gray-200 rounded-r flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>
            
            <div class="flex items-center">
              <label class="w-8 font-medium">RY:</label>
              <div class="flex-1">
                <el-input-number 
                  v-model="tcpOrientation.ry" 
                  :min="-180" 
                  :max="180" 
                  :step="5" 
                  controls-position="right"
                  @change="updateTCPOrientation"
                ></el-input-number>
              </div>
              <div class="ml-2 flex">
                <button 
                  @click="adjustTCPOrientation('ry', -5)"
                  class="w-8 h-8 bg-gray-200 rounded-l flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-minus"></i>
                </button>
                <button 
                  @click="adjustTCPOrientation('ry', 5)"
                  class="w-8 h-8 bg-gray-200 rounded-r flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>
            
            <div class="flex items-center">
              <label class="w-8 font-medium">RZ:</label>
              <div class="flex-1">
                <el-input-number 
                  v-model="tcpOrientation.rz" 
                  :min="-180" 
                  :max="180" 
                  :step="5" 
                  controls-position="right"
                  @change="updateTCPOrientation"
                ></el-input-number>
              </div>
              <div class="ml-2 flex">
                <button 
                  @click="adjustTCPOrientation('rz', -5)"
                  class="w-8 h-8 bg-gray-200 rounded-l flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-minus"></i>
                </button>
                <button 
                  @click="adjustTCPOrientation('rz', 5)"
                  class="w-8 h-8 bg-gray-200 rounded-r flex items-center justify-center hover:bg-gray-300"
                >
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 协调控制 -->
    <div id="coordination-section" class="bg-white rounded-lg shadow p-4 mb-4">
      <h2 class="text-lg font-semibold mb-3 text-secondary flex items-center">
        <i class="fa-solid fa-rotate mr-2"></i> 协调控制
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          :class="[
            'border rounded-md p-4 flex flex-col items-center',
            coordinationMode === 'mirror' ? 'border-primary bg-light-blue' : 'border-gray-200'
          ]"
        >
          <div class="flex items-center justify-center mb-3">
            <i class="fa-solid fa-arrows-left-right-to-line text-gray-600 mr-2"></i>
            <h3 class="font-medium">镜像运动</h3>
          </div>
          <p class="text-sm text-gray-500 text-center mb-3">左右机械臂相对工作空间中心轴对称运动</p>
          <span 
            v-if="coordinationMode === 'mirror'" 
            class="px-3 py-1 bg-success text-white rounded-full flex items-center"
          >
            <i class="fa-solid fa-check mr-1"></i> 当前模式
          </span>
          <button 
            v-else
            @click="setCoordinationMode('mirror')"
            class="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition"
          >
            启动
          </button>
        </div>
        
        <div 
          :class="[
            'border rounded-md p-4 flex flex-col items-center',
            coordinationMode === 'follow' ? 'border-primary bg-light-blue' : 'border-gray-200'
          ]"
        >
          <div class="flex items-center justify-center mb-3">
            <i class="fa-solid fa-people-arrows text-gray-600 mr-2"></i>
            <h3 class="font-medium">跟随运动</h3>
          </div>
          <p class="text-sm text-gray-500 text-center mb-3">左臂跟随右臂运动，保持相对位置关系</p>
          <span 
            v-if="coordinationMode === 'follow'" 
            class="px-3 py-1 bg-success text-white rounded-full flex items-center"
          >
            <i class="fa-solid fa-check mr-1"></i> 当前模式
          </span>
          <button 
            v-else
            @click="setCoordinationMode('follow')"
            class="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition"
          >
            启动
          </button>
        </div>
        
        <div 
          :class="[
            'border rounded-md p-4 flex flex-col items-center',
            coordinationMode === 'independent' ? 'border-primary bg-light-blue' : 'border-gray-200'
          ]"
        >
          <div class="flex items-center justify-center mb-3">
            <i class="fa-solid fa-diagram-project text-primary mr-2"></i>
            <h3 class="font-medium">独立运动</h3>
          </div>
          <p class="text-sm text-gray-500 text-center mb-3">左右机械臂完全独立控制，无协调关系</p>
          <span 
            v-if="coordinationMode === 'independent'" 
            class="px-3 py-1 bg-success text-white rounded-full flex items-center"
          >
            <i class="fa-solid fa-check mr-1"></i> 当前模式
          </span>
          <button 
            v-else
            @click="setCoordinationMode('independent')"
            class="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition"
          >
            启动
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 类型定义
interface Position {
  x: number
  y: number
  z: number
}

interface ArmStatus {
  position: Position
  speed: number
  force: Position
  temperature: number
}

interface Joint {
  current: number
  target: number
  min: number
  max: number
}

// 控制模式
const controlMode = ref<'manual' | 'auto' | 'teach' | 'force'>('manual')

// 当前操作的机械臂
const currentArm = ref<'left' | 'right'>('right')

// 协调控制模式
const coordinationMode = ref<'mirror' | 'follow' | 'independent'>('independent')

// 双臂状态
const rightArm = reactive<ArmStatus>({
  position: { x: 400, y: 0, z: 300 },
  speed: 0.1,
  force: { x: 0.1, y: 0.2, z: 0.3 },
  temperature: 25
})

const leftArm = reactive<ArmStatus>({
  position: { x: -400, y: 0, z: 300 },
  speed: 0.1,
  force: { x: 0.1, y: 0.2, z: 0.3 },
  temperature: 26
})

// 关节角度配置
const joints = ref<Joint[]>([
  { current: 0, target: 0, min: -180, max: 180 },      // J1
  { current: -90, target: -90, min: -120, max: 120 },  // J2
  { current: 90, target: 90, min: -160, max: 160 },    // J3
  { current: 0, target: 0, min: -180, max: 180 },      // J4
  { current: 90, target: 90, min: -120, max: 120 },    // J5
  { current: 0, target: 0, min: -180, max: 180 }       // J6
])

// TCP位置和姿态
const tcpPosition = reactive<Position>({
  x: 400,
  y: 0,
  z: 300
})

const tcpOrientation = reactive({
  rx: 0,
  ry: 0,
  rz: 0
})

// 计算属性
const rightArmStatus = computed(() => '正常运行中')
const leftArmStatus = computed(() => '正常运行中')

// 方法
const emergencyStop = () => {
  ElMessage({
    type: 'warning',
    message: '紧急停止已触发！所有机械臂运动已停止。',
    duration: 3000
  })
  console.log('Emergency stop activated')
}

const switchMode = (mode: 'manual' | 'auto' | 'teach' | 'force') => {
  controlMode.value = mode
  ElMessage({
    type: 'success',
    message: `已切换到${mode === 'manual' ? '手动' : mode === 'auto' ? '自动' : mode === 'teach' ? '示教' : '力控'}模式`,
    duration: 2000
  })
}

const switchArm = () => {
  currentArm.value = currentArm.value === 'right' ? 'left' : 'right'
  ElMessage({
    type: 'info',
    message: `已切换到${currentArm.value === 'right' ? '右臂' : '左臂'}控制`,
    duration: 2000
  })
}

const savePosition = () => {
  ElMessage({
    type: 'success',
    message: '当前位置已保存',
    duration: 2000
  })
  console.log('Position saved:', { joints: joints.value, tcp: tcpPosition, orientation: tcpOrientation })
}

const updateJoint = (index: number, value: number) => {
  joints.value[index].current = value
  console.log(`Joint J${index + 1} updated to:`, value)
}

const updateTCPPosition = () => {
  console.log('TCP Position updated:', tcpPosition)
}

const updateTCPOrientation = () => {
  console.log('TCP Orientation updated:', tcpOrientation)
}

const adjustTCPPosition = (axis: 'x' | 'y' | 'z', delta: number) => {
  tcpPosition[axis] += delta
  updateTCPPosition()
}

const adjustTCPOrientation = (axis: 'rx' | 'ry' | 'rz', delta: number) => {
  tcpOrientation[axis] += delta
  updateTCPOrientation()
}

const setCoordinationMode = (mode: 'mirror' | 'follow' | 'independent') => {
  coordinationMode.value = mode
  ElMessage({
    type: 'success',
    message: `协调控制模式已切换到${mode === 'mirror' ? '镜像运动' : mode === 'follow' ? '跟随运动' : '独立运动'}`,
    duration: 2000
  })
  console.log('Coordination mode set to:', mode)
}
</script>

<style scoped>
.emergency-stop-btn {
  background: radial-gradient(circle, #F56C6C 60%, #cf4f4f 100%);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
}

.emergency-stop-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.emergency-stop-btn:active {
  transform: scale(0.95);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.light-blue {
  background-color: #ECF5FF;
}

/* Element Plus Slider 样式覆盖 */
:deep(.el-slider__runway) {
  height: 6px;
}

:deep(.el-slider__bar) {
  height: 6px;
  background-color: #409EFF;
}

:deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  border: 2px solid #409EFF;
}
</style>
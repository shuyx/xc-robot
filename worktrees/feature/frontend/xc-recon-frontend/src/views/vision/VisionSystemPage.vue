<template>
  <div class="w-full h-full bg-gray-50 p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex items-center mb-2">
        <i class="fa-solid fa-video text-success text-2xl mr-3"></i>
        <h1 class="text-2xl font-bold text-secondary">多相机视觉系统</h1>
      </div>
      <p class="text-gray-600 ml-9">2D/3D视觉感知与图像处理</p>
    </div>

    <!-- Camera Preview Section -->
    <div class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-camera text-success mr-2"></i>
        <h2 class="text-lg font-semibold text-secondary">相机预览区</h2>
        <div class="ml-auto flex space-x-2">
          <button 
            @click="toggleGridView"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center"
          >
            <i class="fa-solid fa-table-cells mr-1"></i> 网格视图
          </button>
          <button 
            @click="toggleExpandedView"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm flex items-center"
          >
            <i class="fa-solid fa-expand mr-1"></i> 扩展视图
          </button>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Camera Components -->
        <div 
          v-for="camera in cameras" 
          :key="camera.id" 
          class="camera-preview bg-white rounded-lg border border-previewBorder shadow-sm overflow-hidden"
        >
          <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
            <div class="flex items-center">
              <i :class="[camera.icon, camera.status === 'online' ? 'text-success' : 'text-danger', 'mr-2']"></i>
              <span class="font-medium">{{ camera.name }}</span>
              <span class="ml-2 flex items-center">
                <span :class="['status-dot', getStatusClass(camera.status)]"></span>
                <span :class="['text-xs', camera.status === 'online' ? 'text-success' : 'text-danger']">
                  {{ getStatusText(camera.status) }}
                </span>
              </span>
            </div>
            <div class="flex space-x-2">
              <button 
                @click="expandCamera(camera.id)"
                class="text-gray-500 hover:text-primary"
              >
                <i class="fa-solid fa-expand"></i>
              </button>
              <button 
                @click="openCameraSettings(camera.id)"
                class="text-gray-500 hover:text-primary"
              >
                <i class="fa-solid fa-gear"></i>
              </button>
            </div>
          </div>
          
          <!-- Camera Feed Display -->
          <div class="h-[200px] flex items-center justify-center" :class="camera.status === 'online' ? 'bg-bgLight' : 'bg-gray-100'">
            <img 
              v-if="camera.status === 'online' && camera.imageUrl" 
              :src="camera.imageUrl" 
              :alt="camera.name + ' feed'"
              class="w-full h-full object-cover"
            >
            <div v-else class="text-center text-gray-500">
              <i :class="[camera.offlineIcon, 'text-4xl mb-2']"></i>
              <p>{{ camera.offlineText }}</p>
            </div>
          </div>
          
          <!-- Camera Info and Controls -->
          <div class="p-3 bg-white">
            <div class="flex justify-between text-sm mb-2">
              <span v-if="camera.status === 'online'">分辨率: {{ camera.resolution }}</span>
              <span v-else>状态: {{ camera.error }}</span>
              
              <span v-if="camera.status === 'online'">帧率: {{ camera.fps }}fps</span>
              <span v-else-if="camera.errorCode">错误码: {{ camera.errorCode }}</span>
              <span v-else-if="camera.port">端口: {{ camera.port }}</span>
            </div>
            
            <!-- Camera Control Buttons -->
            <div class="flex space-x-2">
              <button 
                v-if="camera.status === 'online'"
                @click="openCameraSettings(camera.id)"
                class="flex-1 py-1 px-2 text-xs border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
              >
                <i class="fa-solid fa-sliders mr-1"></i> 设置
              </button>
              <button 
                v-if="camera.status === 'online'"
                @click="calibrateCamera(camera.id)"
                class="flex-1 py-1 px-2 text-xs border border-warning rounded text-warning hover:bg-yellow-50"
              >
                <i class="fa-solid fa-crosshairs mr-1"></i> 标定
              </button>
              <button 
                v-if="camera.status === 'online'"
                @click="toggleRecording(camera.id)"
                class="flex-1 py-1 px-2 text-xs border border-primary rounded text-primary hover:bg-blue-50"
              >
                <i class="fa-solid fa-record-vinyl mr-1"></i> 录制
              </button>
              
              <!-- Offline Camera Controls -->
              <button 
                v-if="camera.status === 'offline' && camera.error === '连接失败'"
                @click="reconnectCamera(camera.id)"
                class="flex-1 py-1 px-2 text-xs border border-danger rounded text-danger hover:bg-red-50"
              >
                <i class="fa-solid fa-rotate mr-1"></i> 重连
              </button>
              <button 
                v-if="camera.status === 'offline' && camera.error === '未连接'"
                @click="connectCamera(camera.id)"
                class="flex-1 py-1 px-2 text-xs border border-primary rounded text-primary hover:bg-blue-50"
              >
                <i class="fa-solid fa-plug mr-1"></i> 连接
              </button>
              <button 
                v-if="camera.status === 'offline'"
                @click="diagnoseCamera(camera.id)"
                class="flex-1 py-1 px-2 text-xs border border-warning rounded text-warning hover:bg-yellow-50"
              >
                <i class="fa-solid fa-stethoscope mr-1"></i> 诊断
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tools and Results Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <!-- Image Processing Tools -->
      <div class="col-span-1">
        <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
            <div class="flex items-center">
              <i class="fa-solid fa-wand-magic-sparkles text-primary mr-2"></i>
              <span class="font-medium">图像处理工具</span>
            </div>
            <div>
              <button 
                @click="openProcessingSettings"
                class="text-gray-500 hover:text-primary"
              >
                <i class="fa-solid fa-gear"></i>
              </button>
            </div>
          </div>
          <div class="p-4">
            <div class="grid grid-cols-2 gap-3 mb-4">
              <button 
                v-for="tool in processingTools" 
                :key="tool.id"
                @click="applyProcessingTool(tool.id)"
                class="tool-btn bg-white border border-primary text-primary rounded-md py-2 px-3 flex items-center justify-center hover:bg-blue-50 text-sm"
              >
                <i :class="[tool.icon, 'mr-2']"></i>
                {{ tool.name }}
              </button>
            </div>
            
            <!-- Parameter Settings -->
            <div class="mt-6">
              <h3 class="text-sm font-medium mb-3 flex items-center">
                <i class="fa-solid fa-sliders text-success mr-2"></i>
                参数设置
              </h3>
              <div class="space-y-3">
                <div>
                  <label class="text-xs text-gray-600 block mb-1">阈值</label>
                  <el-slider 
                    v-model="processingParams.threshold" 
                    :min="0" 
                    :max="100" 
                    :step="1"
                    @change="updateProcessingParams"
                  ></el-slider>
                  <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0</span>
                    <span>{{ processingParams.threshold }}</span>
                    <span>100</span>
                  </div>
                </div>
                <div>
                  <label class="text-xs text-gray-600 block mb-1">平滑度</label>
                  <el-slider 
                    v-model="processingParams.smoothness" 
                    :min="0" 
                    :max="100" 
                    :step="1"
                    @change="updateProcessingParams"
                  ></el-slider>
                  <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0</span>
                    <span>{{ processingParams.smoothness }}</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detection Results -->
      <div class="col-span-1">
        <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
            <div class="flex items-center">
              <i class="fa-solid fa-chart-simple text-primary mr-2"></i>
              <span class="font-medium">检测结果</span>
            </div>
            <div>
              <button 
                @click="exportResults"
                class="text-gray-500 hover:text-primary"
              >
                <i class="fa-solid fa-file-export"></i>
              </button>
            </div>
          </div>
          <div class="p-4">
            <!-- Detection Objects -->
            <div class="mb-4">
              <h3 class="text-sm font-medium mb-2 flex items-center">
                <i class="fa-solid fa-bullseye text-success mr-2"></i>
                检测到目标
              </h3>
              <ul class="space-y-2 text-sm">
                <li v-for="detection in detectionResults.objects" :key="detection.type" class="flex items-center">
                  <i class="fa-solid fa-circle text-xs text-primary mr-2"></i>
                  <span>{{ detection.label }}: </span>
                  <span class="ml-1 font-medium">{{ detection.count }}{{ detection.unit }}</span>
                  <span :class="['ml-auto text-xs', getConfidenceClass(detection.confidence)]">
                    {{ detection.confidence }}%
                  </span>
                </li>
              </ul>
            </div>
            
            <!-- Distance Measurements -->
            <div class="mb-4">
              <h3 class="text-sm font-medium mb-2 flex items-center">
                <i class="fa-solid fa-ruler text-success mr-2"></i>
                距离测量
              </h3>
              <ul class="space-y-2 text-sm">
                <li class="flex items-center">
                  <i class="fa-solid fa-circle text-xs text-primary mr-2"></i>
                  <span>最近物体: </span>
                  <span class="ml-1 font-medium">{{ detectionResults.nearestObject }}m</span>
                </li>
                <li class="flex items-center">
                  <i class="fa-solid fa-circle text-xs text-primary mr-2"></i>
                  <span>最远物体: </span>
                  <span class="ml-1 font-medium">{{ detectionResults.farthestObject }}m</span>
                </li>
              </ul>
            </div>
            
            <!-- Object Classification -->
            <div>
              <h3 class="text-sm font-medium mb-2 flex items-center">
                <i class="fa-solid fa-tag text-success mr-2"></i>
                物体分类
              </h3>
              <div class="bg-gray-50 p-2 rounded text-xs">
                <span 
                  v-for="tag in detectionResults.classifications" 
                  :key="tag"
                  class="inline-block px-2 py-1 bg-blue-100 text-primary rounded mr-1 mb-1"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Controls and Performance -->
      <div class="col-span-1">
        <!-- System Controls -->
        <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden mb-4">
          <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
            <div class="flex items-center">
              <i class="fa-solid fa-gears text-success mr-2"></i>
              <span class="font-medium">系统控制</span>
            </div>
            <div>
              <button 
                @click="openSystemSettings"
                class="text-gray-500 hover:text-primary"
              >
                <i class="fa-solid fa-ellipsis-vertical"></i>
              </button>
            </div>
          </div>
          <div class="p-4">
            <div class="grid grid-cols-2 gap-3 mb-3">
              <button 
                @click="startAllCameras"
                class="tool-btn bg-success text-white rounded-md py-2 px-3 flex items-center justify-center hover:bg-opacity-90 text-sm"
              >
                <i class="fa-solid fa-play mr-2"></i>
                全部启动
              </button>
              <button 
                @click="stopAllCameras"
                class="tool-btn bg-danger text-white rounded-md py-2 px-3 flex items-center justify-center hover:bg-opacity-90 text-sm"
              >
                <i class="fa-solid fa-stop mr-2"></i>
                全部停止
              </button>
              <button 
                @click="startSyncRecording"
                class="tool-btn bg-primary text-white rounded-md py-2 px-3 flex items-center justify-center hover:bg-opacity-90 text-sm"
              >
                <i class="fa-solid fa-record-vinyl mr-2"></i>
                同步录制
              </button>
              <button 
                @click="exportAllData"
                class="tool-btn bg-warning text-white rounded-md py-2 px-3 flex items-center justify-center hover:bg-opacity-90 text-sm"
              >
                <i class="fa-solid fa-file-export mr-2"></i>
                导出数据
              </button>
            </div>
            
            <!-- System Status -->
            <div class="mt-4">
              <h3 class="text-sm font-medium mb-2">系统状态</h3>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs">相机连接状态:</span>
                <span class="text-xs font-medium">{{ onlineCamerasCount }}/{{ cameras.length }} 在线</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5 mb-3">
                <div 
                  class="bg-success h-1.5 rounded-full transition-all duration-300" 
                  :style="{ width: (onlineCamerasCount / cameras.length * 100) + '%' }"
                ></div>
              </div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs">存储空间:</span>
                <span class="text-xs font-medium">{{ systemStatus.storageUsed }}GB/{{ systemStatus.storageTotal }}TB</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1.5 mb-3">
                <div 
                  class="bg-warning h-1.5 rounded-full transition-all duration-300" 
                  :style="{ width: systemStatus.storagePercent + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Performance Monitoring -->
        <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
            <div class="flex items-center">
              <i class="fa-solid fa-chart-line text-primary mr-2"></i>
              <span class="font-medium">性能监控</span>
            </div>
            <div>
              <button 
                @click="refreshPerformanceData"
                class="text-gray-500 hover:text-primary"
              >
                <i class="fa-solid fa-arrows-rotate"></i>
              </button>
            </div>
          </div>
          <div class="p-4">
            <div class="space-y-3">
              <div v-for="metric in performanceMetrics" :key="metric.name">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs text-gray-600">{{ metric.label }}</span>
                  <span class="text-xs font-medium">{{ metric.display }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    :class="['h-1.5 rounded-full transition-all duration-300', metric.colorClass]" 
                    :style="{ width: metric.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <div class="mt-4 text-center">
              <span class="text-xs text-gray-500">最后更新: {{ lastUpdateTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 类型定义
interface Camera {
  id: string
  name: string
  status: 'online' | 'offline'
  icon: string
  resolution?: string
  fps?: number
  imageUrl?: string
  error?: string
  errorCode?: string
  port?: string
  offlineIcon: string
  offlineText: string
}

interface ProcessingTool {
  id: string
  name: string
  icon: string
}

interface DetectionObject {
  type: string
  label: string
  count: number
  unit: string
  confidence: number
}

interface DetectionResults {
  objects: DetectionObject[]
  nearestObject: number
  farthestObject: number
  classifications: string[]
}

interface PerformanceMetric {
  name: string
  label: string
  value: number
  max?: number
  display: string
  percentage: number
  colorClass: string
}

// 响应式数据
const cameras = ref<Camera[]>([
  {
    id: '2d-1',
    name: '2D相机1',
    status: 'online',
    icon: 'fa-solid fa-camera-retro',
    resolution: '1920×1080',
    fps: 30,
    imageUrl: 'https://storage.googleapis.com/uxpilot-auth.appspot.com/ff1d8e2a3b-d40f1bed1ff193e0242e.png',
    offlineIcon: 'fa-solid fa-camera-slash',
    offlineText: '相机离线'
  },
  {
    id: 'tof',
    name: 'TOF相机',
    status: 'online',
    icon: 'fa-solid fa-camera',
    resolution: '640×480',
    fps: 30,
    imageUrl: 'https://storage.googleapis.com/uxpilot-auth.appspot.com/dab05402ca-4ff9138df5c98b99ba88.png',
    offlineIcon: 'fa-solid fa-camera-slash',
    offlineText: '相机离线'
  },
  {
    id: 'fisheye',
    name: '鱼眼相机',
    status: 'offline',
    icon: 'fa-solid fa-camera-retro',
    error: '连接失败',
    errorCode: 'E-1024',
    offlineIcon: 'fa-solid fa-camera-slash',
    offlineText: '相机离线'
  },
  {
    id: '2d-2',
    name: '2D相机2',
    status: 'offline',
    icon: 'fa-solid fa-camera',
    error: '未连接',
    port: 'COM3',
    offlineIcon: 'fa-solid fa-plug-circle-xmark',
    offlineText: '相机未连接'
  }
])

const processingTools = ref<ProcessingTool[]>([
  { id: 'edge-detection', name: '边缘检测', icon: 'fa-solid fa-border-all' },
  { id: 'object-detection', name: '目标识别', icon: 'fa-solid fa-object-group' },
  { id: 'feature-extraction', name: '特征提取', icon: 'fa-solid fa-fingerprint' },
  { id: 'motion-detection', name: '运动检测', icon: 'fa-solid fa-person-walking' },
  { id: 'depth-measurement', name: '深度测量', icon: 'fa-solid fa-ruler-vertical' },
  { id: '3d-reconstruction', name: '3D重建', icon: 'fa-solid fa-cube' }
])

const processingParams = reactive({
  threshold: 50,
  smoothness: 30
})

const detectionResults = reactive<DetectionResults>({
  objects: [
    { type: 'face', label: '人脸', count: 2, unit: '个', confidence: 95 },
    { type: 'object', label: '物体', count: 5, unit: '个', confidence: 87 },
    { type: 'text', label: '文字', count: 1, unit: '处', confidence: 76 }
  ],
  nearestObject: 1.2,
  farthestObject: 3.8,
  classifications: ['人', '椅子', '桌子', '显示器', '键盘']
})

const systemStatus = reactive({
  storageUsed: 256,
  storageTotal: 1,
  storagePercent: 25
})

const performanceMetrics = ref<PerformanceMetric[]>([
  { name: 'cpu', label: 'CPU使用率', value: 45, display: '45%', percentage: 45, colorClass: 'bg-primary' },
  { name: 'memory', label: '内存使用', value: 2.1, max: 8, display: '2.1GB/8GB', percentage: 26, colorClass: 'bg-primary' },
  { name: 'latency', label: '处理延迟', value: 25, display: '25ms', percentage: 25, colorClass: 'bg-success' },
  { name: 'bandwidth', label: '网络带宽', value: 15, display: '15Mbps', percentage: 30, colorClass: 'bg-warning' }
])

const lastUpdateTime = ref('2分钟前')

// 计算属性
const onlineCamerasCount = computed(() => 
  cameras.value.filter(camera => camera.status === 'online').length
)

// 方法
const getStatusClass = (status: string) => {
  return status === 'online' ? 'status-online' : 'status-offline'
}

const getStatusText = (status: string) => {
  return status === 'online' ? '在线' : '离线'
}

const getConfidenceClass = (confidence: number) => {
  if (confidence >= 90) return 'text-success'
  if (confidence >= 70) return 'text-warning'
  return 'text-danger'
}

// 相机控制方法
const expandCamera = (cameraId: string) => {
  ElMessage({
    type: 'info',
    message: `展开相机 ${cameraId} 视图`,
    duration: 2000
  })
  console.log(`Expand camera: ${cameraId}`)
}

const openCameraSettings = (cameraId: string) => {
  ElMessage({
    type: 'info',
    message: `打开相机 ${cameraId} 设置`,
    duration: 2000
  })
  console.log(`Open camera settings: ${cameraId}`)
}

const calibrateCamera = (cameraId: string) => {
  ElMessage({
    type: 'info',
    message: `开始标定相机 ${cameraId}`,
    duration: 2000
  })
  console.log(`Calibrate camera: ${cameraId}`)
}

const toggleRecording = (cameraId: string) => {
  ElMessage({
    type: 'success',
    message: `开始录制相机 ${cameraId}`,
    duration: 2000
  })
  console.log(`Toggle recording: ${cameraId}`)
}

const reconnectCamera = (cameraId: string) => {
  ElMessage({
    type: 'info',
    message: `正在重连相机 ${cameraId}...`,
    duration: 2000
  })
  // 模拟重连
  setTimeout(() => {
    const camera = cameras.value.find(c => c.id === cameraId)
    if (camera) {
      camera.status = 'online'
      camera.resolution = '1920×1080'
      camera.fps = 30
      ElMessage({
        type: 'success',
        message: `相机 ${cameraId} 重连成功`,
        duration: 2000
      })
    }
  }, 1500)
}

const connectCamera = (cameraId: string) => {
  ElMessage({
    type: 'info',
    message: `正在连接相机 ${cameraId}...`,
    duration: 2000
  })
  // 模拟连接
  setTimeout(() => {
    const camera = cameras.value.find(c => c.id === cameraId)
    if (camera) {
      camera.status = 'online'
      camera.resolution = '1920×1080'
      camera.fps = 30
      ElMessage({
        type: 'success',
        message: `相机 ${cameraId} 连接成功`,
        duration: 2000
      })
    }
  }, 1500)
}

const diagnoseCamera = (cameraId: string) => {
  ElMessage({
    type: 'info',
    message: `正在诊断相机 ${cameraId}...`,
    duration: 2000
  })
  console.log(`Diagnose camera: ${cameraId}`)
}

// 视图控制方法
const toggleGridView = () => {
  ElMessage({
    type: 'info',
    message: '切换到网格视图',
    duration: 2000
  })
}

const toggleExpandedView = () => {
  ElMessage({
    type: 'info',
    message: '切换到扩展视图',
    duration: 2000
  })
}

// 图像处理方法
const applyProcessingTool = (toolId: string) => {
  const tool = processingTools.value.find(t => t.id === toolId)
  if (tool) {
    ElMessage({
      type: 'success',
      message: `正在应用${tool.name}...`,
      duration: 2000
    })
    console.log(`Apply processing tool: ${toolId}`)
  }
}

const updateProcessingParams = () => {
  console.log('Update processing parameters:', processingParams)
}

const openProcessingSettings = () => {
  ElMessage({
    type: 'info',
    message: '打开图像处理设置',
    duration: 2000
  })
}

// 结果导出方法
const exportResults = () => {
  ElMessage({
    type: 'success',
    message: '正在导出检测结果...',
    duration: 2000
  })
  console.log('Export detection results')
}

// 系统控制方法
const startAllCameras = () => {
  cameras.value.forEach(camera => {
    camera.status = 'online'
    camera.resolution = '1920×1080'
    camera.fps = 30
  })
  ElMessage({
    type: 'success',
    message: '所有相机已启动',
    duration: 2000
  })
}

const stopAllCameras = () => {
  cameras.value.forEach(camera => {
    camera.status = 'offline'
  })
  ElMessage({
    type: 'warning',
    message: '所有相机已停止',
    duration: 2000
  })
}

const startSyncRecording = () => {
  ElMessage({
    type: 'success',
    message: '开始同步录制所有相机',
    duration: 2000
  })
  console.log('Start synchronized recording')
}

const exportAllData = () => {
  ElMessage({
    type: 'success',
    message: '正在导出所有数据...',
    duration: 2000
  })
  console.log('Export all data')
}

const openSystemSettings = () => {
  ElMessage({
    type: 'info',
    message: '打开系统设置',
    duration: 2000
  })
}

const refreshPerformanceData = () => {
  // 模拟性能数据更新
  performanceMetrics.value.forEach(metric => {
    metric.value = Math.random() * (metric.max || 100)
    metric.percentage = metric.max ? (metric.value / metric.max * 100) : metric.value
    
    switch (metric.name) {
      case 'cpu':
        metric.display = `${Math.round(metric.value)}%`
        break
      case 'memory':
        metric.display = `${metric.value.toFixed(1)}GB/${metric.max}GB`
        break
      case 'latency':
        metric.display = `${Math.round(metric.value)}ms`
        break
      case 'bandwidth':
        metric.display = `${Math.round(metric.value)}Mbps`
        break
    }
  })
  
  lastUpdateTime.value = '刚刚'
  ElMessage({
    type: 'success',
    message: '性能数据已刷新',
    duration: 1000
  })
}

// 生命周期
onMounted(() => {
  console.log('Vision System Page mounted')
})
</script>

<style scoped>
.camera-preview {
  transition: all 0.3s ease;
}

.camera-preview:hover {
  transform: scale(1.02);
}

.tool-btn {
  transition: all 0.2s ease;
}

.tool-btn:hover {
  transform: translateY(-2px);
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
}

.status-online {
  background-color: #00A870;
  box-shadow: 0 0 5px #00A870;
}

.status-offline {
  background-color: #F56C6C;
  box-shadow: 0 0 5px #F56C6C;
}

.status-connecting {
  background-color: #E6A23C;
  box-shadow: 0 0 5px #E6A23C;
}

.status-unknown {
  background-color: #909399;
  box-shadow: 0 0 5px #909399;
}

.status-info {
  background-color: #409EFF;
  box-shadow: 0 0 5px #409EFF;
}

.bgLight {
  background-color: #F0F9F5;
}

.border-previewBorder {
  border-color: #E8F4FD;
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
<template>
  <div id="app" class="w-full h-[calc(100vh-100px)] bg-gray-50 p-6 overflow-y-auto">
    <!-- Page Header -->
    <div id="page-header" class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">人脸识别系统</h1>
      <p class="text-sm text-gray-500">基于深度学习的实时人脸识别与分析</p>
    </div>

    <!-- Main Content -->
    <div id="main-content" class="grid grid-cols-12 gap-6">
      <!-- Camera Preview Section -->
      <div id="camera-preview" class="col-span-12 lg:col-span-7 bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="flex justify-between items-center px-4 py-3 border-b border-gray-100">
          <div class="flex items-center">
            <i class="fa-solid fa-video text-primary mr-2"></i>
            <h2 class="font-semibold">相机预览区</h2>
          </div>
          <div>
            <button class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded">
              <i class="fa-solid fa-expand"></i>
            </button>
          </div>
        </div>
        
        <div class="p-4">
          <div class="flex items-center mb-3">
            <i class="fa-solid fa-camera text-primary mr-2"></i>
            <el-select v-model="selectedCamera" size="small" style="width: 120px;">
              <el-option label="前置相机" value="前置相机"></el-option>
              <el-option label="后置相机" value="后置相机"></el-option>
              <el-option label="TOF相机" value="TOF相机"></el-option>
            </el-select>
          </div>
          
          <div id="video-container" class="relative bg-light rounded-lg h-[320px] mb-4 flex items-center justify-center overflow-hidden">
            <!-- Video placeholder -->
            <div class="absolute inset-0 flex items-center justify-center">
              <img class="w-full h-full object-cover" src="https://storage.googleapis.com/uxpilot-auth.appspot.com/d590cfb88c-7f4867bd1f1f5236957a.png" alt="security camera view with facial recognition box around a person">
            </div>
            
            <!-- Face detection box -->
            <div class="absolute left-[30%] top-[25%] w-[160px] h-[180px] border-2 border-success rounded-md flex flex-col items-center justify-between">
              <div class="bg-success text-white text-xs px-2 py-0.5 rounded mt-1">
                Kevin Yuan
              </div>
              <div class="bg-success/80 text-white text-xs px-2 py-0.5 rounded mb-1">
                95%
              </div>
            </div>
            
            <!-- Face detection box for unknown person -->
            <div class="absolute right-[20%] top-[40%] w-[140px] h-[160px] border-2 border-warning rounded-md flex flex-col items-center justify-between">
              <div class="bg-warning text-white text-xs px-2 py-0.5 rounded mt-1">
                未知人员
              </div>
              <div class="bg-warning/80 text-white text-xs px-2 py-0.5 rounded mb-1">
                65%
              </div>
            </div>
            
            <!-- Status indicator -->
            <div class="absolute top-2 left-2 flex items-center bg-black/30 text-white text-xs px-2 py-1 rounded">
              <span class="w-2 h-2 bg-success rounded-full mr-2"></span>
              <span>识别中</span>
            </div>
          </div>
          
          <div class="flex space-x-2">
            <button 
              @click="toggleRecognition"
              class="bg-success hover:bg-success/90 text-white px-4 py-2 rounded text-sm flex items-center"
            >
              <i class="fa-solid fa-play mr-1" v-if="!isRecognizing"></i>
              <i class="fa-solid fa-pause mr-1" v-else></i>
              {{ isRecognizing ? '暂停' : '开始' }}
            </button>
            <button 
              @click="stopRecognition"
              class="bg-danger hover:bg-danger/90 text-white px-4 py-2 rounded text-sm flex items-center"
            >
              <i class="fa-solid fa-stop mr-1"></i> 停止
            </button>
            <button 
              @click="captureScreenshot"
              class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded text-sm flex items-center"
            >
              <i class="fa-solid fa-camera mr-1"></i> 截图
            </button>
          </div>
        </div>
      </div>
      
      <!-- Recognition Results Section -->
      <div id="recognition-results" class="col-span-12 lg:col-span-5 bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="flex justify-between items-center px-4 py-3 border-b border-gray-100">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-bar text-primary mr-2"></i>
            <h2 class="font-semibold">识别结果区</h2>
          </div>
          <div>
            <button 
              @click="refreshResults"
              class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded"
            >
              <i class="fa-solid fa-arrows-rotate"></i>
            </button>
          </div>
        </div>
        
        <div class="p-4 h-[400px] overflow-y-auto">
          <h3 class="flex items-center text-sm font-medium mb-3">
            <i class="fa-solid fa-bullseye text-primary mr-2"></i>
            实时检测结果
          </h3>
          
          <!-- Result items -->
          <div 
            v-for="result in recognitionResults" 
            :key="result.id"
            :class="[
              'p-3 mb-3 rounded-r-lg',
              result.known ? 'bg-light border-l-4 border-success' : 'bg-light border-l-4 border-warning'
            ]"
          >
            <div class="flex items-center mb-2">
              <div :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-white mr-2',
                result.known ? 'bg-primary' : 'bg-gray-400'
              ]">
                <i :class="result.known ? 'fa-solid fa-user' : 'fa-solid fa-question'"></i>
              </div>
              <div class="font-medium">{{ result.name }}</div>
              <div :class="[
                'ml-auto text-white text-xs px-2 py-0.5 rounded',
                result.known ? 'bg-success' : 'bg-warning'
              ]">
                {{ result.known ? '已识别' : '未识别' }}
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs text-gray-600">
              <div class="flex items-center">
                <i class="fa-solid fa-chart-pie text-info mr-1"></i>
                置信度: <span class="ml-1 font-medium">{{ result.confidence }}%</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-calendar text-info mr-1"></i>
                年龄: <span class="ml-1 font-medium">~{{ result.age }}岁</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-venus-mars text-info mr-1"></i>
                性别: <span class="ml-1 font-medium">{{ result.gender }}</span>
              </div>
              <div class="flex items-center">
                <i class="fa-solid fa-face-smile text-info mr-1"></i>
                情绪: <span class="ml-1 font-medium">{{ result.emotion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Statistics Section -->
      <div id="statistics" class="col-span-12 lg:col-span-7 grid grid-cols-4 gap-4">
        <!-- Stat Card 1 -->
        <div id="stat-card-1" class="bg-white rounded-lg shadow-sm p-4">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium">今日识别</h3>
            <i class="fa-solid fa-users text-primary"></i>
          </div>
          <div class="text-2xl font-bold">{{ dailyStats.totalRecognitions }}<span class="text-sm font-normal text-gray-500 ml-1">次</span></div>
          <div class="text-xs text-success mt-1">
            <i class="fa-solid fa-arrow-up"></i> {{ dailyStats.recognitionGrowth }}% 较昨日
          </div>
        </div>
        
        <!-- Stat Card 2 -->
        <div id="stat-card-2" class="bg-white rounded-lg shadow-sm p-4">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium">平均置信度</h3>
            <i class="fa-solid fa-percent text-primary"></i>
          </div>
          <div class="text-2xl font-bold">{{ dailyStats.avgConfidence }}<span class="text-sm font-normal text-gray-500 ml-1">%</span></div>
          <div class="text-xs text-success mt-1">
            <i class="fa-solid fa-arrow-up"></i> {{ dailyStats.confidenceGrowth }}% 较昨日
          </div>
        </div>
        
        <!-- Stat Card 3 -->
        <div id="stat-card-3" class="bg-white rounded-lg shadow-sm p-4">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium">识别人数</h3>
            <i class="fa-solid fa-user-check text-primary"></i>
          </div>
          <div class="text-2xl font-bold">{{ dailyStats.uniquePeople }}<span class="text-sm font-normal text-gray-500 ml-1">人</span></div>
          <div class="text-xs text-gray-500 mt-1">
            <i class="fa-solid fa-minus"></i> 与昨日持平
          </div>
        </div>
        
        <!-- Stat Card 4 -->
        <div id="stat-card-4" class="bg-white rounded-lg shadow-sm p-4">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium">平均耗时</h3>
            <i class="fa-solid fa-clock text-primary"></i>
          </div>
          <div class="text-2xl font-bold">{{ dailyStats.avgProcessingTime }}<span class="text-sm font-normal text-gray-500 ml-1">ms</span></div>
          <div class="text-xs text-success mt-1">
            <i class="fa-solid fa-arrow-down"></i> {{ dailyStats.timeImprovement }}% 较昨日
          </div>
        </div>
      </div>
      
      <!-- Operations Section -->
      <div id="operations" class="col-span-12 lg:col-span-5 bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="flex justify-between items-center px-4 py-3 border-b border-gray-100">
          <div class="flex items-center">
            <i class="fa-solid fa-sliders text-primary mr-2"></i>
            <h2 class="font-semibold">操作区</h2>
          </div>
        </div>
        
        <div class="p-4 grid grid-cols-2 gap-3">
          <button 
            @click="saveRecords"
            class="bg-primary hover:bg-primary/90 text-white px-3 py-2 rounded text-sm flex items-center justify-center"
          >
            <i class="fa-solid fa-save mr-1"></i> 保存记录
          </button>
          <button 
            @click="clearResults"
            class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 rounded text-sm flex items-center justify-center"
          >
            <i class="fa-solid fa-broom mr-1"></i> 清空结果
          </button>
          <button 
            @click="exportData"
            class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 rounded text-sm flex items-center justify-center"
          >
            <i class="fa-solid fa-file-export mr-1"></i> 导出数据
          </button>
          <button 
            @click="addPerson"
            class="bg-success hover:bg-success/90 text-white px-3 py-2 rounded text-sm flex items-center justify-center"
          >
            <i class="fa-solid fa-user-plus mr-1"></i> 添加人员
          </button>
          <button 
            @click="managePersonnel"
            class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 rounded text-sm flex items-center justify-center"
          >
            <i class="fa-solid fa-address-card mr-1"></i> 人员管理
          </button>
          <button 
            @click="openSystemSettings"
            class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 rounded text-sm flex items-center justify-center"
          >
            <i class="fa-solid fa-gear mr-1"></i> 系统设置
          </button>
        </div>
        
        <!-- System Status -->
        <div class="px-4 py-3 border-t border-gray-100">
          <h3 class="text-sm font-medium mb-3">系统状态</h3>
          <div class="flex flex-col space-y-2">
            <div 
              v-for="status in systemStatus" 
              :key="status.component"
              class="flex items-center justify-between text-xs"
            >
              <div class="flex items-center">
                <span :class="[
                  'w-2 h-2 rounded-full mr-2',
                  status.status === '正常' ? 'bg-success' : 
                  status.status === '负载高' ? 'bg-warning' : 'bg-danger'
                ]"></span>
                <span>{{ status.component }}</span>
              </div>
              <span :class="[
                status.status === '正常' ? 'text-success' : 
                status.status === '负载高' ? 'text-warning' : 'text-danger'
              ]">{{ status.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'

// 识别状态
const isRecognizing = ref(false)
const recognitionThreshold = ref(85)
const detectionFps = ref(15)
const selectedCamera = ref('tof_camera')

// Mock检测到的人脸数据
const detectedFaces = ref<Array<{
  id: number
  name: string
  confidence: number
  x: number
  y: number
  width: number
  height: number
}>>([])

// Mock识别记录
const recentResults = ref([
  {
    id: 1,
    name: 'Kevin Yuan',
    confidence: 95,
    timestamp: '2025-07-19 15:30:25'
  },
  {
    id: 2,
    name: '访客',
    confidence: 78,
    timestamp: '2025-07-19 15:28:15'
  },
  {
    id: 3,
    name: 'Kevin Yuan',
    confidence: 92,
    timestamp: '2025-07-19 15:25:08'
  },
  {
    id: 4,
    name: '未知人员',
    confidence: 65,
    timestamp: '2025-07-19 15:22:30'
  }
])

// 实时识别结果（模板中需要的 recognitionResults）
const recognitionResults = ref([
  {
    id: 1,
    name: 'Kevin Yuan',
    confidence: 95,
    age: 28,
    gender: '男性',
    emotion: '中性',
    known: true
  },
  {
    id: 2,
    name: '未知人员',
    confidence: 65,
    age: 35,
    gender: '女性',
    emotion: '微笑',
    known: false
  }
])

// 今日统计数据（模板中需要的 dailyStats）
const dailyStats = ref({
  totalRecognitions: 125,
  recognitionGrowth: 15,
  avgConfidence: 87,
  confidenceGrowth: 3,
  uniquePeople: 8,
  avgProcessingTime: 45,
  timeImprovement: 12
})

// 系统状态（模板中需要的 systemStatus）
const systemStatus = ref([
  { component: '人脸检测引擎', status: '正常' },
  { component: '特征提取模块', status: '正常' },
  { component: '识别算法', status: '负载高' },
  { component: '数据存储', status: '正常' },
  { component: '网络连接', status: '正常' }
])

// 统计数据
const totalRecognitions = computed(() => recentResults.value.length)
const uniquePersons = computed(() => {
  const uniqueNames = new Set(recentResults.value.map(r => r.name))
  return uniqueNames.size
})
const averageConfidence = computed(() => {
  const sum = recentResults.value.reduce((acc, result) => acc + result.confidence, 0)
  return Math.round(sum / recentResults.value.length)
})

let recognitionInterval: number | null = null

// 切换识别状态
const toggleRecognition = () => {
  isRecognizing.value = !isRecognizing.value
  
  if (isRecognizing.value) {
    startMockRecognition()
    ElMessage.success('人脸识别已启动')
  } else {
    stopMockRecognition()
    ElMessage.info('人脸识别已停止')
  }
}

// 启动Mock识别
const startMockRecognition = () => {
  // 模拟检测到人脸
  const mockFaces = [
    {
      id: 1,
      name: 'Kevin Yuan',
      confidence: 95,
      x: 25,
      y: 20,
      width: 30,
      height: 40
    }
  ]
  
  detectedFaces.value = mockFaces
  
  // 模拟实时识别结果更新
  recognitionInterval = setInterval(() => {
    // 随机更新置信度
    detectedFaces.value.forEach(face => {
      face.confidence = Math.floor(Math.random() * 15) + 85 // 85-99%
    })
  }, 1000)
}

// 停止识别
const stopRecognition = () => {
  isRecognizing.value = false
  stopMockRecognition()
  ElMessage.info('人脸识别已停止')
}

// 停止Mock识别
const stopMockRecognition = () => {
  detectedFaces.value = []
  if (recognitionInterval) {
    clearInterval(recognitionInterval)
    recognitionInterval = null
  }
}

// 获取置信度标签类型
const getConfidenceType = (confidence: number) => {
  if (confidence >= 90) return 'success'
  if (confidence >= 75) return 'warning'
  return 'danger'
}

// 保存截图
const saveSnapshot = () => {
  ElMessage.success('截图已保存到本地')
}

// 截图功能
const captureScreenshot = () => {
  ElMessage.success('截图已保存到本地')
}

// 刷新结果
const refreshResults = () => {
  ElMessage.success('识别结果已刷新')
}

// 保存记录
const saveRecords = () => {
  ElMessage.success('识别记录已保存')
}

// 清空结果
const clearResults = () => {
  if (confirm('确定要清空所有识别结果吗？')) {
    recognitionResults.value = []
    ElMessage.success('识别结果已清空')
  }
}

// 导出数据
const exportData = () => {
  ElMessage.success('数据已导出为CSV文件')
}

// 添加人员
const addPerson = () => {
  ElMessage.info('打开添加人员对话框')
}

// 人员管理
const managePersonnel = () => {
  ElMessage.info('跳转到人员管理页面')
}

// 系统设置
const openSystemSettings = () => {
  ElMessage.info('打开系统设置')
}

// 导出识别记录
const exportResults = () => {
  ElMessage.success('识别记录已导出为CSV文件')
}

onMounted(() => {
  console.log('人脸识别页面已加载')
})

onUnmounted(() => {
  if (recognitionInterval) {
    clearInterval(recognitionInterval)
  }
})
</script>

<style scoped>
.face-recognition-page {
  padding: 20px;
}

.main-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.camera-section, .results-section {
  height: 400px;
  margin-bottom: 20px;
}

.camera-container {
  height: 320px;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.video-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.mock-camera {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #f0f2f5, #e4e7ed);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.mock-camera.recognition-active {
  background: linear-gradient(45deg, #e6f7ff, #d6f7da);
}

.camera-placeholder {
  text-align: center;
  color: #909399;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.detection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.face-box {
  position: absolute;
  border: 2px solid #67c23a;
  border-radius: 4px;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.3);
}

.face-label {
  position: absolute;
  top: -30px;
  left: 0;
  background: #67c23a;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.confidence {
  margin-left: 5px;
  opacity: 0.9;
}

.live-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(245, 108, 108, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.recognition-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.results-list {
  max-height: 200px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.result-item:last-child {
  border-bottom: none;
}

.result-info {
  flex: 1;
}

.result-name {
  font-weight: 500;
  color: #2c3e50;
}

.result-time {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.control-panel {
  margin-top: 20px;
}

.control-item {
  margin-bottom: 15px;
}

.control-item label {
  display: block;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .face-recognition-page {
    padding: 10px;
  }
  
  .camera-section, .results-section {
    height: auto;
    min-height: 300px;
  }
  
  .recognition-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-value {
    font-size: 20px;
  }
}
</style>
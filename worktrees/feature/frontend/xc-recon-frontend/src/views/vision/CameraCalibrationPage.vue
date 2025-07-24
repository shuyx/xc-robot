<template>
  <div class="w-full h-full bg-gray-50 p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <div class="flex items-center mb-2">
        <i class="fa-solid fa-crosshairs text-success text-2xl mr-3"></i>
        <h1 class="text-2xl font-bold text-secondary">相机标定系统</h1>
      </div>
      <p class="text-gray-600 ml-9">相机内参外参标定与精度验证</p>
    </div>

    <!-- Top Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <!-- Preview Area -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden md:col-span-2">
        <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
          <div class="flex items-center">
            <i class="fa-solid fa-video text-success mr-2"></i>
            <span class="font-semibold text-secondary">标定预览区</span>
          </div>
          <div>
            <el-select v-model="selectedCamera" size="small" style="width: 120px">
              <el-option label="TOF相机" value="tof"></el-option>
              <el-option label="RGB相机" value="rgb"></el-option>
              <el-option label="双目相机" value="stereo"></el-option>
            </el-select>
          </div>
        </div>
        <div class="p-0">
          <div class="preview-area bg-bgLight rounded-lg h-[300px] relative overflow-hidden">
            <!-- Calibration Board -->
            <div class="calibration-board absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[200px] h-[150px] border-2 border-success">
              <div class="w-full h-full" style="background: repeating-conic-gradient(#fff 0% 25%, #000 0% 50%) 0 0/40px 40px;"></div>
            </div>
            
            <!-- Control Buttons -->
            <div class="absolute bottom-3 left-3 flex space-x-2">
              <button 
                @click="captureImage"
                class="bg-success text-white px-3 py-1 rounded text-sm flex items-center hover:bg-opacity-90"
              >
                <i class="fa-solid fa-camera mr-1"></i> 拍照
              </button>
              <button 
                @click="recheckBoard"
                class="bg-white border border-success text-success px-3 py-1 rounded text-sm flex items-center hover:bg-success hover:text-white"
              >
                <i class="fa-solid fa-rotate mr-1"></i> 重检
              </button>
              <button 
                @click="clearImages"
                class="bg-white border border-danger text-danger px-3 py-1 rounded text-sm flex items-center hover:bg-danger hover:text-white"
              >
                <i class="fa-solid fa-trash-can mr-1"></i> 清空
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Calibration Type Selection -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
          <div class="flex items-center">
            <i class="fa-solid fa-bullseye text-success mr-2"></i>
            <span class="font-semibold text-secondary">标定类型选择</span>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <el-radio v-model="calibrationType" value="intrinsic" class="mr-2">内参标定</el-radio>
            </div>
            <div class="flex items-center mb-2">
              <el-radio v-model="calibrationType" value="extrinsic" class="mr-2">外参标定</el-radio>
            </div>
            <div class="flex items-center">
              <el-radio v-model="calibrationType" value="handEye" class="mr-2">手眼标定</el-radio>
            </div>
          </div>
          
          <div class="mt-6">
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-ruler-combined text-success mr-2"></i> 标定板规格:
            </h3>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">类型:</label>
              <el-select v-model="boardType" size="small" class="w-full">
                <el-option label="棋盘格" value="chessboard"></el-option>
                <el-option label="圆点阵列" value="circles"></el-option>
                <el-option label="AprilTag" value="apriltag"></el-option>
                <el-option label="ChArUco" value="charuco"></el-option>
              </el-select>
            </div>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">尺寸:</label>
              <el-input v-model="boardSize" size="small" placeholder="9x6"></el-input>
            </div>
            <div class="mb-4">
              <label class="block text-sm mb-1 text-gray-600">边长:</label>
              <el-input v-model="squareSize" size="small" placeholder="20mm"></el-input>
            </div>
            
            <button 
              @click="detectCalibrationBoard"
              class="w-full bg-success text-white py-2 px-3 rounded hover:bg-opacity-90"
            >
              检测标定板
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Section -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden mb-6">
      <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
        <div class="flex items-center">
          <i class="fa-solid fa-chart-simple text-success mr-2"></i>
          <span class="font-semibold text-secondary">标定进度</span>
        </div>
      </div>
      <div class="p-4">
        <div class="mb-4">
          <div class="flex justify-between mb-2 text-sm">
            <span>📸 已采集图像: {{ capturedImages }}/{{ totalImages }}张</span>
            <span>{{ Math.round((capturedImages / totalImages) * 100) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              class="bg-primary h-2.5 rounded-full transition-all duration-300" 
              :style="{ width: (capturedImages / totalImages * 100) + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="mt-4">
          <h3 class="font-semibold mb-2 text-secondary">图像质量评估:</h3>
          <div class="grid grid-cols-3 gap-2 text-sm">
            <div v-for="(image, index) in imageQualityList" :key="index" class="flex items-center">
              <span class="text-gray-600">图像 {{ image.id }}:</span>
              <span 
                :class="[
                  'ml-1',
                  image.quality === '优秀' ? 'text-success' :
                  image.quality === '良好' ? 'text-success' :
                  image.quality === '一般' ? 'text-warning' : 'text-danger'
                ]"
              >
                {{ image.quality === '优秀' || image.quality === '良好' ? '✅' : '⚠️' }} {{ image.quality }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="p-3 border-t bg-gray-50 flex justify-end space-x-2">
        <button 
          @click="deleteImages"
          class="bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-50"
        >
          删除图像
        </button>
        <button 
          @click="recaptureImages"
          class="bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-50"
        >
          重新采集
        </button>
        <button 
          @click="analyzeQuality"
          class="bg-success text-white px-3 py-1 rounded text-sm hover:bg-opacity-90"
        >
          质量分析
        </button>
      </div>
    </div>

    <!-- Bottom Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <!-- Calibration Results -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-line text-success mr-2"></i>
            <span class="font-semibold text-secondary">标定结果</span>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-ruler text-success mr-2"></i> 内参矩阵:
            </h3>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">fx:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.intrinsics.fx }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">fy:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.intrinsics.fy }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">cx:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.intrinsics.cx }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">cy:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.intrinsics.cy }}</span>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-hurricane text-success mr-2"></i> 畸变系数:
            </h3>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">k1:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.distortion.k1 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">k2:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.distortion.k2 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">p1:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.distortion.p1 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">p2:</span>
                <span class="font-semibold text-secondary">{{ calibrationResults.distortion.p2 }}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-chart-bar text-success mr-2"></i> 标定精度:
            </h3>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">重投影误差:</span>
                <span class="font-semibold text-success">{{ calibrationResults.accuracy.reprojectionError }}像素</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">均方根误差:</span>
                <span class="font-semibold text-success">{{ calibrationResults.accuracy.rmsError }}像素</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">标定置信度:</span>
                <span class="font-semibold text-success">{{ calibrationResults.accuracy.confidence }}%</span>
              </div>
            </div>
          </div>
        </div>
        <div class="p-3 border-t bg-gray-50 flex justify-end space-x-2">
          <button 
            @click="viewDetails"
            class="bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-50"
          >
            查看详情
          </button>
          <button 
            @click="verifyCalibration"
            class="bg-success text-white px-3 py-1 rounded text-sm hover:bg-opacity-90"
          >
            验证
          </button>
        </div>
      </div>

      <!-- Calibration Configuration -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
          <div class="flex items-center">
            <i class="fa-solid fa-wrench text-success mr-2"></i>
            <span class="font-semibold text-secondary">标定配置</span>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-bullseye text-success mr-2"></i> 检测参数:
            </h3>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">检测阈值:</label>
              <el-input v-model="detectionParams.threshold" size="small" placeholder="0.5"></el-input>
            </div>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">最小角点:</label>
              <el-input v-model="detectionParams.minCorners" size="small" placeholder="6"></el-input>
            </div>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">边缘长度:</label>
              <el-input v-model="detectionParams.edgeLength" size="small" placeholder="20"></el-input>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-chart-pie text-success mr-2"></i> 算法选择:
            </h3>
            <el-select v-model="algorithmType" size="small" class="w-full">
              <el-option label="Zhang方法" value="zhang"></el-option>
              <el-option label="Tsai方法" value="tsai"></el-option>
              <el-option label="DLT方法" value="dlt"></el-option>
              <el-option label="PnP方法" value="pnp"></el-option>
            </el-select>
          </div>
          
          <div>
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-arrows-rotate text-success mr-2"></i> 迭代设置:
            </h3>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">最大迭代:</label>
              <el-input v-model="iterationSettings.maxIterations" size="small" placeholder="100"></el-input>
            </div>
            <div class="mb-2">
              <label class="block text-sm mb-1 text-gray-600">精度阈值:</label>
              <el-input v-model="iterationSettings.precision" size="small" placeholder="0.01"></el-input>
            </div>
          </div>
        </div>
        <div class="p-3 border-t bg-gray-50 flex justify-end space-x-2">
          <button 
            @click="resetToDefault"
            class="bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-50"
          >
            恢复默认
          </button>
          <button 
            @click="openAdvancedSettings"
            class="bg-success text-white px-3 py-1 rounded text-sm hover:bg-opacity-90"
          >
            高级
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Section 2 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Accuracy Verification -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
          <div class="flex items-center">
            <i class="fa-solid fa-flask text-success mr-2"></i>
            <span class="font-semibold text-secondary">精度验证</span>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-bullseye text-success mr-2"></i> 验证测试:
            </h3>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">测试点数:</span>
                <span class="font-semibold text-secondary">{{ verification.testPoints }}个</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">平均误差:</span>
                <span class="font-semibold text-success">{{ verification.avgError }}像素</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">最大误差:</span>
                <span class="font-semibold text-warning">{{ verification.maxError }}像素</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">标准差:</span>
                <span class="font-semibold text-success">{{ verification.stdDev }}像素</span>
              </div>
            </div>
          </div>
          
          <div>
            <h3 class="font-semibold mb-2 flex items-center text-secondary">
              <i class="fa-solid fa-bullseye text-success mr-2"></i> 测试结果:
            </h3>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">状态:</span>
                <span class="font-semibold text-success">✅ {{ verification.status }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">推荐状态:</span>
                <span class="font-semibold text-success">{{ verification.recommendation }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="p-3 border-t bg-gray-50 flex justify-end space-x-2">
          <button 
            @click="reverifyCalibration"
            class="bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-50"
          >
            重新验证
          </button>
          <button 
            @click="generateReport"
            class="bg-success text-white px-3 py-1 rounded text-sm hover:bg-opacity-90"
          >
            生成报告
          </button>
        </div>
      </div>

      <!-- Error Analysis -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="p-3 flex items-center justify-between bg-gray-50 border-b">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-area text-success mr-2"></i>
            <span class="font-semibold text-secondary">误差分析</span>
          </div>
        </div>
        <div class="p-4">
          <h3 class="font-semibold mb-2 flex items-center text-secondary">
            <i class="fa-solid fa-chart-line text-success mr-2"></i> 误差分布图:
          </h3>
          <div class="h-[150px] bg-gray-50 rounded flex items-center justify-center">
            <!-- Mock Chart Area -->
            <div class="text-center text-gray-500">
              <i class="fa-solid fa-chart-scatter text-4xl mb-2"></i>
              <p class="text-sm">误差分布散点图</p>
              <p class="text-xs text-gray-400">显示X/Y轴误差分布</p>
            </div>
          </div>
        </div>
        <div class="p-3 border-t bg-gray-50 flex justify-end space-x-2">
          <button 
            @click="detailedAnalysis"
            class="bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-50"
          >
            详细分析
          </button>
          <button 
            @click="exportAnalysis"
            class="bg-success text-white px-3 py-1 rounded text-sm hover:bg-opacity-90"
          >
            导出
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 类型定义
interface CalibrationResults {
  intrinsics: {
    fx: number
    fy: number
    cx: number
    cy: number
  }
  distortion: {
    k1: number
    k2: number
    p1: number
    p2: number
  }
  accuracy: {
    reprojectionError: number
    rmsError: number
    confidence: number
  }
}

interface ImageQuality {
  id: number
  quality: string
}

interface DetectionParams {
  threshold: string
  minCorners: string
  edgeLength: string
}

interface IterationSettings {
  maxIterations: string
  precision: string
}

interface Verification {
  testPoints: number
  avgError: number
  maxError: number
  stdDev: number
  status: string
  recommendation: string
}

// 响应式数据
const selectedCamera = ref('tof')
const calibrationType = ref('intrinsic')
const boardType = ref('chessboard')
const boardSize = ref('9x6')
const squareSize = ref('20mm')
const algorithmType = ref('zhang')

const capturedImages = ref(15)
const totalImages = ref(20)

const detectionParams = reactive<DetectionParams>({
  threshold: '0.5',
  minCorners: '6',
  edgeLength: '20'
})

const iterationSettings = reactive<IterationSettings>({
  maxIterations: '100',
  precision: '0.01'
})

const calibrationResults = reactive<CalibrationResults>({
  intrinsics: {
    fx: 1234.5,
    fy: 1235.8,
    cx: 320.1,
    cy: 240.3
  },
  distortion: {
    k1: -0.123,
    k2: 0.045,
    p1: 0.001,
    p2: -0.002
  },
  accuracy: {
    reprojectionError: 0.35,
    rmsError: 0.28,
    confidence: 95.2
  }
})

const verification = reactive<Verification>({
  testPoints: 50,
  avgError: 0.31,
  maxError: 0.89,
  stdDev: 0.18,
  status: '通过',
  recommendation: '可用于生产'
})

const imageQualityList = ref<ImageQuality[]>([
  { id: 1, quality: '优秀' },
  { id: 2, quality: '良好' },
  { id: 3, quality: '优秀' },
  { id: 4, quality: '良好' },
  { id: 5, quality: '优秀' },
  { id: 6, quality: '良好' },
  { id: 7, quality: '一般' },
  { id: 8, quality: '优秀' },
  { id: 9, quality: '良好' },
  { id: 10, quality: '优秀' },
  { id: 11, quality: '优秀' },
  { id: 12, quality: '良好' },
  { id: 13, quality: '优秀' },
  { id: 14, quality: '一般' },
  { id: 15, quality: '良好' }
])

// 预览区控制方法
const captureImage = () => {
  if (capturedImages.value < totalImages.value) {
    capturedImages.value++
    ElMessage({
      type: 'success',
      message: `拍照完成，已采集 ${capturedImages.value}/${totalImages.value} 张图像`,
      duration: 2000
    })
  } else {
    ElMessage({
      type: 'warning',
      message: '已达到目标采集数量',
      duration: 2000
    })
  }
}

const recheckBoard = () => {
  ElMessage({
    type: 'info',
    message: '正在重新检测标定板...',
    duration: 2000
  })
  console.log('Recheck calibration board')
}

const clearImages = () => {
  capturedImages.value = 0
  ElMessage({
    type: 'warning',
    message: '已清空所有采集图像',
    duration: 2000
  })
  console.log('Clear all captured images')
}

// 标定板检测
const detectCalibrationBoard = () => {
  ElMessage({
    type: 'info',
    message: `正在检测${boardType.value}标定板...`,
    duration: 2000
  })
  console.log(`Detect calibration board: ${boardType.value}`)
}

// 进度管理方法
const deleteImages = () => {
  ElMessage({
    type: 'warning',
    message: '已删除选中图像',
    duration: 2000
  })
  console.log('Delete selected images')
}

const recaptureImages = () => {
  ElMessage({
    type: 'info',
    message: '重新采集低质量图像',
    duration: 2000
  })
  console.log('Recapture poor quality images')
}

const analyzeQuality = () => {
  ElMessage({
    type: 'success',
    message: '图像质量分析完成',
    duration: 2000
  })
  console.log('Analyze image quality')
}

// 标定结果方法
const viewDetails = () => {
  ElMessage({
    type: 'info',
    message: '查看详细标定结果',
    duration: 2000
  })
  console.log('View calibration details')
}

const verifyCalibration = () => {
  ElMessage({
    type: 'info',
    message: '开始验证标定结果...',
    duration: 2000
  })
  console.log('Verify calibration results')
}

// 配置管理方法
const resetToDefault = () => {
  detectionParams.threshold = '0.5'
  detectionParams.minCorners = '6'
  detectionParams.edgeLength = '20'
  iterationSettings.maxIterations = '100'
  iterationSettings.precision = '0.01'
  algorithmType.value = 'zhang'
  
  ElMessage({
    type: 'success',
    message: '已恢复默认配置',
    duration: 2000
  })
}

const openAdvancedSettings = () => {
  ElMessage({
    type: 'info',
    message: '打开高级设置面板',
    duration: 2000
  })
  console.log('Open advanced settings')
}

// 验证方法
const reverifyCalibration = () => {
  ElMessage({
    type: 'info',
    message: '重新验证标定精度...',
    duration: 2000
  })
  console.log('Reverify calibration')
}

const generateReport = () => {
  ElMessage({
    type: 'success',
    message: '正在生成标定报告...',
    duration: 2000
  })
  console.log('Generate calibration report')
}

// 误差分析方法
const detailedAnalysis = () => {
  ElMessage({
    type: 'info',
    message: '打开详细误差分析',
    duration: 2000
  })
  console.log('Open detailed error analysis')
}

const exportAnalysis = () => {
  ElMessage({
    type: 'success',
    message: '正在导出误差分析结果...',
    duration: 2000
  })
  console.log('Export error analysis')
}

// 生命周期
onMounted(() => {
  console.log('Camera Calibration Page mounted')
})
</script>

<style scoped>
.preview-area {
  background-color: #F0F9F5;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.calibration-board {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 150px;
  border: 2px solid #00A870;
}

/* Element Plus Radio 样式覆盖 */
:deep(.el-radio) {
  margin-right: 8px;
  margin-bottom: 8px;
}

:deep(.el-radio__label) {
  font-weight: 500;
  color: #2c3e50;
}

/* Element Plus Select 样式覆盖 */
:deep(.el-select) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  border-radius: 4px;
}

/* Element Plus Input 样式覆盖 */
:deep(.el-input--small .el-input__wrapper) {
  padding: 1px 8px;
}

/* Progress Bar */
.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #EBEEF5;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #409EFF;
  border-radius: 5px;
  transition: width 0.3s ease;
}

/* 状态颜色 */
.status-excellent {
  color: #67C23A;
}

.status-good {
  color: #67C23A;
}

.status-average {
  color: #E6A23C;
}

.status-poor {
  color: #F56C6C;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  .md\:col-span-2 {
    grid-column: span 1;
  }
}
</style>
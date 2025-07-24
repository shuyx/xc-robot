<template>
  <div class="p-6 h-[calc(100vh-100px)]">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">硬件组件单元测试</h1>
      <div class="flex items-center text-gray-600">
        <span>主菜单</span>
        <i class="fa-solid fa-chevron-right text-xs mx-2"></i>
        <span>场景测试</span>
        <i class="fa-solid fa-chevron-right text-xs mx-2"></i>
        <span class="text-primary">组件测试</span>
      </div>
      <p class="mt-2 text-gray-600">独立测试各硬件组件的功能和性能</p>
    </div>

    <!-- Component Selection Section -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold flex items-center">
          <i class="fa-solid fa-crosshairs text-primary mr-2"></i>
          测试组件选择
        </h2>
        <button @click="addComponent" class="text-primary text-sm hover:text-primary-dark">
          <i class="fa-solid fa-plus mr-1"></i>添加组件
        </button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <!-- Component Cards -->
        <div 
          v-for="component in components" 
          :key="component.id"
          @click="selectComponent(component)"
          :class="[
            'rounded-lg p-4 cursor-pointer transition-all shadow-sm',
            component.selected 
              ? 'bg-secondary border-2 border-primary' 
              : 'bg-white border border-gray-200 hover:border-primary hover:shadow-sm'
          ]"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="flex items-center">
              <i :class="[component.icon, component.selected ? 'text-success' : 'text-gray-400', 'mr-2']"></i>
              <span class="font-medium">{{ component.name }}</span>
            </span>
            <span 
              v-if="component.selected" 
              class="text-xs px-2 py-1 bg-primary text-white rounded-full"
            >
              已选择
            </span>
          </div>
          <div class="text-xs text-gray-600">
            <div class="flex justify-between">
              <span>状态:</span>
              <span :class="getStatusColor(component.status)">{{ component.status }}</span>
            </div>
            <div class="flex justify-between">
              <span>测试:</span>
              <span>{{ component.completedTests }}/{{ component.totalTests }} 完成</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Test Cases Section -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold flex items-center">
          <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>
          测试用例 ({{ selectedComponent?.name || '未选择' }})
        </h2>
        <div>
          <button @click="addTestCase" class="text-primary text-sm hover:text-primary-dark mr-2">
            <i class="fa-solid fa-plus mr-1"></i>添加测试
          </button>
          <button @click="runAllTests" class="bg-primary text-white text-sm px-3 py-1 rounded hover:bg-opacity-90">
            <i class="fa-solid fa-play mr-1"></i>全部执行
          </button>
        </div>
      </div>

      <div v-if="selectedComponent" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <!-- Test Case Items -->
        <div 
          v-for="(testCase, index) in testCases" 
          :key="testCase.id"
          :class="[
            'border-b border-gray-100 p-4 hover:bg-gray-50',
            testCase.status === 'running' ? 'bg-blue-50' : ''
          ]"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <i :class="getTestStatusIcon(testCase.status)"></i>
              <span class="font-medium">{{ testCase.name }}</span>
            </div>
            <div class="flex items-center">
              <div class="flex items-center mr-6">
                <span class="text-gray-500 mr-2">状态:</span>
                <span :class="getStatusColor(testCase.status)">{{ getStatusText(testCase.status) }}</span>
              </div>
              <div v-if="testCase.status === 'running'" class="flex items-center mr-6">
                <span class="text-gray-500 mr-2">进度:</span>
                <div class="w-24 h-2 bg-gray-200 rounded-full mr-1">
                  <div 
                    class="h-full bg-info rounded-full transition-all duration-300" 
                    :style="{ width: testCase.progress + '%' }"
                  ></div>
                </div>
                <span class="font-medium">{{ testCase.progress }}%</span>
              </div>
              <div v-else class="flex items-center mr-6">
                <span class="text-gray-500 mr-2">耗时:</span>
                <span class="font-medium">{{ testCase.duration || '--' }}</span>
              </div>
              <button 
                @click="handleTestAction(testCase)"
                :class="getTestActionButtonClass(testCase.status)"
              >
                <i :class="getTestActionIcon(testCase.status)"></i>
                {{ getTestActionText(testCase.status) }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-500">
        <i class="fa-solid fa-hand-pointer text-4xl mb-4"></i>
        <p>请先选择一个组件开始测试</p>
      </div>
    </div>

    <!-- Monitoring and Results Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <!-- Real-time Monitoring -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold flex items-center">
            <i class="fa-solid fa-chart-line text-primary mr-2"></i>
            实时监控
          </h2>
          <div class="flex">
            <button class="text-gray-500 text-sm hover:text-gray-700 mr-2">
              <i class="fa-solid fa-expand"></i>
            </button>
            <button @click="refreshMonitoring" class="text-gray-500 text-sm hover:text-gray-700">
              <i class="fa-solid fa-sync"></i>
            </button>
          </div>
        </div>

        <div v-if="currentRunningTest" class="mb-4">
          <div class="flex items-center mb-2">
            <i class="fa-solid fa-crosshairs text-primary mr-2"></i>
            <span class="font-medium">{{ currentRunningTest.name }}</span>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="bg-gray-50 rounded p-3">
              <div class="text-sm text-gray-500 mb-1">{{ monitoringData.metric1Label }}</div>
              <div class="font-semibold text-lg">{{ monitoringData.metric1Value }}</div>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <div class="text-sm text-gray-500 mb-1">{{ monitoringData.metric2Label }}</div>
              <div class="font-semibold text-lg">{{ monitoringData.metric2Value }}</div>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <div class="text-sm text-gray-500 mb-1">误差</div>
              <div class="font-semibold text-lg text-warning">{{ monitoringData.errorRate }}</div>
            </div>
            <div class="bg-gray-50 rounded p-3">
              <div class="text-sm text-gray-500 mb-1">预计剩余</div>
              <div class="font-semibold text-lg">{{ monitoringData.remainingTime }}</div>
            </div>
          </div>

          <div class="mb-4">
            <div class="flex justify-between text-sm mb-1">
              <span>进度</span>
              <span>{{ currentRunningTest.progress }}%</span>
            </div>
            <div class="w-full h-2 bg-gray-200 rounded-full">
              <div 
                class="h-full bg-info rounded-full transition-all duration-300" 
                :style="{ width: currentRunningTest.progress + '%' }"
              ></div>
            </div>
          </div>

          <div class="h-[180px] mb-4">
            <canvas ref="monitoringChart" class="w-full h-full"></canvas>
          </div>

          <div class="flex justify-end">
            <button @click="viewDetailedData" class="text-primary text-sm hover:text-primary-dark mr-2">
              <i class="fa-solid fa-chart-bar mr-1"></i>详细数据
            </button>
            <button @click="pauseTest" class="text-gray-700 text-sm hover:text-gray-900 bg-gray-100 px-3 py-1 rounded hover:bg-gray-200">
              <i class="fa-solid fa-pause mr-1"></i>暂停
            </button>
          </div>
        </div>

        <div v-else class="text-center text-gray-500 py-8">
          <i class="fa-solid fa-chart-line text-4xl mb-4"></i>
          <p>暂无运行中的测试</p>
        </div>
      </div>

      <!-- Test Results -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold flex items-center">
            <i class="fa-solid fa-chart-pie text-primary mr-2"></i>
            测试结果
          </h2>
          <div class="flex">
            <button @click="downloadResults" class="text-gray-500 text-sm hover:text-gray-700">
              <i class="fa-solid fa-download"></i>
            </button>
          </div>
        </div>

        <div v-if="selectedComponent" class="grid grid-cols-2 gap-4 mb-6">
          <div class="bg-gray-50 rounded p-3">
            <div class="text-sm text-gray-500 mb-1">测试通过率</div>
            <div class="font-semibold text-lg text-success">{{ testResults.passRate }}%</div>
          </div>
          <div class="bg-gray-50 rounded p-3">
            <div class="text-sm text-gray-500 mb-1">失败用例</div>
            <div class="font-semibold text-lg">{{ testResults.failedCount }}个</div>
          </div>
          <div class="bg-gray-50 rounded p-3">
            <div class="text-sm text-gray-500 mb-1">平均耗时</div>
            <div class="font-semibold text-lg">{{ testResults.avgDuration }}秒</div>
          </div>
          <div class="bg-gray-50 rounded p-3">
            <div class="text-sm text-gray-500 mb-1">性能评分</div>
            <div class="font-semibold text-lg text-primary">{{ testResults.performanceGrade }}</div>
          </div>
        </div>

        <div v-if="testResults.failedTests.length > 0" class="mb-4">
          <div class="flex items-center mb-2">
            <i class="fa-solid fa-times-circle text-danger mr-2"></i>
            <span class="font-medium">失败用例:</span>
          </div>
          <ul class="ml-6 list-disc text-sm text-gray-700">
            <li v-for="failure in testResults.failedTests" :key="failure.name" class="mb-1">
              {{ failure.name }} 
              <span class="text-xs text-gray-500">({{ failure.reason }})</span>
            </li>
          </ul>
        </div>

        <div class="h-[180px] mb-4">
          <canvas ref="resultsChart" class="w-full h-full"></canvas>
        </div>

        <div class="flex justify-end">
          <button @click="viewTestDetails" class="text-primary text-sm hover:text-primary-dark mr-2">
            <i class="fa-solid fa-search mr-1"></i>查看详情
          </button>
          <button @click="retestFailed" class="text-gray-700 text-sm hover:text-gray-900 bg-gray-100 px-3 py-1 rounded hover:bg-gray-200">
            <i class="fa-solid fa-redo mr-1"></i>重测
          </button>
        </div>
      </div>
    </div>

    <!-- Control and Report Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Test Control -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold flex items-center">
            <i class="fa-solid fa-wrench text-primary mr-2"></i>
            测试控制
          </h2>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-4">
          <button @click="startAllTests" class="bg-primary text-white py-2 px-4 rounded-md hover:bg-opacity-90 flex items-center justify-center">
            <i class="fa-solid fa-play mr-2"></i>开始全部
          </button>
          <button @click="stopAllTests" class="bg-danger text-white py-2 px-4 rounded-md hover:bg-opacity-90 flex items-center justify-center">
            <i class="fa-solid fa-stop mr-2"></i>停止全部
          </button>
          <button @click="createCustomTest" class="bg-info text-white py-2 px-4 rounded-md hover:bg-opacity-90 flex items-center justify-center">
            <i class="fa-solid fa-plus mr-2"></i>自定义测试
          </button>
          <button @click="openTestConfig" class="bg-gray-700 text-white py-2 px-4 rounded-md hover:bg-opacity-90 flex items-center justify-center">
            <i class="fa-solid fa-cog mr-2"></i>测试配置
          </button>
        </div>

        <div class="bg-gray-50 p-4 rounded-lg">
          <h3 class="font-medium mb-2">高级设置</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="flex items-center text-sm mb-2">
                <input v-model="testSettings.autoRetry" type="checkbox" class="mr-2">
                自动重试失败项
              </label>
              <label class="flex items-center text-sm mb-2">
                <input v-model="testSettings.notifications" type="checkbox" class="mr-2">
                测试完成通知
              </label>
              <label class="flex items-center text-sm">
                <input v-model="testSettings.realTimeLogging" type="checkbox" class="mr-2">
                实时数据记录
              </label>
            </div>
            <div>
              <label class="flex items-center text-sm mb-2">
                <input v-model="testSettings.parallelTesting" type="checkbox" class="mr-2">
                并行测试
              </label>
              <label class="flex items-center text-sm mb-2">
                <input v-model="testSettings.strictMode" type="checkbox" class="mr-2">
                严格模式
              </label>
              <label class="flex items-center text-sm">
                <input v-model="testSettings.detailedLogs" type="checkbox" class="mr-2">
                详细日志
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Test Report -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold flex items-center">
            <i class="fa-solid fa-file-alt text-primary mr-2"></i>
            测试报告
          </h2>
        </div>

        <div class="mb-4">
          <h3 class="font-medium mb-2">报告生成:</h3>
          <div class="grid grid-cols-1 gap-2">
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.includeDetailedData" type="checkbox" class="mr-2">
              包含详细数据
            </label>
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.performanceCharts" type="checkbox" class="mr-2">
              性能图表
            </label>
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.compareHistory" type="checkbox" class="mr-2">
              对比历史结果
            </label>
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.environmentInfo" type="checkbox" class="mr-2">
              包含测试环境信息
            </label>
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.customComments" type="checkbox" class="mr-2">
              添加自定义注释
            </label>
          </div>
        </div>

        <div class="mb-4">
          <h3 class="font-medium mb-2">报告格式:</h3>
          <div class="flex space-x-4">
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.format" value="pdf" type="radio" class="mr-2">
              PDF
            </label>
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.format" value="html" type="radio" class="mr-2">
              HTML
            </label>
            <label class="flex items-center text-sm">
              <input v-model="reportSettings.format" value="excel" type="radio" class="mr-2">
              Excel
            </label>
          </div>
        </div>

        <div class="flex justify-between mt-6">
          <button @click="openAdvancedReportSettings" class="text-primary text-sm hover:text-primary-dark">
            <i class="fa-solid fa-cog mr-1"></i>高级设置
          </button>
          <button @click="generateReport" class="bg-primary text-white py-2 px-4 rounded-md hover:bg-opacity-90 flex items-center">
            <i class="fa-solid fa-file-export mr-2"></i>生成报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// TypeScript 接口定义
interface Component {
  id: string
  name: string
  icon: string
  status: 'normal' | 'warning' | 'error' | 'unknown'
  selected: boolean
  completedTests: number
  totalTests: number
}

interface TestCase {
  id: string
  name: string
  status: 'passed' | 'failed' | 'running' | 'pending'
  duration?: string
  progress?: number
}

interface MonitoringData {
  metric1Label: string
  metric1Value: string
  metric2Label: string
  metric2Value: string
  errorRate: string
  remainingTime: string
}

interface TestResults {
  passRate: number
  failedCount: number
  avgDuration: number
  performanceGrade: string
  failedTests: Array<{
    name: string
    reason: string
  }>
}

interface TestSettings {
  autoRetry: boolean
  notifications: boolean
  realTimeLogging: boolean
  parallelTesting: boolean
  strictMode: boolean
  detailedLogs: boolean
}

interface ReportSettings {
  includeDetailedData: boolean
  performanceCharts: boolean
  compareHistory: boolean
  environmentInfo: boolean
  customComments: boolean
  format: 'pdf' | 'html' | 'excel'
}

// 响应式数据
const components = ref<Component[]>([
  {
    id: 'fr3-right',
    name: 'FR3右臂',
    icon: 'fa-solid fa-check-circle',
    status: 'normal',
    selected: true,
    completedTests: 2,
    totalTests: 6
  },
  {
    id: 'fr3-left',
    name: 'FR3左臂',
    icon: 'fa-solid fa-robot',
    status: 'normal',
    selected: false,
    completedTests: 0,
    totalTests: 6
  },
  {
    id: 'hermes-chassis',
    name: 'Hermes底盘',
    icon: 'fa-solid fa-truck-moving',
    status: 'warning',
    selected: false,
    completedTests: 1,
    totalTests: 5
  },
  {
    id: 'tof-camera',
    name: 'TOF相机',
    icon: 'fa-solid fa-camera',
    status: 'normal',
    selected: false,
    completedTests: 0,
    totalTests: 4
  },
  {
    id: '2d-camera-1',
    name: '2D相机1',
    icon: 'fa-solid fa-camera',
    status: 'error',
    selected: false,
    completedTests: 0,
    totalTests: 4
  },
  {
    id: 'fisheye-camera',
    name: '鱼眼相机',
    icon: 'fa-solid fa-camera-retro',
    status: 'unknown',
    selected: false,
    completedTests: 0,
    totalTests: 4
  },
  {
    id: 'lidar',
    name: '激光雷达',
    icon: 'fa-solid fa-radiation',
    status: 'normal',
    selected: false,
    completedTests: 0,
    totalTests: 3
  },
  {
    id: 'imu',
    name: 'IMU传感器',
    icon: 'fa-solid fa-microchip',
    status: 'normal',
    selected: false,
    completedTests: 0,
    totalTests: 5
  }
])

const testCases = ref<TestCase[]>([
  {
    id: 'joint-motion',
    name: '关节运动测试',
    status: 'passed',
    duration: '45秒'
  },
  {
    id: 'tcp-precision',
    name: 'TCP精度测试',
    status: 'passed',
    duration: '32秒'
  },
  {
    id: 'force-control',
    name: '力控响应测试',
    status: 'running',
    progress: 60
  },
  {
    id: 'collision-detection',
    name: '碰撞检测测试',
    status: 'pending'
  },
  {
    id: 'temperature-monitoring',
    name: '温度监控测试',
    status: 'pending'
  },
  {
    id: 'communication-delay',
    name: '通信延迟测试',
    status: 'pending'
  }
])

const monitoringData = reactive<MonitoringData>({
  metric1Label: '当前力值',
  metric1Value: '8.5N',
  metric2Label: '目标力值',
  metric2Value: '10.0N',
  errorRate: '15%',
  remainingTime: '18秒'
})

const testResults = reactive<TestResults>({
  passRate: 85,
  failedCount: 2,
  avgDuration: 38,
  performanceGrade: 'B+',
  failedTests: [
    { name: '高速运动精度', reason: '误差超出阈值 8%' },
    { name: '极限负载测试', reason: '超时 120秒' }
  ]
})

const testSettings = reactive<TestSettings>({
  autoRetry: false,
  notifications: true,
  realTimeLogging: true,
  parallelTesting: false,
  strictMode: true,
  detailedLogs: false
})

const reportSettings = reactive<ReportSettings>({
  includeDetailedData: true,
  performanceCharts: true,
  compareHistory: false,
  environmentInfo: true,
  customComments: false,
  format: 'pdf'
})

// Canvas 引用
const monitoringChart = ref<HTMLCanvasElement>()
const resultsChart = ref<HTMLCanvasElement>()

// 计算属性
const selectedComponent = computed(() => {
  return components.value.find(c => c.selected)
})

const currentRunningTest = computed(() => {
  return testCases.value.find(t => t.status === 'running')
})

// 方法定义
const getStatusColor = (status: string): string => {
  const colors = {
    'normal': 'text-success font-medium',
    'warning': 'text-warning font-medium',
    'error': 'text-danger font-medium',
    'unknown': 'text-gray-400 font-medium',
    'passed': 'text-success font-medium',
    'failed': 'text-danger font-medium',
    'running': 'text-info font-medium',
    'pending': 'text-gray-500 font-medium'
  }
  return colors[status] || 'text-gray-500'
}

const getTestStatusIcon = (status: string): string => {
  const icons = {
    'passed': 'fa-solid fa-check-circle text-success mr-2',
    'failed': 'fa-solid fa-times-circle text-danger mr-2',
    'running': 'fa-solid fa-spinner fa-spin text-info mr-2',
    'pending': 'fa-regular fa-clock text-gray-400 mr-2'
  }
  return icons[status] || 'fa-regular fa-clock text-gray-400 mr-2'
}

const getStatusText = (status: string): string => {
  const texts = {
    'passed': '通过',
    'failed': '失败',
    'running': '进行中',
    'pending': '待测试'
  }
  return texts[status] || '未知'
}

const getTestActionButtonClass = (status: string): string => {
  const classes = {
    'passed': 'text-primary text-sm hover:text-primary-dark',
    'failed': 'text-primary text-sm hover:text-primary-dark',
    'running': 'text-danger text-sm hover:text-red-700',
    'pending': 'text-primary text-sm hover:text-primary-dark'
  }
  return classes[status] || 'text-primary text-sm hover:text-primary-dark'
}

const getTestActionIcon = (status: string): string => {
  const icons = {
    'passed': 'fa-solid fa-redo mr-1',
    'failed': 'fa-solid fa-redo mr-1',
    'running': 'fa-solid fa-stop mr-1',
    'pending': 'fa-solid fa-play mr-1'
  }
  return icons[status] || 'fa-solid fa-play mr-1'
}

const getTestActionText = (status: string): string => {
  const texts = {
    'passed': '重测',
    'failed': '重测',
    'running': '停止',
    'pending': '开始'
  }
  return texts[status] || '开始'
}

const selectComponent = (component: Component) => {
  // 取消所有选择
  components.value.forEach(c => c.selected = false)
  // 选择当前组件
  component.selected = true
  
  ElMessage.success(`已选择 ${component.name}`)
  
  // 根据组件类型加载相应的测试用例
  loadTestCasesForComponent(component)
}

const loadTestCasesForComponent = (component: Component) => {
  // 根据不同组件加载不同的测试用例
  if (component.id === 'fr3-right') {
    testCases.value = [
      { id: 'joint-motion', name: '关节运动测试', status: 'passed', duration: '45秒' },
      { id: 'tcp-precision', name: 'TCP精度测试', status: 'passed', duration: '32秒' },
      { id: 'force-control', name: '力控响应测试', status: 'running', progress: 60 },
      { id: 'collision-detection', name: '碰撞检测测试', status: 'pending' },
      { id: 'temperature-monitoring', name: '温度监控测试', status: 'pending' },
      { id: 'communication-delay', name: '通信延迟测试', status: 'pending' }
    ]
  }
  // 可以为其他组件添加不同的测试用例
}

const handleTestAction = (testCase: TestCase) => {
  if (testCase.status === 'running') {
    stopTest(testCase)
  } else if (testCase.status === 'pending') {
    startTest(testCase)
  } else {
    retestCase(testCase)
  }
}

const startTest = (testCase: TestCase) => {
  testCase.status = 'running'
  testCase.progress = 0
  ElMessage.info(`开始执行 ${testCase.name}`)
  
  // 模拟测试进度
  simulateTestProgress(testCase)
}

const stopTest = (testCase: TestCase) => {
  testCase.status = 'pending'
  testCase.progress = undefined
  ElMessage.warning(`已停止 ${testCase.name}`)
}

const retestCase = (testCase: TestCase) => {
  testCase.status = 'running'
  testCase.progress = 0
  testCase.duration = undefined
  ElMessage.info(`重新测试 ${testCase.name}`)
  
  simulateTestProgress(testCase)
}

const simulateTestProgress = (testCase: TestCase) => {
  const interval = setInterval(() => {
    if (testCase.progress !== undefined && testCase.progress < 100) {
      testCase.progress += Math.random() * 10
      if (testCase.progress >= 100) {
        testCase.progress = 100
        testCase.status = Math.random() > 0.3 ? 'passed' : 'failed'
        testCase.duration = `${Math.floor(Math.random() * 60 + 20)}秒`
        clearInterval(interval)
        ElMessage.success(`${testCase.name} 测试完成`)
      }
    }
  }, 500)
}

const addComponent = () => {
  ElMessage.info('添加组件功能')
}

const addTestCase = () => {
  ElMessage.info('添加测试用例功能')
}

const runAllTests = () => {
  if (!selectedComponent.value) {
    ElMessage.warning('请先选择一个组件')
    return
  }
  
  ElMessage.success('开始执行全部测试')
  testCases.value.forEach(testCase => {
    if (testCase.status === 'pending') {
      setTimeout(() => startTest(testCase), Math.random() * 2000)
    }
  })
}

const startAllTests = () => {
  runAllTests()
}

const stopAllTests = () => {
  testCases.value.forEach(testCase => {
    if (testCase.status === 'running') {
      stopTest(testCase)
    }
  })
  ElMessage.warning('已停止全部测试')
}

const refreshMonitoring = () => {
  ElMessage.info('刷新监控数据')
}

const viewDetailedData = () => {
  ElMessage.info('查看详细数据')
}

const pauseTest = () => {
  ElMessage.info('暂停测试')
}

const downloadResults = () => {
  ElMessage.success('下载测试结果')
}

const viewTestDetails = () => {
  ElMessage.info('查看测试详情')
}

const retestFailed = () => {
  const failedTests = testCases.value.filter(t => t.status === 'failed')
  if (failedTests.length === 0) {
    ElMessage.info('没有失败的测试用例')
    return
  }
  
  failedTests.forEach(testCase => retestCase(testCase))
  ElMessage.success(`开始重测 ${failedTests.length} 个失败用例`)
}

const createCustomTest = () => {
  ElMessage.info('创建自定义测试')
}

const openTestConfig = () => {
  ElMessage.info('打开测试配置')
}

const openAdvancedReportSettings = () => {
  ElMessage.info('高级报告设置')
}

const generateReport = () => {
  if (!selectedComponent.value) {
    ElMessage.warning('请先选择一个组件')
    return
  }
  
  ElMessage.success(`正在生成${reportSettings.format.toUpperCase()}格式的测试报告`)
}

// 图表初始化和清理
let progressInterval: number

onMounted(() => {
  // 模拟实时数据更新
  progressInterval = setInterval(() => {
    const runningTest = currentRunningTest.value
    if (runningTest && runningTest.progress !== undefined) {
      // 更新监控数据
      monitoringData.metric1Value = `${(8.5 + Math.random() * 0.5).toFixed(1)}N`
      monitoringData.errorRate = `${Math.floor(Math.random() * 5 + 15)}%`
      monitoringData.remainingTime = `${Math.floor(Math.random() * 10 + 15)}秒`
    }
  }, 1000)
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})
</script>

<style scoped>
.primary-dark {
  color: #3574d9;
}

.transition-all {
  transition: all 0.2s ease-in-out;
}

.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.hover\:shadow-sm:hover {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.bg-primary {
  background-color: #409EFF;
}

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
  color: #409EFF;
}

.bg-secondary {
  background-color: #F3F0FF;
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
  background-color: #409EFF;
}

.border-primary {
  border-color: #409EFF;
}

.border-success {
  border-color: #00A870;
}

.border-warning {
  border-color: #E6A23C;
}

.border-danger {
  border-color: #F56C6C;
}
</style>
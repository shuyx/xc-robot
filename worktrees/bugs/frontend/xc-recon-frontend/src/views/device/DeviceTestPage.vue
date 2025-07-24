<template>
  <div class="w-full h-[calc(100vh-100px)] overflow-auto bg-gray-100 p-4">
    <!-- Page Header -->
    <div class="mb-4">
      <h1 class="text-2xl font-bold text-secondary">设备连接测试</h1>
      <p class="text-gray-600">硬件设备连接状态检测与功能验证</p>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-2 gap-4">
      <!-- Quick Test Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-bullseye text-warning mr-2"></i>
            <h2 class="text-lg font-semibold">快速测试</h2>
          </div>
          <div>
            <el-tooltip content="刷新设备列表">
              <button 
                class="text-gray-500 hover:text-primary p-1"
                @click="refreshDeviceList"
              >
                <i class="fa-solid fa-sync-alt"></i>
              </button>
            </el-tooltip>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-robot text-primary mr-2"></i>
              <h3 class="font-medium">机械臂系统</h3>
            </div>
            <div class="ml-6 space-y-2">
              <div 
                v-for="arm in armDevices" 
                :key="arm.id"
                class="flex items-center"
              >
                <span 
                  class="inline-block w-3 h-3 rounded-full mr-2"
                  :class="{
                    'bg-success': arm.status === 'connected',
                    'bg-warning': arm.status === 'warning',
                    'bg-danger': arm.status === 'disconnected'
                  }"
                ></span>
                <span>{{ arm.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-truck text-primary mr-2"></i>
              <h3 class="font-medium">底盘系统</h3>
            </div>
            <div class="ml-6 space-y-2">
              <div 
                v-for="chassis in chassisDevices" 
                :key="chassis.id"
                class="flex items-center"
              >
                <span 
                  class="inline-block w-3 h-3 rounded-full mr-2"
                  :class="{
                    'bg-success': chassis.status === 'connected',
                    'bg-warning': chassis.status === 'warning',
                    'bg-danger': chassis.status === 'disconnected'
                  }"
                ></span>
                <span>{{ chassis.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-eye text-primary mr-2"></i>
              <h3 class="font-medium">视觉系统</h3>
            </div>
            <div class="ml-6 space-y-2">
              <div 
                v-for="vision in visionDevices" 
                :key="vision.id"
                class="flex items-center"
              >
                <span 
                  class="inline-block w-3 h-3 rounded-full mr-2"
                  :class="{
                    'bg-success': vision.status === 'connected',
                    'bg-warning': vision.status === 'warning',
                    'bg-danger': vision.status === 'disconnected'
                  }"
                ></span>
                <span>{{ vision.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2 mt-4">
            <button 
              class="bg-warning text-white px-4 py-2 rounded-md hover:bg-opacity-90"
              @click="runAllTests"
              :disabled="isTestRunning"
            >
              <i class="fa-solid fa-play mr-1"></i> 
              {{ isTestRunning ? '测试中...' : '全部测试' }}
            </button>
            <button 
              class="border border-warning text-warning px-4 py-2 rounded-md hover:bg-warning-light"
              @click="selectiveTest"
            >
              <i class="fa-solid fa-list-check mr-1"></i> 选择测试
            </button>
          </div>
        </div>
      </div>
      
      <!-- Test Results Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-bar text-primary mr-2"></i>
            <h2 class="text-lg font-semibold">测试结果</h2>
          </div>
          <div>
            <el-tooltip content="导出结果">
              <button 
                class="text-gray-500 hover:text-primary p-1"
                @click="exportResults"
              >
                <i class="fa-solid fa-download"></i>
              </button>
            </el-tooltip>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4 h-[calc(100%-3rem)]">
          <div 
            v-for="result in testResults" 
            :key="result.id"
            class="mb-4 pb-3 border-b border-gray-200"
          >
            <div class="flex items-start mb-1">
              <span 
                class="inline-block w-5 h-5 rounded-full flex items-center justify-center text-white text-xs mr-2"
                :class="{
                  'bg-success': result.status === 'success',
                  'bg-warning': result.status === 'warning',
                  'bg-danger': result.status === 'error'
                }"
              >
                <span v-if="result.status === 'success'">✓</span>
                <span v-else-if="result.status === 'warning'">⚠</span>
                <span v-else>✗</span>
              </span>
              <div>
                <span class="font-medium">{{ result.device }}: {{ result.message }}</span>
                <div class="text-sm text-gray-600 mt-1 ml-1">
                  <div v-for="detail in result.details" :key="detail.key">
                    {{ detail.key }}: <span class="font-medium">{{ detail.value }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2 mt-6">
            <button 
              class="border border-primary text-primary px-4 py-2 rounded-md hover:bg-blue-50"
              @click="viewDetailedReport"
            >
              <i class="fa-solid fa-file-alt mr-1"></i> 详细报告
            </button>
            <button 
              class="bg-primary text-white px-4 py-2 rounded-md hover:bg-opacity-90"
              @click="retestAll"
            >
              <i class="fa-solid fa-redo mr-1"></i> 重新测试
            </button>
          </div>
        </div>
      </div>
      
      <!-- Detailed Test Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-wrench text-primary mr-2"></i>
            <h2 class="text-lg font-semibold">详细测试</h2>
          </div>
          <div>
            <el-tooltip content="测试设置">
              <button 
                class="text-gray-500 hover:text-primary p-1"
                @click="openTestSettings"
              >
                <i class="fa-solid fa-cog"></i>
              </button>
            </el-tooltip>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="font-medium">当前测试: {{ currentTest.name }}</span>
              <span class="text-xs text-gray-500">开始于: {{ currentTest.startTime }}</span>
            </div>
            <div class="mb-2">
              <div class="flex justify-between mb-1">
                <span class="text-sm">进度:</span>
                <span class="text-sm">{{ currentTest.progress }}%</span>
              </div>
              <el-progress 
                :percentage="currentTest.progress" 
                :show-text="false"
                :stroke-width="8"
                :color="progressColor"
              ></el-progress>
            </div>
            <div class="text-sm text-gray-600">
              预计剩余: {{ currentTest.remainingTime }}
            </div>
          </div>
          
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-chart-line text-primary mr-2"></i>
              <span class="font-medium">实时数据:</span>
            </div>
            <div class="ml-6 text-sm grid grid-cols-2 gap-2">
              <div>CPU: <span class="font-medium">{{ systemMetrics.cpu }}%</span></div>
              <div>内存: <span class="font-medium">{{ systemMetrics.memory }}</span></div>
              <div>网络: <span class="font-medium">{{ systemMetrics.network }}</span></div>
              <div>温度: <span class="font-medium">{{ systemMetrics.temperature }}</span></div>
            </div>
          </div>
          
          <div class="mb-4" v-if="errorMessages.length > 0">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-exclamation-triangle text-danger mr-2"></i>
              <span class="font-medium">错误信息:</span>
            </div>
            <div 
              v-for="error in errorMessages" 
              :key="error.id"
              class="ml-6 p-2 bg-red-50 border border-red-100 rounded-md mb-2"
            >
              <div class="text-danger font-medium">{{ error.message }}</div>
              <div class="text-sm mt-1">建议: {{ error.suggestion }}</div>
            </div>
          </div>
          
          <div class="flex space-x-2 mt-4">
            <button 
              class="bg-danger text-white px-4 py-2 rounded-md hover:bg-opacity-90"
              @click="stopTest"
              :disabled="!isTestRunning"
            >
              <i class="fa-solid fa-stop mr-1"></i> 停止测试
            </button>
            <button 
              class="border border-primary text-primary px-4 py-2 rounded-md hover:bg-blue-50"
              @click="viewTestLog"
            >
              <i class="fa-solid fa-file-alt mr-1"></i> 查看日志
            </button>
          </div>
        </div>
      </div>
      
      <!-- Test History Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>
            <h2 class="text-lg font-semibold">测试历史</h2>
          </div>
          <div>
            <el-tooltip content="筛选">
              <button 
                class="text-gray-500 hover:text-primary p-1"
                @click="filterHistory"
              >
                <i class="fa-solid fa-filter"></i>
              </button>
            </el-tooltip>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4 h-[calc(100%-3rem)] overflow-auto">
          <div 
            v-for="history in testHistory" 
            :key="history.id"
            class="mb-3 pb-3 border-b border-gray-200"
          >
            <div class="flex items-center mb-1">
              <i class="fa-regular fa-calendar text-gray-500 mr-2"></i>
              <span class="font-medium">{{ history.date }}</span>
            </div>
            <div class="ml-6 text-sm">
              <div class="flex items-center">
                <span 
                  class="inline-block w-2 h-2 rounded-full mr-2"
                  :class="{
                    'bg-success': history.status === 'passed',
                    'bg-danger': history.status === 'failed',
                    'bg-warning': history.status === 'partial'
                  }"
                ></span>
                <span>状态: {{ getStatusText(history.status) }}</span>
              </div>
              <div>用时: {{ history.duration }}</div>
            </div>
          </div>
          
          <div class="flex space-x-2 mt-4">
            <button 
              class="border border-primary text-primary px-4 py-2 rounded-md hover:bg-blue-50"
              @click="viewAllHistory"
            >
              <i class="fa-solid fa-list mr-1"></i> 查看全部
            </button>
            <button 
              class="border border-primary text-primary px-4 py-2 rounded-md hover:bg-blue-50"
              @click="exportHistory"
            >
              <i class="fa-solid fa-file-export mr-1"></i> 导出
            </button>
          </div>
        </div>
      </div>
      
      <!-- Test Config Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-cogs text-primary mr-2"></i>
            <h2 class="text-lg font-semibold">测试配置</h2>
          </div>
          <div>
            <el-tooltip content="高级设置">
              <button 
                class="text-gray-500 hover:text-primary p-1"
                @click="openAdvancedSettings"
              >
                <i class="fa-solid fa-sliders-h"></i>
              </button>
            </el-tooltip>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="mb-4">
            <div class="font-medium mb-2">测试类型:</div>
            <div class="ml-4 space-y-2">
              <div 
                v-for="testType in testTypes" 
                :key="testType.id"
                class="flex items-center"
              >
                <input 
                  type="checkbox" 
                  :id="testType.id"
                  v-model="testType.enabled"
                  class="form-checkbox h-4 w-4 text-warning rounded"
                />
                <label :for="testType.id" class="ml-2">{{ testType.name }}</label>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <div class="font-medium mb-2">超时设置:</div>
            <div class="grid grid-cols-2 gap-3 ml-4">
              <div>
                <label class="text-sm text-gray-600">连接:</label>
                <div class="flex items-center">
                  <input 
                    type="number" 
                    v-model="timeoutSettings.connection"
                    class="w-16 h-8 border border-gray-300 rounded px-2 text-center"
                    min="1"
                    max="60"
                  />
                  <span class="ml-1">秒</span>
                </div>
              </div>
              <div>
                <label class="text-sm text-gray-600">功能:</label>
                <div class="flex items-center">
                  <input 
                    type="number" 
                    v-model="timeoutSettings.function"
                    class="w-16 h-8 border border-gray-300 rounded px-2 text-center"
                    min="5"
                    max="300"
                  />
                  <span class="ml-1">秒</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2 mt-6">
            <button 
              class="bg-warning text-white px-4 py-2 rounded-md hover:bg-opacity-90"
              @click="saveConfig"
            >
              <i class="fa-solid fa-save mr-1"></i> 保存配置
            </button>
            <button 
              class="border border-gray-300 text-gray-600 px-4 py-2 rounded-md hover:bg-gray-100"
              @click="resetConfig"
            >
              <i class="fa-solid fa-undo mr-1"></i> 重置
            </button>
          </div>
        </div>
      </div>
      
      <!-- Performance Comparison Section -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-bar text-primary mr-2"></i>
            <h2 class="text-lg font-semibold">性能对比</h2>
          </div>
          <div>
            <el-tooltip content="更多图表">
              <button 
                class="text-gray-500 hover:text-primary p-1"
                @click="expandChart"
              >
                <i class="fa-solid fa-expand"></i>
              </button>
            </el-tooltip>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4 h-[calc(100%-3rem)]">
          <div class="mb-3">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-chart-line text-primary mr-2"></i>
              <span class="font-medium">响应时间趋势:</span>
            </div>
            <div ref="performanceChart" class="h-32 w-full flex items-center justify-center bg-white rounded border">
              <div class="text-center text-gray-500">
                <i class="fa-solid fa-chart-line text-3xl mb-2"></i>
                <p class="text-sm">性能趋势图表</p>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-bullseye text-warning mr-2"></i>
              <span class="font-medium">性能基准:</span>
            </div>
            <div class="ml-6 space-y-1 text-sm">
              <div 
                v-for="benchmark in performanceBenchmarks" 
                :key="benchmark.device"
                class="flex justify-between"
              >
                <span>{{ benchmark.device }}:</span>
                <span class="font-medium">&lt;{{ benchmark.threshold }}</span>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2 mt-4">
            <button 
              class="border border-primary text-primary px-4 py-2 rounded-md hover:bg-blue-50"
              @click="generatePerformanceReport"
            >
              <i class="fa-solid fa-file-alt mr-1"></i> 性能报告
            </button>
            <button 
              class="border border-primary text-primary px-4 py-2 rounded-md hover:bg-blue-50"
              @click="comparePerformance"
            >
              <i class="fa-solid fa-exchange-alt mr-1"></i> 对比
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElProgress } from 'element-plus'

// 类型定义
interface Device {
  id: string
  name: string
  status: 'connected' | 'warning' | 'disconnected'
}

interface TestResult {
  id: string
  device: string
  message: string
  status: 'success' | 'warning' | 'error'
  details: Array<{ key: string; value: string }>
}

interface CurrentTest {
  name: string
  startTime: string
  progress: number
  remainingTime: string
}

interface SystemMetrics {
  cpu: number
  memory: string
  network: string
  temperature: string
}

interface ErrorMessage {
  id: string
  message: string
  suggestion: string
}

interface TestHistory {
  id: string
  date: string
  status: 'passed' | 'failed' | 'partial'
  duration: string
}

interface TestType {
  id: string
  name: string
  enabled: boolean
}

interface PerformanceBenchmark {
  device: string
  threshold: string
}

// 响应式数据
const isTestRunning = ref(false)

const armDevices = ref<Device[]>([
  { id: '1', name: '左臂 FR3-L', status: 'connected' },
  { id: '2', name: '右臂 FR3-R', status: 'connected' }
])

const chassisDevices = ref<Device[]>([
  { id: '1', name: 'Hermes底盘', status: 'connected' },
  { id: '2', name: '激光雷达', status: 'warning' }
])

const visionDevices = ref<Device[]>([
  { id: '1', name: '相机1 (正面)', status: 'connected' },
  { id: '2', name: '相机2 (侧面)', status: 'disconnected' },
  { id: '3', name: '深度相机', status: 'connected' }
])

const testResults = ref<TestResult[]>([
  {
    id: '1',
    device: '机械臂',
    message: '连接正常',
    status: 'success',
    details: [
      { key: '响应时间', value: '12ms' },
      { key: '精度测试', value: '0.02mm' }
    ]
  },
  {
    id: '2',
    device: '底盘',
    message: '连接正常',
    status: 'success',
    details: [
      { key: '响应时间', value: '8ms' },
      { key: '定位精度', value: '±2cm' }
    ]
  },
  {
    id: '3',
    device: '视觉',
    message: '部分异常',
    status: 'warning',
    details: [
      { key: '相机1', value: '正常' },
      { key: '相机2', value: '连接失败' }
    ]
  }
])

const currentTest = reactive<CurrentTest>({
  name: '机械臂精度',
  startTime: '14:25:32',
  progress: 85,
  remainingTime: '2分钟'
})

const systemMetrics = reactive<SystemMetrics>({
  cpu: 45,
  memory: '2.1GB',
  network: '156ms RTT',
  temperature: '42°C'
})

const errorMessages = ref<ErrorMessage[]>([
  {
    id: '1',
    message: '相机2连接超时 (5.2秒)',
    suggestion: '检查USB连接'
  }
])

const testHistory = ref<TestHistory[]>([
  { id: '1', date: '2025-07-19 14:30', status: 'passed', duration: '4分38秒' },
  { id: '2', date: '2025-07-19 10:15', status: 'failed', duration: '5分12秒' },
  { id: '3', date: '2025-07-18 16:20', status: 'passed', duration: '3分45秒' }
])

const testTypes = ref<TestType[]>([
  { id: 'connection-test', name: '连接测试', enabled: true },
  { id: 'function-test', name: '功能测试', enabled: true },
  { id: 'performance-test', name: '性能测试', enabled: true },
  { id: 'stress-test', name: '压力测试', enabled: false }
])

const timeoutSettings = reactive({
  connection: 5,
  function: 30
})

const performanceBenchmarks = ref<PerformanceBenchmark[]>([
  { device: '机械臂', threshold: '20ms' },
  { device: '底盘', threshold: '15ms' },
  { device: '视觉', threshold: '100ms' }
])

const performanceChart = ref<HTMLDivElement>()

// 计算属性
const progressColor = computed(() => {
  if (currentTest.progress < 30) return '#F56C6C'
  if (currentTest.progress < 70) return '#FF9500'
  return '#67C23A'
})

// 方法定义
const refreshDeviceList = () => {
  ElMessage.success('设备列表已刷新')
}

const runAllTests = () => {
  if (isTestRunning.value) return
  
  isTestRunning.value = true
  ElMessage.info('开始运行全部测试...')
  
  // 模拟测试进度
  const progressInterval = setInterval(() => {
    if (currentTest.progress < 100) {
      currentTest.progress += 5
      const remaining = Math.ceil((100 - currentTest.progress) / 5 * 0.2)
      currentTest.remainingTime = `${remaining}分钟`
    } else {
      clearInterval(progressInterval)
      isTestRunning.value = false
      currentTest.progress = 0
      currentTest.remainingTime = '--'
      ElMessage.success('所有测试已完成')
    }
  }, 1000)
}

const selectiveTest = () => {
  ElMessage.info('打开选择测试对话框')
}

const exportResults = () => {
  ElMessage.success('测试结果导出中...')
}

const viewDetailedReport = () => {
  ElMessage.info('打开详细测试报告')
}

const retestAll = () => {
  ElMessage.info('重新开始全部测试')
}

const openTestSettings = () => {
  ElMessage.info('打开测试设置对话框')
}

const stopTest = () => {
  isTestRunning.value = false
  currentTest.progress = 0
  ElMessage.warning('测试已停止')
}

const viewTestLog = () => {
  ElMessage.info('打开测试日志查看器')
}

const filterHistory = () => {
  ElMessage.info('打开历史记录筛选器')
}

const viewAllHistory = () => {
  ElMessage.info('查看全部测试历史')
}

const exportHistory = () => {
  ElMessage.success('历史记录导出中...')
}

const openAdvancedSettings = () => {
  ElMessage.info('打开高级测试设置')
}

const saveConfig = () => {
  ElMessage.success('测试配置已保存')
}

const resetConfig = () => {
  timeoutSettings.connection = 5
  timeoutSettings.function = 30
  testTypes.value.forEach(type => {
    if (['connection-test', 'function-test', 'performance-test'].includes(type.id)) {
      type.enabled = true
    } else {
      type.enabled = false
    }
  })
  ElMessage.info('配置已重置为默认值')
}

const expandChart = () => {
  ElMessage.info('展开性能图表')
}

const generatePerformanceReport = () => {
  ElMessage.info('生成性能报告')
}

const comparePerformance = () => {
  ElMessage.info('打开性能对比工具')
}

const getStatusText = (status: string) => {
  const statusMap = {
    'passed': '全部通过',
    'failed': '测试失败',
    'partial': '部分失败'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

// 组件挂载
onMounted(() => {
  // 模拟图表初始化
  setTimeout(() => {
    if (performanceChart.value) {
      performanceChart.value.innerHTML = `
        <div class="text-center text-primary">
          <i class="fa-solid fa-chart-line text-3xl mb-2"></i>
          <p class="text-sm">性能响应时间趋势</p>
          <p class="text-xs text-gray-500">机械臂、底盘、视觉系统</p>
        </div>
      `
    }
  }, 1000)
})
</script>

<style scoped>
.text-primary {
  color: #409EFF;
}

.text-secondary {
  color: #2c3e50;
}

.text-success {
  color: #67C23A;
}

.text-warning {
  color: #FF9500;
}

.text-danger {
  color: #F56C6C;
}

.text-info {
  color: #909399;
}

.text-tertiary {
  color: #00A870;
}

.bg-success {
  background-color: #67C23A;
}

.bg-warning {
  background-color: #FF9500;
}

.bg-danger {
  background-color: #F56C6C;
}

.bg-warning-light {
  background-color: #FFF3E0;
}

.hover\:bg-opacity-90:hover {
  background-color: rgba(255, 149, 0, 0.9);
}

.hover\:bg-warning-light:hover {
  background-color: #FFF3E0;
}

.hover\:text-primary:hover {
  color: #409EFF;
}

/* Element Plus 自定义样式 */
:deep(.el-progress-bar__inner) {
  background-color: #FF9500;
}

:deep(.el-progress-bar__outer) {
  background-color: #f0f0f0;
}

/* 表单复选框样式 */
.form-checkbox {
  color: #FF9500;
}

.form-checkbox:checked {
  background-color: #FF9500;
  border-color: #FF9500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
  
  .text-lg {
    font-size: 1.125rem;
  }
  
  .p-4 {
    padding: 1rem;
  }
  
  .gap-4 {
    gap: 1rem;
  }
}

@media (max-width: 640px) {
  .px-4 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .space-x-2 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.25rem;
  }
  
  .grid-cols-2.gap-3 {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}
</style>
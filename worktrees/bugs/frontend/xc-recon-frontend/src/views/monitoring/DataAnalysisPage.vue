<template>
  <div class="w-full h-full bg-gray-50">
    <div class="p-4 h-[calc(100vh-100px)] overflow-auto">
      <!-- Page Header -->
      <div class="mb-4">
        <h1 class="text-2xl font-bold text-secondary">数据分析中心</h1>
        <p class="text-gray-500">系统数据深度分析与业务洞察</p>
      </div>
      
      <!-- Main Content Grid -->
      <div class="grid grid-cols-12 gap-4">
        <!-- Analysis Projects Section -->
        <div class="col-span-4 card bg-white rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-folder-open mr-2 text-primary"></i>
              分析项目
            </h2>
          </div>
          <div class="overflow-y-auto h-[calc(100%-3rem)]">
            <div class="mb-4">
              <div class="flex items-center mb-2">
                <i class="fa-solid fa-folder text-primary mr-2"></i>
                <span class="font-medium">我的分析</span>
              </div>
              <ul class="ml-6 space-y-2">
                <li 
                  v-for="project in myAnalytics" 
                  :key="project.id"
                  class="flex items-center cursor-pointer hover:bg-light p-1 rounded"
                  :class="{ 'text-primary': project.active }"
                  @click="selectProject(project)"
                >
                  <i :class="['mr-2', project.icon, project.active ? 'text-primary' : 'text-gray-600']"></i>
                  <span>{{ project.name }}</span>
                </li>
              </ul>
            </div>
            <div class="mb-4">
              <div class="flex items-center mb-2">
                <i class="fa-solid fa-folder text-primary mr-2"></i>
                <span class="font-medium">模板库</span>
              </div>
              <ul class="ml-6 space-y-2">
                <li 
                  v-for="template in templates" 
                  :key="template.id"
                  class="flex items-center cursor-pointer hover:bg-light p-1 rounded"
                  @click="selectTemplate(template)"
                >
                  <i class="fa-solid fa-clipboard mr-2 text-gray-600"></i>
                  <span>{{ template.name }}</span>
                </li>
              </ul>
            </div>
            <div class="flex space-x-2 mt-4">
              <button 
                class="el-button el-button--primary px-3 py-1 text-white rounded-md text-sm flex items-center"
                @click="createNewAnalysis"
              >
                <i class="fa-solid fa-plus mr-1"></i> 新建分析
              </button>
              <button 
                class="el-button el-button--default px-3 py-1 bg-white border border-gray-300 rounded-md text-sm flex items-center"
                @click="importAnalysis"
              >
                <i class="fa-solid fa-file-import mr-1"></i> 导入
              </button>
            </div>
          </div>
        </div>
        
        <!-- Time Range Selection -->
        <div class="col-span-4 card bg-white rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-calendar-days mr-2 text-primary"></i>
              时间范围选择
            </h2>
          </div>
          <div class="mb-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">开始日期</label>
                <div class="relative">
                  <input 
                    type="date" 
                    v-model="timeRange.startDate"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">结束日期</label>
                <div class="relative">
                  <input 
                    type="date" 
                    v-model="timeRange.endDate"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>
            </div>
          </div>
          <div>
            <h3 class="font-medium text-sm mb-2 flex items-center">
              <i class="fa-solid fa-database mr-2 text-primary"></i>
              数据源:
            </h3>
            <div class="space-y-2">
              <div 
                v-for="source in dataSources" 
                :key="source.id"
                class="flex items-center"
              >
                <input 
                  type="checkbox" 
                  :id="source.id"
                  v-model="source.selected"
                  class="mr-2 h-4 w-4 text-primary focus:ring-primary"
                />
                <label :for="source.id" class="text-sm">{{ source.name }}</label>
              </div>
            </div>
            <div class="flex space-x-2 mt-4">
              <button 
                class="el-button el-button--primary px-3 py-1 text-white rounded-md text-sm"
                @click="applySelection"
              >
                应用选择
              </button>
              <button 
                class="el-button el-button--default px-3 py-1 bg-white border border-gray-300 rounded-md text-sm"
                @click="selectAll"
              >
                全选
              </button>
            </div>
          </div>
        </div>
        
        <!-- Analysis Tools -->
        <div class="col-span-4 card bg-white rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-magnifying-glass-chart mr-2 text-primary"></i>
              分析工具栏
            </h2>
          </div>
          <div class="mb-4">
            <h3 class="font-medium text-sm mb-2">图表类型:</h3>
            <div class="grid grid-cols-2 gap-2">
              <div 
                v-for="chart in chartTypes" 
                :key="chart.id"
                class="flex items-center"
              >
                <input 
                  type="radio" 
                  :id="chart.id"
                  name="chart-type"
                  v-model="selectedChartType"
                  :value="chart.id"
                  class="mr-2 h-4 w-4 text-primary focus:ring-primary"
                />
                <label :for="chart.id" class="text-sm">{{ chart.name }}</label>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium text-sm mb-2">分析方法:</h3>
            <div class="space-y-2">
              <div 
                v-for="method in analysisMethods" 
                :key="method.id"
                class="flex items-center"
              >
                <input 
                  type="checkbox" 
                  :id="method.id"
                  v-model="method.selected"
                  class="mr-2 h-4 w-4 text-primary focus:ring-primary"
                />
                <label :for="method.id" class="text-sm">{{ method.name }}</label>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium text-sm mb-2">预测设置:</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs mb-1">预测周期</label>
                <select 
                  v-model="predictionSettings.period"
                  class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary text-sm"
                >
                  <option value="3">3天</option>
                  <option value="7">7天</option>
                  <option value="14">14天</option>
                  <option value="30">30天</option>
                </select>
              </div>
              <div>
                <label class="block text-xs mb-1">置信区间</label>
                <select 
                  v-model="predictionSettings.confidence"
                  class="w-full px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary text-sm"
                >
                  <option value="90">90%</option>
                  <option value="95">95%</option>
                  <option value="99">99%</option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2">
            <button 
              class="el-button el-button--primary px-4 py-2 text-white rounded-md flex items-center"
              @click="runAnalysis"
            >
              <i class="fa-solid fa-chart-line mr-1"></i> 分析
            </button>
            <button 
              class="el-button el-button--success px-4 py-2 text-white rounded-md flex items-center"
              @click="runPrediction"
            >
              <i class="fa-solid fa-bullseye mr-1"></i> 预测
            </button>
            <button 
              class="el-button el-button--default px-4 py-2 bg-white border border-gray-300 rounded-md flex items-center"
              @click="exportData"
            >
              <i class="fa-solid fa-file-export mr-1"></i> 导出
            </button>
          </div>
        </div>
        
        <!-- Visualization Chart Area -->
        <div class="col-span-8 card bg-white rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-chart-simple mr-2 text-primary"></i>
              可视化图表区
            </h2>
            <div class="flex space-x-2">
              <button 
                class="text-sm text-gray-500 hover:text-primary"
                @click="expandChart"
              >
                <i class="fa-solid fa-expand"></i>
              </button>
              <button 
                class="text-sm text-gray-500 hover:text-primary"
                @click="refreshChart"
              >
                <i class="fa-solid fa-rotate"></i>
              </button>
              <button 
                class="text-sm text-gray-500 hover:text-primary"
                @click="downloadChart"
              >
                <i class="fa-solid fa-download"></i>
              </button>
            </div>
          </div>
          <div ref="performanceChart" class="w-full h-[300px] flex items-center justify-center bg-gray-50 rounded-lg">
            <div class="text-center text-gray-500">
              <i class="fa-solid fa-chart-column text-4xl mb-2"></i>
              <p>性能趋势分析图表</p>
              <p class="text-sm">点击"分析"按钮生成图表</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4 mt-4">
            <div class="bg-gray-50 p-3 rounded-lg">
              <h3 class="text-sm font-medium mb-2 flex items-center">
                <i class="fa-solid fa-triangle-exclamation mr-1 text-warning"></i>
                异常检测图
              </h3>
              <div ref="anomalyChart" class="w-full h-[150px] flex items-center justify-center">
                <div class="text-center text-gray-400">
                  <i class="fa-solid fa-triangle-exclamation text-2xl mb-1"></i>
                  <p class="text-xs">异常检测结果</p>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <h3 class="text-sm font-medium mb-2 flex items-center">
                <i class="fa-solid fa-chart-line mr-1 text-purple"></i>
                预测模型图
              </h3>
              <div ref="predictionChart" class="w-full h-[150px] flex items-center justify-center">
                <div class="text-center text-gray-400">
                  <i class="fa-solid fa-chart-line text-2xl mb-1"></i>
                  <p class="text-xs">预测分析结果</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Report Generation -->
        <div class="col-span-4 card bg-white rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-file-lines mr-2 text-primary"></i>
              报告生成
            </h2>
          </div>
          <div class="mb-4">
            <h3 class="font-medium text-sm mb-2">报告类型:</h3>
            <div class="space-y-2">
              <div 
                v-for="reportType in reportTypes" 
                :key="reportType.id"
                class="flex items-center"
              >
                <input 
                  type="radio" 
                  :id="reportType.id"
                  name="report-type"
                  v-model="selectedReportType"
                  :value="reportType.id"
                  class="mr-2 h-4 w-4 text-primary focus:ring-primary"
                />
                <label :for="reportType.id" class="text-sm">{{ reportType.name }}</label>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium text-sm mb-2">推送时间:</h3>
            <select 
              v-model="reportSettings.schedule"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="daily-08">每日 08:00</option>
              <option value="daily-12">每日 12:00</option>
              <option value="daily-18">每日 18:00</option>
              <option value="weekly">每周一 08:00</option>
              <option value="monthly">每月1日 08:00</option>
            </select>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium text-sm mb-2">接收人:</h3>
            <input 
              type="email" 
              v-model="reportSettings.recipient"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          
          <div class="flex space-x-2">
            <button 
              class="el-button el-button--primary px-4 py-2 text-white rounded-md flex items-center"
              @click="generateReport"
            >
              <i class="fa-solid fa-file-pdf mr-1"></i> 生成报告
            </button>
            <button 
              class="el-button el-button--default px-4 py-2 bg-white border border-gray-300 rounded-md flex items-center"
              @click="setupSchedule"
            >
              <i class="fa-solid fa-clock mr-1"></i> 定时设置
            </button>
          </div>
        </div>
        
        <!-- Analysis Results -->
        <div class="col-span-12 card bg-white rounded-lg p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold flex items-center">
              <i class="fa-solid fa-clipboard-list mr-2 text-primary"></i>
              分析结果
            </h2>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <h3 class="font-medium text-sm mb-2 flex items-center">
                <i class="fa-solid fa-magnifying-glass mr-2 text-primary"></i>
                关键发现:
              </h3>
              <ul class="space-y-2 text-sm">
                <li 
                  v-for="finding in analysisResults.keyFindings" 
                  :key="finding.id"
                  class="flex items-start"
                >
                  <i class="fa-solid fa-circle-check mr-2 mt-1 text-success"></i>
                  <span>{{ finding.text }}</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 class="font-medium text-sm mb-2 flex items-center">
                <i class="fa-solid fa-triangle-exclamation mr-2 text-warning"></i>
                异常警告:
              </h3>
              <ul class="space-y-2 text-sm">
                <li 
                  v-for="warning in analysisResults.warnings" 
                  :key="warning.id"
                  class="flex items-start"
                >
                  <i class="fa-solid fa-circle-exclamation mr-2 mt-1 text-warning"></i>
                  <span>{{ warning.text }}</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 class="font-medium text-sm mb-2 flex items-center">
                <i class="fa-solid fa-bullseye mr-2 text-purple"></i>
                预测结果:
              </h3>
              <ul class="space-y-2 text-sm">
                <li 
                  v-for="prediction in analysisResults.predictions" 
                  :key="prediction.id"
                  class="flex items-start"
                >
                  <i class="fa-solid fa-chart-line mr-2 mt-1 text-purple"></i>
                  <span>{{ prediction.text }}</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="flex space-x-2 mt-4">
            <button 
              class="el-button el-button--primary px-4 py-2 text-white rounded-md flex items-center"
              @click="viewDetailedReport"
            >
              <i class="fa-solid fa-file-lines mr-1"></i> 详细报告
            </button>
            <button 
              class="el-button el-button--default px-4 py-2 bg-white border border-gray-300 rounded-md flex items-center"
              @click="exportPDF"
            >
              <i class="fa-solid fa-file-export mr-1"></i> 导出PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 分析项目数据
interface AnalysisProject {
  id: string
  name: string
  icon: string
  active: boolean
}

interface Template {
  id: string
  name: string
}

interface DataSource {
  id: string
  name: string
  selected: boolean
}

interface ChartType {
  id: string
  name: string
}

interface AnalysisMethod {
  id: string
  name: string
  selected: boolean
}

interface ReportType {
  id: string
  name: string
}

interface AnalysisResult {
  keyFindings: Array<{ id: string; text: string }>
  warnings: Array<{ id: string; text: string }>
  predictions: Array<{ id: string; text: string }>
}

// 响应式数据
const myAnalytics = ref<AnalysisProject[]>([
  { id: '1', name: '性能趋势分析', icon: 'fa-solid fa-chart-line', active: true },
  { id: '2', name: '故障模式分析', icon: 'fa-solid fa-wrench', active: false },
  { id: '3', name: '操作效率分析', icon: 'fa-solid fa-chart-bar', active: false },
  { id: '4', name: '预测模型', icon: 'fa-solid fa-bullseye', active: false }
])

const templates = ref<Template[]>([
  { id: '1', name: '日报模板' },
  { id: '2', name: '周报模板' },
  { id: '3', name: '月报模板' }
])

const timeRange = reactive({
  startDate: '2025-07-01',
  endDate: '2025-07-19'
})

const dataSources = ref<DataSource[]>([
  { id: 'arm-sensor', name: '机械臂传感器', selected: true },
  { id: 'chassis-data', name: '底盘导航数据', selected: true },
  { id: 'vision-data', name: '视觉系统数据', selected: true },
  { id: 'task-logs', name: '任务执行日志', selected: true },
  { id: 'env-sensor', name: '环境传感器', selected: false }
])

const chartTypes = ref<ChartType[]>([
  { id: 'line-chart', name: '折线图' },
  { id: 'bar-chart', name: '柱状图' },
  { id: 'pie-chart', name: '饼图' },
  { id: 'scatter-chart', name: '散点图' },
  { id: 'heatmap-chart', name: '热力图' },
  { id: 'radar-chart', name: '雷达图' }
])

const selectedChartType = ref('bar-chart')

const analysisMethods = ref<AnalysisMethod[]>([
  { id: 'trend-analysis', name: '趋势分析', selected: true },
  { id: 'anomaly-detection', name: '异常检测', selected: true },
  { id: 'spectrum-analysis', name: '频谱分析', selected: false },
  { id: 'correlation-analysis', name: '相关性分析', selected: false }
])

const predictionSettings = reactive({
  period: '7',
  confidence: '95'
})

const reportTypes = ref<ReportType[]>([
  { id: 'real-time-report', name: '实时报告' },
  { id: 'scheduled-report', name: '定时报告' },
  { id: 'custom-report', name: '自定义报告' }
])

const selectedReportType = ref('scheduled-report')

const reportSettings = reactive({
  schedule: 'daily-08',
  recipient: 'admin@xc.com'
})

const analysisResults = ref<AnalysisResult>({
  keyFindings: [
    { id: '1', text: '性能提升 15.2%' },
    { id: '2', text: '故障率下降 8.7%' },
    { id: '3', text: '效率峰值在14:00-16:00' }
  ],
  warnings: [
    { id: '1', text: '左臂关节温度异常' },
    { id: '2', text: '电池容量衰减趋势' }
  ],
  predictions: [
    { id: '1', text: '下周预计完成580任务' },
    { id: '2', text: '建议保养时间: 7天后' }
  ]
})

// 图表引用
const performanceChart = ref<HTMLDivElement>()
const anomalyChart = ref<HTMLDivElement>()
const predictionChart = ref<HTMLDivElement>()

// 方法定义
const selectProject = (project: AnalysisProject) => {
  myAnalytics.value.forEach(p => p.active = false)
  project.active = true
  ElMessage.success(`已选择分析项目: ${project.name}`)
}

const selectTemplate = (template: Template) => {
  ElMessage.success(`已选择模板: ${template.name}`)
}

const createNewAnalysis = () => {
  ElMessage.success('创建新分析项目')
}

const importAnalysis = () => {
  ElMessage.success('导入分析项目')
}

const applySelection = () => {
  const selectedSources = dataSources.value.filter(s => s.selected).map(s => s.name)
  ElMessage.success(`已应用数据源: ${selectedSources.join(', ')}`)
}

const selectAll = () => {
  dataSources.value.forEach(source => source.selected = true)
  ElMessage.success('已选择所有数据源')
}

const runAnalysis = () => {
  const selectedMethods = analysisMethods.value.filter(m => m.selected).map(m => m.name)
  ElMessage.success(`开始运行分析: ${selectedMethods.join(', ')}`)
  
  // 模拟图表生成
  setTimeout(() => {
    if (performanceChart.value) {
      performanceChart.value.innerHTML = `
        <div class="text-center text-success">
          <i class="fa-solid fa-chart-column text-4xl mb-2"></i>
          <p>性能趋势分析已完成</p>
          <p class="text-sm">显示过去19天的任务完成趋势</p>
        </div>
      `
    }
    ElMessage.success('分析完成，已生成图表')
  }, 2000)
}

const runPrediction = () => {
  ElMessage.success(`开始预测分析 (${predictionSettings.period}天, ${predictionSettings.confidence}%置信区间)`)
  
  // 模拟预测图表生成
  setTimeout(() => {
    if (predictionChart.value) {
      predictionChart.value.innerHTML = `
        <div class="text-center text-purple">
          <i class="fa-solid fa-chart-line text-2xl mb-1"></i>
          <p class="text-xs">预测分析完成</p>
          <p class="text-xs text-purple">未来${predictionSettings.period}天趋势</p>
        </div>
      `
    }
    ElMessage.success('预测分析完成')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('数据导出中...')
}

const expandChart = () => {
  ElMessage.info('图表全屏显示')
}

const refreshChart = () => {
  ElMessage.info('图表刷新中...')
  setTimeout(() => {
    ElMessage.success('图表刷新完成')
  }, 1000)
}

const downloadChart = () => {
  ElMessage.success('图表下载中...')
}

const generateReport = () => {
  ElMessage.success(`生成${reportTypes.value.find(t => t.id === selectedReportType.value)?.name}`)
}

const setupSchedule = () => {
  ElMessage.success(`定时设置: ${reportSettings.schedule}`)
}

const viewDetailedReport = () => {
  ElMessage.info('打开详细报告页面')
}

const exportPDF = () => {
  ElMessage.success('导出PDF报告')
}

// 组件挂载
onMounted(() => {
  // 模拟异常检测图表
  if (anomalyChart.value) {
    setTimeout(() => {
      anomalyChart.value!.innerHTML = `
        <div class="text-center text-warning">
          <i class="fa-solid fa-triangle-exclamation text-2xl mb-1"></i>
          <p class="text-xs">检测到2个异常</p>
          <p class="text-xs text-warning">需要关注</p>
        </div>
      `
    }, 3000)
  }
})
</script>

<style scoped>
.card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
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
  color: #909399;
}

.text-purple {
  color: #722ED1;
}

.bg-light {
  background-color: #E6F4FF;
}

.el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
}

.el-button--success {
  background-color: #00A870;
  border-color: #00A870;
}

.el-button--default {
  color: #606266;
  background-color: #ffffff;
  border-color: #dcdfe6;
}

.el-button--default:hover {
  color: #409EFF;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.focus\:ring-primary:focus {
  ring-color: #409EFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-cols-12 {
    grid-template-columns: 1fr;
  }
  
  .col-span-4,
  .col-span-8,
  .col-span-12 {
    grid-column: span 1;
  }
  
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .grid-cols-3 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .col-span-4 {
    grid-column: span 6;
  }
  
  .col-span-8 {
    grid-column: span 12;
  }
}
</style>
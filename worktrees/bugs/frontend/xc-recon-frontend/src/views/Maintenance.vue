<template>
  <div class="p-6 bg-light min-h-screen">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">设备维护管理中心</h1>
      <p class="text-gray-500">设备保养、故障诊断与维修记录管理</p>
    </div>
    
    <div class="grid grid-cols-2 gap-6">
      <!-- 维护提醒 -->
      <div class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-bell-exclamation text-warning mr-2"></i>
            <h2 class="font-semibold text-lg">🚨 维护提醒</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-triangle-exclamation text-danger mr-2"></i>
              <h3 class="font-medium">⚠️ 紧急提醒 ({{ alerts.urgent.length }})</h3>
            </div>
            <ul class="ml-6 text-sm text-secondary">
              <li 
                v-for="alert in alerts.urgent" 
                :key="alert.id"
                class="mb-1"
              >
                • {{ alert.message }}
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-calendar-day text-primary mr-2"></i>
              <h3 class="font-medium">📅 今日计划 ({{ alerts.today.length }})</h3>
            </div>
            <ul class="ml-6 text-sm text-secondary">
              <li 
                v-for="alert in alerts.today" 
                :key="alert.id"
                class="mb-1"
              >
                • {{ alert.message }}
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <div class="flex items-center mb-2">
              <i class="fa-solid fa-calendar-week text-info mr-2"></i>
              <h3 class="font-medium">📆 本周计划 ({{ alerts.weekly.length }})</h3>
            </div>
            <ul class="ml-6 text-sm text-secondary">
              <li 
                v-for="alert in alerts.weekly" 
                :key="alert.id"
                class="mb-1"
              >
                • {{ alert.message }}
              </li>
            </ul>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="viewAllAlerts"
            >
              查看全部
            </button>
            <button 
              class="btn-primary"
              @click="createNewPlan"
            >
              新建计划
            </button>
          </div>
        </div>
      </div>
      
      <!-- 设备健康状态 -->
      <div id="device-health-status" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-line text-primary mr-2"></i>
            <h2 class="font-semibold text-lg">📊 设备健康状态</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-medium mb-2">🤖 机械臂系统:</h3>
            <div 
              v-for="arm in healthStatus.robotArms" 
              :key="arm.id"
              class="ml-4 mb-2"
            >
              <div class="flex items-center justify-between">
                <span>{{ arm.name }}:</span>
                <span class="flex items-center">
                  <span 
                    class="status-dot mr-1"
                    :class="getStatusClass(arm.status)"
                  ></span>
                  {{ getStatusText(arm.status) }} {{ arm.health }}%
                </span>
              </div>
              <div class="health-bar">
                <div 
                  class="health-bar-inner"
                  :class="getHealthBarClass(arm.status)"
                  :style="{ width: arm.health + '%' }"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">🚛 底盘系统:</h3>
            <div 
              v-for="chassis in healthStatus.chassisSystems" 
              :key="chassis.id"
              class="ml-4 mb-2"
            >
              <div class="flex items-center justify-between">
                <span>{{ chassis.name }}:</span>
                <span class="flex items-center">
                  <span 
                    class="status-dot mr-1"
                    :class="getStatusClass(chassis.status)"
                  ></span>
                  {{ getStatusText(chassis.status) }} {{ chassis.health }}%
                </span>
              </div>
              <div class="health-bar">
                <div 
                  class="health-bar-inner"
                  :class="getHealthBarClass(chassis.status)"
                  :style="{ width: chassis.health + '%' }"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">👁️ 视觉系统:</h3>
            <div 
              v-for="vision in healthStatus.visionSystems" 
              :key="vision.id"
              class="ml-4 mb-2"
            >
              <div class="flex items-center justify-between">
                <span>{{ vision.name }}:</span>
                <span class="flex items-center">
                  <span 
                    class="status-dot mr-1"
                    :class="getStatusClass(vision.status)"
                  ></span>
                  {{ getStatusText(vision.status) }} {{ vision.health }}%
                </span>
              </div>
              <div class="health-bar">
                <div 
                  class="health-bar-inner"
                  :class="getHealthBarClass(vision.status)"
                  :style="{ width: vision.health + '%' }"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="viewDetailedReport"
            >
              详细报告
            </button>
            <button 
              class="btn-primary"
              @click="refreshHealthStatus"
            >
              刷新
            </button>
          </div>
        </div>
      </div>
      
      <!-- 维护任务管理 -->
      <div id="maintenance-task-management" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-wrench text-info mr-2"></i>
            <h2 class="font-semibold text-lg">🔧 维护任务管理</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-medium mb-2">📝 当前任务:</h3>
            <div 
              v-if="currentTask"
              class="ml-4 p-3 border border-gray-200 rounded-lg"
            >
              <div class="flex items-center mb-2">
                <i class="fa-solid fa-wrench text-info mr-2"></i>
                <span class="font-medium">🔧 {{ currentTask.name }}</span>
              </div>
              <div class="ml-6 text-sm mb-3">
                <div class="flex mb-1">
                  <span class="w-20 text-gray-500">状态:</span>
                  <span 
                    class="font-medium"
                    :class="getTaskStatusClass(currentTask.status)"
                  >
                    {{ currentTask.status }}
                  </span>
                </div>
                <div class="flex mb-1">
                  <span class="w-20 text-gray-500">执行人:</span>
                  <span>{{ currentTask.assignee }}</span>
                </div>
                <div class="flex">
                  <span class="w-20 text-gray-500">预计:</span>
                  <span>{{ currentTask.estimatedTime }}</span>
                </div>
              </div>
              <div class="flex justify-end space-x-2">
                <button 
                  class="btn-secondary text-sm py-1"
                  @click="updateTaskStatus"
                >
                  更新状态
                </button>
                <button 
                  class="btn-primary text-sm py-1"
                  @click="completeTask"
                >
                  完成
                </button>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">📋 待分配任务:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="task in pendingTasks" 
                :key="task.id"
                class="mb-1 flex items-center"
              >
                <span 
                  class="status-dot mr-2"
                  :class="getPriorityStatusClass(task.priority)"
                ></span>
                {{ task.name }} 
                <span 
                  class="ml-2"
                  :class="getPriorityTextClass(task.priority)"
                >
                  ({{ task.priority }})
                </span>
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">📊 任务统计:</h3>
            <div class="ml-4 grid grid-cols-3 gap-4 text-sm">
              <div>
                <div class="text-gray-500">本月完成:</div>
                <div class="font-medium">{{ taskStats.completed }}/{{ taskStats.total }}</div>
              </div>
              <div>
                <div class="text-gray-500">平均用时:</div>
                <div class="font-medium">{{ taskStats.averageTime }}</div>
              </div>
              <div>
                <div class="text-gray-500">按时完成率:</div>
                <div class="font-medium">{{ taskStats.onTimeRate }}%</div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="assignTasks"
            >
              分配任务
            </button>
            <button 
              class="btn-primary"
              @click="createNewTask"
            >
              新建任务
            </button>
          </div>
        </div>
      </div>
      
      <!-- 故障诊断 -->
      <div id="fault-diagnosis" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-stethoscope text-danger mr-2"></i>
            <h2 class="font-semibold text-lg">📋 故障诊断</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-medium mb-2">🔍 智能诊断:</h3>
            <div class="ml-4">
              <div class="mb-3">
                <label class="block text-sm text-gray-500 mb-1">选择设备:</label>
                <select 
                  v-model="diagnosis.selectedDevice"
                  class="w-full p-2 border border-gray-300 rounded"
                >
                  <option 
                    v-for="device in diagnosis.devices" 
                    :key="device.id"
                    :value="device.id"
                  >
                    {{ device.name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="block text-sm text-gray-500 mb-1">症状描述:</label>
                <textarea 
                  v-model="diagnosis.symptoms"
                  class="w-full p-2 border border-gray-300 rounded h-20" 
                  placeholder="关节运动异响..."
                ></textarea>
              </div>
              <div class="flex justify-end space-x-2">
                <button 
                  class="btn-secondary text-sm"
                  @click="viewHistoricalCases"
                >
                  历史案例
                </button>
                <button 
                  class="btn-primary text-sm"
                  @click="startDiagnosis"
                  :disabled="!diagnosis.selectedDevice || !diagnosis.symptoms"
                >
                  开始诊断
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="diagnosis.results.length > 0">
            <h3 class="font-medium mb-2">🎯 诊断结果:</h3>
            <div class="ml-4">
              <div class="mb-3">
                <div class="text-sm text-gray-500 mb-1">可能原因:</div>
                <ul class="text-sm ml-2">
                  <li 
                    v-for="result in diagnosis.results" 
                    :key="result.id"
                    class="mb-1 flex items-center justify-between"
                  >
                    <span>• {{ result.cause }}</span>
                    <span 
                      class="font-medium"
                      :class="getProbabilityClass(result.probability)"
                    >
                      {{ result.probability }}%
                    </span>
                  </li>
                </ul>
              </div>
              <div v-if="diagnosis.recommendations.length > 0">
                <div class="text-sm text-gray-500 mb-1">建议方案:</div>
                <ol class="text-sm ml-2 list-decimal list-inside">
                  <li 
                    v-for="recommendation in diagnosis.recommendations" 
                    :key="recommendation.id"
                    class="mb-1"
                  >
                    {{ recommendation.action }}
                  </li>
                  <li v-if="diagnosis.estimatedTime">
                    预计用时: {{ diagnosis.estimatedTime }}
                  </li>
                </ol>
              </div>
              <div class="flex justify-end space-x-2 mt-3">
                <button 
                  class="btn-secondary text-sm"
                  @click="saveDiagnosis"
                >
                  保存
                </button>
                <button 
                  class="btn-primary text-sm"
                  @click="generateWorkOrder"
                >
                  生成工单
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 维护记录 -->
      <div id="maintenance-records" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-history text-info mr-2"></i>
            <h2 class="font-semibold text-lg">📚 维护记录</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-medium mb-2">🕒 最近记录:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="record in recentRecords" 
                :key="record.id"
                class="mb-1 py-1 border-b border-gray-100"
              >
                <span class="text-gray-500 mr-2">{{ record.date }}</span>
                {{ record.description }}
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">📈 统计数据:</h3>
            <div class="ml-4 grid grid-cols-2 gap-4 text-sm">
              <div>
                <div class="text-gray-500">本月维护次数:</div>
                <div class="font-medium">{{ recordStats.monthlyCount }}次</div>
              </div>
              <div>
                <div class="text-gray-500">平均故障间隔:</div>
                <div class="font-medium">{{ recordStats.averageInterval }}小时</div>
              </div>
              <div>
                <div class="text-gray-500">维护成本:</div>
                <div class="font-medium">¥{{ recordStats.cost.toLocaleString() }}</div>
              </div>
              <div>
                <div class="text-gray-500">设备可用率:</div>
                <div class="font-medium text-success">{{ recordStats.availability }}%</div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="viewDetailedRecords"
            >
              详细记录
            </button>
            <button 
              class="btn-primary"
              @click="exportReport"
            >
              导出报告
            </button>
          </div>
        </div>
      </div>
      
      <!-- 备件管理 -->
      <div id="spare-parts-management" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-box text-warning mr-2"></i>
            <h2 class="font-semibold text-lg">📦 备件管理</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-medium mb-2">📊 库存状态:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="part in spareParts.inventory" 
                :key="part.id"
                class="mb-1 flex items-center justify-between"
              >
                <span>• {{ part.name }}:</span>
                <span class="font-medium">{{ part.quantity }}{{ part.unit }}</span>
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">⚠️ 库存预警:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="warning in spareParts.warnings" 
                :key="warning.id"
                class="mb-1 flex items-center"
                :class="getWarningTextClass(warning.level)"
              >
                <i class="fa-solid fa-triangle-exclamation mr-1"></i>
                • {{ warning.name }}: {{ warning.message }}
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">📋 采购建议:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="suggestion in spareParts.purchaseSuggestions" 
                :key="suggestion.id"
                class="mb-1"
              >
                • {{ suggestion.item }}
              </li>
              <li v-if="spareParts.estimatedCost">
                • 预计费用: ¥{{ spareParts.estimatedCost.toLocaleString() }}
              </li>
            </ul>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="viewInventory"
            >
              库存
            </button>
            <button 
              class="btn-primary"
              @click="generatePurchaseOrder"
            >
              生成采购单
            </button>
          </div>
        </div>
      </div>
      
      <!-- 知识库 -->
      <div id="knowledge-base" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-book text-primary mr-2"></i>
            <h2 class="font-semibold text-lg">📖 知识库</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <div class="relative">
              <input 
                type="text" 
                v-model="knowledgeBase.searchQuery"
                placeholder="故障关键词..." 
                class="w-full p-2 pr-8 border border-gray-300 rounded"
                @keyup.enter="searchKnowledge"
              >
              <i 
                class="fa-solid fa-search absolute right-3 top-3 text-gray-400 cursor-pointer"
                @click="searchKnowledge"
              ></i>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">📂 分类浏览:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="category in knowledgeBase.categories" 
                :key="category.id"
                class="mb-1 flex items-center cursor-pointer hover:text-primary"
                @click="browseCategory(category.id)"
              >
                <i 
                  class="mr-2"
                  :class="category.icon + ' ' + category.color"
                ></i>
                <span>{{ category.name }}</span>
              </li>
            </ul>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">📄 热门文档:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="doc in knowledgeBase.popularDocs" 
                :key="doc.id"
                class="mb-1 cursor-pointer hover:text-primary"
                @click="openDocument(doc.id)"
              >
                • {{ doc.title }}
              </li>
            </ul>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="editKnowledge"
            >
              编辑
            </button>
            <button 
              class="btn-primary"
              @click="uploadDocument"
            >
              上传文档
            </button>
          </div>
        </div>
      </div>
      
      <!-- 维护分析 -->
      <div id="maintenance-analysis" class="bg-white rounded-lg shadow-sm">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
          <div class="flex items-center">
            <i class="fa-solid fa-chart-pie text-primary mr-2"></i>
            <h2 class="font-semibold text-lg">📊 维护分析</h2>
          </div>
        </div>
        <div class="p-4">
          <div class="mb-4">
            <h3 class="font-medium mb-2">📈 故障趋势分析:</h3>
            <div id="fault-trend-chart" class="h-40 ml-4"></div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">🔍 根因分析:</h3>
            <div class="ml-4 text-sm">
              <div class="flex justify-between mb-1">
                <span>主要故障:</span>
                <span class="font-medium">{{ analysis.mainFault.type }}</span>
              </div>
              <div class="flex justify-between">
                <span>占比:</span>
                <span class="font-medium text-danger">{{ analysis.mainFault.percentage }}%</span>
              </div>
            </div>
          </div>
          
          <div class="mb-4">
            <h3 class="font-medium mb-2">💡 优化建议:</h3>
            <ul class="ml-4 text-sm">
              <li 
                v-for="suggestion in analysis.optimizationSuggestions" 
                :key="suggestion.id"
                class="mb-1"
              >
                • {{ suggestion.text }}
              </li>
            </ul>
          </div>
          
          <div class="flex justify-end space-x-3 mt-4">
            <button 
              class="btn-secondary"
              @click="exportAnalysis"
            >
              导出
            </button>
            <button 
              class="btn-primary"
              @click="viewDetailedAnalysis"
            >
              详细报告
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 类型定义
interface Alert {
  id: string
  message: string
}

interface HealthDevice {
  id: string
  name: string
  status: 'normal' | 'warning' | 'error' | 'unknown'
  health: number
}

interface Task {
  id: string
  name: string
  status: string
  assignee: string
  estimatedTime: string
  priority?: 'high' | 'medium' | 'low'
}

interface DiagnosisResult {
  id: string
  cause: string
  probability: number
}

interface DiagnosisRecommendation {
  id: string
  action: string
}

interface Record {
  id: string
  date: string
  description: string
}

interface SparePart {
  id: string
  name: string
  quantity: number
  unit: string
}

interface SparePartWarning {
  id: string
  name: string
  message: string
  level: 'danger' | 'warning'
}

interface KnowledgeCategory {
  id: string
  name: string
  icon: string
  color: string
}

interface Document {
  id: string
  title: string
}

// 维护提醒数据
const alerts = reactive({
  urgent: [
    { id: '1', message: '左臂关节需要润滑' },
    { id: '2', message: '底盘电池需要检查' }
  ] as Alert[],
  today: [
    { id: '3', message: '视觉系统定期标定' }
  ] as Alert[],
  weekly: [
    { id: '4', message: '全系统安全检查' },
    { id: '5', message: '软件版本更新' },
    { id: '6', message: '备件库存盘点' }
  ] as Alert[]
})

// 设备健康状态数据
const healthStatus = reactive({
  robotArms: [
    { id: 'left-arm', name: '左臂', status: 'normal' as const, health: 98 },
    { id: 'right-arm', name: '右臂', status: 'warning' as const, health: 85 }
  ] as HealthDevice[],
  chassisSystems: [
    { id: 'drive', name: '驱动', status: 'normal' as const, health: 96 },
    { id: 'navigation', name: '导航', status: 'normal' as const, health: 92 }
  ] as HealthDevice[],
  visionSystems: [
    { id: 'camera1', name: '相机1', status: 'normal' as const, health: 94 },
    { id: 'camera2', name: '相机2', status: 'error' as const, health: 0 }
  ] as HealthDevice[]
})

// 当前任务数据
const currentTask = reactive({
  id: 'task-1',
  name: '左臂关节润滑',
  status: '进行中',
  assignee: '张工',
  estimatedTime: '30分钟'
})

// 待分配任务数据
const pendingTasks = reactive([
  { id: 'task-2', name: '底盘电池检查', priority: '高' as const },
  { id: 'task-3', name: '视觉系统标定', priority: '中' as const },
  { id: 'task-4', name: '软件更新', priority: '低' as const }
])

// 任务统计数据
const taskStats = reactive({
  completed: 28,
  total: 32,
  averageTime: '1.2小时',
  onTimeRate: 87.5
})

// 故障诊断数据
const diagnosis = reactive({
  selectedDevice: '',
  symptoms: '',
  devices: [
    { id: 'left-arm', name: '机械臂 - 左臂' },
    { id: 'right-arm', name: '机械臂 - 右臂' },
    { id: 'chassis-drive', name: '底盘 - 驱动系统' },
    { id: 'chassis-nav', name: '底盘 - 导航系统' },
    { id: 'vision-camera1', name: '视觉系统 - 相机1' },
    { id: 'vision-camera2', name: '视觉系统 - 相机2' }
  ],
  results: [] as DiagnosisResult[],
  recommendations: [] as DiagnosisRecommendation[],
  estimatedTime: ''
})

// 维护记录数据
const recentRecords = reactive([
  { id: '1', date: '2025-07-19', description: '机械臂保养' },
  { id: '2', date: '2025-07-18', description: '相机清洁' },
  { id: '3', date: '2025-07-17', description: '系统升级' },
  { id: '4', date: '2025-07-16', description: '安全检查' }
])

// 记录统计数据
const recordStats = reactive({
  monthlyCount: 15,
  averageInterval: 72,
  cost: 8650,
  availability: 96.8
})

// 备件管理数据
const spareParts = reactive({
  inventory: [
    { id: '1', name: '关节轴承', quantity: 5, unit: '个' },
    { id: '2', name: '传动带', quantity: 3, unit: '条' },
    { id: '3', name: '传感器', quantity: 8, unit: '个' },
    { id: '4', name: '电机', quantity: 2, unit: '个' }
  ] as SparePart[],
  warnings: [
    { id: '1', name: '润滑油', message: '需采购', level: 'danger' as const },
    { id: '2', name: '密封圈', message: '库存不足', level: 'warning' as const }
  ] as SparePartWarning[],
  purchaseSuggestions: [
    { id: '1', item: '润滑油 2L' },
    { id: '2', item: '密封圈套装 1套' }
  ],
  estimatedCost: 1250
})

// 知识库数据
const knowledgeBase = reactive({
  searchQuery: '',
  categories: [
    { id: '1', name: '🤖 机械臂维护手册', icon: 'fa-solid fa-robot', color: 'text-primary' },
    { id: '2', name: '🚛 底盘保养指南', icon: 'fa-solid fa-truck', color: 'text-warning' },
    { id: '3', name: '👁️ 视觉系统文档', icon: 'fa-solid fa-camera', color: 'text-info' },
    { id: '4', name: '🔧 常见故障案例', icon: 'fa-solid fa-wrench', color: 'text-danger' },
    { id: '5', name: '📋 保养检查清单', icon: 'fa-solid fa-clipboard-check', color: 'text-success' }
  ] as KnowledgeCategory[],
  popularDocs: [
    { id: '1', title: '机械臂标定流程' },
    { id: '2', title: '安全系统检查' },
    { id: '3', title: '故障代码对照表' }
  ] as Document[]
})

// 维护分析数据
const analysis = reactive({
  mainFault: {
    type: '润滑不足',
    percentage: 45.2
  },
  optimizationSuggestions: [
    { id: '1', text: '增加润滑频次' },
    { id: '2', text: '升级润滑系统' },
    { id: '3', text: '培训操作人员' }
  ]
})

// 获取状态样式类
const getStatusClass = (status: string) => {
  switch (status) {
    case 'normal':
      return 'status-normal'
    case 'warning':
      return 'status-warning'
    case 'error':
      return 'status-error'
    default:
      return 'status-unknown'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'normal':
      return '正常'
    case 'warning':
      return '警告'
    case 'error':
      return '故障'
    default:
      return '未知'
  }
}

// 获取健康条颜色类
const getHealthBarClass = (status: string) => {
  switch (status) {
    case 'normal':
      return 'bg-success'
    case 'warning':
      return 'bg-warning'
    case 'error':
      return 'bg-danger'
    default:
      return 'bg-info'
  }
}

// 获取任务状态样式类
const getTaskStatusClass = (status: string) => {
  if (status === '进行中') return 'text-warning'
  if (status === '已完成') return 'text-success'
  if (status === '待开始') return 'text-info'
  return 'text-gray-500'
}

// 获取优先级状态点样式类
const getPriorityStatusClass = (priority: string) => {
  switch (priority) {
    case '高':
      return 'status-error'
    case '中':
      return 'status-warning'
    case '低':
      return 'status-info'
    default:
      return 'status-unknown'
  }
}

// 获取优先级文本样式类
const getPriorityTextClass = (priority: string) => {
  switch (priority) {
    case '高':
      return 'text-danger'
    case '中':
      return 'text-warning'
    case '低':
      return 'text-info'
    default:
      return 'text-gray-500'
  }
}

// 获取概率样式类
const getProbabilityClass = (probability: number) => {
  if (probability >= 80) return 'text-danger'
  if (probability >= 50) return 'text-warning'
  return 'text-info'
}

// 获取警告文本样式类
const getWarningTextClass = (level: string) => {
  return level === 'danger' ? 'text-danger' : 'text-warning'
}

// 方法实现
const viewAllAlerts = () => {
  ElMessage.info('查看全部维护提醒')
}

const createNewPlan = () => {
  ElMessage.info('创建新维护计划')
}

const refreshHealthStatus = () => {
  // 模拟刷新设备健康状态
  healthStatus.robotArms.forEach(arm => {
    arm.health = Math.max(80, Math.min(100, arm.health + (Math.random() - 0.5) * 10))
  })
  healthStatus.chassisSystems.forEach(chassis => {
    chassis.health = Math.max(80, Math.min(100, chassis.health + (Math.random() - 0.5) * 10))
  })
  healthStatus.visionSystems.forEach(vision => {
    if (vision.status !== 'error') {
      vision.health = Math.max(80, Math.min(100, vision.health + (Math.random() - 0.5) * 10))
    }
  })
  ElMessage.success('设备健康状态已刷新')
}

const viewDetailedReport = () => {
  ElMessage.info('查看详细健康报告')
}

const updateTaskStatus = () => {
  ElMessage.info('更新任务状态')
}

const completeTask = async () => {
  try {
    await ElMessageBox.confirm('确定要完成当前任务吗？', '确认完成', {
      type: 'info'
    })
    
    ElMessage.success('任务已完成')
    // 这里应该更新任务状态
  } catch {
    // 用户取消
  }
}

const assignTasks = () => {
  ElMessage.info('分配任务')
}

const createNewTask = () => {
  ElMessage.info('创建新维护任务')
}

const startDiagnosis = async () => {
  if (!diagnosis.selectedDevice || !diagnosis.symptoms) {
    ElMessage.warning('请选择设备并描述症状')
    return
  }
  
  ElMessage.info('正在进行智能诊断...')
  
  // 模拟诊断过程
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  // 模拟诊断结果
  diagnosis.results = [
    { id: '1', cause: '润滑不足', probability: 85 },
    { id: '2', cause: '磨损老化', probability: 12 },
    { id: '3', cause: '零件松动', probability: 3 }
  ]
  
  diagnosis.recommendations = [
    { id: '1', action: '重新润滑关节' },
    { id: '2', action: '检查润滑系统' }
  ]
  
  diagnosis.estimatedTime = '45分钟'
  
  ElMessage.success('诊断完成')
}

const viewHistoricalCases = () => {
  ElMessage.info('查看历史故障案例')
}

const saveDiagnosis = () => {
  ElMessage.success('诊断结果已保存')
}

const generateWorkOrder = () => {
  ElMessage.success('维修工单已生成')
}

const viewDetailedRecords = () => {
  ElMessage.info('查看详细维护记录')
}

const exportReport = () => {
  ElMessage.success('报告导出成功')
}

const viewInventory = () => {
  ElMessage.info('查看详细库存')
}

const generatePurchaseOrder = () => {
  ElMessage.success('采购单已生成')
}

const searchKnowledge = () => {
  if (!knowledgeBase.searchQuery.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  ElMessage.info(`搜索关键词: ${knowledgeBase.searchQuery}`)
}

const browseCategory = (categoryId: string) => {
  const category = knowledgeBase.categories.find(c => c.id === categoryId)
  if (category) {
    ElMessage.info(`浏览分类: ${category.name}`)
  }
}

const openDocument = (docId: string) => {
  const doc = knowledgeBase.popularDocs.find(d => d.id === docId)
  if (doc) {
    ElMessage.info(`打开文档: ${doc.title}`)
  }
}

const editKnowledge = () => {
  ElMessage.info('编辑知识库')
}

const uploadDocument = () => {
  ElMessage.info('上传文档')
}

const exportAnalysis = () => {
  ElMessage.success('分析报告导出成功')
}

const viewDetailedAnalysis = () => {
  ElMessage.info('查看详细分析报告')
}

// 初始化图表
const initCharts = () => {
  // 这里需要等到Highcharts库加载完成
  // 在实际项目中应该安装Highcharts并正确导入
  if (typeof window !== 'undefined' && (window as any).Highcharts) {
    const Highcharts = (window as any).Highcharts
    
    Highcharts.chart('fault-trend-chart', {
      chart: {
        type: 'line',
        backgroundColor: 'transparent',
        style: {
          fontFamily: 'Inter, sans-serif'
        }
      },
      title: {
        text: null
      },
      credits: {
        enabled: false
      },
      xAxis: {
        categories: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
      },
      yAxis: {
        title: {
          text: null
        }
      },
      legend: {
        enabled: true,
        itemStyle: {
          fontSize: '10px'
        }
      },
      tooltip: {
        shared: true
      },
      series: [{
        name: '润滑故障',
        color: '#F56C6C',
        data: [12, 10, 14, 8, 11, 9, 7]
      }, {
        name: '电气故障',
        color: '#E6A23C',
        data: [5, 7, 6, 9, 4, 5, 3]
      }, {
        name: '软件故障',
        color: '#409EFF',
        data: [3, 2, 4, 2, 3, 1, 2]
      }]
    })
  }
}

onMounted(() => {
  console.log('设备维护管理中心页面已加载')
  
  // 延迟初始化图表，确保DOM已渲染
  setTimeout(() => {
    initCharts()
  }, 1000)
})

onUnmounted(() => {
  // 清理工作
})
</script>

<style scoped>
/* 项目配色变量 */
.text-secondary {
  color: #2c3e50;
}

.bg-light {
  background-color: #F8F9FA;
}

.text-primary {
  color: #409EFF;
}

.text-warning {
  color: #E6A23C;
}

.text-danger {
  color: #F56C6C;
}

.text-success {
  color: #67C23A;
}

.text-info {
  color: #909399;
}

.bg-success {
  background-color: #67C23A;
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

/* 状态指示点 */
.status-dot {
  height: 10px;
  width: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 5px;
}

.status-normal { 
  background-color: #67C23A; 
}

.status-warning { 
  background-color: #E6A23C; 
}

.status-error { 
  background-color: #F56C6C; 
}

.status-unknown { 
  background-color: #909399; 
}

.status-info { 
  background-color: #409EFF; 
}

/* 健康条 */
.health-bar {
  height: 6px;
  border-radius: 3px;
  background-color: #EBEEF5;
  overflow: hidden;
  margin-top: 4px;
}

.health-bar-inner {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* 按钮样式 */
.btn-primary {
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #337ECC;
}

.btn-primary:disabled {
  background-color: #909399;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #909399;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-secondary:hover {
  background-color: #737679;
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* 滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

/* 悬停效果 */
.hover\:text-primary:hover {
  color: #409EFF;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .flex.space-x-3 {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .flex.space-x-3 > * {
    margin-left: 0;
  }
}
</style>
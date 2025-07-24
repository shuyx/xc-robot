<template>
  <!-- Log Panel Component -->
  <div 
    class="log-panel-container" 
    :class="[isOpen ? 'w-80' : 'w-0']"
  >
    <!-- Panel Header -->
    <div v-if="isOpen" class="panel-header">
      <div class="header-content">
        <el-icon class="header-icon">
          <Document />
        </el-icon>
        <h2 class="header-title">系统日志</h2>
      </div>
      <div class="header-actions">
        <button @click="togglePanel" class="action-button">
          <el-icon>
            <ArrowRight />
          </el-icon>
        </button>
        <button @click="closePanel" class="action-button">
          <el-icon>
            <Close />
          </el-icon>
        </button>
      </div>
    </div>

    <!-- Toggle Button (when closed) -->
    <div v-else class="toggle-button" @click="openPanel">
      <el-icon>
        <ArrowLeft />
      </el-icon>
    </div>

    <!-- Panel Content -->
    <div v-if="isOpen" class="panel-content">
      <!-- Tabs -->
      <div class="tab-container">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          @click="activeTab = tab.id" 
          class="tab-button"
          :class="{ 'active': activeTab === tab.id }"
        >
          <el-icon class="tab-icon">
            <component :is="tab.icon" />
          </el-icon>
          {{ tab.name }}
        </button>
      </div>

      <!-- Log Content -->
      <div v-if="activeTab === 'realtime'" class="log-content" ref="logContent">
        <div 
          v-for="(log, index) in filteredLogs" 
          :key="index" 
          class="log-item"
          :class="getLogClass(log.level)"
        >
          <div class="log-details">
            <span class="log-time">[{{ log.time }}]</span>
            <span class="log-level" :class="getLogLevelClass(log.level)">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <!-- Error Logs -->
      <div v-if="activeTab === 'errors'" class="log-content">
        <div 
          v-for="(log, index) in errorLogs" 
          :key="index" 
          class="log-item error-log"
        >
          <div class="log-details">
            <span class="log-time">[{{ log.time }}]</span>
            <span class="log-level error">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <!-- Status Tab -->
      <div v-if="activeTab === 'status'" class="status-content">
        <!-- Device Status Section -->
        <div class="status-section">
          <h3 class="section-title">
            <el-icon class="title-icon">
              <Bell />
            </el-icon>
            设备状态监控
          </h3>
          <div class="device-list">
            <div 
              v-for="device in devices" 
              :key="device.id" 
              class="device-item"
            >
              <div class="device-info">
                <el-icon class="device-status" :class="getStatusColorClass(device.status)">
                  <CircleCheck />
                </el-icon>
                <span class="device-name">{{ device.name }}:</span>
              </div>
              <div class="device-details">
                <span :class="getStatusTextClass(device.status)">{{ getStatusText(device.status) }}</span>
                <span class="device-extra">({{ device.details }})</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Current Task Section -->
        <div class="status-section">
          <h3 class="section-title">
            <el-icon class="title-icon">
              <Aim />
            </el-icon>
            当前任务
          </h3>
          <div class="task-info">
            <div class="task-name">{{ currentTask.name }}</div>
            <div class="progress-container">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: currentTask.progress + '%' }"></div>
              </div>
            </div>
            <div class="task-details">
              <span>进度: {{ currentTask.progress }}%</span>
              <span>预计剩余: {{ currentTask.remaining }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="action-bar">
        <div class="search-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索日志..." 
            class="search-input"
          >
          <el-icon class="search-icon">
            <Search />
          </el-icon>
        </div>
        <div class="action-buttons">
          <button @click="exportLogs" class="icon-button" title="导出日志">
            <el-icon>
              <Download />
            </el-icon>
          </button>
          <button @click="clearLogs" class="icon-button" title="清空日志">
            <el-icon>
              <Delete />
            </el-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { 
  Document, ArrowRight, ArrowLeft, Close, Bell, Aim, 
  CircleCheck, Search, Download, Delete, Refresh, 
  WarningFilled, TrendCharts 
} from '@element-plus/icons-vue'

// Props
interface Props {
  isOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false
})

// Emits
const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  'toggle': []
}>()

// Reactive data
const isOpen = ref(props.isOpen)
const activeTab = ref('realtime')
const searchQuery = ref('')
const logContent = ref<HTMLElement>()

// Watch props changes
watch(() => props.isOpen, (newValue) => {
  isOpen.value = newValue
}, { immediate: true })

// Tabs configuration
const tabs = ref([
  { id: 'realtime', name: '实时日志', icon: 'Refresh' },
  { id: 'errors', name: '错误', icon: 'WarningFilled' },
  { id: 'status', name: '状态', icon: 'TrendCharts' }
])

// Mock data
const logs = ref([
  { time: '14:35:12', level: 'INFO', message: '机械臂初始化完成' },
  { time: '14:35:10', level: 'WARN', message: '相机2连接超时' },
  { time: '14:35:08', level: 'INFO', message: '底盘导航就绪' },
  { time: '14:35:05', level: 'ERROR', message: '左臂通信异常' },
  { time: '14:34:58', level: 'INFO', message: '系统启动检查完成' },
  { time: '14:34:45', level: 'INFO', message: '导航地图加载成功' },
  { time: '14:34:30', level: 'WARN', message: '电池电量低于30%' },
  { time: '14:34:22', level: 'INFO', message: '连接到远程服务器成功' },
  { time: '14:34:15', level: 'ERROR', message: '相机标定参数加载失败' },
  { time: '14:34:08', level: 'INFO', message: '初始化机器人底盘' }
])

const devices = ref([
  { id: 1, name: 'FR3右臂', status: 'normal', details: '5ms' },
  { id: 2, name: 'FR3左臂', status: 'error', details: 'timeout' },
  { id: 3, name: '底盘', status: 'normal', details: '8ms' },
  { id: 4, name: '相机2', status: 'warning', details: '连接不稳定' },
  { id: 5, name: '相机1', status: 'normal', details: '12ms' },
  { id: 6, name: '激光雷达', status: 'unknown', details: '检测中' }
])

const currentTask = ref({
  name: '双臂协调抓取',
  progress: 80,
  remaining: '2分钟'
})

// Computed properties
const filteredLogs = computed(() => {
  if (!searchQuery.value) return logs.value
  const query = searchQuery.value.toLowerCase()
  return logs.value.filter(log => 
    log.message.toLowerCase().includes(query) || 
    log.level.toLowerCase().includes(query) ||
    log.time.includes(query)
  )
})

const errorLogs = computed(() => {
  return logs.value.filter(log => log.level === 'ERROR')
})

// Methods
const togglePanel = () => {
  isOpen.value = !isOpen.value
  emit('update:isOpen', isOpen.value)
  emit('toggle')
}

const openPanel = () => {
  isOpen.value = true
  emit('update:isOpen', true)
}

const closePanel = () => {
  isOpen.value = false
  emit('update:isOpen', false)
}

const addLog = (level: string, message: string) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.unshift({ time, level, message })
  
  // Auto scroll to latest log
  if (activeTab.value === 'realtime') {
    nextTick(() => {
      if (logContent.value) {
        logContent.value.scrollTop = 0
      }
    })
  }
}

const exportLogs = () => {
  const logsToExport = activeTab.value === 'errors' ? errorLogs.value : filteredLogs.value
  const content = logsToExport.map(log => `[${log.time}] ${log.level} ${log.message}`).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `system-logs-${new Date().toISOString().slice(0, 10)}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const clearLogs = () => {
  if (confirm('确定要清空日志记录吗？')) {
    logs.value = []
  }
}

const getLogLevelClass = (level: string) => {
  switch (level) {
    case 'ERROR': return 'error'
    case 'WARN': return 'warning'
    case 'INFO': return 'info'
    default: return 'default'
  }
}

const getLogClass = (level: string) => {
  switch (level) {
    case 'ERROR': return 'error-bg'
    case 'WARN': return 'warning-bg'
    default: return ''
  }
}

const getStatusColorClass = (status: string) => {
  switch (status) {
    case 'normal': return 'status-normal'
    case 'warning': return 'status-warning'
    case 'error': return 'status-error'
    case 'info': return 'status-info'
    default: return 'status-unknown'
  }
}

const getStatusTextClass = (status: string) => {
  switch (status) {
    case 'normal': return 'text-success'
    case 'warning': return 'text-warning'
    case 'error': return 'text-error'
    case 'info': return 'text-info'
    default: return 'text-unknown'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'normal': return '正常'
    case 'warning': return '警告'
    case 'error': return '异常'
    case 'info': return '信息'
    default: return '未知'
  }
}

// Simulate new logs
const simulateLogs = () => {
  const messages = [
    { level: 'INFO', message: '任务队列更新' },
    { level: 'INFO', message: '传感器数据已更新' },
    { level: 'WARN', message: '网络延迟增加' },
    { level: 'INFO', message: '位置校准完成' },
    { level: 'ERROR', message: '无法连接到远程服务器' }
  ]
  
  const randomMessage = messages[Math.floor(Math.random() * messages.length)]
  addLog(randomMessage.level, randomMessage.message)
}

// Setup periodic log simulation
onMounted(() => {
  setInterval(simulateLogs, 8000)
})
</script>

<style scoped>
.log-panel-container {
  position: fixed;
  top: 64px;
  right: 0;
  height: calc(100vh - 64px - 48px);
  background: white;
  box-shadow: -2px 0 8px rgba(0,0,0,0.1);
  transition: width 0.3s ease-in-out;
  z-index: 100;
  overflow: hidden;
}

/* Toggle Button */
.toggle-button {
  position: absolute;
  left: -32px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 64px;
  background: var(--secondary-color, #2c3e50);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px 0 0 4px;
  transition: background-color 0.3s ease;
}

.toggle-button:hover {
  background: var(--primary-color, #409EFF);
}

/* Panel Header */
.panel-header {
  height: 56px;
  background: var(--secondary-color, #2c3e50);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  color: var(--primary-color, #409EFF);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 4px;
}

.action-button {
  padding: 8px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Panel Content */
.panel-content {
  height: calc(100% - 56px);
  display: flex;
  flex-direction: column;
}

/* Tabs */
.tab-container {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
}

.tab-button {
  flex: 1;
  padding: 12px 8px;
  background: none;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #606266;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.tab-button.active {
  color: var(--primary-color, #409EFF);
  border-bottom-color: var(--primary-color, #409EFF);
}

.tab-button:hover {
  background: #f5f7fa;
}

.tab-icon {
  font-size: 16px;
}

/* Log Content */
.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.log-item {
  padding: 8px 16px;
  border-bottom: 1px solid #f5f7fa;
  font-size: 12px;
  transition: background-color 0.3s ease;
}

.log-item:hover {
  background: #f5f7fa;
}

.log-item.error-bg {
  background: #fef0f0;
}

.log-item.warning-bg {
  background: #fdf6ec;
}

.log-details {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.log-time {
  color: #909399;
  white-space: nowrap;
  font-family: 'Courier New', monospace;
}

.log-level {
  font-weight: 600;
  min-width: 50px;
}

.log-level.error { color: var(--danger-color, #F56C6C); }
.log-level.warning { color: var(--warning-color, #E6A23C); }
.log-level.info { color: var(--primary-color, #409EFF); }
.log-level.default { color: #606266; }

.log-message {
  flex: 1;
  line-height: 1.4;
}

/* Status Content */
.status-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.status-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--secondary-color, #2c3e50);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: var(--primary-color, #409EFF);
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.device-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 6px;
  background: #f9f9f9;
  transition: background-color 0.3s ease;
}

.device-item:hover {
  background: #f0f0f0;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.device-status {
  font-size: 8px;
}

.device-status.status-normal { color: var(--success-color, #00A870); }
.device-status.status-warning { color: var(--warning-color, #E6A23C); }
.device-status.status-error { color: var(--danger-color, #F56C6C); }
.device-status.status-info { color: var(--primary-color, #409EFF); }
.device-status.status-unknown { color: #DCDFE6; }

.device-name {
  font-size: 12px;
  font-weight: 500;
}

.device-details {
  font-size: 11px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.device-extra {
  color: #909399;
}

.text-success { color: var(--success-color, #00A870); }
.text-warning { color: var(--warning-color, #E6A23C); }
.text-error { color: var(--danger-color, #F56C6C); }
.text-info { color: var(--primary-color, #409EFF); }
.text-unknown { color: #909399; }

/* Task Info */
.task-info {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
}

.task-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.progress-container {
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color, #409EFF);
  transition: width 0.3s ease;
}

.task-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #606266;
}

/* Action Bar */
.action-bar {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  background: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search-container {
  position: relative;
  flex: 1;
  max-width: 180px;
}

.search-input {
  width: 100%;
  padding: 6px 8px 6px 28px;
  font-size: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: var(--primary-color, #409EFF);
}

.search-icon {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: #c0c4cc;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.icon-button {
  padding: 6px;
  background: none;
  border: none;
  color: #606266;
  cursor: pointer;
  border-radius: 4px;
  transition: color 0.3s ease;
}

.icon-button:hover {
  color: var(--primary-color, #409EFF);
}

/* Scrollbar styling */
.log-content::-webkit-scrollbar,
.status-content::-webkit-scrollbar {
  width: 4px;
}

.log-content::-webkit-scrollbar-track,
.status-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.log-content::-webkit-scrollbar-thumb,
.status-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.log-content::-webkit-scrollbar-thumb:hover,
.status-content::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
<template>
  <div id="main-content" class="p-6 w-full h-[calc(100vh-100px)] overflow-auto font-sans bg-gray-100 text-secondary">
    <!-- Page Header -->
    <div id="page-header" class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">系统性能监控</h1>
      <p class="text-gray-500">实时监控系统资源与设备状态</p>
    </div>

    <!-- System Resources Section -->
    <div id="system-resources" class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-computer text-primary mr-2"></i>
        <h2 class="text-xl font-semibold">系统资源</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- CPU Usage Card -->
        <div id="cpu-card" class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div class="flex items-center">
              <i class="fa-solid fa-rotate text-primary mr-2"></i>
              <h3 class="font-medium">CPU使用率</h3>
            </div>
            <button 
              class="text-primary hover:text-blue-600 text-sm"
              @click="refreshCpuData"
            >
              <i class="fa-solid fa-arrows-rotate"></i>
            </button>
          </div>
          <div class="p-4">
            <div class="mb-2 flex items-center">
              <div class="w-full bg-gray-200 rounded-full h-4 mr-3">
                <div 
                  class="bg-success h-4 rounded-full transition-all duration-500" 
                  :style="{ width: systemResources.cpu.usage + '%' }"
                ></div>
              </div>
              <span class="font-semibold text-success">{{ systemResources.cpu.usage }}%</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-sm mb-3">
              <div>
                <span class="text-gray-500">{{ systemResources.cpu.model }}</span>
              </div>
              <div>
                <span class="text-gray-500">温度: <span class="text-warning">{{ systemResources.cpu.temperature }}°C</span></span>
              </div>
            </div>
            <button 
              class="text-primary text-sm hover:underline"
              @click="showCpuDetails"
            >
              详细信息
            </button>
          </div>
        </div>

        <!-- Memory Usage Card -->
        <div id="memory-card" class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div class="flex items-center">
              <i class="fa-solid fa-memory text-primary mr-2"></i>
              <h3 class="font-medium">内存使用率</h3>
            </div>
            <button 
              class="text-primary hover:text-blue-600 text-sm"
              @click="refreshMemoryData"
            >
              <i class="fa-solid fa-arrows-rotate"></i>
            </button>
          </div>
          <div class="p-4">
            <div class="mb-2 flex items-center">
              <div class="w-full bg-gray-200 rounded-full h-4 mr-3">
                <div 
                  class="bg-warning h-4 rounded-full transition-all duration-500" 
                  :style="{ width: systemResources.memory.usage + '%' }"
                ></div>
              </div>
              <span class="font-semibold text-warning">{{ systemResources.memory.usage }}%</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-sm mb-3">
              <div>
                <span class="text-gray-500">{{ systemResources.memory.total }}</span>
              </div>
              <div>
                <span class="text-gray-500">可用: <span class="text-danger">{{ systemResources.memory.available }}</span></span>
              </div>
            </div>
            <button 
              class="text-primary text-sm hover:underline"
              @click="showMemoryDetails"
            >
              详细信息
            </button>
          </div>
        </div>

        <!-- Disk Usage Card -->
        <div id="disk-card" class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div class="flex items-center">
              <i class="fa-solid fa-hard-drive text-primary mr-2"></i>
              <h3 class="font-medium">磁盘使用率</h3>
            </div>
            <button 
              class="text-primary hover:text-blue-600 text-sm"
              @click="refreshDiskData"
            >
              <i class="fa-solid fa-arrows-rotate"></i>
            </button>
          </div>
          <div class="p-4">
            <div class="mb-2 flex items-center">
              <div class="w-full bg-gray-200 rounded-full h-4 mr-3">
                <div 
                  class="bg-warning h-4 rounded-full transition-all duration-500" 
                  :style="{ width: systemResources.disk.usage + '%' }"
                ></div>
              </div>
              <span class="font-semibold text-warning">{{ systemResources.disk.usage }}%</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-sm mb-3">
              <div>
                <span class="text-gray-500">{{ systemResources.disk.total }}</span>
              </div>
              <div>
                <span class="text-gray-500">可用: <span class="text-success">{{ systemResources.disk.available }}</span></span>
              </div>
            </div>
            <button 
              class="text-primary text-sm hover:underline"
              @click="showDiskDetails"
            >
              详细信息
            </button>
          </div>
        </div>

        <!-- Network Traffic Card -->
        <div id="network-card" class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div class="flex items-center">
              <i class="fa-solid fa-globe text-primary mr-2"></i>
              <h3 class="font-medium">网络流量</h3>
            </div>
            <button 
              class="text-primary hover:text-blue-600 text-sm"
              @click="refreshNetworkData"
            >
              <i class="fa-solid fa-arrows-rotate"></i>
            </button>
          </div>
          <div class="p-4">
            <div class="grid grid-cols-2 gap-2 text-sm mb-3">
              <div>
                <i class="fa-solid fa-arrow-up text-success mr-1"></i>
                <span class="text-gray-500">上传: <span class="text-success">{{ systemResources.network.upload }}</span></span>
              </div>
              <div>
                <i class="fa-solid fa-arrow-down text-primary mr-1"></i>
                <span class="text-gray-500">下载: <span class="text-primary">{{ systemResources.network.download }}</span></span>
              </div>
              <div>
                <i class="fa-solid fa-clock text-gray-500 mr-1"></i>
                <span class="text-gray-500">延迟: <span class="text-success">{{ systemResources.network.latency }}</span></span>
              </div>
              <div>
                <i class="fa-solid fa-wifi text-success mr-1"></i>
                <span class="text-gray-500">连接: <span class="text-success">{{ systemResources.network.status }}</span></span>
              </div>
            </div>
            <button 
              class="text-primary text-sm hover:underline"
              @click="showNetworkDetails"
            >
              详细信息
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Device Monitoring Section -->
    <div id="device-monitoring" class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center">
          <i class="fa-solid fa-robot text-primary mr-2"></i>
          <h2 class="text-xl font-semibold">设备监控</h2>
        </div>
        <div class="flex space-x-2">
          <button 
            class="px-3 py-1 bg-primary text-white rounded-md text-sm hover:bg-blue-600 flex items-center"
            @click="addDevice"
          >
            <i class="fa-solid fa-plus mr-1"></i> 添加设备
          </button>
          <button 
            class="px-3 py-1 bg-white border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
            @click="filterDevices"
          >
            <i class="fa-solid fa-filter mr-1"></i> 筛选
          </button>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">设备名称</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPU</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">温度</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">电流</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后心跳</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="device in devices" :key="device.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <i :class="['fa-solid mr-2', device.icon, device.status === 'online' ? 'text-green' : 'text-gray-400']"></i>
                    <span>{{ device.name }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    :class="[
                      'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                      device.status === 'online' 
                        ? 'bg-success bg-opacity-10 text-success' 
                        : 'bg-danger bg-opacity-10 text-danger'
                    ]"
                  >
                    <i 
                      :class="[
                        'fa-solid mr-1',
                        device.status === 'online' ? 'fa-circle text-success' : 'fa-circle text-danger'
                      ]"
                    ></i> 
                    {{ device.status === 'online' ? '正常' : '离线' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ device.status === 'online' ? device.cpu + '%' : '--' }}
                </td>
                <td 
                  class="px-6 py-4 whitespace-nowrap text-sm"
                  :class="device.status === 'online' ? getTemperatureColor(device.temperature) : 'text-gray-500'"
                >
                  {{ device.status === 'online' ? device.temperature + '°C' : '--' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ device.status === 'online' ? device.current : '--' }}
                </td>
                <td 
                  class="px-6 py-4 whitespace-nowrap text-sm"
                  :class="device.status === 'online' ? 'text-gray-500' : 'text-danger'"
                >
                  {{ device.lastHeartbeat }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button 
                    class="text-primary hover:text-blue-700"
                    @click="showDeviceInfo(device)"
                  >
                    <i class="fa-solid fa-circle-info"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Performance Charts Section -->
    <div id="performance-charts" class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-chart-line text-primary mr-2"></i>
        <h2 class="text-xl font-semibold">性能图表</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- CPU Usage Chart -->
        <div id="cpu-chart-card" class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <h3 class="font-medium">CPU使用率 (24小时)</h3>
            <div class="flex space-x-2">
              <button 
                :class="[
                  'text-sm hover:text-primary',
                  chartTimeRange === 'hour' ? 'text-primary border-b border-primary' : 'text-gray-500'
                ]"
                @click="setChartTimeRange('hour')"
              >
                小时
              </button>
              <button 
                :class="[
                  'text-sm hover:text-primary',
                  chartTimeRange === 'day' ? 'text-primary border-b border-primary' : 'text-gray-500'
                ]"
                @click="setChartTimeRange('day')"
              >
                天
              </button>
              <button 
                :class="[
                  'text-sm hover:text-primary',
                  chartTimeRange === 'week' ? 'text-primary border-b border-primary' : 'text-gray-500'
                ]"
                @click="setChartTimeRange('week')"
              >
                周
              </button>
            </div>
          </div>
          <div class="p-4">
            <div ref="cpuChartRef" id="cpu-chart" class="h-64"></div>
          </div>
        </div>

        <!-- Memory Usage Chart -->
        <div id="memory-chart-card" class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <h3 class="font-medium">内存使用率 (24小时)</h3>
            <div class="flex space-x-2">
              <button 
                :class="[
                  'text-sm hover:text-primary',
                  chartTimeRange === 'hour' ? 'text-primary border-b border-primary' : 'text-gray-500'
                ]"
                @click="setChartTimeRange('hour')"
              >
                小时
              </button>
              <button 
                :class="[
                  'text-sm hover:text-primary',
                  chartTimeRange === 'day' ? 'text-primary border-b border-primary' : 'text-gray-500'
                ]"
                @click="setChartTimeRange('day')"
              >
                天
              </button>
              <button 
                :class="[
                  'text-sm hover:text-primary',
                  chartTimeRange === 'week' ? 'text-primary border-b border-primary' : 'text-gray-500'
                ]"
                @click="setChartTimeRange('week')"
              >
                周
              </button>
            </div>
          </div>
          <div class="p-4">
            <div ref="memoryChartRef" id="memory-chart" class="h-64"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts and Summary Section -->
    <div id="alerts-summary" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Alerts Section -->
      <div id="alerts-section">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-bell text-primary mr-2"></i>
          <h2 class="text-xl font-semibold">告警信息</h2>
        </div>
        <div class="bg-white rounded-lg shadow-md p-4">
          <div class="space-y-4">
            <div 
              v-for="alert in alerts" 
              :key="alert.id"
              :class="[
                'border-l-4 pl-3 py-2',
                alert.level === 'warning' ? 'border-warning' : 'border-danger'
              ]"
            >
              <div class="flex items-center">
                <i 
                  :class="[
                    'fa-solid mr-2',
                    alert.level === 'warning' ? 'fa-triangle-exclamation text-warning' : 'fa-circle-exclamation text-danger'
                  ]"
                ></i>
                <span class="font-medium">{{ alert.message }}</span>
              </div>
              <div class="text-sm text-gray-500 mt-1">时间: {{ alert.time }}</div>
              <div class="mt-2 flex space-x-2">
                <button 
                  class="px-3 py-1 bg-primary text-white rounded text-sm hover:bg-blue-600"
                  @click="handleAlert(alert.id)"
                >
                  处理
                </button>
                <button 
                  class="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
                  @click="ignoreAlert(alert.id)"
                >
                  忽略
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Section -->
      <div id="summary-section">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-chart-pie text-primary mr-2"></i>
          <h2 class="text-xl font-semibold">统计摘要</h2>
        </div>
        <div class="bg-white rounded-lg shadow-md p-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="border-b border-gray-100 pb-3">
              <div class="text-sm text-gray-500">运行时间</div>
              <div class="font-semibold mt-1">{{ systemSummary.uptime }}</div>
            </div>
            <div class="border-b border-gray-100 pb-3">
              <div class="text-sm text-gray-500">重启次数</div>
              <div class="font-semibold mt-1">{{ systemSummary.restarts }}次</div>
            </div>
            <div class="border-b border-gray-100 pb-3">
              <div class="text-sm text-gray-500">平均CPU</div>
              <div class="font-semibold mt-1 text-success">{{ systemSummary.avgCpu }}%</div>
            </div>
            <div class="border-b border-gray-100 pb-3">
              <div class="text-sm text-gray-500">平均内存</div>
              <div class="font-semibold mt-1 text-warning">{{ systemSummary.avgMemory }}%</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">告警总数</div>
              <div class="font-semibold mt-1 text-danger">{{ systemSummary.alertCount }}次</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">设备在线率</div>
              <div class="font-semibold mt-1 text-warning">{{ systemSummary.deviceOnlineRate }}%</div>
            </div>
          </div>
          <div class="mt-4 p-3 bg-lightBg rounded-md">
            <div class="text-sm font-medium mb-2">系统健康状态</div>
            <div class="flex items-center">
              <div class="w-full bg-gray-200 rounded-full h-2.5 mr-2">
                <div 
                  class="bg-warning h-2.5 rounded-full transition-all duration-500" 
                  :style="{ width: systemSummary.healthScore + '%' }"
                ></div>
              </div>
              <span class="text-sm font-medium text-warning">{{ systemSummary.healthScore }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

// 导入Highcharts (注意：在实际项目中可能需要安装 highcharts 包)
// import Highcharts from 'highcharts'

// 图表时间范围
const chartTimeRange = ref('day')

// 系统资源数据
const systemResources = reactive({
  cpu: {
    usage: 45,
    model: '8核心 i7-13620Hz',
    temperature: 65
  },
  memory: {
    usage: 85,
    total: '16GB DDR4',
    available: '2.4GB'
  },
  disk: {
    usage: 65,
    total: '500GB SSD',
    available: '175GB'
  },
  network: {
    upload: '2.5MB/s',
    download: '8.1MB/s',
    latency: '5ms',
    status: '稳定'
  }
})

// 设备监控数据
const devices = ref([
  {
    id: 1,
    name: 'FR3右臂',
    icon: 'fa-hand',
    status: 'online',
    cpu: 15,
    temperature: 25,
    current: '2.1A',
    lastHeartbeat: '刚刚'
  },
  {
    id: 2,
    name: 'FR3左臂',
    icon: 'fa-hand',
    status: 'online',
    cpu: 18,
    temperature: 26,
    current: '2.3A',
    lastHeartbeat: '刚刚'
  },
  {
    id: 3,
    name: 'Hermes底盘',
    icon: 'fa-truck-fast',
    status: 'online',
    cpu: 25,
    temperature: 35,
    current: '5.2A',
    lastHeartbeat: '刚刚'
  },
  {
    id: 4,
    name: 'TOF相机',
    icon: 'fa-camera',
    status: 'online',
    cpu: 45,
    temperature: 42,
    current: '1.8A',
    lastHeartbeat: '刚刚'
  },
  {
    id: 5,
    name: '2D相机1',
    icon: 'fa-camera',
    status: 'offline',
    cpu: 0,
    temperature: 0,
    current: '0A',
    lastHeartbeat: '5分钟前'
  },
  {
    id: 6,
    name: '鱼眼相机',
    icon: 'fa-camera',
    status: 'offline',
    cpu: 0,
    temperature: 0,
    current: '0A',
    lastHeartbeat: '10分钟前'
  }
])

// 告警信息
const alerts = ref([
  {
    id: 1,
    level: 'warning',
    message: '内存使用率超过80%',
    time: '14:25'
  },
  {
    id: 2,
    level: 'danger',
    message: '2D相机1连接丢失',
    time: '14:20'
  },
  {
    id: 3,
    level: 'danger',
    message: '鱼眼相机连接丢失',
    time: '14:10'
  }
])

// 系统统计摘要
const systemSummary = reactive({
  uptime: '15天6小时',
  restarts: 2,
  avgCpu: 35,
  avgMemory: 70,
  alertCount: 8,
  deviceOnlineRate: 66,
  healthScore: 75
})

// 图表元素引用
const cpuChartRef = ref<HTMLElement>()
const memoryChartRef = ref<HTMLElement>()

// 实时更新定时器
let updateTimer: NodeJS.Timeout

// 获取温度颜色
const getTemperatureColor = (temperature: number) => {
  if (temperature <= 30) return 'text-success'
  if (temperature <= 40) return 'text-warning'
  return 'text-danger'
}

// 刷新CPU数据
const refreshCpuData = () => {
  systemResources.cpu.usage = Math.floor(Math.random() * 30) + 30 // 30-60%
  systemResources.cpu.temperature = Math.floor(Math.random() * 20) + 55 // 55-75°C
  ElMessage.success('CPU数据已刷新')
}

// 刷新内存数据
const refreshMemoryData = () => {
  systemResources.memory.usage = Math.floor(Math.random() * 15) + 75 // 75-90%
  const availableGb = (16 * (100 - systemResources.memory.usage) / 100).toFixed(1)
  systemResources.memory.available = `${availableGb}GB`
  ElMessage.success('内存数据已刷新')
}

// 刷新磁盘数据
const refreshDiskData = () => {
  systemResources.disk.usage = Math.floor(Math.random() * 20) + 60 // 60-80%
  const availableGb = Math.floor(500 * (100 - systemResources.disk.usage) / 100)
  systemResources.disk.available = `${availableGb}GB`
  ElMessage.success('磁盘数据已刷新')
}

// 刷新网络数据
const refreshNetworkData = () => {
  const upload = (Math.random() * 5 + 1).toFixed(1)
  const download = (Math.random() * 10 + 5).toFixed(1)
  const latency = Math.floor(Math.random() * 10) + 3
  systemResources.network.upload = `${upload}MB/s`
  systemResources.network.download = `${download}MB/s`
  systemResources.network.latency = `${latency}ms`
  ElMessage.success('网络数据已刷新')
}

// 显示详细信息
const showCpuDetails = () => {
  ElMessage.info('CPU详细信息功能正在开发中')
}

const showMemoryDetails = () => {
  ElMessage.info('内存详细信息功能正在开发中')
}

const showDiskDetails = () => {
  ElMessage.info('磁盘详细信息功能正在开发中')
}

const showNetworkDetails = () => {
  ElMessage.info('网络详细信息功能正在开发中')
}

// 设备管理
const addDevice = () => {
  ElMessage.info('添加设备功能正在开发中')
}

const filterDevices = () => {
  ElMessage.info('设备筛选功能正在开发中')
}

const showDeviceInfo = (device: any) => {
  ElMessage.info(`查看${device.name}详细信息功能正在开发中`)
}

// 图表时间范围设置
const setChartTimeRange = (range: string) => {
  chartTimeRange.value = range
  ElMessage.success(`图表时间范围已切换到${range === 'hour' ? '小时' : range === 'day' ? '天' : '周'}`)
  // 这里应该重新初始化图表数据
  initializeCharts()
}

// 告警处理
const handleAlert = (alertId: number) => {
  ElMessage.success(`告警 ${alertId} 已处理`)
  // 移除已处理的告警
  const index = alerts.value.findIndex(alert => alert.id === alertId)
  if (index > -1) {
    alerts.value.splice(index, 1)
  }
}

const ignoreAlert = (alertId: number) => {
  ElMessage.info(`告警 ${alertId} 已忽略`)
  // 移除已忽略的告警
  const index = alerts.value.findIndex(alert => alert.id === alertId)
  if (index > -1) {
    alerts.value.splice(index, 1)
  }
}

// 初始化图表 (模拟Highcharts - 在实际项目中需要安装并正确导入Highcharts)
const initializeCharts = () => {
  // 由于我们使用Vue3 + TypeScript，这里需要模拟Highcharts的初始化
  // 在实际项目中，您需要：
  // 1. npm install highcharts
  // 2. import Highcharts from 'highcharts'
  // 3. 使用真正的Highcharts API
  
  console.log('图表初始化 - CPU使用率图表')
  console.log('图表初始化 - 内存使用率图表')
  
  // 这里应该使用真正的Highcharts初始化代码
  // 示例(需要安装Highcharts后使用):
  /*
  if (cpuChartRef.value) {
    Highcharts.chart(cpuChartRef.value, {
      chart: {
        type: 'spline',
        backgroundColor: 'transparent'
      },
      title: {
        text: null
      },
      credits: {
        enabled: false
      },
      xAxis: {
        categories: chartTimeRange.value === 'hour' 
          ? ['0min', '10min', '20min', '30min', '40min', '50min', '60min']
          : chartTimeRange.value === 'day'
          ? ['0h', '3h', '6h', '9h', '12h', '15h', '18h', '21h', '24h']
          : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        labels: {
          style: { color: '#718096' }
        },
        gridLineWidth: 0,
        lineColor: '#E2E8F0'
      },
      yAxis: {
        title: { text: null },
        labels: {
          format: '{value}%',
          style: { color: '#718096' }
        },
        gridLineColor: '#E2E8F0',
        min: 0,
        max: 100
      },
      tooltip: {
        valueSuffix: '%'
      },
      legend: {
        enabled: false
      },
      series: [{
        name: 'CPU',
        data: chartTimeRange.value === 'hour'
          ? [45, 48, 52, 47, 50, 46, 44]
          : chartTimeRange.value === 'day'
          ? [25, 30, 45, 38, 42, 65, 55, 40, 35]
          : [40, 45, 50, 42, 38, 35, 41],
        color: '#409EFF',
        marker: { enabled: false }
      }]
    })
  }

  if (memoryChartRef.value) {
    Highcharts.chart(memoryChartRef.value, {
      chart: {
        type: 'spline',
        backgroundColor: 'transparent'
      },
      title: {
        text: null
      },
      credits: {
        enabled: false
      },
      xAxis: {
        categories: chartTimeRange.value === 'hour' 
          ? ['0min', '10min', '20min', '30min', '40min', '50min', '60min']
          : chartTimeRange.value === 'day'
          ? ['0h', '3h', '6h', '9h', '12h', '15h', '18h', '21h', '24h']
          : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        labels: {
          style: { color: '#718096' }
        },
        gridLineWidth: 0,
        lineColor: '#E2E8F0'
      },
      yAxis: {
        title: { text: null },
        labels: {
          format: '{value}%',
          style: { color: '#718096' }
        },
        gridLineColor: '#E2E8F0',
        min: 0,
        max: 100
      },
      tooltip: {
        valueSuffix: '%'
      },
      legend: {
        enabled: false
      },
      series: [{
        name: '内存',
        data: chartTimeRange.value === 'hour'
          ? [80, 82, 85, 84, 87, 85, 83]
          : chartTimeRange.value === 'day'
          ? [65, 68, 70, 72, 75, 80, 85, 82, 78]
          : [70, 72, 75, 78, 80, 77, 74],
        color: '#E6A23C',
        marker: { enabled: false }
      }]
    })
  }
  */
}

// 实时数据更新
const startRealTimeUpdates = () => {
  updateTimer = setInterval(() => {
    // 更新CPU使用率
    systemResources.cpu.usage = Math.floor(Math.random() * 30) + 30 // 30-60%
    
    // 更新内存使用率
    systemResources.memory.usage = Math.floor(Math.random() * 15) + 75 // 75-90%
    
    // 更新网络流量
    const upload = (Math.random() * 5 + 1).toFixed(1)
    const download = (Math.random() * 10 + 5).toFixed(1)
    systemResources.network.upload = `${upload}MB/s`
    systemResources.network.download = `${download}MB/s`
    
    // 更新设备数据
    devices.value.forEach(device => {
      if (device.status === 'online') {
        device.cpu = Math.floor(Math.random() * 20) + 10 // 10-30%
        device.temperature = Math.floor(Math.random() * 15) + 20 // 20-35°C
      }
    })
  }, 5000) // 每5秒更新一次
}

const stopRealTimeUpdates = () => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
}

onMounted(async () => {
  // 等待DOM更新完成后初始化图表
  await nextTick()
  initializeCharts()
  
  // 开始实时数据更新
  startRealTimeUpdates()
  
  console.log('系统性能监控页面已加载')
})

onUnmounted(() => {
  // 清理定时器
  stopRealTimeUpdates()
})
</script>

<style scoped>
/* 颜色变量 */
.text-secondary {
  color: #2c3e50;
}

.text-primary {
  color: #409EFF;
}

.text-success {
  color: #67C23A;
}

.text-warning {
  color: #E6A23C;
}

.text-danger {
  color: #F56C6C;
}

.text-green {
  color: #00A870;
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

.bg-primary {
  background-color: #409EFF;
}

.bg-lightBg {
  background-color: #E8F4FD;
}

.border-warning {
  border-color: #E6A23C;
}

.border-danger {
  border-color: #F56C6C;
}

.border-primary {
  border-color: #409EFF;
}

.hover\\:text-blue-600:hover {
  color: #1E90FF;
}

.hover\\:text-blue-700:hover {
  color: #1976D2;
}

.hover\\:bg-blue-600:hover {
  background-color: #1E90FF;
}

.hover\\:bg-gray-50:hover {
  background-color: #F9FAFB;
}

.hover\\:bg-gray-300:hover {
  background-color: #D1D5DB;
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* 表格样式 */
.divide-y > * + * {
  border-top-width: 1px;
}

.divide-gray-200 > * + * {
  border-top-color: #E5E7EB;
}

/* 进度条动画 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.duration-500 {
  transition-duration: 500ms;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .grid-cols-1.md\\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
  
  .overflow-x-auto {
    overflow-x: auto;
  }
}

@media (min-width: 768px) {
  .grid-cols-1.md\\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* 图表容器样式 */
#cpu-chart,
#memory-chart {
  min-height: 256px;
}

/* 滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

html, body {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
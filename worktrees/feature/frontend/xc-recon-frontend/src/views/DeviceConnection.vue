<template>
  <div id="main-content" class="w-full h-[calc(100vh-100px)] overflow-y-auto p-6">
    <!-- Page Header -->
    <div id="page-header" class="mb-6">
      <h1 class="text-2xl font-bold text-secondary">设备连接管理</h1>
      <p class="text-gray-500 mt-1">机器人硬件设备连接与网络配置</p>
    </div>
    
    <!-- Connection Overview -->
    <div id="connection-overview" class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-chart-line text-deviceOrange mr-2"></i>
        <h2 class="text-lg font-semibold">连接概览</h2>
        <button 
          class="ml-auto text-primary hover:text-blue-600 text-sm flex items-center"
          @click="refreshOverview"
        >
          <i class="fa-solid fa-sync mr-1"></i>刷新
        </button>
      </div>
      
      <div class="grid grid-cols-4 gap-4">
        <div id="total-devices" class="bg-white rounded-lg shadow p-4 border-l-4 border-deviceOrange">
          <div class="text-gray-500 text-sm mb-1">总设备</div>
          <div class="flex items-center">
            <span class="text-2xl font-bold">{{ overview.totalDevices }}</span>
            <span class="ml-1 text-gray-500">台</span>
          </div>
        </div>
        
        <div id="online-devices" class="bg-white rounded-lg shadow p-4 border-l-4 border-green">
          <div class="text-gray-500 text-sm mb-1">在线设备</div>
          <div class="flex items-center">
            <span class="text-2xl font-bold text-green">{{ overview.onlineDevices }}</span>
            <span class="ml-1 text-gray-500">台</span>
          </div>
        </div>
        
        <div id="offline-devices" class="bg-white rounded-lg shadow p-4 border-l-4 border-red">
          <div class="text-gray-500 text-sm mb-1">离线设备</div>
          <div class="flex items-center">
            <span class="text-2xl font-bold text-red">{{ overview.offlineDevices }}</span>
            <span class="ml-1 text-gray-500">台</span>
          </div>
        </div>
        
        <div id="network-quality" class="bg-white rounded-lg shadow p-4 border-l-4 border-blue">
          <div class="text-gray-500 text-sm mb-1">网络质量</div>
          <div class="flex items-center">
            <i 
              class="fa-solid fa-circle mr-2"
              :class="getNetworkQualityColor(overview.networkQuality)"
            ></i>
            <span class="font-medium">{{ overview.networkQuality }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Robot Devices -->
    <div id="robot-devices" class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center">
          <i class="fa-solid fa-robot text-deviceOrange mr-2"></i>
          <h2 class="text-lg font-semibold">机器人设备</h2>
        </div>
        <div class="flex space-x-2">
          <button 
            class="bg-deviceOrange hover:bg-orange-600 text-white px-3 py-1.5 rounded text-sm flex items-center transition"
            @click="connectAllDevices('robot')"
          >
            <i class="fa-solid fa-plug mr-1"></i>全部连接
          </button>
          <button 
            class="bg-gray-200 hover:bg-gray-300 text-secondary px-3 py-1.5 rounded text-sm flex items-center transition"
            @click="disconnectAllDevices('robot')"
          >
            <i class="fa-solid fa-power-off mr-1"></i>全部断开
          </button>
          <button 
            class="bg-gray-200 hover:bg-gray-300 text-secondary px-3 py-1.5 rounded text-sm flex items-center transition"
            @click="restartAllDevices('robot')"
          >
            <i class="fa-solid fa-sync mr-1"></i>重启设备
          </button>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                <input 
                  type="checkbox" 
                  class="rounded text-deviceOrange focus:ring-deviceOrange"
                  v-model="selectAllRobotDevices"
                  @change="toggleAllRobotDevices"
                >
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">设备名称</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP地址</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">延迟</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr 
              v-for="device in robotDevices" 
              :key="device.id"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-3 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  class="rounded text-deviceOrange focus:ring-deviceOrange"
                  v-model="device.selected"
                >
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center">
                  <i 
                    class="fa-solid fa-circle mr-2 text-xs"
                    :class="device.status === 'online' ? 'text-green' : 'text-red'"
                  ></i>
                  <span>{{ device.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">{{ device.ip }}</td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs rounded-full"
                  :class="device.status === 'online' ? 'bg-greenLight text-green' : 'bg-redLight text-red'"
                >
                  {{ device.status === 'online' ? '在线' : '离线' }}
                </span>
              </td>
              <td 
                class="px-4 py-3 whitespace-nowrap"
                :class="device.status === 'online' ? 'text-green' : 'text-gray-400'"
              >
                {{ device.status === 'online' ? device.latency + 'ms' : '-' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <button 
                  v-if="device.status === 'online'"
                  class="text-gray-500 hover:text-red-500 mr-2 px-2 py-1 rounded text-sm"
                  @click="disconnectDevice(device.id)"
                >
                  <i class="fa-solid fa-power-off mr-1"></i>断开
                </button>
                <button 
                  v-else
                  class="text-deviceOrange hover:text-orange-600 mr-2 px-2 py-1 rounded text-sm"
                  @click="connectDevice(device.id)"
                >
                  <i class="fa-solid fa-plug mr-1"></i>连接
                </button>
                <button 
                  class="text-gray-500 hover:text-blue-500 px-2 py-1 rounded text-sm"
                  @click="openDeviceSettings(device.id)"
                >
                  <i class="fa-solid fa-cog mr-1"></i>设置
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Vision Devices -->
    <div id="vision-devices" class="mb-6">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-camera text-deviceOrange mr-2"></i>
        <h2 class="text-lg font-semibold">视觉设备</h2>
      </div>
      
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                <input 
                  type="checkbox" 
                  class="rounded text-deviceOrange focus:ring-deviceOrange"
                  v-model="selectAllVisionDevices"
                  @change="toggleAllVisionDevices"
                >
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">设备名称</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP地址</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">延迟</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr 
              v-for="device in visionDevices" 
              :key="device.id"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-3 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  class="rounded text-deviceOrange focus:ring-deviceOrange"
                  v-model="device.selected"
                >
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center">
                  <i 
                    class="fa-solid fa-circle mr-2 text-xs"
                    :class="device.status === 'online' ? 'text-green' : 'text-red'"
                  ></i>
                  <span>{{ device.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">{{ device.ip }}</td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs rounded-full"
                  :class="device.status === 'online' ? 'bg-greenLight text-green' : 'bg-redLight text-red'"
                >
                  {{ device.status === 'online' ? '在线' : '离线' }}
                </span>
              </td>
              <td 
                class="px-4 py-3 whitespace-nowrap"
                :class="getLatencyColor(device.latency)"
              >
                {{ device.status === 'online' ? device.latency + 'ms' : '-' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <button 
                  v-if="device.status === 'online'"
                  class="text-gray-500 hover:text-red-500 mr-2 px-2 py-1 rounded text-sm"
                  @click="disconnectDevice(device.id)"
                >
                  <i class="fa-solid fa-power-off mr-1"></i>断开
                </button>
                <button 
                  v-else
                  class="text-deviceOrange hover:text-orange-600 mr-2 px-2 py-1 rounded text-sm"
                  @click="connectDevice(device.id)"
                >
                  <i class="fa-solid fa-plug mr-1"></i>连接
                </button>
                <button 
                  class="text-gray-500 hover:text-blue-500 px-2 py-1 rounded text-sm"
                  @click="openDeviceSettings(device.id)"
                >
                  <i class="fa-solid fa-cog mr-1"></i>设置
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Network Tools -->
    <div id="network-tools">
      <div class="flex items-center mb-4">
        <i class="fa-solid fa-wrench text-deviceOrange mr-2"></i>
        <h2 class="text-lg font-semibold">网络工具</h2>
      </div>
      
      <div class="grid grid-cols-3 gap-4">
        <div id="ping-test" class="bg-white rounded-lg shadow p-5">
          <div class="flex items-center mb-3">
            <i class="fa-solid fa-network-wired text-deviceOrange mr-2"></i>
            <h3 class="font-medium">Ping测试</h3>
          </div>
          <p class="text-gray-500 text-sm mb-4">检测设备连接延迟和可达性</p>
          <div class="mb-4">
            <label class="block text-sm text-gray-600 mb-1">目标地址</label>
            <input 
              type="text" 
              v-model="networkTools.pingTarget"
              class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-deviceOrange focus:border-transparent" 
              placeholder="输入IP地址"
            >
          </div>
          <button 
            class="w-full bg-deviceOrange hover:bg-orange-600 text-white px-4 py-2 rounded transition flex items-center justify-center"
            @click="startPingTest"
            :disabled="!networkTools.pingTarget || networkTools.pingRunning"
          >
            <i class="fa-solid fa-play mr-1"></i>开始测试
          </button>
        </div>
        
        <div id="port-scan" class="bg-white rounded-lg shadow p-5">
          <div class="flex items-center mb-3">
            <i class="fa-solid fa-sitemap text-deviceOrange mr-2"></i>
            <h3 class="font-medium">端口扫描</h3>
          </div>
          <p class="text-gray-500 text-sm mb-4">检测目标设备开放的网络端口</p>
          <div class="mb-4">
            <label class="block text-sm text-gray-600 mb-1">目标地址</label>
            <input 
              type="text" 
              v-model="networkTools.scanTarget"
              class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-deviceOrange focus:border-transparent" 
              placeholder="输入IP地址"
            >
          </div>
          <button 
            class="w-full bg-deviceOrange hover:bg-orange-600 text-white px-4 py-2 rounded transition flex items-center justify-center"
            @click="startPortScan"
            :disabled="!networkTools.scanTarget || networkTools.scanRunning"
          >
            <i class="fa-solid fa-search mr-1"></i>开始扫描
          </button>
        </div>
        
        <div id="network-diagnostics" class="bg-white rounded-lg shadow p-5">
          <div class="flex items-center mb-3">
            <i class="fa-solid fa-chart-line text-deviceOrange mr-2"></i>
            <h3 class="font-medium">网络诊断</h3>
          </div>
          <p class="text-gray-500 text-sm mb-4">分析网络质量和潜在问题</p>
          <div class="mb-4">
            <label class="block text-sm text-gray-600 mb-1">诊断范围</label>
            <select 
              v-model="networkTools.diagnosticsScope"
              class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-deviceOrange focus:border-transparent"
            >
              <option value="all">所有设备</option>
              <option value="robot">机器人设备</option>
              <option value="vision">视觉设备</option>
            </select>
          </div>
          <button 
            class="w-full bg-deviceOrange hover:bg-orange-600 text-white px-4 py-2 rounded transition flex items-center justify-center"
            @click="startNetworkDiagnostics"
            :disabled="networkTools.diagnosticsRunning"
          >
            <i class="fa-solid fa-stethoscope mr-1"></i>开始诊断
          </button>
        </div>
      </div>
    </div>
    
    <!-- Auto-refresh indicator -->
    <div class="fixed bottom-4 right-4 bg-white rounded-full shadow-lg px-3 py-2 text-xs text-gray-500 flex items-center">
      <i class="fa-solid fa-sync-alt mr-1 animate-spin"></i>
      <span>{{ autoRefreshCountdown }}秒后自动刷新</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 类型定义
interface Device {
  id: string
  name: string
  ip: string
  status: 'online' | 'offline'
  latency: number
  selected: boolean
}

interface ConnectionOverview {
  totalDevices: number
  onlineDevices: number
  offlineDevices: number
  networkQuality: string
}

interface NetworkTools {
  pingTarget: string
  pingRunning: boolean
  scanTarget: string
  scanRunning: boolean
  diagnosticsScope: string
  diagnosticsRunning: boolean
}

// 连接概览数据
const overview = reactive<ConnectionOverview>({
  totalDevices: 6,
  onlineDevices: 4,
  offlineDevices: 2,
  networkQuality: '良好'
})

// 机器人设备数据
const robotDevices = reactive<Device[]>([
  {
    id: 'fr3-right',
    name: 'FR3右臂',
    ip: '192.168.58.2',
    status: 'online',
    latency: 5,
    selected: false
  },
  {
    id: 'fr3-left',
    name: 'FR3左臂',
    ip: '192.168.58.3',
    status: 'online',
    latency: 6,
    selected: false
  },
  {
    id: 'hermes-base',
    name: 'Hermes底盘',
    ip: '192.168.31.211',
    status: 'online',
    latency: 8,
    selected: false
  }
])

// 视觉设备数据
const visionDevices = reactive<Device[]>([
  {
    id: 'tof-camera',
    name: 'TOF相机',
    ip: '192.168.58.100',
    status: 'online',
    latency: 12,
    selected: false
  },
  {
    id: '2d-camera-1',
    name: '2D相机1',
    ip: '192.168.58.101',
    status: 'offline',
    latency: 0,
    selected: false
  },
  {
    id: 'fisheye-camera',
    name: '鱼眼相机',
    ip: '192.168.58.102',
    status: 'offline',
    latency: 0,
    selected: false
  }
])

// 网络工具数据
const networkTools = reactive<NetworkTools>({
  pingTarget: '',
  pingRunning: false,
  scanTarget: '',
  scanRunning: false,
  diagnosticsScope: 'all',
  diagnosticsRunning: false
})

// 选择状态
const selectAllRobotDevices = ref(false)
const selectAllVisionDevices = ref(false)

// 自动刷新倒计时
const autoRefreshCountdown = ref(5)
let autoRefreshTimer: NodeJS.Timeout | null = null

// 获取网络质量颜色
const getNetworkQualityColor = (quality: string) => {
  switch (quality) {
    case '良好':
      return 'text-green'
    case '一般':
      return 'text-yellow'
    case '差':
      return 'text-red'
    default:
      return 'text-gray-400'
  }
}

// 获取延迟颜色
const getLatencyColor = (latency: number) => {
  if (latency <= 10) return 'text-green'
  if (latency <= 30) return 'text-yellow'
  return 'text-red'
}

// 刷新概览数据
const refreshOverview = () => {
  // 重新计算设备统计
  const allDevices = [...robotDevices, ...visionDevices]
  overview.totalDevices = allDevices.length
  overview.onlineDevices = allDevices.filter(d => d.status === 'online').length
  overview.offlineDevices = allDevices.filter(d => d.status === 'offline').length
  
  // 模拟网络质量检测
  const onlineRatio = overview.onlineDevices / overview.totalDevices
  if (onlineRatio >= 0.8) {
    overview.networkQuality = '良好'
  } else if (onlineRatio >= 0.5) {
    overview.networkQuality = '一般'
  } else {
    overview.networkQuality = '差'
  }
  
  ElMessage.success('连接概览已刷新')
}

// 全选/取消全选机器人设备
const toggleAllRobotDevices = () => {
  robotDevices.forEach(device => {
    device.selected = selectAllRobotDevices.value
  })
}

// 全选/取消全选视觉设备
const toggleAllVisionDevices = () => {
  visionDevices.forEach(device => {
    device.selected = selectAllVisionDevices.value
  })
}

// 连接设备
const connectDevice = async (deviceId: string) => {
  const allDevices = [...robotDevices, ...visionDevices]
  const device = allDevices.find(d => d.id === deviceId)
  
  if (device) {
    try {
      ElMessage.info(`正在连接 ${device.name}...`)
      
      // 模拟连接过程
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      device.status = 'online'
      device.latency = Math.floor(Math.random() * 20) + 5
      
      ElMessage.success(`${device.name} 连接成功`)
      refreshOverview()
    } catch (error) {
      ElMessage.error(`${device.name} 连接失败`)
    }
  }
}

// 断开设备
const disconnectDevice = async (deviceId: string) => {
  const allDevices = [...robotDevices, ...visionDevices]
  const device = allDevices.find(d => d.id === deviceId)
  
  if (device) {
    try {
      await ElMessageBox.confirm(`确定要断开 ${device.name} 吗？`, '确认断开', {
        type: 'warning'
      })
      
      device.status = 'offline'
      device.latency = 0
      
      ElMessage.success(`${device.name} 已断开`)
      refreshOverview()
    } catch {
      // 用户取消
    }
  }
}

// 连接所有设备
const connectAllDevices = async (type: 'robot' | 'vision') => {
  const devices = type === 'robot' ? robotDevices : visionDevices
  const offlineDevices = devices.filter(d => d.status === 'offline')
  
  if (offlineDevices.length === 0) {
    ElMessage.info('所有设备已在线')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要连接所有${type === 'robot' ? '机器人' : '视觉'}设备吗？`, '确认连接', {
      type: 'info'
    })
    
    ElMessage.info(`正在连接${offlineDevices.length}台设备...`)
    
    // 模拟批量连接
    for (const device of offlineDevices) {
      device.status = 'online'
      device.latency = Math.floor(Math.random() * 20) + 5
      await new Promise(resolve => setTimeout(resolve, 500))
    }
    
    ElMessage.success(`成功连接${offlineDevices.length}台设备`)
    refreshOverview()
  } catch {
    // 用户取消
  }
}

// 断开所有设备
const disconnectAllDevices = async (type: 'robot' | 'vision') => {
  const devices = type === 'robot' ? robotDevices : visionDevices
  const onlineDevices = devices.filter(d => d.status === 'online')
  
  if (onlineDevices.length === 0) {
    ElMessage.info('所有设备已离线')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要断开所有${type === 'robot' ? '机器人' : '视觉'}设备吗？`, '确认断开', {
      type: 'warning'
    })
    
    // 批量断开
    onlineDevices.forEach(device => {
      device.status = 'offline'
      device.latency = 0
    })
    
    ElMessage.success(`成功断开${onlineDevices.length}台设备`)
    refreshOverview()
  } catch {
    // 用户取消
  }
}

// 重启所有设备
const restartAllDevices = async (type: 'robot' | 'vision') => {
  const devices = type === 'robot' ? robotDevices : visionDevices
  
  try {
    await ElMessageBox.confirm(`确定要重启所有${type === 'robot' ? '机器人' : '视觉'}设备吗？`, '确认重启', {
      type: 'warning'
    })
    
    ElMessage.info('正在重启设备...')
    
    // 模拟重启过程
    devices.forEach(device => {
      device.status = 'offline'
      device.latency = 0
    })
    
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    devices.forEach(device => {
      device.status = 'online'
      device.latency = Math.floor(Math.random() * 20) + 5
    })
    
    ElMessage.success('设备重启完成')
    refreshOverview()
  } catch {
    // 用户取消
  }
}

// 打开设备设置
const openDeviceSettings = (deviceId: string) => {
  const allDevices = [...robotDevices, ...visionDevices]
  const device = allDevices.find(d => d.id === deviceId)
  
  if (device) {
    ElMessage.info(`打开 ${device.name} 设置页面`)
    // 这里应该导航到设备设置页面
  }
}

// 开始Ping测试
const startPingTest = async () => {
  if (!networkTools.pingTarget) {
    ElMessage.warning('请输入目标地址')
    return
  }
  
  networkTools.pingRunning = true
  ElMessage.info(`正在测试 ${networkTools.pingTarget} 的连通性...`)
  
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const latency = Math.floor(Math.random() * 50) + 1
    ElMessage.success(`Ping测试完成，延迟: ${latency}ms`)
  } catch {
    ElMessage.error('Ping测试失败')
  } finally {
    networkTools.pingRunning = false
  }
}

// 开始端口扫描
const startPortScan = async () => {
  if (!networkTools.scanTarget) {
    ElMessage.warning('请输入目标地址')
    return
  }
  
  networkTools.scanRunning = true
  ElMessage.info(`正在扫描 ${networkTools.scanTarget} 的开放端口...`)
  
  try {
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    const openPorts = [22, 80, 443, 8080]
    ElMessage.success(`扫描完成，发现开放端口: ${openPorts.join(', ')}`)
  } catch {
    ElMessage.error('端口扫描失败')
  } finally {
    networkTools.scanRunning = false
  }
}

// 开始网络诊断
const startNetworkDiagnostics = async () => {
  networkTools.diagnosticsRunning = true
  ElMessage.info(`正在对${networkTools.diagnosticsScope === 'all' ? '所有设备' : networkTools.diagnosticsScope === 'robot' ? '机器人设备' : '视觉设备'}进行网络诊断...`)
  
  try {
    await new Promise(resolve => setTimeout(resolve, 4000))
    
    ElMessage.success('网络诊断完成，网络状态良好')
  } catch {
    ElMessage.error('网络诊断失败')
  } finally {
    networkTools.diagnosticsRunning = false
  }
}

// 自动刷新倒计时
const startAutoRefresh = () => {
  autoRefreshTimer = setInterval(() => {
    autoRefreshCountdown.value--
    if (autoRefreshCountdown.value <= 0) {
      // 模拟数据更新
      refreshOverview()
      autoRefreshCountdown.value = 5
    }
  }, 1000)
}

onMounted(() => {
  console.log('设备连接管理页面已加载')
  startAutoRefresh()
})

onUnmounted(() => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})
</script>

<style scoped>
/* 项目配色变量 */
.text-secondary {
  color: #2c3e50;
}

.text-deviceOrange {
  color: #FF9500;
}

.bg-deviceOrange {
  background-color: #FF9500;
}

.hover\:bg-orange-600:hover {
  background-color: #E6830A;
}

.border-deviceOrange {
  border-color: #FF9500;
}

.text-green {
  color: #67C23A;
}

.bg-green {
  background-color: #67C23A;
}

.border-green {
  border-color: #67C23A;
}

.bg-greenLight {
  background-color: #E1F3D8;
}

.text-red {
  color: #F56C6C;
}

.bg-red {
  background-color: #F56C6C;
}

.border-red {
  border-color: #F56C6C;
}

.bg-redLight {
  background-color: #FDE2E2;
}

.text-blue {
  color: #409EFF;
}

.border-blue {
  border-color: #409EFF;
}

.text-yellow {
  color: #E6A23C;
}

.text-primary {
  color: #409EFF;
}

.hover\:text-blue-600:hover {
  color: #1E90FF;
}

.focus\:ring-deviceOrange:focus {
  --tw-ring-color: #FF9500;
}

.focus\:ring-2:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

.focus\:border-transparent:focus {
  border-color: transparent;
}

/* 确保字体一致性 */
* {
  font-family: 'Inter', sans-serif;
}

/* 滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}

/* 禁用状态样式 */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 动画效果 */
.transition {
  transition: all 0.2s ease-in-out;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .flex.space-x-2 {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .flex.space-x-2 > * {
    margin-left: 0;
  }
}
</style>
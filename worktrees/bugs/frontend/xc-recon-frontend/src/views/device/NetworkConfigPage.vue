<template>
  <div class="font-sans text-secondary bg-gray-50">
    <div class="p-6 w-full h-[calc(100vh-100px)] overflow-y-auto">
      <!-- Page Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-secondary">网络配置管理</h1>
        <p class="text-gray-600">机器人网络参数配置与连接管理</p>
      </div>

      <!-- Host Network Configuration -->
      <div class="mb-6">
        <div class="flex items-center mb-3">
          <i class="fa-solid fa-desktop text-primary mr-2"></i>
          <h2 class="text-xl font-semibold">主机网络配置</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Basic Network Settings -->
          <div class="bg-white rounded-lg shadow-sm">
            <div class="flex items-center justify-between p-4 border-b border-gray-200">
              <div class="flex items-center">
                <i class="fa-solid fa-wrench text-primary mr-2"></i>
                <h3 class="font-medium">基础网络设置</h3>
              </div>
              <div>
                <button 
                  class="text-gray-400 hover:text-primary"
                  @click="refreshNetworkSettings"
                >
                  <i class="fa-solid fa-sync"></i>
                </button>
              </div>
            </div>
            <div class="p-4">
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-600">IP地址:</span>
                  <span class="font-medium">{{ hostNetwork.ipAddress }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">子网掩码:</span>
                  <span class="font-medium">{{ hostNetwork.subnetMask }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">网关:</span>
                  <span class="font-medium">{{ hostNetwork.gateway }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">DNS:</span>
                  <span class="font-medium">{{ hostNetwork.dns }}</span>
                </div>
              </div>
            </div>
            <div class="p-4 border-t border-gray-100 flex justify-end space-x-2">
              <button 
                class="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                @click="resetNetworkSettings"
              >
                重置
              </button>
              <button 
                class="px-3 py-1.5 bg-primary text-white rounded-md text-sm hover:bg-blue-500"
                @click="modifyNetworkSettings"
              >
                修改
              </button>
            </div>
          </div>

          <!-- WiFi Settings -->
          <div class="bg-white rounded-lg shadow-sm">
            <div class="flex items-center justify-between p-4 border-b border-gray-200">
              <div class="flex items-center">
                <i class="fa-solid fa-wifi text-primary mr-2"></i>
                <h3 class="font-medium">WiFi设置</h3>
              </div>
              <div>
                <button 
                  class="text-gray-400 hover:text-primary"
                  @click="openWifiSettings"
                >
                  <i class="fa-solid fa-cog"></i>
                </button>
              </div>
            </div>
            <div class="p-4">
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-600">网络名:</span>
                  <span class="font-medium">{{ wifiSettings.networkName }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">状态:</span>
                  <span class="flex items-center">
                    <span 
                      class="h-2.5 w-2.5 rounded-full mr-2"
                      :class="wifiSettings.connected ? 'bg-connected' : 'bg-offline'"
                    ></span>
                    <span class="font-medium">{{ wifiSettings.connected ? '已连接' : '未连接' }}</span>
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">信号强度:</span>
                  <div class="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-connected h-2 rounded-full" 
                      :style="{ width: wifiSettings.signalStrength + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">带宽:</span>
                  <span class="font-medium">{{ wifiSettings.bandwidth }}</span>
                </div>
              </div>
            </div>
            <div class="p-4 border-t border-gray-100 flex justify-end space-x-2">
              <button 
                class="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                @click="disconnectWifi"
              >
                断开
              </button>
              <button 
                class="px-3 py-1.5 bg-primary text-white rounded-md text-sm hover:bg-blue-500"
                @click="reconnectWifi"
              >
                重连
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Device Network Configuration -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center">
            <i class="fa-solid fa-robot text-primary mr-2"></i>
            <h2 class="text-xl font-semibold">设备网络配置</h2>
          </div>
          <button 
            class="px-3 py-1.5 bg-warning text-white rounded-md text-sm hover:bg-orange-500 flex items-center"
            @click="addDevice"
          >
            <i class="fa-solid fa-plus mr-1"></i>
            添加设备
          </button>
        </div>
        <div class="bg-white rounded-lg shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 text-gray-600 text-sm">
                <tr>
                  <th class="py-3 px-4 text-left font-medium">设备名称</th>
                  <th class="py-3 px-4 text-left font-medium">IP地址</th>
                  <th class="py-3 px-4 text-left font-medium">端口</th>
                  <th class="py-3 px-4 text-left font-medium">状态</th>
                  <th class="py-3 px-4 text-left font-medium">延迟</th>
                  <th class="py-3 px-4 text-right font-medium">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr 
                  v-for="device in devices" 
                  :key="device.id"
                  class="hover:bg-gray-50 cursor-pointer"
                  @click="selectDevice(device)"
                >
                  <td class="py-3 px-4">{{ device.name }}</td>
                  <td class="py-3 px-4">{{ device.ipAddress }}</td>
                  <td class="py-3 px-4">{{ device.port }}</td>
                  <td class="py-3 px-4">
                    <span class="flex items-center">
                      <span 
                        class="h-2.5 w-2.5 rounded-full mr-2"
                        :class="{
                          'bg-connected': device.status === 'online',
                          'bg-offline': device.status === 'offline'
                        }"
                      ></span>
                      <span>{{ device.status === 'online' ? '正常' : '离线' }}</span>
                    </span>
                  </td>
                  <td class="py-3 px-4">{{ device.latency }}</td>
                  <td class="py-3 px-4 text-right">
                    <button 
                      class="px-2 py-1 bg-config text-white rounded text-xs hover:bg-blue-500"
                      @click.stop="configureDevice(device)"
                    >
                      配置
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Network Topology and Tools -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Network Topology -->
        <div class="bg-white rounded-lg shadow-sm">
          <div class="flex items-center justify-between p-4 border-b border-gray-200">
            <div class="flex items-center">
              <i class="fa-solid fa-project-diagram text-primary mr-2"></i>
              <h3 class="font-medium">网络拓扑图</h3>
            </div>
            <div>
              <button 
                class="text-gray-400 hover:text-primary"
                @click="expandTopology"
              >
                <i class="fa-solid fa-expand"></i>
              </button>
            </div>
          </div>
          <div class="p-4 h-[250px] flex items-center justify-center">
            <div class="w-full h-full relative">
              <!-- Network Topology SVG -->
              <svg width="100%" height="100%" viewBox="0 0 400 200">
                <!-- Router -->
                <g class="cursor-pointer" @click="selectTopologyNode('router')">
                  <rect x="175" y="10" width="50" height="30" rx="5" fill="#FFF3E0" stroke="#FF9500" stroke-width="2"></rect>
                  <text x="200" y="30" text-anchor="middle" font-size="12" fill="#2c3e50">路由器</text>
                  <!-- Connection Line -->
                  <line x1="200" y1="40" x2="200" y2="60" stroke="#409EFF" stroke-width="2"></line>
                </g>

                <!-- Switch -->
                <g class="cursor-pointer" @click="selectTopologyNode('switch')">
                  <rect x="175" y="60" width="50" height="30" rx="5" fill="#FFF3E0" stroke="#FF9500" stroke-width="2"></rect>
                  <text x="200" y="80" text-anchor="middle" font-size="12" fill="#2c3e50">交换机</text>
                  <!-- Connection Lines -->
                  <line x1="175" y1="90" x2="90" y2="120" stroke="#409EFF" stroke-width="2"></line>
                  <line x1="200" y1="90" x2="200" y2="120" stroke="#409EFF" stroke-width="2"></line>
                  <line x1="225" y1="90" x2="310" y2="120" stroke="#409EFF" stroke-width="2"></line>
                </g>

                <!-- Host -->
                <g class="cursor-pointer" @click="selectTopologyNode('host')">
                  <rect x="70" y="120" width="40" height="30" rx="5" fill="#FFF3E0" stroke="#FF9500" stroke-width="2"></rect>
                  <text x="90" y="140" text-anchor="middle" font-size="11" fill="#2c3e50">主机</text>
                  <!-- Connection Line -->
                  <line x1="90" y1="150" x2="90" y2="170" stroke="#409EFF" stroke-width="2"></line>
                </g>

                <!-- FR3 Right -->
                <g class="cursor-pointer" @click="selectTopologyNode('fr3-right')">
                  <rect x="180" y="120" width="40" height="30" rx="5" fill="#FFF3E0" stroke="#FF9500" stroke-width="2"></rect>
                  <text x="200" y="140" text-anchor="middle" font-size="11" fill="#2c3e50">FR3右</text>
                </g>

                <!-- FR3 Left -->
                <g class="cursor-pointer" @click="selectTopologyNode('fr3-left')">
                  <rect x="290" y="120" width="40" height="30" rx="5" fill="#FFF3E0" stroke="#FF9500" stroke-width="2"></rect>
                  <text x="310" y="140" text-anchor="middle" font-size="11" fill="#2c3e50">FR3左</text>
                </g>

                <!-- Camera -->
                <g class="cursor-pointer" @click="selectTopologyNode('camera')">
                  <rect x="70" y="170" width="40" height="30" rx="5" fill="#FFF3E0" stroke="#F56C6C" stroke-width="2"></rect>
                  <text x="90" y="190" text-anchor="middle" font-size="11" fill="#2c3e50">相机</text>
                </g>

                <!-- Chassis -->
                <g class="cursor-pointer" @click="selectTopologyNode('chassis')">
                  <rect x="130" y="170" width="40" height="30" rx="5" fill="#FFF3E0" stroke="#FF9500" stroke-width="2"></rect>
                  <text x="150" y="190" text-anchor="middle" font-size="11" fill="#2c3e50">底盘</text>
                </g>

                <!-- Status Legend -->
                <g transform="translate(330, 180)">
                  <circle cx="0" cy="-30" r="5" fill="#67C23A"></circle>
                  <text x="10" y="-28" font-size="10" fill="#2c3e50">正常</text>
                  <circle cx="0" cy="-15" r="5" fill="#F56C6C"></circle>
                  <text x="10" y="-13" font-size="10" fill="#2c3e50">故障</text>
                  <circle cx="0" cy="0" r="5" fill="#E0E0E0"></circle>
                  <text x="10" y="2" font-size="10" fill="#2c3e50">离线</text>
                </g>
              </svg>
            </div>
          </div>
        </div>

        <!-- Network Tools -->
        <div class="bg-white rounded-lg shadow-sm">
          <div class="flex items-center justify-between p-4 border-b border-gray-200">
            <div class="flex items-center">
              <i class="fa-solid fa-tools text-primary mr-2"></i>
              <h3 class="font-medium">网络工具</h3>
            </div>
          </div>
          <div class="p-4 space-y-4">
            <!-- Network Scanner -->
            <div>
              <div class="flex items-center mb-2">
                <i class="fa-solid fa-search text-primary mr-2"></i>
                <h4 class="font-medium">网络扫描</h4>
              </div>
              <div class="mb-2">
                <label class="text-sm text-gray-600 block mb-1">扫描范围:</label>
                <input 
                  type="text" 
                  v-model="networkTools.scanRange"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <button 
                class="w-full px-3 py-2 bg-warning text-white rounded-md text-sm hover:bg-orange-500"
                @click="startNetworkScan"
                :disabled="networkTools.scanning"
              >
                {{ networkTools.scanning ? '扫描中...' : '开始扫描' }}
              </button>
            </div>

            <!-- Port Detection -->
            <div class="pt-3 border-t border-gray-100">
              <div class="flex items-center mb-2">
                <i class="fa-solid fa-exclamation-triangle text-primary mr-2"></i>
                <h4 class="font-medium">端口检测</h4>
              </div>
              <div class="mb-2">
                <label class="text-sm text-gray-600 block mb-1">目标IP:</label>
                <input 
                  type="text" 
                  v-model="networkTools.targetIp"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div class="mb-2">
                <label class="text-sm text-gray-600 block mb-1">端口:</label>
                <input 
                  type="text" 
                  v-model="networkTools.targetPort"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <button 
                class="w-full px-3 py-2 bg-warning text-white rounded-md text-sm hover:bg-orange-500"
                @click="startPortDetection"
                :disabled="networkTools.detecting"
              >
                {{ networkTools.detecting ? '检测中...' : '开始检测' }}
              </button>
            </div>

            <!-- Connection Log -->
            <div class="pt-3 border-t border-gray-100">
              <div class="flex items-center mb-2">
                <i class="fa-solid fa-clipboard-list text-primary mr-2"></i>
                <h4 class="font-medium">连接日志</h4>
              </div>
              <button 
                class="w-full px-3 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                @click="viewConnectionLog"
              >
                查看详细日志
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Network Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Network Stats -->
        <div class="bg-white rounded-lg shadow-sm">
          <div class="flex items-center justify-between p-4 border-b border-gray-200">
            <div class="flex items-center">
              <i class="fa-solid fa-chart-bar text-primary mr-2"></i>
              <h3 class="font-medium">网络统计</h3>
            </div>
            <div>
              <button 
                class="text-gray-400 hover:text-primary"
                @click="refreshNetworkStats"
              >
                <i class="fa-solid fa-sync"></i>
              </button>
            </div>
          </div>
          <div class="p-4">
            <div ref="networkChart" class="h-[180px] mb-4 flex items-center justify-center bg-gray-50 rounded">
              <div class="text-center text-gray-500">
                <i class="fa-solid fa-chart-bar text-3xl mb-2"></i>
                <p class="text-sm">网络数据包统计图表</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-sm text-gray-500">数据包发送</div>
                <div class="font-semibold">{{ networkStats.packetsSent.toLocaleString() }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">数据包接收</div>
                <div class="font-semibold">{{ networkStats.packetsReceived.toLocaleString() }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">丢包率</div>
                <div class="font-semibold">{{ networkStats.packetLoss }}%</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">平均延迟</div>
                <div class="font-semibold">{{ networkStats.averageLatency }}ms</div>
              </div>
            </div>
          </div>
          <div class="p-4 border-t border-gray-100 flex justify-end">
            <button 
              class="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
              @click="viewDetailedStats"
            >
              详细统计
            </button>
          </div>
        </div>

        <!-- Bandwidth Usage -->
        <div class="bg-white rounded-lg shadow-sm">
          <div class="flex items-center justify-between p-4 border-b border-gray-200">
            <div class="flex items-center">
              <i class="fa-solid fa-tachometer-alt text-primary mr-2"></i>
              <h3 class="font-medium">带宽使用</h3>
            </div>
            <div class="flex items-center space-x-2">
              <select 
                v-model="bandwidthPeriod"
                class="text-xs border border-gray-300 rounded px-2 py-1"
                @change="updateBandwidthChart"
              >
                <option value="1h">最近1小时</option>
                <option value="24h">最近24小时</option>
                <option value="7d">最近7天</option>
              </select>
              <button 
                class="text-gray-400 hover:text-primary"
                @click="downloadBandwidthData"
              >
                <i class="fa-solid fa-download"></i>
              </button>
            </div>
          </div>
          <div class="p-4">
            <div ref="bandwidthChart" class="h-[180px] mb-4 flex items-center justify-center bg-gray-50 rounded">
              <div class="text-center text-gray-500">
                <i class="fa-solid fa-tachometer-alt text-3xl mb-2"></i>
                <p class="text-sm">带宽使用趋势图表</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-sm text-gray-500">当前下载</div>
                <div class="font-semibold">{{ bandwidthStats.currentDownload }} MB/s</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">当前上传</div>
                <div class="font-semibold">{{ bandwidthStats.currentUpload }} MB/s</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">峰值下载</div>
                <div class="font-semibold">{{ bandwidthStats.peakDownload }} MB/s</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">峰值上传</div>
                <div class="font-semibold">{{ bandwidthStats.peakUpload }} MB/s</div>
              </div>
            </div>
          </div>
          <div class="p-4 border-t border-gray-100 flex justify-end">
            <button 
              class="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
              @click="viewHistoricalData"
            >
              历史数据
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

// 类型定义
interface HostNetwork {
  ipAddress: string
  subnetMask: string
  gateway: string
  dns: string
}

interface WifiSettings {
  networkName: string
  connected: boolean
  signalStrength: number
  bandwidth: string
}

interface Device {
  id: string
  name: string
  ipAddress: string
  port: string
  status: 'online' | 'offline'
  latency: string
}

interface NetworkTools {
  scanRange: string
  scanning: boolean
  targetIp: string
  targetPort: string
  detecting: boolean
}

interface NetworkStats {
  packetsSent: number
  packetsReceived: number
  packetLoss: string
  averageLatency: string
}

interface BandwidthStats {
  currentDownload: string
  currentUpload: string
  peakDownload: string
  peakUpload: string
}

// 响应式数据
const hostNetwork = ref<HostNetwork>({
  ipAddress: '192.168.1.100',
  subnetMask: '255.255.255.0',
  gateway: '192.168.1.1',
  dns: '8.8.8.8'
})

const wifiSettings = ref<WifiSettings>({
  networkName: 'XC-Robot-5G',
  connected: true,
  signalStrength: 80,
  bandwidth: '867 Mbps'
})

const devices = ref<Device[]>([
  {
    id: '1',
    name: 'FR3右臂',
    ipAddress: '192.168.58.2',
    port: '502',
    status: 'online',
    latency: '5ms'
  },
  {
    id: '2',
    name: 'FR3左臂',
    ipAddress: '192.168.58.3',
    port: '502',
    status: 'online',
    latency: '6ms'
  },
  {
    id: '3',
    name: 'Hermes底盘',
    ipAddress: '192.168.31.211',
    port: '1448',
    status: 'online',
    latency: '8ms'
  },
  {
    id: '4',
    name: 'TOF相机',
    ipAddress: '192.168.58.100',
    port: '8080',
    status: 'online',
    latency: '12ms'
  },
  {
    id: '5',
    name: '2D相机1',
    ipAddress: '192.168.58.101',
    port: '8080',
    status: 'offline',
    latency: '--'
  },
  {
    id: '6',
    name: '鱼眼相机',
    ipAddress: '192.168.58.102',
    port: '8080',
    status: 'offline',
    latency: '--'
  }
])

const networkTools = reactive<NetworkTools>({
  scanRange: '192.168.1.1-254',
  scanning: false,
  targetIp: '192.168.58.2',
  targetPort: '502',
  detecting: false
})

const networkStats = ref<NetworkStats>({
  packetsSent: 1234567,
  packetsReceived: 1230145,
  packetLoss: '0.36',
  averageLatency: '8.5'
})

const bandwidthStats = ref<BandwidthStats>({
  currentDownload: '1.2',
  currentUpload: '0.3',
  peakDownload: '8.7',
  peakUpload: '2.1'
})

const bandwidthPeriod = ref('1h')

// 图表引用
const networkChart = ref<HTMLDivElement>()
const bandwidthChart = ref<HTMLDivElement>()

// 方法定义
const refreshNetworkSettings = () => {
  ElMessage.success('网络设置已刷新')
}

const resetNetworkSettings = () => {
  ElMessage.info('重置网络设置')
}

const modifyNetworkSettings = () => {
  ElMessage.info('打开网络设置修改对话框')
}

const openWifiSettings = () => {
  ElMessage.info('打开WiFi配置界面')
}

const disconnectWifi = () => {
  wifiSettings.value.connected = false
  ElMessage.warning('WiFi已断开')
}

const reconnectWifi = () => {
  wifiSettings.value.connected = true
  ElMessage.success('WiFi重新连接成功')
}

const addDevice = () => {
  ElMessage.info('打开添加设备对话框')
}

const selectDevice = (device: Device) => {
  ElMessage.info(`选择设备: ${device.name}`)
}

const configureDevice = (device: Device) => {
  ElMessage.info(`配置设备: ${device.name}`)
}

const expandTopology = () => {
  ElMessage.info('展开网络拓扑图')
}

const selectTopologyNode = (nodeType: string) => {
  ElMessage.info(`选择网络节点: ${nodeType}`)
}

const startNetworkScan = () => {
  networkTools.scanning = true
  ElMessage.info(`开始扫描网络范围: ${networkTools.scanRange}`)
  
  setTimeout(() => {
    networkTools.scanning = false
    ElMessage.success('网络扫描完成，发现 6 个设备')
  }, 3000)
}

const startPortDetection = () => {
  networkTools.detecting = true
  ElMessage.info(`检测 ${networkTools.targetIp}:${networkTools.targetPort}`)
  
  setTimeout(() => {
    networkTools.detecting = false
    ElMessage.success('端口检测完成，端口开放正常')
  }, 2000)
}

const viewConnectionLog = () => {
  ElMessage.info('打开连接日志查看器')
}

const refreshNetworkStats = () => {
  ElMessage.success('网络统计数据已刷新')
  
  // 模拟数据更新
  networkStats.value.packetsSent += Math.floor(Math.random() * 1000)
  networkStats.value.packetsReceived += Math.floor(Math.random() * 1000)
}

const viewDetailedStats = () => {
  ElMessage.info('打开详细统计报告')
}

const updateBandwidthChart = () => {
  ElMessage.info(`更新带宽图表: ${bandwidthPeriod.value}`)
}

const downloadBandwidthData = () => {
  ElMessage.success('带宽数据下载中...')
}

const viewHistoricalData = () => {
  ElMessage.info('打开历史数据查看器')
}

// 组件挂载
onMounted(() => {
  // 模拟图表初始化
  setTimeout(() => {
    if (networkChart.value) {
      networkChart.value.innerHTML = `
        <div class="text-center text-primary">
          <i class="fa-solid fa-chart-bar text-3xl mb-2"></i>
          <p class="text-sm">网络数据统计图表</p>
          <p class="text-xs text-gray-500">显示实时网络流量</p>
        </div>
      `
    }
    
    if (bandwidthChart.value) {
      bandwidthChart.value.innerHTML = `
        <div class="text-center text-success">
          <i class="fa-solid fa-tachometer-alt text-3xl mb-2"></i>
          <p class="text-sm">带宽使用趋势</p>
          <p class="text-xs text-gray-500">下载/上传带宽监控</p>
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
  color: #00A870;
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

.bg-primary {
  background-color: #409EFF;
}

.bg-warning {
  background-color: #FF9500;
}

.bg-connected {
  background-color: #67C23A;
}

.bg-offline {
  background-color: #F56C6C;
}

.bg-config {
  background-color: #409EFF;
}

.hover\:bg-blue-500:hover {
  background-color: #3a8ee6;
}

.hover\:bg-orange-500:hover {
  background-color: #e8940c;
}

.focus\:ring-primary:focus {
  ring-color: #409EFF;
}

.focus\:border-transparent:focus {
  border-color: transparent;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .overflow-x-auto table {
    min-width: 600px;
  }
  
  .text-xl {
    font-size: 1.125rem;
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
}

@media (max-width: 640px) {
  .p-6 {
    padding: 1rem;
  }
  
  .space-x-2 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.25rem;
  }
  
  .px-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
}
</style>
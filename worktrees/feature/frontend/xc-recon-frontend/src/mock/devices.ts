// 设备和连接Mock数据
export interface Device {
  id: string
  name: string
  type: 'robot_arm' | 'chassis' | 'camera' | 'sensor' | 'controller'
  brand: string
  model: string
  ip: string
  port: number
  status: 'online' | 'offline' | 'error' | 'maintenance'
  connectionType: 'ethernet' | 'wifi' | 'usb' | 'serial'
  lastHeartbeat: string
  firmware: string
  hardware: string
  location: string
  description: string
  capabilities: string[]
  metrics: DeviceMetrics
  config: DeviceConfig
}

export interface DeviceMetrics {
  cpuUsage: number
  memoryUsage: number
  temperature: number
  batteryLevel?: number
  signalStrength?: number
  uptime: number
  errorCount: number
  operationCount: number
}

export interface DeviceConfig {
  autoReconnect: boolean
  heartbeatInterval: number
  timeout: number
  maxRetries: number
  enableLogging: boolean
  logLevel: 'debug' | 'info' | 'warn' | 'error'
}

export interface NetworkConfig {
  ssid?: string
  security?: 'WPA2' | 'WPA3' | 'Open'
  dhcp: boolean
  staticIp?: string
  gateway?: string
  dns?: string[]
  proxy?: {
    enabled: boolean
    host?: string
    port?: number
  }
}

// Mock设备数据
export const mockDevices: Device[] = [
  {
    id: 'device-001',
    name: '左臂机械臂',
    type: 'robot_arm',
    brand: '法奥意威',
    model: 'FR3',
    ip: '192.168.58.2',
    port: 29999,
    status: 'online',
    connectionType: 'ethernet',
    lastHeartbeat: '2025-07-20 14:32:15',
    firmware: 'v2.3.1',
    hardware: 'FR3-001',
    location: '工作台左侧',
    description: '7自由度协作机械臂，负责精密操作任务',
    capabilities: ['抓取', '放置', '装配', '焊接', '打磨'],
    metrics: {
      cpuUsage: 25,
      memoryUsage: 42,
      temperature: 38.5,
      uptime: 8640000, // 100天
      errorCount: 2,
      operationCount: 15847
    },
    config: {
      autoReconnect: true,
      heartbeatInterval: 1000,
      timeout: 5000,
      maxRetries: 3,
      enableLogging: true,
      logLevel: 'info'
    }
  },
  {
    id: 'device-002',
    name: '右臂机械臂',
    type: 'robot_arm',
    brand: '法奥意威',
    model: 'FR3',
    ip: '192.168.58.3',
    port: 29999,
    status: 'online',
    connectionType: 'ethernet',
    lastHeartbeat: '2025-07-20 14:32:12',
    firmware: 'v2.3.1',
    hardware: 'FR3-002',
    location: '工作台右侧',
    description: '7自由度协作机械臂，负责配合操作任务',
    capabilities: ['抓取', '放置', '装配', '检测', '包装'],
    metrics: {
      cpuUsage: 28,
      memoryUsage: 38,
      temperature: 39.2,
      uptime: 8635200, // 99.9天
      errorCount: 1,
      operationCount: 14523
    },
    config: {
      autoReconnect: true,
      heartbeatInterval: 1000,
      timeout: 5000,
      maxRetries: 3,
      enableLogging: true,
      logLevel: 'info'
    }
  },
  {
    id: 'device-003',
    name: 'Hermes底盘',
    type: 'chassis',
    brand: '思岚科技',
    model: 'Hermes',
    ip: '192.168.58.10',
    port: 1448,
    status: 'online',
    connectionType: 'ethernet',
    lastHeartbeat: '2025-07-20 14:32:18',
    firmware: 'v1.8.2',
    hardware: 'Hermes-001',
    location: '移动平台',
    description: '全方位移动底盘，支持激光导航和避障',
    capabilities: ['移动', '导航', '避障', '定位', '建图'],
    metrics: {
      cpuUsage: 15,
      memoryUsage: 35,
      temperature: 42.1,
      batteryLevel: 78,
      uptime: 7200000, // 83.3天
      errorCount: 0,
      operationCount: 8945
    },
    config: {
      autoReconnect: true,
      heartbeatInterval: 2000,
      timeout: 8000,
      maxRetries: 5,
      enableLogging: true,
      logLevel: 'debug'
    }
  },
  {
    id: 'device-004',
    name: '深度摄像头',
    type: 'camera',
    brand: 'Intel',
    model: 'RealSense D435i',
    ip: '192.168.58.20',
    port: 8080,
    status: 'online',
    connectionType: 'usb',
    lastHeartbeat: '2025-07-20 14:32:10',
    firmware: 'v5.12.2',
    hardware: 'D435i-001',
    location: '工作台上方',
    description: 'RGB-D深度摄像头，提供三维视觉感知',
    capabilities: ['RGB图像', '深度图像', '点云', '目标检测', '姿态估计'],
    metrics: {
      cpuUsage: 45,
      memoryUsage: 62,
      temperature: 35.8,
      uptime: 6048000, // 70天
      errorCount: 3,
      operationCount: 25684
    },
    config: {
      autoReconnect: true,
      heartbeatInterval: 500,
      timeout: 3000,
      maxRetries: 3,
      enableLogging: true,
      logLevel: 'warn'
    }
  },
  {
    id: 'device-005',
    name: '工业控制器',
    type: 'controller',
    brand: 'Acer',
    model: 'Mini ProMini',
    ip: '192.168.58.1',
    port: 22,
    status: 'online',
    connectionType: 'ethernet',
    lastHeartbeat: '2025-07-20 14:32:20',
    firmware: 'Windows 11',
    hardware: 'i7-13620Hz',
    location: '控制柜',
    description: '主控计算机，运行机器人控制系统',
    capabilities: ['系统控制', '数据处理', '网络通信', '存储管理', 'AI推理'],
    metrics: {
      cpuUsage: 32,
      memoryUsage: 55,
      temperature: 45.2,
      uptime: 10368000, // 120天
      errorCount: 5,
      operationCount: 45782
    },
    config: {
      autoReconnect: true,
      heartbeatInterval: 5000,
      timeout: 10000,
      maxRetries: 2,
      enableLogging: true,
      logLevel: 'error'
    }
  }
]

// 设备Mock服务
export class DeviceMockService {
  // 获取所有设备
  static async getDevices(): Promise<Device[]> {
    await new Promise(resolve => setTimeout(resolve, 500))
    return [...mockDevices]
  }
  
  // 获取单个设备
  static async getDevice(id: string): Promise<Device | null> {
    await new Promise(resolve => setTimeout(resolve, 200))
    return mockDevices.find(d => d.id === id) || null
  }
  
  // 连接设备
  static async connectDevice(id: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const device = mockDevices.find(d => d.id === id)
    if (!device) {
      return { success: false, message: '设备不存在' }
    }
    
    if (device.status === 'online') {
      return { success: false, message: '设备已连接' }
    }
    
    // 模拟连接成功
    device.status = 'online'
    device.lastHeartbeat = new Date().toLocaleString('zh-CN')
    
    return { success: true, message: '设备连接成功' }
  }
  
  // 断开设备
  static async disconnectDevice(id: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const device = mockDevices.find(d => d.id === id)
    if (!device) {
      return { success: false, message: '设备不存在' }
    }
    
    device.status = 'offline'
    
    return { success: true, message: '设备已断开' }
  }
  
  // 测试设备连接
  static async testConnection(ip: string, port: number): Promise<{ success: boolean; latency?: number; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟网络测试
    const isReachable = Math.random() > 0.1 // 90%成功率
    
    if (isReachable) {
      const latency = Math.floor(Math.random() * 50) + 5 // 5-55ms
      return {
        success: true,
        latency,
        message: `连接成功，延迟 ${latency}ms`
      }
    } else {
      return {
        success: false,
        message: '连接超时，请检查网络配置'
      }
    }
  }
  
  // 获取设备状态统计
  static async getDeviceStats(): Promise<{
    total: number
    online: number
    offline: number
    error: number
    maintenance: number
  }> {
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const total = mockDevices.length
    const online = mockDevices.filter(d => d.status === 'online').length
    const offline = mockDevices.filter(d => d.status === 'offline').length
    const error = mockDevices.filter(d => d.status === 'error').length
    const maintenance = mockDevices.filter(d => d.status === 'maintenance').length
    
    return { total, online, offline, error, maintenance }
  }
  
  // 更新设备配置
  static async updateDeviceConfig(id: string, config: Partial<DeviceConfig>): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 600))
    
    const device = mockDevices.find(d => d.id === id)
    if (!device) {
      return { success: false, message: '设备不存在' }
    }
    
    device.config = { ...device.config, ...config }
    
    return { success: true, message: '配置更新成功' }
  }
  
  // 模拟实时更新设备指标
  static updateDeviceMetrics(): void {
    mockDevices.forEach(device => {
      if (device.status === 'online') {
        // 更新CPU使用率
        device.metrics.cpuUsage += (Math.random() - 0.5) * 10
        device.metrics.cpuUsage = Math.max(0, Math.min(100, device.metrics.cpuUsage))
        
        // 更新内存使用率
        device.metrics.memoryUsage += (Math.random() - 0.5) * 5
        device.metrics.memoryUsage = Math.max(0, Math.min(100, device.metrics.memoryUsage))
        
        // 更新温度
        device.metrics.temperature += (Math.random() - 0.5) * 2
        device.metrics.temperature = Math.max(20, Math.min(80, device.metrics.temperature))
        
        // 更新电池电量（如果有）
        if (device.metrics.batteryLevel !== undefined) {
          device.metrics.batteryLevel += (Math.random() - 0.5) * 1
          device.metrics.batteryLevel = Math.max(0, Math.min(100, device.metrics.batteryLevel))
        }
        
        // 更新运行时间
        device.metrics.uptime += 1000
        
        // 更新心跳时间
        device.lastHeartbeat = new Date().toLocaleString('zh-CN')
      }
    })
  }
}

// 启动实时数据更新（每5秒更新一次）
setInterval(() => {
  DeviceMockService.updateDeviceMetrics()
}, 5000)
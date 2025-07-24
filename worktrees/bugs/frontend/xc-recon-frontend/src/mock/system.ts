// 系统监控和状态Mock数据
export interface SystemInfo {
  id: string
  hostname: string
  os: string
  version: string
  architecture: string
  uptime: number
  bootTime: string
  timezone: string
  locale: string
}

export interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
    frequency: number
    temperature: number
    loadAverage: number[]
  }
  memory: {
    total: number
    used: number
    free: number
    available: number
    usage: number
  }
  disk: {
    total: number
    used: number
    free: number
    usage: number
  }
  network: {
    interfaces: NetworkInterface[]
    totalBytesReceived: number
    totalBytesSent: number
    packetsReceived: number
    packetsSent: number
  }
  processes: {
    total: number
    running: number
    sleeping: number
    zombie: number
  }
}

export interface NetworkInterface {
  name: string
  type: 'ethernet' | 'wifi' | 'loopback'
  status: 'up' | 'down'
  ipAddress: string
  macAddress: string
  speed: number
  bytesReceived: number
  bytesSent: number
}

export interface SystemAlert {
  id: string
  type: 'info' | 'warning' | 'error' | 'critical'
  title: string
  message: string
  timestamp: string
  acknowledged: boolean
  source: 'system' | 'device' | 'application'
  severity: number
}

export interface LogEntry {
  id: string
  timestamp: string
  level: 'debug' | 'info' | 'warn' | 'error' | 'critical'
  source: string
  message: string
  details?: Record<string, any>
}

// Mock系统信息
export const mockSystemInfo: SystemInfo = {
  id: 'sys-001',
  hostname: 'XC-Robot-Controller',
  os: 'Windows 11 Pro',
  version: '22H2',
  architecture: 'x64',
  uptime: 8640000, // 100天
  bootTime: '2025-04-12 09:15:30',
  timezone: 'Asia/Shanghai',
  locale: 'zh-CN'
}

// Mock系统指标
export const mockSystemMetrics: SystemMetrics = {
  cpu: {
    usage: 35,
    cores: 16,
    frequency: 3600,
    temperature: 45.5,
    loadAverage: [0.8, 1.2, 1.5]
  },
  memory: {
    total: 32768, // 32GB
    used: 18432,
    free: 14336,
    available: 20480,
    usage: 56.25
  },
  disk: {
    total: 2048000, // 2TB
    used: 512000,
    free: 1536000,
    usage: 25
  },
  network: {
    interfaces: [
      {
        name: 'Ethernet',
        type: 'ethernet',
        status: 'up',
        ipAddress: '192.168.58.1',
        macAddress: '00:1B:44:11:3A:B7',
        speed: 1000,
        bytesReceived: 1024000000,
        bytesSent: 512000000
      },
      {
        name: 'Wi-Fi',
        type: 'wifi',
        status: 'up',
        ipAddress: '192.168.1.100',
        macAddress: '00:1B:44:11:3A:B8',
        speed: 866,
        bytesReceived: 256000000,
        bytesSent: 128000000
      }
    ],
    totalBytesReceived: 1280000000,
    totalBytesSent: 640000000,
    packetsReceived: 850000,
    packetsSent: 425000
  },
  processes: {
    total: 245,
    running: 12,
    sleeping: 225,
    zombie: 0
  }
}

// Mock系统告警
export const mockSystemAlerts: SystemAlert[] = [
  {
    id: 'alert-001',
    type: 'warning',
    title: 'CPU温度告警',
    message: '系统CPU温度超过阈值（45°C），当前温度：47.5°C',
    timestamp: '2025-07-20 14:25:10',
    acknowledged: false,
    source: 'system',
    severity: 3
  },
  {
    id: 'alert-002',
    type: 'info',
    title: '设备连接成功',
    message: '右臂机械臂（192.168.58.3）连接成功',
    timestamp: '2025-07-20 14:20:15',
    acknowledged: true,
    source: 'device',
    severity: 1
  },
  {
    id: 'alert-003',
    type: 'error',
    title: '网络连接异常',
    message: 'Wi-Fi网络连接不稳定，检测到3次断线重连',
    timestamp: '2025-07-20 14:15:32',
    acknowledged: false,
    source: 'system',
    severity: 4
  }
]

// Mock日志条目
export const mockLogEntries: LogEntry[] = [
  {
    id: 'log-001',
    timestamp: '2025-07-20 14:32:15',
    level: 'info',
    source: 'RobotController',
    message: '左臂机械臂执行抓取动作完成',
    details: {
      deviceId: 'device-001',
      action: 'grasp',
      position: [245.5, 120.3, 180.0],
      force: 15.2
    }
  },
  {
    id: 'log-002',
    timestamp: '2025-07-20 14:32:08',
    level: 'warn',
    source: 'SystemMonitor',
    message: 'CPU使用率超过80%阈值',
    details: {
      cpuUsage: 85.3,
      threshold: 80,
      duration: 30000
    }
  },
  {
    id: 'log-003',
    timestamp: '2025-07-20 14:31:45',
    level: 'debug',
    source: 'CameraService',
    message: '深度摄像头图像处理完成',
    details: {
      frameCount: 1245,
      processingTime: 25.6,
      detectedObjects: 3
    }
  }
]

// 系统Mock服务
export class SystemMockService {
  // 获取系统信息
  static async getSystemInfo(): Promise<SystemInfo> {
    await new Promise(resolve => setTimeout(resolve, 300))
    return { ...mockSystemInfo }
  }
  
  // 获取系统指标
  static async getSystemMetrics(): Promise<SystemMetrics> {
    await new Promise(resolve => setTimeout(resolve, 200))
    return { ...mockSystemMetrics }
  }
  
  // 获取系统告警
  static async getSystemAlerts(acknowledged?: boolean): Promise<SystemAlert[]> {
    await new Promise(resolve => setTimeout(resolve, 400))
    
    if (acknowledged !== undefined) {
      return mockSystemAlerts.filter(alert => alert.acknowledged === acknowledged)
    }
    
    return [...mockSystemAlerts]
  }
  
  // 确认告警
  static async acknowledgeAlert(alertId: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const alert = mockSystemAlerts.find(a => a.id === alertId)
    if (!alert) {
      return { success: false, message: '告警不存在' }
    }
    
    alert.acknowledged = true
    return { success: true, message: '告警已确认' }
  }
  
  // 获取系统日志
  static async getSystemLogs(
    level?: string,
    source?: string,
    limit: number = 50
  ): Promise<LogEntry[]> {
    await new Promise(resolve => setTimeout(resolve, 600))
    
    let logs = [...mockLogEntries]
    
    if (level) {
      logs = logs.filter(log => log.level === level)
    }
    
    if (source) {
      logs = logs.filter(log => log.source === source)
    }
    
    return logs.slice(0, limit)
  }
  
  // 获取系统状态统计
  static async getSystemStats(): Promise<{
    uptime: number
    totalDevices: number
    activeAlerts: number
    systemLoad: number
    memoryUsage: number
    diskUsage: number
  }> {
    await new Promise(resolve => setTimeout(resolve, 250))
    
    return {
      uptime: mockSystemInfo.uptime,
      totalDevices: 5,
      activeAlerts: mockSystemAlerts.filter(a => !a.acknowledged).length,
      systemLoad: mockSystemMetrics.cpu.usage,
      memoryUsage: mockSystemMetrics.memory.usage,
      diskUsage: mockSystemMetrics.disk.usage
    }
  }
  
  // 重启系统
  static async restartSystem(): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // 模拟重启成功
    return { success: true, message: '系统重启指令已发送' }
  }
  
  // 模拟实时更新系统指标
  static updateSystemMetrics(): void {
    // 更新CPU使用率
    mockSystemMetrics.cpu.usage += (Math.random() - 0.5) * 10
    mockSystemMetrics.cpu.usage = Math.max(0, Math.min(100, mockSystemMetrics.cpu.usage))
    
    // 更新CPU温度
    mockSystemMetrics.cpu.temperature += (Math.random() - 0.5) * 2
    mockSystemMetrics.cpu.temperature = Math.max(30, Math.min(70, mockSystemMetrics.cpu.temperature))
    
    // 更新内存使用率
    mockSystemMetrics.memory.usage += (Math.random() - 0.5) * 5
    mockSystemMetrics.memory.usage = Math.max(20, Math.min(90, mockSystemMetrics.memory.usage))
    
    // 更新内存使用量
    const usedMemory = (mockSystemMetrics.memory.total * mockSystemMetrics.memory.usage) / 100
    mockSystemMetrics.memory.used = Math.floor(usedMemory)
    mockSystemMetrics.memory.free = mockSystemMetrics.memory.total - mockSystemMetrics.memory.used
    
    // 更新运行时间
    mockSystemMetrics.processes.total += Math.floor((Math.random() - 0.5) * 10)
    mockSystemMetrics.processes.total = Math.max(200, Math.min(300, mockSystemMetrics.processes.total))
    
    // 更新网络流量
    mockSystemMetrics.network.totalBytesReceived += Math.floor(Math.random() * 1000000)
    mockSystemMetrics.network.totalBytesSent += Math.floor(Math.random() * 500000)
    
    // 更新系统运行时间
    mockSystemInfo.uptime += 1000
  }
}

// 启动实时数据更新（每3秒更新一次）
setInterval(() => {
  SystemMockService.updateSystemMetrics()
}, 3000)
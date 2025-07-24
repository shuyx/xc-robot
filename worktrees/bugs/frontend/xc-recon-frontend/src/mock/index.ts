// Mock数据统一导出和管理
export * from './users'
export * from './devices'
export * from './system'
export * from './tasks'

// 智能交互相关Mock数据
export interface FaceRecognition {
  id: string
  name: string
  confidence: number
  lastSeen: string
  isAuthorized: boolean
  avatar?: string
  department?: string
  accessLevel: 'guest' | 'employee' | 'admin'
}

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    intent?: string
    confidence?: number
    entities?: Record<string, any>
  }
}

export interface ElevatorStatus {
  id: string
  floor: number
  direction: 'up' | 'down' | 'idle'
  doorStatus: 'open' | 'closed' | 'opening' | 'closing'
  occupancy: number
  maxCapacity: number
  isActive: boolean
  maintenanceMode: boolean
}

// Mock智能交互数据
export const mockFaceRecognitions: FaceRecognition[] = [
  {
    id: 'face-001',
    name: 'Kevin Zhang',
    confidence: 96.8,
    lastSeen: '2025-07-20 14:30:25',
    isAuthorized: true,
    avatar: 'K',
    department: '技术研发部',
    accessLevel: 'admin'
  },
  {
    id: 'face-002',
    name: '李明',
    confidence: 88.5,
    lastSeen: '2025-07-20 14:25:10',
    isAuthorized: true,
    department: '生产运营部',
    accessLevel: 'employee'
  },
  {
    id: 'face-003',
    name: '未知访客',
    confidence: 75.2,
    lastSeen: '2025-07-20 14:20:45',
    isAuthorized: false,
    accessLevel: 'guest'
  }
]

export const mockChatMessages: ChatMessage[] = [
  {
    id: 'msg-001',
    type: 'user',
    content: '请启动左臂机械臂的校准程序',
    timestamp: '2025-07-20 14:30:00',
    metadata: {
      intent: 'robot_control',
      confidence: 95.5,
      entities: {
        device: '左臂机械臂',
        action: '校准'
      }
    }
  },
  {
    id: 'msg-002',
    type: 'assistant',
    content: '已收到指令，正在启动左臂机械臂（设备ID: device-001）的校准程序。预计耗时3分钟，请确保工作区域安全。',
    timestamp: '2025-07-20 14:30:05'
  },
  {
    id: 'msg-003',
    type: 'system',
    content: '左臂机械臂校准完成，所有关节精度正常。',
    timestamp: '2025-07-20 14:33:15'
  }
]

export const mockElevatorStatus: ElevatorStatus[] = [
  {
    id: 'elevator-001',
    floor: 3,
    direction: 'up',
    doorStatus: 'closed',
    occupancy: 2,
    maxCapacity: 8,
    isActive: true,
    maintenanceMode: false
  },
  {
    id: 'elevator-002',
    floor: 1,
    direction: 'idle',
    doorStatus: 'open',
    occupancy: 0,
    maxCapacity: 8,
    isActive: true,
    maintenanceMode: false
  }
]

// 智能交互Mock服务
export class IntelligentInteractionMockService {
  // 人脸识别
  static async recognizeFace(): Promise<FaceRecognition | null> {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 模拟90%识别成功率
    if (Math.random() > 0.1) {
      const randomIndex = Math.floor(Math.random() * mockFaceRecognitions.length)
      const recognition = { ...mockFaceRecognitions[randomIndex] }
      recognition.lastSeen = new Date().toLocaleString('zh-CN')
      recognition.confidence = 75 + Math.random() * 25 // 75-100%
      return recognition
    }
    
    return null
  }
  
  // 发送聊天消息
  static async sendChatMessage(content: string): Promise<ChatMessage> {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content,
      timestamp: new Date().toLocaleString('zh-CN')
    }
    
    mockChatMessages.push(userMessage)
    
    // 模拟AI回复
    setTimeout(() => {
      const responses = [
        '我理解了您的要求，正在处理中...',
        '已收到指令，系统正在执行相关操作。',
        '请稍等，我正在分析当前系统状态...',
        '指令已执行，请查看设备状态更新。',
        '操作完成，如有其他需要请随时告诉我。'
      ]
      
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        type: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date().toLocaleString('zh-CN')
      }
      
      mockChatMessages.push(assistantMessage)
    }, 1000)
    
    return userMessage
  }
  
  // 获取聊天历史
  static async getChatHistory(limit: number = 20): Promise<ChatMessage[]> {
    await new Promise(resolve => setTimeout(resolve, 300))
    return mockChatMessages.slice(-limit)
  }
  
  // 获取电梯状态
  static async getElevatorStatus(): Promise<ElevatorStatus[]> {
    await new Promise(resolve => setTimeout(resolve, 400))
    return [...mockElevatorStatus]
  }
  
  // 呼叫电梯
  static async callElevator(floor: number): Promise<{ success: boolean; message: string; estimatedTime?: number }> {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const availableElevator = mockElevatorStatus.find(e => e.isActive && !e.maintenanceMode)
    
    if (!availableElevator) {
      return { success: false, message: '当前没有可用的电梯' }
    }
    
    const estimatedTime = Math.abs(availableElevator.floor - floor) * 10 + 20 // 每层10秒 + 20秒基础时间
    
    // 模拟电梯移动
    availableElevator.direction = availableElevator.floor < floor ? 'up' : 'down'
    
    return {
      success: true,
      message: `电梯${availableElevator.id}正在前往${floor}楼`,
      estimatedTime
    }
  }
  
  // 模拟电梯状态更新
  static updateElevatorStatus(): void {
    mockElevatorStatus.forEach(elevator => {
      if (elevator.direction !== 'idle') {
        // 模拟电梯移动
        if (Math.random() > 0.7) {
          if (elevator.direction === 'up') {
            elevator.floor = Math.min(20, elevator.floor + 1)
          } else {
            elevator.floor = Math.max(1, elevator.floor - 1)
          }
          
          // 随机停止
          if (Math.random() > 0.8) {
            elevator.direction = 'idle'
            elevator.doorStatus = 'open'
          }
        }
      }
      
      // 模拟乘客变化
      if (elevator.doorStatus === 'open') {
        elevator.occupancy += Math.floor((Math.random() - 0.5) * 3)
        elevator.occupancy = Math.max(0, Math.min(elevator.maxCapacity, elevator.occupancy))
        
        // 随机关门
        if (Math.random() > 0.6) {
          elevator.doorStatus = 'closed'
        }
      }
    })
  }
}

// 启动电梯状态更新（每5秒更新一次）
setInterval(() => {
  IntelligentInteractionMockService.updateElevatorStatus()
}, 5000)

// Mock数据初始化服务
export class MockDataService {
  // 初始化所有Mock数据
  static async initialize(): Promise<void> {
    console.log('🚀 Mock数据框架初始化完成')
    console.log('📊 可用数据模块:')
    console.log('  - 用户认证 (AuthMockService)')
    console.log('  - 设备管理 (DeviceMockService)')
    console.log('  - 系统监控 (SystemMockService)')
    console.log('  - 任务管理 (TaskMockService)')
    console.log('  - 智能交互 (IntelligentInteractionMockService)')
  }
  
  // 获取系统总览数据
  static async getSystemOverview(): Promise<{
    users: number
    devices: number
    activeTasks: number
    systemLoad: number
    alerts: number
  }> {
    const [deviceStats, taskStats, systemStats, alerts] = await Promise.all([
      import('./devices').then(m => m.DeviceMockService.getDeviceStats()),
      import('./tasks').then(m => m.TaskMockService.getTaskStats()),
      import('./system').then(m => m.SystemMockService.getSystemStats()),
      import('./system').then(m => m.SystemMockService.getSystemAlerts(false))
    ])
    
    return {
      users: 3, // mockUsers.length
      devices: deviceStats.total,
      activeTasks: taskStats.running,
      systemLoad: systemStats.systemLoad,
      alerts: alerts.length
    }
  }
}
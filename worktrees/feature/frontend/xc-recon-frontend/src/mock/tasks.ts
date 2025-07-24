// 任务管理Mock数据
export interface Task {
  id: string
  name: string
  type: 'pickup' | 'place' | 'move' | 'scan' | 'assembly' | 'inspection' | 'custom'
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  description: string
  createdAt: string
  startedAt?: string
  completedAt?: string
  estimatedDuration: number
  actualDuration?: number
  progress: number
  assignedDevices: string[]
  parameters: Record<string, any>
  result?: TaskResult
  errors?: TaskError[]
}

export interface TaskResult {
  success: boolean
  data?: Record<string, any>
  metrics?: {
    executionTime: number
    accuracy: number
    efficiency: number
  }
  outputs?: string[]
}

export interface TaskError {
  code: string
  message: string
  timestamp: string
  severity: 'warning' | 'error' | 'critical'
  context?: Record<string, any>
}

export interface TaskTemplate {
  id: string
  name: string
  type: Task['type']
  description: string
  parameters: TaskParameter[]
  estimatedDuration: number
  requiredDevices: string[]
  tags: string[]
}

export interface TaskParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'position' | 'rotation' | 'file'
  required: boolean
  defaultValue?: any
  constraints?: {
    min?: number
    max?: number
    options?: string[]
    pattern?: string
  }
  description: string
}

export interface TaskQueue {
  id: string
  name: string
  tasks: string[]
  status: 'idle' | 'running' | 'paused' | 'completed'
  currentTaskIndex: number
  createdAt: string
  startedAt?: string
  completedAt?: string
  priority: Task['priority']
}

// Mock任务数据
export const mockTasks: Task[] = [
  {
    id: 'task-001',
    name: '工件抓取任务',
    type: 'pickup',
    status: 'completed',
    priority: 'high',
    description: '使用左臂机械臂抓取工作台上的圆形工件',
    createdAt: '2025-07-20 14:00:00',
    startedAt: '2025-07-20 14:05:00',
    completedAt: '2025-07-20 14:08:30',
    estimatedDuration: 180000, // 3分钟
    actualDuration: 210000, // 3.5分钟
    progress: 100,
    assignedDevices: ['device-001'],
    parameters: {
      targetPosition: [245.5, 120.3, 180.0],
      gripForce: 15.2,
      approachSpeed: 50,
      objectType: 'cylinder'
    },
    result: {
      success: true,
      data: {
        finalPosition: [245.7, 120.1, 179.8],
        graspForce: 14.8
      },
      metrics: {
        executionTime: 210000,
        accuracy: 98.5,
        efficiency: 85.7
      },
      outputs: ['工件成功抓取', '位置精度: ±0.2mm']
    }
  },
  {
    id: 'task-002',
    name: '零件装配任务',
    type: 'assembly',
    status: 'running',
    priority: 'medium',
    description: '双臂协作完成零件装配操作',
    createdAt: '2025-07-20 14:10:00',
    startedAt: '2025-07-20 14:15:00',
    estimatedDuration: 600000, // 10分钟
    progress: 65,
    assignedDevices: ['device-001', 'device-002'],
    parameters: {
      leftArmPosition: [200.0, 150.0, 200.0],
      rightArmPosition: [300.0, 150.0, 200.0],
      assemblyType: 'insert',
      tolerance: 0.1
    }
  },
  {
    id: 'task-003',
    name: '质量检测任务',
    type: 'inspection',
    status: 'pending',
    priority: 'low',
    description: '使用视觉系统检测产品质量',
    createdAt: '2025-07-20 14:20:00',
    estimatedDuration: 300000, // 5分钟
    progress: 0,
    assignedDevices: ['device-004'],
    parameters: {
      inspectionType: 'dimensional',
      tolerances: {
        length: 0.1,
        width: 0.1,
        height: 0.05
      },
      imageResolution: '1920x1080'
    }
  },
  {
    id: 'task-004',
    name: '机器人移动任务',
    type: 'move',
    status: 'failed',
    priority: 'medium',
    description: '控制机器人移动到指定位置',
    createdAt: '2025-07-20 13:45:00',
    startedAt: '2025-07-20 13:50:00',
    estimatedDuration: 120000, // 2分钟
    actualDuration: 45000,
    progress: 30,
    assignedDevices: ['device-003'],
    parameters: {
      targetPosition: [5.0, 3.2, 0.0],
      maxSpeed: 1.5,
      pathType: 'optimal'
    },
    errors: [
      {
        code: 'NAV_001',
        message: '路径规划失败：目标位置存在障碍物',
        timestamp: '2025-07-20 13:51:30',
        severity: 'error',
        context: {
          obstaclePosition: [4.8, 3.1, 0.0],
          obstacleSize: [0.5, 0.3, 1.0]
        }
      }
    ]
  }
]

// Mock任务模板
export const mockTaskTemplates: TaskTemplate[] = [
  {
    id: 'template-001',
    name: '标准抓取模板',
    type: 'pickup',
    description: '通用物体抓取任务模板',
    estimatedDuration: 180000,
    requiredDevices: ['robot_arm'],
    tags: ['抓取', '通用', '单臂'],
    parameters: [
      {
        name: 'targetPosition',
        type: 'position',
        required: true,
        description: '目标物体位置坐标 [x, y, z]'
      },
      {
        name: 'gripForce',
        type: 'number',
        required: false,
        defaultValue: 15.0,
        constraints: { min: 5.0, max: 50.0 },
        description: '抓取力度 (N)'
      },
      {
        name: 'approachSpeed',
        type: 'number',
        required: false,
        defaultValue: 50,
        constraints: { min: 10, max: 100 },
        description: '接近速度 (%)'
      }
    ]
  },
  {
    id: 'template-002',
    name: '双臂协作模板',
    type: 'assembly',
    description: '双臂协作装配任务模板',
    estimatedDuration: 600000,
    requiredDevices: ['robot_arm', 'robot_arm'],
    tags: ['装配', '双臂', '协作'],
    parameters: [
      {
        name: 'leftArmPosition',
        type: 'position',
        required: true,
        description: '左臂目标位置'
      },
      {
        name: 'rightArmPosition',
        type: 'position',
        required: true,
        description: '右臂目标位置'
      },
      {
        name: 'assemblyType',
        type: 'string',
        required: true,
        constraints: { options: ['insert', 'screw', 'press', 'weld'] },
        description: '装配类型'
      }
    ]
  }
]

// Mock任务队列
export const mockTaskQueues: TaskQueue[] = [
  {
    id: 'queue-001',
    name: '生产队列A',
    tasks: ['task-001', 'task-002', 'task-003'],
    status: 'running',
    currentTaskIndex: 1,
    createdAt: '2025-07-20 14:00:00',
    startedAt: '2025-07-20 14:05:00',
    priority: 'high'
  },
  {
    id: 'queue-002',
    name: '测试队列',
    tasks: ['task-004'],
    status: 'paused',
    currentTaskIndex: 0,
    createdAt: '2025-07-20 13:45:00',
    startedAt: '2025-07-20 13:50:00',
    priority: 'medium'
  }
]

// 任务Mock服务
export class TaskMockService {
  // 获取所有任务
  static async getTasks(status?: Task['status']): Promise<Task[]> {
    await new Promise(resolve => setTimeout(resolve, 400))
    
    if (status) {
      return mockTasks.filter(task => task.status === status)
    }
    
    return [...mockTasks]
  }
  
  // 获取单个任务
  static async getTask(id: string): Promise<Task | null> {
    await new Promise(resolve => setTimeout(resolve, 200))
    return mockTasks.find(task => task.id === id) || null
  }
  
  // 创建新任务
  static async createTask(taskData: Omit<Task, 'id' | 'createdAt' | 'status' | 'progress'>): Promise<{ success: boolean; taskId?: string; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const newTask: Task = {
      ...taskData,
      id: `task-${String(mockTasks.length + 1).padStart(3, '0')}`,
      createdAt: new Date().toLocaleString('zh-CN'),
      status: 'pending',
      progress: 0
    }
    
    mockTasks.push(newTask)
    
    return {
      success: true,
      taskId: newTask.id,
      message: '任务创建成功'
    }
  }
  
  // 启动任务
  static async startTask(id: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const task = mockTasks.find(t => t.id === id)
    if (!task) {
      return { success: false, message: '任务不存在' }
    }
    
    if (task.status !== 'pending' && task.status !== 'paused') {
      return { success: false, message: '任务状态不允许启动' }
    }
    
    task.status = 'running'
    task.startedAt = new Date().toLocaleString('zh-CN')
    
    return { success: true, message: '任务启动成功' }
  }
  
  // 暂停任务
  static async pauseTask(id: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const task = mockTasks.find(t => t.id === id)
    if (!task) {
      return { success: false, message: '任务不存在' }
    }
    
    if (task.status !== 'running') {
      return { success: false, message: '只能暂停运行中的任务' }
    }
    
    task.status = 'paused'
    
    return { success: true, message: '任务已暂停' }
  }
  
  // 取消任务
  static async cancelTask(id: string): Promise<{ success: boolean; message: string }> {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const task = mockTasks.find(t => t.id === id)
    if (!task) {
      return { success: false, message: '任务不存在' }
    }
    
    if (task.status === 'completed' || task.status === 'cancelled') {
      return { success: false, message: '任务已完成或已取消' }
    }
    
    task.status = 'cancelled'
    
    return { success: true, message: '任务已取消' }
  }
  
  // 获取任务模板
  static async getTaskTemplates(): Promise<TaskTemplate[]> {
    await new Promise(resolve => setTimeout(resolve, 300))
    return [...mockTaskTemplates]
  }
  
  // 获取任务队列
  static async getTaskQueues(): Promise<TaskQueue[]> {
    await new Promise(resolve => setTimeout(resolve, 350))
    return [...mockTaskQueues]
  }
  
  // 获取任务统计
  static async getTaskStats(): Promise<{
    total: number
    pending: number
    running: number
    completed: number
    failed: number
    avgExecutionTime: number
    successRate: number
  }> {
    await new Promise(resolve => setTimeout(resolve, 250))
    
    const total = mockTasks.length
    const pending = mockTasks.filter(t => t.status === 'pending').length
    const running = mockTasks.filter(t => t.status === 'running').length
    const completed = mockTasks.filter(t => t.status === 'completed').length
    const failed = mockTasks.filter(t => t.status === 'failed').length
    
    const completedTasks = mockTasks.filter(t => t.actualDuration)
    const avgExecutionTime = completedTasks.length > 0 
      ? completedTasks.reduce((sum, t) => sum + (t.actualDuration || 0), 0) / completedTasks.length
      : 0
    
    const successRate = total > 0 ? (completed / total) * 100 : 0
    
    return {
      total,
      pending,
      running,
      completed,
      failed,
      avgExecutionTime,
      successRate
    }
  }
  
  // 模拟任务进度更新
  static updateTaskProgress(): void {
    mockTasks.forEach(task => {
      if (task.status === 'running') {
        // 更新进度
        task.progress += Math.random() * 5
        task.progress = Math.min(100, task.progress)
        
        // 模拟任务完成
        if (task.progress >= 100) {
          task.status = 'completed'
          task.completedAt = new Date().toLocaleString('zh-CN')
          task.actualDuration = task.estimatedDuration + (Math.random() - 0.5) * 60000 // ±1分钟误差
          
          // 生成结果
          task.result = {
            success: Math.random() > 0.1, // 90%成功率
            metrics: {
              executionTime: task.actualDuration!,
              accuracy: 85 + Math.random() * 15,
              efficiency: 75 + Math.random() * 25
            },
            outputs: ['任务执行完成', `执行时间: ${Math.floor(task.actualDuration! / 1000)}秒`]
          }
        }
      }
    })
  }
}

// 启动任务进度更新（每2秒更新一次）
setInterval(() => {
  TaskMockService.updateTaskProgress()
}, 2000)
// 用户和认证Mock数据
export interface User {
  id: string
  username: string
  fullName: string
  email: string
  role: 'admin' | 'operator' | 'viewer'
  avatar?: string
  department: string
  permissions: string[]
  lastLogin: string
  status: 'active' | 'inactive'
  createdAt: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  success: boolean
  token?: string
  user?: User
  message?: string
}

// Mock用户数据
export const mockUsers: User[] = [
  {
    id: 'user-001',
    username: 'kevin',
    fullName: 'Kevin Zhang',
    email: 'kevin@xc-robot.com',
    role: 'admin',
    avatar: 'K',
    department: '技术研发部',
    permissions: [
      'robot:control',
      'device:manage',
      'system:admin',
      'monitoring:view',
      'testing:execute'
    ],
    lastLogin: '2025-07-20 14:30:25',
    status: 'active',
    createdAt: '2024-01-15 09:00:00'
  },
  {
    id: 'user-002',
    username: 'operator1',
    fullName: '操作员小李',
    email: 'li@xc-robot.com',
    role: 'operator',
    avatar: '李',
    department: '生产运营部',
    permissions: [
      'robot:control',
      'device:view',
      'monitoring:view',
      'testing:execute'
    ],
    lastLogin: '2025-07-20 13:45:10',
    status: 'active',
    createdAt: '2024-03-20 10:30:00'
  },
  {
    id: 'user-003',
    username: 'viewer1',
    fullName: '观察员小王',
    email: 'wang@xc-robot.com',
    role: 'viewer',
    avatar: '王',
    department: '质量管理部',
    permissions: [
      'monitoring:view',
      'device:view'
    ],
    lastLogin: '2025-07-20 12:20:45',
    status: 'active',
    createdAt: '2024-05-10 14:15:00'
  }
]

// 认证Mock服务
export class AuthMockService {
  // 模拟登录
  static async login(request: LoginRequest): Promise<LoginResponse> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const { username, password } = request
    
    // 简单的用户名密码验证
    const validCredentials = [
      { username: 'kevin', password: 'admin123' },
      { username: 'operator1', password: 'op123' },
      { username: 'viewer1', password: 'view123' }
    ]
    
    const credential = validCredentials.find(c => c.username === username && c.password === password)
    
    if (credential) {
      const user = mockUsers.find(u => u.username === username)
      if (user) {
        // 生成Mock token
        const token = `mock_token_${user.id}_${Date.now()}`
        
        // 更新最后登录时间
        user.lastLogin = new Date().toLocaleString('zh-CN')
        
        return {
          success: true,
          token,
          user,
          message: '登录成功'
        }
      }
    }
    
    return {
      success: false,
      message: '用户名或密码错误'
    }
  }
  
  // 模拟获取当前用户信息
  static async getCurrentUser(token: string): Promise<User | null> {
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // 从token中提取用户ID
    const userId = token.split('_')[2]
    return mockUsers.find(u => u.id === `user-${userId.padStart(3, '0')}`) || null
  }
  
  // 模拟登出
  static async logout(): Promise<{ success: boolean }> {
    await new Promise(resolve => setTimeout(resolve, 300))
    return { success: true }
  }
  
  // 模拟token验证
  static async validateToken(token: string): Promise<boolean> {
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // 简单的token格式验证
    return token.startsWith('mock_token_') && token.length > 20
  }
}

// 权限检查辅助函数
export function hasPermission(user: User, permission: string): boolean {
  return user.permissions.includes(permission)
}

// 角色权限映射
export const rolePermissions: Record<string, string[]> = {
  admin: [
    'robot:control',
    'device:manage',
    'system:admin',
    'monitoring:view',
    'testing:execute',
    'user:manage',
    'config:modify'
  ],
  operator: [
    'robot:control',
    'device:view',
    'monitoring:view',
    'testing:execute'
  ],
  viewer: [
    'monitoring:view',
    'device:view'
  ]
}
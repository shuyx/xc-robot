// 菜单配置 - 基于sidebar_nav.html的9分组结构
export interface MenuItem {
  id: string
  title: string
  icon: string
  path?: string
  children?: MenuItem[]
}

export const menuConfig: MenuItem[] = [
  {
    id: 'quick-launch',
    title: '快速启动',
    icon: 'Lightning',
    children: [
      { id: 'main-dashboard', title: '主界面', icon: 'House', path: '/dashboard' },
      { id: 'favorites', title: '收藏功能', icon: 'Star', path: '/favorites' },
      { id: 'recent', title: '最近使用', icon: 'Clock', path: '/recent' }
    ]
  },
  {
    id: 'device-connection',
    title: '设备连接',
    icon: 'Connection',
    children: [
      { id: 'device-connect', title: '设备连接', icon: 'Link', path: '/device/connection' },
      { id: 'network-config', title: '网络配置', icon: 'Promotion', path: '/device/network' },
      { id: 'device-test', title: '设备测试', icon: 'Operation', path: '/device/test' }
    ]
  },
  {
    id: 'robot-control',
    title: '机器人控制',
    icon: 'Avatar',
    children: [
      { id: 'arm-control', title: '机械臂控制', icon: 'Avatar', path: '/robot/arm' },
      { id: 'chassis-control', title: '底盘控制', icon: 'Aim', path: '/robot/chassis' },
      { id: 'joint-control', title: '联动控制', icon: 'Refresh', path: '/robot/joint' }
    ]
  },
  {
    id: 'intelligent-interaction',
    title: '智能交互',
    icon: 'ChatDotRound',
    children: [
      { id: 'face-recognition', title: '人脸识别', icon: 'User', path: '/interaction/face' },
      { id: 'smart-chat', title: '智能对话', icon: 'ChatRound', path: '/interaction/chat' },
      { id: 'elevator-control', title: '梯控系统', icon: 'OfficeBuilding', path: '/interaction/elevator' }
    ]
  },
  {
    id: 'scene-testing',
    title: '场景测试',
    icon: 'SetUp',
    children: [
      { id: 'component-test', title: '组件测试', icon: 'Tools', path: '/testing/component' },
      { id: 'integration-test', title: '集成测试', icon: 'Link', path: '/testing/integration' },
      { id: 'vision-guided-test', title: '视觉引导测试', icon: 'View', path: '/testing/vision' },
      { id: 'end-to-end-test', title: '端到端场景', icon: 'Aim', path: '/testing/e2e' }
    ]
  },
  {
    id: 'simulation-planning',
    title: '仿真规划',
    icon: 'Coordinate',
    children: [
      { id: 'robot-simulation', title: '机器人仿真', icon: 'VideoPlay', path: '/simulation/robot' },
      { id: 'path-planning', title: '路径规划', icon: 'Map', path: '/simulation/path' },
      { id: 'task-orchestration', title: '任务编排', icon: 'Document', path: '/simulation/task' }
    ]
  },
  {
    id: 'visual-perception',
    title: '视觉感知',
    icon: 'View',
    children: [
      { id: 'vision-system', title: '视觉系统', icon: 'View', path: '/vision/system' },
      { id: 'camera-calibration', title: '相机标定', icon: 'Camera', path: '/vision/calibration' },
      { id: 'point-cloud', title: '点云处理', icon: 'Cloudy', path: '/vision/pointcloud' },
      { id: 'image-processing', title: '图像处理', icon: 'Picture', path: '/vision/image' }
    ]
  },
  {
    id: 'data-monitoring',
    title: '数据监控',
    icon: 'TrendCharts',
    children: [
      { id: 'system-monitor', title: '系统监控', icon: 'TrendCharts', path: '/monitoring/system' },
      { id: 'data-analysis', title: '数据分析', icon: 'PieChart', path: '/monitoring/analysis' },
      { id: 'performance-stats', title: '性能统计', icon: 'LineChart', path: '/monitoring/performance' }
    ]
  },
  {
    id: 'system-management',
    title: '系统管理',
    icon: 'Setting',
    children: [
      { id: 'system-settings', title: '系统设置', icon: 'Setting', path: '/management/settings' },
      { id: 'parameter-config', title: '参数配置', icon: 'Operation', path: '/management/config' },
      { id: 'maintenance', title: '维护管理', icon: 'Tools', path: '/management/maintenance' }
    ]
  }
]

// 菜单图标颜色映射 - 基于sidebar_nav.html的颜色设计
export const menuIconColors: Record<string, string> = {
  'quick-launch': 'text-yellow-400',
  'device-connection': 'text-green-400', 
  'robot-control': 'text-primary',
  'intelligent-interaction': 'text-blue-400',
  'scene-testing': 'text-purple-400',
  'simulation-planning': 'text-red-400',
  'visual-perception': 'text-teal-400',
  'data-monitoring': 'text-indigo-400',
  'system-management': 'text-gray-400'
}

// 导出扁平化的路由列表（用于路由配置）
export const getRouteList = (): Array<{ path: string; name: string; title: string }> => {
  const routes: Array<{ path: string; name: string; title: string }> = []
  
  menuConfig.forEach(menu => {
    // 添加主菜单路由
    routes.push({
      path: menu.path,
      name: menu.id,
      title: menu.title
    })
    
    // 添加子菜单路由
    menu.children?.forEach(child => {
      routes.push({
        path: child.path,
        name: child.id,
        title: child.title
      })
    })
  })
  
  return routes
}
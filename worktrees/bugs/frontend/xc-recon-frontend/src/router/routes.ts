// 路由配置 - 基于菜单配置自动生成路由
import type { RouteRecordRaw } from 'vue-router'
import { menuConfig } from '@/config/menu'

// 页面组件映射配置
const componentMap: Record<string, () => Promise<any>> = {
  // 测试页面
  'icon-test': () => import('@/views/IconTest.vue'),
  
  // 快速启动
  'main-dashboard': () => import('@/views/Dashboard.vue'),
  'favorites': () => import('@/views/QuickLaunch.vue'), // 收藏功能已在QuickLaunch中实现
  'recent': () => import('@/views/QuickLaunch.vue'), // 最近使用功能已在QuickLaunch中实现
  
  // 设备连接
  'device-connect': () => import('@/views/DeviceConnection.vue'),
  'network-config': () => import('@/views/device/NetworkConfigPage.vue'),
  'device-test': () => import('@/views/device/DeviceTestPage.vue'),
  
  // 机器人控制
  'arm-control': () => import('@/views/robot/ArmControlPage.vue'),
  'chassis-control': () => import('@/views/robot/ChassisControlPage.vue'),
  'joint-control': () => import('@/views/common/PlaceholderPage.vue'), // 暂时使用占位符
  
  // 智能交互
  'face-recognition': () => import('@/views/interaction/FaceRecognitionPage.vue'),
  'smart-chat': () => import('@/views/interaction/SmartChatPage.vue'),
  'elevator-control': () => import('@/views/interaction/ElevatorControlPage.vue'),
  
  // 场景测试
  'component-test': () => import('@/views/testing/ComponentTestPage.vue'),
  'integration-test': () => import('@/views/testing/IntegrationTestPage.vue'),
  'vision-guided-test': () => import('@/views/testing/VisionGuidedTestPage.vue'),
  'end-to-end-test': () => import('@/views/testing/EndToEndTestPage.vue'),
  
  // 仿真规划
  'robot-simulation': () => import('@/views/simulation/RobotSimulationPage.vue'),
  'path-planning': () => import('@/views/simulation/PathPlanningPage.vue'),
  'task-orchestration': () => import('@/views/simulation/TaskOrchestrationPage.vue'),
  
  // 视觉感知
  'vision-system': () => import('@/views/vision/VisionSystemPage.vue'),
  'camera-calibration': () => import('@/views/vision/CameraCalibrationPage.vue'),
  'point-cloud': () => import('@/views/common/PlaceholderPage.vue'), // 暂时使用占位符
  'image-processing': () => import('@/views/common/PlaceholderPage.vue'), // 暂时使用占位符
  
  // 数据监控
  'system-monitor': () => import('@/views/SystemMonitoring.vue'),
  'data-analysis': () => import('@/views/monitoring/DataAnalysisPage.vue'),
  'performance-stats': () => import('@/views/PerformanceStats.vue'),
  
  // 系统管理
  'system-settings': () => import('@/views/Settings.vue'),
  'parameter-config': () => import('@/views/Config.vue'),
  'maintenance': () => import('@/views/Maintenance.vue'),
  
  // 文档页面
  'technical-support': () => import('@/views/docs/TechnicalSupportPage.vue'),
  'software-info': () => import('@/views/docs/SoftwareInfoPage.vue')
}

// 生成子路由配置
export function generateChildRoutes(): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []
  
  menuConfig.forEach(menu => {
    if (menu.children) {
      menu.children.forEach(child => {
        if (child.path && child.id) {
          const component = componentMap[child.id]
          if (component) {
            routes.push({
              path: child.path,
              name: child.id,
              component,
              meta: {
                title: child.title,
                icon: child.icon,
                menuGroup: menu.id,
                menuGroupTitle: menu.title
              }
            })
          } else {
            // 如果没有对应组件，创建占位符页面
            routes.push({
              path: child.path,
              name: child.id,
              component: () => import('@/views/common/PlaceholderPage.vue'),
              meta: {
                title: child.title,
                icon: child.icon,
                menuGroup: menu.id,
                menuGroupTitle: menu.title,
                placeholder: true
              }
            })
          }
        }
      })
    }
  })
  
  // 添加图标测试页面路由
  routes.push({
    path: '/icon-test',
    name: 'icon-test',
    component: componentMap['icon-test'],
    meta: {
      title: '图标测试',
      icon: 'fa-solid fa-vials',
      hidden: false
    }
  })
  
  // 添加文档页面路由
  routes.push({
    path: '/docs/technical-support',
    name: 'technical-support',
    component: componentMap['technical-support'],
    meta: {
      title: '技术文档',
      icon: 'fa-solid fa-life-ring',
      hidden: true,
      requiresAuth: false
    }
  })
  
  routes.push({
    path: '/docs/software-info',
    name: 'software-info', 
    component: componentMap['software-info'],
    meta: {
      title: '软件信息',
      icon: 'fa-solid fa-info-circle',
      hidden: true,
      requiresAuth: false
    }
  })
  
  return routes
}

// 生成面包屑导航数据
export function generateBreadcrumbs(routeName: string): Array<{ title: string; path?: string }> {
  const breadcrumbs: Array<{ title: string; path?: string }> = []
  
  for (const menu of menuConfig) {
    if (menu.children) {
      const child = menu.children.find(item => item.id === routeName)
      if (child) {
        breadcrumbs.push({ title: menu.title })
        breadcrumbs.push({ title: child.title, path: child.path })
        break
      }
    }
  }
  
  return breadcrumbs
}

// 获取路由元信息
export function getRouteMetaInfo(routeName: string) {
  for (const menu of menuConfig) {
    if (menu.children) {
      const child = menu.children.find(item => item.id === routeName)
      if (child) {
        return {
          title: child.title,
          icon: child.icon,
          menuGroup: menu.id,
          menuGroupTitle: menu.title,
          path: child.path
        }
      }
    }
  }
  return null
}
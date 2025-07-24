# XC-RECON-V2 Vue3新界面设计方案

**项目**: XC-RECON-V2 双臂类人形机器人控制系统  
**技术栈**: Vue 3 + TypeScript + Element Plus  
**创建日期**: 2025-07-19  
**设计者**: Kevin Yuan  
**状态**: 设计完成，待实施

---

## 🎯 设计概述

### 核心设计原则
1. **用户体验连续性**: 继承旧版9分组结构，降低学习成本
2. **技术现代化升级**: Vue3组件化、TypeScript类型安全、响应式设计
3. **UI优先开发策略**: Mock数据驱动，前后端并行开发
4. **渐进式实施**: 按模块优先级分期实施，智能交互优先

### 项目背景分析
- **后端架构**: 95%完成，FastAPI + PostgreSQL企业级架构
- **前端现状**: 0%开始，需要从零构建Vue3界面
- **开发环境**: Mac开发(Mock数据) + Win测试(真实硬件)
- **核心价值**: 双臂机器人控制 + 智能交互 + 视觉感知

---

## 🏗️ 技术架构设计

### 技术栈选择
```yaml
前端框架: Vue 3.3+ (Composition API)
开发语言: TypeScript 5.0+
UI组件库: Element Plus 2.4+
状态管理: Pinia 2.1+
路由系统: Vue Router 4.2+
样式系统: SCSS + CSS变量 + 响应式设计
构建工具: Vite 4.0+
包管理: npm
```

### 目录结构设计
```
src/
├── components/           # 通用组件
│   ├── layout/          # 布局组件
│   │   ├── MainLayout.vue
│   │   ├── Header.vue
│   │   ├── Sidebar.vue
│   │   └── Breadcrumb.vue
│   ├── base/            # 基础组件
│   │   ├── BaseIcon.vue
│   │   ├── BaseButton.vue
│   │   └── BaseCard.vue
│   └── business/        # 业务组件
│       ├── DeviceStatus.vue
│       ├── RobotArm.vue
│       └── CameraView.vue
├── views/               # 页面组件
│   ├── quickstart/
│   ├── device/
│   ├── control/
│   ├── testing/
│   ├── simulation/
│   ├── vision/
│   ├── interaction/     # 智能交互模块(优先)
│   ├── monitoring/
│   └── management/
├── stores/              # Pinia状态管理
│   ├── interface.ts     # UI界面状态
│   ├── menu.ts          # 菜单状态
│   ├── device.ts        # 设备状态
│   └── user.ts          # 用户状态
├── router/              # 路由配置
│   ├── index.ts
│   └── menu.config.ts
├── services/            # API服务
│   ├── api.ts           # 基础API
│   ├── device.service.ts
│   ├── task.service.ts
│   └── mock.service.ts  # Mock数据服务
├── utils/               # 工具函数
├── styles/              # 样式文件
│   ├── variables.scss   # SCSS变量
│   ├── mixins.scss      # SCSS混入
│   └── global.scss      # 全局样式
└── types/               # TypeScript类型定义
    ├── menu.ts
    ├── device.ts
    └── api.ts
```

---

## 🗂️ 菜单系统设计

### 菜单数据结构
```typescript
// types/menu.ts
export interface RouteMeta {
  titleKey: string;        // i18n键名: 'menu.group.robot_control'
  icon: string;           // SVG图标组件名: 'RobotArm'
  permissions?: string[]; // 权限控制: ['admin', 'operator']
  favoritable?: boolean;  // 是否可收藏
  keepAlive?: boolean;    // 是否缓存页面
}

export interface MenuRoute {
  path: string;           // 路由路径
  name: string;           // 唯一路由名
  component: () => Promise<any>; // 懒加载组件
  meta: RouteMeta;
  children?: MenuRoute[];
  redirect?: string;      // 重定向路径
}

export interface MenuGroup {
  id: string;            // 分组ID: 'quickstart'
  order: number;         // 显示顺序
  collapsible: boolean;  // 是否可折叠
  defaultCollapsed: boolean; // 默认折叠状态
  routes: MenuRoute[];
}
```

### 完整菜单配置
```typescript
// router/menu.config.ts
export const menuGroups: MenuGroup[] = [
  {
    id: 'quickstart',
    order: 1,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/quickstart',
        name: 'QuickStart',
        component: () => import('@/views/quickstart/QuickStartPage.vue'),
        meta: {
          titleKey: 'menu.group.quickstart',
          icon: 'Lightning',
          favoritable: true
        },
        children: [
          {
            path: '/quickstart/favorites',
            name: 'Favorites',
            component: () => import('@/views/quickstart/FavoritesPage.vue'),
            meta: {
              titleKey: 'menu.item.favorites',
              icon: 'Star',
              favoritable: true
            }
          },
          {
            path: '/quickstart/recent',
            name: 'RecentUsed',
            component: () => import('@/views/quickstart/RecentUsedPage.vue'),
            meta: {
              titleKey: 'menu.item.recent_used',
              icon: 'History'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'device',
    order: 2,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/device',
        name: 'DeviceConnection',
        component: () => import('@/views/device/DeviceConnectionPage.vue'),
        meta: {
          titleKey: 'menu.group.device_connection',
          icon: 'Connection',
          favoritable: true
        },
        children: [
          {
            path: '/device/connection-test',
            name: 'ConnectionTest',
            component: () => import('@/views/device/ConnectionTestPage.vue'),
            meta: {
              titleKey: 'menu.item.connection_test',
              icon: 'TestConnection'
            }
          },
          {
            path: '/device/network-config',
            name: 'NetworkConfig',
            component: () => import('@/views/device/NetworkConfigPage.vue'),
            meta: {
              titleKey: 'menu.item.network_config',
              icon: 'Network'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'control',
    order: 3,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/control',
        name: 'RobotControl',
        component: () => import('@/views/control/RobotControlPage.vue'),
        meta: {
          titleKey: 'menu.group.robot_control',
          icon: 'Robot',
          favoritable: true
        },
        children: [
          {
            path: '/control/arm',
            name: 'ArmControl',
            component: () => import('@/views/control/ArmControlPage.vue'),
            meta: {
              titleKey: 'menu.item.arm_control',
              icon: 'RobotArm',
              keepAlive: true
            }
          },
          {
            path: '/control/chassis',
            name: 'ChassisControl',
            component: () => import('@/views/control/ChassisControlPage.vue'),
            meta: {
              titleKey: 'menu.item.chassis_control',
              icon: 'Chassis'
            }
          },
          {
            path: '/control/coordination',
            name: 'CoordinationControl',
            component: () => import('@/views/control/CoordinationControlPage.vue'),
            meta: {
              titleKey: 'menu.item.coordination_control',
              icon: 'Coordination'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'testing',
    order: 4,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/testing',
        name: 'ScenarioTesting',
        component: () => import('@/views/testing/ScenarioTestingPage.vue'),
        meta: {
          titleKey: 'menu.group.scenario_testing',
          icon: 'Testing',
          favoritable: true
        },
        children: [
          {
            path: '/testing/component',
            name: 'ComponentTesting',
            component: () => import('@/views/testing/ComponentTestingPage.vue'),
            meta: {
              titleKey: 'menu.item.component_testing',
              icon: 'Component'
            }
          },
          {
            path: '/testing/integration',
            name: 'IntegrationTesting',
            component: () => import('@/views/testing/IntegrationTestingPage.vue'),
            meta: {
              titleKey: 'menu.item.integration_testing',
              icon: 'Integration'
            }
          },
          {
            path: '/testing/vision-guided',
            name: 'VisionGuidedTesting',
            component: () => import('@/views/testing/VisionGuidedTestingPage.vue'),
            meta: {
              titleKey: 'menu.item.vision_guided_testing',
              icon: 'VisionGuided'
            }
          },
          {
            path: '/testing/e2e',
            name: 'E2EScenarios',
            component: () => import('@/views/testing/E2EScenariosPage.vue'),
            meta: {
              titleKey: 'menu.item.e2e_scenarios',
              icon: 'E2E'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'simulation',
    order: 5,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/simulation',
        name: 'SimulationPlanning',
        component: () => import('@/views/simulation/SimulationPlanningPage.vue'),
        meta: {
          titleKey: 'menu.group.simulation_planning',
          icon: 'Simulation',
          favoritable: true
        },
        children: [
          {
            path: '/simulation/robot-sim',
            name: 'RobotSimulation',
            component: () => import('@/views/simulation/RobotSimulationPage.vue'),
            meta: {
              titleKey: 'menu.item.robot_simulation',
              icon: 'RobotSim'
            }
          },
          {
            path: '/simulation/path-planning',
            name: 'PathPlanning',
            component: () => import('@/views/simulation/PathPlanningPage.vue'),
            meta: {
              titleKey: 'menu.item.path_planning',
              icon: 'PathPlanning'
            }
          },
          {
            path: '/simulation/task-orchestration',
            name: 'TaskOrchestration',
            component: () => import('@/views/simulation/TaskOrchestrationPage.vue'),
            meta: {
              titleKey: 'menu.item.task_orchestration',
              icon: 'TaskOrchestration'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'vision',
    order: 6,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/vision',
        name: 'VisionPerception',
        component: () => import('@/views/vision/VisionPerceptionPage.vue'),
        meta: {
          titleKey: 'menu.group.vision_perception',
          icon: 'Vision',
          favoritable: true
        },
        children: [
          {
            path: '/vision/system',
            name: 'VisionSystem',
            component: () => import('@/views/vision/VisionSystemPage.vue'),
            meta: {
              titleKey: 'menu.item.vision_system',
              icon: 'VisionSystem'
            }
          },
          {
            path: '/vision/calibration',
            name: 'CameraCalibration',
            component: () => import('@/views/vision/CameraCalibrationPage.vue'),
            meta: {
              titleKey: 'menu.item.camera_calibration',
              icon: 'Calibration'
            }
          },
          {
            path: '/vision/pointcloud',
            name: 'PointcloudProcessing',
            component: () => import('@/views/vision/PointcloudProcessingPage.vue'),
            meta: {
              titleKey: 'menu.item.pointcloud_processing',
              icon: 'Pointcloud'
            }
          },
          {
            path: '/vision/image-processing',
            name: 'ImageProcessing',
            component: () => import('@/views/vision/ImageProcessingPage.vue'),
            meta: {
              titleKey: 'menu.item.image_processing',
              icon: 'ImageProcessing'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'interaction',
    order: 7,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/interaction',
        name: 'SmartInteraction',
        component: () => import('@/views/interaction/SmartInteractionPage.vue'),
        meta: {
          titleKey: 'menu.group.smart_interaction',
          icon: 'Interaction',
          favoritable: true
        },
        children: [
          {
            path: '/interaction/face-recognition',
            name: 'FaceRecognition',
            component: () => import('@/views/interaction/FaceRecognitionPage.vue'),
            meta: {
              titleKey: 'menu.item.face_recognition',
              icon: 'FaceRecognition',
              keepAlive: true
            }
          },
          {
            path: '/interaction/conversational-task',
            name: 'ConversationalTask',
            component: () => import('@/views/interaction/ConversationalTaskPage.vue'),
            meta: {
              titleKey: 'menu.item.conversational_task',
              icon: 'Conversation',
              keepAlive: true
            }
          },
          {
            path: '/interaction/elevator-control',
            name: 'ElevatorControl',
            component: () => import('@/views/interaction/ElevatorControlPage.vue'),
            meta: {
              titleKey: 'menu.item.elevator_control',
              icon: 'Elevator'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'monitoring',
    order: 8,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/monitoring',
        name: 'DataMonitoring',
        component: () => import('@/views/monitoring/DataMonitoringPage.vue'),
        meta: {
          titleKey: 'menu.group.data_monitoring',
          icon: 'Monitoring',
          favoritable: true
        },
        children: [
          {
            path: '/monitoring/system',
            name: 'SystemMonitor',
            component: () => import('@/views/monitoring/SystemMonitorPage.vue'),
            meta: {
              titleKey: 'menu.item.system_monitor',
              icon: 'SystemMonitor'
            }
          },
          {
            path: '/monitoring/analytics',
            name: 'DataAnalytics',
            component: () => import('@/views/monitoring/DataAnalyticsPage.vue'),
            meta: {
              titleKey: 'menu.item.data_analytics',
              icon: 'Analytics'
            }
          },
          {
            path: '/monitoring/performance',
            name: 'PerformanceStats',
            component: () => import('@/views/monitoring/PerformanceStatsPage.vue'),
            meta: {
              titleKey: 'menu.item.performance_stats',
              icon: 'Performance'
            }
          }
        ]
      }
    ]
  },
  {
    id: 'management',
    order: 9,
    collapsible: true,
    defaultCollapsed: false,
    routes: [
      {
        path: '/management',
        name: 'SystemManagement',
        component: () => import('@/views/management/SystemManagementPage.vue'),
        meta: {
          titleKey: 'menu.group.system_management',
          icon: 'Management',
          favoritable: true,
          permissions: ['admin']
        },
        children: [
          {
            path: '/management/config',
            name: 'ParameterConfig',
            component: () => import('@/views/management/ParameterConfigPage.vue'),
            meta: {
              titleKey: 'menu.item.parameter_config',
              icon: 'Config',
              permissions: ['admin']
            }
          },
          {
            path: '/management/maintenance',
            name: 'Maintenance',
            component: () => import('@/views/management/MaintenancePage.vue'),
            meta: {
              titleKey: 'menu.item.maintenance',
              icon: 'Maintenance',
              permissions: ['admin', 'operator']
            }
          },
          {
            path: '/management/settings',
            name: 'SystemSettings',
            component: () => import('@/views/management/SystemSettingsPage.vue'),
            meta: {
              titleKey: 'menu.item.system_settings',
              icon: 'Settings',
              permissions: ['admin']
            }
          }
        ]
      }
    ]
  }
]
```

---

## 🎨 设计系统规范

### 配色系统
```scss
// styles/variables.scss
:root {
  // 主色调
  --color-primary: #409EFF;        // Element Plus 主色
  --color-primary-light: #79BBFF;  // 主色浅色
  --color-primary-dark: #337ECC;   // 主色深色
  
  // 辅助色调
  --color-secondary: #2c3e50;      // 深蓝灰
  --color-accent: #00A870;         // 绿色强调
  
  // 状态色
  --color-success: #67C23A;        // 成功绿
  --color-warning: #E6A23C;        // 警告橙
  --color-danger: #F56C6C;         // 危险红
  --color-info: #909399;           // 信息灰
  
  // 背景色
  --color-bg-primary: #ffffff;     // 主背景
  --color-bg-secondary: #f8f8f8;   // 次背景
  --color-bg-tertiary: #f2f2f2;    // 三级背景
  
  // 文本色
  --color-text-primary: #2c3e50;   // 主文本
  --color-text-secondary: rgba(60,60,60,0.66); // 次文本
  --color-text-placeholder: #C0C4CC; // 占位文本
  
  // 边框色
  --color-border-light: #EBEEF5;   // 浅边框
  --color-border-base: #DCDFE6;    // 基础边框
  --color-border-dark: #D4D7DE;    // 深边框
  
  // 阴影
  --shadow-light: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
  --shadow-base: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --shadow-dark: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

// 暗色主题
[data-theme="dark"] {
  --color-bg-primary: #1a1a1a;
  --color-bg-secondary: #2a2a2a;
  --color-bg-tertiary: #3a3a3a;
  --color-text-primary: #ffffff;
  --color-text-secondary: rgba(255,255,255,0.66);
  --color-border-light: #414141;
  --color-border-base: #4C4D4F;
  --color-border-dark: #58585B;
}
```

### 组件规范
```scss
// styles/mixins.scss
@mixin card-style {
  background: var(--color-bg-primary);
  border-radius: 8px;
  box-shadow: var(--shadow-light);
  border: 1px solid var(--color-border-light);
  padding: 20px;
}

@mixin button-style {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-base);
  }
}

@mixin responsive-grid {
  display: grid;
  gap: 20px;
  
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (min-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 图标系统
```typescript
// components/base/BaseIcon.vue
<template>
  <component 
    :is="iconComponent" 
    :class="['base-icon', `base-icon--${size}`]"
    :style="{ color }"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import * as ElementPlusIcons from '@element-plus/icons-vue'

interface Props {
  name: string
  size?: 'small' | 'medium' | 'large'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium'
})

const iconComponent = computed(() => {
  return ElementPlusIcons[props.name as keyof typeof ElementPlusIcons]
})
</script>

<style scoped>
.base-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.base-icon--small { font-size: 16px; }
.base-icon--medium { font-size: 20px; }
.base-icon--large { font-size: 24px; }
</style>
```

---

## 📱 核心组件设计

### 主布局组件
```vue
<!-- components/layout/MainLayout.vue -->
<template>
  <el-container class="main-layout">
    <!-- 顶部头部 -->
    <el-header class="main-header" height="60px">
      <Header />
    </el-header>
    
    <el-container>
      <!-- 左侧菜单 -->
      <el-aside 
        class="main-sidebar"
        :width="sidebarWidth"
      >
        <Sidebar />
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="content-wrapper">
          <!-- 面包屑导航 -->
          <Breadcrumb class="breadcrumb" />
          
          <!-- 页面内容 -->
          <div class="page-content">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <keep-alive :include="keepAlivePages">
                  <component :is="Component" />
                </keep-alive>
              </transition>
            </router-view>
          </div>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useInterfaceStore } from '@/stores/interface'
import Header from './Header.vue'
import Sidebar from './Sidebar.vue'
import Breadcrumb from './Breadcrumb.vue'

const interfaceStore = useInterfaceStore()
const { isMenuCollapsed } = storeToRefs(interfaceStore)

const sidebarWidth = computed(() => 
  isMenuCollapsed.value ? '64px' : '250px'
)

const keepAlivePages = computed(() => [
  'FaceRecognition',
  'ConversationalTask',
  'ArmControl'
])
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.main-header {
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-light);
}

.main-sidebar {
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-light);
  transition: width 0.3s ease;
}

.main-content {
  padding: 0;
  background: var(--color-bg-tertiary);
}

.content-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.breadcrumb {
  padding: 16px 20px;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-light);
}

.page-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
```

### 侧边栏菜单组件
```vue
<!-- components/layout/Sidebar.vue -->
<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo" v-if="!isMenuCollapsed">
        <img src="/logo.png" alt="XC-RECON" />
        <span class="logo-text">XC-RECON</span>
      </div>
      <el-button 
        class="collapse-btn"
        @click="toggleMenu"
        :icon="isMenuCollapsed ? Expand : Fold"
        type="text"
      />
    </div>
    
    <el-menu
      class="sidebar-menu"
      :default-active="activeMenuItem"
      :collapse="isMenuCollapsed"
      :unique-opened="true"
      router
    >
      <template v-for="group in menuGroups" :key="group.id">
        <el-sub-menu 
          v-if="group.routes[0].children?.length"
          :index="group.id"
          :class="['menu-group', { 'is-favorited': isFavoriteGroup(group.id) }]"
        >
          <template #title>
            <BaseIcon :name="group.routes[0].meta.icon" />
            <span>{{ $t(group.routes[0].meta.titleKey) }}</span>
            <el-button
              class="favorite-btn"
              @click.stop="toggleFavoriteGroup(group.id)"
              :icon="isFavoriteGroup(group.id) ? StarFilled : Star"
              type="text"
              size="small"
            />
          </template>
          
          <el-menu-item
            v-for="child in group.routes[0].children"
            :key="child.name"
            :index="child.path"
            :class="{ 'is-favorited': isFavoriteItem(child.name) }"
          >
            <BaseIcon :name="child.meta.icon" />
            <span>{{ $t(child.meta.titleKey) }}</span>
            <el-button
              v-if="child.meta.favoritable"
              class="favorite-btn"
              @click.stop="toggleFavoriteItem(child.name)"
              :icon="isFavoriteItem(child.name) ? StarFilled : Star"
              type="text"
              size="small"
            />
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item
          v-else
          :index="group.routes[0].path"
          :class="['menu-group', { 'is-favorited': isFavoriteGroup(group.id) }]"
        >
          <BaseIcon :name="group.routes[0].meta.icon" />
          <span>{{ $t(group.routes[0].meta.titleKey) }}</span>
          <el-button
            class="favorite-btn"
            @click.stop="toggleFavoriteGroup(group.id)"
            :icon="isFavoriteGroup(group.id) ? StarFilled : Star"
            type="text"
            size="small"
          />
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Expand, Fold, Star, StarFilled } from '@element-plus/icons-vue'
import { useInterfaceStore } from '@/stores/interface'
import { useMenuStore } from '@/stores/menu'
import { menuGroups } from '@/router/menu.config'
import BaseIcon from '@/components/base/BaseIcon.vue'

const route = useRoute()
const interfaceStore = useInterfaceStore()
const menuStore = useMenuStore()

const { isMenuCollapsed } = storeToRefs(interfaceStore)
const { favoriteGroups, favoriteItems } = storeToRefs(menuStore)

const activeMenuItem = computed(() => route.path)

const toggleMenu = () => {
  interfaceStore.toggleMenu()
}

const isFavoriteGroup = (groupId: string) => {
  return favoriteGroups.value.includes(groupId)
}

const isFavoriteItem = (itemName: string) => {
  return favoriteItems.value.includes(itemName)
}

const toggleFavoriteGroup = (groupId: string) => {
  menuStore.toggleFavoriteGroup(groupId)
}

const toggleFavoriteItem = (itemName: string) => {
  menuStore.toggleFavoriteItem(itemName)
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  height: 60px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border-light);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo img {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: var(--color-primary);
}

.collapse-btn {
  color: var(--color-text-secondary);
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.menu-group {
  position: relative;
}

.favorite-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-placeholder);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.menu-group:hover .favorite-btn,
.is-favorited .favorite-btn {
  opacity: 1;
}

.is-favorited .favorite-btn {
  color: var(--color-warning);
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  padding-right: 40px;
}

:deep(.el-menu-item.is-active) {
  background: var(--color-primary-light-9);
  color: var(--color-primary);
}
</style>
```

---

## 🤝 智能交互模块设计 (优先实施)

### 人脸识别页面
```vue
<!-- views/interaction/FaceRecognitionPage.vue -->
<template>
  <div class="face-recognition-page">
    <PageHeader 
      title="人脸识别系统"
      subtitle="基于深度学习的实时人脸识别与分析"
    >
      <el-button type="primary" @click="startRecognition">
        <BaseIcon name="VideoCamera" />
        {{ isRecognizing ? '停止识别' : '开始识别' }}
      </el-button>
    </PageHeader>
    
    <div class="page-content">
      <el-row :gutter="20">
        <!-- 相机预览区 -->
        <el-col :span="14">
          <el-card class="camera-card">
            <template #header>
              <div class="card-header">
                <BaseIcon name="VideoCamera" />
                <span>实时预览</span>
                <el-select v-model="selectedCamera" size="small">
                  <el-option
                    v-for="camera in availableCameras"
                    :key="camera.id"
                    :label="camera.name"
                    :value="camera.id"
                  />
                </el-select>
              </div>
            </template>
            
            <div class="camera-container">
              <video 
                ref="videoRef"
                class="camera-preview"
                autoplay
                muted
                :style="{ display: isRecognizing ? 'block' : 'none' }"
              />
              <canvas 
                ref="canvasRef"
                class="detection-overlay"
                :style="{ display: isRecognizing ? 'block' : 'none' }"
              />
              <div 
                v-if="!isRecognizing"
                class="camera-placeholder"
              >
                <BaseIcon name="VideoCamera" size="large" />
                <p>点击"开始识别"启动相机</p>
              </div>
            </div>
            
            <div class="camera-controls">
              <el-space>
                <el-button @click="capturePhoto" :disabled="!isRecognizing">
                  <BaseIcon name="Camera" />
                  拍照
                </el-button>
                <el-button @click="saveRecognitionLog" :disabled="!hasResults">
                  <BaseIcon name="Download" />
                  保存记录
                </el-button>
                <el-button @click="clearResults">
                  <BaseIcon name="Delete" />
                  清空结果
                </el-button>
              </el-space>
            </div>
          </el-card>
        </el-col>
        
        <!-- 识别结果区 -->
        <el-col :span="10">
          <el-card class="results-card">
            <template #header>
              <div class="card-header">
                <BaseIcon name="User" />
                <span>识别结果</span>
                <el-badge :value="recognitionResults.length" type="primary" />
              </div>
            </template>
            
            <div class="results-container">
              <el-empty 
                v-if="recognitionResults.length === 0"
                description="暂无识别结果"
              />
              
              <div v-else class="results-list">
                <div
                  v-for="(result, index) in recognitionResults"
                  :key="index"
                  class="result-item"
                >
                  <div class="result-avatar">
                    <img 
                      v-if="result.faceImage"
                      :src="result.faceImage"
                      :alt="result.name"
                    />
                    <BaseIcon v-else name="User" size="large" />
                  </div>
                  
                  <div class="result-info">
                    <div class="result-name">
                      {{ result.name || '未知人员' }}
                    </div>
                    <div class="result-confidence">
                      置信度: {{ result.confidence }}%
                    </div>
                    <div class="result-time">
                      {{ formatTime(result.timestamp) }}
                    </div>
                  </div>
                  
                  <div class="result-actions">
                    <el-button
                      size="small"
                      type="primary"
                      @click="viewDetails(result)"
                    >
                      详情
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
          
          <!-- 统计信息卡片 -->
          <el-card class="stats-card">
            <template #header>
              <div class="card-header">
                <BaseIcon name="PieChart" />
                <span>统计信息</span>
              </div>
            </template>
            
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ todayRecognitions }}</div>
                <div class="stat-label">今日识别</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ averageConfidence }}%</div>
                <div class="stat-label">平均置信度</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ uniquePersons }}</div>
                <div class="stat-label">识别人数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ recognitionSpeed }}ms</div>
                <div class="stat-label">平均耗时</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 详情对话框 -->
    <PersonDetailDialog 
      v-model="showDetailDialog"
      :person-data="selectedPerson"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useFaceRecognitionStore } from '@/stores/faceRecognition'
import PageHeader from '@/components/base/PageHeader.vue'
import BaseIcon from '@/components/base/BaseIcon.vue'
import PersonDetailDialog from './components/PersonDetailDialog.vue'

const faceStore = useFaceRecognitionStore()

// 响应式数据
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const isRecognizing = ref(false)
const selectedCamera = ref('camera_1')
const showDetailDialog = ref(false)
const selectedPerson = ref(null)

// Mock数据
const availableCameras = ref([
  { id: 'camera_1', name: '前置相机' },
  { id: 'camera_2', name: '后置相机' },
  { id: 'camera_tof', name: 'TOF相机' }
])

const recognitionResults = ref([
  {
    name: 'Kevin Yuan',
    confidence: 95,
    timestamp: new Date().toISOString(),
    faceImage: null,
    features: {
      age: 30,
      gender: 'male',
      emotion: 'neutral'
    }
  },
  {
    name: '未知人员',
    confidence: 65,
    timestamp: new Date(Date.now() - 5000).toISOString(),
    faceImage: null,
    features: {
      age: 25,
      gender: 'female',
      emotion: 'smile'
    }
  }
])

// 计算属性
const hasResults = computed(() => recognitionResults.value.length > 0)
const todayRecognitions = computed(() => recognitionResults.value.length)
const averageConfidence = computed(() => {
  if (recognitionResults.value.length === 0) return 0
  const sum = recognitionResults.value.reduce((acc, r) => acc + r.confidence, 0)
  return Math.round(sum / recognitionResults.value.length)
})
const uniquePersons = computed(() => {
  const names = new Set(recognitionResults.value.map(r => r.name))
  return names.size
})
const recognitionSpeed = computed(() => 150) // Mock数据

// 方法
const startRecognition = async () => {
  if (!isRecognizing.value) {
    try {
      await initCamera()
      isRecognizing.value = true
      ElMessage.success('人脸识别已启动')
    } catch (error) {
      ElMessage.error('相机启动失败')
    }
  } else {
    stopRecognition()
  }
}

const stopRecognition = () => {
  isRecognizing.value = false
  if (videoRef.value?.srcObject) {
    const stream = videoRef.value.srcObject as MediaStream
    stream.getTracks().forEach(track => track.stop())
  }
  ElMessage.info('人脸识别已停止')
}

const initCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 640, height: 480 } 
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (error) {
    throw new Error('无法访问相机')
  }
}

const capturePhoto = () => {
  // Mock拍照功能
  ElMessage.success('照片已保存')
}

const saveRecognitionLog = () => {
  // Mock保存功能
  ElMessage.success('识别记录已保存')
}

const clearResults = () => {
  recognitionResults.value = []
  ElMessage.info('结果已清空')
}

const viewDetails = (result: any) => {
  selectedPerson.value = result
  showDetailDialog.value = true
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString()
}

onMounted(() => {
  // 初始化组件
})

onUnmounted(() => {
  if (isRecognizing.value) {
    stopRecognition()
  }
})
</script>

<style scoped>
.face-recognition-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow-y: auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.camera-card {
  height: 500px;
  margin-bottom: 20px;
}

.camera-container {
  position: relative;
  width: 100%;
  height: 360px;
  background: var(--color-bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
}

.camera-preview,
.detection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--color-text-secondary);
}

.camera-controls {
  margin-top: 16px;
}

.results-card {
  height: 400px;
  margin-bottom: 20px;
}

.results-container {
  height: 320px;
  overflow-y: auto;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  background: var(--color-bg-primary);
}

.result-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.result-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-info {
  flex: 1;
}

.result-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.result-confidence {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.result-time {
  font-size: 12px;
  color: var(--color-text-placeholder);
}

.stats-card {
  height: 120px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}
</style>
```

---

## 🔧 状态管理设计

### 界面状态存储
```typescript
// stores/interface.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useInterfaceStore = defineStore('interface', () => {
  // 状态
  const isMenuCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const isFullscreen = ref(false)
  const notifications = ref<Notification[]>([])
  const isLoading = ref(false)
  
  // 计算属性
  const sidebarWidth = computed(() => 
    isMenuCollapsed.value ? '64px' : '250px'
  )
  
  // 动作
  const toggleMenu = () => {
    isMenuCollapsed.value = !isMenuCollapsed.value
    localStorage.setItem('menuCollapsed', String(isMenuCollapsed.value))
  }
  
  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }
  
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      isFullscreen.value = true
    } else {
      document.exitFullscreen()
      isFullscreen.value = false
    }
  }
  
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString()
    notifications.value.push({ ...notification, id })
    
    // 自动删除通知
    setTimeout(() => {
      removeNotification(id)
    }, notification.duration || 5000)
  }
  
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }
  
  // 初始化
  const init = () => {
    // 恢复菜单状态
    const savedMenuState = localStorage.getItem('menuCollapsed')
    if (savedMenuState) {
      isMenuCollapsed.value = savedMenuState === 'true'
    }
    
    // 恢复主题
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark'
    if (savedTheme) {
      setTheme(savedTheme)
    }
  }
  
  return {
    // 状态
    isMenuCollapsed,
    theme,
    isFullscreen,
    notifications,
    isLoading,
    // 计算属性
    sidebarWidth,
    // 动作
    toggleMenu,
    setTheme,
    toggleFullscreen,
    addNotification,
    removeNotification,
    setLoading,
    init
  }
})

// 类型定义
interface Notification {
  id: string
  title: string
  message: string
  type: 'success' | 'warning' | 'info' | 'error'
  duration?: number
}
```

### 菜单状态存储
```typescript
// stores/menu.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { menuGroups } from '@/router/menu.config'

export const useMenuStore = defineStore('menu', () => {
  // 状态
  const collapsedGroups = ref<string[]>([])
  const favoriteGroups = ref<string[]>([])
  const favoriteItems = ref<string[]>([])
  const searchKeyword = ref('')
  
  // 计算属性
  const filteredMenuGroups = computed(() => {
    if (!searchKeyword.value) return menuGroups
    
    return menuGroups.filter(group => {
      const groupMatches = group.routes[0].meta.titleKey
        .toLowerCase()
        .includes(searchKeyword.value.toLowerCase())
      
      const childMatches = group.routes[0].children?.some(child =>
        child.meta.titleKey
          .toLowerCase()
          .includes(searchKeyword.value.toLowerCase())
      )
      
      return groupMatches || childMatches
    })
  })
  
  const favoriteMenuItems = computed(() => {
    const items: any[] = []
    
    // 收藏的分组
    favoriteGroups.value.forEach(groupId => {
      const group = menuGroups.find(g => g.id === groupId)
      if (group) {
        items.push({
          type: 'group',
          ...group.routes[0]
        })
      }
    })
    
    // 收藏的单项
    favoriteItems.value.forEach(itemName => {
      menuGroups.forEach(group => {
        const item = group.routes[0].children?.find(child => child.name === itemName)
        if (item) {
          items.push({
            type: 'item',
            ...item
          })
        }
      })
    })
    
    return items
  })
  
  // 动作
  const toggleGroupCollapse = (groupId: string) => {
    const index = collapsedGroups.value.indexOf(groupId)
    if (index > -1) {
      collapsedGroups.value.splice(index, 1)
    } else {
      collapsedGroups.value.push(groupId)
    }
    localStorage.setItem('collapsedGroups', JSON.stringify(collapsedGroups.value))
  }
  
  const toggleFavoriteGroup = (groupId: string) => {
    const index = favoriteGroups.value.indexOf(groupId)
    if (index > -1) {
      favoriteGroups.value.splice(index, 1)
    } else {
      favoriteGroups.value.push(groupId)
    }
    localStorage.setItem('favoriteGroups', JSON.stringify(favoriteGroups.value))
  }
  
  const toggleFavoriteItem = (itemName: string) => {
    const index = favoriteItems.value.indexOf(itemName)
    if (index > -1) {
      favoriteItems.value.splice(index, 1)
    } else {
      favoriteItems.value.push(itemName)
    }
    localStorage.setItem('favoriteItems', JSON.stringify(favoriteItems.value))
  }
  
  const setSearchKeyword = (keyword: string) => {
    searchKeyword.value = keyword
  }
  
  const clearSearch = () => {
    searchKeyword.value = ''
  }
  
  // 初始化
  const init = () => {
    // 恢复折叠状态
    const savedCollapsed = localStorage.getItem('collapsedGroups')
    if (savedCollapsed) {
      collapsedGroups.value = JSON.parse(savedCollapsed)
    }
    
    // 恢复收藏状态
    const savedFavoriteGroups = localStorage.getItem('favoriteGroups')
    if (savedFavoriteGroups) {
      favoriteGroups.value = JSON.parse(savedFavoriteGroups)
    }
    
    const savedFavoriteItems = localStorage.getItem('favoriteItems')
    if (savedFavoriteItems) {
      favoriteItems.value = JSON.parse(savedFavoriteItems)
    }
  }
  
  return {
    // 状态
    collapsedGroups,
    favoriteGroups,
    favoriteItems,
    searchKeyword,
    // 计算属性
    filteredMenuGroups,
    favoriteMenuItems,
    // 动作
    toggleGroupCollapse,
    toggleFavoriteGroup,
    toggleFavoriteItem,
    setSearchKeyword,
    clearSearch,
    init
  }
})
```

---

## 🛠️ Mock数据框架

### Mock Service Worker配置
```typescript
// src/mocks/browser.ts
import { setupWorker } from 'msw'
import { deviceHandlers } from './handlers/device'
import { taskHandlers } from './handlers/task'
import { userHandlers } from './handlers/user'
import { visionHandlers } from './handlers/vision'

export const worker = setupWorker(
  ...deviceHandlers,
  ...taskHandlers,
  ...userHandlers,
  ...visionHandlers
)
```

### 设备相关Mock数据
```typescript
// src/mocks/handlers/device.ts
import { rest } from 'msw'
import { mockDevices } from '../data/devices'

export const deviceHandlers = [
  // 获取设备列表
  rest.get('/api/v1/devices', (req, res, ctx) => {
    return res(
      ctx.delay(300),
      ctx.status(200),
      ctx.json({
        status: 'success',
        data: mockDevices,
        total: mockDevices.length
      })
    )
  }),
  
  // 连接设备
  rest.post('/api/v1/devices/:deviceId/connect', (req, res, ctx) => {
    const { deviceId } = req.params
    const device = mockDevices.find(d => d.id === deviceId)
    
    if (!device) {
      return res(
        ctx.delay(500),
        ctx.status(404),
        ctx.json({
          status: 'error',
          message: '设备不存在'
        })
      )
    }
    
    // 模拟连接过程
    device.status = 'connecting'
    setTimeout(() => {
      device.status = 'online'
      device.last_heartbeat = new Date().toISOString()
    }, 2000)
    
    return res(
      ctx.delay(1000),
      ctx.status(200),
      ctx.json({
        status: 'success',
        message: `${device.name} 连接成功`,
        data: device
      })
    )
  }),
  
  // 断开设备
  rest.post('/api/v1/devices/:deviceId/disconnect', (req, res, ctx) => {
    const { deviceId } = req.params
    const device = mockDevices.find(d => d.id === deviceId)
    
    if (device) {
      device.status = 'offline'
      device.last_heartbeat = null
    }
    
    return res(
      ctx.delay(500),
      ctx.status(200),
      ctx.json({
        status: 'success',
        message: '设备已断开',
        data: device
      })
    )
  }),
  
  // 获取设备实时数据
  rest.get('/api/v1/devices/:deviceId/realtime', (req, res, ctx) => {
    const { deviceId } = req.params
    const device = mockDevices.find(d => d.id === deviceId)
    
    if (!device) {
      return res(ctx.status(404))
    }
    
    // 模拟实时数据变化
    if (device.type === 'robotic_arm') {
      device.realtime_data = {
        joint_angles: Array.from({ length: 6 }, () => 
          Math.round((Math.random() - 0.5) * 180 * 100) / 100
        ),
        tcp_position: Array.from({ length: 6 }, () => 
          Math.round((Math.random() - 0.5) * 1000 * 100) / 100
        ),
        force: Array.from({ length: 6 }, () => 
          Math.round(Math.random() * 5 * 100) / 100
        )
      }
    }
    
    return res(
      ctx.delay(100),
      ctx.status(200),
      ctx.json({
        status: 'success',
        data: device.realtime_data
      })
    )
  })
]
```

### 设备Mock数据
```typescript
// src/mocks/data/devices.ts
export const mockDevices = [
  {
    id: 'fr3_right_arm',
    name: 'FR3右臂',
    type: 'robotic_arm',
    ip: '192.168.58.2',
    port: 20003,
    status: 'offline',
    position: [0, -1.57, 1.57, 0, 1.57, 0],
    last_heartbeat: null,
    config: {
      max_velocity: 2.0,
      max_acceleration: 2.0,
      collision_behavior: 'stop'
    },
    realtime_data: {
      joint_angles: [0, -90, 90, 0, 90, 0],
      tcp_position: [400, 0, 300, 0, 0, 0],
      force: [0.1, 0.2, 0.3, 0.01, 0.02, 0.03],
      temperature: [25, 26, 24, 25, 23, 24],
      current: [0.5, 0.6, 0.4, 0.3, 0.2, 0.1]
    },
    capabilities: [
      'position_control',
      'velocity_control',
      'force_control',
      'impedance_control'
    ]
  },
  {
    id: 'fr3_left_arm',
    name: 'FR3左臂',
    type: 'robotic_arm',
    ip: '192.168.58.3',
    port: 20003,
    status: 'offline',
    position: [0, -1.57, 1.57, 0, 1.57, 0],
    last_heartbeat: null,
    config: {
      max_velocity: 2.0,
      max_acceleration: 2.0,
      collision_behavior: 'stop'
    },
    realtime_data: {
      joint_angles: [0, -90, 90, 0, 90, 0],
      tcp_position: [400, 0, 300, 0, 0, 0],
      force: [0.1, 0.2, 0.3, 0.01, 0.02, 0.03],
      temperature: [25, 26, 24, 25, 23, 24],
      current: [0.5, 0.6, 0.4, 0.3, 0.2, 0.1]
    },
    capabilities: [
      'position_control',
      'velocity_control',
      'force_control',
      'impedance_control'
    ]
  },
  {
    id: 'hermes_chassis',
    name: 'Hermes底盘',
    type: 'mobile_base',
    ip: '192.168.31.211',
    port: 1448,
    status: 'offline',
    position: [0, 0, 0],
    last_heartbeat: null,
    config: {
      max_linear_velocity: 1.0,
      max_angular_velocity: 1.0,
      safety_distance: 0.3
    },
    realtime_data: {
      pose: { x: 0, y: 0, theta: 0 },
      velocity: { linear: 0, angular: 0 },
      battery: 85,
      sensors: {
        lidar: { status: 'active', data_rate: 10 },
        imu: { status: 'active', calibrated: true },
        odometry: { status: 'active', accuracy: 0.95 }
      }
    },
    capabilities: [
      'navigation',
      'mapping',
      'localization',
      'obstacle_avoidance'
    ]
  },
  {
    id: 'tof_camera',
    name: 'TOF相机',
    type: 'tof_camera',
    ip: '192.168.58.100',
    port: 8080,
    status: 'offline',
    last_heartbeat: null,
    config: {
      resolution: '640x480',
      frame_rate: 30,
      depth_range: [0.2, 10.0]
    },
    realtime_data: {
      frame_count: 0,
      temperature: 45,
      depth_accuracy: 0.95,
      point_cloud_size: 307200
    },
    capabilities: [
      'depth_measurement',
      'point_cloud_generation',
      'object_detection'
    ]
  },
  {
    id: 'rgb_camera_1',
    name: '2D相机1',
    type: 'rgb_camera',
    ip: '192.168.58.101',
    port: 8080,
    status: 'offline',
    last_heartbeat: null,
    config: {
      resolution: '1920x1080',
      frame_rate: 30,
      auto_exposure: true
    },
    realtime_data: {
      frame_count: 0,
      exposure: 'auto',
      white_balance: 'auto',
      brightness: 50
    },
    capabilities: [
      'image_capture',
      'video_streaming',
      'feature_detection'
    ]
  },
  {
    id: 'fisheye_camera',
    name: '鱼眼相机',
    type: 'fisheye_camera',
    ip: '192.168.58.102',
    port: 8080,
    status: 'offline',
    last_heartbeat: null,
    config: {
      resolution: '1280x720',
      frame_rate: 30,
      fov: 180
    },
    realtime_data: {
      frame_count: 0,
      distortion_correction: true,
      field_of_view: 180
    },
    capabilities: [
      'wide_angle_capture',
      'panoramic_imaging',
      'distortion_correction'
    ]
  }
]
```

---

## 📋 实施指南

### UI设计顺序 (UX Pilot工作流)

**阶段1: 核心框架页面** (优先级P0)
1. **主布局页面**: 整体布局、侧边栏、头部导航
2. **设备连接页面**: 设备列表、连接状态、网络配置
3. **人脸识别页面**: 相机预览、识别结果、统计信息

**阶段2: 智能交互模块** (优先级P0)  
4. **智能对话页面**: 聊天界面、任务状态、历史记录
5. **梯控系统页面**: 电梯控制、楼层选择、操作记录

**阶段3: 机器人控制** (优先级P1)
6. **机械臂控制页面**: 关节控制、TCP位置、力控模式
7. **底盘控制页面**: 运动控制、传感器状态、导航地图
8. **联动控制页面**: 协调控制、任务编排、状态监控

**阶段4: 其他功能模块** (优先级P2)
9. **场景测试页面**: 测试场景、结果统计、报告生成
10. **仿真规划页面**: 3D仿真、路径规划、任务编排
11. **视觉感知页面**: 相机标定、图像处理、点云处理
12. **数据监控页面**: 系统监控、性能统计、日志分析
13. **系统管理页面**: 参数配置、用户管理、系统设置

### UX Pilot设计Prompt模板

```markdown
# XC-RECON-V2 页面设计要求

## 配色系统约束
- **主色调**: Primary #409EFF (Element Plus蓝), Secondary #2c3e50 (深蓝灰), Accent #00A870 (绿色)
- **状态色**: Success #67C23A, Warning #E6A23C, Danger #F56C6C, Info #909399
- **背景色**: 主背景 #ffffff, 次背景 #f8f8f8, 三级背景 #f2f2f2
- **文本色**: 主文本 #2c3e50, 次文本 rgba(60,60,60,0.66), 占位文本 #C0C4CC

## 设计原则
- **现代扁平设计风格**: 简洁清晰，避免过度装饰
- **Vue3+Element Plus风格**: 遵循Element Plus设计语言
- **响应式布局**: 支持桌面端和移动端适配
- **优先可访问性**: 确保颜色对比度和键盘导航

## 功能描述
[具体页面的功能描述]

## 布局要求
[具体页面的布局描述]

## 交互要求
[具体页面的交互逻辑]

请基于以上要求设计页面，确保配色和风格统一。
```

### 技术实施工作流

**Step 1: 环境准备**
```bash
cd /Users/shushu/xc-robot/xc-recon-v2/frontend/xc-recon-frontend
npm run dev  # 验证环境
```

**Step 2: 基础框架实施**
```bash
# 创建目录结构
mkdir -p src/{components/{layout,base,business},views,stores,router,services,utils,styles,types}

# 创建核心配置文件
touch src/router/menu.config.ts
touch src/stores/interface.ts
touch src/stores/menu.ts
```

**Step 3: 组件开发**
- 实现MainLayout.vue主布局
- 实现Sidebar.vue侧边栏菜单
- 实现BaseIcon.vue图标组件

**Step 4: 页面实施**
- 按优先级顺序实现各功能页面
- 每个页面使用Mock数据驱动
- 确保响应式布局和交互效果

**Step 5: 状态管理集成**
- 配置Pinia状态管理
- 实现菜单状态和界面状态
- 添加本地存储持久化

**Step 6: Mock数据集成**
- 配置MSW Mock Service Worker
- 实现完整的Mock API响应
- 模拟真实的延迟和错误情况

---

## 🚀 预期成果

### 技术成果
- **现代化Vue3界面**: 基于Composition API和TypeScript的类型安全前端
- **完整组件体系**: 可复用的业务组件和基础组件库
- **响应式设计**: 支持桌面端、平板端、移动端的自适应界面
- **高性能架构**: 路由懒加载、组件缓存、状态管理优化

### 业务成果
- **用户体验提升**: 继承旧版熟悉的9分组结构，降低学习成本
- **操作效率提升**: 收藏功能、搜索功能、快捷键支持
- **可维护性提升**: 模块化架构、TypeScript类型安全、完整的测试覆盖
- **扩展性提升**: 插件化架构、配置化菜单、主题系统

### 开发效率成果
- **并行开发**: Mock数据支撑，前后端独立开发
- **快速迭代**: 热重载、组件化开发、状态管理
- **质量保证**: TypeScript类型检查、ESLint规范、自动化测试
- **部署便利**: 容器化部署、环境配置、跨平台支持

---

**状态**: 设计方案完成，可立即开始实施 🚀  
**下一步**: 按照实施指南开始Vue3导航菜单框架建立